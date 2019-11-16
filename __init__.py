# meta info
bl_info = {
    "name": "SA Model Formats support",
    "author": "Justin113D",
    "version": (0,6,4),
    "blender": (2, 80, 0),
    "location": "File > Import/Export",
    "description": "Import/Exporter for the SA Models Formats. For any questions, contact me via Discord: Justin113D#1927",
    "warning": "",
    "wiki_url": "",
    "support": 'COMMUNITY',
    "category": "Import-Export"}

if "bpy" in locals():
    import importlib
    if "file_MDL" in locals():
        importlib.reload(file_MDL)
    if "file_LVL" in locals():
        importlib.reload(file_LVL)
    if "format_BASIC" in locals():
        importlib.reload(format_BASIC)
    if "format_GC" in locals():
        importlib.reload(format_GC)
    if "format_CHUNK" in locals():
        importlib.reload(format_CHUNK)
    if "strippifier" in locals():
        importlib.reload(strippifier)
    if "fileHelper" in locals():
        importlib.reload(fileHelper)
    if "enums" in locals():
        importlib.reload(enums)
    if "common" in locals():
        importlib.reload(common)

import bpy
import os
from . import fileHelper, common
from bpy.props import (
    BoolProperty,
    BoolVectorProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    IntVectorProperty,
    EnumProperty,
    StringProperty
    )
from bpy_extras.io_utils import ExportHelper, ImportHelper#, path_reference_mode

class TOPBAR_MT_SA_export(bpy.types.Menu):
    bl_label = "SA Formats"
    #bl_idname = "export_scene.samenu"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Export as...")
        layout.operator("export_scene.sa1mdl")
        layout.operator("export_scene.sa2mdl")
        layout.operator("export_scene.sa2bmdl")
        layout.separator()
        layout.operator("export_scene.sa1lvl")
        layout.operator("export_scene.sa2lvl")
        layout.operator("export_scene.sa2blvl")

# export operators

def removeFile():

    fileW = __init__.exportedFile
    if fileW is not None:
        fileW.close()
        os.remove(fileW.filepath)
        __init__.exportedFile = None

def exportFile(op, mdl: bool, context, **keywords):
    try:
        if mdl:
            out = file_MDL.write(context, **keywords)
        else:
            out = file_LVL.write(context, **keywords)
    except strippifier.TopologyError as e:
        op.report({'WARNING'}, "Export stopped!\n" + str(e))
        removeFile()
        return {'CANCELLED'}
    except common.ExportError as e:
        op.report({'WARNING'}, "Export stopped!\n" + str(e))
        removeFile()
        return {'CANCELLED'}
    except Exception as e:
        removeFile()
        raise e

    # moving and renaming the temporary file
    # also removing the file that existed before
    fileW = __init__.exportedFile
    filepath = keywords["filepath"]
    if(os.path.isfile(filepath)):
        os.remove(filepath)
    os.rename(fileW.filepath, filepath)

    return {'FINISHED'}

class ExportSA1MDL(bpy.types.Operator, ExportHelper):
    """Export Objects into an SA1 model file"""
    bl_idname = "export_scene.sa1mdl"
    bl_label = "SA1 model (.sa1mdl)"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".sa1mdl"

    filter_glob: StringProperty(
        default="*.sa1mdl;",
        options={'HIDDEN'},
        )

    global_scale: FloatProperty(
        name="Scale",
        min=0.01, max=1000.0,
        default=1.0,
        )

    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
        )

    apply_modifs: BoolProperty(
        name="Apply Modifiers",
        description="Apply active viewport modifiers",
        default=True,
        )

    console_debug_output: BoolProperty(
        name = "Console Output",
        description = "Shows exporting progress in Console (Slows down Exporting Immensely)",
        default = False,
        )

    def execute(self, context):
        from . import file_MDL
        keywords = self.as_keywords(ignore=( "check_existing", "filter_glob"))
        keywords["export_format"] = 'SA1'
        return exportFile(self, True, context, **keywords)

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout
        layout.alignment = 'RIGHT'

        layout.prop(self, "global_scale")
        layout.prop(self, "use_selection")
        layout.prop(self, "apply_modifs")
        layout.separator()
        layout.prop(self, "console_debug_output")

class ExportSA2MDL(bpy.types.Operator, ExportHelper):
    """Export Objects into an SA2 model file"""
    bl_idname = "export_scene.sa2mdl"
    bl_label = "SA2 model (.sa2mdl)"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".sa2mdl"

    filter_glob: StringProperty(
        default="*.sa2mdl;",
        options={'HIDDEN'},
        )

    global_scale: FloatProperty(
        name="Scale",
        min=0.01, max=1000.0,
        default=1.0,
        )

    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
        )

    apply_modifs: BoolProperty(
        name="Apply Modifiers",
        description="Apply active viewport modifiers",
        default=True,
        )

    console_debug_output: BoolProperty(
        name = "Console Output",
        description = "Shows exporting progress in Console (Slows down Exporting Immensely)",
        default = False,
        )

    def execute(self, context):
        from . import file_MDL
        keywords = self.as_keywords(ignore=( "check_existing", "filter_glob"))
        keywords["export_format"] = 'SA2'
        return exportFile(self, True, context, **keywords)

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout
        layout.alignment = 'RIGHT'

        layout.prop(self, "global_scale")
        layout.prop(self, "use_selection")
        layout.prop(self, "apply_modifs")
        layout.separator()
        layout.prop(self, "console_debug_output")

class ExportSA2BMDL(bpy.types.Operator, ExportHelper):
    """Export Objects into an SA2B model file"""
    bl_idname = "export_scene.sa2bmdl"
    bl_label = "SA2B model (.sa2bmdl)"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".sa2bmdl"

    filter_glob: StringProperty(
        default="*.sa2bmdl;",
        options={'HIDDEN'},
        )

    global_scale: FloatProperty(
        name="Scale",
        min=0.01, max=1000.0,
        default=1.0,
        )

    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
        )

    apply_modifs: BoolProperty(
        name="Apply Modifiers",
        description="Apply active viewport modifiers",
        default=True,
        )

    console_debug_output: BoolProperty(
        name = "Console Output",
        description = "Shows exporting progress in Console (Slows down Exporting Immensely)",
        default = False,
        )

    def execute(self, context):
        from . import file_MDL
        keywords = self.as_keywords(ignore=( "check_existing", "filter_glob"))
        keywords["export_format"] = 'SA2B'
        return exportFile(self, True, context, **keywords)

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout
        layout.alignment = 'RIGHT'

        layout.prop(self, "global_scale")
        layout.prop(self, "use_selection")
        layout.prop(self, "apply_modifs")
        layout.separator()
        layout.prop(self, "console_debug_output")

class ExportSA1LVL(bpy.types.Operator, ExportHelper):
    """Export scene into an SA1 level file"""
    bl_idname = "export_scene.sa1lvl"
    bl_label = "SA1 level (.sa1lvl)"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".sa1lvl"

    filter_glob: StringProperty(
        default="*.sa1lvl;",
        options={'HIDDEN'},
        )

    global_scale: FloatProperty(
        name="Scale",
        min=0.01, max=1000.0,
        default=1.0,
        )

    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
        )

    apply_modifs: BoolProperty(
        name="Apply Modifiers",
        description="Apply active viewport modifiers",
        default=True,
        )

    console_debug_output: BoolProperty(
        name = "Console Output",
        description = "Shows exporting progress in Console (Slows down Exporting Immensely)",
        default = False,
        )

    def execute(self, context):
        from . import file_LVL
        keywords = self.as_keywords(ignore=( "check_existing", "filter_glob"))
        keywords["export_format"] = 'SA1'
        return exportFile(self, False, context, **keywords)

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout
        layout.alignment = 'RIGHT'

        layout.prop(self, "global_scale")
        layout.prop(self, "use_selection")
        layout.prop(self, "apply_modifs")
        layout.separator()
        layout.prop(self, "console_debug_output")

class ExportSA2LVL(bpy.types.Operator, ExportHelper):
    """Export scene into an SA2 level file"""
    bl_idname = "export_scene.sa2lvl"
    bl_label = "SA2 level (.sa2lvl)"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".sa2lvl"

    filter_glob: StringProperty(
        default="*.sa2lvl;",
        options={'HIDDEN'},
        )

    global_scale: FloatProperty(
        name="Scale",
        min=0.01, max=1000.0,
        default=1.0,
        )

    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
        )

    apply_modifs: BoolProperty(
        name="Apply Modifiers",
        description="Apply active viewport modifiers",
        default=True,
        )

    console_debug_output: BoolProperty(
        name = "Console Output",
        description = "Shows exporting progress in Console (Slows down Exporting Immensely)",
        default = False,
        )

    def execute(self, context):
        from . import file_LVL
        keywords = self.as_keywords(ignore=( "check_existing", "filter_glob"))
        keywords["export_format"] = 'SA2'
        return exportFile(self, False, context, **keywords)

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout
        layout.alignment = 'RIGHT'

        layout.prop(self, "global_scale")
        layout.prop(self, "use_selection")
        layout.prop(self, "apply_modifs")
        layout.separator()
        layout.prop(self, "console_debug_output")

class ExportSA2BLVL(bpy.types.Operator, ExportHelper):
    """Export scene into an SA2B level file"""
    bl_idname = "export_scene.sa2blvl"
    bl_label = "SA2B level (.sa2blvl)"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".sa2blvl"

    filter_glob: StringProperty(
        default="*.sa2blvl;",
        options={'HIDDEN'},
        )

    global_scale: FloatProperty(
        name="Scale",
        min=0.01, max=1000.0,
        default=1.0,
        )

    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
        )

    apply_modifs: BoolProperty(
        name="Apply Modifiers",
        description="Apply active viewport modifiers",
        default=True,
        )

    console_debug_output: BoolProperty(
        name = "Console Output",
        description = "Shows exporting progress in Console (Slows down Exporting Immensely)",
        default = False,
        )

    def execute(self, context):
        from . import file_LVL
        keywords = self.as_keywords(ignore=( "check_existing", "filter_glob"))

        keywords["export_format"] = 'SA2B'
        return exportFile(self, False, context, **keywords)

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout
        layout.alignment = 'RIGHT'

        layout.prop(self, "global_scale")
        layout.prop(self, "use_selection")
        layout.prop(self, "apply_modifs")
        layout.separator()
        layout.prop(self, "console_debug_output")

# import operators

class ImportMDL(bpy.types.Operator, ImportHelper):
    """Imports any adventure mdl file"""
    bl_idname = "import_scene.mdl"
    bl_label = "Sonic Adv. model (.*mdl)"
    bl_options = {'PRESET', 'UNDO'}

    filter_glob: StringProperty(
        default="*.sa1mdl;*.sa2mdl;*.sa2bmdl;",
        options={'HIDDEN'},
        )

    console_debug_output: BoolProperty(
            name = "Console Output",
            description = "Shows exporting progress in Console (Slows down Exporting Immensely)",
            default = False,
            )

    def execute(self, context):
        from . import file_MDL

        return file_MDL.read(context, self.filepath, self.console_debug_output)

class ImportLVL(bpy.types.Operator, ImportHelper):
    """Imports any adventure mdl file"""
    bl_idname = "import_scene.lvl"
    bl_label = "Sonic Adv. level (.*lvl)"
    bl_options = {'PRESET', 'UNDO'}

    filter_glob: StringProperty(
        default="*.sa1lvl;*.sa2lvl;*.sa2blvl;",
        options={'HIDDEN'},
        )

    console_debug_output: BoolProperty(
            name = "Console Output",
            description = "Shows exporting progress in Console (Slows down Exporting Immensely)",
            default = False,
            )

    def execute(self, context):
        from . import file_LVL

        return file_LVL.read(context, self.filepath, self.console_debug_output)


# operators
class StrippifyTest(bpy.types.Operator):
    bl_idname = "object.strippifytest"
    bl_label = "Strippify (testing)"
    bl_description = "Strippifies the active model object and puts each strip into a new object"

    def mesh_triangulate(self, me):
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces, quad_method='FIXED', ngon_method='EAR_CLIP')
        bm.to_mesh(me)
        bm.free()

    doConcat: BoolProperty(
        name = "Concat",
        description="Combines all strips into one big strip",
        default=False
        )

    doSwaps: BoolProperty(
        name = "Utilize Swapping",
        description = "Utilizes swapping when creating strips, which can result in a smaller total strip count",
        default = False
        )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        #os.system("cls")
        obj = context.active_object
        if obj is None or not isinstance(obj.data, bpy.types.Mesh):
            print("active object not a mesh")
            return {'FINISHED'}

        ob_for_convert = obj.original
        me = ob_for_convert.to_mesh()
        self.mesh_triangulate(me)

        # creating the vertex list
        verts = []
        oIDtodID = [0] * len(me.vertices)

        for IDo, vo in enumerate(me.vertices):
            vert = [vo.co.x, vo.co.y, vo.co.z]
            found = -1
            for IDd, vd in enumerate(verts):
                if vert == vd:
                    found = IDd
                    break
            if found == -1:
                verts.append(vert)
                oIDtodID[IDo] = len(verts) - 1
            else:
                oIDtodID[IDo] = found

        # creating the index list
        indexList = [0] * len(me.polygons) * 3

        for i, p in enumerate(me.polygons):
            for j, li in enumerate(p.loop_indices):
                indexList[i * 3 + j] = oIDtodID[me.loops[li].vertex_index]

        # strippifying it
        from . import strippifier
        stripf = strippifier.Strippifier()
        indexStrips = stripf.Strippify(indexList, doSwaps = self.doSwaps, concat = self.doConcat)

        if not self.doConcat:
            empty = bpy.data.objects.new(obj.data.name + "_str", None)
            context.collection.objects.link(empty)
            for i, s in enumerate(indexStrips):
                # making them lists so blender can use them
                indexList = list()
                for j in range(0, len(s)-2):
                    p = [s[j], s[j+1], s[j+2]]
                    indexList.append(p)

                mesh = bpy.data.meshes.new(name = obj.data.name + "_str_" + str(i))
                mesh.from_pydata(verts, [], indexList)
                meObj = bpy.data.objects.new(mesh.name, object_data = mesh)
                context.collection.objects.link(meObj)
                meObj.parent = empty
        else:
            indexList = list()
            for i in range(0, len(indexStrips) - 2):
                p = [indexStrips[i], indexStrips[i+1], indexStrips[i+2]]
                if len(set(p)) == 3:
                    indexList.append(p)

            mesh = bpy.data.meshes.new(name = obj.data.name + "_str")
            mesh.from_pydata(verts, [], indexList)
            meObj = bpy.data.objects.new(mesh.name, object_data = mesh)
            context.collection.objects.link(meObj)

        return {'FINISHED'}

class ArmatureFromObjects(bpy.types.Operator):
    bl_idname = "object.armaturefromobjects"
    bl_label = "Armature from objects"
    bl_description = "Generate an armature from object. Select the parent of all objects, which will represent the root"

    def addChildren(parent, result, resultMeshes):
        if parent.type == 'MESH':
            resultMeshes.append(len(result))
        result.append(parent)

        for c in parent.children:
            ArmatureFromObjects.addChildren(c, result, resultMeshes)

    def execute(self, context):

        if len(context.selected_objects) == 0 or bpy.context.object.mode != 'OBJECT':
            return {'CANCELLED'}
        active = context.active_object

        objects = list()
        meshes = list()

        ArmatureFromObjects.addChildren(active, objects, meshes)

        zfillSize = max(2, len(str(len(meshes))))

        if len(objects) == 1:
            return {'CANCELLED'}

        armature = bpy.data.armatures.new("ARM_" + active.name)
        armatureObj = bpy.data.objects.new("ARM_" + active.name, armature)
        armatureObj.parent = active.parent
        armatureObj.matrix_local = active.matrix_local
        globalMatrix = active.matrix_world

        context.scene.collection.objects.link(armatureObj)

        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = armatureObj
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        edit_bones = armatureObj.data.edit_bones
        boneMap = dict()
        bones = objects[1:]


        for b in bones:
            boneName = b.name
            bone = edit_bones.new(b.name)
            bone.layers[0] = True
            bone.head = (0,0,0)
            bone.tail = (1,0,0)
            bone.matrix = globalMatrix.inverted() @ b.matrix_world

            if b.parent in bones:
                bone.parent = boneMap[b.parent]
            boneMap[b] = bone

        bpy.ops.object.mode_set(mode='OBJECT')
        meshCount = 0

        for i in meshes:
            boneObject = objects[i]

            meshCopy = boneObject.data.copy()
            meshCopy.name = "Mesh_" + str(meshCount).zfill(zfillSize)
            meshObj = boneObject.copy()
            meshObj.name = meshCopy.name
            meshObj.data = meshCopy
            context.scene.collection.objects.link(meshObj)

            meshObj.parent = armatureObj
            meshObj.matrix_local = globalMatrix.inverted() @ boneObject.matrix_world

            bpy.ops.object.mode_set(mode='OBJECT')
            meshObj.select_set(True, view_layer=context.view_layer)
            bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)

            modif = meshObj.modifiers.new("deform", 'ARMATURE')
            modif.object = armatureObj

            group = meshObj.vertex_groups.new(name=boneObject.name)
            group.add([v.index for v in meshCopy.vertices], 1, 'ADD')

            meshCount += 1
            meshObj.select_set(False, view_layer=context.view_layer)





        return {'FINISHED'}

def qmeUpdate(context, newValue):

    matQProps = context.scene.saSettings.matQProps
    matQEditor = context.scene.saSettings.matQEditor

    objects = context.selected_objects
    mats = []
    for o in objects:
        if o.type == 'MESH':
            for m in o.data.materials:
                if m not in mats:
                    mats.append(m)

    for m in mats:
        matProps = m.saSettings

        if matQEditor.b_apply_diffuse and newValue:
            matProps.b_Diffuse = matQProps.b_Diffuse

        if matQEditor.b_apply_specular and newValue:
            matProps.b_Specular = matQProps.b_Specular

        if matQEditor.b_apply_Ambient and newValue:
            matProps.b_Ambient = matQProps.b_Ambient

        if matQEditor.b_apply_specularity and newValue:
            matProps.b_Exponent = matQProps.b_Exponent

        if matQEditor.b_apply_texID and newValue:
            matProps.b_TextureID = matQProps.b_TextureID

        if matQProps.b_d_025:
            matProps.b_d_025 = newValue

        if matQProps.b_d_050:
            matProps.b_d_050 = newValue

        if matQProps.b_d_100:
            matProps.b_d_100 = newValue

        if matQProps.b_d_200:
            matProps.b_d_200 = newValue

        if matQProps.b_use_Anisotropy:
            matProps.b_use_Anisotropy = newValue

        if matQEditor.b_apply_filter and newValue:
            matProps.b_texFilter = matQProps.b_texFilter

        if matQProps.b_clampU:
            matProps.b_clampU = newValue

        if matQProps.b_clampV:
            matProps.b_clampV = newValue

        if matQProps.b_mirrorU:
            matProps.b_mirrorU = newValue

        if matQProps.b_mirrorV:
            matProps.b_mirrorV = newValue

        if matQProps.b_mirrorV:
            matProps.b_mirrorV = newValue

        if matQProps.b_useTexture:
            matProps.b_useTexture = newValue

        if matQProps.b_useEnv:
            matProps.b_useEnv = newValue

        if matQProps.b_useAlpha:
            matProps.b_useAlpha = newValue
            matProps.b_destAlpha = matQProps.b_destAlpha
            matProps.b_srcAlpha = matQProps.b_srcAlpha

        if matQProps.b_doubleSided:
            matProps.b_doubleSided = newValue

        if matQProps.b_ignoreSpecular:
            matProps.b_ignoreSpecular = newValue

        if matQProps.b_ignoreLighting:
            matProps.b_ignoreLighting = newValue

        if matQProps.b_ignoreAmbient:
            matProps.b_ignoreAmbient = newValue

        if matQProps.b_flatShading:
            matProps.b_flatShading = newValue

class qmeUpdateSet(bpy.types.Operator):
    """Quick Material Editor Updater for setting selected field to true"""
    bl_idname = "object.qmeset"
    bl_label = "SET properties"
    bl_description = "Sets the selected QME properties in the materials of all selected objects to TRUE"

    def execute(self, context):
        qmeUpdate(context, True)
        return {'FINISHED'}

class qmeUpdateUnset(bpy.types.Operator):
    """Quick Material Editor Updater for unsetting selected field to true"""
    bl_idname = "object.qmeunset"
    bl_label = "UNSET properties"
    bl_description = "Sets the selected QME properties in the materials of all selected objects to FALSE"

    def execute(self, context):
        qmeUpdate(context, False)
        return {'FINISHED'}

class qmeReset(bpy.types.Operator):
    """Quick Material Editor Resetter"""
    bl_idname = "object.qmereset"
    bl_label = "Reset QME Settings"
    bl_description = "Resets quick material editor properties"

    def execute(self, context):
        matProps = context.scene.saSettings.matQProps
        menuProps = context.scene.saSettings.matQEditor

        for p in dir(matProps):
            if not p.startswith("b_") and not p.startswith("gc_"):
                continue

            a = getattr(matProps, p)
            if type(a) is bool:
                setattr(matProps, p, False)

        for p in dir(menuProps):
            if not p.startswith("b_") and not p.startswith("gc_"):
                continue

            a = getattr(menuProps, p)
            if type(a) is bool:
                setattr(menuProps, p, False)

        return {'FINISHED'}

# property groups
class SAObjectSettings(bpy.types.PropertyGroup):
    """hosts all properties to edit the surface flags of a COL"""
    # used in both
    isCollision: BoolProperty(
        name="Is Collision",
        description="Whether the object can be collided with at all. \n Also determines whether the mesh is invisible in sa2",
        default=False
        )

    solid: BoolProperty(
        name="Solid",
        description="Whether the character can collide with the model",
        default=True
        )

    water: BoolProperty(
        name="Water",
        description="The model will act like water",
        default=False
        )

    cannotLand: BoolProperty(
        name="Cannot land",
        description="Whether you can stand on the model",
        default=False
        )

    diggable: BoolProperty(
        name="Diggable",
        description="Whether the treasure hunter characters can dig on the models surface",
        default=False
        )

    unclimbable: BoolProperty(
        name="Unclimbable",
        description="Whether the treasure hunter characters can climb on the models surface",
        default=False
        )

    hurt: BoolProperty(
        name="Hurt",
        description="The character will take damage when coming in contact with this model",
        default=False
        )

    isVisible: BoolProperty(
        name="isVisible",
        description="Whether the model is Visible (only matters in sa1)",
        default=False
        )

    userFlags: StringProperty(
        name="User flags",
        description="User determined flags (for experiments, otherwise usage is unadvised)",
        default="0"
        )

    # sa2 only

    standOnSlope: BoolProperty(
        name="Stand on slope",
        description="Whether the character wont slide down when standing on stairs",
        default=False
        )

    water2: BoolProperty(
        name="Water 2",
        description="The same as water, but different!",
        default=False
        )

    noShadows: BoolProperty(
        name="No shadows",
        description="No shadows will be displayed on mesh",
        default=False
        )

    noFog: BoolProperty(
        name="No fog",
        description="Disables fog for this object",
        default=False
        )

    unknown24: BoolProperty(
        name="Unknown 24",
        description="No idea what this does",
        default=False
        )

    unknown29: BoolProperty(
        name="Unknown 29",
        description="No idea what this does",
        default=False
        )

    unknown30: BoolProperty(
        name="Unknown 30",
        description="No idea what this does",
        default=False
        )

    # sa1 only

    noFriction: BoolProperty(
        name="No friction",
        description="Whether the model has friction",
        default=False
        )

    noAcceleration: BoolProperty(
        name="no acceleration",
        description="If the acceleration of the character should stay when interacting with the model",
        default=False
        )

    increasedAcceleration: BoolProperty(
        name="Increased acceleration",
        description="Whether the acceleration of the character should be raised when interacting with the model",
        default=False
        )

    footprints: BoolProperty(
        name="Footprints",
        description="The character will leave footprints behind when walking on this models surface",
        default=False
        )

    @classmethod
    def defaultDict(cls) -> dict:
        d = dict()
        d["isCollision"] = False
        d["solid"] = False
        d["water"] = False
        d["cannotLand"] = False
        d["diggable"] = False
        d["unclimbable"] = False
        d["hurt"] = False
        d["isVisible"] = False
        d["userFlags"] = common.hex4(0)

        d["standOnSlope"] = False
        d["water2"] = False
        d["noShadows"] = False
        d["noFog"] = False
        d["unknown24"] = False
        d["unknown29"] = False
        d["unknown30"] = False

        d["noFriction"] = False
        d["noAcceleration"] = False
        d["increasedAcceleration"] = False
        d["footprints"] = False
        return d

    def toDictionary(self) -> dict:
        d = dict()
        d["isCollision"] = self.isCollision
        d["solid"] = self.solid
        d["water"] = self.water
        d["cannotLand"] = self.cannotLand
        d["diggable"] = self.diggable
        d["unclimbable"] = self.unclimbable
        d["hurt"] = self.hurt
        d["isVisible"] = self.isVisible
        d["userFlags"] = self.userFlags

        d["standOnSlope"] = self.standOnSlope
        d["water2"] = self.water2
        d["noShadows"] = self.noShadows
        d["noFog"] = self.noFog
        d["unknown24"] = self.unknown24
        d["unknown29"] = self.unknown29
        d["unknown30"] = self.unknown30

        d["noFriction"] = self.noFriction
        d["noAcceleration"] = self.noAcceleration
        d["increasedAcceleration"] = self.increasedAcceleration
        d["footprints"] = self.footprints

        return d

    def fromDictionary(self, d: dict):
        self.isCollision = d["isCollision"]
        self.solid = d["solid"]
        self.water = d["water"]
        self.cannotLand = d["cannotLand"]
        self.diggable = d["diggable"]
        self.unclimbable = d["unclimbable"]
        self.hurt = d["hurt"]
        self.isVisible = d["isVisible"]
        self.userFlags = d["userFlags"]

        self.standOnSlope = d["standOnSlope"]
        self.water2 = d["water2"]
        self.noShadows = d["noShadows"]
        self.noFog = d["noFog"]
        self.unknown24 = d["unknown24"]
        self.unknown29 = d["unknown29"]
        self.unknown30 = d["unknown30"]

        self.noFriction = d["noFriction"]
        self.noAcceleration = d["noAcceleration"]
        self.increasedAcceleration = d["increasedAcceleration"]
        self.footprints = d["footprints"]

class SASettings(bpy.types.PropertyGroup):
    """Information global to the scene"""

    author: StringProperty(
        name="Author",
        description="The creator of this file",
        default="",
        )

    description: StringProperty(
        name="Description",
        description="A Description of the file contents",
        default="",
        )

    texFileName: StringProperty(
        name="Texture file name",
        description="The name of the texture file specified in the landtable info (lvl format)",
        default=""
        )

    landtableName: StringProperty(
        name="Name",
        description="The label for the landtable in the file. If empty, the filename will be used",
        default=""
        )

    texListPointer: StringProperty(
        name="Texture List Pointer (hex)",
        description="Used for when replacing a stage and its textures",
        default="0"
        )

    drawDistance: FloatProperty(
        name="Draw Distance",
        description="How far the camera has to be away from an object to render (only sa2lvl)",
        default=3000
        )

    doubleSidedCollision: BoolProperty(
        name="Double sided collision",
        description="Enables double sided collision detection. This is supposed to be used as a failsafe for people unexperienced with how normals work",
        default=True
        )

    expandedMatEdit: BoolProperty( name ="Material Quick Edit", default=False)

    expandedSA1obj: BoolProperty( name ="Object SA1 Properties", default=False)

    expandedSA2obj: BoolProperty( name ="Object SA2 Properties", default=False)

class SAMaterialSettings(bpy.types.PropertyGroup):
    """Hosts all of the material data necessary for exporting"""
    # sa1 properties

    b_Diffuse: FloatVectorProperty(
        name = "Diffuse Color",
        description="Color of the material",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        )

    b_Specular: FloatVectorProperty(
        name = "Specular Color",
        description="Color of the Specular",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        )

    b_Ambient : FloatVectorProperty(
        name = "Ambient Color",
        description="Ambient Color (SA2 only)",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        )

    b_Exponent: FloatProperty(
        name = "Specularity",
        description= "Specular Precision on the material",
        default=1.0,
        min = 0, max = 1
        )

    b_TextureID: IntProperty(
        name = "Texture ID",
        description= "ID of the texture in the PVM/GVM to use",
        default=0,
        min = 0
        )

    # flags:
    # mipmap distance multiplier
    b_d_025: BoolProperty(
        name="+ 0.25",
        description="adds 0.25 to the mipmap distance multiplier",
        default=False
        )

    b_d_050: BoolProperty(
        name="+ 0.5",
        description="adds 0.5 to the mipmap distance multiplier",
        default=False
        )

    b_d_100: BoolProperty(
        name="+ 1",
        description="adds 1 to the mipmap distance multiplier",
        default=False
        )

    b_d_200: BoolProperty(
        name="+ 2",
        description="adds 2 to the mipmap distance multiplier",
        default=False
        )

    # texture filtering

    b_use_Anisotropy: BoolProperty(
        name="Anisotropy",
        description="Enable Anisotropy for the texture of the material",
        default=True
        )

    b_texFilter: EnumProperty(
        name="Filter Type",
        description="The texture filter",
        items=( ('POINT', 'Point', "no filtering"),
                ('BILINEAR', 'Bilinear', "Bilinear Filtering"),
                ('TRILINEAR', 'Trilinear', "Trilinear Filtering"),
                ('BLEND', 'Blend', "Bi- and Trilinear Filtering blended together")
            ),
        default='BILINEAR'
        )

    # uv properties

    b_clampV: BoolProperty(
        name="Clamp V",
        description="The V channel of the mesh UVs always stays between 0 and 1",
        default=False
        )

    b_clampU: BoolProperty(
        name="Clamp U",
        description="The U channel of the mesh UVs always stays between 0 and 1",
        default=False
        )

    b_mirrorV: BoolProperty(
        name="Mirror V",
        description="The V channel of the mesh UVs mirrors every time it reaches a multiple of 1",
        default=False
        )

    b_mirrorU: BoolProperty(
        name="Mirror U",
        description="The V channel of the mesh UVs mirrors every time it reaches a multiple of 1",
        default=False
        )

    # general material properties
    b_ignoreSpecular: BoolProperty(
        name="Ignore Specular",
        description="Removes the specularity from the material",
        default=False
        )

    b_useAlpha: BoolProperty(
        name="Use Alpha",
        description="Utilizes the alpha channel of the color and texture to render transparency",
        default=False
        )

    b_srcAlpha: EnumProperty(
        name = "Source Alpha",
        description="Destination Alpha",
        items=( ('ZERO', 'Zero', ""),
                ('ONE', 'One', ""),
                ('OTHER', 'Other', ""),
                ('INV_OTHER', 'Inverted other', ""),
                ('SRC', 'Source', ""),
                ('INV_SRC', 'Inverted source', ""),
                ('DST', 'Destination', ""),
                ('INV_DST', 'Inverted destination', ""),
              ),
        default='SRC'
        )

    b_destAlpha: EnumProperty(
        name = "Destination Alpha",
        description="Destination Alpha",
        items=( ('ZERO', 'Zero', ""),
                ('ONE', 'One', ""),
                ('OTHER', 'Other', ""),
                ('INV_OTHER', 'Inverted other', ""),
                ('SRC', 'Source', ""),
                ('INV_SRC', 'Inverted source', ""),
                ('DST', 'Destination', ""),
                ('INV_DST', 'Inverted destination', ""),
              ),
        default='INV_SRC'
        )

    b_useTexture: BoolProperty(
        name="Use Texture",
        description="Uses the texture references in the properties",
        default=True
        )

    b_useEnv: BoolProperty(
        name="Environment mapping",
        description="Uses normal mapping instead of the uv coordinates, to make the texture face the camera (equivalent to matcaps)",
        default=False
        )

    b_doubleSided: BoolProperty(
        name="Disable Backface culling",
        description="Renders both sides of the mesh",
        default=True
        )

    b_flatShading: BoolProperty(
        name="Flat Shading",
        description="Render without shading",
        default=False
        )

    b_ignoreLighting: BoolProperty(
        name="Ignore Lighting",
        description="Ignores lighting as a whole when rendering",
        default=False
        )

    b_ignoreAmbient: BoolProperty(
        name="Ignore Ambient",
        description="Ignores ambient as a whole when rendering (SA2 Only)",
        default=False
        )

    b_unknown: BoolProperty(
        name="unknown",
        description="to be figured out",
        default = False
        )

    # GC features (parameters)

    gc_shadowStencil: IntProperty(
        name="Shadow Stencil",
        description="shadow stencil",
        min=0, max=0xF,
        default=1
        )

    # texcoord gen

    gc_texMatrixID: EnumProperty(
        name = "Matrix ID",
        description="If gentype is matrix, then this property defines which user defined matrix to use",
        items=( ('MATRIX0', 'Matrix 0', ""),
                ('MATRIX1', 'Matrix 1', ""),
                ('MATRIX2', 'Matrix 2', ""),
                ('MATRIX3', 'Matrix 3', ""),
                ('MATRIX4', 'Matrix 4', ""),
                ('MATRIX5', 'Matrix 5', ""),
                ('MATRIX6', 'Matrix 6', ""),
                ('MATRIX7', 'Matrix 7', ""),
                ('MATRIX8', 'Matrix 8', ""),
                ('MATRIX9', 'Matrix 9', ""),
                ('IDENTITY', 'Identity', "")
            ),
        default='IDENTITY'
        )

    gc_texGenSourceMtx: EnumProperty(
        name = "Generation Source - Matrix",
        description="Which data of the mesh to use when generating the uv coords (Matrix)",
        items=( ('POSITION', 'Position', ""),
                ('NORMAL', 'Normal', ""),
                ('BINORMAL', 'Binormal', ""),
                ('TANGENT', 'Tangent', ""),
                ('TEX0', 'Tex0', ""),
                ('TEX1', 'Tex1', ""),
                ('TEX2', 'Tex2', ""),
                ('TEX3', 'Tex3', ""),
                ('TEX4', 'Tex4', ""),
                ('TEX5', 'Tex5', ""),
                ('TEX6', 'Tex6', ""),
                ('TEX7', 'Tex7', ""),
            ),
        default='TEX0'
        )

    gc_texGenSourceBmp: EnumProperty(
        name = "Generation Source - Bump",
        description="Which uv map of the mesh to use when generating the uv coords (Bump)",
        items=( ('TEXCOORD0', 'TexCoord0', ""),
                ('TEXCOORD1', 'TexCoord1', ""),
                ('TEXCOORD2', 'TexCoord2', ""),
                ('TEXCOORD3', 'TexCoord3', ""),
                ('TEXCOORD4', 'TexCoord4', ""),
                ('TEXCOORD5', 'TexCoord5', ""),
                ('TEXCOORD6', 'TexCoord6', ""),
            ),
        default='TEXCOORD0'
        )

    gc_texGenSourceSRTG: EnumProperty(
        name = "Generation Source - SRTG",
        description="Which color slot of the mesh to use when generating the uv coords (SRTG)",
        items=( ('COLOR0', 'Color0', ""),
                ('COLOR1', 'Color1', ""),
            ),
        default='COLOR0'
        )

    gc_texGenType: EnumProperty(
        name = "Generation Type",
        description="Which function to use when generating the coords",
        items=( ('MTX3X4', 'Matrix 3x4', ""),
                ('MTX2X4', 'Matrix 2x4', ""),
                ('BUMP0', 'Bump 0', ""),
                ('BUMP1', 'Bump 1', ""),
                ('BUMP2', 'Bump 2', ""),
                ('BUMP3', 'Bump 3', ""),
                ('BUMP4', 'Bump 4', ""),
                ('BUMP5', 'Bump 5', ""),
                ('BUMP6', 'Bump 6', ""),
                ('BUMP7', 'Bump 7', ""),
                ('SRTG', 'SRTG', ""),
            ),
        default='MTX2X4'
        )

    gc_texCoordID: EnumProperty(
        name = "Texcoord ID (output slot)",
        description="Determines in which slot the generated coordinates should be saved, so that they can be used",
        items = ( ('TEXCOORD0', 'TexCoord0', ""),
                  ('TEXCOORD1', 'TexCoord1', ""),
                  ('TEXCOORD2', 'TexCoord2', ""),
                  ('TEXCOORD3', 'TexCoord3', ""),
                  ('TEXCOORD4', 'TexCoord4', ""),
                  ('TEXCOORD5', 'TexCoord5', ""),
                  ('TEXCOORD6', 'TexCoord6', ""),
                  ('TEXCOORD7', 'TexCoord7', ""),
                  ('TEXCOORDMAX', 'TexCoordMax', ""),
                  ('TEXCOORDNULL', 'TexCoordNull', ""),
            ),
        default='TEXCOORD0'
        )

    def toDictionary(self) -> dict:
        d = dict()
        d["b_Diffuse"] = self.b_Diffuse
        d["b_Specular"] = self.b_Specular
        d["b_Ambient"] = self.b_Ambient
        d["b_Exponent"] = self.b_Exponent
        d["b_TextureID"] = self.b_TextureID
        d["b_d_025"] = self.b_d_025
        d["b_d_050"] = self.b_d_050
        d["b_d_100"] = self.b_d_100
        d["b_d_200"] = self.b_d_200
        d["b_use_Anisotropy"] = self.b_use_Anisotropy
        d["b_texFilter"] = self.b_texFilter
        d["b_clampV"] = self.b_clampV
        d["b_clampU"] = self.b_clampU
        d["b_mirrorV"] = self.b_mirrorV
        d["b_mirrorU"] = self.b_mirrorU
        d["b_ignoreSpecular"] = self.b_ignoreSpecular
        d["b_useAlpha"] = self.b_useAlpha
        d["b_srcAlpha"] = self.b_srcAlpha
        d["b_destAlpha"] = self.b_destAlpha
        d["b_useTexture"] = self.b_useTexture
        d["b_useEnv"] = self.b_useEnv
        d["b_doubleSided"] = self.b_doubleSided
        d["b_flatShading"] = self.b_flatShading
        d["b_ignoreLighting"] = self.b_ignoreLighting
        d["b_ignoreAmbient"] = self.b_ignoreAmbient
        d["b_unknown"] = self.b_unknown
        d["gc_shadowStencil"] = self.gc_shadowStencil
        d["gc_texMatrixID"] = self.gc_texMatrixID
        d["gc_texGenSourceMtx"] = self.gc_texGenSourceMtx
        d["gc_texGenSourceBmp"] = self.gc_texGenSourceBmp
        d["gc_texGenSourceSRTG"] = self.gc_texGenSourceSRTG
        d["gc_texGenType"] = self.gc_texGenType
        d["gc_texCoordID"] = self.gc_texCoordID
        return d

    def readMatDict(self, d):
        self.b_Diffused = d["b_Diffuse"]
        self.b_Specular = d["b_Specular"]
        self.b_Ambient = d["b_Ambient"]
        self.b_Exponent = d["b_Exponent"]
        self.b_TextureID = d["b_TextureID"]
        self.b_d_025 = d["b_d_025"]
        self.b_d_050 = d["b_d_050"]
        self.b_d_100 = d["b_d_100"]
        self.b_d_200 = d["b_d_200"]
        self.b_use_Anisotropy = d["b_use_Anisotropy"]
        self.b_texFilter = d["b_texFilter"]
        self.b_clampV = d["b_clampV"]
        self.b_clampU = d["b_clampU"]
        self.b_mirrorV = d["b_mirrorV"]
        self.b_mirrorU = d["b_mirrorU"]
        self.b_ignoreSpecular = d["b_ignoreSpecular"]
        self.b_useAlpha = d["b_useAlpha"]
        self.b_srcAlpha = d["b_srcAlpha"]
        self.b_destAlpha = d["b_destAlpha"]
        self.b_useTexture = d["b_useTexture"]
        self.b_useEnv = d["b_useEnv"]
        self.b_doubleSided = d["b_doubleSided"]
        self.b_flatShading = d["b_flatShading"]
        self.b_ignoreLighting = d["b_ignoreLighting"]
        self.b_ignoreAmbient = d["b_ignoreAmbient"]
        self.b_unknown = d["b_unknown"]
        self.gc_shadowStencil = d["gc_shadowStencil"]
        self.gc_texMatrixID = d["gc_texMatrixID"]
        self.gc_texGenSourceMtx = d["gc_texGenSourceMtx"]
        self.gc_texGenSourceBmp = d["gc_texGenSourceBmp"]
        self.gc_texGenSourceSRTG = d["gc_texGenSourceSRTG"]
        self.gc_texGenType = d["gc_texGenType"]
        self.gc_texCoordID = d["gc_texCoordID"]

class SAMaterialPanelSettings(bpy.types.PropertyGroup):
    """Menu settings for the material edit menus determining which menu should be visible"""

    expandedBMipMap: BoolProperty( name="Mipmap Distance Multiplicator", default=False )
    expandedBTexFilter: BoolProperty( name="Texture Filtering", default=False )
    expandedBUV: BoolProperty( name = "UV Properties", default=False )
    expandedBGeneral: BoolProperty( name = "General Properties", default=False )

    expandedGC: BoolProperty( name="SA2B specific", default=False )
    expandedGCTexGen: BoolProperty( name = "Generate texture coords", default=False )

    # Quick material edit properties

    expandedPanel: BoolProperty( name="Material Properties", default=False )

    b_apply_diffuse: BoolProperty(
        name = "Apply diffuse",
        description="Sets the diffuse of all material when pressing 'Update'",
        default=False
        )

    b_apply_specular: BoolProperty(
        name = "Apply specular",
        description="Sets the specular of all material when pressing 'Update'",
        default=False
        )

    b_apply_Ambient: BoolProperty(
        name = "Apply ambient",
        description="Sets the ambient of all material when pressing 'Update'",
        default=False
        )

    b_apply_specularity: BoolProperty(
        name = "Apply specularity",
        description="Sets the specularity of all material when pressing 'Update'",
        default=False
        )

    b_apply_texID: BoolProperty(
        name = "Apply texture ID",
        description="Sets the texture ID of all material when pressing 'Update'",
        default=False
        )

    b_apply_filter: BoolProperty(
        name = "Apply filter type",
        description="Sets the filter type of all material when pressing 'Update'",
        default=False
        )

class SAMeshSettings(bpy.types.PropertyGroup):

    sa2ExportType: EnumProperty(
        name = "SA2 Export Type",
        description = "Determines which vertex data should be written for sa2",
        items = ( ('VC', "Colors", "Only vertex colors are gonna be written"),
                  ('NRM', "Normals", "Only normals are gonna be written"),
                ),
        default = 'VC'
        )

    sa2IndexOffset: IntProperty(
        name = "(SA2) Additional Vertex Offset",
        description = "Additional vertex offset for specific model mods",
        min=0, max = 32767,
        default = 0
    )

# panels

def propAdv(layout, label, prop1, prop1Name, prop2, prop2Name, qe = False):
    split = layout.split(factor=0.6)
    row = split.row()
    row.alignment='LEFT'
    if qe:
        row.prop(prop2, prop2Name, text="")

    row.label(text=label)
    split.prop(prop1, prop1Name, text="")

def drawMaterialPanel(layout, menuProps, matProps, qe = False):

    if qe:
        layout.prop(menuProps, "expandedPanel",
        icon="TRIA_DOWN" if menuProps.expandedPanel else "TRIA_RIGHT",
        emboss = False
        )

    if menuProps.expandedPanel and qe or not qe:
        menu = layout
        menu.alignment = 'RIGHT'

        propAdv(menu, "Diffuse Color:", matProps, "b_Diffuse", menuProps, "b_apply_diffuse", qe)
        propAdv(menu, "Specular Color:", matProps, "b_Specular", menuProps, "b_apply_specular", qe)
        propAdv(menu, "Ambient Color:", matProps, "b_Ambient", menuProps, "b_apply_Ambient", qe)
        propAdv(menu, "Specular Strength:", matProps, "b_Exponent", menuProps, "b_apply_specularity", qe)
        propAdv(menu, "Texture ID:", matProps, "b_TextureID", menuProps, "b_apply_texID", qe)

        #mipmap menu
        box = menu.box()
        box.prop(menuProps, "expandedBMipMap",
            icon="TRIA_DOWN" if menuProps.expandedBMipMap else "TRIA_RIGHT",
            emboss = False
            )

        if menuProps.expandedBMipMap:
            box.prop(matProps, "b_d_025")
            box.prop(matProps, "b_d_050")
            box.prop(matProps, "b_d_100")
            box.prop(matProps, "b_d_200")
            mmdm = 0.25 if matProps.b_d_025 else 0
            mmdm += 0.5 if matProps.b_d_050 else 0
            mmdm += 1 if matProps.b_d_100 else 0
            mmdm += 2 if matProps.b_d_200 else 0
            box.label(text = "Total multiplicator: " + str(mmdm))

        #texture filtering menu
        box = menu.box()
        box.prop(menuProps, "expandedBTexFilter",
            icon="TRIA_DOWN" if menuProps.expandedBTexFilter else "TRIA_RIGHT",
            emboss = False
            )

        if menuProps.expandedBTexFilter:
            box.prop(matProps, "b_use_Anisotropy")
            propAdv(box, "Filter Type:", matProps, "b_texFilter", menuProps, "b_apply_filter", qe)

        # uv properties
        box = menu.box()
        box.prop(menuProps, "expandedBUV",
            icon="TRIA_DOWN" if menuProps.expandedBUV else "TRIA_RIGHT",
            emboss = False
            )

        if menuProps.expandedBUV:
            box.prop(matProps, "b_clampU")
            box.prop(matProps, "b_clampV")
            box.prop(matProps, "b_mirrorV")
            box.prop(matProps, "b_mirrorU")

        box = menu.box()
        box.prop(menuProps, "expandedBGeneral",
            icon="TRIA_DOWN" if menuProps.expandedBGeneral else "TRIA_RIGHT",
            emboss = False
            )

        if menuProps.expandedBGeneral:


            box.prop(matProps, "b_useTexture")
            box.prop(matProps, "b_useEnv")
            box.prop(matProps, "b_useAlpha")
            if matProps.b_useAlpha:
                split = box.split(factor= 0.5)
                split.label(text ="Source Alpha:")
                split.prop(matProps, "b_srcAlpha", text = "")

                split = box.split(factor= 0.5)
                split.label(text ="Destination Alpha:")
                split.prop(matProps, "b_destAlpha", text = "")
            box.prop(matProps, "b_doubleSided")
            box.prop(matProps, "b_ignoreSpecular")
            box.prop(matProps, "b_ignoreLighting")
            box.prop(matProps, "b_ignoreAmbient")
            box.prop(matProps, "b_flatShading")
            box.prop(matProps, "b_unknown")

        box = menu.box()
        box.prop(menuProps, "expandedGC",
            icon="TRIA_DOWN" if menuProps.expandedGC else "TRIA_RIGHT",
            emboss = False
            )

        if menuProps.expandedGC:

            split = box.split(factor=0.6)
            split.label(text = "Shadow Stencil:")
            split.prop(matProps, "gc_shadowStencil", text="")

            box.prop(menuProps, "expandedGCTexGen",
                icon="TRIA_DOWN" if menuProps.expandedGCTexGen else "TRIA_RIGHT",
                emboss = False
                )
            if menuProps.expandedGCTexGen:
                    split = box.split(factor=0.5)
                    split.label(text = "Texcoord ID (output slot)")
                    split.prop(matProps, "gc_texCoordID", text = "")

                    split = box.split(factor=0.5)
                    split.label(text = "Generation Type")
                    split.prop(matProps, "gc_texGenType", text="")

                    if matProps.gc_texGenType[0] == 'M': #matrix
                        split = box.split(factor=0.5)
                        split.label(text = "Matrix ID")
                        split.prop(matProps, "gc_texMatrixID", text="")

                        split = box.split(factor=0.5)
                        split.label(text = "Source")
                        split.prop(matProps, "gc_texGenSourceMtx", text="")

                    elif matProps.gc_texGenType[0] == 'B': # Bump
                        split = box.split(factor=0.5)
                        split.label(text = "Source")
                        split.prop(matProps, "gc_texGenSourceBmp", text="")

                    else: #SRTG
                        split = box.split(factor=0.5)
                        split.label(text = "Source")
                        split.prop(matProps, "gc_texGenSourceSRTG", text="")

class SAObjectPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_saProperties"
    bl_label = "SA Object Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(self, context):
        return context.active_object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        objProps = context.active_object.saSettings
        menuProps = context.scene.saSettings

        layout.prop(objProps, "isCollision")
        if objProps.isCollision:
            layout.prop(objProps, "isVisible")

        # sa1 flags
        box = layout.box()
        box.prop(menuProps, "expandedSA1obj",
            icon="TRIA_DOWN" if menuProps.expandedSA1obj else "TRIA_RIGHT",
            emboss = False
            )

        if menuProps.expandedSA1obj and objProps.isCollision:
            box.prop(objProps, "solid")
            box.prop(objProps, "water")
            box.prop(objProps, "noFriction")
            box.prop(objProps, "noAcceleration")
            box.prop(objProps, "cannotLand")
            box.prop(objProps, "increasedAcceleration")
            box.prop(objProps, "diggable")
            box.prop(objProps, "unclimbable")
            box.prop(objProps, "hurt")

        if menuProps.expandedSA1obj and (not objProps.isCollision or objProps.isCollision and objProps.isVisible):
            box.prop(objProps, "footprints")

        # sa2 flags

        box = layout.box()
        box.prop(menuProps, "expandedSA2obj",
            icon="TRIA_DOWN" if menuProps.expandedSA2obj else "TRIA_RIGHT",
            emboss = False
            )

        if menuProps.expandedSA2obj and objProps.isCollision:
            box.prop(objProps, "solid")
            box.prop(objProps, "water")
            box.prop(objProps, "standOnSlope")
            box.prop(objProps, "diggable")
            box.prop(objProps, "unclimbable")
            box.prop(objProps, "hurt")
            box.prop(objProps, "cannotLand")
            box.prop(objProps, "water2")

        if menuProps.expandedSA2obj and (not objProps.isCollision or objProps.isCollision and objProps.isVisible):
            box.prop(objProps, "noShadows")
            box.prop(objProps, "noFog")

        if menuProps.expandedSA2obj and objProps.isCollision:
            box.separator()
            box.label(text="Experimental")
            box.prop(objProps, "unknown24")
            box.prop(objProps, "unknown29")
            box.prop(objProps, "unknown30")

        layout.separator()
        layout.label(text="Experimental")
        split = layout.split()

        split = layout.split(factor=0.4)
        split.label(text="User flags (hex):")
        split = split.split(factor=0.15)
        split.alignment='RIGHT'
        split.label(text="0x")
        split.prop(objProps, "userFlags", text="")

class SAMeshPanel(bpy.types.Panel):
    bl_idname = "MESH_PT_saProperties"
    bl_label = "SA Mesh Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(self, context):
        return context.active_object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        meshprops = context.active_object.data.saSettings

        split = layout.split(factor=0.4)
        split.label(text="SA2 Export Type")
        split.prop(meshprops, "sa2ExportType", text = "")
        split = layout.split(factor=0.4)
        split.label(text="(SA2) Additional Vertex Offset")
        split.prop(meshprops, "sa2IndexOffset", text = "")


class SAMaterialPanel(bpy.types.Panel):
    bl_idname = "MATERIAL_PT_saProperties"
    bl_label = "SA Material Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"


    @classmethod
    def poll(cls, context):
        return (context.active_object.active_material is not None)

    def draw(self, context):
        layout = self.layout
        menuProps = context.scene.saSettings.matEditor
        matProps = context.active_object.active_material.saSettings

        drawMaterialPanel(layout, menuProps, matProps)

class SAScenePanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_saProperties"
    bl_label = "SA file info"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.saSettings

        layout.prop(settings, "author")
        layout.prop(settings, "description")

        layout.separator(factor=2)
        layout.label(text="Landtable data")
        layout.prop(settings, "landtableName")
        layout.prop(settings, "texFileName")

        split = layout.split(factor=0.5)
        split.label(text="Draw Distance:")
        split.prop(settings, "drawDistance", text="")

        split = layout.split(factor=0.3)
        split.label(text="TexListPtr (hex):")
        split = split.split(factor=0.1)
        split.alignment='RIGHT'
        split.label(text="0x")
        split.prop(settings, "texListPointer", text="")

        layout.prop(settings, "doubleSidedCollision")

class SA3DPanel(bpy.types.Panel):
    bl_idname = 'MESH_PT_satools'
    bl_label = 'SA Tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def draw(self, context):
        layout = self.layout

        settings = context.scene.saSettings

        box = layout.box()

        box.prop(settings, "expandedMatEdit",
            icon="TRIA_DOWN" if settings.expandedMatEdit else "TRIA_RIGHT",
            emboss = False
            )

        if settings.expandedMatEdit:
            box.operator(qmeUpdateSet.bl_idname)
            box.operator(qmeUpdateUnset.bl_idname)
            box.operator(qmeReset.bl_idname)
            drawMaterialPanel(box, settings.matQEditor, settings.matQProps, qe=True)

        layout.operator(ArmatureFromObjects.bl_idname)
        layout.operator(StrippifyTest.bl_idname)


def menu_func_exportsa(self, context):
    self.layout.menu("TOPBAR_MT_SA_export")

def menu_func_importsa(self, context):
    self.layout.operator(ImportMDL.bl_idname)
    self.layout.operator(ImportLVL.bl_idname)

classes = (
    TOPBAR_MT_SA_export,
    ExportSA1MDL,
    ExportSA2MDL,
    ExportSA2BMDL,
    ExportSA1LVL,
    ExportSA2LVL,
    ExportSA2BLVL,
    ImportMDL,
    ImportLVL,

    StrippifyTest,
    ArmatureFromObjects,
    qmeReset,
    qmeUpdateSet,
    qmeUpdateUnset,

    SAObjectSettings,
    SASettings,
    SAMaterialSettings,
    SAMaterialPanelSettings,
    SAMeshSettings,

    SAObjectPanel,
    SAMaterialPanel,
    SAScenePanel,
    SA3DPanel,
    SAMeshPanel,
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    SASettings.matEditor = bpy.props.PointerProperty(type=SAMaterialPanelSettings)
    SASettings.matQEditor = bpy.props.PointerProperty(type=SAMaterialPanelSettings)
    SASettings.matQProps = bpy.props.PointerProperty(type=SAMaterialSettings)

    bpy.types.Scene.saSettings = bpy.props.PointerProperty(type=SASettings)
    bpy.types.Object.saSettings = bpy.props.PointerProperty(type=SAObjectSettings)
    bpy.types.Material.saSettings = bpy.props.PointerProperty(type=SAMaterialSettings)
    bpy.types.Mesh.saSettings = bpy.props.PointerProperty(type=SAMeshSettings)

    bpy.types.TOPBAR_MT_file_export.append(menu_func_exportsa)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_importsa)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_exportsa)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_importsa)

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()