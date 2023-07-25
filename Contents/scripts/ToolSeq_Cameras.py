from os.path import abspath, dirname
from sys import stderr

from PySide2.QtCore import QEvent, Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QWidget, QComboBox, QStyledItemDelegate
from maya import cmds as maya_cmds
from maya.OpenMayaUI import MQtUtil
from maya.api import OpenMaya, OpenMayaUI
from shiboken2 import wrapInstance

ptrs = []

def ptrs_remove(ptr):
	if ptr in ptrs:
		ptrs.remove(ptr)

class ToolSeq_Cameras(QWidget):

	qUiLoader = QUiLoader()
	userScriptDir = dirname(abspath(__file__)) + '/'
	qUiLoader.setWorkingDirectory(userScriptDir)

	def __init__(self):
		ptrs.append(self)
		self.windowMain = wrapInstance(int(MQtUtil.mainWindow()), QMainWindow)
		super(ToolSeq_Cameras, self).__init__(self.windowMain)

		self.window = ToolSeq_Cameras.qUiLoader.load(ToolSeq_Cameras.userScriptDir + 'ui/ToolSeq_Cameras.ui', self)
		self.window.destroyed.connect(lambda: ptrs_remove(self))
		self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
		self.window.setAttribute(Qt.WA_DeleteOnClose)
		for qComboBox in self.window.findChildren(QComboBox):
			qComboBox.setItemDelegate(QStyledItemDelegate(qComboBox))
		with open(ToolSeq_Cameras.userScriptDir + 'ToolSeq.qss', 'r') as fileStyleSheet:
			self.window.setStyleSheet(fileStyleSheet.read())

		self.window.Button_P.installEventFilter(self)
		self.window.Button_TB.installEventFilter(self)
		self.window.Button_FB.installEventFilter(self)
		self.window.Button_LR.installEventFilter(self)

		maya_cmds.undoInfo(stateWithoutFlush=False)
		try:
			self.Activity_CreateAll()
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(stateWithoutFlush=True)

		self.window.show()

	def eventFilter(self, source, event):
		sourceObjectName = source.objectName()
		eventType = event.type()
		if sourceObjectName == 'Button_P':
			if eventType == QEvent.MouseButtonRelease:
				eventButton = event.button()
				if eventButton == Qt.LeftButton:
					self.Action_Camera('Camera_Perspective')
				elif eventButton == Qt.RightButton:
					self.Action_Camera('Camera_Perspective')
				elif eventButton == Qt.MiddleButton:
					ToolSeq_Cameras.Action_Ortographic()
		elif sourceObjectName == 'Button_TB':
			if eventType == QEvent.MouseButtonRelease:
				eventButton = event.button()
				if eventButton == Qt.LeftButton:
					self.Action_Camera('Camera_Top')
				elif eventButton == Qt.RightButton:
					self.Action_Camera('Camera_Bottom')
				elif eventButton == Qt.MiddleButton:
					ToolSeq_Cameras.Action_Ortographic()
		elif sourceObjectName == 'Button_FB':
			if eventType == QEvent.MouseButtonRelease:
				eventButton = event.button()
				if eventButton == Qt.LeftButton:
					self.Action_Camera('Camera_Front')
				elif eventButton == Qt.RightButton:
					self.Action_Camera('Camera_Back')
				elif eventButton == Qt.MiddleButton:
					ToolSeq_Cameras.Action_Ortographic()
		elif sourceObjectName == 'Button_LR':
			if eventType == QEvent.MouseButtonRelease:
				eventButton = event.button()
				if eventButton == Qt.LeftButton:
					self.Action_Camera('Camera_Left')
				elif eventButton == Qt.RightButton:
					self.Action_Camera('Camera_Right')
				elif eventButton == Qt.MiddleButton:
					ToolSeq_Cameras.Action_Ortographic()
		return False

	@staticmethod
	def Activity_CreateAll():
		selection = maya_cmds.ls(selection=True)

		if not maya_cmds.objExists('ToolSeq_Cameras'):
			maya_cmds.group(empty=True, name='ToolSeq_Cameras')
			maya_cmds.hide('ToolSeq_Cameras')
			maya_cmds.reorder('ToolSeq_Cameras', front=True)
		ToolSeq_Cameras.Activity_CreateCamera('Camera_Perspective', 'persp')
		ToolSeq_Cameras.Activity_CreateCamera('Camera_Top', 'top')
		ToolSeq_Cameras.Activity_CreateCamera('Camera_Bottom', 'bottom')
		ToolSeq_Cameras.Activity_CreateCamera('Camera_Front', 'front')
		ToolSeq_Cameras.Activity_CreateCamera('Camera_Back', 'back')
		ToolSeq_Cameras.Activity_CreateCamera('Camera_Left', 'left')
		ToolSeq_Cameras.Activity_CreateCamera('Camera_Right', 'right')

		maya_cmds.select(selection)

	@staticmethod
	def Activity_CreateCamera(cameraName, cameraDirection):
		if maya_cmds.objExists(cameraName):
			return

		if cameraDirection in ['persp', 'top', 'front', 'left']:
			maya_cmds.duplicate(cameraDirection.replace('left', 'side'), name=cameraName)
		elif cameraDirection == 'bottom':
			maya_cmds.duplicate('top', name=cameraName)
			maya_cmds.setAttr(cameraName + '.rotateX', 90)
		elif cameraDirection == 'back':
			maya_cmds.duplicate('front', name=cameraName)
			maya_cmds.setAttr(cameraName + '.rotateY', 180)
		elif cameraDirection == 'right':
			maya_cmds.duplicate('side', name=cameraName)
			maya_cmds.setAttr(cameraName + '.rotateY', -90)
		maya_cmds.hide(cameraName)
		maya_cmds.parent(cameraName, 'ToolSeq_Cameras')
		maya_cmds.reorder(cameraName, back=True)

	@staticmethod
	def Action_DeleteAll():
		maya_cmds.undoInfo(stateWithoutFlush=False)
		try:
			maya_cmds.lookThru('modelPanel1', 'top')
			maya_cmds.lookThru('modelPanel2', 'side')
			maya_cmds.lookThru('modelPanel3', 'front')
			maya_cmds.lookThru('modelPanel4', 'persp')
			maya_cmds.delete('Camera_Perspective', 'Camera_Top', 'Camera_Bottom', 'Camera_Front', 'Camera_Back', 'Camera_Left', 'Camera_Right', 'ToolSeq_Cameras')
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(stateWithoutFlush=True)

	def Action_Camera(self, cameraName):
		maya_cmds.undoInfo(stateWithoutFlush=False)
		try:
			if not maya_cmds.objExists(cameraName):
				self.Activity_CreateAll()
			maya_cmds.lookThru(cameraName)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(stateWithoutFlush=True)

	@staticmethod
	def Action_Ortographic():
		maya_cmds.undoInfo(stateWithoutFlush=False)
		try:
			orthographic = OpenMaya.MFnDependencyNode(OpenMayaUI.M3dView.active3dView().getCamera().node()).findPlug('orthographic', True)
			orthographic.setBool(not orthographic.asBool())
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(stateWithoutFlush=True)