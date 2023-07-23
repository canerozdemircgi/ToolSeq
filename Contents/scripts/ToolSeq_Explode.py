from random import uniform
from sys import stderr

from PySide2.QtCore import QEvent, Qt
from PySide2.QtGui import QTextCursor
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QWidget, QComboBox, QStyledItemDelegate
from maya import OpenMayaUI as OpenMayaUI_v1
from maya import cmds as maya_cmds
from shiboken2 import wrapInstance
from os.path import abspath, dirname

ptrs = []

def ptrs_remove(ptr):
	if ptr in ptrs:
		ptrs.remove(ptr)

class ToolSeq_Explode(QWidget):

	qUiLoader = QUiLoader()
	userScriptDir = dirname(abspath(__file__)) + '/'
	qUiLoader.setWorkingDirectory(userScriptDir)

	def __init__(self):
		ptrs.append(self)
		self.windowMain = wrapInstance(int(OpenMayaUI_v1.MQtUtil.mainWindow()), QMainWindow)
		super(ToolSeq_Explode, self).__init__(self.windowMain)

		self.window = ToolSeq_Explode.qUiLoader.load(ToolSeq_Explode.userScriptDir + 'ToolSeq_Explode.ui', self)
		self.window.destroyed.connect(lambda: ptrs_remove(self))
		self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
		self.window.setAttribute(Qt.WA_DeleteOnClose)
		for qComboBox in self.window.findChildren(QComboBox):
			qComboBox.setItemDelegate(QStyledItemDelegate(qComboBox))
		with open(ToolSeq_Explode.userScriptDir + 'ToolSeq.qss', 'r') as fileStyleSheet:
			self.window.setStyleSheet(fileStyleSheet.read())

		self.window.Widget_GroupLowCount.installEventFilter(self)
		self.window.Widget_GroupHigCount.installEventFilter(self)
		self.window.Text_GroupLow.textChanged.connect(self.Event_GroupLow)
		self.window.Text_GroupHig.textChanged.connect(self.Event_GroupHig)
		self.window.Button_Apply.installEventFilter(self)
		self.window.Button_Revert.installEventFilter(self)

		self.groupLow = []
		self.groupHig = []
		self.pivotLow = []
		self.pivotHig = []

		self.groupLowChi = []
		self.groupHigChi = []
		self.pivotLowChi = []
		self.pivotHigChi = []

		self.window.show()

	def eventFilter(self, source, event):
		sourceObjectName = source.objectName()
		eventType = event.type()
		if sourceObjectName == 'Widget_GroupLowCount':
			if eventType == QEvent.MouseButtonRelease:
				eventButton = event.button()
				if eventButton == Qt.LeftButton:
					self.Event_GroupLowCount_1()
				elif eventButton == Qt.RightButton:
					self.Event_GroupLowCount_3()
				elif eventButton == Qt.MiddleButton:
					self.Event_GroupLowCount_2()
		elif sourceObjectName == 'Widget_GroupHigCount':
			if eventType == QEvent.MouseButtonRelease:
				eventButton = event.button()
				if eventButton == Qt.LeftButton:
					self.Event_GroupHigCount_1()
				elif eventButton == Qt.RightButton:
					self.Event_GroupHigCount_3()
				elif eventButton == Qt.MiddleButton:
					self.Event_GroupHigCount_2()
		elif sourceObjectName == 'Button_Apply':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_Apply()
		elif sourceObjectName == 'Button_Revert':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_Revert()
		return False

	def Event_GroupLowCount_1(self):
		self.window.Text_GroupLow.setPlainText('\n'.join(maya_cmds.ls(selection=True, transforms=True)) + '\n')

	def Event_GroupHigCount_1(self):
		self.window.Text_GroupHig.setPlainText('\n'.join(maya_cmds.ls(selection=True, transforms=True)) + '\n')

	def Event_GroupLowCount_3(self):
		self.window.Text_GroupLow.moveCursor(QTextCursor.End)
		self.window.Text_GroupLow.insertPlainText('\n'.join(maya_cmds.ls(selection=True, transforms=True)) + '\n')

	def Event_GroupHigCount_3(self):
		self.window.Text_GroupHig.moveCursor(QTextCursor.End)
		self.window.Text_GroupHig.insertPlainText('\n'.join(maya_cmds.ls(selection=True, transforms=True)) + '\n')

	def Event_GroupLowCount_2(self):
		self.window.Text_GroupLow.clear()

	def Event_GroupHigCount_2(self):
		self.window.Text_GroupHig.clear()

	def Event_GroupLow(self):
		textLow = self.window.Text_GroupLow.toPlainText().strip()
		self.window.Label_GroupLowCount.setText(str(textLow.count('\n') + 1) if textLow else '0')

	def Event_GroupHig(self):
		textHig = self.window.Text_GroupHig.toPlainText().strip()
		self.window.Label_GroupHigCount.setText(str(textHig.count('\n') + 1) if textHig else '0')

	def Action_Apply(self):
		self.window.Button_Apply.setEnabled(False)
		self.window.Button_Revert.setEnabled(True)

		maya_cmds.undoInfo(openChunk=True)
		try:
			self.groupLow = maya_cmds.listRelatives(self.window.Text_GroupLow.toPlainText().strip().split('\n'), path=True, children=True, type='transform')
			self.groupHig = maya_cmds.listRelatives(self.window.Text_GroupHig.toPlainText().strip().split('\n'), path=True, children=True, type='transform')
			if len(self.groupLow) != len(self.groupHig):
				raise TypeError('Children Of Transforms Does Not Match between Low Groups and High Groups')

			self.groupLowChi = maya_cmds.listRelatives(self.groupLow, path=True, allDescendents=True, type='transform')
			self.pivotLowChi = []
			for i in range(len(self.groupLowChi)):
				self.pivotLowChi.append(maya_cmds.xform(self.groupLowChi[i], q=True, worldSpace=True, rotatePivot=True))

			self.groupHigChi = maya_cmds.listRelatives(self.groupHig, path=True, allDescendents=True, type='transform')
			self.pivotHigChi = []
			for i in range(len(self.groupHigChi)):
				self.pivotHigChi.append(maya_cmds.xform(self.groupHigChi[i], q=True, worldSpace=True, rotatePivot=True))

			xMin = self.window.Float_XMin.value()
			xMax = self.window.Float_XMax.value()
			yMin = self.window.Float_YMin.value()
			yMax = self.window.Float_YMax.value()
			zMin = self.window.Float_ZMin.value()
			zMax = self.window.Float_ZMax.value()

			self.pivotLow = []
			self.pivotHig = []
			for i in range(len(self.groupLow)):
				self.pivotLow.append(maya_cmds.xform(self.groupLow[i], q=True, worldSpace=True, rotatePivot=True))
				self.pivotHig.append(maya_cmds.xform(self.groupHig[i], q=True, worldSpace=True, rotatePivot=True))
				maya_cmds.move(uniform(xMin, xMax), uniform(yMin, yMax), uniform(zMin, zMax), self.groupLow[i], self.groupHig[i], relative=True)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Action_Revert(self):
		self.window.Button_Apply.setEnabled(True)
		self.window.Button_Revert.setEnabled(False)

		maya_cmds.undoInfo(openChunk=True)
		try:
			for i in range(len(self.groupLow)):
				maya_cmds.move(self.pivotLow[i][0], self.pivotLow[i][1], self.pivotLow[i][2], self.groupLow[i], rotatePivotRelative=True)
				maya_cmds.move(self.pivotHig[i][0], self.pivotHig[i][1], self.pivotHig[i][2], self.groupHig[i], rotatePivotRelative=True)

			for i in range(len(self.groupLowChi)):
				maya_cmds.move(self.pivotLowChi[i][0], self.pivotLowChi[i][1], self.pivotLowChi[i][2], self.groupLowChi[i], rotatePivotRelative=True)
			for i in range(len(self.groupHigChi)):
				maya_cmds.move(self.pivotHigChi[i][0], self.pivotHigChi[i][1], self.pivotHigChi[i][2], self.groupHigChi[i], rotatePivotRelative=True)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)