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

class ToolSeq_Freeze(QWidget):

	qUiLoader = QUiLoader()
	userScriptDir = dirname(abspath(__file__)) + '/'
	qUiLoader.setWorkingDirectory(userScriptDir)

	def __init__(self):
		ptrs.append(self)
		self.windowMain = wrapInstance(int(OpenMayaUI_v1.MQtUtil.mainWindow()), QMainWindow)
		super(ToolSeq_Freeze, self).__init__(self.windowMain)

		self.window = ToolSeq_Freeze.qUiLoader.load(ToolSeq_Freeze.userScriptDir + 'ToolSeq_Freeze.ui', self)
		self.window.destroyed.connect(lambda: ptrs_remove(self))
		self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
		self.window.setAttribute(Qt.WA_DeleteOnClose)
		for qComboBox in self.window.findChildren(QComboBox):
			qComboBox.setItemDelegate(QStyledItemDelegate(qComboBox))
		with open(ToolSeq_Freeze.userScriptDir + 'ToolSeq.qss', 'r') as fileStyleSheet:
			self.window.setStyleSheet(fileStyleSheet.read())

		self.window.Widget_01.installEventFilter(self)
		self.window.Text_Transforms.textChanged.connect(self.Event_Transforms)
		self.window.Button_ApplyTransformationMatrix.installEventFilter(self)
		self.window.Button_UnFreezeTranslate.installEventFilter(self)
		self.window.Button_UnFreezeScale.installEventFilter(self)

		self.window.show()
		maya_cmds.loadPlugin('ToolSeq_Freeze.py', quiet=True)

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
		elif sourceObjectName == 'Button_ApplyTransformationMatrix':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_ApplyTransformationMatrix()
		elif sourceObjectName == 'Button_UnFreezeTranslate':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_UnFreezeTranslate()
		elif sourceObjectName == 'Button_UnFreezeScale':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_UnFreezeScale()
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

	def Action_ApplyTransformationMatrix(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			maya_cmds.ToolSeq_Freeze_Apply(
				transforms=self.window.Text_Transforms.toPlainText().strip(),
				isMovX=self.window.Check_MovX.isChecked(),
				isMovY=self.window.Check_MovY.isChecked(),
				isMovZ=self.window.Check_MovZ.isChecked(),
				isRotX=self.window.Check_RotX.isChecked(),
				isRotY=self.window.Check_RotY.isChecked(),
				isRotZ=self.window.Check_RotZ.isChecked(),
				isScaX=self.window.Check_ScaX.isChecked(),
				isScaY=self.window.Check_ScaY.isChecked(),
				isScaZ=self.window.Check_ScaZ.isChecked(),
				movX=self.window.Float_MovX.value(),
				movY=self.window.Float_MovY.value(),
				movZ=self.window.Float_MovZ.value(),
				rotX=self.window.Float_RotX.value(),
				rotY=self.window.Float_RotY.value(),
				rotZ=self.window.Float_RotZ.value(),
				scaX=self.window.Float_ScaX.value(),
				scaY=self.window.Float_ScaY.value(),
				scaZ=self.window.Float_ScaZ.value()
			)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Action_UnFreezeTranslate(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			transforms = self.window.Text_Transforms.toPlainText().strip().split('\n')
			pivotTypeText = self.window.Combo_UnFreezeTranslate.currentText()
			pivotType = {}
			if pivotTypeText == 'RotPiv':
				pivotType = {'rotatePivot': True}
			elif pivotTypeText == 'ScaPiv':
				pivotType = {'scalePivot': True}
			for i in range(len(transforms)):
				pivot = maya_cmds.xform(transforms[i], q=True, worldSpace=True, **pivotType)
				maya_cmds.ToolSeq_Freeze_Apply(
					transforms=transforms[i],
					isMovX=True,
					isMovY=True,
					isMovZ=True,
					movX=pivot[0],
					movY=pivot[1],
					movZ=pivot[2]
				)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Action_UnFreezeScale(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			transforms = self.window.Text_Transforms.toPlainText().strip().split('\n')
			isConsiderRot = self.window.Check_ConsiderRot.isChecked()
			selection = []
			if isConsiderRot:
				selection = maya_cmds.ls(selection=True)
				duplicates = maya_cmds.duplicate(transforms)
				for i in range(len(duplicates)):
					maya_cmds.setAttr(duplicates[i] + '.rotateX', 0)
					maya_cmds.setAttr(duplicates[i] + '.rotateY', 0)
					maya_cmds.setAttr(duplicates[i] + '.rotateZ', 0)
			else:
				duplicates = transforms

			for i in range(len(transforms)):
				boundaries = maya_cmds.exactWorldBoundingBox(duplicates[i], calculateExactly=True)
				maya_cmds.ToolSeq_Freeze_Apply(
					transforms=transforms[i],
					isScaX=True,
					isScaY=True,
					isScaZ=True,
					scaX=boundaries[3] - boundaries[0],
					scaY=boundaries[4] - boundaries[1],
					scaZ=boundaries[5] - boundaries[2]
				)

			if isConsiderRot:
				maya_cmds.delete(duplicates)
				maya_cmds.select(selection)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)