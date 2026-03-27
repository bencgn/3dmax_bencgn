import bpy
import os
import math

bl_info = {
    "name": "Mixamo Retarget Tool",
    "author": "Antigravity",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Retarget Tool",
    "description": "Automatic animation retargeting from Mixamo (T-pose) to custom rig (A-pose)",
    "category": "Animation",
}

class MixamoRetargetProperties(bpy.types.PropertyGroup):
    target_armature: bpy.props.PointerProperty(
        name="Target Rig",
        type=bpy.types.Object,
        description="Armature to retarget animation onto"
    )
    mixamo_armature: bpy.props.PointerProperty(
        name="Mixamo Rig",
        type=bpy.types.Object,
        description="Source Mixamo armature"
    )
    pose_offset: bpy.props.FloatProperty(
        name="A/T Pose Offset",
        default=45.0,
        min=-90.0,
        max=90.0,
        description="Offset in degrees for upper arms (T-pose to A-pose)"
    )
    frame_start: bpy.props.IntProperty(
        name="Start Frame",
        default=1
    )
    frame_end: bpy.props.IntProperty(
        name="End Frame",
        default=250
    )
    batch_folder: bpy.props.StringProperty(
        name="Batch Folder",
        subtype='DIR_PATH',
        description="Folder containing FBX animations to batch retarget"
    )

def map_bones(source_rig, target_rig):
    """Map bones based on name heuristics"""
    mapping = {}
    
    # Common Mixamo bone names without prefix
    mixamo_dict = {
        "Hips": ["hips", "pelvis", "root"],
        "Spine": ["spine", "spine_01", "spine1", "spine.001"],
        "Spine1": ["spine_02", "spine2", "spine.002", "chest"],
        "Spine2": ["spine_03", "spine3", "spine.003", "upper_chest"],
        "Neck": ["neck"],
        "Head": ["head"],
        "LeftShoulder": ["clavicle.l", "shoulder.l", "leftshoulder"],
        "LeftArm": ["upperarm.l", "upper_arm.l", "arm.l", "leftarm"],
        "LeftForeArm": ["forearm.l", "lower_arm.l", "lowerarm.l", "leftforearm"],
        "LeftHand": ["hand.l", "lefthand"],
        "RightShoulder": ["clavicle.r", "shoulder.r", "rightshoulder"],
        "RightArm": ["upperarm.r", "upper_arm.r", "arm.r", "rightarm"],
        "RightForeArm": ["forearm.r", "lower_arm.r", "lowerarm.r", "rightforearm"],
        "RightHand": ["hand.r", "righthand"],
        "LeftUpLeg": ["thigh.l", "upperleg.l", "upper_leg.l", "leftupleg"],
        "LeftLeg": ["calf.l", "lowerleg.l", "lower_leg.l", "leftleg"],
        "LeftFoot": ["foot.l", "leftfoot"],
        "LeftToeBase": ["toe.l", "toes.l", "lefttoebase"],
        "RightUpLeg": ["thigh.r", "upperleg.r", "upper_leg.r", "rightupleg"],
        "RightLeg": ["calf.r", "lowerleg.r", "lower_leg.r", "rightleg"],
        "RightFoot": ["foot.r", "rightfoot"],
        "RightToeBase": ["toe.r", "toes.r", "righttoebase"]
    }
    
    src_bones = source_rig.data.bones.keys()
    tgt_bones = target_rig.data.bones.keys()
    
    for mix_key, tgt_options in mixamo_dict.items():
        src_bone = None
        for sb in src_bones:
            if mix_key.lower() in sb.lower():
                # Allow for prefixes like mixamorig:
                if sb.endswith(mix_key) or ":" + mix_key in sb:
                    src_bone = sb
                    break
        
        if not src_bone:
            print(f"DEBUG: Source bone matching '{mix_key}' not found, skipping.")
            continue
            
        tgt_bone = None
        for tb in tgt_bones:
            tb_clean = tb.lower().replace(" ", "_").replace(".", "_")
            # Convert targeting parts appropriately
            tb_opts = [opt.replace(".", "_") for opt in tgt_options]
            if any(opt in tb_clean for opt in tb_opts) or any(opt in tb.lower() for opt in tgt_options):
                tgt_bone = tb
                break
                
        if tgt_bone:
            mapping[src_bone] = tgt_bone
            print(f"DEBUG: Mapped {src_bone} -> {tgt_bone}")
            
    return mapping

def apply_constraints(source_rig, target_rig, pose_offset):
    """Create constraints for transferring animation"""
    mapping = map_bones(source_rig, target_rig)
    
    bpy.context.view_layer.objects.active = target_rig
    bpy.ops.object.mode_set(mode='POSE')
    
    for src_bone, tgt_bone in mapping.items():
        if tgt_bone not in target_rig.pose.bones:
            continue
            
        pb = target_rig.pose.bones[tgt_bone]
        
        # Clear existing
        for c in reversed(pb.constraints):
            if c.type in ('COPY_ROTATION', 'COPY_LOCATION'):
                pb.constraints.remove(c)
        
        # Hips get Location too
        if "hips" in src_bone.lower():
            con_loc = pb.constraints.new('COPY_LOCATION')
            con_loc.name = "Retarget_Loc"
            con_loc.target = source_rig
            con_loc.subtarget = src_bone
            con_loc.target_space = 'LOCAL'
            con_loc.owner_space = 'LOCAL'
            
        # All get Rotation
        con_rot = pb.constraints.new('COPY_ROTATION')
        con_rot.name = "Retarget_Rot"
        con_rot.target = source_rig
        con_rot.subtarget = src_bone
        con_rot.target_space = 'LOCAL'
        con_rot.owner_space = 'LOCAL'
        
        # Handle T-Pose to A-Pose offset
        if pose_offset != 0 and "arm" in src_bone.lower() and "fore" not in src_bone.lower():
            con_rot.mix_mode = 'ADD'
            pb.rotation_mode = 'XYZ'
            
            # Apply offset rotation based on side
            if ".r" in tgt_bone.lower() or "_r" in tgt_bone.lower() or "right" in tgt_bone.lower():
                pb.rotation_euler[2] = math.radians(pose_offset)
            else:
                pb.rotation_euler[2] = math.radians(-pose_offset)
                
    bpy.ops.object.mode_set(mode='OBJECT')

def bake_action(target_rig, f_start, f_end):
    """Bake the animation to the target rig and clear constraints"""
    bpy.context.view_layer.objects.active = target_rig
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    
    print(f"DEBUG: Baking animation from frames {f_start} to {f_end}")
    
    bpy.ops.nla.bake(
        frame_start=f_start,
        frame_end=f_end,
        only_selected=True,
        visual_keying=True,
        clear_constraints=True,
        clear_parents=False,
        use_current_action=True,
        bake_types={'POSE'}
    )
    
    bpy.ops.object.mode_set(mode='OBJECT')

class VIEW3D_PT_mixamo_retarget(bpy.types.Panel):
    bl_label = "Retarget Tool"
    bl_idname = "VIEW3D_PT_mixamo_retarget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Retarget Tool"

    def draw(self, context):
        layout = self.layout
        props = context.scene.mixamo_retarget_props
        
        box = layout.box()
        box.label(text="Rigs:")
        box.prop(props, "mixamo_armature")
        box.prop(props, "target_armature")
        
        layout.separator()
        layout.prop(props, "pose_offset")
        
        row = layout.row()
        row.prop(props, "frame_start")
        row.prop(props, "frame_end")
        
        layout.separator()
        layout.operator("retarget.import_fbx", icon='IMPORT')
        layout.operator("retarget.apply_anim", icon='ANIM')
        
        layout.separator()
        box_batch = layout.box()
        box_batch.label(text="Batch Process:")
        box_batch.prop(props, "batch_folder")
        box_batch.operator("retarget.batch_folder", icon='FILE_FOLDER')

class RETARGET_OT_import_fbx(bpy.types.Operator):
    bl_idname = "retarget.import_fbx"
    bl_label = "Import Mixamo FBX"
    bl_description = "Import an FBX file and set it as the Mixamo Rig"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    
    def execute(self, context):
        if not os.path.exists(self.filepath):
            self.report({'ERROR'}, "File not found")
            return {'CANCELLED'}
            
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.import_scene.fbx(filepath=self.filepath)
        
        mix_rig = None
        for obj in context.selected_objects:
            if obj.type == 'ARMATURE':
                mix_rig = obj
                break
                
        if mix_rig:
            context.scene.mixamo_retarget_props.mixamo_armature = mix_rig
            self.report({'INFO'}, f"Set source rig: {mix_rig.name}")
        else:
            self.report({'WARNING'}, "No armature found in imported FBX")
            
        return {'FINISHED'}
        
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class RETARGET_OT_apply_anim(bpy.types.Operator):
    bl_idname = "retarget.apply_anim"
    bl_label = "Retarget Animation"
    bl_description = "Apply constraints and bake the animation"
    
    @classmethod
    def poll(cls, context):
        props = context.scene.mixamo_retarget_props
        return props.mixamo_armature and props.target_armature
        
    def execute(self, context):
        props = context.scene.mixamo_retarget_props
        src = props.mixamo_armature
        tgt = props.target_armature
        
        if src == tgt:
            self.report({'ERROR'}, "Source and Target rigs must be different")
            return {'CANCELLED'}
            
        apply_constraints(src, tgt, props.pose_offset)
        
        start = props.frame_start
        end = props.frame_end
        if src.animation_data and src.animation_data.action:
            start = int(src.animation_data.action.frame_range[0])
            end = int(src.animation_data.action.frame_range[1])
            
        bake_action(tgt, start, end)
        self.report({'INFO'}, "Retargeting Complete")
        return {'FINISHED'}

class RETARGET_OT_batch_folder(bpy.types.Operator):
    bl_idname = "retarget.batch_folder"
    bl_label = "Batch Retarget Folder"
    bl_description = "Process all FBX files in the batch folder"
    
    @classmethod
    def poll(cls, context):
        props = context.scene.mixamo_retarget_props
        return bool(props.batch_folder) and bool(props.target_armature)
        
    def execute(self, context):
        props = context.scene.mixamo_retarget_props
        tgt = props.target_armature
        folder = bpy.path.abspath(props.batch_folder)
        
        if not os.path.isdir(folder):
            self.report({'ERROR'}, "Invalid folder path")
            return {'CANCELLED'}
            
        fbx_files = [f for f in os.listdir(folder) if f.lower().endswith('.fbx')]
        if not fbx_files:
            self.report({'WARNING'}, "No FBX files found in directory")
            return {'CANCELLED'}
            
        for fbx in fbx_files:
            filepath = os.path.join(folder, fbx)
            print(f"\\n--- Processing: {fbx} ---")
            
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.import_scene.fbx(filepath=filepath)
            
            src = None
            for obj in context.selected_objects:
                if obj.type == 'ARMATURE':
                    src = obj
                    break
                    
            if not src:
                print(f"DEBUG: No armature found in {fbx}, skipping.")
                continue
                
            apply_constraints(src, tgt, props.pose_offset)
            
            start = props.frame_start
            end = props.frame_end
            if src.animation_data and src.animation_data.action:
                start = int(src.animation_data.action.frame_range[0])
                end = int(src.animation_data.action.frame_range[1])
                
            bake_action(tgt, start, end)
            
            if tgt.animation_data and tgt.animation_data.action:
                tgt.animation_data.action.name = os.path.splitext(fbx)[0]
                
            bpy.ops.object.select_all(action='DESELECT')
            src.select_set(True)
            bpy.ops.object.delete()
            
            for obj in bpy.context.scene.objects:
                if obj.select_get(): 
                    bpy.ops.object.delete()
                    
        self.report({'INFO'}, f"Batch processed {len(fbx_files)} animations")
        return {'FINISHED'}

classes = (
    MixamoRetargetProperties,
    VIEW3D_PT_mixamo_retarget,
    RETARGET_OT_import_fbx,
    RETARGET_OT_apply_anim,
    RETARGET_OT_batch_folder
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.mixamo_retarget_props = bpy.props.PointerProperty(type=MixamoRetargetProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.mixamo_retarget_props

if __name__ == "__main__":
    register()
