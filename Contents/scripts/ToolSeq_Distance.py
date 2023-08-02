from math import sqrt, inf
from os.path import abspath, dirname
from sys import stderr

from PySide2.QtCore import QEvent, Qt
from PySide2.QtGui import QTextCursor
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QWidget, QComboBox, QStyledItemDelegate
from maya import cmds as maya_cmds
from maya.OpenMayaUI import MQtUtil
from shiboken2 import wrapInstance

class ToolSeq_Distance(QWidget):

	userScriptDir = dirname(abspath(__file__)) + '/'

	qUiLoader = QUiLoader()
	qUiLoader.setWorkingDirectory(userScriptDir)

	windowMain = wrapInstance(int(MQtUtil.mainWindow()), QMainWindow)

	def __init__(self):
		super(ToolSeq_Distance, self).__init__(ToolSeq_Distance.windowMain)

		self.window = ToolSeq_Distance.qUiLoader.load(ToolSeq_Distance.userScriptDir + 'ui/ToolSeq_Distance.ui', self)
		self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
		self.window.setAttribute(Qt.WA_DeleteOnClose)
		for qComboBox in self.window.findChildren(QComboBox):
			qComboBox.setItemDelegate(QStyledItemDelegate(qComboBox))
		with open(ToolSeq_Distance.userScriptDir + 'ToolSeq.qss', 'r') as fileStyleSheet:
			self.window.setStyleSheet(fileStyleSheet.read())

		self.window.Widget_01.installEventFilter(self)
		self.window.Text_Items.textChanged.connect(self.Event_Items)
		self.window.Button_CalculateDistance.installEventFilter(self)
		self.window.Button_CalculateBoundaries.installEventFilter(self)
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
		elif sourceObjectName == 'Button_CalculateBoundaries':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Event_CalculateBoundaries()
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
		distances = ToolSeq_Distance.Return_Distances(self.window.Text_Items.toPlainText().strip().split('\n'))
		self.Activity_ShowValues(distances)

	def Event_CalculateBoundaries(self):
		boundaries = ToolSeq_Distance.Return_Boundaries(self.window.Text_Items.toPlainText().strip().split('\n'))
		self.Activity_ShowValues(boundaries)

	def Activity_ShowValues(self, values):
		self.window.Float_DistanceX.setValue(values[0])
		self.window.Float_DistanceY.setValue(values[1])
		self.window.Float_DistanceZ.setValue(values[2])
		self.window.Float_DistanceXYZ.setValue(values[3])

	@staticmethod
	def Return_Distances(items):
		vertices = maya_cmds.filterExpand(items, selectionMask=31)
		if vertices is not None and len(vertices) == 2:
			return ToolSeq_Distance.Return_DistancesTwo(vertices)

		cvs = maya_cmds.filterExpand(items, selectionMask=28)
		if cvs is not None and len(cvs) == 2:
			return ToolSeq_Distance.Return_DistancesTwo(cvs)

		curvePoints = maya_cmds.filterExpand(items, selectionMask=39)
		if curvePoints is not None and len(curvePoints) == 2:
			return ToolSeq_Distance.Return_DistancesTwo(curvePoints)

		surfacePoints = maya_cmds.filterExpand(items, selectionMask=41)
		if surfacePoints is not None and len(surfacePoints) == 2:
			return ToolSeq_Distance.Return_DistancesTwo(surfacePoints)

		locators = maya_cmds.filterExpand(items, selectionMask=22)
		if locators is not None and len(locators) == 2:
			return ToolSeq_Distance.Return_DistancesTwo(locators)

		edges = maya_cmds.filterExpand(maya_cmds.polyListComponentConversion(items, toEdge=True), selectionMask=32)
		if edges is not None:
			distances = [0.0, 0.0, 0.0, 0.0]
			for i in range(len(edges)):
				edgeVertices = maya_cmds.filterExpand(maya_cmds.polyListComponentConversion(edges[i], toVertex=True), selectionMask=31)
				position0 = maya_cmds.pointPosition(edgeVertices[0])
				position1 = maya_cmds.pointPosition(edgeVertices[1])

				distances[0] += abs(position0[0] - position1[0])
				distances[1] += abs(position0[1] - position1[1])
				distances[2] += abs(position0[2] - position1[2])
				distances[3] += sqrt((position0[0] - position1[0]) ** 2 + (position0[1] - position1[1]) ** 2 + (position0[2] - position1[2]) ** 2)
			return distances

		return [-1.0, -1.0, -1.0, -1.0]

	@staticmethod
	def Return_Boundaries(items):
		items = maya_cmds.ls(items, transforms=True, shapes=True)
		if len(items) > 0:
			boundariesMin = [inf, inf, inf]
			boundariesMax = [-inf, -inf, -inf]
			for item in items:
				boundariesMin = [min(boundariesMin[0], maya_cmds.getAttr(item + '.boundingBoxMinX')), min(boundariesMin[1], maya_cmds.getAttr(item + '.boundingBoxMinY')), min(boundariesMin[2], maya_cmds.getAttr(item + '.boundingBoxMinZ'))]
				boundariesMax = [max(boundariesMax[0], maya_cmds.getAttr(item + '.boundingBoxMaxX')), max(boundariesMax[1], maya_cmds.getAttr(item + '.boundingBoxMaxY')), max(boundariesMax[2], maya_cmds.getAttr(item + '.boundingBoxMaxZ'))]
			return [boundariesMax[0] - boundariesMin[0], boundariesMax[1] - boundariesMin[1], boundariesMax[2] - boundariesMin[2], -1.0]

		vertices = maya_cmds.filterExpand(maya_cmds.polyListComponentConversion(items, toVertex=True), selectionMask=31)
		if vertices is not None:
			boundariesMin = [inf, inf, inf]
			boundariesMax = [-inf, -inf, -inf]
			for vertex in vertices:
				position = maya_cmds.pointPosition(vertex)
				boundariesMin = [min(boundariesMin[0], position[0]), min(boundariesMin[1], position[1]), min(boundariesMin[2], position[2])]
				boundariesMax = [max(boundariesMax[0], position[0]), max(boundariesMax[1], position[1]), max(boundariesMax[2], position[2])]
			return [boundariesMax[0] - boundariesMin[0], boundariesMax[1] - boundariesMin[1], boundariesMax[2] - boundariesMin[2], -1.0]

		return [-1.0, -1.0, -1.0, -1.0]

	@staticmethod
	def Return_DistancesTwo(locations):
		distances = [-1.0, -1.0, -1.0, -1.0]
		position0 = maya_cmds.pointPosition(locations[0])
		position1 = maya_cmds.pointPosition(locations[1])

		distances[0] = abs(position0[0] - position1[0])
		distances[1] = abs(position0[1] - position1[1])
		distances[2] = abs(position0[2] - position1[2])
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
				position0 = maya_cmds.pointPosition(edgeVertices[0])
				position1 = maya_cmds.pointPosition(edgeVertices[1])
				distances.append([sqrt((position0[0] - position1[0]) ** 2 + (position0[1] - position1[1]) ** 2 + (position0[2] - position1[2]) ** 2), i])
			distances.sort(key=lambda s: s[0])

			self.Activity_ShowValues([-1.0, -1.0, -1.0, distances[0][0]])
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
				position0 = maya_cmds.pointPosition(edgeVertices[0])
				position1 = maya_cmds.pointPosition(edgeVertices[1])
				distances.append([sqrt((position0[0] - position1[0]) ** 2 + (position0[1] - position1[1]) ** 2 + (position0[2] - position1[2]) ** 2), i])
			distances.sort(key=lambda s: s[0], reverse=True)

			self.Activity_ShowValues([-1.0, -1.0, -1.0, distances[0][0]])
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

			self.Activity_ShowValues([result, -1.0, -1.0, -1.0])
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

			self.Activity_ShowValues([-1.0, result, -1.0, -1.0])
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

			self.Activity_ShowValues([-1.0, -1.0, result, -1.0])
			if self.window.Check_TargetSelected.isChecked():
				maya_cmds.move(result, 0, 0, absolute=True, z=True)
			else:
				maya_cmds.move(result, 0, 0, items, absolute=True, z=True)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)