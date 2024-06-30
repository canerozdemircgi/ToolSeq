from sys import stderr

from PySide2.QtGui import QImage
from maya import cmds as maya_cmds
from maya.api import OpenMaya

maya_useNewAPI = True

def initializePlugin(mObject):
	OpenMaya.MFnPlugin(mObject).registerCommand(ToolSeq_Displacement_Apply.pluginName, ToolSeq_Displacement_Apply.cmdCreator, ToolSeq_Displacement_Apply.syntaxNew)

def uninitializePlugin(mObject):
	OpenMaya.MFnPlugin(mObject).deregisterCommand(ToolSeq_Displacement_Apply.pluginName)

class ToolSeq_Displacement_ApplyData(object):
	def __init__(self, X, Y, Z, N):
		self.X = X
		self.Y = Y
		self.Z = Z
		self.N = N

class ToolSeq_Displacement_Apply(OpenMaya.MPxCommand):
	pluginName = 'ToolSeq_Displacement_Apply'

	shapeFlag = '-s'
	shapeFlagLong = '-shape'
	uvNameFlag = '-uv'
	uvNameFlagLong = '-uvName'
	imageFlag = '-i'
	imageFlagLong = '-image'

	isXFlag = '-iX'
	isXFlagLong = '-iscX'
	isYFlag = '-iY'
	isYFlagLong = '-iscY'
	isZFlag = '-iZ'
	isZFlagLong = '-iscZ'
	isNFlag = '-iN'
	isNFlagLong = '-iscN'

	chaXFlag = '-cX'
	chaXFlagLong = '-chaX'
	chaYFlag = '-cY'
	chaYFlagLong = '-chaY'
	chaZFlag = '-cZ'
	chaZFlagLong = '-chaZ'
	chaNFlag = '-cN'
	chaNFlagLong = '-chaN'
	minXFlag = '-miX'
	minXFlagLong = '-minX'
	minYFlag = '-miY'
	minYFlagLong = '-minY'
	minZFlag = '-miZ'
	minZFlagLong = '-minZ'
	minNFlag = '-miN'
	minNFlagLong = '-minN'
	maxXFlag = '-maX'
	maxXFlagLong = '-maxX'
	maxYFlag = '-maY'
	maxYFlagLong = '-maxY'
	maxZFlag = '-maZ'
	maxZFlagLong = '-maxZ'
	maxNFlag = '-maN'
	maxNFlagLong = '-maxN'

	def __init__(self):
		OpenMaya.MPxCommand.__init__(self)

		self.shape = None
		self.uvName = None
		self.image = None

		self.matrixIs = None
		self.matrixCha = None
		self.matrixMin = None
		self.matrixMax = None

		self.mPoints = None

	@staticmethod
	def cmdCreator():
		return ToolSeq_Displacement_Apply()

	@staticmethod
	def syntaxNew():
		syntax = OpenMaya.MSyntax()

		syntax.addFlag(ToolSeq_Displacement_Apply.shapeFlag, ToolSeq_Displacement_Apply.shapeFlagLong, OpenMaya.MSyntax.kString)
		syntax.addFlag(ToolSeq_Displacement_Apply.uvNameFlag, ToolSeq_Displacement_Apply.uvNameFlagLong, OpenMaya.MSyntax.kString)
		syntax.addFlag(ToolSeq_Displacement_Apply.imageFlag, ToolSeq_Displacement_Apply.imageFlagLong, OpenMaya.MSyntax.kString)

		syntax.addFlag(ToolSeq_Displacement_Apply.isXFlag, ToolSeq_Displacement_Apply.isXFlagLong, OpenMaya.MSyntax.kBoolean)
		syntax.addFlag(ToolSeq_Displacement_Apply.isYFlag, ToolSeq_Displacement_Apply.isYFlagLong, OpenMaya.MSyntax.kBoolean)
		syntax.addFlag(ToolSeq_Displacement_Apply.isZFlag, ToolSeq_Displacement_Apply.isZFlagLong, OpenMaya.MSyntax.kBoolean)
		syntax.addFlag(ToolSeq_Displacement_Apply.isNFlag, ToolSeq_Displacement_Apply.isNFlagLong, OpenMaya.MSyntax.kBoolean)

		syntax.addFlag(ToolSeq_Displacement_Apply.chaXFlag, ToolSeq_Displacement_Apply.chaXFlagLong, OpenMaya.MSyntax.kLong)
		syntax.addFlag(ToolSeq_Displacement_Apply.chaYFlag, ToolSeq_Displacement_Apply.chaYFlagLong, OpenMaya.MSyntax.kLong)
		syntax.addFlag(ToolSeq_Displacement_Apply.chaZFlag, ToolSeq_Displacement_Apply.chaZFlagLong, OpenMaya.MSyntax.kLong)
		syntax.addFlag(ToolSeq_Displacement_Apply.chaNFlag, ToolSeq_Displacement_Apply.chaNFlagLong, OpenMaya.MSyntax.kLong)

		syntax.addFlag(ToolSeq_Displacement_Apply.minXFlag, ToolSeq_Displacement_Apply.minXFlagLong, OpenMaya.MSyntax.kDouble)
		syntax.addFlag(ToolSeq_Displacement_Apply.minYFlag, ToolSeq_Displacement_Apply.minYFlagLong, OpenMaya.MSyntax.kDouble)
		syntax.addFlag(ToolSeq_Displacement_Apply.minZFlag, ToolSeq_Displacement_Apply.minZFlagLong, OpenMaya.MSyntax.kDouble)
		syntax.addFlag(ToolSeq_Displacement_Apply.minNFlag, ToolSeq_Displacement_Apply.minNFlagLong, OpenMaya.MSyntax.kDouble)
		syntax.addFlag(ToolSeq_Displacement_Apply.maxXFlag, ToolSeq_Displacement_Apply.maxXFlagLong, OpenMaya.MSyntax.kDouble)
		syntax.addFlag(ToolSeq_Displacement_Apply.maxYFlag, ToolSeq_Displacement_Apply.maxYFlagLong, OpenMaya.MSyntax.kDouble)
		syntax.addFlag(ToolSeq_Displacement_Apply.maxZFlag, ToolSeq_Displacement_Apply.maxZFlagLong, OpenMaya.MSyntax.kDouble)
		syntax.addFlag(ToolSeq_Displacement_Apply.maxNFlag, ToolSeq_Displacement_Apply.maxNFlagLong, OpenMaya.MSyntax.kDouble)

		return syntax

	def isUndoable(self):
		return True

	def doIt(self, args):
		mArgParser = OpenMaya.MArgParser(self.syntax(), args)

		self.shape = mArgParser.flagArgumentString(self.shapeFlag, 0)
		self.uvName = mArgParser.flagArgumentString(self.uvNameFlag, 0)
		self.image = mArgParser.flagArgumentString(self.imageFlag, 0)

		self.matrixIs = ToolSeq_Displacement_ApplyData(
			mArgParser.flagArgumentBool(self.isXFlag, 0) if mArgParser.isFlagSet(self.isXFlag) else False,
			mArgParser.flagArgumentBool(self.isYFlag, 0) if mArgParser.isFlagSet(self.isYFlag) else False,
			mArgParser.flagArgumentBool(self.isZFlag, 0) if mArgParser.isFlagSet(self.isZFlag) else False,
			mArgParser.flagArgumentBool(self.isNFlag, 0) if mArgParser.isFlagSet(self.isNFlag) else False
		)
		self.matrixCha = ToolSeq_Displacement_ApplyData(
			mArgParser.flagArgumentInt(self.chaXFlag, 0) if self.matrixIs.X else None,
			mArgParser.flagArgumentInt(self.chaYFlag, 0) if self.matrixIs.Y else None,
			mArgParser.flagArgumentInt(self.chaZFlag, 0) if self.matrixIs.Z else None,
			mArgParser.flagArgumentInt(self.chaNFlag, 0) if self.matrixIs.N else None
		)
		self.matrixMin = ToolSeq_Displacement_ApplyData(
			mArgParser.flagArgumentDouble(self.minXFlag, 0) if self.matrixIs.X else None,
			mArgParser.flagArgumentDouble(self.minYFlag, 0) if self.matrixIs.Y else None,
			mArgParser.flagArgumentDouble(self.minZFlag, 0) if self.matrixIs.Z else None,
			mArgParser.flagArgumentDouble(self.minNFlag, 0) if self.matrixIs.N else None
		)
		self.matrixMax = ToolSeq_Displacement_ApplyData(
			mArgParser.flagArgumentDouble(self.maxXFlag, 0) if self.matrixIs.X else None,
			mArgParser.flagArgumentDouble(self.maxYFlag, 0) if self.matrixIs.Y else None,
			mArgParser.flagArgumentDouble(self.maxZFlag, 0) if self.matrixIs.Z else None,
			mArgParser.flagArgumentDouble(self.maxNFlag, 0) if self.matrixIs.N else None
		)

		self.redoIt()

	def redoIt(self):
		maya_cmds.undoInfo(stateWithoutFlush=False)
		try:
			image = QImage(self.image)
			if image.format() != QImage.Format_RGBA8888:
				image = image.convertToFormat(QImage.Format_RGBA8888)

			imageBits = image.bits()
			imageWidth = image.width()
			imageHeight = image.height()
			imageWidthM = imageWidth - 1
			imageHeightM = imageHeight - 1

			mFnMesh = OpenMaya.MFnMesh(OpenMaya.MGlobal.getSelectionListByName(self.shape).getDagPath(0))
			mPoints = mFnMesh.getPoints(OpenMaya.MSpace.kWorld)
			self.mPoints = OpenMaya.MPointArray(mPoints)

			tmp1, uvIdsFace = mFnMesh.getAssignedUVs(self.uvName)
			tmp2, vertexIdsFace = mFnMesh.getVertices()
			u, v = mFnMesh.getUVs(self.uvName)
			uvs = [0] * len(u)
			for i in range(len(uvIdsFace)):
				uvIdFace = uvIdsFace[i]
				uvs[vertexIdsFace[i]] = [u[uvIdFace], v[uvIdFace]]

			if self.matrixIs.X:
				diffX = self.matrixMax.X - self.matrixMin.X
				for i in range(len(mPoints)):
					u = int((uvs[i][0] % 1.0) * imageWidthM)
					v = int((uvs[i][1] % 1.0) * imageHeightM)
					mPoints[i].x += ((ord(imageBits[(u + v * imageWidth) * 4 + self.matrixCha.X]) * diffX) / 255.0) + self.matrixMin.X
			if self.matrixIs.Y:
				diffY = self.matrixMax.Y - self.matrixMin.Y
				for i in range(len(mPoints)):
					u = int((uvs[i][0] % 1.0) * imageWidthM)
					v = int((uvs[i][1] % 1.0) * imageHeightM)
					mPoints[i].y += ((ord(imageBits[(u + v * imageWidth) * 4 + self.matrixCha.Y]) * diffY) / 255.0) + self.matrixMin.Y
			if self.matrixIs.Z:
				diffZ = self.matrixMax.Z - self.matrixMin.Z
				for i in range(len(mPoints)):
					u = int((uvs[i][0] % 1.0) * imageWidthM)
					v = int((uvs[i][1] % 1.0) * imageHeightM)
					mPoints[i].z += ((ord(imageBits[(u + v * imageWidth) * 4 + self.matrixCha.Z]) * diffZ) / 255.0) + self.matrixMin.Z
			if self.matrixIs.N:
				diffN = self.matrixMax.N - self.matrixMin.N
				mNormals = mFnMesh.getVertexNormals(True, OpenMaya.MSpace.kWorld)
				for i in range(len(mPoints)):
					u = int((uvs[i][0] % 1.0) * imageWidthM)
					v = int((uvs[i][1] % 1.0) * imageHeightM)
					mPoints[i].x += mNormals[i].x * (((ord(imageBits[(u + v * imageWidth) * 4 + self.matrixCha.N]) * diffN) / 255.0) + self.matrixMin.N)
					mPoints[i].y += mNormals[i].y * (((ord(imageBits[(u + v * imageWidth) * 4 + self.matrixCha.N]) * diffN) / 255.0) + self.matrixMin.N)
					mPoints[i].z += mNormals[i].z * (((ord(imageBits[(u + v * imageWidth) * 4 + self.matrixCha.N]) * diffN) / 255.0) + self.matrixMin.N)
			mFnMesh.setPoints(mPoints, OpenMaya.MSpace.kWorld)
			mFnMesh.updateSurface()
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(stateWithoutFlush=True)

	def undoIt(self):
		maya_cmds.undoInfo(stateWithoutFlush=False)
		try:
			mFnMesh = OpenMaya.MFnMesh(OpenMaya.MGlobal.getSelectionListByName(self.shape).getDagPath(0))
			mFnMesh.setPoints(self.mPoints, OpenMaya.MSpace.kWorld)
			mFnMesh.updateSurface()
		except Exception as e:
			print(str(e), file=stderr)
		maya_cmds.undoInfo(stateWithoutFlush=True)