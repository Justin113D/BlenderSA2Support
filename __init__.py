# meta info
bl_info = {
    "name": "SA2 Model Formats support",
    "author": "Justin113D",
    "version": (0,0,1),
    "blender": (2, 80, 0),
    "location": "File > Import/Export",
    "description": "Import/Exporter for the SA2 Models Formats. For any questions, contact me via Discord: Justin113D#1927",
    "warning": "",
    "wiki_url": "",
    "support": 'COMMUNITY',
    "category": "Import-Export"}

if "bpy" in locals():
    import importlib
    if "export_mdl" in locals():
        importlib.reload(export_mdl)
    if "export_lvl" in locals():
        importlib.reload(export_lvl)
    if "format_BASIC" in locals():
        importlib.reload(format_BASIC)
    if "format_GC" in locals():
        importlib.reload(format_GC)
    if "strippifier" in locals():
        importlib.reload(strippifier)   
    if "fileWriter" in locals():
        importlib.reload(fileWriter)
    if "enums" in locals():
        importlib.reload(enums)
    if "common" in locals():
        importlib.reload(common)

import bpy
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
from bpy_extras.io_utils import (
    #ImportHelper,
    ExportHelper,
    orientation_helper,
    path_reference_mode,
    axis_conversion,
    )

class TOPBAR_MT_SA_export(bpy.types.Menu):
    bl_label = "SA Formats"
    #bl_idname = "export_scene.samenu"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Export as...")
        layout.operator("export_scene.sa1mdl")
        #layout.label(text="SA2 model (.sa2mdl)")
        #layout.operator("export_scene.sa2mdl")
        layout.label(text="SA2B model (.sa2bmdl)")
        #layout.operator("export_scene.sa2bmdl")
        layout.operator("export_scene.sa1lvl")
        layout.label(text="SA2B level (.sa2blvl)")
        #layout.operator("export_scene.sa2blvl")

@orientation_helper(axis_forward='Z', axis_up='Y')    
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
        default = True,
        )

    def execute(self, context):
        from . import export_mdl
        from mathutils import Matrix
        keywords = self.as_keywords(ignore=("global_scale",
                                    "check_existing",
                                    "filter_glob",
                                    "axis_forward",
                                    "axis_up"
                                    ))
        
        global_matrix = (Matrix.Scale(self.global_scale, 4) @
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())
        
        keywords["global_matrix"] = global_matrix
        keywords["export_format"] = 'SA1MDL'
        return export_mdl.write(context, **keywords)

@orientation_helper(axis_forward='Z', axis_up='Y')    
class ExportSA2MDL(bpy.types.Operator, ExportHelper):
    """Export Objects into an SA2 model file"""
    bl_idname = "export_scene.sa2mdl"
    bl_label = "SA2 model (.sa2mdl)"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".sa2bmdl"

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
        default = True,
        )

    def execute(self, context):
        from . import export_mdl
        from mathutils import Matrix
        keywords = self.as_keywords(ignore=("global_scale",
                                    "check_existing",
                                    "filter_glob",
                                    "axis_forward",
                                    "axis_up"
                                    ))
        
        global_matrix = (Matrix.Scale(self.global_scale, 4) @
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())
        
        keywords["global_matrix"] = global_matrix
        keywords["export_format"] = 'SA2MDL'
        return export_mdl.write(context, **keywords)

@orientation_helper(axis_forward='Z', axis_up='Y')    
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
        default = True,
        )

    def execute(self, context):
        from . import export_mdl
        from mathutils import Matrix
        keywords = self.as_keywords(ignore=("global_scale",
                                    "check_existing",
                                    "filter_glob",
                                    "axis_forward",
                                    "axis_up"
                                    ))
        
        global_matrix = (Matrix.Scale(self.global_scale, 4) @
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())
        
        keywords["global_matrix"] = global_matrix
        keywords["export_format"] = 'SA2BMDL'
        return export_mdl.write(context, **keywords)

@orientation_helper(axis_forward='Z', axis_up='Y')  
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
        default = True,
        )
    
    def execute(self, context):
        from . import export_lvl
        from mathutils import Matrix
        keywords = self.as_keywords(ignore=("global_scale",
                                    "check_existing",
                                    "filter_glob",
                                    "axis_forward",
                                    "axis_up",
                                    ))
        
        global_matrix = (Matrix.Scale(self.global_scale, 4) @
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())
        
        keywords["global_matrix"] = global_matrix
        keywords["export_format"] = 'SA1LVL'
        return export_lvl.write(context, **keywords)

@orientation_helper(axis_forward='Z', axis_up='Y')  
class ExportSA2BLVL(bpy.types.Operator, ExportHelper):
    """Export scene into an SA2B level file"""
    bl_idname = "export_scene.sa2blvl"
    bl_label = "SA2B level (.sa2blvl)"
    bl_options = {'PRESET', 'UNDO'}

    filter_glob: StringProperty(
        default="*.sa2blvl;",
        options={'HIDDEN'},
        )

    global_scale: FloatProperty(
        name="Scale",
        min=0.01, max=1000.0,
        default=1.0,
        )

    apply_modifs: BoolProperty(
        name="Apply Modifiers",
        description="Apply active viewport modifiers",
        default=True,
        )

    console_debug_output: BoolProperty(
        name = "Console Output",
        description = "Shows exporting progress in Console (Slows down Exporting Immensely)",
        default = True,
        )
    
    def execute(self, context):
        from . import export_lvl
        from mathutils import Matrix
        keywords = self.as_keywords(ignore=("global_scale",
                                    "check_existing",
                                    "filter_glob",
                                    "axis_forward",
                                    "axis_up",
                                    ))
        
        global_matrix = (Matrix.Scale(self.global_scale, 4) @
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())
        
        keywords["global_matrix"] = global_matrix
        keywords["export_format"] = 'SA2BLVL'
        return export_lvl.write(context, **keywords)

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
        import os
        os.system("cls")
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

#property groups
class SAObjectSettings(bpy.types.PropertyGroup):
    """Menu to edit the surface flags of a COL"""
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

    cannotLand: BoolProperty(
        name="Cannot land",
        description="Whether you can stand on the model",
        default=False
        )

    increasedAcceleration: BoolProperty(
        name="Increased acceleration",
        description="Whether the acceleration of the character should be raised when interacting with the model",
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

    footprints: BoolProperty(
        name="Footprints",
        description="The character will leave footprints behind when walking on this models surface",
        default=False
        )

    isVisible: BoolProperty(
        name="isVisible",
        description="Whether the model is Visible (only matters in sa1)",
        default=False
        )

    userFlags: IntProperty(
        name="User flags",
        description="User determined flags (for experiments, otherwise usage is unadvised)",
        default=0
        )

class SASettings(bpy.types.PropertyGroup):

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


    expandedBASIC: BoolProperty( name="SA1 (BASIC) Material Properties", default=False )
    expandedBMipMap: BoolProperty( name="Mipmap Distance Multiplicator", default=False )
    expandedBTexFilter: BoolProperty( name="Texture Filtering", default=False )
    expandedBUV: BoolProperty( name = "UV Properties", default=False )
    expandedBGeneral: BoolProperty( name = "General Properties", default=False )

    expandedGC: BoolProperty( name="SA2B (GC) Material Properties", default=False )
    expandedGCIndexAttr: BoolProperty( name = "Data to save", default=False )
    expandedGCTex: BoolProperty( name = "Texture parameters", default=False )
    expandedGCTexGen: BoolProperty( name = "Generate texture coords", default=False )
    expandedGCAlpha: BoolProperty( name = "Use alpha", default=False )

    expandedChunk: BoolProperty( default=False )  

class SAMaterialSettings(bpy.types.PropertyGroup):
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

    b_Exponent: FloatProperty(
        name = "Specularity",
        description= "Specular Precision on the material",
        default=11.0,
        min = 0, max = 11
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
        items=( ('NONE', 'None', "No filtering"),
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
                ('INV_SRC', 'Inverter source', ""),
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
                ('INV_SRC', 'Inverter source', ""),
                ('DST', 'Destination', ""),
                ('INV_DST', 'Inverted destination', ""),
              ),
        default='DST'
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

    # GC material settings (parameters)

    # Index attribute parameters (enabling certain data for export)
    gc_hasNormal: BoolProperty(
        name = "Export normals",
        description="If ticked, the normals of the mesh will be saved into the file",
        default= False
        )
    
    gc_hasColor: BoolProperty(
        name = "Export vertex colors",
        description="If ticked, the vertex colors of the mesh will be saved into the file",
        default= True
        )

    gc_hasUV: BoolProperty(
        name = "Export uv maps",
        description="If ticked, the uv maps of the mesh will be saved into the file",
        default= True
        )

    # ambient color

    gc_Diffuse: FloatVectorProperty(
        name = "Diffuse Color",
        description="Color of the material",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),       
        )
    
    # texture properties
    gc_UseTexture: BoolProperty(
        name = "Use texture",
        description="Whether a texture should be used",
        default=True
        )
    
    gc_TextureID: IntProperty(
        name = "Texture ID",
        description="ID of the texture in the PAK to use",
        default=0
        )
    
    gc_clampV: BoolProperty(
        name="Clamp V",
        description="The V channel of the mesh UVs always stays between 0 and 1",
        default=False
        )

    gc_clampU: BoolProperty(
        name="Clamp U",
        description="The U channel of the mesh UVs always stays between 0 and 1",
        default=False
        )

    gc_mirrorV: BoolProperty(
        name="Mirror V",
        description="The V channel of the mesh UVs mirrors every time it reaches a multiple of 1",
        default=False
        )

    gc_mirrorU: BoolProperty(
        name="Mirror U",
        description="The V channel of the mesh UVs mirrors every time it reaches a multiple of 1",
        default=False
        )

    # texcoord gen

    gc_genTexCoords: BoolProperty(
        name="Generate Texture Coordinates",
        description="Whether texture coordinates should be generated using specific parameters",
        default=False
        )

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
        default='POSITION'
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
        default='MTX3X4'
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

    #alpha blending

    gc_useAlpha: BoolProperty(
        name = "Use alpha",
        default=False
        )

    gc_srcAlpha: EnumProperty(
        name = "Source alpha",
        description= "Source alpha",
        items=( ('ZERO', 'Zero', ""),
                ('ONE', 'One', ""),
                ('SRC_COL', 'Source Color', ""),
                ('INV_SRC_COL', 'Invertex Source Color', ""),
                ('SRC', 'Source', ""),
                ('INV_SRC', 'Inverter source', ""),
                ('DST', 'Destination', ""),
                ('INV_DST', 'Inverted destination', "")
            ),
        default='SRC'
        )

    gc_destAlpha: EnumProperty(
        name = "Destination alpha",
        description= "Destination alpha",
        items=( ('ZERO', 'Zero', ""),
                ('ONE', 'One', ""),
                ('SRC_COL', 'Source Color', ""),
                ('INV_SRC_COL', 'Invertex Source Color', ""),
                ('SRC', 'Source', ""),
                ('INV_SRC', 'Inverter source', ""),
                ('DST', 'Destination', ""),
                ('INV_DST', 'Inverted destination', "")
            ),
        default='DST'
        )    

#panels
class SAObjectPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_saProperties"
    bl_label = "SA Material Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(self, context):
        return context.active_object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        objProps = context.active_object.saSettings

        layout.prop(objProps, "isCollision")

        if objProps.isCollision:
            box = layout.box()
            box.label(text="Collision Surface Flags")

            box.prop(objProps, "isVisible")
            box.prop(objProps, "solid")
            box.prop(objProps, "water")

            box.separator(factor=0.5)
            box.label(text="Working in sa1 only:")
            box.prop(objProps, "noFriction")
            box.prop(objProps, "noAcceleration")
            box.prop(objProps, "cannotLand")
            box.prop(objProps, "increasedAcceleration")
            box.prop(objProps, "diggable")
            box.prop(objProps, "unclimbable")
            box.prop(objProps, "hurt")
            box.prop(objProps, "footprints")
        
        layout.separator()
        layout.label(text="Experimental")
        split = layout.split()
        split.label(text="User flags")
        split.prop(objProps, "userFlags", text="")

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
        menuProps = context.scene.saSettings
        matProps = context.active_object.active_material.saSettings

        layout.prop(menuProps, "expandedBASIC",
            icon="TRIA_DOWN" if menuProps.expandedBASIC else "TRIA_RIGHT",
            emboss = False
            )

        if menuProps.expandedBASIC:
            menu = layout.column()
            menu.alignment = 'RIGHT'

            row = menu.row()   
            row.prop(matProps, "b_Diffuse")

            row = menu.row()   
            row.prop(matProps, "b_Specular")
            
            row = menu.row()
            row.label(text ="Specular Strength:")           
            col = row.column()
            col.alignment = 'RIGHT'
            col.prop(matProps, "b_Exponent", text = "")

            row = menu.row()
            row.label(text ="Texture ID:")           
            col = row.column()
            col.alignment = 'RIGHT'
            col.prop(matProps, "b_TextureID", text = "")
            
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
                split = box.split(factor= 0.4)
                split.label(text="Filter Type:")
                split.prop(matProps, "b_texFilter", text="")

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
                box.prop(matProps, "b_ignoreSpecular")
                box.prop(matProps, "b_useAlpha")
                if matProps.b_useAlpha:
                    split = box.split(factor= 0.5)
                    split.label(text ="Source Alpha:")  
                    split.prop(matProps, "b_srcAlpha", text = "")

                    split = box.split(factor= 0.5)
                    split.label(text ="Destination Alpha:")
                    split.prop(matProps, "b_destAlpha", text = "")

                box.prop(matProps, "b_useTexture")
                box.prop(matProps, "b_useEnv")
                box.prop(matProps, "b_doubleSided")
                box.prop(matProps, "b_flatShading")
                box.prop(matProps, "b_ignoreLighting")

        layout.prop(menuProps, "expandedGC",
            icon="TRIA_DOWN" if menuProps.expandedGC else "TRIA_RIGHT",
            emboss = False
            )

        if menuProps.expandedGC:
            menu = layout.column()
            menu.alignment = 'RIGHT'

            row = menu.row()   
            row.prop(matProps, "gc_Diffuse")

            box = menu.box()
            box.prop(menuProps, "expandedGCIndexAttr",
                icon="TRIA_DOWN" if menuProps.expandedGCIndexAttr else "TRIA_RIGHT",
                emboss = False
                )

            if menuProps.expandedGCIndexAttr:
                box.prop(matProps, "gc_hasNormal")
                box.prop(matProps, "gc_hasColor")
                box.prop(matProps, "gc_hasUV")

            box = menu.box()
            row = box.row()
            row.prop(matProps, "gc_UseTexture", text="")
            if matProps.gc_UseTexture:
                row.prop(menuProps, "expandedGCTex",
                    icon="TRIA_DOWN" if menuProps.expandedGCTex else "TRIA_RIGHT",
                    emboss = False
                    )

                if menuProps.expandedGCTex:
                    split = box.split(factor=0.7)
                    split.label(text="Texture ID")
                    split.prop(matProps, "gc_TextureID", text="")
                    box.prop(matProps, "gc_clampV")
                    box.prop(matProps, "gc_clampU")
                    box.prop(matProps, "gc_mirrorV")
                    box.prop(matProps, "gc_mirrorU")
            else:
                row.prop(menuProps, "expandedGCTex",
                    icon="BLANK1", emboss = False
                    )
            
            box = menu.box()
            row = box.row()
            row.prop(matProps, "gc_genTexCoords", text="")
            if matProps.gc_genTexCoords:
                row.prop(menuProps, "expandedGCTexGen",
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
            else:
                row.prop(menuProps, "expandedGCTexGen",
                    icon="BLANK1", emboss = False
                    )

            box = menu.box()
            row = box.row()
            row.prop(matProps, "gc_useAlpha", text="")
            if matProps.gc_useAlpha:
                row.prop(menuProps, "expandedGCAlpha",
                    icon="TRIA_DOWN" if menuProps.expandedGCAlpha else "TRIA_RIGHT",
                    emboss = False
                    )

                if menuProps.expandedGCAlpha:
                    split = box.split(factor=0.5)
                    split.label(text = "Source Alpha")
                    split.prop(matProps, "gc_srcAlpha", text = "")

                    split = box.split(factor=0.5)
                    split.label(text = "Destination Alpha")
                    split.prop(matProps, "gc_destAlpha", text = "")
            else:
                row.prop(menuProps, "expandedGCAlpha",
                    icon="BLANK1", emboss = False
                    )

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

def menu_func_strippifyTest(self, context):
    self.layout.operator(StrippifyTest.bl_idname)

def menu_func_exportsa(self, context):
    self.layout.menu("TOPBAR_MT_SA_export")

classes = (
    TOPBAR_MT_SA_export,
    ExportSA1MDL,
    ExportSA2MDL,
    ExportSA2BMDL,
    ExportSA1LVL,
    ExportSA2BLVL,
    StrippifyTest,
    SAObjectSettings,
    SASettings,
    SAMaterialSettings,
    SAObjectPanel,
    SAMaterialPanel,
    SAScenePanel
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.TOPBAR_MT_file_export.append(menu_func_exportsa)
    bpy.types.VIEW3D_MT_object.append(menu_func_strippifyTest)

    bpy.types.Scene.saSettings = bpy.props.PointerProperty(type=SASettings)
    bpy.types.Object.saSettings = bpy.props.PointerProperty(type=SAObjectSettings)
    bpy.types.Material.saSettings = bpy.props.PointerProperty(type=SAMaterialSettings)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_exportsa)
    bpy.types.VIEW3D_MT_object.remove(menu_func_strippifyTest)

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
   register()