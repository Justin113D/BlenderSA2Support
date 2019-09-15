import bpy
from . import FileWriter, enums

DO = False # Debug Out

class Vector3:
    """Point in 3D Space"""

    x = 0
    y = 0
    z = 0

    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z

    def distanceFromCenter(self):
        return (self.x * self.x + self.y * self.y + self.z * self.z)**(0.5)

    def write(self, fileW):
        """Writes data to file"""
        fileW.wFloat(self.x)
        fileW.wFloat(self.y)
        fileW.wFloat(self.z)

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

class BAMSRotation:

    x = 0
    y = 0
    z = 0

    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.x = BAMSRotation.DegToBAMS(x)
        self.y = BAMSRotation.DegToBAMS(y)
        self.z = BAMSRotation.DegToBAMS(z)


    def DegToBAMS(v):
        return round(v * (65536 / 360.0))

    def BAMSToDeg(v):
        return v / (65536 / 360.0)

    def write(self, fileW):
        """Writes data to file"""
        fileW.wInt(self.x)
        fileW.wInt(self.y)
        fileW.wInt(self.z)

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

class saObject:

    name = ""
    hierarchyLvl = 0
    address = 0
    flags = enums.ObjectFlags.NoAnimate | enums.ObjectFlags.NoMorph
    meshAddress = 0
    position = Vector3()
    rotation = BAMSRotation()
    scale = Vector3(1,1,1)
    child = None
    sibling = None

    def __init__(self,
                 name: str = "",
                 meshname: str = None,
                 flags = enums.ObjectFlags.NoAnimate | enums.ObjectFlags.NoMorph,
                 pos = [0,0,0],
                 rot = [0,0,0],
                 scale = [0,0,0],
                 child = None,
                 sibling = None,
                 hlvl = 0,
                 labels = None):
    
        self.name = name
        self.flags = flags
        if meshname is None:
            self.meshAddress = 0
            self.flags |= enums.ObjectFlags.NoDisplay
        else:
            self.meshAddress = labels["a_" + meshname]

        self.position = Vector3(pos[0], pos[1], pos[2])
        self.rotation = BAMSRotation(rot[0], rot[1], rot[2])
        self.scale = Vector3(scale[0], scale[1], scale[2])
        self.child = child
        if child is None:
            self.flags |= enums.ObjectFlags.NoChildren
        self.sibling = sibling
        self.address = 0 # set when writing
        self.hierarchyLvl = hlvl

    def getObjList(bObject: bpy.types.Object, objects, hlvl, global_matrix, siblings, result, labels):

        sibling = None
        if len(siblings) > 1:
            
            siblIndex = siblings.index(bObject) + 1
            if siblIndex < len(siblings):
                sibling = siblings[siblIndex]
                while not (sibling in objects):
                    siblIndex += 1
                    if siblIndex < len(siblings):
                        sibling = siblings[siblIndex]
                    else:
                        sibling = None
                        break
                    
                if sibling is not None:
                    saObject.getObjList(sibling, objects, hlvl, global_matrix, siblings, result, labels)
                    sibling = result[-1]

        if len(bObject.children) > 0 and bObject.children[0] in objects:
            saObject.getObjList(bObject.children[0], objects, hlvl + 1, global_matrix, bObject.children, result, labels)
            child = result[-1]
        else:
            child = None

        obj_mat = bObject.matrix_world @ global_matrix

        meshname = None
        if bObject.type == 'MESH':
            meshname = bObject.data.name

        obj = saObject(name=bObject.name,
                       meshname=meshname, 
                       # flags will be set later
                       pos= obj_mat.translation,
                       rot= obj_mat.to_euler(),
                       scale= obj_mat.to_scale(),
                       child= child,
                       sibling= sibling,
                       hlvl=hlvl,
                       labels=labels
                       )
        result.append(obj)

    def write(self, fileW, labels):
        labels["o_" + self.name] = fileW.tell()
        self.address = fileW.tell()

        fileW.wUInt(self.flags.value)
        fileW.wUInt(self.meshAddress)
        self.position.write(fileW)
        self.rotation.write(fileW)
        self.scale.write(fileW)
        fileW.wUInt(0 if self.child is None else self.child.address)
        fileW.wUInt(0 if self.sibling is None else self.sibling.address)

    def writeObjList(fileW, objList, labels):
        for o in objList:
            o.write(fileW, labels)
        
        return objList[-1].address # last object address

    def debugOut(self):
        print(" Object:", self.name)
        print("   address:", '{:08x}'.format(self.address))
        print("   mesh addr:", '{:08x}'.format(self.meshAddress))
        print("   flags:", self.flags)
        print("   position:", str(self.position))
        print("   rotation:", str(self.rotation))
        print("   scale:", str(self.scale))
        print("   child:", "None" if self.child is None else self.child.name)
        print("   sibling:", "None" if self.sibling is None else self.sibling.name)
        print("---- \n")

    def debugHierarchy(objList):
        print("object hierarchy:")
        for o in reversed(objList):
            print(" --" * o.hierarchyLvl, o.name)
        print("\n---- \n")

def trianglulateMesh(me):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method='FIXED', ngon_method='EAR_CLIP')
    bm.to_mesh(me)
    bm.free()

def convertMesh(obj, depsgraph, apply_modifs):

   if isinstance(obj, bpy.types.Object):
      ob_for_convert = obj.evaluated_get(depsgraph) if apply_modifs else obj.original
      me = ob_for_convert.to_mesh()
      name = obj.data.name
   else:
      me = obj
      name = me.name

   trianglulateMesh(me)
   return [me, name]

def writeBASICMaterialData(fileW: FileWriter.FileWriter, materials, labels: dict):
    from . import BASIC

    mats = list()

    if len(materials) == 0:
        labels["mat_default"] = fileW.tell()
        bMat = BASIC.Material()
        bMat.write(fileW)
        mats.append(bMat)
    else:
        for m in materials:
            labels["mat_" + m.name] = fileW.tell()
            bMat = BASIC.Material(name=m.name, material=m)
            bMat.write(fileW)
            mats.append(bMat)

    global DO
    if DO:
        for m in mats:
            print(" Material:", m.name)
            print("   diffuse color:", str(m.diffuse))
            print("   specular color:", str(m.specular))
            print("   specular strength:", m.exponent)
            print("   texture ID:", m.textureID)
            print("   flags:", m.mFlags, "\n---- \n")

def writeBASICMeshData( fileW: FileWriter.FileWriter,
                        depsgraph,
                        meshes,
                        apply_modifs,
                        global_matrix,
                        materialAddress,
                        materials,
                        labels: dict):
    from . import BASIC
    for m in meshes:
        me = convertMesh(m, depsgraph, apply_modifs)
        basicMesh = BASIC.WriteMesh(me[0], me[1], global_matrix, fileW.tell(), materialAddress, materials, labels)
        fileW.w(basicMesh)

