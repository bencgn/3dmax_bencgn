bl_info = {
    "name": "Mixamo Auto Rigger",
    "author": "AI",
    "version": (2,0),
    "blender": (3,6,0),
    "location": "View3D > Sidebar > Mixamo",
    "category": "Rigging"
}

import bpy
import re


########################################
# CLEAN NAME
########################################

def clean_name(name):

    name = re.sub(r'_\d+$','',name)
    return name


########################################
# MAIN MAPPING
########################################

bone_map = {

"Bip001 Pelvis":"mixamorig:Hips",

"Bip001 Spine":"mixamorig:Spine",
"Bip001 Spine1":"mixamorig:Spine1",
"Bip001 Spine2":"mixamorig:Spine2",

"Bip001 Neck":"mixamorig:Neck",
"Bip001 Head":"mixamorig:Head",

# LEFT ARM
"Bip001 L Clavicle":"mixamorig:LeftShoulder",
"Bip001 L UpperArm":"mixamorig:LeftArm",
"Bip001 L Forearm":"mixamorig:LeftForeArm",
"Bip001 L Hand":"mixamorig:LeftHand",

# RIGHT ARM
"Bip001 R Clavicle":"mixamorig:RightShoulder",
"Bip001 R UpperArm":"mixamorig:RightArm",
"Bip001 R Forearm":"mixamorig:RightForeArm",
"Bip001 R Hand":"mixamorig:RightHand",

# LEFT LEG
"Bip001 L Thigh":"mixamorig:LeftUpLeg",
"Bip001 L Calf":"mixamorig:LeftLeg",
"Bip001 L Foot":"mixamorig:LeftFoot",
"Bip001 L Toe0":"mixamorig:LeftToeBase",

# RIGHT LEG
"Bip001 R Thigh":"mixamorig:RightUpLeg",
"Bip001 R Calf":"mixamorig:RightLeg",
"Bip001 R Foot":"mixamorig:RightFoot",
"Bip001 R Toe0":"mixamorig:RightToeBase",
}


########################################
# FINGER MAP
########################################

finger_map = {

"Finger0":["Thumb1","Thumb2","Thumb3"],
"Finger1":["Index1","Index2","Index3"],
"Finger2":["Middle1","Middle2","Middle3"],
"Finger3":["Ring1","Ring2","Ring3"],
"Finger4":["Pinky1","Pinky2","Pinky3"]

}


########################################
# AUTO FINGER DETECT
########################################

def rename_finger(name):

    clean = clean_name(name)

    side = None

    if " L " in clean:
        side="Left"

    if " R " in clean:
        side="Right"

    if not side:
        return None

    for finger in finger_map:

        if finger in clean:

            index = clean.split(finger)[1]

            try:
                index=int(index)
            except:
                index=0

            arr = finger_map[finger]

            if index < len(arr):

                return f"mixamorig:{side}Hand{arr[index]}"

    return None


########################################
# OPERATOR RENAME
########################################

class MIXAMO_OT_auto_rename(bpy.types.Operator):

    bl_idname = "mixamo.auto_rename"
    bl_label = "Auto Rename To Mixamo"

    def execute(self,context):

        obj=context.object

        if obj.type!="ARMATURE":
            self.report({'ERROR'},"Select Armature")
            return {'CANCELLED'}

        for bone in obj.data.bones:

            name = clean_name(bone.name)

            # MAIN MAP

            if name in bone_map:

                bone.name = bone_map[name]
                continue

            # FINGER MAP

            finger = rename_finger(bone.name)

            if finger:

                bone.name = finger

        self.report({'INFO'},"Auto Rename Complete")

        return {'FINISHED'}


########################################
# PREVIEW
########################################

class MIXAMO_OT_preview(bpy.types.Operator):

    bl_idname="mixamo.preview_map"
    bl_label="Preview Mapping"

    def execute(self,context):

        obj=context.object

        for bone in obj.data.bones:

            name=clean_name(bone.name)

            if name in bone_map:

                print(bone.name,"->",bone_map[name])

            else:

                finger=rename_finger(bone.name)

                if finger:

                    print(bone.name,"->",finger)

        self.report({'INFO'},"Check Console")

        return {'FINISHED'}


########################################
# UI
########################################

class MIXAMO_PT_panel(bpy.types.Panel):

    bl_label="Mixamo Auto Rigger"
    bl_idname="MIXAMO_PT_panel"
    bl_space_type='VIEW_3D'
    bl_region_type='UI'
    bl_category="Mixamo"

    def draw(self,context):

        layout=self.layout

        layout.label(text="Mixamo Auto Rename")

        layout.operator("mixamo.preview_map")

        layout.operator("mixamo.auto_rename")

        layout.separator()

        layout.label(text="Supported Rig:")

        layout.label(text="3dsMax Biped")
        layout.label(text="Finger Auto Detect")


########################################
# REGISTER
########################################

classes=[

MIXAMO_OT_auto_rename,
MIXAMO_OT_preview,
MIXAMO_PT_panel

]

def register():

    for c in classes:
        bpy.utils.register_class(c)

def unregister():

    for c in classes:
        bpy.utils.unregister_class(c)


if __name__=="__main__":
    register()