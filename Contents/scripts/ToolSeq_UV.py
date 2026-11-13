from os.path import abspath, dirname
from sys import stderr

from PySide2.QtCore import QEvent, Qt
from PySide2.QtGui import QTextCursor
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QWidget, QComboBox, QStyledItemDelegate
from maya import cmds as maya_cmds
from maya.OpenMayaUI import MQtUtil
from shiboken2 import wrapInstance

class ToolSeq_UV(QWidget):

	userScriptDir = dirname(abspath(__file__)) + '/'

	qUiLoader = QUiLoader()
	qUiLoader.setWorkingDirectory(userScriptDir)

	windowMain = wrapInstance(int(MQtUtil.mainWindow()), QMainWindow)

	def __init__(self):
		super(ToolSeq_UV, self).__init__(ToolSeq_UV.windowMain)

		self.window = ToolSeq_UV.qUiLoader.load(ToolSeq_UV.userScriptDir + 'ui/ToolSeq_UV.ui', self)
		self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
		self.window.setAttribute(Qt.WA_DeleteOnClose)
		for qComboBox in self.window.findChildren(QComboBox):
			qComboBox.setItemDelegate(QStyledItemDelegate(qComboBox))
		with open(ToolSeq_UV.userScriptDir + 'ToolSeq.qss') as fileStyleSheet:
			self.window.setStyleSheet(fileStyleSheet.read())

		self.window.Widget_01.installEventFilter(self)
		self.window.Widget_012.installEventFilter(self)
		self.window.Text_Items.textChanged.connect(self.Event_Items)
		self.window.Combo_CutType.currentTextChanged.connect(self.Event_CutType)
		self.window.Button_Apply.installEventFilter(self)

		self.window.show()
		wMax1 = max(self.window.Check_Unfold.width(), self.window.Check_Optimize.width())
		self.window.Check_Unfold.setFixedWidth(wMax1)
		self.window.Check_Optimize.setFixedWidth(wMax1)
		wMax2 = max(self.window.Label_TileSpace.width(), self.window.Label_ShellSpace.width())
		self.window.Label_TileSpace.setFixedWidth(wMax2)
		self.window.Label_ShellSpace.setFixedWidth(wMax2)

	def eventFilter(self, source, event):
		sourceObjectName = source.objectName()
		eventType = event.type()
		if sourceObjectName == 'Widget_01':
			if eventType == QEvent.MouseButtonRelease:
				eventButton = event.button()
				if eventButton == Qt.LeftButton:
					self.Event_ItemsCount_1()
				elif eventButton == Qt.RightButton:
					self.Event_ItemsCount_3()
				elif eventButton == Qt.MiddleButton:
					self.Event_ItemsCount_2()
		elif sourceObjectName == 'Widget_012':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_ItemsCoverage()
					return True
		elif sourceObjectName == 'Button_Apply':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_Apply()
		return False

	def Event_ItemsCount_1(self):
		self.window.Text_Items.setPlainText('\n'.join(maya_cmds.polyListComponentConversion(toFace=True)) + '\n')

	def Event_ItemsCount_3(self):
		self.window.Text_Items.moveCursor(QTextCursor.End)
		self.window.Text_Items.insertPlainText('\n'.join(maya_cmds.polyListComponentConversion(toFace=True)) + '\n')

	def Event_ItemsCount_2(self):
		self.window.Text_Items.clear()

	def Event_Items(self):
		text = self.window.Text_Items.toPlainText().strip()
		self.window.Label_ItemsCount.setText(str(text.count('\n') + 1) if text else '0')
		self.Event_ItemsCoverage()

	def Event_ItemsCoverage(self):
		text = self.window.Text_Items.toPlainText().strip()
		self.window.Label_ItemCoverage.setText(' '.join(str(round(100 * i, 5)) + '%' for i in maya_cmds.polyUVCoverage(text.splitlines())) if text else '0%')

	def Event_CutType(self, text):
		if text == 'Automatic':
			self.window.Float_CutTolerance.setVisible(True)
			self.window.Line_CutName.setVisible(False)
		elif text == 'Manual':
			self.window.Float_CutTolerance.setVisible(False)
			self.window.Line_CutName.setVisible(True)

	def Action_Apply(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			items = self.window.Text_Items.toPlainText().strip().splitlines()

			if self.window.Check_Unitize.isChecked():
				maya_cmds.polyForceUV(items, unitize=True)
				maya_cmds.polyMapSewMove(items, caching=True)

			if self.window.Check_Cut.isChecked():
				cutType = self.window.Combo_CutType.currentText()
				if cutType == 'Automatic':
					maya_cmds.u3dAutoSeam(items, splitShells=self.window.Float_CutTolerance.value())
				elif cutType == 'Manual':
					maya_cmds.polyMapCut(maya_cmds.sets(self.window.Line_CutName.text().strip(), q=True))

			if self.window.Check_Unfold.isChecked():
				maya_cmds.u3dUnfold(items, iterations=self.window.Int_UnfoldIteration.value(), pack=False)

			if self.window.Check_Optimize.isChecked():
				maya_cmds.u3dOptimize(items, iterations=self.window.Int_OptimizeIteration.value())

			if self.window.Check_Layout.isChecked():
				paramRotate = {}
				if self.window.Check_LayoutRotation.isChecked():
					paramRotate = {
						'rotateStep': self.window.Float_LayoutRotationStep.value(),
						'rotateMin': self.window.Float_LayoutRotationMin.value(),
						'rotateMax': self.window.Float_LayoutRotationMax.value()
					}
				maya_cmds.u3dLayout(
					items,
					mutations=self.window.Int_LayoutIteration.value(),
					resolution=self.window.Int_LayoutResolution.value(),
					preRotateMode=self.window.Combo_LayoutAlign.currentIndex(),
					preScaleMode=1,
					tileMargin=self.window.Int_LayoutTileSpaceL.value() / float(self.window.Int_LayoutTileSpaceH.value()),
					shellSpacing=self.window.Int_LayoutShellSpaceL.value() / float(self.window.Int_LayoutShellSpaceH.value()),
					**paramRotate
				)

			self.Event_ItemsCoverage()
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)