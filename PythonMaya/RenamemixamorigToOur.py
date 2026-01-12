import maya.cmds as cmds
import maya.mel as mel
import re

class MixamoRenamer:
    def __init__(self):
        # Define the mapping from Mixamo naming to your custom naming
        self.name_mapping = {
            # Spine and root
            "mixamorig:Hips": "Root_M",
            "mixamorig:Spine": "Spine1_M",
            "mixamorig:Spine1": "Spine2_M",
            "mixamorig:Spine2": "Chest_M",
            
            # Head and neck
            "mixamorig:Neck": "Neck_M",
            "mixamorig:Head": "Head_M",
            "mixamorig:HeadTop_End": "HeadEnd_M",
            
            # Left arm
            "mixamorig:LeftShoulder": "Scapula_L",
            "mixamorig:LeftArm": "Shoulder_L",
            "mixamorig:LeftForeArm": "Elbow_L",
            "mixamorig:LeftHand": "Wrist_L",
            
            # Left fingers
            "mixamorig:LeftHandThumb1": "ThumbFinger1_L",
            "mixamorig:LeftHandThumb2": "ThumbFinger2_L",
            "mixamorig:LeftHandThumb3": "ThumbFinger3_L",
            "mixamorig:LeftHandThumb4": "ThumbFingerEnd_L",
            "mixamorig:LeftHandIndex1": "IndexFinger1_L",
            "mixamorig:LeftHandIndex2": "IndexFinger2_L",
            "mixamorig:LeftHandIndex3": "IndexFinger3_L",
            "mixamorig:LeftHandIndex4": "IndexFingerEnd_L",
            "mixamorig:LeftHandMiddle1": "MiddleFinger1_L",
            "mixamorig:LeftHandMiddle2": "MiddleFinger2_L",
            "mixamorig:LeftHandMiddle3": "MiddleFinger3_L",
            "mixamorig:LeftHandMiddle4": "MiddleFingerEnd_L",
            "mixamorig:LeftHandRing1": "RingFinger1_L",
            "mixamorig:LeftHandRing2": "RingFinger2_L",
            "mixamorig:LeftHandRing3": "RingFinger3_L",
            "mixamorig:LeftHandRing4": "RingFingerEnd_L",
            "mixamorig:LeftHandPinky1": "PinkyFinger1_L",
            "mixamorig:LeftHandPinky2": "PinkyFinger2_L",
            "mixamorig:LeftHandPinky3": "PinkyFinger3_L",
            "mixamorig:LeftHandPinky4": "PinkyFingerEnd_L",
            
            # Right arm
            "mixamorig:RightShoulder": "Scapula_R",
            "mixamorig:RightArm": "Shoulder_R",
            "mixamorig:RightForeArm": "Elbow_R",
            "mixamorig:RightHand": "Wrist_R",
            
            # Right fingers
            "mixamorig:RightHandThumb1": "ThumbFinger1_R",
            "mixamorig:RightHandThumb2": "ThumbFinger2_R",
            "mixamorig:RightHandThumb3": "ThumbFinger3_R",
            "mixamorig:RightHandThumb4": "ThumbFingerEnd_R",
            "mixamorig:RightHandIndex1": "IndexFinger1_R",
            "mixamorig:RightHandIndex2": "IndexFinger2_R",
            "mixamorig:RightHandIndex3": "IndexFinger3_R",
            "mixamorig:RightHandIndex4": "IndexFingerEnd_R",
            "mixamorig:RightHandMiddle1": "MiddleFinger1_R",
            "mixamorig:RightHandMiddle2": "MiddleFinger2_R",
            "mixamorig:RightHandMiddle3": "MiddleFinger3_R",
            "mixamorig:RightHandMiddle4": "MiddleFingerEnd_R",
            "mixamorig:RightHandRing1": "RingFinger1_R",
            "mixamorig:RightHandRing2": "RingFinger2_R",
            "mixamorig:RightHandRing3": "RingFinger3_R",
            "mixamorig:RightHandRing4": "RingFingerEnd_R",
            "mixamorig:RightHandPinky1": "PinkyFinger1_R",
            "mixamorig:RightHandPinky2": "PinkyFinger2_R",
            "mixamorig:RightHandPinky3": "PinkyFinger3_R",
            "mixamorig:RightHandPinky4": "PinkyFingerEnd_R",
            
            # Left leg
            "mixamorig:LeftUpLeg": "Hip_L",
            "mixamorig:LeftLeg": "Knee_L",
            "mixamorig:LeftFoot": "Ankle_L",
            "mixamorig:LeftToeBase": "Toes_L",
            "mixamorig:LeftToe_End": "ToesEnd_L",
            
            # Right leg
            "mixamorig:RightUpLeg": "Hip_R",
            "mixamorig:RightLeg": "Knee_R",
            "mixamorig:RightFoot": "Ankle_R",
            "mixamorig:RightToeBase": "Toes_R",
            "mixamorig:RightToe_End": "ToesEnd_R"
        }
        
        # Create the UI
        self.create_ui()
    
    def create_ui(self):
        """Create the UI for the Mixamo renamer tool"""
        # Check if the window already exists and delete it
        window_name = "mixamoRenamerUI"
        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name)
        
        # Create the window
        window = cmds.window(window_name, title="Mixamo to Custom Rig Renamer", widthHeight=(400, 300))
        
        # Create the main layout
        main_layout = cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=10, columnWidth=400)
        
        # Add a header
        cmds.text(label="Mixamo to Custom Rig Renamer", font="boldLabelFont", height=30)
        cmds.separator(height=10)
        
        # Add description
        cmds.text(label="This tool renames Mixamo rig joints to match your custom naming convention.", align="left")
        cmds.text(label="Select the root joint of your Mixamo rig and click 'Rename Joints'.", align="left")
        
        cmds.separator(height=20)
        
        # Add options
        self.search_prefix = cmds.textFieldGrp(label="Search Prefix:", text="mixamorig:", columnWidth=[(1, 100), (2, 250)])
        
        # Add a checkbox for search and replace mode
        self.use_mapping = cmds.checkBoxGrp(label="Use Mapping:", value1=True, 
                                           changeCommand=self.toggle_mapping_mode,
                                           columnWidth=[(1, 100), (2, 250)])
        
        # Add a checkbox for renaming children
        self.rename_children = cmds.checkBoxGrp(label="Rename Children:", value1=True, 
                                               columnWidth=[(1, 100), (2, 250)])
        
        cmds.separator(height=20)
        
        # Add buttons
        cmds.button(label="Rename Selected Joints", 
                   command=self.rename_joints, 
                   height=50,
                   backgroundColor=[0.2, 0.6, 0.2])
        
        cmds.button(label="Select All Mixamo Joints", 
                   command=self.select_mixamo_joints, 
                   height=30)
        
        # Add status text
        self.status_text = cmds.text(label="Ready", align="center")
        
        # Show the window
        cmds.showWindow(window)
    
    def toggle_mapping_mode(self, *args):
        """Toggle between mapping mode and simple prefix replacement"""
        use_mapping = cmds.checkBoxGrp(self.use_mapping, query=True, value1=True)
        if not use_mapping:
            cmds.confirmDialog(title="Simple Prefix Mode", 
                              message="In simple prefix mode, the tool will only replace the 'mixamorig:' prefix with your custom prefix.",
                              button=["OK"])
    
    def select_mixamo_joints(self, *args):
        """Select all joints with the Mixamo prefix"""
        search_prefix = cmds.textFieldGrp(self.search_prefix, query=True, text=True)
        
        # Find all joints with the prefix
        all_joints = cmds.ls(type="joint")
        mixamo_joints = [j for j in all_joints if j.startswith(search_prefix)]
        
        if mixamo_joints:
            cmds.select(mixamo_joints, replace=True)
            cmds.text(self.status_text, edit=True, label=f"Selected {len(mixamo_joints)} Mixamo joints")
        else:
            cmds.confirmDialog(title="No Joints Found", 
                              message=f"No joints with prefix '{search_prefix}' were found.",
                              button=["OK"])
            cmds.text(self.status_text, edit=True, label="No Mixamo joints found")
    
    def rename_joints(self, *args):
        """Rename the selected joints based on the mapping"""
        # Get the selected joints
        selected_joints = cmds.ls(selection=True, type="joint")
        
        if not selected_joints:
            cmds.confirmDialog(title="No Selection", 
                              message="Please select at least one joint to rename.",
                              button=["OK"])
            return
        
        # Get options from UI
        use_mapping = cmds.checkBoxGrp(self.use_mapping, query=True, value1=True)
        rename_children = cmds.checkBoxGrp(self.rename_children, query=True, value1=True)
        search_prefix = cmds.textFieldGrp(self.search_prefix, query=True, text=True)
        
        # Collect all joints to process
        joints_to_process = []
        
        if rename_children:
            # Get all child joints of the selected joints
            for joint in selected_joints:
                # Get the joint and all its children
                joint_hierarchy = cmds.listRelatives(joint, allDescendents=True, type="joint", fullPath=True) or []
                joint_hierarchy.append(joint)  # Add the selected joint itself
                joints_to_process.extend(joint_hierarchy)
        else:
            # Only process the selected joints
            joints_to_process = selected_joints
        
        # Remove duplicates
        joints_to_process = list(set(joints_to_process))
        
        # Count how many joints will be renamed
        rename_count = 0
        
        # Process each joint
        for joint in joints_to_process:
            # Get the short name if it's a full path
            short_name = joint.split("|")[-1]
            
            new_name = None
            
            if use_mapping and short_name in self.name_mapping:
                # Use the predefined mapping
                new_name = self.name_mapping[short_name]
            elif short_name.startswith(search_prefix):
                # Simple prefix replacement
                new_name = short_name.replace(search_prefix, "")
            
            if new_name and new_name != short_name:
                try:
                    cmds.rename(joint, new_name)
                    rename_count += 1
                except Exception as e:
                    print(f"Error renaming {joint}: {str(e)}")
        
        # Update status
        cmds.text(self.status_text, edit=True, label=f"Renamed {rename_count} joints")
        
        if rename_count > 0:
            cmds.confirmDialog(title="Rename Complete", 
                              message=f"Successfully renamed {rename_count} joints.",
                              button=["OK"])

# Function to run the tool
def run():
    MixamoRenamer()

# Auto-run when the script is imported
if __name__ == "__main__":
    run()