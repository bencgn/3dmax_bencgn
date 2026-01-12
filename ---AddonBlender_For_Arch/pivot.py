import bpy
import mathutils
from bpy.types import Operator, Panel
from bpy.props import EnumProperty


bl_info = {
    "name": "Pivot Point Tools",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Pivot Tools",
    "description": "Set pivot point to center or bottom center of mesh",
    "category": "Object",
}


class OBJECT_OT_set_pivot_center(Operator):
    """Set pivot point to center of mesh"""
    bl_idname = "object.set_pivot_center"
    bl_label = "Center Pivot"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and context.mode == 'OBJECT'

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                # Save current cursor location
                saved_location = context.scene.cursor.location.copy()
                
                # Set 3D cursor to object's geometry center
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                
                # Restore cursor location
                context.scene.cursor.location = saved_location
                
        self.report({'INFO'}, "Pivot set to center")
        return {'FINISHED'}


class OBJECT_OT_set_pivot_bottom(Operator):
    """Set pivot point to bottom center of mesh"""
    bl_idname = "object.set_pivot_bottom"
    bl_label = "Bottom Center Pivot"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and context.mode == 'OBJECT'

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                # Save current cursor location
                saved_location = context.scene.cursor.location.copy()
                
                # Get the bounding box in world space
                bbox_corners = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
                
                # Find the minimum Z value (bottom)
                min_z = min([corner.z for corner in bbox_corners])
                
                # Calculate center X and Y
                center_x = sum([corner.x for corner in bbox_corners]) / 8
                center_y = sum([corner.y for corner in bbox_corners]) / 8
                
                # Set 3D cursor to bottom center
                context.scene.cursor.location = (center_x, center_y, min_z)
                
                # Set origin to 3D cursor
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                
                # Restore cursor location
                context.scene.cursor.location = saved_location
                
        self.report({'INFO'}, "Pivot set to bottom center")
        return {'FINISHED'}


class OBJECT_OT_cursor_to_origin(Operator):
    """Set 3D cursor to world origin (0, 0, 0)"""
    bl_idname = "object.cursor_to_origin"
    bl_label = "Cursor to Origin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.cursor.location = (0, 0, 0)
        self.report({'INFO'}, "Cursor set to origin (0, 0, 0)")
        return {'FINISHED'}


class VIEW3D_PT_pivot_tools(Panel):
    """Panel for pivot point tools"""
    bl_label = "Pivot Tools"
    bl_idname = "VIEW3D_PT_pivot_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Pivot Tools'

    def draw(self, context):
        layout = self.layout
        
        # Title
        layout.label(text="Set Pivot Point:", icon='PIVOT_BOUNDBOX')
        
        # Buttons
        col = layout.column(align=True)
        col.scale_y = 1.5
        
        # Center pivot button
        row = col.row()
        row.operator("object.set_pivot_center", text="Center Pivot", icon='PIVOT_MEDIAN')
        
        # Bottom center pivot button
        row = col.row()
        row.operator("object.set_pivot_bottom", text="Bottom Center Pivot", icon='PIVOT_CURSOR')
        
        # Separator
        layout.separator()
        
        # Cursor to origin button
        layout.operator("object.cursor_to_origin", text="Cursor to Origin (0,0,0)", icon='CURSOR')
        
        # Info
        layout.separator()
        box = layout.box()
        box.label(text="Select mesh objects first", icon='INFO')


# Registration
classes = (
    OBJECT_OT_set_pivot_center,
    OBJECT_OT_set_pivot_bottom,
    OBJECT_OT_cursor_to_origin,
    VIEW3D_PT_pivot_tools,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
