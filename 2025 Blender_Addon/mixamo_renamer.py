bl_info = {
    "name": "Mixamo Bone Renamer",
    "author": "AI",
    "version": (1,0),
    "blender": (3,6,0),
    "location": "View3D > Sidebar > Mixamo",
    "category": "Rigging"
}

import bpy

# -----------------------------
# Bone Mapping
# -----------------------------

bone_map = {

"Bip001 Pelvis":"mixamorig:Hips",

"Bip001 Spine":"mixamorig:Spine",
"Bip001 Spine1":"mixamorig:Spine1",
"Bip001 Spine2":"mixamorig:Spine2",

"Bip001 Neck":"mixamorig:Neck",
"Bip001 Head":"mixamorig:Head",

# Left Arm
"Bip001 L Clavicle":"mixamorig:LeftShoulder",
"Bip001 L UpperArm":"mixamorig:LeftArm",
"Bip001 L Forearm":"mixamorig:LeftForeArm",
"Bip001 L Hand":"mixamorig:LeftHand",

# Right Arm
"Bip001 R Clavicle":"mixamorig:RightShoulder",
"Bip001 R UpperArm":"mixamorig:RightArm",
"Bip001 R Forearm":"mixamorig:RightForeArm",
"Bip001 R Hand":"mixamorig:RightHand",

# Left Leg
"Bip001 L Thigh":"mixamorig:LeftUpLeg",
"Bip001 L Calf":"mixamorig:LeftLeg",
"Bip001 L Foot":"mixamorig:LeftFoot",
"Bip001 L Toe0":"mixamorig:LeftToeBase",

# Right Leg
"Bip001 R Thigh":"mixamorig:RightUpLeg",
"Bip001 R Calf":"mixamorig:RightLeg",
"Bip001 R Foot":"mixamorig:RightFoot",
"Bip001 R Toe0":"mixamorig:RightToeBase",
}

# -----------------------------
# Helper
# -----------------------------

def clean_name(name):

    name = name.split("_")[0]

    return name


# -----------------------------
# Operator Rename
# -----------------------------

class MIXAMO_OT_rename(bpy.types.Operator):

    bl_idname = "mixamo.rename"
    bl_label = "Rename Bones to Mixamo"

    def execute(self,context):

        obj = context.object

        if obj.type != 'ARMATURE':
            self.report({'ERROR'},"Select Armature")
            return {'CANCELLED'}

        for bone in obj.data.bones:

            clean = clean_name(bone.name)

            if clean in bone_map:

                bone.name = bone_map[clean]

        self.report({'INFO'},"Rename Done")

        return {'FINISHED'}


# -----------------------------
# Operator Auto Map
# -----------------------------

class MIXAMO_OT_preview(bpy.types.Operator):

    bl_idname = "mixamo.preview"
    bl_label = "Preview Mapping"

    def execute(self,context):

        obj = context.object

        for bone in obj.data.bones:

            clean = clean_name(bone.name)

            if clean in bone_map:

                print(bone.name," -> ",bone_map[clean])

        self.report({'INFO'},"Check Console")

        return {'FINISHED'}


# -----------------------------
# UI Panel
# -----------------------------

class MIXAMO_PT_panel(bpy.types.Panel):

    bl_label = "Mixamo Renamer"
    bl_idname = "MIXAMO_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mixamo"

    def draw(self,context):

        layout = self.layout

        layout.label(text="Auto Rename Bones")

        layout.operator("mixamo.preview")

        layout.operator("mixamo.rename")

        layout.separator()

        layout.label(text="Mapping:")

        for k,v in bone_map.items():

            row = layout.row()

            row.label(text=k)
            row.label(text="→")
            row.label(text=v)


# -----------------------------
# Register
# -----------------------------

classes = [

MIXAMO_OT_rename,
MIXAMO_OT_preview,
MIXAMO_PT_panel

]

def register():

    for c in classes:
        bpy.utils.register_class(c)

def unregister():

    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()