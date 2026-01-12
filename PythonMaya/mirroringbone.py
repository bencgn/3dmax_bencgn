import maya.cmds as cmds
import maya.mel as mel
import re

class MirrorBoneTool:
    def __init__(self):
        # Define the naming patterns for left and right sides
        self.left_identifiers = ["_L", "Left", "_l", "left", "L_", "l_"]
        self.right_identifiers = ["_R", "Right", "_r", "right", "R_", "r_"]
        
        # Create the UI
        self.create_ui()
    
    def create_ui(self):
        """Create the UI for the Mirror Bone tool"""
        # Check if the window already exists and delete it
        window_name = "mirrorBoneUI"
        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name)
        
        # Create the window
        window = cmds.window(window_name, title="Mirror Bone Tool", widthHeight=(400, 400))
        
        # Create the main layout
        main_layout = cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=10, columnWidth=400)
        
        # Add a header
        cmds.text(label="Mirror Bone Tool", font="boldLabelFont", height=30)
        cmds.separator(height=10)
        
        # Add description
        cmds.text(label="This tool mirrors bone transformations from one side to the other.", align="left")
        cmds.text(label="Select the source bone(s) and click one of the mirror buttons.", align="left")
        
        cmds.separator(height=20)
        
        # Add options
        self.mirror_translate = cmds.checkBoxGrp(label="Mirror Translation:", value1=True, 
                                               columnWidth=[(1, 120), (2, 250)])
        
        self.mirror_rotate = cmds.checkBoxGrp(label="Mirror Rotation:", value1=True, 
                                             columnWidth=[(1, 120), (2, 250)])
        
        self.mirror_scale = cmds.checkBoxGrp(label="Mirror Scale:", value1=False, 
                                            columnWidth=[(1, 120), (2, 250)])
        
        # Add naming pattern options
        cmds.frameLayout(label="Naming Patterns", collapsable=True, collapse=False)
        cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=5)
        
        # Left side identifiers
        cmds.text(label="Left Side Identifiers (comma-separated):", align="left")
        self.left_patterns = cmds.textField(text="_L,Left,_l,left,L_,l_")
        
        # Right side identifiers
        cmds.text(label="Right Side Identifiers (comma-separated):", align="left")
        self.right_patterns = cmds.textField(text="_R,Right,_r,right,R_,r_")
        
        cmds.setParent("..")
        cmds.setParent("..")
        
        cmds.separator(height=20)
        
        # Add mirror direction options
        cmds.frameLayout(label="Mirror Direction", collapsable=False)
        cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=10)
        
        # Mirror buttons
        cmds.button(label="Mirror Left → Right", 
                   command=self.mirror_left_to_right, 
                   height=40,
                   backgroundColor=[0.2, 0.6, 0.8])
        
        cmds.button(label="Mirror Right → Left", 
                   command=self.mirror_right_to_left, 
                   height=40,
                   backgroundColor=[0.8, 0.6, 0.2])
        
        cmds.setParent("..")
        cmds.setParent("..")
        
        # Add advanced options
        cmds.frameLayout(label="Advanced Options", collapsable=True, collapse=True)
        cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=5)
        
        self.mirror_behavior = cmds.radioButtonGrp(label="Mirror Behavior:", 
                                                 labelArray3=["World", "Local", "Custom"], 
                                                 numberOfRadioButtons=3, 
                                                 select=1,
                                                 columnWidth=[(1, 120), (2, 80), (3, 80), (4, 80)])
        
        self.mirror_axis = cmds.radioButtonGrp(label="Mirror Axis:", 
                                             labelArray3=["X", "Y", "Z"], 
                                             numberOfRadioButtons=3, 
                                             select=1,
                                             columnWidth=[(1, 120), (2, 80), (3, 80), (4, 80)])
        
        cmds.setParent("..")
        cmds.setParent("..")
        
        # Add status text
        self.status_text = cmds.text(label="Ready - Select bone(s) and click a mirror button", align="center")
        
        # Show the window
        cmds.showWindow(window)
    
    def get_mirror_bone(self, bone_name):
        """Find the mirror bone name based on naming patterns"""
        # Get the current naming patterns from UI
        left_patterns = cmds.textField(self.left_patterns, query=True, text=True).split(',')
        right_patterns = cmds.textField(self.right_patterns, query=True, text=True).split(',')
        
        # Check if bone name contains left pattern and replace with right pattern
        for i, left_pattern in enumerate(left_patterns):
            if left_pattern in bone_name:
                return bone_name.replace(left_pattern, right_patterns[min(i, len(right_patterns)-1)])
        
        # Check if bone name contains right pattern and replace with left pattern
        for i, right_pattern in enumerate(right_patterns):
            if right_pattern in bone_name:
                return bone_name.replace(right_pattern, left_patterns[min(i, len(left_patterns)-1)])
        
        # If no pattern match, return None
        return None
    
    def is_left_bone(self, bone_name):
        """Check if the bone name contains a left side identifier"""
        left_patterns = cmds.textField(self.left_patterns, query=True, text=True).split(',')
        for pattern in left_patterns:
            if pattern in bone_name:
                return True
        return False
    
    def is_right_bone(self, bone_name):
        """Check if the bone name contains a right side identifier"""
        right_patterns = cmds.textField(self.right_patterns, query=True, text=True).split(',')
        for pattern in right_patterns:
            if pattern in bone_name:
                return True
        return False
    
    def mirror_transform(self, source_bone, target_bone):
        """Mirror the transformation from source bone to target bone"""
        # Get mirror options from UI
        mirror_translate = cmds.checkBoxGrp(self.mirror_translate, query=True, value1=True)
        mirror_rotate = cmds.checkBoxGrp(self.mirror_rotate, query=True, value1=True)
        mirror_scale = cmds.checkBoxGrp(self.mirror_scale, query=True, value1=True)
        
        # Get mirror behavior
        mirror_behavior = cmds.radioButtonGrp(self.mirror_behavior, query=True, select=True)
        mirror_axis = cmds.radioButtonGrp(self.mirror_axis, query=True, select=True)
        
        # Mirror axis mapping (1=X, 2=Y, 3=Z)
        axis_index = mirror_axis - 1
        
        # Mirror translation
        if mirror_translate:
            # Get source translation
            trans = cmds.xform(source_bone, query=True, translation=True, worldSpace=(mirror_behavior == 1))
            
            # Mirror the appropriate axis
            mirrored_trans = list(trans)
            mirrored_trans[axis_index] = -mirrored_trans[axis_index]
            
            # Apply to target
            cmds.xform(target_bone, translation=mirrored_trans, worldSpace=(mirror_behavior == 1))
        
        # Mirror rotation
        if mirror_rotate:
            # Get source rotation
            if mirror_behavior == 1:  # World
                rot = cmds.xform(source_bone, query=True, rotation=True, worldSpace=True)
            else:  # Local or Custom
                rot = cmds.xform(source_bone, query=True, rotation=True, objectSpace=True)
            
            # Mirror the rotation
            mirrored_rot = list(rot)
            
            # For proper mirroring, we need to flip two of the rotation axes
            # The axis perpendicular to the mirror plane stays the same
            if axis_index == 0:  # X axis mirror
                mirrored_rot[1] = -mirrored_rot[1]
                mirrored_rot[2] = -mirrored_rot[2]
            elif axis_index == 1:  # Y axis mirror
                mirrored_rot[0] = -mirrored_rot[0]
                mirrored_rot[2] = -mirrored_rot[2]
            else:  # Z axis mirror
                mirrored_rot[0] = -mirrored_rot[0]
                mirrored_rot[1] = -mirrored_rot[1]
            
            # Apply to target
            if mirror_behavior == 1:  # World
                cmds.xform(target_bone, rotation=mirrored_rot, worldSpace=True)
            else:  # Local or Custom
                cmds.xform(target_bone, rotation=mirrored_rot, objectSpace=True)
        
        # Mirror scale
        if mirror_scale:
            # Get source scale
            scale = cmds.xform(source_bone, query=True, scale=True, relative=True)
            
            # Apply to target (scale doesn't need mirroring, just copying)
            cmds.xform(target_bone, scale=scale, relative=True)
    
    def mirror_left_to_right(self, *args):
        """Mirror selected left bones to their right counterparts"""
        selected_bones = cmds.ls(selection=True, type="joint")
        
        if not selected_bones:
            cmds.confirmDialog(title="No Selection", 
                              message="Please select at least one bone/joint to mirror.",
                              button=["OK"])
            cmds.text(self.status_text, edit=True, label="Error: No bone selected")
            return
        
        # Filter for left-side bones
        left_bones = [bone for bone in selected_bones if self.is_left_bone(bone)]
        
        if not left_bones:
            cmds.confirmDialog(title="No Left Bones", 
                              message="No left-side bones found in selection. Please select bones with left-side naming pattern.",
                              button=["OK"])
            cmds.text(self.status_text, edit=True, label="Error: No left-side bones in selection")
            return
        
        # Mirror each left bone to its right counterpart
        mirrored_count = 0
        for left_bone in left_bones:
            right_bone = self.get_mirror_bone(left_bone)
            
            if right_bone and cmds.objExists(right_bone):
                self.mirror_transform(left_bone, right_bone)
                mirrored_count += 1
            else:
                cmds.warning(f"Could not find mirror bone for {left_bone}")
        
        # Update status
        if mirrored_count > 0:
            cmds.text(self.status_text, edit=True, label=f"Mirrored {mirrored_count} bone(s) from left to right")
            cmds.confirmDialog(title="Mirror Complete", 
                              message=f"Successfully mirrored {mirrored_count} bone(s) from left to right.",
                              button=["OK"])
        else:
            cmds.text(self.status_text, edit=True, label="No bones were mirrored")
    
    def mirror_right_to_left(self, *args):
        """Mirror selected right bones to their left counterparts"""
        selected_bones = cmds.ls(selection=True, type="joint")
        
        if not selected_bones:
            cmds.confirmDialog(title="No Selection", 
                              message="Please select at least one bone/joint to mirror.",
                              button=["OK"])
            cmds.text(self.status_text, edit=True, label="Error: No bone selected")
            return
        
        # Filter for right-side bones
        right_bones = [bone for bone in selected_bones if self.is_right_bone(bone)]
        
        if not right_bones:
            cmds.confirmDialog(title="No Right Bones", 
                              message="No right-side bones found in selection. Please select bones with right-side naming pattern.",
                              button=["OK"])
            cmds.text(self.status_text, edit=True, label="Error: No right-side bones in selection")
            return
        
        # Mirror each right bone to its left counterpart
        mirrored_count = 0
        for right_bone in right_bones:
            left_bone = self.get_mirror_bone(right_bone)
            
            if left_bone and cmds.objExists(left_bone):
                self.mirror_transform(right_bone, left_bone)
                mirrored_count += 1
            else:
                cmds.warning(f"Could not find mirror bone for {right_bone}")
        
        # Update status
        if mirrored_count > 0:
            cmds.text(self.status_text, edit=True, label=f"Mirrored {mirrored_count} bone(s) from right to left")
            cmds.confirmDialog(title="Mirror Complete", 
                              message=f"Successfully mirrored {mirrored_count} bone(s) from right to left.",
                              button=["OK"])
        else:
            cmds.text(self.status_text, edit=True, label="No bones were mirrored")

# Function to run the tool
def run():
    MirrorBoneTool()

# Auto-run when the script is imported
if __name__ == "__main__":
    run()