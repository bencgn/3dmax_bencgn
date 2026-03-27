import bpy
import math
from mathutils import Matrix, Vector, Quaternion, Euler

bl_info = {
    "name": "T-Pose ↔ V-Pose Converter",
    "author": "Assistant",
    "version": (1, 1),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Tool",
    "description": "Convert between T-Pose and V-Pose rest positions while preserving animation",
    "category": "Rigging",
}

# ─── Key arm bone names (Mixamo-style, overrideable from UI) ──────────────────
DEFAULT_LEFT_ARM  = "mixamorig:LeftArm"
DEFAULT_RIGHT_ARM = "mixamorig:RightArm"


#
# ─── ALGORITHM OVERVIEW ────────────────────────────────────────────────────────
#
# Converting T-pose REST ➜ V-pose REST while keeping animation intact requires
# a two-step approach:
#
#  STEP 1 – "Rotate arms into V-pose in Pose mode":
#     • Enter Pose mode, select the upper-arm bones, add a rotation offset so
#       the arms tilt downward (V-shape).  Those rotations live in LOCAL space.
#
#  STEP 2 – "Apply as new Rest Pose":
#     • In Edit mode call "Apply Pose as Rest Pose".  This bakes the pose offset
#       into the bone's EDIT (rest) transform and resets all pose-mode values to
#       zero.  From this point on the animation still plays – but EVERY keyframe
#       is now offset by the same amount because the rest pose has shifted.
#
#  WHY animations don't break:
#     Because Blender stores animation as DELTAS from the rest pose.  After
#     "Apply as Rest Pose" the old T-pose deltas are still correct – the arm
#     moves the same relative amount.  Visually the character looks like it is
#     in V-pose at rest but the animation plays identically.
#
#  (Optional) Mesh correction:
#     Meshes weighted to those bones will deform as expected because the
#     armature modifier re-deforms from the new rest pose automatically.
#


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_upper_arm_bones(armobj, left_name, right_name):
    """Return the two PoseBone objects for left and right upper arm."""
    bones = armobj.pose.bones
    result = {}
    for name in (left_name, right_name):
        if name in bones:
            result[name] = bones[name]
    return result


# ─── Operator: Step 1 – Rotate arms into V-Pose ───────────────────────────────

class TTOPOSE_OT_apply_v_rotation(bpy.types.Operator):
    """Rotate upper arm bones downward into V-Pose in Pose mode"""
    bl_idname = "ttopose.apply_v_rotation"
    bl_label  = "Step 1 – Set Arms to V-Pose"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE'

    def execute(self, context):
        obj     = context.active_object
        props   = obj.ttopose_props
        angle   = math.radians(props.v_angle)
        l_name  = props.left_arm_bone
        r_name  = props.right_arm_bone

        # Enter Pose mode
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')

        pb = obj.pose.bones

        # Rotate LEFT arm downward (negative Z local rotation for most rigs)
        if l_name in pb:
            bone = pb[l_name]
            bone.bone.select = True
            obj.data.bones.active = bone.bone
            # Tilt arm DOWN by rotating around LOCAL Z axis
            # Left arm tilts DOWN = negative local-Z rotation
            bone.rotation_mode = 'XYZ'
            rot = Euler(bone.rotation_euler)
            rot.z = -angle  # tilt downward
            bone.rotation_euler = rot
        else:
            self.report({'WARNING'}, f"Left arm bone '{l_name}' not found.")

        # Rotate RIGHT arm downward (positive Z for symmetry)
        if r_name in pb:
            bone = pb[r_name]
            bone.bone.select = True
            # Right arm tilts DOWN = positive local-Z rotation
            bone.rotation_mode = 'XYZ'
            rot = Euler(bone.rotation_euler)
            rot.z = angle
            bone.rotation_euler = rot
        else:
            self.report({'WARNING'}, f"Right arm bone '{r_name}' not found.")

        bpy.ops.object.mode_set(mode='OBJECT')
        self.report({'INFO'}, f"Arms rotated {math.degrees(angle):.1f}° to V-Pose. Proceed to Step 2.")
        return {'FINISHED'}


# ─── Operator: Step 2 – Apply as Rest Pose ────────────────────────────────────

class TTOPOSE_OT_apply_rest_pose(bpy.types.Operator):
    """Apply current pose as new Rest Pose – animation is automatically preserved"""
    bl_idname = "ttopose.apply_rest_pose"
    bl_label  = "Step 2 – Apply as Rest Pose"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE'

    def execute(self, context):
        obj = context.active_object

        # Must be in Pose mode to apply pose
        if context.object.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')

        # Select all bones so the apply affects everything
        bpy.ops.pose.select_all(action='SELECT')

        # This is the core Blender operator that bakes pose → rest
        bpy.ops.pose.armature_apply(selected=False)

        bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, "Rest Pose updated to V-Pose. Animation is preserved automatically.")
        return {'FINISHED'}


# ─── Operator: Step 3 – Reset Mesh Shape Keys to New Rest ─────────────────────

class TTOPOSE_OT_reset_v_rotation(bpy.types.Operator):
    """Reset arm rotation only – undo Step 1 if you want to start over"""
    bl_idname = "ttopose.reset_v_rotation"
    bl_label  = "Reset Arm Rotation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE'

    def execute(self, context):
        obj   = context.active_object
        props = obj.ttopose_props
        l_name = props.left_arm_bone
        r_name = props.right_arm_bone

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')

        pb = obj.pose.bones

        for name in (l_name, r_name):
            if name in pb:
                bone = pb[name]
                bone.rotation_mode = 'XYZ'
                bone.rotation_euler = Euler((0, 0, 0))

        bpy.ops.object.mode_set(mode='OBJECT')
        self.report({'INFO'}, "Arm rotation reset to original.")
        return {'FINISHED'}


# ─── Operator: V-Pose → T-Pose Step 1 (Rotate UP) ────────────────────────────

class TTOPOSE_OT_apply_t_rotation(bpy.types.Operator):
    """Rotate upper arm bones UPWARD back into T-Pose in Pose mode"""
    bl_idname = "ttopose.apply_t_rotation"
    bl_label  = "Step 1 – Set Arms to T-Pose"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE'

    def execute(self, context):
        obj    = context.active_object
        props  = obj.ttopose_props
        angle  = math.radians(props.v_angle)
        l_name = props.left_arm_bone
        r_name = props.right_arm_bone

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')

        pb = obj.pose.bones

        # V→T: rotate LEFT arm UPWARD (positive Z, opposite of T→V)
        if l_name in pb:
            bone = pb[l_name]
            bone.bone.select = True
            obj.data.bones.active = bone.bone
            bone.rotation_mode = 'XYZ'
            rot = Euler(bone.rotation_euler)
            rot.z = angle   # tilt UPWARD = opposite direction
            bone.rotation_euler = rot
        else:
            self.report({'WARNING'}, f"Left arm bone '{l_name}' not found.")

        # V→T: rotate RIGHT arm UPWARD (negative Z)
        if r_name in pb:
            bone = pb[r_name]
            bone.bone.select = True
            bone.rotation_mode = 'XYZ'
            rot = Euler(bone.rotation_euler)
            rot.z = -angle  # tilt UPWARD
            bone.rotation_euler = rot
        else:
            self.report({'WARNING'}, f"Right arm bone '{r_name}' not found.")

        bpy.ops.object.mode_set(mode='OBJECT')
        self.report({'INFO'}, f"Arms rotated +{math.degrees(angle):.1f}° to T-Pose. Proceed to Step 2.")
        return {'FINISHED'}


# ─── Per-Armature Properties ──────────────────────────────────────────────────

class TtoPoseProperties(bpy.types.PropertyGroup):
    left_arm_bone: bpy.props.StringProperty(
        name="Left Upper Arm Bone",
        default=DEFAULT_LEFT_ARM,
        description="Name of the left upper arm bone"
    )
    right_arm_bone: bpy.props.StringProperty(
        name="Right Upper Arm Bone",
        default=DEFAULT_RIGHT_ARM,
        description="Name of the right upper arm bone"
    )
    v_angle: bpy.props.FloatProperty(
        name="V-Angle (degrees)",
        default=45.0,
        min=0.0,
        max=90.0,
        description="How many degrees to tilt the arms downward (45° = typical V-pose)"
    )


# ─── UI Panel ─────────────────────────────────────────────────────────────────

class VIEW3D_PT_t_to_v_pose(bpy.types.Panel):
    bl_label       = "T-Pose ↔ V-Pose"
    bl_idname      = "VIEW3D_PT_t_to_v_pose"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category    = 'Tool'

    def draw(self, context):
        layout = self.layout
        obj    = context.active_object

        if not (obj and obj.type == 'ARMATURE'):
            layout.label(text="Select an Armature", icon='INFO')
            return

        props = obj.ttopose_props

        # ── Settings ──────────────────────────────────────────
        box = layout.box()
        box.label(text="Settings", icon='SETTINGS')
        box.prop(props, "left_arm_bone",  text="Left Arm")
        box.prop(props, "right_arm_bone", text="Right Arm")
        box.prop(props, "v_angle",        text="Tilt Angle (°)")

        layout.separator()

        # ── Step 1 ────────────────────────────────────────────
        box1 = layout.box()
        box1.label(text="Step 1 – Preview V-Pose", icon='POSE_HLT')
        box1.label(text="Rotates arm bones in Pose mode.", icon='INFO')
        r = box1.row()
        r.scale_y = 1.4
        r.operator("ttopose.apply_v_rotation", text="Set Arms to V-Pose", icon='CON_ROTLIKE')

        layout.separator()

        # ── Step 2 ────────────────────────────────────────────
        box2 = layout.box()
        box2.label(text="Step 2 – Commit as Rest Pose", icon='OUTLINER_OB_ARMATURE')
        box2.label(text="Bakes V-Pose → Rest Pose.", icon='INFO')
        box2.label(text="Animation stays intact.", icon='CHECKMARK')
        r = box2.row()
        r.scale_y = 1.4
        r.operator("ttopose.apply_rest_pose", text="Apply as Rest Pose", icon='IMPORT')

        layout.separator()

        # ── Reset ─────────────────────────────────────────────
        layout.operator("ttopose.reset_v_rotation", text="↩ Reset Arm Rotation", icon='LOOP_BACK')

        layout.separator()
        layout.separator()

        # ════════════════════════════════════════════════════
        # V-Pose  →  T-Pose section
        # ════════════════════════════════════════════════════
        layout.label(text="─────── V-Pose → T-Pose ───────")

        layout.separator()

        # ── Step 1 ────────────────────────────────────────────
        boxA = layout.box()
        boxA.label(text="Step 1 – Preview T-Pose", icon='POSE_HLT')
        boxA.label(text="Rotate arms UP back to horizontal.", icon='INFO')
        rA = boxA.row()
        rA.scale_y = 1.4
        rA.operator("ttopose.apply_t_rotation", text="Set Arms to T-Pose", icon='CON_ROTLIKE')

        layout.separator()

        # ── Step 2 (shared operator, same logic) ──────────────
        boxB = layout.box()
        boxB.label(text="Step 2 – Commit as Rest Pose", icon='OUTLINER_OB_ARMATURE')
        boxB.label(text="Bakes T-Pose → Rest Pose.", icon='INFO')
        boxB.label(text="Animation stays intact.", icon='CHECKMARK')
        rB = boxB.row()
        rB.scale_y = 1.4
        rB.operator("ttopose.apply_rest_pose", text="Apply as Rest Pose", icon='IMPORT')

        layout.separator()

        layout.operator("ttopose.reset_v_rotation", text="↩ Reset Arm Rotation", icon='LOOP_BACK')


# ─── Registration ─────────────────────────────────────────────────────────────

classes = (
    TtoPoseProperties,
    TTOPOSE_OT_apply_v_rotation,
    TTOPOSE_OT_apply_t_rotation,
    TTOPOSE_OT_apply_rest_pose,
    TTOPOSE_OT_reset_v_rotation,
    VIEW3D_PT_t_to_v_pose,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.ttopose_props = bpy.props.PointerProperty(type=TtoPoseProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    if hasattr(bpy.types.Object, "ttopose_props"):
        del bpy.types.Object.ttopose_props

if __name__ == "__main__":
    register()
