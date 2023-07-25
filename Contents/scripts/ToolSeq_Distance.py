from math import sqrt
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

class ToolSeq_Distance(QWidget):

	qUiLoader = QUiLoader()
	userScriptDir = dirname(abspath(__file__)) + '/'
	qUiLoader.setWorkingDirectory(userScriptDir)

	def __init__(self):
		ptrs.append(self)
		self.windowMain = wrapInstance(int(MQtUtil.mainWindow()), QMainWindow)
		super(ToolSeq_Distance, self).__init__(self.windowMain)

		self.window = ToolSeq_Distance.qUiLoader.load(ToolSeq_Distance.userScriptDir + 'ui/ToolSeq_Distance.ui', self)
		self.window.destroyed.connect(lambda: ptrs_remove(self))
		self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
		self.window.setAttribute(Qt.WA_DeleteOnClose)
		for qComboBox in self.window.findChildren(QComboBox):
			qComboBox.setItemDelegate(QStyledItemDelegate(qComboBox))
		with open(ToolSeq_Distance.userScriptDir + 'ToolSeq.qss', 'r') as fileStyleSheet:
			self.window.setStyleSheet(fileStyleSheet.read())

		self.window.Widget_01.installEventFilter(self)
		self.window.Text_Items.textChanged.connect(self.Event_Items)
		self.window.Button_CalculateDistance.installEventFilter(self)
		self.window.Button_SelectMinEdges.installEventFilter(self)
		self.window.Button_SelectMaxEdges.installEventFilter(self)
		self.window.Button_MoveX.installEventFilter(self)
		self.window.Button_MoveY.installEventFilter(self)
		self.window.Button_MoveZ.installEventFilter(self)

		self.window.show()

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
		elif sourceObjectName == 'Button_CalculateDistance':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_CalculateDistance()
		elif sourceObjectName == 'Button_SelectMinEdges':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_SelectMinEdges()
		elif sourceObjectName == 'Button_SelectMaxEdges':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_SelectMaxEdges()
		elif sourceObjectName == 'Button_MoveX':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_MoveX()
		elif sourceObjectName == 'Button_MoveY':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_MoveY()
		elif sourceObjectName == 'Button_MoveZ':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_MoveZ()
		return False

	def Event_ItemsCount_1(self):
		self.window.Text_Items.setPlainText('\n'.join(maya_cmds.ls(selection=True)) + '\n')

	def Event_ItemsCount_3(self):
		self.window.Text_Items.moveCursor(QTextCursor.End)
		self.window.Text_Items.insertPlainText('\n'.join(maya_cmds.ls(selection=True)) + '\n')

	def Event_ItemsCount_2(self):
		self.window.Text_Items.clear()

	def Event_Items(self):
		text = self.window.Text_Items.toPlainText().strip()
		self.window.Label_ItemsCount.setText(str(text.count('\n') + 1) if text else '0')

	def Event_CalculateDistance(self):
		distances = self.Return_Distances()
		self.Activity_ShowDistance(distances)

	def Activity_ShowDistance(self, distances):
		self.window.Float_DistanceX.setValue(distances[0])
		self.window.Float_DistanceY.setValue(distances[1])
		self.window.Float_DistanceZ.setValue(distances[2])
		self.window.Float_DistanceXYZ.setValue(distances[3])

	def Return_Distances(self):
		items = self.window.Text_Items.toPlainText().strip().split('\n')

		vertices = maya_cmds.filterExpand(items, selectionMask=31)
		if vertices is not None and len(vertices) == 2:
			return self.Return_DistancesTwo(vertices)

		cvs = maya_cmds.filterExpand(items, selectionMask=28)
		if cvs is not None and len(cvs) == 2:
			return self.Return_DistancesTwo(cvs)

		curvePoints = maya_cmds.filterExpand(items, selectionMask=39)
		if curvePoints is not None and len(curvePoints) == 2:
			return self.Return_DistancesTwo(curvePoints)

		surfacePoints = maya_cmds.filterExpand(items, selectionMask=41)
		if surfacePoints is not None and len(surfacePoints) == 2:
			return self.Return_DistancesTwo(surfacePoints)

		locators = maya_cmds.filterExpand(items, selectionMask=22)
		if locators is not None and len(locators) == 2:
			return self.Return_DistancesTwo(locators)

		edges = maya_cmds.filterExpand(maya_cmds.polyListComponentConversion(items, toEdge=True), selectionMask=32)
		if edges is not None:
			distances = [0.0, 0.0, 0.0, 0.0]
			for i in range(len(edges)):
				edgeVertices = maya_cmds.filterExpand(maya_cmds.polyListComponentConversion(edges[i], toVertex=True), selectionMask=31)
				pos0 = maya_cmds.pointPosition(edgeVertices[0])
				pos1 = maya_cmds.pointPosition(edgeVertices[1])

				distances[0] += abs(pos0[0] - pos1[0])
				distances[1] += abs(pos0[1] - pos1[1])
				distances[2] += abs(pos0[2] - pos1[2])
				distances[3] += sqrt((pos0[0] - pos1[0]) ** 2 + (pos0[1] - pos1[1]) ** 2 + (pos0[2] - pos1[2]) ** 2)
			return distances

		return [-1.0, -1.0, -1.0, -1.0]

	@staticmethod
	def Return_DistancesTwo(locations):
		distances = [-1.0, -1.0, -1.0, -1.0]
		pos0 = maya_cmds.pointPosition(locations[0])
		pos1 = maya_cmds.pointPosition(locations[1])

		distances[0] = abs(pos0[0] - pos1[0])
		distances[1] = abs(pos0[1] - pos1[1])
		distances[2] = abs(pos0[2] - pos1[2])
		distances[3] = sqrt(distances[0] ** 2 + distances[1] ** 2 + distances[2] ** 2)
		return distances

	def Action_SelectMinEdges(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			items = self.window.Text_Items.toPlainText().strip().split('\n')
			edges = maya_cmds.filterExpand(maya_cmds.polyListComponentConversion(items, toEdge=True), selectionMask=32)
			precision = self.window.Float_Precision.value()

			distances = []
			for i in range(len(edges)):
				edgeVertices = maya_cmds.filterExpand(maya_cmds.polyListComponentConversion(edges[i], toVertex=True), selectionMask=31)
				pos0 = maya_cmds.pointPosition(edgeVertices[0])
				pos1 = maya_cmds.pointPosition(edgeVertices[1])
				distances.append([sqrt((pos0[0] - pos1[0]) ** 2 + (pos0[1] - pos1[1]) ** 2 + (pos0[2] - pos1[2]) ** 2), i])
			distances.sort(key=lambda s: s[0])

			self.Activity_ShowDistance([-1.0, -1.0, -1.0, distances[0][0]])
			result = [edges[distances[0][1]]]
			for i in range(1, len(distances)):
				if abs(distances[0][0] - distances[i][0]) <= precision:
					result.append(edges[distances[i][1]])
			maya_cmds.select(result)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Action_SelectMaxEdges(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			items = self.window.Text_Items.toPlainText().strip().split('\n')
			edges = maya_cmds.filterExpand(maya_cmds.polyListComponentConversion(items, toEdge=True), selectionMask=32)
			precision = self.window.Float_Precision.value()

			distances = []
			for i in range(len(edges)):
				edgeVertices = maya_cmds.filterExpand(maya_cmds.polyListComponentConversion(edges[i], toVertex=True), selectionMask=31)
				pos0 = maya_cmds.pointPosition(edgeVertices[0])
				pos1 = maya_cmds.pointPosition(edgeVertices[1])
				distances.append([sqrt((pos0[0] - pos1[0]) ** 2 + (pos0[1] - pos1[1]) ** 2 + (pos0[2] - pos1[2]) ** 2), i])
			distances.sort(key=lambda s: s[0], reverse=True)

			self.Activity_ShowDistance([-1.0, -1.0, -1.0, distances[0][0]])
			result = [edges[distances[0][1]]]
			for i in range(1, len(distances)):
				if abs(distances[0][0] - distances[i][0]) <= precision:
					result.append(edges[distances[i][1]])
			maya_cmds.select(result)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Action_MoveX(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			items = self.window.Text_Items.toPlainText().strip().split('\n')
			boundaries = maya_cmds.exactWorldBoundingBox(items, calculateExactly=True)
			if self.window.Radio_Min.isChecked():
				result = boundaries[0]
			elif self.window.Radio_Max.isChecked():
				result = boundaries[3]
			elif self.window.Radio_Cen.isChecked():
				result = (boundaries[0] + boundaries[3]) / 2.0

			self.Activity_ShowDistance([result, -1.0, -1.0, -1.0])
			if self.window.Check_TargetSelected.isChecked():
				maya_cmds.move(result, 0, 0, absolute=True, x=True)
			else:
				maya_cmds.move(result, 0, 0, items, absolute=True, x=True)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Action_MoveY(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			items = self.window.Text_Items.toPlainText().strip().split('\n')
			boundaries = maya_cmds.exactWorldBoundingBox(items, calculateExactly=True)
			if self.window.Radio_Min.isChecked():
				result = boundaries[1]
			elif self.window.Radio_Max.isChecked():
				result = boundaries[4]
			elif self.window.Radio_Cen.isChecked():
				result = (boundaries[1] + boundaries[4]) / 2.0

			self.Activity_ShowDistance([-1.0, result, -1.0, -1.0])
			if self.window.Check_TargetSelected.isChecked():
				maya_cmds.move(result, 0, 0, absolute=True, y=True)
			else:
				maya_cmds.move(result, 0, 0, items, absolute=True, y=True)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Action_MoveZ(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			items = self.window.Text_Items.toPlainText().strip().split('\n')
			boundaries = maya_cmds.exactWorldBoundingBox(items, calculateExactly=True)
			if self.window.Radio_Min.isChecked():
				result = boundaries[2]
			elif self.window.Radio_Max.isChecked():
				result = boundaries[5]
			elif self.window.Radio_Cen.isChecked():
				result = (boundaries[2] + boundaries[5]) / 2.0

			self.Activity_ShowDistance([-1.0, -1.0, result, -1.0])
			if self.window.Check_TargetSelected.isChecked():
				maya_cmds.move(result, 0, 0, absolute=True, z=True)
			else:
				maya_cmds.move(result, 0, 0, items, absolute=True, z=True)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)