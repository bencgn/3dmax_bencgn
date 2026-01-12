import maya.cmds as cmds
import maya.mel as mel

class DeleteSelectedBone:
    def __init__(self):
        # Create the UI
        self.create_ui()
    
    def create_ui(self):
        """Create the UI for the Delete Selected Bone tool"""
        # Check if the window already exists and delete it
        window_name = "deleteSelectedBoneUI"
        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name)
        
        # Create the window
        window = cmds.window(window_name, title="Delete Selected Bone", widthHeight=(350, 250))
        
        # Create the main layout
        main_layout = cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=10, columnWidth=350)
        
        # Add a header
        cmds.text(label="Delete Selected Bone", font="boldLabelFont", height=30)
        cmds.separator(height=10)
        
        # Add description
        cmds.text(label="This tool deletes a selected joint/bone without deleting its children.", align="left")
        cmds.text(label="The children will be parented to the deleted joint's parent.", align="left")
        
        cmds.separator(height=20)
        
        # Add options
        self.maintain_offset = cmds.checkBoxGrp(label="Maintain Offset:", value1=True, 
                                               columnWidth=[(1, 100), (2, 250)],
                                               annotation="When checked, the child joints will maintain their world position")
        
        self.delete_constraints = cmds.checkBoxGrp(label="Delete Constraints:", value1=True, 
                                                 columnWidth=[(1, 100), (2, 250)],
                                                 annotation="When checked, constraints on the deleted joint will be removed")
        
        cmds.separator(height=20)
        
        # Add buttons
        cmds.button(label="Delete Selected Bone", 
                   command=self.delete_selected_bone, 
                   height=50,
                   backgroundColor=[0.8, 0.3, 0.3])
        
        # Add status text
        self.status_text = cmds.text(label="Ready - Select a bone and click the button", align="center")
        
        # Show the window
        cmds.showWindow(window)
    
    def delete_selected_bone(self, *args):
        """Delete the selected bone/joint without deleting its children"""
        # Get the selected joints
        selected_joints = cmds.ls(selection=True, type="joint")
        
        if not selected_joints:
            cmds.confirmDialog(title="No Selection", 
                              message="Please select at least one joint to delete.",
                              button=["OK"])
            cmds.text(self.status_text, edit=True, label="Error: No joint selected")
            return
        
        # Get options from UI
        maintain_offset = cmds.checkBoxGrp(self.maintain_offset, query=True, value1=True)
        delete_constraints = cmds.checkBoxGrp(self.delete_constraints, query=True, value1=True)
        
        # Process each selected joint
        processed_count = 0
        
        for joint in selected_joints:
            try:
                # Get the parent of the selected joint
                parent = cmds.listRelatives(joint, parent=True, fullPath=True)
                
                # Get all direct children of the selected joint
                children = cmds.listRelatives(joint, children=True, type="joint", fullPath=True)
                
                if not children:
                    # If no children, just delete the joint
                    if delete_constraints:
                        # Find and delete constraints
                        constraints = cmds.listConnections(joint, type="constraint")
                        if constraints:
                            cmds.delete(constraints)
                    
                    cmds.delete(joint)
                    processed_count += 1
                    continue
                
                # For each child, parent it to the original parent
                for child in children:
                    if parent:
                        # Parent the child to the original parent
                        cmds.parent(child, parent[0], absolute=(not maintain_offset))
                    else:
                        # If no parent, move to world
                        cmds.parent(child, world=True, absolute=(not maintain_offset))
                
                # Delete the original joint
                if delete_constraints:
                    # Find and delete constraints
                    constraints = cmds.listConnections(joint, type="constraint")
                    if constraints:
                        cmds.delete(constraints)
                
                cmds.delete(joint)
                processed_count += 1
                
            except Exception as e:
                cmds.warning(f"Error processing joint {joint}: {str(e)}")
        
        # Update status
        if processed_count > 0:
            cmds.text(self.status_text, edit=True, label=f"Successfully deleted {processed_count} joint(s)")
            cmds.confirmDialog(title="Delete Complete", 
                              message=f"Successfully deleted {processed_count} joint(s) while preserving their children.",
                              button=["OK"])
        else:
            cmds.text(self.status_text, edit=True, label="No joints were deleted")

# Function to run the tool
def run():
    DeleteSelectedBone()

# Auto-run when the script is imported
if __name__ == "__main__":
    run()