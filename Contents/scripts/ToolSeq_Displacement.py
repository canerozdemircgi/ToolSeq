from os.path import abspath, dirname
from sys import stderr

from PySide2.QtCore import QEvent, Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QWidget, QComboBox, QStyledItemDelegate, QFileDialog
from maya import cmds as maya_cmds
from maya.OpenMayaUI import MQtUtil
from shiboken2 import wrapInstance

class ToolSeq_Displacement(QWidget):

	userScriptDir = dirname(abspath(__file__)) + '/'

	qUiLoader = QUiLoader()
	qUiLoader.setWorkingDirectory(userScriptDir)

	windowMain = wrapInstance(int(MQtUtil.mainWindow()), QMainWindow)

	def __init__(self):
		super(ToolSeq_Displacement, self).__init__(ToolSeq_Displacement.windowMain)

		self.window = ToolSeq_Displacement.qUiLoader.load(ToolSeq_Displacement.userScriptDir + 'ui/ToolSeq_Displacement.ui', self)
		self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
		self.window.setAttribute(Qt.WA_DeleteOnClose)
		for qComboBox in self.window.findChildren(QComboBox):
			qComboBox.setItemDelegate(QStyledItemDelegate(qComboBox))
		with open(ToolSeq_Displacement.userScriptDir + 'ToolSeq.qss') as fileStyleSheet:
			self.window.setStyleSheet(fileStyleSheet.read())

		self.window.Widget_Shape.installEventFilter(self)
		self.window.Button_ImagePath.installEventFilter(self)
		self.window.Button_Apply.installEventFilter(self)

		self.window.show()
		maya_cmds.loadPlugin('ToolSeq_Displacement.py', quiet=True)

	def eventFilter(self, source, event):
		sourceObjectName = source.objectName()
		eventType = event.type()
		if sourceObjectName == 'Widget_Shape':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_Shape()
		elif sourceObjectName == 'Button_ImagePath':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_ImagePath()
		elif sourceObjectName == 'Button_Apply':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_Apply()
		return False

	def Event_Shape(self):
		self.window.Line_Shape.setText(maya_cmds.ls(selection=True, dag=True, shapes=True)[0])

	def Event_ImagePath(self):
		self.window.Line_Image.setText(QFileDialog.getOpenFileName()[0])

	def Action_Apply(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			maya_cmds.ToolSeq_Displacement_Apply(
				shape=self.window.Line_Shape.text().strip(),
				uvName=self.window.Line_UvName.text().strip(),
				image=self.window.Line_Image.text().strip(),
				iscX=self.window.Check_X.isChecked(),
				iscY=self.window.Check_Y.isChecked(),
				iscZ=self.window.Check_Z.isChecked(),
				iscN=self.window.Check_N.isChecked(),
				chaX=self.window.Combo_RGBAX.currentIndex(),
				chaY=self.window.Combo_RGBAY.currentIndex(),
				chaZ=self.window.Combo_RGBAZ.currentIndex(),
				chaN=self.window.Combo_RGBAN.currentIndex(),
				minX=self.window.Float_MinX.value(),
				minY=self.window.Float_MinY.value(),
				minZ=self.window.Float_MinZ.value(),
				minN=self.window.Float_MinN.value(),
				maxX=self.window.Float_MaxX.value(),
				maxY=self.window.Float_MaxY.value(),
				maxZ=self.window.Float_MaxZ.value(),
				maxN=self.window.Float_MaxN.value()
			)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)