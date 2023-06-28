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

class ToolSeq_Uninstance(QWidget):

	qUiLoader = QUiLoader()
	userScriptDir = dirname(abspath(__file__)) + '/'
	qUiLoader.setWorkingDirectory(userScriptDir)

	def __init__(self):
		ptrs.append(self)
		self.windowMain = wrapInstance(int(OpenMayaUI_v1.MQtUtil.mainWindow()), QMainWindow)
		super(ToolSeq_Uninstance, self).__init__(self.windowMain)

		self.window = ToolSeq_Uninstance.qUiLoader.load(ToolSeq_Uninstance.userScriptDir + 'ToolSeq_Uninstance.ui', self)
		self.window.destroyed.connect(lambda: ptrs_remove(self))
		self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
		self.window.setAttribute(Qt.WA_DeleteOnClose)
		for qComboBox in self.window.findChildren(QComboBox):
			qComboBox.setItemDelegate(QStyledItemDelegate(qComboBox))
		with open(ToolSeq_Uninstance.userScriptDir + 'ToolSeq.qss', 'r') as fileStyleSheet:
			self.window.setStyleSheet(fileStyleSheet.read())

		self.window.Widget_01.installEventFilter(self)
		self.window.Text_Transforms.textChanged.connect(self.Event_Transforms)
		self.window.Button_UninstanceHierarchy.installEventFilter(self)
		self.window.Widget_SourceShape.installEventFilter(self)
		self.window.Widget_TargetShape.installEventFilter(self)
		self.window.Button_AddInstancedShape.installEventFilter(self)
		self.window.Button_ReplaceInstancedShape.installEventFilter(self)

		self.window.show()

	def eventFilter(self, source, event):
		sourceObjectName = source.objectName()
		eventType = event.type()
		if sourceObjectName == 'Widget_01':
			if eventType == QEvent.MouseButtonRelease:
				eventButton = event.button()
				if eventButton == Qt.LeftButton:
					self.Event_TransformsCount_1()
				elif eventButton == Qt.RightButton:
					self.Event_TransformsCount_3()
				elif eventButton == Qt.MiddleButton:
					self.Event_TransformsCount_2()
		elif sourceObjectName == 'Button_UninstanceHierarchy':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_UninstanceHierarchy()
		elif sourceObjectName == 'Widget_SourceShape':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_SourceShape()
		elif sourceObjectName == 'Widget_TargetShape':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_TargetShape()
		elif sourceObjectName == 'Button_AddInstancedShape':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Activity_AddInstancedShape()
		elif sourceObjectName == 'Button_ReplaceInstancedShape':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Activity_ReplaceInstancedShape()
		return False

	def Event_TransformsCount_1(self):
		self.window.Text_Transforms.setPlainText('\n'.join(maya_cmds.ls(selection=True, transforms=True)) + '\n')

	def Event_TransformsCount_3(self):
		self.window.Text_Transforms.moveCursor(QTextCursor.End)
		self.window.Text_Transforms.insertPlainText('\n'.join(maya_cmds.ls(selection=True, transforms=True)) + '\n')

	def Event_TransformsCount_2(self):
		self.window.Text_Transforms.clear()

	def Event_Transforms(self):
		text = self.window.Text_Transforms.toPlainText().strip()
		self.window.Label_TransformsCount.setText(str(text.count('\n') + 1) if text else '0')

	def Action_UninstanceHierarchy(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			maya_cmds.select(self.window.Text_Transforms.toPlainText().strip().split('\n'), hierarchy=True)
			transforms = maya_cmds.ls(long=True, selection=True, transforms=True)
			transforms.sort(key=lambda s: s.count('|'))

			if self.window.Check_KeepOld.isChecked():
				transformsTmp = []
				level = transforms[0].count('|')
				levelFirst = True
				while len(transforms) > 0:
					if level == transforms[0].count('|'):
						duplicate = maya_cmds.duplicate(transforms[0], returnRootsOnly=True)
						if not levelFirst:
							maya_cmds.delete(transforms[0])
							duplicate = [maya_cmds.rename(duplicate[0], transforms[0].split('|')[-1])]
						transformsTmp.append(duplicate[0])
						del transforms[0]
					else:
						level = transforms[0].count('|')
						levelFirst = False
						maya_cmds.select(transformsTmp, hierarchy=True)
						maya_cmds.select(transformsTmp, deselect=True)
						transformsTmp = []
						transforms = maya_cmds.ls(long=True, selection=True, transforms=True)
						transforms.sort(key=lambda s: s.count('|'))
			else:
				for i in range(len(transforms)):
					duplicate = maya_cmds.duplicate(transforms[i], returnRootsOnly=True)
					maya_cmds.delete(transforms[i])
					maya_cmds.rename(duplicate[0], transforms[i].split('|')[-1])
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Event_SourceShape(self):
		self.window.Line_SourceShape.setText(maya_cmds.ls(selection=True, dag=True, objectsOnly=True, shapes=True)[0])

	def Event_TargetShape(self):
		self.window.Line_TargetShape.setText(maya_cmds.ls(selection=True, dag=True, objectsOnly=True, shapes=True)[0])

	def Activity_AddInstancedShape(self):
		self.Action_ModifyInstancedShape(False)

	def Activity_ReplaceInstancedShape(self):
		self.Action_ModifyInstancedShape(True)

	def Action_ModifyInstancedShape(self, deleteOriginal):
		maya_cmds.undoInfo(openChunk=True)
		try:
			shapeSource = self.window.Line_SourceShape.text().strip()
			shapeTarget = self.window.Line_TargetShape.text().strip()
			parentSource = maya_cmds.listRelatives(shapeSource, path=True, parent=True)
			parentsTarget = maya_cmds.listRelatives(shapeTarget, path=True, allParents=True)
			for i in range(len(parentsTarget)):
				instanceSource = maya_cmds.instance(parentSource)
				instanceSourceChildrens = maya_cmds.listRelatives(instanceSource, path=True, children=True)
				for j in range(len(instanceSourceChildrens)):
					if parentsTarget[i] not in maya_cmds.listRelatives(instanceSourceChildrens[j], path=True, allParents=True):
						maya_cmds.parent(instanceSourceChildrens[j], parentsTarget[i], shape=True, relative=True)
				maya_cmds.delete(instanceSource)
			if deleteOriginal:
				maya_cmds.delete(shapeTarget)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)