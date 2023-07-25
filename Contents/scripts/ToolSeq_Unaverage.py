from os.path import abspath, dirname
from sys import stderr

from PySide2.QtCore import QEvent, Qt
from PySide2.QtGui import QTextCursor
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QWidget, QComboBox, QStyledItemDelegate
from maya import cmds as maya_cmds
from maya.OpenMayaUI import MQtUtil
from shiboken2 import wrapInstance

ptrs = []

def ptrs_remove(ptr):
	if ptr in ptrs:
		ptrs.remove(ptr)

class ToolSeq_Unaverage(QWidget):

	qUiLoader = QUiLoader()
	userScriptDir = dirname(abspath(__file__)) + '/'
	qUiLoader.setWorkingDirectory(userScriptDir)

	def __init__(self):
		ptrs.append(self)
		self.windowMain = wrapInstance(int(MQtUtil.mainWindow()), QMainWindow)
		super(ToolSeq_Unaverage, self).__init__(self.windowMain)

		self.window = ToolSeq_Unaverage.qUiLoader.load(ToolSeq_Unaverage.userScriptDir + 'ui/ToolSeq_Unaverage.ui', self)
		self.window.destroyed.connect(lambda: ptrs_remove(self))
		self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
		self.window.setAttribute(Qt.WA_DeleteOnClose)
		for qComboBox in self.window.findChildren(QComboBox):
			qComboBox.setItemDelegate(QStyledItemDelegate(qComboBox))
		with open(ToolSeq_Unaverage.userScriptDir + 'ToolSeq.qss', 'r') as fileStyleSheet:
			self.window.setStyleSheet(fileStyleSheet.read())

		self.window.Widget_01.installEventFilter(self)
		self.window.Text_Items.textChanged.connect(self.Event_Items)
		self.window.Button_Apply.installEventFilter(self)

		self.window.show()
		wMax = max(self.window.Label_Amount.width(), self.window.Label_Blend.width(), self.window.Label_Iterations.width())
		self.window.Label_Amount.setFixedWidth(wMax)
		self.window.Label_Blend.setFixedWidth(wMax)
		self.window.Label_Iterations.setFixedWidth(wMax)

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
		elif sourceObjectName == 'Button_Apply':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_Apply()
		return False

	def Event_ItemsCount_1(self):
		self.window.Text_Items.setPlainText('\n'.join(maya_cmds.polyListComponentConversion(toVertex=True)) + '\n')

	def Event_ItemsCount_3(self):
		self.window.Text_Items.moveCursor(QTextCursor.End)
		self.window.Text_Items.insertPlainText('\n'.join(maya_cmds.polyListComponentConversion(toVertex=True)) + '\n')

	def Event_ItemsCount_2(self):
		self.window.Text_Items.clear()

	def Event_Items(self):
		text = self.window.Text_Items.toPlainText().strip()
		self.window.Label_ItemsCount.setText(str(text.count('\n') + 1) if text else '0')

	def Action_Apply(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			items = self.window.Text_Items.toPlainText().strip().split('\n')
			objects = list(set([items[i].split('.')[0] for i in range(len(items))]))

			amount = self.window.Int_Amount.value()
			iterations = self.window.Int_Iterations.value()
			blend = self.window.Float_Blend.value() * -1.0

			for i in range(len(objects)):
				for _ in range(iterations):
					duplicate = maya_cmds.duplicate(objects[i], returnRootsOnly=True)
					maya_cmds.polyAverageVertex([item.replace(objects[i], duplicate[0]) for item in items if objects[i] in item], caching=True, iterations=amount)
					maya_cmds.blendShape(duplicate, objects[i], envelope=blend, weight=[0, 1.0])
					maya_cmds.delete(duplicate)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)