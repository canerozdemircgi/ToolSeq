from maya import cmds as maya_cmds

class ToolSeq_ItemHud(object):

	def __init__(self):
		isOpen = False
		if maya_cmds.headsUpDisplay('ToolSeq_ItemHud_Shape', exists=True):
			isOpen = True
			maya_cmds.headsUpDisplay('ToolSeq_ItemHud_Shape', remove=True)
		if maya_cmds.headsUpDisplay('ToolSeq_ItemHud_Transform', exists=True):
			isOpen = True
			maya_cmds.headsUpDisplay('ToolSeq_ItemHud_Transform', remove=True)
		if maya_cmds.headsUpDisplay('ToolSeq_ItemHud_Selection', exists=True):
			isOpen = True
			maya_cmds.headsUpDisplay('ToolSeq_ItemHud_Selection', remove=True)
		if isOpen:
			return

		maya_cmds.headsUpDisplay(
			'ToolSeq_ItemHud_Shape',
			label='Shapes:',
			labelWidth=50,
			dataWidth=65,
			dataAlignment='right',
			section=0,
			block=maya_cmds.headsUpDisplay(nextFreeBlock=0) + 1,
			decimalPrecision=1,
			event='SelectionChanged',
			command=ToolSeq_ItemHud.Return_Shape
		)

		maya_cmds.headsUpDisplay(
			'ToolSeq_ItemHud_Transform',
			label='Transforms:',
			labelWidth=50,
			dataWidth=65,
			dataAlignment='right',
			section=0,
			block=maya_cmds.headsUpDisplay(nextFreeBlock=0) + 2,
			decimalPrecision=1,
			event='SelectionChanged',
			command=ToolSeq_ItemHud.Return_Transform
		)

		maya_cmds.headsUpDisplay(
			'ToolSeq_ItemHud_Selection',
			label='Selections:',
			labelWidth=50,
			dataWidth=65,
			dataAlignment='right',
			section=0,
			block=maya_cmds.headsUpDisplay(nextFreeBlock=0) + 3,
			decimalPrecision=1,
			event='SelectionChanged',
			command=ToolSeq_ItemHud.Return_Selection
		)

	@staticmethod
	def Return_Shape():
		shapesLen = len(maya_cmds.ls(dag=True, objectsOnly=True, shapes=True))
		shapesSelectedLen = len(maya_cmds.ls(selection=True, dag=True, objectsOnly=True, shapes=True))
		return [shapesLen, shapesSelectedLen]

	@staticmethod
	def Return_Transform():
		transformsLen = len(maya_cmds.ls(transforms=True))
		transformsSelectedLen = len(maya_cmds.ls(selection=True, transforms=True))
		return [transformsLen, transformsSelectedLen]

	@staticmethod
	def Return_Selection():
		return len(maya_cmds.ls(selection=True, flatten=True))