import bpy
import json
import os
import blf
import bpy_extras
from bpy_extras.io_utils import ExportHelper

draw_handle_px = None

def draw_callback_px(self, context):
    obj = getattr(context, "active_object", None)
    if not obj or obj.type != 'ARMATURE':
        return
        
    if not obj.data.get("show_custom_names", False):
        return

    font_id = 0
    size = obj.data.get("custom_text_size", 20)
    blf.size(font_id, size)
    blf.color(font_id, 1.0, 1.0, 1.0, 1.0) # White text

    region = getattr(context, "region", None)
    rv3d = getattr(context, "region_data", None)

    if not region or not rv3d:
        return

    for bone in obj.data.bones:
        world_pos = obj.matrix_world @ bone.head_local
        coord = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, world_pos)
        
        if coord:
            blf.position(font_id, coord.x, coord.y, 0)
            blf.draw(font_id, bone.name)

bl_info = {
    "name": "Extract Bone Names",
    "author": "Assistant",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Tool",
    "description": "Export the bone names of the active armature to a bone.js file",
    "category": "Import-Export",
}

class EXPORT_OT_bone_names(bpy.types.Operator, ExportHelper):
    """Export bone names of active armature to a JS file"""
    bl_idname = "export.bone_names"
    bl_label = "Export Bone Names"
    
    # ExportHelper mixin class uses this
    filename_ext = ".js"

    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for exporting the file",
        maxlen=1024,
        default="bone.js",
    )

    filter_glob: bpy.props.StringProperty(
        default="*.js",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        obj = context.active_object
        
        if not obj or obj.type != 'ARMATURE':
            self.report({'WARNING'}, "Please select an Armature object.")
            return {'CANCELLED'}

        # Build bone tree recursively
        def build_bone_tree(bone):
            tree = {"name": bone.name, "children": []}
            for child in bone.children:
                tree["children"].append(build_bone_tree(child))
            return tree

        # Find root bones and build the hierarchy
        bone_tree = []
        for bone in obj.data.bones:
            if not bone.parent:
                bone_tree.append(build_bone_tree(bone))
        
        # Create a Javascript variable structure
        js_content = f"const boneTree = {json.dumps(bone_tree, indent=4)};\n"
        js_content += "export default boneTree;\n"

        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(js_content)
            self.report({'INFO'}, f"Successfully exported bone tree to {self.filepath}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to write file: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class VIEW3D_PT_extract_bone_names(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Extract Bone Names"
    bl_idname = "VIEW3D_PT_extract_bone_names"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        
        if obj and obj.type == 'ARMATURE':
            layout.label(text=f"Active: {obj.name}")
            layout.label(text=f"Bones: {len(obj.data.bones)}")
            
            # Checkbox to toggle showing bone names in the viewport
            layout.prop(obj.data, "show_custom_names", text="Show Bone Names in Scene")
            if obj.data.get("show_custom_names", False):
                layout.prop(obj.data, "custom_text_size", text="Text Size")
            
            layout.separator()
            
            # Button to call the export operator
            row = layout.row()
            row.scale_y = 1.5
            row.operator("export.bone_names", text="Export to bone.js", icon='EXPORT')
        else:
            layout.label(text="Select an Armature", icon='INFO')
            layout.label(text="to see options.")

classes = (
    EXPORT_OT_bone_names,
    VIEW3D_PT_extract_bone_names,
)

def register():
    bpy.types.Armature.show_custom_names = bpy.props.BoolProperty(
        name="Show Custom Names",
        description="Show custom bone names in viewport",
        default=False
    )
    bpy.types.Armature.custom_text_size = bpy.props.IntProperty(
        name="Text Size",
        description="Text size of custom bone names",
        default=20,
        min=8,
        max=100
    )

    for cls in classes:
        bpy.utils.register_class(cls)
        
    global draw_handle_px
    if draw_handle_px is None:
        draw_handle_px = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (None, bpy.context), 'WINDOW', 'POST_PIXEL')

def unregister():
    global draw_handle_px
    if draw_handle_px is not None:
        bpy.types.SpaceView3D.draw_handler_remove(draw_handle_px, 'WINDOW')
        draw_handle_px = None
    
    if hasattr(bpy.types.Armature, "show_custom_names"):
        del bpy.types.Armature.show_custom_names
    if hasattr(bpy.types.Armature, "custom_text_size"):
        del bpy.types.Armature.custom_text_size

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
