import random as randomlib
from colorsys import hsv_to_rgb, hls_to_rgb
from itertools import chain
from math import floor
from operator import add as operator_add, mul as operator_mul
from os.path import abspath, dirname
from re import compile as re_compile, split as re_split
from sys import stderr

from PySide2.QtCore import QEvent, Qt
from PySide2.QtGui import QFont, QTextCursor, QFontMetricsF
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QWidget, QComboBox, QStyledItemDelegate, QAction
from maya import cmds as maya_cmds
from maya.OpenMayaUI import MQtUtil
from maya.mel import eval as mel_eval
from shiboken2 import wrapInstance

class ToolSeq_Random(object):

	def __init__(self, randoms):
		self.randoms = randoms
		self.randomsLen = len(self.randoms)
		self.index = -1

	def Get(self):
		self.index += 1
		return self.randoms[self.index]

def ToolSeq_Randomizer_Commands(_ITEM, _RANDOM):
	pass

class ToolSeq_Randomizer(QWidget):

	userScriptDir = dirname(abspath(__file__)) + '/'

	qUiLoader = QUiLoader()
	qUiLoader.setWorkingDirectory(userScriptDir)

	windowMain = wrapInstance(int(MQtUtil.mainWindow()), QMainWindow)
	operations = ['movX', 'movY', 'movZ', 'movN', 'rotX', 'rotY', 'rotZ', 'scaX', 'scaY', 'scaZ']

	@staticmethod
	def natural(s, _nsre=re_compile('([0-9]+)')):
		return [int(text) if text.isdigit() else text.lower() for text in _nsre.split(s)]

	@staticmethod
	def fmod(x, y):
		return abs(x - y * floor(x / y))

	@staticmethod
	def operator_sec(_, b):
		return b

	@staticmethod
	def hsl_to_rgb(h, s, l):
		return hls_to_rgb(h, l, s)

	@staticmethod
	def random_sample_iordered(population, k):
		indexes = set(randomlib.sample(range(len(population)), k))
		return [x for i, x in enumerate(population) if i in indexes]

	def __init__(self, state=None):
		super(ToolSeq_Randomizer, self).__init__(ToolSeq_Randomizer.windowMain)

		self.window = ToolSeq_Randomizer.qUiLoader.load(ToolSeq_Randomizer.userScriptDir + 'ui/ToolSeq_Randomizer.ui', self)
		self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
		self.window.setAttribute(Qt.WA_DeleteOnClose)
		for qComboBox in self.window.findChildren(QComboBox):
			qComboBox.setItemDelegate(QStyledItemDelegate(qComboBox))
		with open(ToolSeq_Randomizer.userScriptDir + 'ToolSeq.qss', 'r') as fileStyleSheet:
			self.window.setStyleSheet(fileStyleSheet.read())

		self.window.Widget_PreCommands.setVisible(False)
		self.window.Widget_PostCommands.setVisible(False)
		self.window.Splitter_1.setSizes([1000, 1000])

		font = QFont('Consolas', 9)
		font.setStyleHint(QFont.Monospace)
		self.window.Text_Items.setFont(font)
		self.window.Text_Internals.setFont(font)
		self.window.Text_Randoms.setFont(font)
		self.window.Text_PreCommands.setFont(font)
		self.window.Text_PostCommands.setFont(font)
		fontTab = QFontMetricsF(font).horizontalAdvance(' ') * 4
		self.window.Text_Items.setTabStopDistance(fontTab)
		self.window.Text_Internals.setTabStopDistance(fontTab)
		self.window.Text_Randoms.setTabStopDistance(fontTab)
		self.window.Text_PreCommands.setTabStopDistance(fontTab)
		self.window.Text_PostCommands.setTabStopDistance(fontTab)

		self.window.installEventFilter(self)
		self.window.Widget_ItemsHead.installEventFilter(self)
		self.window.Widget_InternalsHead.installEventFilter(self)
		self.window.Widget_RandomsHead.installEventFilter(self)
		self.window.Widget_PreCommandsHead.installEventFilter(self)
		self.window.Widget_PostCommandsHead.installEventFilter(self)
		self.window.Text_Items.textChanged.connect(self.Event_Items)
		self.window.Text_Internals.textChanged.connect(self.Event_Internals)
		self.window.Text_Randoms.textChanged.connect(self.Event_Randoms)
		self.window.Text_Items.customContextMenuRequested.connect(self.Context_Items)
		self.window.Text_PreCommands.customContextMenuRequested.connect(self.Context_PreCommands)
		self.window.Text_PostCommands.customContextMenuRequested.connect(self.Context_PostCommands)
		self.window.Radio_ModeObject.toggled.connect(self.Event_ModeObject)
		self.window.Radio_ModeComponent.toggled.connect(self.Event_ModeComponent)
		self.window.Radio_ModeInterpolate.toggled.connect(self.Event_ModeInterpolate)
		self.window.Radio_ModeSelect.toggled.connect(self.Event_ModeSelect)
		self.window.Radio_ModeMaterial.toggled.connect(self.Event_ModeMaterial)
		self.window.Radio_ModeCommand.toggled.connect(self.Event_ModeCommand)
		self.window.Radio_ModeColor.toggled.connect(self.Event_ModeColor)
		self.window.Radio_ModeReplace.toggled.connect(self.Event_ModeReplace)
		self.window.Combo_ModeColorType.currentTextChanged.connect(self.Event_ColorType)
		self.window.Combo_ModeColorMethod.currentTextChanged.connect(self.Event_ColorMethod)
		self.window.Button_FunctInsert.installEventFilter(self)
		self.window.Combo_FunctLimit.currentTextChanged.connect(self.Event_FunctLimit)
		self.window.Button_PresetBevel.installEventFilter(self)
		self.window.Button_PresetChamfer.installEventFilter(self)
		self.window.Button_PresetExtrudeV.installEventFilter(self)
		self.window.Button_PresetExtrudeE.installEventFilter(self)
		self.window.Button_PresetExtrudeF.installEventFilter(self)
		self.window.Button_PresetPaintGray.installEventFilter(self)
		self.window.Button_PresetPaintRGB.installEventFilter(self)
		self.window.Button_PresetPaintHSV.installEventFilter(self)
		self.window.Button_PresetPaintHSL.installEventFilter(self)
		self.window.Button_PresetWireGray.installEventFilter(self)
		self.window.Button_PresetWireRGB.installEventFilter(self)
		self.window.Button_PresetWireHSV.installEventFilter(self)
		self.window.Button_PresetWireHSL.installEventFilter(self)
		self.window.Button_PresetDefault.installEventFilter(self)
		self.window.Button_Randomize.installEventFilter(self)

		self.window.Text_Randoms.setPlainText('uniform(-10, 10)\n')

		self.window.show()
		if state is None:
			self.window.setMinimumHeight(self.window.height() - 127)
			self.window.resize(self.window.width(), self.window.height() - 77)
		else:
			self.window.setGeometry(state)
		self.window.Tab_Main.tabBar().setFixedWidth(self.window.Tab_Main.width())

		maya_cmds.loadPlugin('ToolSeq_Randomizer.py', quiet=True)

	def eventFilter(self, source, event):
		sourceObjectName = source.objectName()
		eventType = event.type()
		if sourceObjectName == 'WindowMain':
			if eventType == QEvent.Resize:
				self.window.Tab_Main.tabBar().setFixedWidth(self.window.Tab_Main.width())
		elif sourceObjectName == 'Widget_ItemsHead':
			if eventType == QEvent.MouseButtonRelease:
				eventButton = event.button()
				if eventButton == Qt.LeftButton:
					self.Event_ItemsCount_1()
				elif eventButton == Qt.RightButton:
					self.Event_ItemsCount_3()
				elif eventButton == Qt.MiddleButton:
					self.Event_ItemsCount_2()
		elif sourceObjectName == 'Widget_InternalsHead':
			if eventType == QEvent.MouseButtonRelease:
				eventButton = event.button()
				if eventButton == Qt.LeftButton:
					self.Event_InternalsCount_1()
				elif eventButton == Qt.RightButton:
					self.Event_InternalsCount_3()
				elif eventButton == Qt.MiddleButton:
					self.Event_InternalsCount_2()
		elif sourceObjectName == 'Widget_RandomsHead':
			if eventType == QEvent.MouseButtonRelease:
				eventButton = event.button()
				if eventButton == Qt.LeftButton:
					self.Event_RandomsCount_1()
				elif eventButton == Qt.RightButton:
					self.Event_RandomsCount_3()
				elif eventButton == Qt.MiddleButton:
					self.Event_RandomsCount_2()
		elif sourceObjectName == 'Widget_PreCommandsHead':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.MiddleButton:
					self.Event_PreCommandsCount_2()
		elif sourceObjectName == 'Widget_PostCommandsHead':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.MiddleButton:
					self.Event_PostCommandsCount_2()
		elif sourceObjectName == 'Button_FunctInsert':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_RandomsCount_3()
		elif sourceObjectName == 'Button_PresetBevel':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_PresetBevel()
		elif sourceObjectName == 'Button_PresetChamfer':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_PresetChamfer()
		elif sourceObjectName == 'Button_PresetExtrudeV':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_PresetExtrudeV()
		elif sourceObjectName == 'Button_PresetExtrudeE':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_PresetExtrudeE()
		elif sourceObjectName == 'Button_PresetExtrudeF':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_PresetExtrudeF()
		elif sourceObjectName == 'Button_PresetPaintGray':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_PresetPaintGray()
		elif sourceObjectName == 'Button_PresetPaintRGB':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_PresetPaintRGB()
		elif sourceObjectName == 'Button_PresetPaintHSV':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_PresetPaintHSV()
		elif sourceObjectName == 'Button_PresetPaintHSL':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_PresetPaintHSL()
		elif sourceObjectName == 'Button_PresetWireGray':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_PresetWireGray()
		elif sourceObjectName == 'Button_PresetWireRGB':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_PresetWireRGB()
		elif sourceObjectName == 'Button_PresetWireHSV':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_PresetWireHSV()
		elif sourceObjectName == 'Button_PresetWireHSL':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_PresetWireHSL()
		elif sourceObjectName == 'Button_PresetDefault':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_PresetDefault()
		elif sourceObjectName == 'Button_Randomize':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_Randomize()
		return False

	def Context_Items(self, point):
		menu = self.window.Text_Items.createStandardContextMenu()

		actionSeparator = menu.insertSeparator(menu.actions()[0])
		actionSelect = QAction('Select Selected')
		menu.insertAction(actionSeparator, actionSelect)

		actionSeparator = menu.insertSeparator(menu.actions()[0])
		actionSort = QAction('Sort')
		actionNatural = QAction('Natural')
		actionReverse = QAction('Reverse')
		actionShuffle = QAction('Shuffle')
		menu.insertAction(actionSeparator, actionSort)
		menu.insertAction(actionSeparator, actionNatural)
		menu.insertAction(actionSeparator, actionReverse)
		menu.insertAction(actionSeparator, actionShuffle)

		action = menu.exec_(self.window.Text_Items.viewport().mapToGlobal(point))
		if action == actionSelect:
			items = re_split('[\n ]', self.window.Text_Items.textCursor().selectedText().replace(u'\u2029', '\n').strip())
			maya_cmds.select(items)
		elif action == actionSort:
			items = self.window.Text_Items.toPlainText().strip().split('\n')
			items.sort(key=lambda s: s.lower())
			self.window.Text_Items.setPlainText('\n'.join(items))
		elif action == actionNatural:
			items = self.window.Text_Items.toPlainText().strip().split('\n')
			items.sort(key=lambda s: ToolSeq_Randomizer.natural(s))
			self.window.Text_Items.setPlainText('\n'.join(items))
		elif action == actionReverse:
			items = self.window.Text_Items.toPlainText().strip().split('\n')
			items.reverse()
			self.window.Text_Items.setPlainText('\n'.join(items))
		elif action == actionShuffle:
			items = self.window.Text_Items.toPlainText().strip().split('\n')
			randomlib.shuffle(items)
			self.window.Text_Items.setPlainText('\n'.join(items))

	def Context_Commands(self, point):
		menu = self.window.Text_Internals.createStandardContextMenu()
		actionSeparator = menu.insertSeparator(menu.actions()[0])

		actionMayaCmds = QAction('maya_cmds')
		actionItem = QAction('_ITEM')
		actionRandom = QAction('_RANDOM.Get()')
		menu.insertAction(actionSeparator, actionMayaCmds)
		menu.insertAction(actionSeparator, actionItem)
		menu.insertAction(actionSeparator, actionRandom)

		action = menu.exec_(self.window.Text_Internals.viewport().mapToGlobal(point))
		if action == actionMayaCmds:
			self.window.Text_Internals.insertPlainText(actionMayaCmds.text())
		elif action == actionItem:
			self.window.Text_Internals.insertPlainText(actionItem.text())
		elif action == actionRandom:
			self.window.Text_Internals.insertPlainText(actionRandom.text())

	def Context_PreCommands(self, point):
		menu = self.window.Text_PreCommands.createStandardContextMenu()
		actionSeparator = menu.insertSeparator(menu.actions()[0])

		actionMayaCmds = QAction('maya_cmds')
		actionItems = QAction('_ITEMS')
		menu.insertAction(actionSeparator, actionMayaCmds)
		menu.insertAction(actionSeparator, actionItems)

		action = menu.exec_(self.window.Text_PreCommands.viewport().mapToGlobal(point))
		if action == actionMayaCmds:
			self.window.Text_PreCommands.insertPlainText(actionMayaCmds.text())
		elif action == actionItems:
			self.window.Text_PreCommands.insertPlainText(actionItems.text())

	def Context_PostCommands(self, point):
		menu = self.window.Text_PostCommands.createStandardContextMenu()
		actionSeparator = menu.insertSeparator(menu.actions()[0])

		actionMayaCmds = QAction('maya_cmds')
		actionItems = QAction('_ITEMS')
		menu.insertAction(actionSeparator, actionMayaCmds)
		menu.insertAction(actionSeparator, actionItems)

		action = menu.exec_(self.window.Text_PostCommands.viewport().mapToGlobal(point))
		if action == actionMayaCmds:
			self.window.Text_PostCommands.insertPlainText(actionMayaCmds.text())
		elif action == actionItems:
			self.window.Text_PostCommands.insertPlainText(actionItems.text())

	@staticmethod
	def Return_Attributes():
		channelBoxName = mel_eval('$tmp=$gChannelBoxName')
		selectedHistoryAttributes = maya_cmds.channelBox(channelBoxName, q=True, selectedHistoryAttributes=True)
		selectedMainAttributes = maya_cmds.channelBox(channelBoxName, q=True, selectedMainAttributes=True)
		selectedOutputAttributes = maya_cmds.channelBox(channelBoxName, q=True, selectedOutputAttributes=True)
		selectedShapeAttributes = maya_cmds.channelBox(channelBoxName, q=True, selectedShapeAttributes=True)
		selectedAttributes = []
		if selectedHistoryAttributes is not None:
			selectedAttributes += selectedHistoryAttributes
		if selectedMainAttributes is not None:
			selectedAttributes += selectedMainAttributes
		if selectedOutputAttributes is not None:
			selectedAttributes += selectedOutputAttributes
		if selectedShapeAttributes is not None:
			selectedAttributes += selectedShapeAttributes
		return selectedAttributes

	def Return_Items(self):
		flatten = self.window.Check_ItemsFlatten.isChecked()
		if self.window.Radio_ModeObject.isChecked():
			return maya_cmds.ls(selection=True, transforms=True)
		elif self.window.Radio_ModeComponent.isChecked():
			return maya_cmds.ls(selection=True, flatten=flatten)
		elif self.window.Radio_ModeInterpolate.isChecked():
			return maya_cmds.ls(selection=True, transforms=True)
		elif self.window.Radio_ModeSelect.isChecked():
			return maya_cmds.ls(selection=True, flatten=flatten)
		elif self.window.Radio_ModeMaterial.isChecked():
			return maya_cmds.ls(selection=True, flatten=flatten)
		elif self.window.Radio_ModeCommand.isChecked():
			return maya_cmds.ls(selection=True, flatten=flatten)
		elif self.window.Radio_ModeColor.isChecked():
			return maya_cmds.ls(selection=True, flatten=flatten)
		elif self.window.Radio_ModeReplace.isChecked():
			return maya_cmds.ls(selection=True, transforms=True)

	def Return_Internals(self):
		if self.window.Radio_ModeObject.isChecked():
			return ToolSeq_Randomizer.Return_Attributes()
		elif self.window.Radio_ModeComponent.isChecked():
			return ToolSeq_Randomizer.operations
		elif self.window.Radio_ModeInterpolate.isChecked():
			return ToolSeq_Randomizer.Return_Attributes()
		elif self.window.Radio_ModeSelect.isChecked():
			return ''
		elif self.window.Radio_ModeMaterial.isChecked():
			return maya_cmds.ls(selection=True, materials=True)
		elif self.window.Radio_ModeCommand.isChecked():
			return [maya_cmds.undoInfo(q=True, undoName=True)]
		elif self.window.Radio_ModeColor.isChecked():
			return ToolSeq_Randomizer.Return_Attributes()
		elif self.window.Radio_ModeReplace.isChecked():
			return maya_cmds.ls(selection=True, transforms=True)

	def Return_Random(self):
		randomType = self.window.Combo_FunctFormula.currentText()
		if randomType == 'betavariate':
			return 'betavariate(5, 10)'
		elif randomType == 'expovariate':
			return 'expovariate(1.5)'
		elif randomType == 'gammavariate':
			return 'gammavariate(9, 0.5)'
		elif randomType == 'gauss':
			return 'gauss(100, 50)'
		elif randomType == 'lognormvariate':
			return 'lognormvariate(0, 0.25)'
		elif randomType == 'normalvariate':
			return 'normalvariate(100, 50)'
		elif randomType == 'paretovariate':
			return 'paretovariate(3)'
		elif randomType == 'triangular':
			return 'triangular(-1, 1, 0)'
		elif randomType == 'uniform':
			return 'uniform(-1, 1)'
		elif randomType == 'vonmisesvariate':
			return 'vonmisesvariate(0, 4)'
		elif randomType == 'weibullvariate':
			return 'weibullvariate(1, 1.5)'
		elif randomType == 'solo':
			return 'solo(-1)'
		elif randomType == 'custom':
			return 'custom()'

	def Event_ItemsCount_1(self):
		separator = ' ' if self.window.Check_ItemsSet.isChecked() else '\n'
		self.window.Text_Items.setPlainText(separator.join(self.Return_Items()) + '\n')

	def Event_InternalsCount_1(self):
		separator = ' ' if self.window.Check_InternalsSet.isEnabled() and self.window.Check_InternalsSet.isChecked() else '\n'
		self.window.Text_Internals.setPlainText(separator.join(self.Return_Internals()) + '\n')

	def Event_ItemsCount_3(self):
		separator = ' ' if self.window.Check_ItemsSet.isChecked() else '\n'
		self.window.Text_Items.moveCursor(QTextCursor.End)
		self.window.Text_Items.insertPlainText(separator.join(self.Return_Items()) + '\n')

	def Event_InternalsCount_3(self):
		separator = ' ' if self.window.Check_InternalsSet.isEnabled() and self.window.Check_InternalsSet.isChecked() else '\n'
		self.window.Text_Internals.moveCursor(QTextCursor.End)
		self.window.Text_Internals.insertPlainText(separator.join(self.Return_Internals()) + '\n')

	def Event_RandomsCount_1(self):
		self.window.Text_Randoms.setPlainText(self.Return_Random() + '\n')

	def Event_RandomsCount_3(self):
		self.window.Text_Randoms.moveCursor(QTextCursor.End)
		self.window.Text_Randoms.insertPlainText(self.Return_Random() + '\n')

	def Event_ItemsCount_2(self):
		self.window.Text_Items.clear()

	def Event_InternalsCount_2(self):
		self.window.Text_Internals.clear()

	def Event_RandomsCount_2(self):
		self.window.Text_Randoms.clear()

	def Event_PreCommandsCount_2(self):
		self.window.Text_PreCommands.clear()

	def Event_PostCommandsCount_2(self):
		self.window.Text_PostCommands.clear()

	def Event_Items(self):
		text = self.window.Text_Items.toPlainText().strip()
		self.window.Label_ItemsCount.setText(str(text.count('\n') + 1) if text else '0')

	def Event_Internals(self):
		text = self.window.Text_Internals.toPlainText().strip()
		self.window.Label_InternalsCount.setText(str(text.count('\n') + 1) if text else '0')

	def Event_Randoms(self):
		text = self.window.Text_Randoms.toPlainText().strip()
		self.window.Label_RandomsCount.setText(str(text.count('\n') + 1) if text else '0')

	def Event_ModeObject(self, _):
		self.window.Check_ItemsFlatten.setEnabled(False)
		self.window.Check_ItemsFlatten.setChecked(False)
		self.window.Check_InternalsSet.setEnabled(True)
		self.window.Label_Internals.setText('Attributes')
		self.window.Text_Internals.clear()
		self.window.Text_Randoms.setPlainText('uniform(-10, 10)')

	def Event_ModeComponent(self, _):
		self.window.Check_ItemsFlatten.setEnabled(True)
		self.window.Check_ItemsFlatten.setChecked(True)
		self.window.Check_InternalsSet.setEnabled(True)
		self.window.Label_Internals.setText('Operations')
		self.window.Text_Internals.setPlainText('\n'.join(ToolSeq_Randomizer.operations))
		self.window.Text_Randoms.setPlainText('uniform(-10, 10)')

	def Event_ModeInterpolate(self, checked):
		self.window.Check_ItemsFlatten.setEnabled(False)
		self.window.Check_ItemsFlatten.setChecked(False)
		self.window.Check_InternalsSet.setEnabled(True)
		self.window.Label_Internals.setText('Attributes')
		self.window.Text_Internals.clear()

		if checked:
			self.window.Widget_Randoms.setVisible(False)
			self.window.Widget_Function.setEnabled(False)
			self.window.Widget_Filter.setEnabled(False)
		else:
			self.window.Widget_Randoms.setVisible(True)
			self.window.Widget_Function.setEnabled(True)
			self.window.Widget_Filter.setEnabled(True)

	def Event_ModeSelect(self, checked):
		self.window.Check_ItemsFlatten.setEnabled(True)
		self.window.Check_ItemsFlatten.setChecked(True)
		self.window.Text_Randoms.setPlainText('solo(1)')

		if checked:
			self.window.Widget_Internals.setVisible(False)
		else:
			self.window.Widget_Internals.setVisible(True)

	def Event_ModeMaterial(self, _):
		self.window.Check_ItemsFlatten.setEnabled(True)
		self.window.Check_ItemsFlatten.setChecked(False)
		self.window.Check_InternalsSet.setEnabled(False)
		self.window.Label_Internals.setText('Materials')
		self.window.Text_Internals.clear()
		self.window.Text_Randoms.setPlainText('solo(1)')

	def Event_ModeCommand(self, checked):
		self.window.Check_ItemsFlatten.setEnabled(True)
		self.window.Check_ItemsFlatten.setChecked(True)
		self.window.Check_InternalsSet.setEnabled(False)
		self.window.Label_Internals.setText('Commands')
		self.window.Text_Internals.clear()
		self.window.Text_Randoms.setPlainText('uniform(0, 1)')

		if checked:
			self.window.Text_Internals.setContextMenuPolicy(Qt.CustomContextMenu)
			self.window.Text_Internals.customContextMenuRequested.connect(self.Context_Commands)
		else:
			self.window.Text_Internals.setContextMenuPolicy(Qt.DefaultContextMenu)
			self.window.Text_Internals.customContextMenuRequested.disconnect(self.Context_Commands)

	def Event_ModeColor(self, checked):
		self.window.Check_ItemsFlatten.setEnabled(True)
		self.window.Check_ItemsFlatten.setChecked(False)
		self.window.Check_InternalsSet.setEnabled(True)
		self.window.Label_Internals.setText('Attributes')

		if checked:
			self.window.Combo_FunctQuantity.setProperty('state', self.window.Combo_FunctQuantity.currentText())
			self.Event_ColorType(self.window.Combo_ModeColorType.currentText())
		else:
			self.window.Combo_FunctQuantity.setCurrentText(self.window.Combo_FunctQuantity.property('state'))

	def Event_ModeReplace(self, _):
		self.window.Check_ItemsFlatten.setEnabled(False)
		self.window.Check_ItemsFlatten.setChecked(False)
		self.window.Check_InternalsSet.setEnabled(False)
		self.window.Label_Internals.setText('Items')
		self.window.Text_Internals.clear()
		self.window.Text_Randoms.setPlainText('solo(1)')

	def Event_ColorType(self, text):
		if text == 'Gray':
			self.window.Text_Internals.setPlainText('colorR colorG colorB')
			self.window.Text_Randoms.setPlainText('uniform(0, 1)')
			self.window.Combo_FunctQuantity.setCurrentText('Single')
		else:
			self.window.Text_Internals.setPlainText('colorR\ncolorG\ncolorB')
			self.window.Text_Randoms.setPlainText('uniform(0, 1)\nuniform(0, 1)\nuniform(0, 1)')
			self.window.Combo_FunctQuantity.setCurrentText('Seq 1>2')

	def Event_ColorMethod(self, text):
		self.window.Combo_ModeColorMaterialType.setEnabled(text == 'Assign')

	def Event_FunctLimit(self, text):
		checked = text != 'Free'
		self.window.Float_FunctLimitMin.setEnabled(checked)
		self.window.Float_FunctLimitMax.setEnabled(checked)

	def Event_PresetBevel(self):
		self.window.Radio_ModeCommand.setChecked(True)
		self.window.Text_Internals.setPlainText('maya_cmds.polyBevel3(_ITEM, caching=True, offsetAsFraction=True, fraction=_RANDOM.Get(), subdivideNgons=True, smoothingAngle=30)')
		self.window.Text_Randoms.setPlainText('uniform(0.0625, 0.9375)')

	def Event_PresetChamfer(self):
		self.window.Radio_ModeCommand.setChecked(True)
		self.window.Text_Internals.setPlainText('maya_cmds.polyExtrudeVertex(_ITEM, caching=True, worldSpace=True, width=_RANDOM.Get())')
		self.window.Text_Randoms.setPlainText('uniform(0.0625, 0.4375)')
		self.window.Check_FunctPostCommands.setChecked(True)
		self.window.Text_PostCommands.setPlainText('maya_cmds.select(_ITEMS)\nmaya_cmds.DeleteVertex()')

	def Event_PresetExtrudeV(self):
		self.window.Radio_ModeCommand.setChecked(True)
		self.window.Text_Internals.setPlainText('maya_cmds.polyExtrudeVertex(_ITEM, caching=True, worldSpace=True, width=0.25, length=_RANDOM.Get())')
		self.window.Text_Randoms.setPlainText('uniform(0.0625, 1)')

	def Event_PresetExtrudeE(self):
		self.window.Radio_ModeCommand.setChecked(True)
		self.window.Text_Internals.setPlainText('maya_cmds.polyExtrudeEdge(_ITEM, caching=True, worldSpace=True, thickness=_RANDOM.Get())')
		self.window.Text_Randoms.setPlainText('uniform(0.0625, 1)')

	def Event_PresetExtrudeF(self):
		self.window.Radio_ModeCommand.setChecked(True)
		self.window.Text_Internals.setPlainText('maya_cmds.polyExtrudeFacet(_ITEM, caching=True, worldSpace=True, thickness=_RANDOM.Get())')
		self.window.Text_Randoms.setPlainText('uniform(0.0625, 1)')

	def Event_PresetPaintGray(self):
		self.window.Radio_ModeCommand.setChecked(True)
		self.window.Text_Internals.setPlainText('r = g = b = _RANDOM.Get()\nmaya_cmds.polyColorPerVertex(_ITEM, rgb=(r, g, b))')
		self.window.Text_Randoms.setPlainText('uniform(0, 1)')
		self.window.Check_FunctPreCommands.setChecked(True)
		self.window.Text_PreCommands.setPlainText('maya_cmds.polyColorPerVertex(_ITEMS, colorDisplayOption=True)')
		self.window.Combo_FunctQuantity.setCurrentText('Single')

	def Event_PresetPaintRGB(self):
		self.window.Radio_ModeCommand.setChecked(True)
		self.window.Text_Internals.setPlainText('r = _RANDOM.Get()\ng = _RANDOM.Get()\nb = _RANDOM.Get()\nmaya_cmds.polyColorPerVertex(_ITEM, rgb=(r, g, b))')
		self.window.Text_Randoms.setPlainText('uniform(0, 1)\nuniform(0, 1)\nuniform(0, 1)')
		self.window.Check_FunctPreCommands.setChecked(True)
		self.window.Text_PreCommands.setPlainText('maya_cmds.polyColorPerVertex(_ITEMS, colorDisplayOption=True)')
		self.window.Combo_FunctQuantity.setCurrentText('Seq 1>2')

	def Event_PresetPaintHSV(self):
		self.window.Radio_ModeCommand.setChecked(True)
		self.window.Text_Internals.setPlainText('h = _RANDOM.Get()\ns = _RANDOM.Get()\nv = _RANDOM.Get()\nmaya_cmds.polyColorPerVertex(_ITEM, rgb=hsv_to_rgb(h, s, v))')
		self.window.Text_Randoms.setPlainText('uniform(0, 1)\nuniform(0, 1)\nuniform(0, 1)')
		self.window.Check_FunctPreCommands.setChecked(True)
		self.window.Text_PreCommands.setPlainText('maya_cmds.polyColorPerVertex(_ITEMS, colorDisplayOption=True)')
		self.window.Combo_FunctQuantity.setCurrentText('Seq 1>2')

	def Event_PresetPaintHSL(self):
		self.window.Radio_ModeCommand.setChecked(True)
		self.window.Text_Internals.setPlainText('h = _RANDOM.Get()\ns = _RANDOM.Get()\nl = _RANDOM.Get()\nmaya_cmds.polyColorPerVertex(_ITEM, rgb=hls_to_rgb(h, l, s))')
		self.window.Text_Randoms.setPlainText('uniform(0, 1)\nuniform(0, 1)\nuniform(0, 1)')
		self.window.Check_FunctPreCommands.setChecked(True)
		self.window.Text_PreCommands.setPlainText('maya_cmds.polyColorPerVertex(_ITEMS, colorDisplayOption=True)')
		self.window.Combo_FunctQuantity.setCurrentText('Seq 1>2')

	def Event_PresetWireGray(self):
		self.window.Radio_ModeCommand.setChecked(True)
		self.window.Text_Internals.setPlainText('r = g = b = _RANDOM.Get()\nfor i in range(len(_ITEM)):\n\tmaya_cmds.setAttr(_ITEM[i] + \'.overrideEnabled\', True)\n\tmaya_cmds.setAttr(_ITEM[i] + \'.overrideRGBColors\', True)\n\tmaya_cmds.setAttr(_ITEM[i] + \'.overrideColorRGB\', r, g, b)')
		self.window.Text_Randoms.setPlainText('uniform(0, 1)')
		self.window.Combo_FunctQuantity.setCurrentText('Single')

	def Event_PresetWireRGB(self):
		self.window.Radio_ModeCommand.setChecked(True)
		self.window.Text_Internals.setPlainText('r = _RANDOM.Get()\ng = _RANDOM.Get()\nb = _RANDOM.Get()\nfor i in range(len(_ITEM)):\n\tmaya_cmds.setAttr(_ITEM[i] + \'.overrideEnabled\', True)\n\tmaya_cmds.setAttr(_ITEM[i] + \'.overrideRGBColors\', True)\n\tmaya_cmds.setAttr(_ITEM[i] + \'.overrideColorRGB\', r, g, b)')
		self.window.Text_Randoms.setPlainText('uniform(0, 1)\nuniform(0, 1)\nuniform(0, 1)')
		self.window.Combo_FunctQuantity.setCurrentText('Seq 1>2')

	def Event_PresetWireHSV(self):
		self.window.Radio_ModeCommand.setChecked(True)
		self.window.Text_Internals.setPlainText('h = _RANDOM.Get()\ns = _RANDOM.Get()\nv = _RANDOM.Get()\nfor i in range(len(_ITEM)):\n\tmaya_cmds.setAttr(_ITEM[i] + \'.overrideEnabled\', True)\n\tmaya_cmds.setAttr(_ITEM[i] + \'.overrideRGBColors\', True)\n\tmaya_cmds.setAttr(_ITEM[i] + \'.overrideColorRGB\', *hsv_to_rgb(h, s, v))')
		self.window.Text_Randoms.setPlainText('uniform(0, 1)\nuniform(0, 1)\nuniform(0, 1)')
		self.window.Combo_FunctQuantity.setCurrentText('Seq 1>2')

	def Event_PresetWireHSL(self):
		self.window.Radio_ModeCommand.setChecked(True)
		self.window.Text_Internals.setPlainText('h = _RANDOM.Get()\ns = _RANDOM.Get()\nl = _RANDOM.Get()\nfor i in range(len(_ITEM)):\n\tmaya_cmds.setAttr(_ITEM[i] + \'.overrideEnabled\', True)\n\tmaya_cmds.setAttr(_ITEM[i] + \'.overrideRGBColors\', True)\n\tmaya_cmds.setAttr(_ITEM[i] + \'.overrideColorRGB\', *hls_to_rgb(h, l, s))')
		self.window.Text_Randoms.setPlainText('uniform(0, 1)\nuniform(0, 1)\nuniform(0, 1)')
		self.window.Combo_FunctQuantity.setCurrentText('Seq 1>2')

	def Event_PresetDefault(self):
		selfNew = ToolSeq_Randomizer(self.window.geometry())
		selfNew.window.Tab_Main.setCurrentWidget(selfNew.window.Widget_Preset)
		self.window.close()

	def Calculate_Randoms(self, itemsLen, internalsLen=1):
		randomsLen = itemsLen * internalsLen
		datas = [s.strip().split('|') for s in self.window.Text_Randoms.toPlainText().strip().split('\n')]
		mark = 0

		indexes = [0] * randomsLen
		quantity = self.window.Combo_FunctQuantity.currentText()
		if quantity == 'Single':
			pass
		elif quantity == 'Seq 1>2':
			indexes = [i % len(datas) for i in range(randomsLen)]
		elif quantity == 'Seq 2>1':
			x = y = 0
			for i in range(internalsLen):
				for j in range(itemsLen):
					indexes[x] = y
					x += 1
				y = (y + 1) % len(datas)
		elif quantity == 'Percent':
			mark += 1
			percents = [float(datas[0][mark])] * len(datas)
			for i in range(1, len(datas)):
				percents[i] = float(datas[i][mark]) + percents[i - 1]
			for i in range(randomsLen):
				selector = randomlib.uniform(0, percents[-1])
				for j in range(len(datas)):
					if selector < percents[j]:
						indexes[i] = j
						break

		functions = [compile('ToolSeq_Randoms.' + datas[i][0], '<string>', 'eval') for i in range(len(datas))]
		randoms = [eval(functions[indexes[i]], globals()) for i in range(randomsLen)]

		limit = self.window.Combo_FunctLimit.currentText()
		if limit != 'Free':
			limitMin = self.window.Float_FunctLimitMin.value()
			limitMax = self.window.Float_FunctLimitMax.value()
			if limit == 'Clamp':
				randoms = [max(limitMin, min(limitMax, randoms[i])) for i in range(randomsLen)]
			elif limit == 'Return':
				limitDif = limitMax - limitMin
				for i in range(randomsLen):
					if randoms[i] < limitMin or randoms[i] > limitMax:
						randoms[i] = (randoms[i] % limitDif) + limitMin

		isInterval = self.window.Check_FunctInterval.isChecked()
		intervals = []
		if isInterval:
			mark += 1
			intervals = [float(datas[i][mark]) for i in range(len(datas))]
			for i in range(randomsLen):
				interval = intervals[indexes[i]]
				if interval != 0:
					randoms[i] -= ToolSeq_Randomizer.fmod(randoms[i], interval)

		if self.window.Check_FunctExclude.isChecked():
			mark += 1
			excludes = [[float(data) for data in datas[i][mark].strip().split(' ')] for i in range(len(datas))]
			i = 0
			while i < randomsLen:
				for exclude in excludes[indexes[i]]:
					if abs(randoms[i] - exclude) < 0.0001:
						randoms[i] = eval(functions[indexes[i]], globals())
						if isInterval:
							interval = intervals[indexes[i]]
							if interval != 0:
								randoms[i] -= ToolSeq_Randomizer.fmod(randoms[i], interval)
						i -= 1
						break
				i += 1

		sorting = self.window.Combo_FunctSorting.currentText()
		if sorting == 'Unsort':
			pass
		elif sorting == 'Small > Big':
			randoms.sort()
		elif sorting == 'Big > Small':
			randoms.sort(reverse=True)

		if self.window.Check_FilterPattern.isChecked():
			patternFormula = self.window.Line_FilterPatternFormula.text().strip().split(' ')
			f = 1
			while f < len(patternFormula):
				patternFormula[f] = int(patternFormula[f])
				f += 2
			patternDefault = self.window.Float_FilterPatternDefault.value()

			i = f = 0
			letterDefault = self.window.Line_FilterPatternDefault.text().strip()
			letterUnique = self.window.Line_FilterPatternUnique.text().strip()
			letterSame = self.window.Line_FilterPatternSame.text().strip()
			letterMirrorP = self.window.Line_FilterPatternMirrorP.text().strip()
			letterMirrorN = self.window.Line_FilterPatternMirrorN.text().strip()
			letterCumulP = self.window.Line_FilterPatternCumulP.text().strip()
			letterCumulN = self.window.Line_FilterPatternCumulN.text().strip()
			while i < randomsLen:
				if patternFormula[f] == letterDefault:
					f = (f + 1) % len(patternFormula)
					j = 0
					while j < patternFormula[f] and i < randomsLen:
						randoms[i] = patternDefault
						j += 1
						i += 1
				elif patternFormula[f] == letterUnique:
					f = (f + 1) % len(patternFormula)
					i += patternFormula[f]
				elif patternFormula[f] == letterSame:
					f = (f + 1) % len(patternFormula)
					j = 0
					i += 1
					while j < patternFormula[f] - 1 and i < randomsLen:
						randoms[i] = randoms[i - 1]
						j += 1
						i += 1
				elif patternFormula[f] == letterCumulP:
					f = (f + 1) % len(patternFormula)
					j = 0
					i += 1
					while j < patternFormula[f] - 1 and i < randomsLen:
						randoms[i] += randoms[i - 1]
						j += 1
						i += 1
				elif patternFormula[f] == letterCumulN:
					f = (f + 1) % len(patternFormula)
					j = 0
					i += patternFormula[f] - 1
					if i >= randomsLen:
						patternFormula[f] -= i - randomsLen + 1
						i = randomsLen - 1
					while j < patternFormula[f] - 1 and i < randomsLen:
						randoms[i - 1] += randoms[i]
						j += 1
						i -= 1
					i += patternFormula[f]
				elif patternFormula[f] == letterMirrorP:
					f = (f + 1) % len(patternFormula)
					j = 0
					if patternFormula[f] > i:
						i += patternFormula[f] - i
					while j < patternFormula[f] and i < randomsLen:
						randoms[i] = randoms[i - patternFormula[f]]
						j += 1
						i += 1
				elif patternFormula[f] == letterMirrorN:
					f = (f + 1) % len(patternFormula)
					j = 0
					if patternFormula[f] > i:
						i += patternFormula[f] - i
					while j < patternFormula[f] and i < randomsLen:
						randoms[i] = randoms[i - (2 * j + 1)]
						j += 1
						i += 1
				else:
					raise TypeError('Pattern not recognized: ' + patternFormula[f])
				f = (f + 1) % len(patternFormula)

		return ToolSeq_Random(randoms)

	def Action_Randomize(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			itemsText = self.window.Text_Items.toPlainText().strip()
			internalsText = self.window.Text_Internals.toPlainText().strip()
			itemsWide = re_split('[\n ]', itemsText)

			if self.window.Check_FunctPreCommands.isChecked():
				exec(self.window.Text_PreCommands.toPlainText().strip(), {'_ITEMS': itemsWide}, globals())

			if self.window.Radio_ModeObject.isChecked():
				items_ = [s.strip().split(' ') for s in itemsText.split('\n')]
				internals_ = [s.strip().split(' ') for s in internalsText.split('\n')]
				randoms = self.Calculate_Randoms(len(items_), len(internals_))

				if self.window.Check_ModeObjectRelative.isChecked():
					operatorRel = ToolSeq_Randomizer.operator_sec
					if self.window.Combo_ModeObjectRelative.currentText() == '+':
						operatorRel = operator_add
					elif self.window.Combo_ModeObjectRelative.currentText() == '*':
						operatorRel = operator_mul
					for items in items_:
						for internals in internals_:
							random = randoms.Get()
							for item in items:
								for internal in internals:
									maya_cmds.setAttr(item + '.' + internal, operatorRel(maya_cmds.getAttr(item + '.' + internal), random))
				else:
					for items in items_:
						for internals in internals_:
							random = randoms.Get()
							for item in items:
								for internal in internals:
									maya_cmds.setAttr(item + '.' + internal, random)

			elif self.window.Radio_ModeComponent.isChecked():
				items_ = [s.strip().split(' ') for s in itemsText.split('\n')]
				internals_ = [s.strip().split(' ') for s in internalsText.split('\n')]
				randoms = self.Calculate_Randoms(len(items_), len(internals_))

				for internals in internals_:
					for internal in internals:
						if internal == 'movX' or internal == 'movY' or internal == 'movZ' or internal == 'movN':
							maya_cmds.ToolSeq_Randomizer_Apply(operation=internal, randoms=hex(id(randoms)), items=hex(id(items_)))
							randoms.index -= len(items_)
						elif internal == 'rotX':
							for items in items_:
								maya_cmds.rotate(randoms.Get(), 0, 0, items, relative=True, componentSpace=True, worldSpace=True, forceOrderXYZ=True, x=True)
							randoms.index -= len(items_)
						elif internal == 'rotY':
							for items in items_:
								maya_cmds.rotate(randoms.Get(), 0, 0, items, relative=True, componentSpace=True, worldSpace=True, forceOrderXYZ=True, y=True)
							randoms.index -= len(items_)
						elif internal == 'rotZ':
							for items in items_:
								maya_cmds.rotate(randoms.Get(), 0, 0, items, relative=True, componentSpace=True, worldSpace=True, forceOrderXYZ=True, z=True)
							randoms.index -= len(items_)
						elif internal == 'scaX':
							for items in items_:
								maya_cmds.scale(randoms.Get(), 1, 1, items, relative=True, componentSpace=True, localSpace=True, x=True)
							randoms.index -= len(items_)
						elif internal == 'scaY':
							for items in items_:
								maya_cmds.scale(randoms.Get(), 1, 1, items, relative=True, componentSpace=True, localSpace=True, y=True)
							randoms.index -= len(items_)
						elif internal == 'scaZ':
							for items in items_:
								maya_cmds.scale(randoms.Get(), 1, 1, items, relative=True, componentSpace=True, localSpace=True, z=True)
							randoms.index -= len(items_)
					randoms.index += len(items_)

			elif self.window.Radio_ModeInterpolate.isChecked():
				items_ = [s.strip().split(' ') for s in itemsText.split('\n')]
				internals_ = [s.strip().split(' ') for s in internalsText.split('\n')]

				for j in range(len(internals_)):
					attrFist = maya_cmds.getAttr(items_[0][0] + '.' + internals_[j][0])
					attrLast = maya_cmds.getAttr(items_[-1][-1] + '.' + internals_[j][-1])
					attrIncr = (attrLast - attrFist) / float(len(items_) - 1)
					for items in items_:
						for internal in internals_[j]:
							for item in items:
								maya_cmds.setAttr(item + '.' + internal, attrFist)
						attrFist += attrIncr

			elif self.window.Radio_ModeSelect.isChecked():
				items_ = [s.strip().split(' ') for s in itemsText.split('\n')]
				random = int(round(self.Calculate_Randoms(1).randoms[0]))
				if random <= 0 or random > len(items_):
					raise TypeError('Selection is out of range: ' + str(random))
				itemsSels = ToolSeq_Randomizer.random_sample_iordered(items_, random)
				maya_cmds.select(chain.from_iterable(itemsSels))

			elif self.window.Radio_ModeMaterial.isChecked():
				items_ = [s.strip().split(' ') for s in itemsText.split('\n')]
				random = int(round(self.Calculate_Randoms(1).randoms[0]))
				if random <= 0 or random > len(items_):
					raise TypeError('Selection is out of range: ' + str(random))
				itemsSels = ToolSeq_Randomizer.random_sample_iordered(items_, random)

				selection = maya_cmds.ls(selection=True)
				internals = internalsText.split('\n')
				for itemSels in itemsSels:
					internal = randomlib.choice(internals)
					for itemSel in itemSels:
						maya_cmds.select(itemSel)
						maya_cmds.hyperShade(assign=internal)
				maya_cmds.select(selection)

			elif self.window.Radio_ModeCommand.isChecked():
				items_ = [s.strip().split(' ') for s in itemsText.split('\n')]
				randoms = self.Calculate_Randoms(len(items_), internalsText.count('_RANDOM.Get()'))
				exec('def ToolSeq_Randomizer_Commands(_ITEM, _RANDOM):\n\t%s' % internalsText.replace('\n', '\n\t'), globals())

				for items in items_:
					ToolSeq_Randomizer_Commands(items, randoms)

			elif self.window.Radio_ModeColor.isChecked():
				items_ = [s.strip().split(' ') for s in itemsText.split('\n')]
				internals_ = [s.strip().split(' ') for s in internalsText.split('\n')]
				randoms = self.Calculate_Randoms(len(items_), len(internals_))

				if self.window.Combo_ModeColorMethod.currentText() == 'Direct':
					pass
				elif self.window.Combo_ModeColorMethod.currentText() == 'Find':
					selection = maya_cmds.ls(selection=True)
					for x in range(len(items_)):
						y = 0
						while y < len(items_[x]):
							maya_cmds.select(items_[x][y])
							maya_cmds.hyperShade(shaderNetworksSelectMaterialNodes=True)
							itemMaterial = maya_cmds.ls(selection=True, materials=True)
							del items_[x][y]
							items_[x][y:y] = itemMaterial
							y += len(itemMaterial)
					maya_cmds.select(selection)
				elif self.window.Combo_ModeColorMethod.currentText() == 'Assign':
					materialType = self.window.Combo_ModeColorMaterialType.currentText()
					for x in range(len(items_)):
						material = maya_cmds.shadingNode(materialType, asShader=True)
						shadingGroup = material + 'SG'
						maya_cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=shadingGroup)
						maya_cmds.connectAttr(material + '.outColor', shadingGroup + '.surfaceShader', force=True)
						for y in range(len(items_[x])):
							maya_cmds.sets(items_[x][y], e=True, forceElement=shadingGroup)
							items_[x][y] = material

				for items in items_:
					for internals in internals_:
						random = randoms.Get()
						for item in items:
							for internal in internals:
								maya_cmds.setAttr(item + '.' + internal, random)

				if self.window.Combo_ModeColorType.currentText() == 'HSV':
					internalsVects = list(set([s[0:-1] for s in re_split('[\n ]', internalsText)]))
					for items in items_:
						for item in items:
							for internalsVect in internalsVects:
								attribute = item + '.' + internalsVect
								maya_cmds.setAttr(attribute, *hsv_to_rgb(*maya_cmds.getAttr(attribute)[0]))
				elif self.window.Combo_ModeColorType.currentText() == 'HSL':
					internalsVects = list(set([s[0:-1] for s in re_split('[\n ]', internalsText)]))
					for items in items_:
						for item in items:
							for internalsVect in internalsVects:
								attribute = item + '.' + internalsVect
								maya_cmds.setAttr(attribute, *ToolSeq_Randomizer.hsl_to_rgb(*maya_cmds.getAttr(attribute)[0]))

			elif self.window.Radio_ModeReplace.isChecked():
				items_ = [s.strip().split(' ') for s in itemsText.split('\n')]
				random = int(round(self.Calculate_Randoms(1).randoms[0]))
				if random <= 0 or random > len(items_):
					raise TypeError('Selection is out of range: ' + str(random))
				itemsSels = ToolSeq_Randomizer.random_sample_iordered(items_, random)

				isRot = self.window.Check_ModeReplaceRotate.isChecked()
				isSca = self.window.Check_ModeReplaceScale.isChecked()

				rots = []
				scas = []
				if isRot:
					for itemSels in itemsSels:
						for itemSel in itemSels:
							rots.append(maya_cmds.getAttr(itemSel + '.rotate'))
				if isSca:
					for itemSels in itemsSels:
						for itemSel in itemSels:
							scas.append(maya_cmds.getAttr(itemSel + '.scale'))

				internals = internalsText.split('\n')
				pivotTypeText = self.window.Combo_ModeReplacePivot.currentText()
				pivotTypeSour = {}
				pivotTypeDest = {}
				if pivotTypeText == 'RotPiv':
					pivotTypeSour = {'rotatePivot': True}
					pivotTypeDest = {'rotatePivotRelative': True}
				elif pivotTypeText == 'ScaPiv':
					pivotTypeSour = {'scalePivot': True}
					pivotTypeDest = {'scalePivotRelative': True}
				if self.window.Combo_ModeReplaceMethod.currentText() == 'Copy':
					for itemSels in itemsSels:
						internal = randomlib.choice(internals)
						for itemSel in itemSels:
							if '|' in itemSel:
								itemSel = itemSel.split('|')[-1]

							parent = maya_cmds.listRelatives(itemSel, path=True, parent=True)
							position = maya_cmds.xform(itemSel, q=True, worldSpace=True, **pivotTypeSour)

							maya_cmds.delete(itemSel)
							maya_cmds.duplicate(internal, name=itemSel)
							maya_cmds.move(position[0], position[1], position[2], itemSel, **pivotTypeDest)

							if parent is not None:
								maya_cmds.parent(itemSel, parent)
				elif self.window.Combo_ModeReplaceMethod.currentText() == 'Instance':
					for itemSels in itemsSels:
						internal = randomlib.choice(internals)
						for itemSel in itemSels:
							if '|' in itemSel:
								itemSel = itemSel.split('|')[-1]

							parent = maya_cmds.listRelatives(itemSel, path=True, parent=True)
							position = maya_cmds.xform(itemSel, q=True, worldSpace=True, **pivotTypeSour)

							maya_cmds.delete(itemSel)
							maya_cmds.instance(internal, name=itemSel)
							maya_cmds.move(position[0], position[1], position[2], itemSel, **pivotTypeDest)

							if parent is not None:
								maya_cmds.parent(itemSel, parent)

				if isRot:
					i = 0
					for itemSels in itemsSels:
						for itemSel in itemSels:
							maya_cmds.setAttr(itemSel + '.rotate', *rots[i][0])
							i += 1
				if isSca:
					i = 0
					for itemSels in itemsSels:
						for itemSel in itemSels:
							maya_cmds.setAttr(itemSel + '.scale', *scas[i][0])
							i += 1

			if self.window.Check_FunctPostCommands.isChecked():
				exec(self.window.Text_PostCommands.toPlainText().strip(), {'_ITEMS': itemsWide}, globals())
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

class ToolSeq_Randoms:
	@staticmethod
	def betavariate(alpha, beta):
		return randomlib.betavariate(alpha, beta)

	@staticmethod
	def expovariate(lambd):
		return randomlib.expovariate(lambd)

	@staticmethod
	def gammavariate(alpha, beta):
		return randomlib.gammavariate(alpha, beta)

	@staticmethod
	def gauss(mu, sigma):
		return randomlib.gauss(mu, sigma)

	@staticmethod
	def lognormvariate(mu, sigma):
		return randomlib.lognormvariate(mu, sigma)

	@staticmethod
	def normalvariate(mu, sigma):
		return randomlib.normalvariate(mu, sigma)

	@staticmethod
	def paretovariate(alpha):
		return randomlib.paretovariate(alpha)

	@staticmethod
	def triangular(low, high, mode):
		return randomlib.triangular(low, high, mode)

	@staticmethod
	def uniform(low, high):
		return randomlib.uniform(low, high)

	@staticmethod
	def vonmisesvariate(mu, kappa):
		return randomlib.vonmisesvariate(mu, kappa)

	@staticmethod
	def weibullvariate(alpha, beta):
		return randomlib.weibullvariate(alpha, beta)

	@staticmethod
	def solo(val):
		return val

	@staticmethod
	def custom():
		return 0