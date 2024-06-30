from os.path import abspath, dirname
from sys import stderr

from PySide2.QtCore import QEvent, Qt
from PySide2.QtGui import QColor
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QWidget, QComboBox, QStyledItemDelegate, QListWidgetItem
from maya import cmds as maya_cmds
from maya.OpenMayaUI import MQtUtil
from shiboken2 import wrapInstance

class ToolSeq_DupNamer(QWidget):

	userScriptDir = dirname(abspath(__file__)) + '/'

	qUiLoader = QUiLoader()
	qUiLoader.setWorkingDirectory(userScriptDir)

	windowMain = wrapInstance(int(MQtUtil.mainWindow()), QMainWindow)

	def __init__(self):
		super(ToolSeq_DupNamer, self).__init__(ToolSeq_DupNamer.windowMain)

		self.window = ToolSeq_DupNamer.qUiLoader.load(ToolSeq_DupNamer.userScriptDir + 'ui/ToolSeq_DupNamer.ui', self)
		self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
		self.window.setAttribute(Qt.WA_DeleteOnClose)
		for qComboBox in self.window.findChildren(QComboBox):
			qComboBox.setItemDelegate(QStyledItemDelegate(qComboBox))
		with open(ToolSeq_DupNamer.userScriptDir + 'ToolSeq.qss', 'r') as fileStyleSheet:
			self.window.setStyleSheet(fileStyleSheet.read())

		self.window.List_IdenticalNames.itemSelectionChanged.connect(self.Action_SelectList)
		self.window.Button_AppendToList.installEventFilter(self)
		self.window.Button_ExtractFromList.installEventFilter(self)
		self.window.Button_ClearList.installEventFilter(self)
		self.window.Button_RenameAutoInList.installEventFilter(self)

		self.window.show()

	def eventFilter(self, source, event):
		sourceObjectName = source.objectName()
		eventType = event.type()
		if sourceObjectName == 'Button_AppendToList':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_AppendToList()
		elif sourceObjectName == 'Button_ExtractFromList':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_ExtractFromList()
		elif sourceObjectName == 'Button_ClearList':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_ClearList()
		elif sourceObjectName == 'Button_RenameAutoInList':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_RenameAutoInList()
		return False

	def Action_SelectList(self):
		maya_cmds.undoInfo(stateWithoutFlush=False)
		maya_cmds.select([selectedItem.text() for selectedItem in self.window.List_IdenticalNames.selectedItems()])
		maya_cmds.undoInfo(stateWithoutFlush=True)

	def Event_AppendToList(self):
		maya_cmds.undoInfo(stateWithoutFlush=False)
		try:
			selection = maya_cmds.ls(selection=True)
			maya_cmds.select(hierarchy=True)
			transforms = maya_cmds.ls(selection=True, transforms=True)
			transforms.sort(key=lambda s: s.lower())
			if self.window.Check_IgnoreInstances.isChecked():
				for i in range(len(transforms)):
					if '|' in transforms[i] and not self.window.List_IdenticalNames.findItems(transforms[i], Qt.MatchExactly):
						transformParents = maya_cmds.listRelatives(transforms[i], path=True, allParents=True)
						if (len(transformParents) if transformParents is not None else 0) <= 1:
							self.window.List_IdenticalNames.addItem(transforms[i])
			else:
				for i in range(len(transforms)):
					if '|' in transforms[i] and not self.window.List_IdenticalNames.findItems(transforms[i], Qt.MatchExactly):
						transformParents = maya_cmds.listRelatives(transforms[i], path=True, allParents=True)
						if (len(transformParents) if transformParents is not None else 0) <= 1:
							self.window.List_IdenticalNames.addItem(transforms[i])
						else:
							transformWidget = QListWidgetItem(transforms[i])
							transformWidget.setTextColor(QColor.fromRgb(255, 64, 64))
							self.window.List_IdenticalNames.addItem(transformWidget)
			self.window.Label_IdenticalNamesCount.setText(str(self.window.List_IdenticalNames.count()))
			maya_cmds.select(selection)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(stateWithoutFlush=True)

	def Event_ExtractFromList(self):
		selectedItems = self.window.List_IdenticalNames.selectedItems()
		if not selectedItems:
			return
		for i in range(len(selectedItems)):
			self.window.List_IdenticalNames.takeItem(self.window.List_IdenticalNames.row(selectedItems[i]))
		self.window.Label_IdenticalNamesCount.setText(str(self.window.List_IdenticalNames.count()))

	def Event_ClearList(self):
		self.window.List_IdenticalNames.clear()
		self.window.Label_IdenticalNamesCount.setText('0')

	def Action_RenameAutoInList(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			transforms = [self.window.List_IdenticalNames.item(i).text() for i in range(self.window.List_IdenticalNames.count())]
			transforms.sort(key=lambda s: s.count('|'))
			transforms.reverse()
			for i in range(len(transforms)):
				try:
					maya_cmds.rename(transforms[i], transforms[i].replace('|', '_'))
				except:
					print('Could not rename item: ' + transforms[i], file=stderr)
			self.Event_ClearList()
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)