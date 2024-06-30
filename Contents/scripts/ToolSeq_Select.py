from os.path import abspath, dirname
from sys import stderr

from PySide2.QtCore import QEvent, Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QWidget, QComboBox, QStyledItemDelegate
from maya import cmds as maya_cmds
from maya.OpenMayaUI import MQtUtil
from maya.mel import eval as mel_eval
from shiboken2 import wrapInstance

class ToolSeq_Select(QWidget):

	userScriptDir = dirname(abspath(__file__)) + '/'

	qUiLoader = QUiLoader()
	qUiLoader.setWorkingDirectory(userScriptDir)

	windowMain = wrapInstance(int(MQtUtil.mainWindow()), QMainWindow)

	def __init__(self):
		super(ToolSeq_Select, self).__init__(ToolSeq_Select.windowMain)

		self.window = ToolSeq_Select.qUiLoader.load(ToolSeq_Select.userScriptDir + 'ui/ToolSeq_Select.ui', self)
		self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
		self.window.setAttribute(Qt.WA_DeleteOnClose)
		for qComboBox in self.window.findChildren(QComboBox):
			qComboBox.setItemDelegate(QStyledItemDelegate(qComboBox))
		with open(ToolSeq_Select.userScriptDir + 'ToolSeq.qss', 'r') as fileStyleSheet:
			self.window.setStyleSheet(fileStyleSheet.read())

		self.window.Button_LR_Standard.installEventFilter(self)
		self.window.Button_LR_Pattern.installEventFilter(self)
		self.window.Button_SelectSoft.installEventFilter(self)
		self.window.Button_SelectHard.installEventFilter(self)
		self.window.Button_SelectBorder.installEventFilter(self)
		self.window.Button_SelectAngle.installEventFilter(self)
		self.window.Button_Operate.installEventFilter(self)
		self.window.Button_Clear.installEventFilter(self)
		self.window.Button_Show.installEventFilter(self)

		self.window.show()

	def eventFilter(self, source, event):
		sourceObjectName = source.objectName()
		eventType = event.type()
		if sourceObjectName == 'Button_LR_Standard':
			if eventType == QEvent.MouseButtonRelease:
				eventButton = event.button()
				if eventButton == Qt.LeftButton:
					self.Action_LR_Standard_1()
				elif eventButton == Qt.RightButton:
					self.Action_LR_Standard_3()
		elif sourceObjectName == 'Button_LR_Pattern':
			if eventType == QEvent.MouseButtonRelease:
				eventButton = event.button()
				if eventButton == Qt.LeftButton:
					ToolSeq_Select.Action_LR_Pattern_1()
				elif eventButton == Qt.RightButton:
					ToolSeq_Select.Action_LR_Pattern_3()
		elif sourceObjectName == 'Button_SelectSoft':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					ToolSeq_Select.Action_SelectSoft()
		elif sourceObjectName == 'Button_SelectHard':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					ToolSeq_Select.Action_SelectHard()
		elif sourceObjectName == 'Button_SelectBorder':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					ToolSeq_Select.Action_SelectBorder()
		elif sourceObjectName == 'Button_SelectAngle':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_SelectAngle()
		elif sourceObjectName == 'Button_Operate':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_Operate()
		elif sourceObjectName == 'Button_Clear':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_Clear()
		elif sourceObjectName == 'Button_Show':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_Show()
		return False

	def Action_LR_Standard_1(self):
		maya_cmds.undoInfo(openChunk=True)
		mel_eval('polySelectEdgesEveryN edgeLoop %d' % (self.window.Int_LR_Standard.value()))
		maya_cmds.undoInfo(closeChunk=True)

	def Action_LR_Standard_3(self):
		maya_cmds.undoInfo(openChunk=True)
		mel_eval('polySelectEdgesEveryN edgeRing %d' % (self.window.Int_LR_Standard.value()))
		maya_cmds.undoInfo(closeChunk=True)

	@staticmethod
	def Action_LR_Pattern_1():
		maya_cmds.undoInfo(openChunk=True)
		mel_eval('polySelectEdgesPattern edgeLoopPattern')
		maya_cmds.undoInfo(closeChunk=True)

	@staticmethod
	def Action_LR_Pattern_3():
		maya_cmds.undoInfo(openChunk=True)
		mel_eval('polySelectEdgesPattern edgeRingPattern')
		maya_cmds.undoInfo(closeChunk=True)

	@staticmethod
	def Action_SelectSoft():
		maya_cmds.undoInfo(openChunk=True)
		try:
			maya_cmds.ConvertSelectionToEdges()
			maya_cmds.polySelectConstraint(mode=2, type=0x8000, smoothness=2)
			mel_eval('resetPolySelectConstraint')
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	@staticmethod
	def Action_SelectHard():
		maya_cmds.undoInfo(openChunk=True)
		try:
			maya_cmds.ConvertSelectionToEdges()
			maya_cmds.polySelectConstraint(mode=2, type=0x8000, smoothness=1)
			mel_eval('resetPolySelectConstraint')
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	@staticmethod
	def Action_SelectBorder():
		maya_cmds.undoInfo(openChunk=True)
		try:
			maya_cmds.ConvertSelectionToEdges()
			maya_cmds.polySelectConstraint(mode=2, type=0x8000, where=1)
			mel_eval('resetPolySelectConstraint')
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Action_SelectAngle(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			maya_cmds.polySoftEdge(caching=True, angle=self.window.Float_SelectAngle.value())
			maya_cmds.polySelectConstraint(mode=2, type=0x8000, smoothness=1)
			mel_eval('resetPolySelectConstraint')
			maya_cmds.polySelectConstraint(mode=2, type=0x8000, propagate=4)
			mel_eval('resetPolySelectConstraint')
			setA = maya_cmds.sets()
			setB = maya_cmds.sets(maya_cmds.polyListComponentConversion(maya_cmds.ls(selection=True, objectsOnly=True), toEdge=True))
			maya_cmds.select(maya_cmds.sets(setA, subtract=setB))
			maya_cmds.delete(setA, setB)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Action_Operate(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			operate = self.window.Combo_Operate.currentText()
			if operate == 'Union':
				setsName = self.window.Line_SetsName.text().strip()
				if maya_cmds.objExists(setsName):
					setsTmp = maya_cmds.sets(name='ToolSeq_Select_Sets_Tmp')
					maya_cmds.select(maya_cmds.sets(setsTmp, union=setsName))
					maya_cmds.delete(setsName, setsTmp)
					maya_cmds.sets(name=setsName)
				else:
					maya_cmds.sets(name=setsName)
			elif operate == 'Subtract 1-2':
				setsName = self.window.Line_SetsName.text().strip()
				if maya_cmds.objExists(setsName):
					setsTmp = maya_cmds.sets(name='ToolSeq_Select_Sets_Tmp')
					maya_cmds.select(maya_cmds.sets(setsTmp, subtract=setsName))
					maya_cmds.delete(setsName, setsTmp)
					maya_cmds.sets(name=setsName)
				else:
					maya_cmds.sets(name=setsName, empty=True)
			elif operate == 'Subtract 2-1':
				setsName = self.window.Line_SetsName.text().strip()
				if maya_cmds.objExists(setsName):
					setsTmp = maya_cmds.sets(name='ToolSeq_Select_Sets_Tmp')
					maya_cmds.select(maya_cmds.sets(setsName, subtract=setsTmp))
					maya_cmds.delete(setsName, setsTmp)
					maya_cmds.sets(name=setsName)
				else:
					maya_cmds.sets(name=setsName, empty=True)
			elif operate == 'Intersect':
				setsName = self.window.Line_SetsName.text().strip()
				if maya_cmds.objExists(setsName):
					setsTmp = maya_cmds.sets(name='ToolSeq_Select_Sets_Tmp')
					maya_cmds.select(maya_cmds.sets(setsTmp, intersection=setsName))
					maya_cmds.delete(setsName, setsTmp)
					maya_cmds.sets(name=setsName)
				else:
					maya_cmds.sets(name=setsName, empty=True)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Action_Clear(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			setsName = self.window.Line_SetsName.text().strip()
			if maya_cmds.objExists(setsName):
				maya_cmds.sets(clear=setsName)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Action_Show(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			setsName = self.window.Line_SetsName.text().strip()
			if maya_cmds.objExists(setsName):
				maya_cmds.select(setsName)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)