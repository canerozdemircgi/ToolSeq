import itertools
import re
from os.path import abspath, dirname
from sys import stderr

from PySide2.QtCore import QEvent, Qt
from PySide2.QtGui import QTextCursor
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QWidget, QComboBox, QStyledItemDelegate
from maya import cmds as maya_cmds
from maya.OpenMayaUI import MQtUtil
from shiboken2 import wrapInstance

class ToolSeq_ReNamer(QWidget):

	userScriptDir = dirname(abspath(__file__)) + '/'

	qUiLoader = QUiLoader()
	qUiLoader.setWorkingDirectory(userScriptDir)

	windowMain = wrapInstance(int(MQtUtil.mainWindow()), QMainWindow)

	def __init__(self):
		super(ToolSeq_ReNamer, self).__init__(ToolSeq_ReNamer.windowMain)

		self.window = ToolSeq_ReNamer.qUiLoader.load(ToolSeq_ReNamer.userScriptDir + 'ui/ToolSeq_ReNamer.ui', self)
		self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
		self.window.setAttribute(Qt.WA_DeleteOnClose)
		for qComboBox in self.window.findChildren(QComboBox):
			qComboBox.setItemDelegate(QStyledItemDelegate(qComboBox))
		with open(ToolSeq_ReNamer.userScriptDir + 'ToolSeq.qss') as fileStyleSheet:
			self.window.setStyleSheet(fileStyleSheet.read())

		self.window.Widget_01.installEventFilter(self)
		self.window.Text_Transforms.textChanged.connect(self.Event_Transforms)
		self.window.Button_Select.installEventFilter(self)
		self.window.Button_Rename.installEventFilter(self)

		self.window.show()

	def eventFilter(self, source, event):
		sourceObjectName = source.objectName()
		eventType = event.type()
		if sourceObjectName == 'Widget_01':
			if eventType == QEvent.MouseButtonRelease:
				eventButton = event.button()
				if eventButton == Qt.LeftButton:
					self.Event_TransformsCount_1()
				elif eventButton == Qt.RightButton:
					self.Event_TransformsCount_3()
				elif eventButton == Qt.MiddleButton:
					self.Event_TransformsCount_2()
		elif sourceObjectName == 'Button_Select':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_Select()
		elif sourceObjectName == 'Button_Rename':
			if eventType == QEvent.MouseButtonRelease:
				if event.button() == Qt.LeftButton:
					self.Action_Rename()
		return False

	def Event_TransformsCount_1(self):
		self.window.Text_Transforms.setPlainText('\n'.join(maya_cmds.ls(selection=True, transforms=True)) + '\n')

	def Event_TransformsCount_3(self):
		self.window.Text_Transforms.moveCursor(QTextCursor.End)
		self.window.Text_Transforms.insertPlainText('\n'.join(maya_cmds.ls(selection=True, transforms=True)) + '\n')

	def Event_TransformsCount_2(self):
		self.window.Text_Transforms.clear()

	def Event_Transforms(self):
		text = self.window.Text_Transforms.toPlainText().strip()
		self.window.Label_TransformsCount.setText(str(text.count('\n') + 1) if text else '0')

	def Action_Select(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			transforms = self.window.Text_Transforms.toPlainText().strip().splitlines()
			searchStr = self.window.Line_Search.text().strip()

			results = self.Activity_Search(transforms, searchStr)
			maya_cmds.select(results)
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(closeChunk=True)

	def Action_Rename(self):
		maya_cmds.undoInfo(openChunk=True)
		try:
			transforms = self.window.Text_Transforms.toPlainText().strip().splitlines()
			searchStr = self.window.Line_Search.text().strip()
			if searchStr == '':
				return
			replaceStr = self.window.Line_Replace.text().strip()

			transforms = self.Filter_Instances(transforms)

			results = self.Activity_Rename(transforms, searchStr, replaceStr)
			results.sort(key=lambda s: s.count('|'))
			results.reverse()

			print('ToolSeq_ReNamer: %s objects will be renamed' % len(results))
			for filtered, renamed in results:
				maya_cmds.rename(filtered, renamed)
				print('ToolSeq_ReNamer: %s => %s' % (filtered, renamed))
			maya_cmds.confirmDialog(title='ToolSeq_ReNamer', message='%s objects have been renamed' % len(results), button=['OK'])
			self.Event_TransformsCount_2()
		except Exception as e:
			print(str(e), file=stderr)
			maya_cmds.confirmDialog(title='ToolSeq_ReNamer', message='Unexpected error has been occurred, check Script Editor', button=['OK'])
		maya_cmds.undoInfo(closeChunk=True)

	def Activity_Search(self, sources, searchStr):
		if self.window.Check_Regex.isChecked():
			if self.window.Check_CaseSensitive.isChecked():
				searchRe = re.compile(searchStr)
			else:
				searchRe = re.compile(searchStr, re.IGNORECASE)
			results = [source for source in sources if searchRe.search(source.split('|')[-1] if '|' in source else source)]
		else:
			if self.window.Check_CaseSensitive.isChecked():
				results = [source for source in sources if searchStr in (source.split('|')[-1] if '|' in source else source)]
			else:
				results = [source for source in sources if searchStr.lower() in (source.split('|')[-1].lower() if '|' in source else source.lower())]
		return results

	def Activity_Rename(self, sources, searchStr, replaceStr):
		if self.window.Check_Regex.isChecked():
			if self.window.Check_CaseSensitive.isChecked():
				searchRe = re.compile(searchStr)
			else:
				searchRe = re.compile(searchStr, re.IGNORECASE)
			results = []
			for source in sources:
				sourceSplit = source.split('|')
				if searchRe.search(sourceSplit[-1] if '|' in source else source):
					results.append((source, searchRe.sub(replaceStr, sourceSplit[-1])))
		else:
			if self.window.Check_CaseSensitive.isChecked():
				results = []
				for source in sources:
					sourceSplit = source.split('|')
					if searchStr in (sourceSplit[-1] if '|' in source else source):
						results.append((source, sourceSplit[-1].replace(searchStr, replaceStr)))
			else:
				results = []
				for source in sources:
					sourceSplit = source.split('|')
					if searchStr.lower() in (sourceSplit[-1].lower() if '|' in source else source.lower()):
						results.append((source, ToolSeq_ReNamer.Replace_All_IgnoreCase(sourceSplit[-1], searchStr, replaceStr)))
		return results

	@staticmethod
	def Replace_All_IgnoreCase(sourceStr, searchStr, replaceStr):
		sourceStrLower = sourceStr.lower()
		searchStrLower = searchStr.lower()

		result = ''
		indexSta = 0

		while (index := sourceStrLower.find(searchStrLower, indexSta)) != -1:
			result += sourceStr[indexSta:index] + replaceStr
			indexSta = index + len(searchStr)

		result += sourceStr[indexSta:]
		return result

	@staticmethod
	def Filter_Instances(transforms):
		result = {}
		for transform in transforms:
			if '|' in transform:
				transformParents = maya_cmds.listRelatives(transform, path=True, allParents=True)
				if (len(transformParents) if transformParents is not None else 0) > 1:
					frozensetTransformParents = frozenset(transformParents)
					if frozensetTransformParents not in result:
						result[frozensetTransformParents] = maya_cmds.listRelatives(transformParents[0], path=True, children=True)
				else:
					result[transform] = [transform]
			else:
				result[transform] = [transform]
		return list(itertools.chain.from_iterable(result.values()))