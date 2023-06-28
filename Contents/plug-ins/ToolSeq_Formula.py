from sys import stderr

from maya import cmds as maya_cmds
from maya.api import OpenMaya

maya_useNewAPI = True

def initializePlugin(mObject):
	OpenMaya.MFnPlugin(mObject).registerCommand(ToolSeq_Formula_Apply.pluginName, ToolSeq_Formula_Apply.cmdCreator, ToolSeq_Formula_Apply.syntaxNew)

def uninitializePlugin(mObject):
	OpenMaya.MFnPlugin(mObject).deregisterCommand(ToolSeq_Formula_Apply.pluginName)

def ToolSeq_Formula_xyz(x, y, z):
	return x, y, z

def ToolSeq_Formula_xyzn(x, y, z, xn, yn, zn):
	return x, y, z

class ToolSeq_Formula_Apply(OpenMaya.MPxCommand):
	pluginName = 'ToolSeq_Formula_Apply'

	shapeFlag = '-s'
	shapeFlagLong = '-shape'

	preFormulaFlag = '-pf'
	preFormulaFlagLong = '-preFormula'

	formulaFlag = '-f'
	formulaFlagLong = '-formula'

	isSecureFlag = '-iS'
	isSecureFlagLong = '-isSecure'
	isVarNFlag = '-iN'
	isVarNFlagLong = '-isVarN'

	def __init__(self):
		OpenMaya.MPxCommand.__init__(self)

		self.shape = None

		self.preFormula = None
		self.formula = None

		self.isSecure = None
		self.isVarN = None

		self.mPoints = None

	@staticmethod
	def cmdCreator():
		return ToolSeq_Formula_Apply()

	@staticmethod
	def syntaxNew():
		syntax = OpenMaya.MSyntax()

		syntax.addFlag(ToolSeq_Formula_Apply.shapeFlag, ToolSeq_Formula_Apply.shapeFlagLong, OpenMaya.MSyntax.kString)

		syntax.addFlag(ToolSeq_Formula_Apply.preFormulaFlag, ToolSeq_Formula_Apply.preFormulaFlagLong, OpenMaya.MSyntax.kString)
		syntax.addFlag(ToolSeq_Formula_Apply.formulaFlag, ToolSeq_Formula_Apply.formulaFlagLong, OpenMaya.MSyntax.kString)

		syntax.addFlag(ToolSeq_Formula_Apply.isSecureFlag, ToolSeq_Formula_Apply.isSecureFlagLong, OpenMaya.MSyntax.kBoolean)
		syntax.addFlag(ToolSeq_Formula_Apply.isVarNFlag, ToolSeq_Formula_Apply.isVarNFlagLong, OpenMaya.MSyntax.kBoolean)

		return syntax

	def isUndoable(self):
		return True

	def doIt(self, args):
		mArgParser = OpenMaya.MArgParser(self.syntax(), args)

		self.shape = mArgParser.flagArgumentString(self.shapeFlag, 0)

		self.preFormula = mArgParser.flagArgumentString(self.preFormulaFlag, 0)
		self.formula = mArgParser.flagArgumentString(self.formulaFlag, 0)

		self.isSecure = mArgParser.flagArgumentBool(self.isSecureFlag, 0)
		self.isVarN = mArgParser.flagArgumentBool(self.isVarNFlag, 0)

		self.redoIt()

	def redoIt(self):
		maya_cmds.undoInfo(stateWithoutFlush=False)
		try:
			mFnMesh = OpenMaya.MFnMesh(OpenMaya.MGlobal.getSelectionListByName(self.shape).getDagPath(0))
			mPoints = mFnMesh.getPoints(OpenMaya.MSpace.kWorld)
			self.mPoints = OpenMaya.MPointArray(mPoints)

			exec (self.preFormula, globals())
			formula = self.formula
			if self.isSecure:
				formula = 'try:\n\t%s\nexcept:\n\tpass' % formula.replace('\n', '\n\t')

			if self.isVarN:
				exec ('def ToolSeq_Formula_xyzn(x, y, z, xn, yn, zn):\n\t%s\n\treturn x, y, z' % formula.replace('\n', '\n\t'))
				mNormals = mFnMesh.getVertexNormals(True, OpenMaya.MSpace.kWorld)
				for i in range(len(mPoints)):
					mPoints[i].x, mPoints[i].y, mPoints[i].z = ToolSeq_Formula_xyzn(mPoints[i].x, mPoints[i].y, mPoints[i].z, mNormals[i].x, mNormals[i].y, mNormals[i].z)
			else:
				exec ('def ToolSeq_Formula_xyz(x, y, z):\n\t%s\n\treturn x, y, z' % formula.replace('\n', '\n\t'))
				for i in range(len(mPoints)):
					mPoints[i].x, mPoints[i].y, mPoints[i].z = ToolSeq_Formula_xyz(mPoints[i].x, mPoints[i].y, mPoints[i].z)
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