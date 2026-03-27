import bpy

bl_info = {
    "name": "Pose to Rest Converter",
    "author": "Assistant",
    "version": (1, 2),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Tool",
    "description": "Clear pose to return to rest, and insert Rest Keyframes",
    "category": "Rigging",
}

class POSE_OT_pose_to_rest(bpy.types.Operator):
    """Clear all bone transforms to return the armature and mesh to the rest pose"""
    bl_idname = "pose.clear_to_rest"
    bl_label = "Go to Rest Pose"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        armobj = context.active_object

        # Đảm bảo vào Pose Mode để clear transform
        if context.object.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        
        # Chọn toàn bộ xương và xóa transform (trả về Rest)
        # Vì ta KHÔNG can thiệp vào Mesh, Mesh sẽ tự động đi theo xương và về Rest theo.
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()
        
        bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, "Cleared pose. Armature and Mesh returned to Rest.")
        return {'FINISHED'}


class POSE_OT_insert_rest_frame_zero(bpy.types.Operator):
    """Clear transforms and insert a LocRotScale Keyframe at Frame 0 for all bones"""
    bl_idname = "pose.insert_rest_keyframe_zero"
    bl_label = "Insert Rest at Frame 0"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        armobj = context.active_object

        # Đảm bảo vào Pose Mode
        if context.object.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
            
        # Chọn toàn bộ xương
        bpy.ops.pose.select_all(action='SELECT')
        
        # Xóa transform
        bpy.ops.pose.transforms_clear()
        
        # Tiến tới Frame 0
        bpy.context.scene.frame_set(0)
        
        # Insert Keyframe 
        bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
            
        bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, "Inserted Rest Keyframe at Frame 0.")
        return {'FINISHED'}


class VIEW3D_PT_pose_to_rest(bpy.types.Panel):
    """Creates a Panel in the View3D Tool Sidebar"""
    bl_label = "Pose to Rest Tool"
    bl_idname = "VIEW3D_PT_pose_to_rest"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        
        if obj and obj.type == 'ARMATURE':
            # Nút 1: Đưa xương và mesh về Rest
            box1 = layout.box()
            box1.label(text="1. Return Mesh and Bones to Rest")
            row1 = box1.row()
            row1.scale_y = 1.3
            row1.operator("pose.clear_to_rest", text="Go to Rest Pose", icon='OUTLINER_OB_ARMATURE')
            
            layout.separator()
            
            # Nút 2: Insert Rest tại Frame 0
            box2 = layout.box()
            box2.label(text="2. Add Rest Pose Keyframe")
            row2 = box2.row()
            row2.scale_y = 1.3
            row2.operator("pose.insert_rest_keyframe_zero", text="Insert Rest at Frame 0", icon='KEYINGSET')
        else:
            layout.label(text="Select an Armature Object", icon='INFO')


classes = (
    POSE_OT_pose_to_rest,
    POSE_OT_insert_rest_frame_zero,
    VIEW3D_PT_pose_to_rest,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
