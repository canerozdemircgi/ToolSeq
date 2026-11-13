from sys import stderr

from maya import cmds as maya_cmds
from maya.api import OpenMaya

maya_useNewAPI = True

def initializePlugin(mObject):
	OpenMaya.MFnPlugin(mObject).registerCommand(ToolSeq_Freeze_Apply.pluginName, ToolSeq_Freeze_Apply.cmdCreator, ToolSeq_Freeze_Apply.syntaxNew)

def uninitializePlugin(mObject):
	OpenMaya.MFnPlugin(mObject).deregisterCommand(ToolSeq_Freeze_Apply.pluginName)

class ToolSeq_Freeze_ApplyData(object):
	def __init__(self, movX, movY, movZ, rotX, rotY, rotZ, scaX, scaY, scaZ):
		self.movX = movX
		self.movY = movY
		self.movZ = movZ
		self.rotX = rotX
		self.rotY = rotY
		self.rotZ = rotZ
		self.scaX = scaX
		self.scaY = scaY
		self.scaZ = scaZ

class ToolSeq_Freeze_Apply(OpenMaya.MPxCommand):
	pluginName = 'ToolSeq_Freeze_Apply'

	transformsFlag = '-t'
	transformsFlagLong = '-transforms'

	isMovXFlag = '-imX'
	isMovXFlagLong = '-isMovX'
	isMovYFlag = '-imY'
	isMovYFlagLong = '-isMovY'
	isMovZFlag = '-imZ'
	isMovZFlagLong = '-isMovZ'
	isRotXFlag = '-irX'
	isRotXFlagLong = '-isRotX'
	isRotYFlag = '-irY'
	isRotYFlagLong = '-isRotY'
	isRotZFlag = '-irZ'
	isRotZFlagLong = '-isRotZ'
	isScaXFlag = '-isX'
	isScaXFlagLong = '-isScaX'
	isScaYFlag = '-isY'
	isScaYFlagLong = '-isScaY'
	isScaZFlag = '-isZ'
	isScaZFlagLong = '-isScaZ'

	movXFlag = '-mX'
	movXFlagLong = '-movX'
	movYFlag = '-mY'
	movYFlagLong = '-movY'
	movZFlag = '-mZ'
	movZFlagLong = '-movZ'
	rotXFlag = '-rX'
	rotXFlagLong = '-rotX'
	rotYFlag = '-rY'
	rotYFlagLong = '-rotY'
	rotZFlag = '-rZ'
	rotZFlagLong = '-rotZ'
	scaXFlag = '-sX'
	scaXFlagLong = '-scaX'
	scaYFlag = '-sY'
	scaYFlagLong = '-scaY'
	scaZFlag = '-sZ'
	scaZFlagLong = '-scaZ'

	def __init__(self):
		OpenMaya.MPxCommand.__init__(self)

		self.transforms = []
		self.matrixIs = None
		self.matrixOld = []
		self.matrixNew = []

	@staticmethod
	def cmdCreator():
		return ToolSeq_Freeze_Apply()

	@staticmethod
	def syntaxNew():
		syntax = OpenMaya.MSyntax()

		syntax.addFlag(ToolSeq_Freeze_Apply.transformsFlag, ToolSeq_Freeze_Apply.transformsFlagLong, OpenMaya.MSyntax.kString)

		syntax.addFlag(ToolSeq_Freeze_Apply.isMovXFlag, ToolSeq_Freeze_Apply.isMovXFlagLong, OpenMaya.MSyntax.kBoolean)
		syntax.addFlag(ToolSeq_Freeze_Apply.isMovYFlag, ToolSeq_Freeze_Apply.isMovYFlagLong, OpenMaya.MSyntax.kBoolean)
		syntax.addFlag(ToolSeq_Freeze_Apply.isMovZFlag, ToolSeq_Freeze_Apply.isMovZFlagLong, OpenMaya.MSyntax.kBoolean)
		syntax.addFlag(ToolSeq_Freeze_Apply.isRotXFlag, ToolSeq_Freeze_Apply.isRotXFlagLong, OpenMaya.MSyntax.kBoolean)
		syntax.addFlag(ToolSeq_Freeze_Apply.isRotYFlag, ToolSeq_Freeze_Apply.isRotYFlagLong, OpenMaya.MSyntax.kBoolean)
		syntax.addFlag(ToolSeq_Freeze_Apply.isRotZFlag, ToolSeq_Freeze_Apply.isRotZFlagLong, OpenMaya.MSyntax.kBoolean)
		syntax.addFlag(ToolSeq_Freeze_Apply.isScaXFlag, ToolSeq_Freeze_Apply.isScaXFlagLong, OpenMaya.MSyntax.kBoolean)
		syntax.addFlag(ToolSeq_Freeze_Apply.isScaYFlag, ToolSeq_Freeze_Apply.isScaYFlagLong, OpenMaya.MSyntax.kBoolean)
		syntax.addFlag(ToolSeq_Freeze_Apply.isScaZFlag, ToolSeq_Freeze_Apply.isScaZFlagLong, OpenMaya.MSyntax.kBoolean)

		syntax.addFlag(ToolSeq_Freeze_Apply.movXFlag, ToolSeq_Freeze_Apply.movXFlagLong, OpenMaya.MSyntax.kDouble)
		syntax.addFlag(ToolSeq_Freeze_Apply.movYFlag, ToolSeq_Freeze_Apply.movYFlagLong, OpenMaya.MSyntax.kDouble)
		syntax.addFlag(ToolSeq_Freeze_Apply.movZFlag, ToolSeq_Freeze_Apply.movZFlagLong, OpenMaya.MSyntax.kDouble)
		syntax.addFlag(ToolSeq_Freeze_Apply.rotXFlag, ToolSeq_Freeze_Apply.rotXFlagLong, OpenMaya.MSyntax.kDouble)
		syntax.addFlag(ToolSeq_Freeze_Apply.rotYFlag, ToolSeq_Freeze_Apply.rotYFlagLong, OpenMaya.MSyntax.kDouble)
		syntax.addFlag(ToolSeq_Freeze_Apply.rotZFlag, ToolSeq_Freeze_Apply.rotZFlagLong, OpenMaya.MSyntax.kDouble)
		syntax.addFlag(ToolSeq_Freeze_Apply.scaXFlag, ToolSeq_Freeze_Apply.scaXFlagLong, OpenMaya.MSyntax.kDouble)
		syntax.addFlag(ToolSeq_Freeze_Apply.scaYFlag, ToolSeq_Freeze_Apply.scaYFlagLong, OpenMaya.MSyntax.kDouble)
		syntax.addFlag(ToolSeq_Freeze_Apply.scaZFlag, ToolSeq_Freeze_Apply.scaZFlagLong, OpenMaya.MSyntax.kDouble)

		return syntax

	def isUndoable(self):
		return True

	def doIt(self, args):
		mArgParser = OpenMaya.MArgParser(self.syntax(), args)

		self.transforms = mArgParser.flagArgumentString(self.transformsFlag, 0).splitlines()

		self.matrixIs = ToolSeq_Freeze_ApplyData(
			mArgParser.flagArgumentBool(self.isMovXFlag, 0) if mArgParser.isFlagSet(self.isMovXFlag) else False,
			mArgParser.flagArgumentBool(self.isMovYFlag, 0) if mArgParser.isFlagSet(self.isMovYFlag) else False,
			mArgParser.flagArgumentBool(self.isMovZFlag, 0) if mArgParser.isFlagSet(self.isMovZFlag) else False,
			mArgParser.flagArgumentBool(self.isRotXFlag, 0) if mArgParser.isFlagSet(self.isRotXFlag) else False,
			mArgParser.flagArgumentBool(self.isRotYFlag, 0) if mArgParser.isFlagSet(self.isRotYFlag) else False,
			mArgParser.flagArgumentBool(self.isRotZFlag, 0) if mArgParser.isFlagSet(self.isRotZFlag) else False,
			mArgParser.flagArgumentBool(self.isScaXFlag, 0) if mArgParser.isFlagSet(self.isScaXFlag) else False,
			mArgParser.flagArgumentBool(self.isScaYFlag, 0) if mArgParser.isFlagSet(self.isScaYFlag) else False,
			mArgParser.flagArgumentBool(self.isScaZFlag, 0) if mArgParser.isFlagSet(self.isScaZFlag) else False
		)

		movXNew = mArgParser.flagArgumentDouble(self.movXFlag, 0) if self.matrixIs.movX else None
		movYNew = mArgParser.flagArgumentDouble(self.movYFlag, 0) if self.matrixIs.movY else None
		movZNew = mArgParser.flagArgumentDouble(self.movZFlag, 0) if self.matrixIs.movZ else None
		rotXNew = mArgParser.flagArgumentDouble(self.rotXFlag, 0) if self.matrixIs.rotX else None
		rotYNew = mArgParser.flagArgumentDouble(self.rotYFlag, 0) if self.matrixIs.rotY else None
		rotZNew = mArgParser.flagArgumentDouble(self.rotZFlag, 0) if self.matrixIs.rotZ else None
		scaXNew = mArgParser.flagArgumentDouble(self.scaXFlag, 0) if self.matrixIs.scaX else None
		scaYNew = mArgParser.flagArgumentDouble(self.scaYFlag, 0) if self.matrixIs.scaY else None
		scaZNew = mArgParser.flagArgumentDouble(self.scaZFlag, 0) if self.matrixIs.scaZ else None

		for i in range(len(self.transforms)):
			self.matrixOld.append(ToolSeq_Freeze_ApplyData(
				maya_cmds.getAttr(self.transforms[i] + '.translateX'),
				maya_cmds.getAttr(self.transforms[i] + '.translateY'),
				maya_cmds.getAttr(self.transforms[i] + '.translateZ'),
				maya_cmds.getAttr(self.transforms[i] + '.rotateX'),
				maya_cmds.getAttr(self.transforms[i] + '.rotateY'),
				maya_cmds.getAttr(self.transforms[i] + '.rotateZ'),
				maya_cmds.getAttr(self.transforms[i] + '.scaleX'),
				maya_cmds.getAttr(self.transforms[i] + '.scaleY'),
				maya_cmds.getAttr(self.transforms[i] + '.scaleZ')
			))
			self.matrixNew.append(ToolSeq_Freeze_ApplyData(
				movXNew,
				movYNew,
				movZNew,
				rotXNew,
				rotYNew,
				rotZNew,
				scaXNew,
				scaYNew,
				scaZNew
			))

		self.redoIt()

	def redoIt(self):
		self.Apply(self.matrixNew)

	def undoIt(self):
		self.Apply(self.matrixOld)

	def Apply(self, matrix):
		maya_cmds.undoInfo(stateWithoutFlush=False)
		try:
			shapes = maya_cmds.ls(maya_cmds.listRelatives(self.transforms, path=True, allDescendents=True), shapes=True)

			pivR = []
			pivS = []
			for i in range(len(self.transforms)):
				pivR.append(maya_cmds.xform(self.transforms[i], q=True, worldSpace=True, rotatePivot=True))
				pivS.append(maya_cmds.xform(self.transforms[i], q=True, worldSpace=True, scalePivot=True))
				maya_cmds.xform(self.transforms[i], worldSpace=True, zeroTransformPivots=True)

			mPoints = []
			for i in range(len(shapes)):
				mDagPath = OpenMaya.MGlobal.getSelectionListByName(shapes[i]).getDagPath(0)
				objectType = maya_cmds.objectType(shapes[i])
				if objectType == 'mesh':
					mPoints.append(OpenMaya.MFnMesh(mDagPath).getPoints(OpenMaya.MSpace.kWorld))
				elif objectType == 'nurbsCurve':
					mPoints.append(OpenMaya.MFnNurbsCurve(mDagPath).cvPositions(OpenMaya.MSpace.kWorld))
				elif objectType == 'nurbsSurface':
					mPoints.append(OpenMaya.MFnNurbsSurface(mDagPath).cvPositions(OpenMaya.MSpace.kWorld))
				else:
					raise TypeError('Not supported object type: ' + objectType)

			for i in range(len(self.transforms)):
				if self.matrixIs.movX:
					maya_cmds.setAttr(self.transforms[i] + '.translateX', matrix[i].movX)
				if self.matrixIs.movY:
					maya_cmds.setAttr(self.transforms[i] + '.translateY', matrix[i].movY)
				if self.matrixIs.movZ:
					maya_cmds.setAttr(self.transforms[i] + '.translateZ', matrix[i].movZ)
				if self.matrixIs.rotX:
					maya_cmds.setAttr(self.transforms[i] + '.rotateX', matrix[i].rotX)
				if self.matrixIs.rotY:
					maya_cmds.setAttr(self.transforms[i] + '.rotateY', matrix[i].rotY)
				if self.matrixIs.rotZ:
					maya_cmds.setAttr(self.transforms[i] + '.rotateZ', matrix[i].rotZ)
				if self.matrixIs.scaX:
					maya_cmds.setAttr(self.transforms[i] + '.scaleX', matrix[i].scaX)
				if self.matrixIs.scaY:
					maya_cmds.setAttr(self.transforms[i] + '.scaleY', matrix[i].scaY)
				if self.matrixIs.scaZ:
					maya_cmds.setAttr(self.transforms[i] + '.scaleZ', matrix[i].scaZ)
				maya_cmds.xform(self.transforms[i], worldSpace=True, rotatePivot=pivR[i], scalePivot=pivS[i])

			for i in range(len(shapes)):
				mDagPath = OpenMaya.MGlobal.getSelectionListByName(shapes[i]).getDagPath(0)
				objectType = maya_cmds.objectType(shapes[i])
				if objectType == 'mesh':
					mFnMesh = OpenMaya.MFnMesh(mDagPath)
					mFnMesh.setPoints(mPoints[i], OpenMaya.MSpace.kWorld)
					mFnMesh.updateSurface()
				elif objectType == 'nurbsCurve':
					mFnNurbsCurve = OpenMaya.MFnNurbsCurve(mDagPath)
					mFnNurbsCurve.setCVPositions(mPoints[i], OpenMaya.MSpace.kWorld)
					mFnNurbsCurve.updateCurve()
				elif objectType == 'nurbsSurface':
					mFnNurbsSurface = OpenMaya.MFnNurbsSurface(mDagPath)
					mFnNurbsSurface.setCVPositions(mPoints[i], OpenMaya.MSpace.kWorld)
					mFnNurbsSurface.updateSurface()
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(stateWithoutFlush=True)