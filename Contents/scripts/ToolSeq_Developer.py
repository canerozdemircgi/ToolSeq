import re
from inspect import getmembers
from os.path import abspath, dirname
from threading import Thread

from PySide2.QtCore import QEvent, Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QWidget, QComboBox, QStyledItemDelegate
from maya import cmds as maya_cmds
from maya.OpenMayaUI import MQtUtil
from maya.mel import eval as mel_eval
from shiboken2 import wrapInstance

class ToolSeq_Developer(QWidget):

	userScriptDir = dirname(abspath(__file__)) + '/'

	qUiLoader = QUiLoader()
	qUiLoader.setWorkingDirectory(userScriptDir)

	windowMain = wrapInstance(int(MQtUtil.mainWindow()), QMainWindow)

	isFirstInit = True

	def __init__(self):
		super(ToolSeq_Developer, self).__init__(ToolSeq_Developer.windowMain)

		self.window = ToolSeq_Developer.qUiLoader.load(ToolSeq_Developer.userScriptDir + 'ui/ToolSeq_Developer.ui', self)
		self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
		self.window.setAttribute(Qt.WA_DeleteOnClose)
		for qComboBox in self.window.findChildren(QComboBox):
			qComboBox.setItemDelegate(QStyledItemDelegate(qComboBox))
		with open(ToolSeq_Developer.userScriptDir + 'ToolSeq.qss', 'r') as fileStyleSheet:
			self.window.setStyleSheet(fileStyleSheet.read())

		self.window.Radio_Attributes.released.connect(self.Event_Attributes_1)
		self.window.Radio_Attributes.toggled.connect(self.Event_Attributes_2)
		self.window.Radio_CommandsMel.toggled.connect(self.Event_CommandsMel)
		self.window.Radio_CommandsPython.toggled.connect(self.Event_CommandsPython)
		self.window.Radio_VariablesMel.toggled.connect(self.Event_Variables)
		self.window.Line_Attributes.installEventFilter(self)
		self.window.Line_Search.installEventFilter(self)
		self.window.Button_Search.installEventFilter(self)
		self.window.Button_Act.installEventFilter(self)

		self.window.setEnabled(False)
		self.window.show()
		Thread(target=self.__init__later, args=()).start()

	def __init__later(self):
		self.attributes = []
		if ToolSeq_Developer.isFirstInit:
			ToolSeq_Developer.commandsMel = sorted(maya_cmds.melInfo(), key=lambda sMel: sMel.lower())
			ToolSeq_Developer.commandsPython = sorted([s[0] for s in getmembers(maya_cmds, callable)], key=lambda sPyt: sPyt.lower())
			ToolSeq_Developer.variables = sorted(mel_eval('env'), key=lambda sVar: sVar.lower())
			ToolSeq_Developer.isFirstInit = False

		self.listPtr = ToolSeq_Developer.commandsMel

		self.__init__later_callback()

	def __init__later_callback(self):
		self.window.Label_CountAll.setText(str(len(ToolSeq_Developer.commandsMel)))
		self.window.setEnabled(True)

	def eventFilter(self, source, event):
		sourceObjectName = source.objectName()
		eventType = event.type()
		if sourceObjectName == 'Line_Attributes':
			if eventType == QEvent.KeyRelease:
				eventKey = event.key()
				if eventKey == Qt.Key_Return or eventKey == Qt.Key_Enter:
					self.Event_AttributesRefresh()
		elif sourceObjectName == 'Line_Search':
			if eventType == QEvent.KeyRelease:
				eventKey = event.key()
				if eventKey == Qt.Key_Return or eventKey == Qt.Key_Enter:
					self.Event_Search()
		elif sourceObjectName == 'Button_Search':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_Search()
		elif sourceObjectName == 'Button_Act':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_Act()
		return False

	def Event_Attributes_1(self):
		self.window.Line_Attributes.setText(maya_cmds.ls(selection=True, objectsOnly=True)[0])

	def Event_Attributes_2(self, checked):
		if checked:
			self.window.Label_CountAll.setText(str(len(self.attributes)))
			self.window.Text_Results.clear()
			self.window.Label_CountFiltered.setText('0')
			self.window.Button_Act.setText('Preview')
			self.listPtr = self.attributes

	def Event_CommandsMel(self, checked):
		if checked:
			self.window.Label_CountAll.setText(str(len(ToolSeq_Developer.commandsMel)))
			self.window.Text_Results.clear()
			self.window.Label_CountFiltered.setText('0')
			self.window.Button_Act.setText('Help')
			self.listPtr = ToolSeq_Developer.commandsMel

	def Event_CommandsPython(self, checked):
		if checked:
			self.window.Label_CountAll.setText(str(len(ToolSeq_Developer.commandsPython)))
			self.window.Text_Results.clear()
			self.window.Label_CountFiltered.setText('0')
			self.window.Button_Act.setText('Help')
			self.listPtr = ToolSeq_Developer.commandsPython

	def Event_Variables(self, checked):
		if checked:
			self.window.Label_CountAll.setText(str(len(ToolSeq_Developer.variables)))
			self.window.Text_Results.clear()
			self.window.Label_CountFiltered.setText('0')
			self.window.Button_Act.setText('Preview')
			self.listPtr = ToolSeq_Developer.variables

	def Event_AttributesRefresh(self):
		try:
			self.attributes = sorted(maya_cmds.listAttr(self.window.Line_Attributes.text().strip(), write=self.window.Check_Writable.isChecked()), key=lambda sAtt: sAtt.lower())
		except:
			self.attributes = []
		self.Event_Attributes_2(True)

	def Event_Search(self):
		self.window.Text_Results.clear()
		if self.window.Check_Regex.isChecked():
			if self.window.Check_CaseSensitive.isChecked():
				searchRe = re.compile(self.window.Line_Search.text().strip())
			else:
				searchRe = re.compile(self.window.Line_Search.text().strip(), re.IGNORECASE)
			result = [self.listPtr[i] for i in range(len(self.listPtr)) if searchRe.search(self.listPtr[i])]
		else:
			if self.window.Check_CaseSensitive.isChecked():
				searchStr = self.window.Line_Search.text().strip()
				result = [self.listPtr[i] for i in range(len(self.listPtr)) if searchStr in self.listPtr[i]]
			else:
				searchStr = self.window.Line_Search.text().strip().lower()
				result = [self.listPtr[i] for i in range(len(self.listPtr)) if searchStr in self.listPtr[i].lower()]
		self.window.Text_Results.setPlainText('\n'.join(result))
		self.window.Label_CountFiltered.setText(str(len(result)))

	def Event_Act(self):
		text = self.window.Text_Results.textCursor().selectedText().strip()
		if text == '':
			return

		if self.window.Radio_Attributes.isChecked():
			print('%s = %s' % (text, maya_cmds.getAttr(self.window.Line_Attributes.text().strip() + '.' + text)))
		elif self.window.Radio_CommandsMel.isChecked() or self.window.Radio_CommandsPython.isChecked():
			try:
				print(maya_cmds.help(text))
			except RuntimeError:
				print(mel_eval('whatIs ' + text))
		elif self.window.Radio_VariablesMel.isChecked():
			print('%s = %s' % (text, mel_eval('$tmp=' + text)))