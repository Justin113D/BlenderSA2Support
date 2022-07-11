from struct import error
import os, os.path

import bpy
import mathutils
import math
import queue
from typing import List, Dict, Tuple
from . import fileHelper, enums

DO = False  # Debug Out

def get_path():
    return os.path.dirname(os.path.realpath(__file__))

def get_name():
    return os.path.basename(get_path())

def get_prefs():
    return bpy.context.preferences.addons[get_name()].preferences

def center(p1: float, p2: float) -> float:
	"""Returns the mid point between two numbers"""
	return (p1 + p2) / 2.0

def hex4(number: int) -> str:
	return '{:08x}'.format(number)

def RadToBAMS(v: float, asInt=False) -> int:
	if round(v, 4) == 0:
		return 0
	val = int(round((math.degrees(v) / 360.0) * 0x10000))
	if not asInt:
		if val > 0xFFFF:
			val &= 0xFFFF

		while val < 0:
			val += 0x10000

	else:
		if val > 0xFFFFFFFF:
			val &= 0xFFFFFFFF

		while val < 0:
			val += 0x100000000

	return val

def BAMSToRad(v: int, shortRot=False) -> float:
	if not shortRot and v & 0x80000000:
		v -= 0x100000000
	elif shortRot:
		v &= 0xFFFF
	return math.radians(v / (0x10000 / 360.0))

def getDistinctwID(items: list):

	distinct = list()
	IDs = [0] * len(items)

	for i, o in enumerate(items):
		found = None
		for j, d in enumerate(distinct):
			if o == d:
				found = j
				break
		if found is None:
			distinct.append(o)
			IDs[i] = len(distinct) - 1
		else:
			IDs[i] = found

	return distinct, IDs

class ExportError(Exception):

	def __init__(self, message):
		super().__init__(message)

class ColorARGB:
	"""4 Channel Color (ARGB)

	takes values from 0.0 - 1.0 as input and converts them to 0 - 255
	"""

	a: int
	r: int
	g: int
	b: int

	def __init__(self, c=(1, 1, 1, 1)):
		self.a = round(c[3] * 255)
		self.r = round(c[0] * 255)
		self.g = round(c[1] * 255)
		self.b = round(c[2] * 255)

	@classmethod
	def fromRGBA(cls, value: int):
		col = ColorARGB()

		col.r = (value >> 24) & 0xFF
		col.g = (value >> 16) & 0xFF
		col.b = (value >> 8) & 0xFF
		col.a = value & 0xFF
		return col

	def writeRGBA(self, fileW):
		"""writes data to file"""
		fileW.wByte(self.a)
		fileW.wByte(self.b)
		fileW.wByte(self.g)
		fileW.wByte(self.r)

	@classmethod
	def fromARGB(cls, value: int):
		col = ColorARGB()
		col.a = (value >> 24) & 0xFF
		col.r = (value >> 16) & 0xFF
		col.g = (value >> 8) & 0xFF
		col.b = value & 0xFF
		return col

	def writeARGB(self, fileW):
		"""writes data to file"""
		fileW.wByte(self.b)
		fileW.wByte(self.g)
		fileW.wByte(self.r)
		fileW.wByte(self.a)

	def writeRGB(self, fileW):
		"""writes data to file"""
		fileW.wByte(self.b)
		fileW.wByte(self.g)
		fileW.wByte(self.r)

	def toBlenderTuple(self):
		return (self.r / 255.0, self.g / 255.0, self.b / 255.0, self.a / 255.0)

	def isWhite(self):
		return self.a == 255 \
			and self.r == 255 \
			and self.g == 255 \
			and self.b == 255

	def __eq__(self, other):
		return self.a == other.a \
			and self.r == other.r \
			and self.g == other.g \
			and self.b == other.b

	def __str__(self):
		return f"({self.a},{self.r},{self.g},{self.b})"

class UV:
	"""A single texture coordinate

	Converts from 0.0 - 1.0 range to 0 - 255 range """

	x: int
	y: int

	def __init__(self, uv=(0.0, 0.0)):
		self.x = max(-32767, min(32767, round(uv[0] * 256)))
		self.y = max(-32767, min(32767, round((1-uv[1]) * 256)))

	def __eq__(self, other):
		return self.x == other.x and self.y == other.y

	def getBlenderUV(self):
		return (self.x / 256.0, 1-(self.y / 256.0))

	def write(self, fileW: fileHelper.FileWriter):
		"""Writes data to file"""
		fileW.wShort(self.x)
		fileW.wShort(self.y)

class Vector3(mathutils.Vector):
	"""Point in 3D Space"""

	def length(self):
		"""returns length of the vector"""
		return (self.x**2 + self.y**2 + self.z**2)**(0.5)

	def write(self, fileW):
		"""Writes data to file"""
		fileW.wFloat(self.x)
		fileW.wFloat(self.y)
		fileW.wFloat(self.z)

	def __str__(self):
		return f"({round(self.x, 3)},{round(self.y, 3)},{round(self.z, 3)})"

class BAMSRotation:
	"""XYZ Rotation used for the adventure games"""

	x: int
	y: int
	z: int

	def __init__(self, val, asInt=False):
		self.x = RadToBAMS(val[0], asInt=asInt)
		self.y = RadToBAMS(val[1], asInt=asInt)
		self.z = RadToBAMS(val[2], asInt=asInt)

	def toQuaternion(self) -> mathutils.Quaternion:
		return mathutils.Euler((
				BAMSToRad(self.x),
				BAMSToRad(self.y),
				BAMSToRad(self.z)
			)).to_quaternion()

	def write(self, fileW: fileHelper.FileWriter):
		"""Writes data to file"""
		fileW.wUInt(self.x)
		fileW.wUInt(self.y)
		fileW.wUInt(self.z)

	def __str__(self):
		return (f"({round(BAMSToRad(self.x), 3)},"
				f"{round(BAMSToRad(self.y), 3)},"
				f"{round(BAMSToRad(self.z), 3)})")

class BoundingBox:
	"""Used to calculate the bounding sphere which the game uses"""

	boundCenter: Vector3
	radius: float

	def __init__(self, vertices):
		"""Creates a bounding sphere from a set of vertices"""

		if vertices is None:
			self.radius = 0
			self.boundCenter = Vector3((0, 0, 0))
			return

		x = 0
		xn = 0
		y = 0
		yn = 0
		z = 0
		zn = 0

		for v in vertices:
			if x < v.co.x:
				x = v.co.x
			elif xn > v.co.x:
				xn = v.co.x

			if y < v.co.y:
				y = v.co.y
			elif yn > v.co.y:
				yn = v.co.y

			if z < v.co.z:
				z = v.co.z
			elif zn > v.co.z:
				zn = v.co.z

		cx = center(x, xn)
		cy = center(y, yn)
		cz = center(z, zn)

		distance = 0
		for v in vertices:
			tDist = Vector3((cx - v.co.x,  cy - v.co.y, cz - v.co.z)).length()
			if tDist > distance:
				distance = tDist

		self.boundCenter = Vector3((cx, cy, cz))
		self.radius = distance

	def adjust(self, matrix: mathutils.Matrix):
		self.boundCenter = matrix @ self.boundCenter
		self.radius *= matrix.to_scale()[0]

	def write(self, fileW):
		self.boundCenter.write(fileW)
		fileW.wFloat(self.radius)

	def __str__(self):
		return str(self.boundCenter) + " - " + str(self.radius)

class ModelData:
	"""A class that holds all necessary data to export an Object/COL"""

	name: str

	# used for exporting the meshes in correct formats
	origObject: bpy.types.Object

	# the triangulated mesh
	processedMesh: bpy.types.Mesh

	children: list
	child: "ModelData" = None
	sibling: "ModelData" = None
	parent: "ModelData" = None
	hierarchyDepth: int
	partOfArmature: bool

	worldMatrix: mathutils.Matrix
	position: Vector3
	rotation: BAMSRotation
	scale: Vector3
	bounds: BoundingBox

	objFlags: dict
	saProps: dict

	unknown1: int  # sa1 COL
	unknown2: int  # both COL

	meshPtr: int  # set after writing meshes
	objectPtr: int  # set after writing model address

	def __init__(self,
				 bObject: bpy.types.Object,
				 parent: "ModelData",
				 hierarchyDepth: int,
				 name: str,
				 global_matrix: mathutils.Matrix,
				 collision: bool = False,
				 visible: bool = False):

		if global_matrix is None:
			return

		self.name = name
		self.hierarchyDepth = hierarchyDepth
		if parent is not None:
			self.partOfArmature = isinstance(parent, Armature) \
								  or parent.partOfArmature
		else:
			self.partOfArmature = False

		if bObject is not None and bObject.type == 'MESH':
			# get the blender bounds
			self.bounds = BoundingBox(None)

			self.saProps = bObject.saSettings.toDictionary()
			self.saProps["solid"] = collision
			self.saProps["isVisible"] = visible
		else:
			self.bounds = BoundingBox(None)
			self.saProps = None

		self.origObject = bObject
		self.objFlags = bObject.saObjflags.toDictionary()

		if bObject is None:
			self.worldMatrix = mathutils.Matrix.Identity(4)
		else:
			self.worldMatrix = bObject.matrix_world

		self.children = list()
		self.parent = parent
		if parent is not None:
			self.parent.children.append(self)
			matrix = parent.worldMatrix.inverted() @ self.worldMatrix
		else:
			matrix = self.worldMatrix

		# settings space data

		obj_mat: mathutils.Matrix = global_matrix @ matrix
		scale = matrix.to_scale()
		rot: mathutils.Euler = matrix.to_euler('XZY')
		rot = global_matrix @ mathutils.Vector((rot.x, rot.y, rot.z))

		self.position = Vector3(obj_mat.to_translation())
		self.rotation = BAMSRotation(rot, asInt=True)
		self.scale = Vector3((scale.x, scale.z, scale.y))

		# settings the unknowns
		self.unknown1 = 0
		self.unknown2 = 0

		self.meshPtr = None

	@classmethod
	def updateMeshes(cls, objList: list, meshList: list):

		for o in objList:
			o.processedMesh = None
			if o.origObject is not None and o.origObject.type == 'MESH':
				for m in meshList:
					if m.name == o.origObject.data.name:
						o.processedMesh = m
						break

	@classmethod
	def updateMeshPointer(cls,
						  objList: list,
						  meshDict: dict,
						  cMeshDict: list = None):
		"""Updates the mesh pointer of a ModelData list utilizing a meshDict"""
		for o in objList:
			if o.processedMesh is not None:
				if cMeshDict is not None and o.saProps["solid"]:
					o.meshPtr, bounds = cMeshDict[o.processedMesh.name]
				else:
					o.meshPtr, bounds = meshDict[o.processedMesh.name]
			else:
				o.meshPtr = 0
				continue
			if o.meshPtr is not None:
				# now its time to rotate the point
				# around the center of the object

				# get matrix from rotation
				rotMtx = o.rotation.toQuaternion().to_matrix().to_4x4()

				o.bounds.boundCenter = rotMtx @ bounds.boundCenter
				o.bounds.boundCenter += o.position

				# getting the biggest scale

				s = o.scale[0]
				if o.scale[1] > s:
					s = o.scale[1]
				if o.scale[2] > s:
					s = o.scale[2]
				o.bounds.radius = s * bounds.radius * 1.01

	def getObjectFlags(self) -> enums.ObjectFlags:
		"""Calculates the Objectflags"""
		from .enums import ObjectFlags
		flags = ObjectFlags.null
		if self.objFlags is None:
			return flags
		p = self.objFlags

		if p["ignorePosition"]:
			flags |= ObjectFlags.NoPosition
		if p["ignoreRotation"]:
			flags |= ObjectFlags.NoRotate
		if p["ignoreScale"]:
			flags |= ObjectFlags.NoScale
		if p["rotateZYX"]:
			flags |= ObjectFlags.RotateZYX
		if p["skipDraw"]:
			flags |= ObjectFlags.NoDisplay
		if p["skipChildren"]:
			flags |= ObjectFlags.NoChildren
		if p["flagAnimate"]:
			flags |= ObjectFlags.NoAnimate
		if p["flagMorph"]:
			flags |= ObjectFlags.NoMorph

		# Checks for NONE object type or if no children for an object to auto-set those flags in the event the user did not set them.
		if (flags & ObjectFlags.NoDisplay) or (flags & ObjectFlags.NoChildren):
			if self.origObject.type == 'NONE':
				flags |= ObjectFlags.NoDisplay
			if len(self.origObject.children) == 0:
				flags |= ObjectFlags.NoChildren

		return flags

	def getSA1SurfaceFlags(self) -> enums.SA1SurfaceFlags:
		"""Calculates SA1 COL flags"""
		from .enums import SA1SurfaceFlags
		flags = SA1SurfaceFlags.null
		if self.saProps is None:
			return flags
		p = self.saProps

		if p["solid"]:
			flags |= SA1SurfaceFlags.Solid
		if p["sa1_water"]:
			flags |= SA1SurfaceFlags.Water
		if p["sa1_noFriction"]:
			flags |= SA1SurfaceFlags.NoFriction
		if p["sa1_noAcceleration"]:
			flags |= SA1SurfaceFlags.NoAcceleration
		if p["sa1_lowAcceleration"]:
			flags |= SA1SurfaceFlags.LowAcceleration
		if p["sa1_cannotLand"]:
			flags |= SA1SurfaceFlags.CannotLand
		if p["sa1_increasedAcceleration"]:
			flags |= SA1SurfaceFlags.IncreasedAcceleration
		if p["sa1_diggable"]:
			flags |= SA1SurfaceFlags.Diggable
		if p["sa1_waterfall"]:
			flags |= SA1SurfaceFlags.Waterfall
		if p["sa1_unclimbable"]:
			flags |= SA1SurfaceFlags.Unclimbable
		if p["sa1_chaos0Land"]:
			flags |= SA1SurfaceFlags.Chaos0Land
		if p["sa1_stairs"]:
			flags |= SA1SurfaceFlags.Stairs
		if p["sa1_hurt"]:
			flags |= SA1SurfaceFlags.Hurt
		if p["sa1_lowDepth"]:
			flags |= SA1SurfaceFlags.LowDepth
		if p["sa1_footprints"]:
			flags |= SA1SurfaceFlags.Footprints
		if p["sa1_accelerate"]:
			flags |= SA1SurfaceFlags.Accelerate
		if p["sa1_colWater"]:
			flags |= SA1SurfaceFlags.WaterCollision
		if p["sa1_rotByGravity"]:
			flags |= SA1SurfaceFlags.RotateByGravity
		if p["sa1_noZWrite"]:
			flags |= SA1SurfaceFlags.NoZWrite
		if p["sa1_drawByMesh"]:
			flags |= SA1SurfaceFlags.DrawByMesh
		if p["sa1_enableManipulation"]:
			flags |= SA1SurfaceFlags.EnableManipulation
		if p["sa1_dynCollision"]:
			flags |= SA1SurfaceFlags.DynamicCollision
		if p["sa1_useRotation"]:
			flags |= SA1SurfaceFlags.UseRotation
		if p["isVisible"]:
			flags |= SA1SurfaceFlags.Visible

		return flags

	def getSA2SurfaceFlags(self) -> enums.SA2SurfaceFlags:
		"""Calculates SA1 COL flags"""
		from .enums import SA2SurfaceFlags
		flags = SA2SurfaceFlags.null
		if self.saProps is None:
			return flags
		p = self.saProps

		if p["solid"]:
			flags |= SA2SurfaceFlags.Solid
		if p["sa2_water"]:
			flags |= SA2SurfaceFlags.Water
		if p["sa2_stairs"]:
			flags |= SA2SurfaceFlags.Stairs
		if p["sa2_diggable"]:
			flags |= SA2SurfaceFlags.Diggable
		if p["sa2_unclimbable"]:
			flags |= SA2SurfaceFlags.Unclimbable
		if p["sa2_hurt"]:
			flags |= SA2SurfaceFlags.Hurt
		if p["sa2_footprints"]:
			flags |= SA2SurfaceFlags.Footprints
		if p["sa2_cannotLand"]:
			flags |= SA2SurfaceFlags.CannotLand
		if p["sa2_water2"]:
			flags |= SA2SurfaceFlags.Water2
		if p["sa2_unknown24"]:
			flags |= SA2SurfaceFlags.Unknown24
		if p["sa2_unknown29"]:
			flags |= SA2SurfaceFlags.Unknown29
		if p["sa2_unknown30"]:
			flags |= SA2SurfaceFlags.Unknown30
		if p["isVisible"]:
			flags |= SA2SurfaceFlags.Visible
		if p["sa2_noShadows"]:
			flags |= SA2SurfaceFlags.NoShadows
		if p["sa2_noFog"]:
			flags |= SA2SurfaceFlags.noFog

		return flags

	@classmethod
	def writeObjectList(cls,
						objects: list,
						fileW: fileHelper.FileWriter,
						labels: dict,
						lvl: bool = False):

		for o in reversed(objects):
			o.writeObject(fileW, labels, lvl)

		return objects[0].objectPtr

	def writeObject(self,
					fileW: fileHelper.FileWriter,
					labels: dict,
					lvl: bool = False):
		"""Writes object data"""
		name = self.name
		numberCount = 0
		while name[numberCount].isdigit():
			numberCount += 1

		if name[numberCount] == '_':
			name = name[numberCount + 1:]
		else:
			name = name[numberCount:]

		self.objectPtr = fileW.tell()
		labels[self.objectPtr] = name

		fileW.wUInt(self.getObjectFlags().value)
		fileW.wUInt(self.meshPtr)
		self.position.write(fileW)
		self.rotation.write(fileW)
		self.scale.write(fileW)
		fileW.wUInt(0 if self.child is None or lvl
					else self.child.objectPtr)
		fileW.wUInt(0 if self.sibling is None or lvl
					else self.sibling.objectPtr)

	def writeCOL(self, fileW: fileHelper.FileWriter, labels: dict, SA2: bool):
		"""writes COL data"""
		# a COL always needs a mesh
		if self.meshPtr == 0:
			return

		# labels[fileW.tell()] = self.name

		if SA2:
			self.bounds.write(fileW)
			fileW.wUInt(self.objectPtr)
			fileW.wUInt(self.unknown2)
			fileW.wUInt(int("0x" + self.saProps["blockbit"], 0))
			fileW.wUInt(self.getSA2SurfaceFlags().value
						| int("0x" + self.saProps["userFlags"], 0))
		else:
			self.bounds.write(fileW)
			fileW.wUInt(self.unknown1)
			fileW.wUInt(self.unknown2)
			fileW.wUInt(self.objectPtr)
			fileW.wUInt(int("0x" + self.saProps["blockbit"], 0))
			fileW.wUInt(self.getSA1SurfaceFlags().value
						| int("0x" + self.saProps["userFlags"], 0))

class ArmatureMesh:
	model: ModelData
	indexBufferOffset: int
	weightMap: Dict[str, Tuple[int, enums.WeightStatus]]

	# a weightindex of -1 indicates to write the entire mesh
	# and an index of -2 means to write only unweighted vertices

	def __init__(self,
				 model: ModelData,
				 indexBufferOffset: int,
				 weightMap: Dict[str, Tuple[int, enums.WeightStatus]]):
		self.model = model
		self.indexBufferOffset = indexBufferOffset
		self.weightMap = weightMap

class Bone:

	name: str
	hierarchyDepth: int
	objFlags: dict

	matrix_world: mathutils.Matrix  # in the world
	matrix_local: mathutils.Matrix  # relative to parent bone

	parentBone: "Bone" = None
	children: List["Bone"]

	child = None
	sibling = None

	position: Vector3
	rotation: BAMSRotation
	scale: Vector3

	meshPtr: int  # set after writing meshes
	objectPtr: int  # set after writing model address

	def __init__(self,
				 name: str,
				 hierarchyDepth,
				 armatureMatrix: mathutils.Matrix,
				 localMatrix: mathutils.Matrix,
				 exportMatrix: mathutils.Matrix,
				 parentBone,
				 objFlags: dict):
		self.name = name
		self.hierarchyDepth = hierarchyDepth

		self.matrix_world = armatureMatrix @ localMatrix
		if parentBone is not None:
			self.matrix_local = parentBone.matrix_world.inverted() \
								@ self.matrix_world
			matrix = self.matrix_local
		else:  # only the root can cause this
			self.matrix_local = self.matrix_world
			matrix = armatureMatrix

		posMatrix = exportMatrix @ matrix
		self.position = Vector3(posMatrix.to_translation())
		self.scale = Vector3((1, 1, 1))

		rot: mathutils.Euler = matrix.to_euler('XZY')
		self.rotation = BAMSRotation(
			exportMatrix @ mathutils.Vector((rot.x, rot.y, rot.z)))

		self.parentBone = parentBone
		self.children = list()

		if parentBone is not None:
			parentBone.children.append(self)

		self.objFlags = objFlags

	@classmethod
	def getBones(cls,
				 bBone: bpy.types.Bone,
				 parent: "Bone",
				 hierarchyDepth: int,
				 export_matrix: mathutils.Matrix,
				 armatureMatrix: mathutils.Matrix,
				 result: List[ModelData]):

		bone = Bone(bBone.name,
					hierarchyDepth,
					armatureMatrix,
					bBone.matrix_local,
					export_matrix, parent,
					bBone.saObjflags.toDictionary())
		result.append(bone)
		lastSibling = None

		for b in bBone.children:
			child = Bone.getBones(b,
								  bone,
								  hierarchyDepth + 1,
								  export_matrix,
								  armatureMatrix,
								  result)
			if lastSibling is not None:
				lastSibling.sibling = child
			lastSibling = child

		# update sibling relationship
		if len(bone.children) > 0:
			bone.child = bone.children[0]

		return bone

	def write(self, fileW: fileHelper.FileWriter, labels: dict):
		"""Writes bone data in form of object data"""
		name = self.name
		numberCount = 0
		while name[numberCount].isdigit():
			numberCount += 1

		if name[numberCount] == '_':
			name = name[numberCount + 1:]
		else:
			name = name[numberCount:]

		self.objectPtr = fileW.tell()
		labels[self.objectPtr] = name

		p = self.objFlags
		objFlags = enums.ObjectFlags.null
		if p["ignorePosition"]:
			objFlags |= enums.ObjectFlags.NoPosition
		if p["ignoreRotation"]:
			objFlags |= enums.ObjectFlags.NoRotate
		if p["ignoreScale"]:
			objFlags |= enums.ObjectFlags.NoScale
		if p["rotateZYX"]:
			objFlags |= enums.ObjectFlags.RotateZYX
		if p["skipDraw"]:
			objFlags |= enums.ObjectFlags.NoDisplay
		if p["skipChildren"]:
			objFlags |= enums.ObjectFlags.NoChildren
		if p["flagAnimate"]:
			objFlags |= enums.ObjectFlags.NoAnimate
		if p["flagMorph"]:
			objFlags |= enums.ObjectFlags.NoMorph

		# Checking if NoDisplay or NoChildren is set and auto-setting them if not to prevent potential error in-game.
		if (objFlags & enums.ObjectFlags.NoDisplay) or (objFlags & enums.ObjectFlags.NoChildren):
			if self.meshPtr == 0:
				objFlags |= enums.ObjectFlags.NoDisplay
			if len(self.children) == 0:
				objFlags |= enums.ObjectFlags.NoChildren

		fileW.wUInt(objFlags.value)
		fileW.wUInt(self.meshPtr)
		self.position.write(fileW)
		self.rotation.write(fileW)
		self.scale.write(fileW)
		fileW.wUInt(0 if self.child is None else self.child.objectPtr)
		fileW.wUInt(0 if self.sibling is None else self.sibling.objectPtr)

class Armature(ModelData):

	def writeArmature(self,
					  fileW: fileHelper.FileWriter,
					  export_matrix: mathutils.Matrix,
					  materials: List[bpy.types.Material],
					  labels: dict):
		armature = self.origObject.data
		bones: List[Bone] = list()

		# first we need to evaluate all bone data (the fun part)
		# lets start with the root bone.
		# thats basically representing the armature object
		root = Bone(self.name,
					0,
					self.origObject.matrix_world,
					mathutils.Matrix.Identity(4),
					export_matrix, None,
					self.objFlags)
		bones.append(root)

		# starting with the parentless bones
		lastSibling = None
		for b in armature.bones:
			if b.parent is None:
				bone = Bone.getBones(
					b,
					root,
					1,
					export_matrix,
					self.origObject.matrix_world,
					bones)

				if lastSibling is not None:
					lastSibling.sibling = bone
				lastSibling = bone

		if len(root.children) > 0:
			root.child = root.children[0]

		if DO:
			print(" == Bone Hierarchy == \n")
			for b in bones:
				marker = " "
				for r in range(b.hierarchyDepth):
					marker += "- "
				if len(marker) > 1:
					print(marker, b.name)
				else:
					print("", b.name)
			print(" - - - -\n")

		# now, time to get the mesh data
		# first we need to get all objects that the armature modifies
		objects: List[ModelData] = list()
		objQueue = queue.Queue()

		for o in self.children:
			objQueue.put(o)

		while not objQueue.empty():
			o = objQueue.get()
			objects.append(o)
			for c in o.children:
				objQueue.put(c)

		# now we have all objects that get modified by the armature
		# lets get the meshes
		meshes = list()
		for o in objects:
			if o.processedMesh not in meshes:
				meshes.append(o.processedMesh)

		# giving each mesh an index buffer offset
		meshesWOffset = dict()
		currentOffset = 0
		for m in meshes:
			meshesWOffset[m] = currentOffset
			currentOffset += len(m.vertices)

		# ok lemme write some notes down:
		# there are 3 types of objects that the armature modifies:
		# 1. Objects with weights, which are parented to the armature
		# 2. Objects parented to bones (also no weights)
		# 3. Objects without weights. may be parented to
		# armature or object that is parented to armature

		armatureMeshes: List[ArmatureMesh] = list()
		for o in objects:
			mesh = o.processedMesh
			if mesh is None:
				continue

			case1 = False
			for m in o.origObject.modifiers:
				if isinstance(m, bpy.types.ArmatureModifier) \
						and m.object is self.origObject:
					# yeah then its case 1, otherwise no
					case1 = True
					break

			weightMap = dict()
			obj = o.origObject

			if case1:
				usedBoneGroups: Dict[Bone, bpy.types.VertexGroup] = dict()

				for b in bones:
					for g in obj.vertex_groups:
						if g.name == b.name:
							usedBoneGroups[b] = g
							break

				usedGroups = [g.index for g in usedBoneGroups.values()]

				setStart = False
				last = None
				# checking valid weight groups
				validGroups = list()
				emptyVertsFound = False
				for v in mesh.vertices:
					found = False
					for g in v.groups:
						if g.group in usedGroups and g.weight > 0:
							found = True
							if g.group not in validGroups:
								validGroups.append(g.group)
					if not found:
						emptyVertsFound = True
				usedGroups = validGroups

				validBoneGroups: Dict[Bone, bpy.types.VertexGroup] = dict()
				for b, g in usedBoneGroups.items():
					if g.index in usedGroups:
						validBoneGroups[b] = g
				usedBoneGroups = validBoneGroups

				if emptyVertsFound:
					weightMap[root.name] = [-2, enums.WeightStatus.Start]
					setStart = True
					last = root.name

				for b, g in usedBoneGroups.items():
					weightMap[b.name] = [g.index,
										 enums.WeightStatus.Middle if setStart
										 else enums.WeightStatus.Start]
					setStart = True
					last = b.name

				if len(weightMap) == 0:
					weightMap[root.name] = [-1, enums.WeightStatus.Start]
				elif len(weightMap) == 1:
					weightMap[list(weightMap.keys())[0]] = \
						[-1, enums.WeightStatus.Start]
				elif len(weightMap) > 1:
					weightMap[last] = \
						[weightMap[last][0],
						 enums.WeightStatus.End]

			elif len(o.origObject.parent_bone) > 0:
				weightMap[o.origObject.parent_bone] = \
					[-1, enums.WeightStatus.Start]
			else:
				weightMap[root.name] = [-1, enums.WeightStatus.Start]

			armatureMeshes.append(
				ArmatureMesh(o,
							 meshesWOffset[mesh],
							 weightMap))
		if DO:
			for a in armatureMeshes:
				print("  " + a.model.name, a.indexBufferOffset)
				for k in a.weightMap.keys():
					print("    " + k, a.weightMap[k])
			print("")

		boneMap: Dict[str, mathutils.Matrix] = dict()
		for b in bones:
			boneMap[b.name] = b.matrix_world

		# converting mesh data
		from . import format_CHUNK
		boneAttaches = format_CHUNK.fromWeightData(boneMap,
												   armatureMeshes,
												   export_matrix,
												   materials)

		# writing mesh data
		for b in bones:
			b.meshPtr = 0
			if b.name not in boneAttaches:
				continue
			mesh = boneAttaches[b.name]
			b.meshPtr = mesh.write(fileW, labels)

		if DO:
			print("\n - - - -")

		# writing object data
		for b in reversed(bones):
			b.write(fileW, labels)

		return bones[0].objectPtr

def convertObjectData(context: bpy.types.Context,
					  use_selection: bool,
					  apply_modifs: bool,
					  export_matrix: mathutils.Matrix,
					  fmt: str,
					  lvl: bool):

	global DO

	# gettings the objects to export
	if use_selection:
		objects = context.selected_objects
	else:
		objects = context.scene.objects.values()

	if len(objects) == 0:
		raise ExportError("No objects to export")

	# getting the objects without parents
	noParents = list()
	for o in objects:
		if o.parent is None or not (o.parent in objects):
			noParents.append(o)

	# correct object order
	# sort top level objects first
	noParents.sort(key=lambda x: x.name)

	# sort children recursively and convert them to ModelData objects
	modelData: List[ModelData] = list()
	parent = None
	hierarchyDepth = 0
	if not lvl:
		if len(noParents) > 1:
			parent = ModelData(None,
							   None,
							   0,
							   "root",
							   export_matrix,
							   False,
							   False)
			modelData.append(parent)
			hierarchyDepth = 1

	lastSibling = None
	for o in noParents:
		current = sortChildren(o,
							   objects,
							   parent,
							   hierarchyDepth,
							   export_matrix,
							   fmt,
							   lvl,
							   modelData)
		if lastSibling is not None:
			lastSibling.sibling = current
		lastSibling = current

	if parent is not None:
		parent.child = parent.children[0]

	objects = modelData

	# get meshes
	if not lvl or lvl and fmt == 'SA1':

		mObjects = list()  # objects with a mesh
		for o in objects:
			if o.origObject is not None and o.origObject.type == 'MESH':
				mObjects.append(o)

		meshObjects, toConvert, addESplit, modifierStates \
			= evaluateMeshModifiers(mObjects, apply_modifs)
		meshes, materials = getMeshes(toConvert,
									  meshObjects,
									  apply_modifs,
									  context.evaluated_depsgraph_get(),
									  addESplit,
									  modifierStates)

		for k, v in modifierStates.items():
			k.show_viewport = v

		ModelData.updateMeshes(objects, meshes)

		# since sa2 can have armatures, we need to
		# handle things a little different...
		if fmt == 'SA2':
			newObjects = list()
			newMeshes = list()
			for o in objects:
				if not o.partOfArmature:
					newObjects.append(o)
					if o.processedMesh is not None \
							and o.processedMesh not in newMeshes:
						newMeshes.append(o.processedMesh)
			if len(newObjects) == 1 and isinstance(newObjects[0], Armature):
				objects = newObjects
				meshes = list()

		if DO:
			print(" == Exporting ==")
			print("  Materials:", len(materials))
			print("  Meshes:", len(meshes))
			print("  Objects:", len(objects))
			print("  - - - - - -\n")

		return objects, meshes, materials, mObjects

	else:  # only occurs when format is sa2lvl or sa2blvl
		cObjects = list()  # collision objects
		vObjects = list()  # visual objects

		for o in objects:
			if o.origObject.type == 'MESH':
				if o.saProps["solid"]:
					cObjects.append(o)
				if not o.saProps["solid"] \
						or o.saProps["solid"] \
						and o.saProps["isVisible"]:
					if fmt == 'SA2B':
						if len(o.origObject.data.color_attributes) == 0:
							obj = o.origObject
							obj.data.saSettings.sa2ExportType = 'VC'
							bpy.context.view_layer.objects.active = obj
							bpy.ops.geometry.color_attribute_add(name='COL0', domain='CORNER', data_type='BYTE_COLOR', color=(1.0,1.0,1.0,1.0))
							bpy.context.view_layer.objects.active = None
					vObjects.append(o)

		mObjects1, toConvert1, addESplit1, modifierStates1 \
			= evaluateMeshModifiers(cObjects, apply_modifs)

		mObjects2, toConvert2, addESplit2, modifierStates2 \
			= evaluateMeshModifiers(vObjects, apply_modifs)

		despgraph = context.evaluated_depsgraph_get()
		vMeshes, materials = getMeshes(toConvert2,
									   mObjects2,
									   apply_modifs,
									   despgraph,
									   addESplit2,
									   modifierStates2)

		finished = dict()
		for m in vMeshes:
			finished[m.name] = m

		cMeshes, dontUse = getMeshes(toConvert1,
									 mObjects1,
									 apply_modifs,
									 despgraph,
									 addESplit1,
									 modifierStates1,
									 finished)

		for k, v in modifierStates1.items():
			k.show_viewport = v
		for k, v in modifierStates2.items():
			k.show_viewport = v

		meshes = list()
		meshes.extend(cMeshes)
		meshes.extend(vMeshes)

		ModelData.updateMeshes(objects, meshes)

		if DO:
			print(" == Exporting ==")
			print("  Materials:", len(materials))
			print("  Visual Meshes:", len(vMeshes))
			print("  Collision Meshes:", len(cMeshes))
			print("  Objects:", len(objects))
			print("  - - - - - -\n")

		return objects, cMeshes, vMeshes, materials, cObjects, vObjects

def sortChildren(cObject: bpy.types.Object,
				 objects: List[bpy.types.Object],
				 parent: ModelData,
				 hierarchyDepth: int,
				 export_matrix: mathutils.Matrix,
				 fmt: str,
				 lvl: bool,
				 result: List[ModelData]) -> ModelData:
	"""Converts objects to ModelData and writes
	them in the correct order into the result list"""

	lastSibling = None
	if cObject.type == 'MESH':
		if lvl and fmt != 'SA1' \
				and cObject.saSettings.solid \
				and cObject.saSettings.isVisible:
			model = ModelData(cObject,
							  parent,
							  hierarchyDepth,
							  "vsl_" + cObject.name,
							  export_matrix,
							  False,
							  True)
			# collision
			lastSibling = ModelData(cObject,
									parent,
									hierarchyDepth,
									"cls_" + cObject.name,
									export_matrix,
									True,
									False)
			result.append(lastSibling)
		else:
			visible = True if not cObject.saSettings.solid \
						else cObject.saSettings.isVisible
			model = ModelData(cObject,
							  parent,
							  hierarchyDepth,
							  cObject.name,
							  export_matrix,
							  cObject.saSettings.solid,
							  visible)
	elif fmt == 'SA2' and not lvl and cObject.type == 'ARMATURE':
		visible = True if not cObject.saSettings.solid \
					else cObject.saSettings.isVisible
		model = Armature(cObject,
						 parent,
						 hierarchyDepth,
						 cObject.name,
						 export_matrix,
						 cObject.saSettings.solid,
						 visible)
	else:
		# everything that is not a mesh should be written as an empty
		model = ModelData(cObject,
						  parent,
						  hierarchyDepth,
						  cObject.name,
						  export_matrix,
						  False,
						  False)

	result.append(model)

	for c in cObject.children:
		if c in objects:
			child = sortChildren(c,
								 objects,
								 model,
								 hierarchyDepth + 1,
								 export_matrix,
								 fmt,
								 lvl,
								 result)
			if lastSibling is not None:
				lastSibling.sibling = child
			lastSibling = child

	# update sibling relationship
	if len(model.children) > 0:
		model.child = model.children[0]

	return model

def evaluateMeshModifiers(objects: List[ModelData], apply_modifs: bool):
	tMeshes = list()
	for o in objects:
		tMeshes.append(o.origObject.data)

	# checking whether there are any objects that share a mesh
	collectedMOMeshes = list()
	mObjects = list()
	meshesToConvert = list()
	for o in objects:
		if len(o.origObject.data.vertices) == 0:
			continue
		if tMeshes.count(o.origObject.data) > 1:
			if collectedMOMeshes.count(o.origObject.data) == 0:
				mObjects.append(o)
				meshesToConvert.append(o)
				collectedMOMeshes.append(o.origObject.data)
		else:
			meshesToConvert.append(o)

	# setting modifier data first, so that the mesh gets exported correctly
	toConvert = list()
	modifierStates: Dict[bpy.types.Modifier, bool] = dict()
	addESplit: Dict[bpy.types.Object, bpy.types.EdgeSplitModifier] = dict()
	for o in meshesToConvert:
		obj = o.origObject
		toConvert.append(o)
		t_apply_modifs = False if o in mObjects else apply_modifs

		hasEdgeSplit = False
		for m in obj.modifiers:
			if isinstance(m, bpy.types.ArmatureModifier):
				modifierStates[m] = m.show_viewport
				m.show_viewport = False
			elif isinstance(m, bpy.types.EdgeSplitModifier):
				hasEdgeSplit = True

		# if the mesh has no edge split modifier
		# but uses auto smooth, then add one to compensate for sharp edges
		if obj.data.use_auto_smooth and not hasEdgeSplit and t_apply_modifs:
			ESM = obj.modifiers.new("AutoEdgeSplit", 'EDGE_SPLIT')
			ESM.split_angle = obj.data.auto_smooth_angle
			ESM.use_edge_angle = not obj.data.has_custom_normals
			addESplit[obj] = ESM

	return mObjects, meshesToConvert, addESplit, modifierStates

def getMeshes(meshesToConvert: List[ModelData],
			  mObjects: List[ModelData],
			  apply_modifs: bool,
			  depsgraph,
			  addESplit: Dict[bpy.types.Object, bpy.types.EdgeSplitModifier],
			  modifierStates: Dict[bpy.types.Modifier, bool],
			  finished=dict()):
	outMeshes = list()
	materials: Dict[str, bpy.types.Material] = dict()

	for o in meshesToConvert:
		obj = o.origObject
		if not (o.saProps["solid"] and not o.saProps["isVisible"]):
			for m in obj.data.materials:
				if m.name not in materials:
					materials[m.name] = m

		if obj.data.name in finished:
			outMeshes.append(finished[obj.data.name])
			continue

		if len(o.origObject.data.vertices) == 0:
			continue
		t_apply_modifs = False if o in mObjects else apply_modifs

		ob_for_convert = obj.evaluated_get(depsgraph) if t_apply_modifs \
			else obj.original

		me = ob_for_convert.to_mesh(preserve_all_data_layers=True,
									depsgraph=depsgraph)
		trianglulateMesh(me)

		if obj in addESplit:
			obj.modifiers.remove(addESplit[obj])

		me.saSettings.sa2ExportType = obj.data.saSettings.sa2ExportType
		me.saSettings.sa2IndexOffset = obj.data.saSettings.sa2IndexOffset

		outMeshes.append(me)

	return outMeshes, materials

def trianglulateMesh(mesh: bpy.types.Mesh):
	"""Transforms a mesh into a mesh only consisting
	of triangles, so that it can be stripped"""

	# if we use custom normals, we gotta correct them
	# manually, since blenders triangulate is shit
	if mesh.use_auto_smooth:
		# calculate em, so that we can collect the correct normals
		mesh.calc_normals_split()

		# and now store them, together with the vertex indices,
		# since those will be the only identical data after triangulating
		normalData = list()
		for p in mesh.polygons:
			indices = list()
			normals = list()

			for l in p.loop_indices:
				loop = mesh.loops[l]
				nrm = loop.normal
				normals.append((nrm.x, nrm.y, nrm.z))
				indices.append(loop.vertex_index)

			normalData.append((indices, normals))

		# free the split data
		# mesh.free_normals_split()

	import bmesh
	bm = bmesh.new()
	bm.from_mesh(mesh)
	bmesh.ops.triangulate(bm,
						  faces=bm.faces,
						  quad_method='FIXED',
						  ngon_method='EAR_CLIP')
	bm.to_mesh(mesh)
	bm.free()

	if mesh.use_auto_smooth:
		polygons = list()
		for p in mesh.polygons:
			polygons.append(p)

		splitNormals = [None] * len(mesh.loops)

		for nd in normalData:
			foundTris = 0
			toFind = len(nd[0])-2

			out = False
			toRemove = list()

			for p in polygons:
				found = 0
				for l in p.loop_indices:
					if mesh.loops[l].vertex_index in nd[0]:
						found += 1

				if found == 3:
					foundTris += 1

					for l in p.loop_indices:
						splitNormals[l] \
							= nd[1][nd[0].index(mesh.loops[l].vertex_index)]

					toRemove.append(p)
					if foundTris == toFind:
						break

			for p in toRemove:
				polygons.remove(p)

		if len(polygons) > 0:
			print("\ntriangulating went wrong?", len(polygons))
		else:
			mesh.normals_split_custom_set(splitNormals)

def getNormalData(mesh: bpy.types.Mesh) -> list():
	normals = list()
	if mesh.use_auto_smooth:
		mesh.calc_normals_split()
		for v in mesh.vertices:
			normal = mathutils.Vector((0, 0, 0))
			normalCount = 0
			for l in mesh.loops:
				if l.vertex_index == v.index:
					normal += l.normal
					normalCount += 1
			if normalCount == 0:
				normals.append(v.normal)
			else:
				normals.append(normal / normalCount)

		mesh.free_normals_split()
	else:
		for v in mesh.vertices:
			normals.append(v.normal)
	return normals

def writeMethaData(fileW: fileHelper.FileWriter,
				   labels: dict,
				   scene: bpy.types.Scene,
				   ):
	"""Writes the meta data of the file"""

	# === LABELS ===
	fileW.wUInt(enums.Chunktypes.Label.value)
	newLabels = dict()
	sizeLoc = fileW.tell()
	fileW.wUInt(0)

	global DO
	if DO:
		print(" == Labels ==")
		for v, k in labels.items():
			print("  ", k + ":", hex4(v))
		print("")

	# placeholders
	for l in labels:
		fileW.wUInt(0)
		fileW.wUInt(0)

	fileW.wLong(-1)

	# writing the strings
	for val, key in labels.items():
		newLabels[val] = fileW.tell() - sizeLoc - 4
		strKey = str(key)
		strKey = strKey.replace('.', '_')
		strKey = strKey.replace(' ', '_')
		fileW.wString(strKey)
		fileW.align(4)

	# returning to the dictionary start
	size = fileW.tell() - sizeLoc - 4
	fileW.seek(sizeLoc, 0)
	fileW.wUInt(size)

	# writing the dictionary
	for key, val in newLabels.items():
		fileW.wUInt(key)
		fileW.wUInt(val)

	# back to the end
	fileW.seek(0, 2)

	# getting the file info
	settings = scene.saSettings

	# === AUTHOR ===
	if not (settings.author == ""):
		fileW.wUInt(enums.Chunktypes.Author.value)
		sizeLoc = fileW.tell()
		fileW.wUInt(0)
		fileW.wString(settings.author)
		fileW.align(4)
		size = fileW.tell() - sizeLoc - 4
		fileW.seek(sizeLoc, 0)
		fileW.wUInt(size)
		fileW.seek(0, 2)

		if DO:
			print(" Author:", settings.author)

	# === DESCRIPTION ===
	if not (settings.description == ""):
		fileW.wUInt(enums.Chunktypes.Description.value)
		sizeLoc = fileW.tell()
		fileW.wUInt(0)
		fileW.wString(settings.description)
		fileW.align(4)
		size = fileW.tell() - sizeLoc - 4
		fileW.seek(sizeLoc, 0)
		fileW.wUInt(size)
		fileW.seek(0, 2)

		if DO:
			print(" Description:", settings.description)

	fileW.wUInt(enums.Chunktypes.End.value)
	fileW.wUInt(0)

def matrixFromScale(scale: mathutils.Vector) -> mathutils.Matrix:
	mtx = mathutils.Matrix()
	mtx[0][0] = scale[0]
	mtx[1][1] = scale[1]
	mtx[2][2] = scale[2]
	return mtx

def polyToTris(p: list) -> list:
	cP = 0
	cN = len(p) - 1
	rev = False
	triCount = len(p) - 2
	out = list()

	for i in range(triCount):
		if not rev:
			print(cP, cP + 1, cN)
			out.append((p[cP], p[cP + 1], p[cN]))
		else:
			print(cP, cN - 1, cN)
			out.append((p[cP], p[cN - 1], p[cN]))

		rev = not rev
		if rev:
			cP += 1
		else:
			cN -= 1

	return out

# for reading only
class Model:

	name: str
	objFlags: dict
	meshPtr: int

	matrix_world: mathutils.Matrix
	matrix_local: mathutils.Matrix

	child = None
	sibling = None

	parent = None
	children = list()
	meshes = list()

	def __init__(self,
				 name: str,
				 objFlags: dict,
				 meshPtr: int,
				 matrix_world: mathutils.Matrix,
				 matrix_local: mathutils.Matrix,
				 parent):
		self.name = name
		self.objFlags = objFlags
		self.meshPtr = meshPtr
		self.matrix_world = matrix_world
		self.matrix_local = matrix_local
		self.parent = parent
		if parent is not None:
			parent.children.append(self)
		self.children = list()
		self.meshes = list()

	def debug(self):
		print(f"  Model: {self.name}")
		print(f"    objectFlags: {self.objFlags}")
		print(f"    meshPtr: {hex4(self.meshPtr)}")
		print(f"    position: {Vector3(self.matrix_local.to_translation())}")
		rot = self.matrix_local.to_euler()
		print(f"    rotation: ({rot.x},{rot.y},{rot.z})")
		print(f"    scale: {Vector3(self.matrix_local.to_scale())}")

def readObjects(fileR:
				fileHelper.FileReader,
				address: int,
				hierarchyDepth: int,
				parent,
				labels: dict,
				result: list) -> Model:

	if address in labels:
		label: str = labels[address]

		name = label
	else:
		name = "node_" + hex4(address)

	from .__init__ import SAObjectSettings
	from .enums import ObjectFlags
	objFlags = SAObjectSettings.defaultDict()
	f = fileR.rUInt(address)
	
	objFlags["ignorePosition"]\
		= bool(f & ObjectFlags.NoPosition.value)
	objFlags["ignoreRotation"]\
		= bool(f & ObjectFlags.NoRotate.value)
	objFlags["ignoreScale"]\
		= bool(f & ObjectFlags.NoScale.value)
	objFlags["rotateZYX"]\
		= bool(f & ObjectFlags.RotateZYX.value)
	objFlags["skipDraw"]\
		= bool(f & ObjectFlags.NoDisplay.value)
	objFlags["skipChildren"]\
		= bool(f & ObjectFlags.NoChildren.value)
	objFlags["flagAnimate"]\
		= bool(f & ObjectFlags.NoAnimate.value)
	objFlags["flagMorph"]\
		= bool(f & ObjectFlags.NoMorph.value)

	meshPtr = fileR.rUInt(address + 4)
	# getting the rotation is a bit more difficult
	xRot = BAMSToRad(fileR.rInt(address + 20))
	yRot = BAMSToRad(fileR.rInt(address + 24))
	zRot = BAMSToRad(fileR.rInt(address + 28))

	pos = (fileR.rFloat(address + 8),
		-fileR.rFloat(address + 16),
		fileR.rFloat(address + 12))

	posMtx = mathutils.Matrix.Translation(pos)
	rotMtx = mathutils.Euler((xRot, -zRot, yRot), 'XZY').to_matrix().to_4x4()
	scaleMtx = matrixFromScale(
		(fileR.rFloat(address + 32),
		fileR.rFloat(address + 40),
		fileR.rFloat(address + 36)))

	matrix_local = posMtx @ rotMtx @ scaleMtx

	if parent is not None:
		matrix_world = parent.matrix_world @ matrix_local
	else:
		matrix_world = matrix_local.copy()

	model = Model(name,
				objFlags,
				meshPtr,
				matrix_world,
				matrix_local,
				parent)
	if result is not None:
		result.append(model)

	childPtr = fileR.rUInt(address + 44)
	if childPtr > 0:
		child = readObjects(fileR,
							childPtr,
							hierarchyDepth + 1,
							model,
							labels,
							result)
		model.child = child

	siblingPtr = fileR.rUInt(address + 48)
	if siblingPtr > 0:
		sibling = readObjects(fileR,
							siblingPtr,
							hierarchyDepth,
							parent,
							labels,
							result)
		model.sibling = sibling

	return model

class Col:
	saProps: dict

	unknown1: int  # sa1 COL
	unknown2: int  # both COL

	model: Model

	def __init__(self,
				 unknown1: int,
				 unknown2: int,
				 saProps: dict,
				 model: Model):
		self.unknown1 = unknown1
		self.unknown2 = unknown2
		self.saProps = saProps
		self.model = model

	@classmethod
	def read(cls,
			 fileR: fileHelper.FileReader,
			 address: int,
			 labels: dict,
			 SA2: bool):

		address += 16
		from . import __init__
		from .__init__ import SALandEntrySettings
		saProps = SALandEntrySettings.defaultDict()

		if SA2:
			objectPtr = fileR.rUInt(address)
			unknown1 = 0
			unknown2 = fileR.rInt(address + 4)
			blockbit = fileR.rInt(address + 8)
			f = fileR.rUInt(address+12)

			from .enums import SA2SurfaceFlags

			saProps["solid"]\
				= bool(f & SA2SurfaceFlags.Solid.value)
			saProps["sa2_water"]\
				= bool(f & SA2SurfaceFlags.Water.value)
			saProps["sa2_diggable"]\
				= bool(f & SA2SurfaceFlags.Diggable.value)
			saProps["sa2_unclimbable"]\
				= bool(f & SA2SurfaceFlags.Unclimbable.value)
			saProps["sa2_stairs"]\
				= bool(f & SA2SurfaceFlags.Stairs.value)
			saProps["sa2_hurt"]\
				= bool(f & SA2SurfaceFlags.Hurt.value)
			saProps["sa2_footprints"]\
				= bool(f & SA2SurfaceFlags.Footprints.value)
			saProps["sa2_cannotLand"]\
				= bool(f & SA2SurfaceFlags.CannotLand.value)
			saProps["sa2_water2"]\
				= bool(f & SA2SurfaceFlags.Water2.value)
			saProps["sa2_noShadows"]\
				= bool(f & SA2SurfaceFlags.NoShadows.value)
			saProps["sa2_noFog"]\
				= bool(f & SA2SurfaceFlags.noFog.value)
			saProps["sa2_unknown24"]\
				= bool(f & SA2SurfaceFlags.Unknown24.value)
			saProps["sa2_unknown29"]\
				= bool(f & SA2SurfaceFlags.Unknown29.value)
			saProps["sa2_unknown30"]\
				= bool(f & SA2SurfaceFlags.Unknown30.value)
			saProps["isVisible"]\
				= bool(f & SA2SurfaceFlags.Visible.value)

			saProps["userFlags"]\
				= hex4((f & ~SA2SurfaceFlags.known.value) & 0xFFFFFFFF)

			saProps["blockbit"] = hex4(blockbit)

			try:
				flagTest = SA2SurfaceFlags(f)
			except Exception:
				print("Unknown surface flags found:")
				print(saProps["userFlags"])

		else:
			objectPtr = fileR.rUInt(address + 8)
			unknown1 = fileR.rInt(address)
			unknown2 = fileR.rInt(address + 4)
			blockbit = fileR.rInt(address + 12)
			f = fileR.rUInt(address+16)
			from .enums import SA1SurfaceFlags

			saProps["solid"]\
				= bool(f & SA1SurfaceFlags.Solid.value)
			saProps["sa1_water"]\
				= bool(f & SA1SurfaceFlags.Water.value)
			saProps["sa1_noFriction"]\
				= bool(f & SA1SurfaceFlags.NoFriction.value)
			saProps["sa1_noAcceleration"]\
				= bool(f & SA1SurfaceFlags.NoAcceleration.value)
			saProps["sa1_lowAcceleration"]\
				= bool(f & SA1SurfaceFlags.LowAcceleration.value)
			saProps["sa1_useSkyDrawDistance"]\
				= bool(f & SA1SurfaceFlags.UseSkyDrawDistance.value)
			saProps["sa1_increasedAcceleration"]\
				= bool(f & SA1SurfaceFlags.IncreasedAcceleration.value)
			saProps["sa1_cannotLand"]\
				= bool(f & SA1SurfaceFlags.CannotLand.value)
			saProps["sa1_diggable"]\
				= bool(f & SA1SurfaceFlags.Diggable.value)
			saProps["sa1_waterfall"]\
				= bool(f & SA1SurfaceFlags.Waterfall.value)
			saProps["sa1_unclimbable"]\
				= bool(f & SA1SurfaceFlags.Unclimbable.value)
			saProps["sa1_chaos0Land"]\
				= bool(f & SA1SurfaceFlags.Chaos0Land.value)
			saProps["sa1_stairs"]\
				= bool(f & SA1SurfaceFlags.Stairs.value)
			saProps["sa1_hurt"]\
				= bool(f & SA1SurfaceFlags.Hurt.value)
			saProps["sa1_lowDepth"]\
				= bool(f & SA1SurfaceFlags.LowDepth.value)
			saProps["sa1_footprints"]\
				= bool(f & SA1SurfaceFlags.Footprints.value)
			saProps["sa1_accelerate"]\
				= bool(f & SA1SurfaceFlags.Accelerate.value)
			saProps["sa1_colWater"]\
				= bool(f & SA1SurfaceFlags.WaterCollision.value)
			saProps["sa1_rotByGravity"]\
				= bool(f & SA1SurfaceFlags.RotateByGravity.value)
			saProps["sa1_noZWrite"]\
				= bool(f & SA1SurfaceFlags.NoZWrite.value)
			saProps["sa1_drawByMesh"]\
				= bool(f & SA1SurfaceFlags.DrawByMesh.value)
			saProps["sa1_enableManipulation"]\
				= bool(f & SA1SurfaceFlags.EnableManipulation.value)
			saProps["sa1_dynCollision"]\
				= bool(f & SA1SurfaceFlags.DynamicCollision.value)
			saProps["sa1_useRotation"]\
				= bool(f & SA1SurfaceFlags.UseRotation.value)
			saProps["isVisible"]\
				= bool(f & SA1SurfaceFlags.Visible.value)

			saProps["userFlags"]\
				= hex4((f & ~SA1SurfaceFlags.known.value) & 0xFFFFFFFF)

			saProps["blockbit"] = hex4(blockbit)

			try:
				flagTest = SA1SurfaceFlags(f)
			except Exception:
				print("Unknown surface flags found:")
				print(saProps["userFlags"])

		model = readObjects(fileR, objectPtr, 0, None, labels, None)

		return Col(unknown1, unknown2, saProps, model)

	def toBlenderObject(self) -> bpy.types.Object:

		data = None if len(self.model.meshes) < 1 else self.model.meshes[0]
		obj = bpy.data.objects.new(self.model.name, data)
		obj.matrix_world = self.model.matrix_world
		obj.saSettings.fromDictionary(self.saProps)
		obj.saObjflags.fromDictionary(self.model.objFlags)

		return obj

def fixMaterialNames(objects: List[bpy.types.Object]):

	materials: List[bpy.types.Material] = list()
	collisionMats: List[bpy.types.Material] = list()

	for o in objects:
		if o.type == 'MESH':
			for m in o.data.materials:
				if m.name[0] == 'c':
					if m not in collisionMats:
						collisionMats.append(m)
				elif m not in materials:
					materials.append(m)

	materials.sort(key=lambda x: x.name)
	collisionMats.sort(key=lambda x: x.name)

	zfillLengthM = len(str(len(materials)))
	zfillLengthC = len(str(len(collisionMats)))

	for i, m in enumerate(materials):
		m.name = "material_" + str(i).zfill(zfillLengthM)
	for i, m in enumerate(collisionMats):
		m.name = "collision_" + str(i).zfill(zfillLengthC)

def getDefaultPath():
	settings = bpy.context.scene.saProjInfo
	path = ""
	if (get_prefs().useProjectPath) and (settings.ProjectFolder != ""):
		path = settings.ProjectFolder
	else:
		path = get_prefs().defaultPath

	return path

def PGetAngleXZFromNormal(px: float, py: float, pz: float):
	# Copied from SA1
	fpx = math.fabs(px)
	fpy = math.fabs(py)
	num = 0.1591549762031479
	if ((pz > 0.9999) or (fpy < 0.002 and fpx < 0.002 and pz > 0.0)):
		ax = 90.0
		az = 0.0
	elif ((py < -0.9999) or (fpy < 0.002 and fpx < 0.002 and pz < 0.0)):
		ax = 270.0
		az = 0.0
	else:
		ax = (math.asin(pz) * 65536.0 * num)
		az = (math.atan2(px, py) * 65536.0 * -num)

	angx = int(ax)
	angz = int(az)

	if angx < 0:
		angx += 65536
	if angz < 0:
		angz += 65536.0

	retx = float((angx/65535.0)*360.0)
	retz = float((angz/65535.0)*360.0)
	print(str(retx))
	print(str(retz))
	return [retx, retz]