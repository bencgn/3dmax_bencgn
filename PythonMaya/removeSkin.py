import maya.cmds as cmds
import maya.mel as mel

class RemoveSkinTool:
    def __init__(self):
        # Create the UI
        self.create_ui()
    
    def create_ui(self):
        """Create the UI for the Remove Skin tool"""
        # Check if the window already exists and delete it
        window_name = "removeSkinUI"
        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name)
        
        # Create the window
        window = cmds.window(window_name, title="Remove Skin Tool", widthHeight=(350, 250))
        
        # Create the main layout
        main_layout = cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=10, columnWidth=350)
        
        # Add a header
        cmds.text(label="Remove Skin Tool", font="boldLabelFont", height=30)
        cmds.separator(height=10)
        
        # Add description
        cmds.text(label="This tool removes skin clusters from selected objects.", align="left")
        cmds.text(label="Select one or more objects and click the button below.", align="left")
        
        cmds.separator(height=20)
        
        # Add options
        self.remove_history = cmds.checkBoxGrp(label="Remove History:", value1=False, 
                                             columnWidth=[(1, 120), (2, 200)],
                                             annotation="When checked, all history will be removed from the object")
        
        cmds.separator(height=20)
        
        # Add buttons
        cmds.button(label="Remove Skin from Selected", 
                   command=self.remove_skin_selected, 
                   height=50,
                   backgroundColor=[0.8, 0.3, 0.3])
        
        cmds.button(label="Select All Skinned Objects", 
                   command=self.select_skinned_objects, 
                   height=30)
        
        # Add status text
        self.status_text = cmds.text(label="Ready - Select objects and click the button", align="center")
        
        # Show the window
        cmds.showWindow(window)
    
    def remove_skin_selected(self, *args):
        """Remove skin clusters from selected objects"""
        # Get selected objects
        selected = cmds.ls(selection=True, long=True)
        
        if not selected:
            cmds.confirmDialog(title="No Selection", 
                              message="Please select at least one object to remove skin from.",
                              button=["OK"])
            cmds.text(self.status_text, edit=True, label="Error: No objects selected")
            return
        
        # Get option
        remove_history = cmds.checkBoxGrp(self.remove_history, query=True, value1=True)
        
        # Process each selected object
        processed_count = 0
        for obj in selected:
            try:
                # Check if the object has a skin cluster
                skin_clusters = self.find_skin_clusters(obj)
                
                if skin_clusters:
                    # Remove the skin clusters
                    for skin_cluster in skin_clusters:
                        cmds.skinCluster(skin_cluster, edit=True, unbind=True)
                    
                    # If option is set, remove all history
                    if remove_history:
                        cmds.delete(obj, constructionHistory=True)
                    
                    processed_count += 1
                
            except Exception as e:
                cmds.warning(f"Error processing {obj}: {str(e)}")
        
        # Update status
        if processed_count > 0:
            cmds.text(self.status_text, edit=True, label=f"Successfully removed skin from {processed_count} objects")
            cmds.confirmDialog(title="Remove Complete", 
                              message=f"Successfully removed skin from {processed_count} objects.",
                              button=["OK"])
        else:
            cmds.text(self.status_text, edit=True, label="No skin clusters were found on selected objects")
            cmds.confirmDialog(title="No Skin Found", 
                              message="No skin clusters were found on the selected objects.",
                              button=["OK"])
    
    def select_skinned_objects(self, *args):
        """Select all objects in the scene that have skin clusters"""
        # Find all skin clusters in the scene
        all_skin_clusters = cmds.ls(type="skinCluster")
        
        if not all_skin_clusters:
            cmds.confirmDialog(title="No Skin Clusters", 
                              message="No skin clusters found in the scene.",
                              button=["OK"])
            cmds.text(self.status_text, edit=True, label="No skin clusters found in scene")
            return
        
        # Get the objects associated with each skin cluster
        skinned_objects = []
        for skin_cluster in all_skin_clusters:
            # Get the geometry influenced by this skin cluster
            geometry = cmds.skinCluster(skin_cluster, query=True, geometry=True)
            if geometry:
                skinned_objects.extend(geometry)
        
        # Remove duplicates
        skinned_objects = list(set(skinned_objects))
        
        if skinned_objects:
            cmds.select(skinned_objects)
            cmds.text(self.status_text, edit=True, label=f"Selected {len(skinned_objects)} skinned objects")
        else:
            cmds.text(self.status_text, edit=True, label="No skinned objects found")
    
    def find_skin_clusters(self, obj):
        """Find skin clusters attached to the given object"""
        # Get the shape node if the object is a transform
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        nodes_to_check = [obj] + shapes
        
        # Find skin clusters connected to the object or its shapes
        skin_clusters = []
        for node in nodes_to_check:
            # Get all connections to the node
            connections = cmds.listConnections(node, type="skinCluster") or []
            skin_clusters.extend(connections)
        
        # Remove duplicates
        return list(set(skin_clusters))

# Function to run the tool
def run():
    RemoveSkinTool()

# Auto-run when the script is imported
if __name__ == "__main__":
    run()