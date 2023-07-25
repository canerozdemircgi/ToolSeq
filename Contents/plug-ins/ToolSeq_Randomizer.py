from sys import stderr

from _ctypes import PyObj_FromPtr
from maya import cmds as maya_cmds
from maya.api import OpenMaya

maya_useNewAPI = True

def initializePlugin(mObject):
	OpenMaya.MFnPlugin(mObject).registerCommand(ToolSeq_Randomizer_Apply.pluginName, ToolSeq_Randomizer_Apply.cmdCreator, ToolSeq_Randomizer_Apply.syntaxNew)

def uninitializePlugin(mObject):
	OpenMaya.MFnPlugin(mObject).deregisterCommand(ToolSeq_Randomizer_Apply.pluginName)

class ToolSeq_Randomizer_Apply(OpenMaya.MPxCommand):
	pluginName = 'ToolSeq_Randomizer_Apply'

	operationFlag = '-o'
	operationFlagLong = '-operation'

	randomsFlag = '-r'
	randomsFlagLong = '-randoms'

	itemsFlag = '-i'
	itemsFlagLong = '-items'

	def __init__(self):
		OpenMaya.MPxCommand.__init__(self)

		self.operation = None
		self.randoms = None
		self.items = None

		self.mPointsDict = {}

	@staticmethod
	def cmdCreator():
		return ToolSeq_Randomizer_Apply()

	@staticmethod
	def syntaxNew():
		syntax = OpenMaya.MSyntax()

		syntax.addFlag(ToolSeq_Randomizer_Apply.operationFlag, ToolSeq_Randomizer_Apply.operationFlagLong, OpenMaya.MSyntax.kString)
		syntax.addFlag(ToolSeq_Randomizer_Apply.randomsFlag, ToolSeq_Randomizer_Apply.randomsFlagLong, OpenMaya.MSyntax.kString)
		syntax.addFlag(ToolSeq_Randomizer_Apply.itemsFlag, ToolSeq_Randomizer_Apply.itemsFlagLong, OpenMaya.MSyntax.kString)

		return syntax

	def isUndoable(self):
		return True

	def doIt(self, args):
		mArgParser = OpenMaya.MArgParser(self.syntax(), args)

		self.operation = mArgParser.flagArgumentString(self.operationFlag, 0)
		self.randoms = PyObj_FromPtr(int(mArgParser.flagArgumentString(self.randomsFlag, 0), 0))
		self.items = PyObj_FromPtr(int(mArgParser.flagArgumentString(self.itemsFlag, 0), 0))

		self.redoIt()

	def redoIt(self):
		maya_cmds.undoInfo(stateWithoutFlush=False)
		try:
			selections = OpenMaya.MSelectionList()
			for items in self.items:
				for item in items:
					selections.add(item)

			mPointsDict = {}
			mNormalsDict = {}
			for i in range(selections.length()):
				mDagPath = selections.getDagPath(i)
				mDagPathName = mDagPath.partialPathName()
				if mDagPathName not in mPointsDict:
					objectType = maya_cmds.objectType(mDagPathName)
					if objectType == 'mesh':
						mFnMesh = OpenMaya.MFnMesh(mDagPath)
						mPoints = mFnMesh.getPoints(OpenMaya.MSpace.kWorld)
						if self.operation == 'movN':
							mNormalsDict[mDagPathName] = mFnMesh.getVertexNormals(True, OpenMaya.MSpace.kWorld)
						mPointsDict[mDagPathName] = mPoints
						self.mPointsDict[mDagPathName] = OpenMaya.MPointArray(mPoints)
					elif objectType == 'nurbsCurve':
						mFnNurbsCurve = OpenMaya.MFnNurbsCurve(mDagPath)
						mPoints = mFnNurbsCurve.cvPositions(OpenMaya.MSpace.kWorld)
						mPointsDict[mDagPathName] = mPoints
						self.mPointsDict[mDagPathName] = OpenMaya.MPointArray(mPoints)
					elif objectType == 'nurbsSurface':
						mFnNurbsSurface = OpenMaya.MFnNurbsSurface(mDagPath)
						mPoints = mFnNurbsSurface.cvPositions(OpenMaya.MSpace.kWorld)
						mPointsDict[mDagPathName] = mPoints
						self.mPointsDict[mDagPathName] = OpenMaya.MPointArray(mPoints)
					elif objectType == 'transform':
						mPointsDict[mDagPathName] = None
						self.mPointsDict[mDagPathName] = None
					else:
						print('Not supported object type: ' + objectType, file=stderr)

			if self.operation == 'movX':
				for items in self.items:
					random = self.randoms.Get()
					for item in items:
						selection = OpenMaya.MSelectionList()
						selection.add(item)
						mDagPath, mObj = selection.getComponent(0)
						mPoints = mPointsDict[mDagPath.partialPathName()]

						apiType = mObj.apiType()
						if apiType == OpenMaya.MFn.kMeshVertComponent or apiType == OpenMaya.MFn.kCurveCVComponent or apiType == OpenMaya.MFn.kSurfaceCVComponent:
							iterator = OpenMaya.MItGeometry(mDagPath, mObj)
							while not iterator.isDone():
								index = iterator.index()
								mPoints[index].x += random
								iterator.next()
						elif apiType == OpenMaya.MFn.kMeshEdgeComponent:
							iterator = OpenMaya.MItMeshEdge(mDagPath, mObj)
							while not iterator.isDone():
								indexes = [iterator.vertexId(0), iterator.vertexId(1)]
								for i in range(len(indexes)):
									mPoints[indexes[i]].x += random
								iterator.next()
						elif apiType == OpenMaya.MFn.kMeshPolygonComponent:
							iterator = OpenMaya.MItMeshPolygon(mDagPath, mObj)
							while not iterator.isDone():
								indexes = iterator.getVertices()
								for i in range(len(indexes)):
									mPoints[indexes[i]].x += random
								iterator.next()
						elif apiType == OpenMaya.MFn.kInvalid:
							maya_cmds.undoInfo(stateWithoutFlush=True)
							maya_cmds.move(random, 0, 0, item, relative=True, x=True)
							maya_cmds.undoInfo(stateWithoutFlush=False)
						else:
							print('Not supported component type: ' + mObj.apiTypeStr, file=stderr)

			elif self.operation == 'movY':
				for items in self.items:
					random = self.randoms.Get()
					for item in items:
						selection = OpenMaya.MSelectionList()
						selection.add(item)
						mDagPath, mObj = selection.getComponent(0)
						mPoints = mPointsDict[mDagPath.partialPathName()]

						apiType = mObj.apiType()
						if apiType == OpenMaya.MFn.kMeshVertComponent or apiType == OpenMaya.MFn.kCurveCVComponent or apiType == OpenMaya.MFn.kSurfaceCVComponent:
							iterator = OpenMaya.MItGeometry(mDagPath, mObj)
							while not iterator.isDone():
								index = iterator.index()
								mPoints[index].y += random
								iterator.next()
						elif apiType == OpenMaya.MFn.kMeshEdgeComponent:
							iterator = OpenMaya.MItMeshEdge(mDagPath, mObj)
							while not iterator.isDone():
								indexes = [iterator.vertexId(0), iterator.vertexId(1)]
								for i in range(len(indexes)):
									mPoints[indexes[i]].y += random
								iterator.next()
						elif apiType == OpenMaya.MFn.kMeshPolygonComponent:
							iterator = OpenMaya.MItMeshPolygon(mDagPath, mObj)
							while not iterator.isDone():
								indexes = iterator.getVertices()
								for i in range(len(indexes)):
									mPoints[indexes[i]].y += random
								iterator.next()
						elif apiType == OpenMaya.MFn.kInvalid:
							maya_cmds.undoInfo(stateWithoutFlush=True)
							maya_cmds.move(random, 0, 0, item, relative=True, y=True)
							maya_cmds.undoInfo(stateWithoutFlush=False)
						else:
							print('Not supported component type: ' + mObj.apiTypeStr, file=stderr)

			elif self.operation == 'movZ':
				for items in self.items:
					random = self.randoms.Get()
					for item in items:
						selection = OpenMaya.MSelectionList()
						selection.add(item)
						mDagPath, mObj = selection.getComponent(0)
						mPoints = mPointsDict[mDagPath.partialPathName()]

						apiType = mObj.apiType()
						if apiType == OpenMaya.MFn.kMeshVertComponent or apiType == OpenMaya.MFn.kCurveCVComponent or apiType == OpenMaya.MFn.kSurfaceCVComponent:
							iterator = OpenMaya.MItGeometry(mDagPath, mObj)
							while not iterator.isDone():
								index = iterator.index()
								mPoints[index].z += random
								iterator.next()
						elif apiType == OpenMaya.MFn.kMeshEdgeComponent:
							iterator = OpenMaya.MItMeshEdge(mDagPath, mObj)
							while not iterator.isDone():
								indexes = [iterator.vertexId(0), iterator.vertexId(1)]
								for i in range(len(indexes)):
									mPoints[indexes[i]].z += random
								iterator.next()
						elif apiType == OpenMaya.MFn.kMeshPolygonComponent:
							iterator = OpenMaya.MItMeshPolygon(mDagPath, mObj)
							while not iterator.isDone():
								indexes = iterator.getVertices()
								for i in range(len(indexes)):
									mPoints[indexes[i]].z += random
								iterator.next()
						elif apiType == OpenMaya.MFn.kInvalid:
							maya_cmds.undoInfo(stateWithoutFlush=True)
							maya_cmds.move(random, 0, 0, item, relative=True, z=True)
							maya_cmds.undoInfo(stateWithoutFlush=False)
						else:
							print('Not supported component type: ' + mObj.apiTypeStr, file=stderr)

			elif self.operation == 'movN':
				for items in self.items:
					random = self.randoms.Get()
					for item in items:
						selection = OpenMaya.MSelectionList()
						selection.add(item)
						mDagPath, mObj = selection.getComponent(0)
						mDagPathName = mDagPath.partialPathName()
						mPoints = mPointsDict[mDagPathName]
						mNormals = mNormalsDict[mDagPathName]

						apiType = mObj.apiType()
						if apiType == OpenMaya.MFn.kMeshVertComponent or apiType == OpenMaya.MFn.kCurveCVComponent or apiType == OpenMaya.MFn.kSurfaceCVComponent:
							iterator = OpenMaya.MItGeometry(mDagPath, mObj)
							while not iterator.isDone():
								index = iterator.index()
								mPoints[index] += OpenMaya.MPoint(random * mNormals[index])
								iterator.next()
						elif apiType == OpenMaya.MFn.kMeshEdgeComponent:
							iterator = OpenMaya.MItMeshEdge(mDagPath, mObj)
							while not iterator.isDone():
								indexes = [iterator.vertexId(0), iterator.vertexId(1)]
								for i in range(len(indexes)):
									mPoints[indexes[i]] += OpenMaya.MPoint(random * mNormals[indexes[i]])
								iterator.next()
						elif apiType == OpenMaya.MFn.kMeshPolygonComponent:
							iterator = OpenMaya.MItMeshPolygon(mDagPath, mObj)
							while not iterator.isDone():
								indexes = iterator.getVertices()
								for i in range(len(indexes)):
									mPoints[indexes[i]] += OpenMaya.MPoint(random * mNormals[indexes[i]])
								iterator.next()
						else:
							print('Not supported component type: ' + mObj.apiTypeStr, file=stderr)

			for key in mPointsDict:
				selection = OpenMaya.MSelectionList()
				selection.add(key)
				mDagPath = selection.getDagPath(0)
				mDagPathName = mDagPath.partialPathName()
				objectType = maya_cmds.objectType(mDagPathName)
				if objectType == 'mesh':
					mFnMesh = OpenMaya.MFnMesh(mDagPath)
					mFnMesh.setPoints(mPointsDict[mDagPathName], OpenMaya.MSpace.kWorld)
					mFnMesh.updateSurface()
				elif objectType == 'nurbsCurve':
					mFnNurbsCurve = OpenMaya.MFnNurbsCurve(mDagPath)
					mFnNurbsCurve.setCVPositions(mPointsDict[mDagPathName], OpenMaya.MSpace.kWorld)
					mFnNurbsCurve.updateCurve()
				elif objectType == 'nurbsSurface':
					mFnNurbsSurface = OpenMaya.MFnNurbsSurface(mDagPath)
					mFnNurbsSurface.setCVPositions(mPointsDict[mDagPathName], OpenMaya.MSpace.kWorld)
					mFnNurbsSurface.updateSurface()
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(stateWithoutFlush=True)

	def undoIt(self):
		maya_cmds.undoInfo(stateWithoutFlush=False)
		try:
			for key in self.mPointsDict:
				selection = OpenMaya.MSelectionList()
				selection.add(key)
				mDagPath = selection.getDagPath(0)
				mDagPathName = mDagPath.partialPathName()
				objectType = maya_cmds.objectType(mDagPathName)
				if objectType == 'mesh':
					mFnMesh = OpenMaya.MFnMesh(mDagPath)
					mFnMesh.setPoints(self.mPointsDict[mDagPathName], OpenMaya.MSpace.kWorld)
					mFnMesh.updateSurface()
				elif objectType == 'nurbsCurve':
					mFnNurbsCurve = OpenMaya.MFnNurbsCurve(mDagPath)
					mFnNurbsCurve.setCVPositions(self.mPointsDict[mDagPathName], OpenMaya.MSpace.kWorld)
					mFnNurbsCurve.updateCurve()
				elif objectType == 'nurbsSurface':
					mFnNurbsSurface = OpenMaya.MFnNurbsSurface(mDagPath)
					mFnNurbsSurface.setCVPositions(self.mPointsDict[mDagPathName], OpenMaya.MSpace.kWorld)
					mFnNurbsSurface.updateSurface()
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(stateWithoutFlush=True)