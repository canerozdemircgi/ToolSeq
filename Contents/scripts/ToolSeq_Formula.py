from os.path import abspath, dirname
from sys import stderr

from PySide2.QtCore import QEvent, Qt
from PySide2.QtGui import QFont, QFontMetricsF
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QWidget, QComboBox, QStyledItemDelegate
from maya import cmds as maya_cmds
from maya.OpenMayaUI import MQtUtil
from shiboken2 import wrapInstance

class ToolSeq_Formula(QWidget):

	userScriptDir = dirname(abspath(__file__)) + '/'

	qUiLoader = QUiLoader()
	qUiLoader.setWorkingDirectory(userScriptDir)

	windowMain = wrapInstance(int(MQtUtil.mainWindow()), QMainWindow)
	preFormulas = [
		'',
		'from math import pow',
		'from math import pow',
		'from math import pow',
		'from math import pow, sqrt',
		'from math import pow, sqrt',
		'from math import sqrt, fabs',
		'from math import sin',
		'from math import sin',
		'from math import sin',
		'from math import sin',
		'from math import sin, cos',
		'from math import sin, fabs',
		'from math import sin, fabs',
		'from math import sin, cos, floor, ceil',
		'from math import cos'
	]
	formulas = [
		'y = x * z',
		'y = pow((x + z) / 4.0, 2)',
		'y = (pow(x, 2) + pow(z, 2)) / 4.0',
		'y = (pow(x, 2) * pow(z, 2)) / 64.0',
		'y = sqrt(1 + pow(x, 2) - pow(z, 2))',
		'y = sqrt(16 - pow(x, 2) * pow(z, 2))',
		'y = sqrt(fabs(x * z))',
		'y = sin(x) + sin(z)',
		'y = sin(x) * sin(z)',
		'y = sin(x + z)',
		'y = sin(x * z)',
		'y = sin(z * cos(x))',
		'y = 2 * sin(x) * fabs(sin(x)) * sin(z) * fabs(sin(z))',
		'y = sin(x) - fabs(sin(x)) + sin(z) - fabs(sin(z))',
		'y = max(cos(x), floor(sin(x * 2))) + min(cos(z * 2), ceil(sin(z)))',
		'x += xn * cos(x) * 2.5\ny += yn * cos(y) * 2.5\nz += zn * cos(z) * 2.5'
	]

	def __init__(self):
		super(ToolSeq_Formula, self).__init__(ToolSeq_Formula.windowMain)

		self.window = ToolSeq_Formula.qUiLoader.load(ToolSeq_Formula.userScriptDir + 'ui/ToolSeq_Formula.ui', self)
		self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
		self.window.setAttribute(Qt.WA_DeleteOnClose)
		for qComboBox in self.window.findChildren(QComboBox):
			qComboBox.setItemDelegate(QStyledItemDelegate(qComboBox))
		with open(ToolSeq_Formula.userScriptDir + 'ToolSeq.qss', 'r') as fileStyleSheet:
			self.window.setStyleSheet(fileStyleSheet.read())

		font = QFont('Consolas', 9)
		font.setStyleHint(QFont.Monospace)
		self.window.Text_PreFormula.setFont(font)
		self.window.Text_Formula.setFont(font)
		fontTab = QFontMetricsF(font).horizontalAdvance(' ') * 4
		self.window.Text_PreFormula.setTabStopDistance(fontTab)
		self.window.Text_Formula.setTabStopDistance(fontTab)

		self.window.Text_PreFormula.setPlainText(ToolSeq_Formula.preFormulas[11])
		self.window.Text_Formula.setPlainText(ToolSeq_Formula.formulas[11])

		self.window.Widget_Shape.installEventFilter(self)
		self.window.Check_VariableN.toggled.connect(self.Event_VariableN)
		self.window.Button_Fill.installEventFilter(self)
		self.window.Button_Formulate.installEventFilter(self)

		self.window.show()
		wMax = max(self.window.Label_1.width(), self.window.Label_2.width())
		self.window.Label_1.setFixedWidth(wMax)
		self.window.Label_2.setFixedWidth(wMax)

		maya_cmds.loadPlugin('ToolSeq_Formula.py', quiet=True)

	def eventFilter(self, source, event):
		sourceObjectName = source.objectName()
		eventType = event.type()
		if sourceObjectName == 'Widget_Shape':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_Shape()
		elif sourceObjectName == 'Button_Fill':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_Fill()
		elif sourceObjectName == 'Button_Formulate':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_Formulate()
		return False

	def Event_Shape(self):
		self.window.Line_Shape.setText(maya_cmds.ls(selection=True, dag=True, shapes=True)[0])

	def Event_VariableN(self, checked):
		self.window.Label_Variables.setText('xn yn zn x y z' if checked else 'x y z')

	def Event_Fill(self):
		index = self.window.Combo_CutType.currentIndex()
		self.window.Text_PreFormula.setPlainText(ToolSeq_Formula.preFormulas[index])
		self.window.Text_Formula.setPlainText(ToolSeq_Formula.formulas[index])

		if index == 4 or index == 5:
			self.window.Check_Secure.setChecked(True)
			self.window.Check_VariableN.setChecked(False)
		elif index == 15:
			self.window.Check_Secure.setChecked(False)
			self.window.Check_VariableN.setChecked(True)
		else:
			self.window.Check_Secure.setChecked(False)
			self.window.Check_VariableN.setChecked(False)

	def Action_Formulate(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			maya_cmds.ToolSeq_Formula_Apply(
				shape=self.window.Line_Shape.text().strip(),
				preFormula=self.window.Text_PreFormula.toPlainText().strip(),
				formula=self.window.Text_Formula.toPlainText().strip(),
				isSecure=self.window.Check_Secure.isChecked(),
				isVarN=self.window.Check_VariableN.isChecked()
			)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)