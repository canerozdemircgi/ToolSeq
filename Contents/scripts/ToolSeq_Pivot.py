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

class ToolSeq_Pivot(QWidget):

	qUiLoader = QUiLoader()
	userScriptDir = dirname(abspath(__file__)) + '/'
	qUiLoader.setWorkingDirectory(userScriptDir)

	def __init__(self):
		ptrs.append(self)
		self.windowMain = wrapInstance(int(OpenMayaUI_v1.MQtUtil.mainWindow()), QMainWindow)
		super(ToolSeq_Pivot, self).__init__(self.windowMain)

		self.window = ToolSeq_Pivot.qUiLoader.load(ToolSeq_Pivot.userScriptDir + 'ToolSeq_Pivot.ui', self)
		self.window.destroyed.connect(lambda: ptrs_remove(self))
		self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
		self.window.setAttribute(Qt.WA_DeleteOnClose)
		for qComboBox in self.window.findChildren(QComboBox):
			qComboBox.setItemDelegate(QStyledItemDelegate(qComboBox))
		with open(ToolSeq_Pivot.userScriptDir + 'ToolSeq.qss', 'r') as fileStyleSheet:
			self.window.setStyleSheet(fileStyleSheet.read())

		self.window.Widget_01.installEventFilter(self)
		self.window.Text_Transforms.textChanged.connect(self.Event_Transforms)
		self.window.Button_Minimum.installEventFilter(self)
		self.window.Button_Maximum.installEventFilter(self)
		self.window.Button_Center.installEventFilter(self)
		self.window.Button_CreateLocators.installEventFilter(self)
		self.window.Widget_Locator.installEventFilter(self)
		self.window.Button_MoveTransformsPivot.installEventFilter(self)
		self.window.Button_MatchTransformsPivot.installEventFilter(self)

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
		elif sourceObjectName == 'Button_Minimum':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_Minimum()
		elif sourceObjectName == 'Button_Maximum':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_Maximum()
		elif sourceObjectName == 'Button_Center':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_Center()
		elif sourceObjectName == 'Button_CreateLocators':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_CreateLocators()
		elif sourceObjectName == 'Widget_Locator':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_Locator()
		elif sourceObjectName == 'Button_MoveTransformsPivot':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_MoveTransformsPivot()
		elif sourceObjectName == 'Button_MatchTransformsPivot':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_MatchTransformsPivot()
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

	def Action_Minimum(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			transforms = self.window.Text_Transforms.toPlainText().strip().split('\n')
			checkX = self.window.Check_X.isChecked()
			checkY = self.window.Check_Y.isChecked()
			checkZ = self.window.Check_Z.isChecked()

			checkRotate = self.window.Check_MinMaxCenRotPiv.isChecked()
			checkScale = self.window.Check_MinMaxCenScaPiv.isChecked()

			for i in range(len(transforms)):
				boundaries = maya_cmds.exactWorldBoundingBox(transforms[i], calculateExactly=True)
				rotatePivotObj = transforms[i] + '.rotatePivot'
				scalePivotObj = transforms[i] + '.scalePivot'
				if checkX:
					if checkRotate:
						maya_cmds.move(boundaries[0], 0, 0, rotatePivotObj, absolute=True, x=True)
					if checkScale:
						maya_cmds.move(boundaries[0], 0, 0, scalePivotObj, absolute=True, x=True)
				if checkY:
					if checkRotate:
						maya_cmds.move(boundaries[1], 0, 0, rotatePivotObj, absolute=True, y=True)
					if checkScale:
						maya_cmds.move(boundaries[1], 0, 0, scalePivotObj, absolute=True, y=True)
				if checkZ:
					if checkRotate:
						maya_cmds.move(boundaries[2], 0, 0, rotatePivotObj, absolute=True, z=True)
					if checkScale:
						maya_cmds.move(boundaries[2], 0, 0, scalePivotObj, absolute=True, z=True)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Action_Maximum(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			transforms = self.window.Text_Transforms.toPlainText().strip().split('\n')
			checkX = self.window.Check_X.isChecked()
			checkY = self.window.Check_Y.isChecked()
			checkZ = self.window.Check_Z.isChecked()

			checkRotate = self.window.Check_MinMaxCenRotPiv.isChecked()
			checkScale = self.window.Check_MinMaxCenScaPiv.isChecked()

			for i in range(len(transforms)):
				boundaries = maya_cmds.exactWorldBoundingBox(transforms[i], calculateExactly=True)
				rotatePivotObj = transforms[i] + '.rotatePivot'
				scalePivotObj = transforms[i] + '.scalePivot'
				if checkX:
					if checkRotate:
						maya_cmds.move(boundaries[3], 0, 0, rotatePivotObj, absolute=True, x=True)
					if checkScale:
						maya_cmds.move(boundaries[3], 0, 0, scalePivotObj, absolute=True, x=True)
				if checkY:
					if checkRotate:
						maya_cmds.move(boundaries[4], 0, 0, rotatePivotObj, absolute=True, y=True)
					if checkScale:
						maya_cmds.move(boundaries[4], 0, 0, scalePivotObj, absolute=True, y=True)
				if checkZ:
					if checkRotate:
						maya_cmds.move(boundaries[5], 0, 0, rotatePivotObj, absolute=True, z=True)
					if checkScale:
						maya_cmds.move(boundaries[5], 0, 0, scalePivotObj, absolute=True, z=True)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Action_Center(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			transforms = self.window.Text_Transforms.toPlainText().strip().split('\n')
			checkX = self.window.Check_X.isChecked()
			checkY = self.window.Check_Y.isChecked()
			checkZ = self.window.Check_Z.isChecked()

			checkRotate = self.window.Check_MinMaxCenRotPiv.isChecked()
			checkScale = self.window.Check_MinMaxCenScaPiv.isChecked()

			for i in range(len(transforms)):
				boundaries = maya_cmds.exactWorldBoundingBox(transforms[i], calculateExactly=True)
				rotatePivotObj = transforms[i] + '.rotatePivot'
				scalePivotObj = transforms[i] + '.scalePivot'
				if checkX:
					if checkRotate:
						maya_cmds.move((boundaries[0] + boundaries[3]) / 2.0, 0, 0, rotatePivotObj, absolute=True, x=True)
					if checkScale:
						maya_cmds.move((boundaries[0] + boundaries[3]) / 2.0, 0, 0, scalePivotObj, absolute=True, x=True)
				if checkY:
					if checkRotate:
						maya_cmds.move((boundaries[1] + boundaries[4]) / 2.0, 0, 0, rotatePivotObj, absolute=True, y=True)
					if checkScale:
						maya_cmds.move((boundaries[1] + boundaries[4]) / 2.0, 0, 0, scalePivotObj, absolute=True, y=True)
				if checkZ:
					if checkRotate:
						maya_cmds.move((boundaries[2] + boundaries[5]) / 2.0, 0, 0, rotatePivotObj, absolute=True, z=True)
					if checkScale:
						maya_cmds.move((boundaries[2] + boundaries[5]) / 2.0, 0, 0, scalePivotObj, absolute=True, z=True)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Action_CreateLocators(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			transforms = self.window.Text_Transforms.toPlainText().strip().split('\n')
			checkX = self.window.Check_X.isChecked()
			checkY = self.window.Check_Y.isChecked()
			checkZ = self.window.Check_Z.isChecked()

			pivotTypeText = self.window.Combo_CreateLocatorsType.currentText()
			pivotType = {}
			if pivotTypeText == 'RotPiv':
				pivotType = {'rotatePivot': True}
			elif pivotTypeText == 'ScaPiv':
				pivotType = {'scalePivot': True}

			for i in range(len(transforms)):
				locator = maya_cmds.spaceLocator(name='ToolSeq_Pivot_Locator_01')
				pivot = maya_cmds.xform(transforms[i], q=True, worldSpace=True, **pivotType)
				if checkX:
					maya_cmds.move(pivot[0], 0, 0, locator, absolute=True, x=True)
				if checkY:
					maya_cmds.move(pivot[1], 0, 0, locator, absolute=True, y=True)
				if checkZ:
					maya_cmds.move(pivot[2], 0, 0, locator, absolute=True, z=True)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Event_Locator(self):
		self.window.Line_Locator.setText(maya_cmds.ls(selection=True, transforms=True)[0])

	def Action_MoveTransformsPivot(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			transforms = self.window.Text_Transforms.toPlainText().strip().split('\n')
			checkX = self.window.Check_X.isChecked()
			checkY = self.window.Check_Y.isChecked()
			checkZ = self.window.Check_Z.isChecked()

			locator = self.window.Line_Locator.text().strip()
			checkRotate = self.window.Check_MoveTransformsPivotRotPiv.isChecked()
			checkScale = self.window.Check_MoveTransformsPivotScaPiv.isChecked()
			rotatePivot = maya_cmds.xform(locator, q=True, worldSpace=True, rotatePivot=True)
			scalePivot = maya_cmds.xform(locator, q=True, worldSpace=True, scalePivot=True)

			for i in range(len(transforms)):
				rotatePivotObj = transforms[i] + '.rotatePivot'
				scalePivotObj = transforms[i] + '.scalePivot'
				if checkX:
					if checkRotate:
						maya_cmds.move(rotatePivot[0], 0, 0, rotatePivotObj, absolute=True, x=True)
					if checkScale:
						maya_cmds.move(scalePivot[0], 0, 0, scalePivotObj, absolute=True, x=True)
				if checkY:
					if checkRotate:
						maya_cmds.move(rotatePivot[1], 0, 0, rotatePivotObj, absolute=True, y=True)
					if checkScale:
						maya_cmds.move(scalePivot[1], 0, 0, scalePivotObj, absolute=True, y=True)
				if checkZ:
					if checkRotate:
						maya_cmds.move(rotatePivot[2], 0, 0, rotatePivotObj, absolute=True, z=True)
					if checkScale:
						maya_cmds.move(scalePivot[2], 0, 0, scalePivotObj, absolute=True, z=True)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Action_MatchTransformsPivot(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			transforms = self.window.Text_Transforms.toPlainText().strip().split('\n')
			checkX = self.window.Check_X.isChecked()
			checkY = self.window.Check_Y.isChecked()
			checkZ = self.window.Check_Z.isChecked()

			locator = self.window.Line_Locator.text().strip()
			pivotTypeText = self.window.Combo_MatchTransformsPivotType.currentText()
			pivotType = {}
			pivot = []
			if pivotTypeText == 'RotPiv':
				pivotType = {'rotatePivotRelative': True}
				pivot = maya_cmds.xform(locator, q=True, worldSpace=True, rotatePivot=True)
			elif pivotTypeText == 'ScaPiv':
				pivotType = {'scalePivotRelative': True}
				pivot = maya_cmds.xform(locator, q=True, worldSpace=True, scalePivot=True)

			for i in range(len(transforms)):
				if checkX:
					maya_cmds.move(pivot[0], 0, 0, transforms[i], x=True, **pivotType)
				if checkY:
					maya_cmds.move(pivot[1], 0, 0, transforms[i], y=True, **pivotType)
				if checkZ:
					maya_cmds.move(pivot[2], 0, 0, transforms[i], z=True, **pivotType)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)