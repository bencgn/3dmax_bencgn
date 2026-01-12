import maya.cmds as cmds
import maya.mel as mel

class CleanupTool:
    def __init__(self):
        # Create the UI
        self.create_ui()
    
    def create_ui(self):
        """Create the UI for the Cleanup tool"""
        # Check if the window already exists and delete it
        window_name = "cleanupToolUI"
        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name)
        
        # Create the window
        window = cmds.window(window_name, title="Cleanup Tool", widthHeight=(400, 600))
        
        # Create the main layout
        main_layout = cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=10, columnWidth=400)
        
        # Add a header
        cmds.text(label="Maya Cleanup Tool", font="boldLabelFont", height=30)
        cmds.separator(height=10)
        
        # Add description
        cmds.text(label="This tool helps you clean up your Maya scene and reset transforms.", align="left")
        
        cmds.separator(height=20)
        
        # Create tab layout
        self.tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        
        # Create Transform Reset tab
        transform_tab = cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=5)
        
        cmds.frameLayout(label="Reset Transforms", collapsable=True, collapse=False)
        cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=5)
        
        # Add transform reset options
        self.reset_translate = cmds.checkBoxGrp(label="Reset Translate:", value1=True, 
                                             columnWidth=[(1, 120), (2, 250)])
        self.reset_rotate = cmds.checkBoxGrp(label="Reset Rotate:", value1=True, 
                                          columnWidth=[(1, 120), (2, 250)])
        self.reset_scale = cmds.checkBoxGrp(label="Reset Scale:", value1=True, 
                                         columnWidth=[(1, 120), (2, 250)])
        
        cmds.separator(height=10)
        
        # Add preserve shape option
        self.preserve_shape = cmds.checkBoxGrp(label="Preserve Shape:", value1=True, 
                                           columnWidth=[(1, 120), (2, 250)],
                                           annotation="When checked, mesh shape will be preserved when resetting scale")
        
        # Add freeze transform option
        self.freeze_transforms = cmds.checkBoxGrp(label="Freeze Transforms:", value1=False, 
                                               columnWidth=[(1, 120), (2, 250)])
        
        cmds.separator(height=10)
        
        # Add reset transform buttons
        cmds.button(label="Reset Selected", 
                   command=self.reset_selected_transforms, 
                   height=40,
                   backgroundColor=[0.2, 0.6, 0.2])
        
        cmds.button(label="Reset Scale & Keep Shape", 
                   command=self.reset_scale_preserve_shape, 
                   height=40,
                   backgroundColor=[0.2, 0.4, 0.6],
                   annotation="Reset scale to 1 while preserving the current shape of the mesh")
        
        cmds.button(label="Reset All", 
                   command=self.reset_all_transforms, 
                   height=30,
                   backgroundColor=[0.6, 0.2, 0.2])
        
        cmds.setParent("..")  # Exit the column layout
        cmds.setParent("..")  # Exit the frame layout
        
        # Add pivot options
        cmds.frameLayout(label="Pivot Options", collapsable=True, collapse=False)
        cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=5)
        
        cmds.button(label="Center Pivot", 
                   command=self.center_pivot, 
                   height=30)
        
        cmds.button(label="Reset Pivot", 
                   command=self.reset_pivot, 
                   height=30)
        
        cmds.setParent("..")  # Exit the column layout
        cmds.setParent("..")  # Exit the frame layout
        
        cmds.setParent("..")  # Exit the transform tab
        
        # Create Scene Cleanup tab
        cleanup_tab = cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=5)
        
        cmds.frameLayout(label="Delete Options", collapsable=True, collapse=False)
        cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=5)
        
        # Add delete options
        self.delete_history = cmds.checkBoxGrp(label="Delete History:", value1=True, 
                                            columnWidth=[(1, 120), (2, 250)])
        self.delete_unused_nodes = cmds.checkBoxGrp(label="Delete Unused Nodes:", value1=True, 
                                                 columnWidth=[(1, 120), (2, 250)])
        self.delete_display_layers = cmds.checkBoxGrp(label="Delete Display Layers:", value1=False, 
                                                   columnWidth=[(1, 120), (2, 250)])
        self.delete_anim_layers = cmds.checkBoxGrp(label="Delete Anim Layers:", value1=False, 
                                                columnWidth=[(1, 120), (2, 250)])
        
        cmds.separator(height=10)
        
        # Add delete buttons
        cmds.button(label="Clean Selected", 
                   command=self.cleanup_selected, 
                   height=40,
                   backgroundColor=[0.2, 0.6, 0.2])
        
        cmds.button(label="Clean Scene", 
                   command=self.cleanup_scene, 
                   height=30,
                   backgroundColor=[0.6, 0.2, 0.2])
        
        cmds.setParent("..")  # Exit the column layout
        cmds.setParent("..")  # Exit the frame layout
        
        # Add optimize options
        cmds.frameLayout(label="Optimize Scene", collapsable=True, collapse=False)
        cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=5)
        
        cmds.button(label="Remove Namespaces", 
                   command=self.remove_namespaces, 
                   height=30)
        
        cmds.button(label="Optimize Scene Size", 
                   command=self.optimize_scene, 
                   height=30)
        
        cmds.setParent("..")  # Exit the column layout
        cmds.setParent("..")  # Exit the frame layout
        
        cmds.setParent("..")  # Exit the cleanup tab
        
        # Set up the tabs
        cmds.tabLayout(self.tabs, edit=True, tabLabel=((transform_tab, "Transform Reset"), (cleanup_tab, "Scene Cleanup")))
        
        cmds.setParent(main_layout)  # Return to main layout
        
        # Add status text
        self.status_text = cmds.text(label="Ready - Select objects and use the buttons above", align="center")
        
        # Show the window
        cmds.showWindow(window)
    
    def reset_selected_transforms(self, *args):
        """Reset transforms on selected objects"""
        selected = cmds.ls(selection=True)
        
        if not selected:
            cmds.confirmDialog(title="No Selection", 
                              message="Please select at least one object to reset transforms.",
                              button=["OK"])
            cmds.text(self.status_text, edit=True, label="Error: No objects selected")
            return
        
        # Get options
        reset_translate = cmds.checkBoxGrp(self.reset_translate, query=True, value1=True)
        reset_rotate = cmds.checkBoxGrp(self.reset_rotate, query=True, value1=True)
        reset_scale = cmds.checkBoxGrp(self.reset_scale, query=True, value1=True)
        freeze = cmds.checkBoxGrp(self.freeze_transforms, query=True, value1=True)
        
        # Process each selected object
        for obj in selected:
            try:
                # Get preserve shape option
                preserve_shape = cmds.checkBoxGrp(self.preserve_shape, query=True, value1=True)
                
                # Reset transforms
                if reset_translate:
                    cmds.setAttr(f"{obj}.translateX", 0)
                    cmds.setAttr(f"{obj}.translateY", 0)
                    cmds.setAttr(f"{obj}.translateZ", 0)
                
                if reset_rotate:
                    cmds.setAttr(f"{obj}.rotateX", 0)
                    cmds.setAttr(f"{obj}.rotateY", 0)
                    cmds.setAttr(f"{obj}.rotateZ", 0)
                
                if reset_scale:
                    if preserve_shape:
                        # Get current scale values
                        current_scale_x = cmds.getAttr(f"{obj}.scaleX")
                        current_scale_y = cmds.getAttr(f"{obj}.scaleY")
                        current_scale_z = cmds.getAttr(f"{obj}.scaleZ")
                        
                        # Check if this is a mesh
                        shapes = cmds.listRelatives(obj, shapes=True, type="mesh") or []
                        if shapes:
                            # Duplicate the mesh to preserve its current shape
                            temp = cmds.duplicate(obj, name=f"{obj}_temp")[0]
                            
                            # Freeze transformations on the duplicate to bake in the scale
                            cmds.makeIdentity(temp, apply=True, scale=True)
                            
                            # Reset scale on original object
                            cmds.setAttr(f"{obj}.scaleX", 1)
                            cmds.setAttr(f"{obj}.scaleY", 1)
                            cmds.setAttr(f"{obj}.scaleZ", 1)
                            
                            # Transfer shape from temp to original
                            temp_shape = cmds.listRelatives(temp, shapes=True)[0]
                            orig_shape = cmds.listRelatives(obj, shapes=True)[0]
                            
                            # Use blendShape to transfer the shape
                            blend_node = cmds.blendShape(temp_shape, orig_shape, weight=[0, 1])[0]
                            
                            # Delete the temporary objects
                            cmds.delete(temp)
                            cmds.delete(blend_node)
                        else:
                            # Not a mesh, just reset scale
                            cmds.setAttr(f"{obj}.scaleX", 1)
                            cmds.setAttr(f"{obj}.scaleY", 1)
                            cmds.setAttr(f"{obj}.scaleZ", 1)
                    else:
                        # Simply reset scale without preserving shape
                        cmds.setAttr(f"{obj}.scaleX", 1)
                        cmds.setAttr(f"{obj}.scaleY", 1)
                        cmds.setAttr(f"{obj}.scaleZ", 1)
                
                # Freeze transforms if option is set
                if freeze:
                    cmds.makeIdentity(obj, apply=True, translate=reset_translate, rotate=reset_rotate, scale=reset_scale)
            
            except Exception as e:
                cmds.warning(f"Error processing {obj}: {str(e)}")
        
        # Update status
        cmds.text(self.status_text, edit=True, label=f"Reset transforms on {len(selected)} objects")
    
    def reset_scale_preserve_shape(self, *args):
        """Reset scale to 1 while preserving the current shape of the mesh"""
        selected = cmds.ls(selection=True)
        
        if not selected:
            cmds.confirmDialog(title="No Selection", 
                              message="Please select at least one object to reset scale.",
                              button=["OK"])
            cmds.text(self.status_text, edit=True, label="Error: No objects selected")
            return
        
        # Process each selected object
        processed_count = 0
        for obj in selected:
            try:
                # Check if this is a mesh
                shapes = cmds.listRelatives(obj, shapes=True, type="mesh") or []
                if shapes:
                    # Get current scale values
                    current_scale_x = cmds.getAttr(f"{obj}.scaleX")
                    current_scale_y = cmds.getAttr(f"{obj}.scaleY")
                    current_scale_z = cmds.getAttr(f"{obj}.scaleZ")
                    
                    # Only process if scale is not already 1,1,1
                    if not (abs(current_scale_x-1) < 0.001 and abs(current_scale_y-1) < 0.001 and abs(current_scale_z-1) < 0.001):
                        # Duplicate the mesh to preserve its current shape
                        temp = cmds.duplicate(obj, name=f"{obj}_temp")[0]
                        
                        # Freeze transformations on the duplicate to bake in the scale
                        cmds.makeIdentity(temp, apply=True, scale=True)
                        
                        # Reset scale on original object
                        cmds.setAttr(f"{obj}.scaleX", 1)
                        cmds.setAttr(f"{obj}.scaleY", 1)
                        cmds.setAttr(f"{obj}.scaleZ", 1)
                        
                        # Transfer shape from temp to original
                        temp_shape = cmds.listRelatives(temp, shapes=True)[0]
                        orig_shape = cmds.listRelatives(obj, shapes=True)[0]
                        
                        # Use blendShape to transfer the shape
                        blend_node = cmds.blendShape(temp_shape, orig_shape, weight=[0, 1])[0]
                        
                        # Delete the temporary objects
                        cmds.delete(temp)
                        cmds.delete(blend_node)
                        
                        processed_count += 1
                else:
                    # Not a mesh, just reset scale
                    cmds.setAttr(f"{obj}.scaleX", 1)
                    cmds.setAttr(f"{obj}.scaleY", 1)
                    cmds.setAttr(f"{obj}.scaleZ", 1)
                    processed_count += 1
            except Exception as e:
                cmds.warning(f"Error processing {obj}: {str(e)}")
        
        # Update status
        if processed_count > 0:
            cmds.text(self.status_text, edit=True, label=f"Reset scale on {processed_count} objects while preserving shape")
        else:
            cmds.text(self.status_text, edit=True, label="No objects were processed")
    
    def reset_all_transforms(self, *args):
        """Reset transforms on all transformable objects"""
        # Get all transformable objects
        all_transforms = cmds.ls(type="transform")
        
        # Select them all
        cmds.select(all_transforms)
        
        # Use the reset selected function
        self.reset_selected_transforms()
    
    def center_pivot(self, *args):
        """Center pivot on selected objects"""
        selected = cmds.ls(selection=True)
        
        if not selected:
            cmds.confirmDialog(title="No Selection", 
                              message="Please select at least one object to center pivot.",
                              button=["OK"])
            cmds.text(self.status_text, edit=True, label="Error: No objects selected")
            return
        
        # Center pivot on each object
        for obj in selected:
            try:
                cmds.xform(obj, centerPivots=True)
            except Exception as e:
                cmds.warning(f"Error centering pivot on {obj}: {str(e)}")
        
        # Update status
        cmds.text(self.status_text, edit=True, label=f"Centered pivot on {len(selected)} objects")
    
    def reset_pivot(self, *args):
        """Reset pivot to origin on selected objects"""
        selected = cmds.ls(selection=True)
        
        if not selected:
            cmds.confirmDialog(title="No Selection", 
                              message="Please select at least one object to reset pivot.",
                              button=["OK"])
            cmds.text(self.status_text, edit=True, label="Error: No objects selected")
            return
        
        # Reset pivot on each object
        for obj in selected:
            try:
                # Store the current pivot position in world space
                pivot_pos = cmds.xform(obj, query=True, worldSpace=True, rotatePivot=True)
                
                # Move the object to compensate for the pivot change
                cmds.move(pivot_pos[0], pivot_pos[1], pivot_pos[2], obj, absolute=True, worldSpace=True)
                
                # Reset the pivot to origin
                cmds.xform(obj, worldSpace=True, pivots=[0, 0, 0])
            except Exception as e:
                cmds.warning(f"Error resetting pivot on {obj}: {str(e)}")
        
        # Update status
        cmds.text(self.status_text, edit=True, label=f"Reset pivot on {len(selected)} objects")
    
    def cleanup_selected(self, *args):
        """Cleanup selected objects"""
        selected = cmds.ls(selection=True)
        
        if not selected:
            cmds.confirmDialog(title="No Selection", 
                              message="Please select at least one object to clean up.",
                              button=["OK"])
            cmds.text(self.status_text, edit=True, label="Error: No objects selected")
            return
        
        # Get options
        delete_history = cmds.checkBoxGrp(self.delete_history, query=True, value1=True)
        
        # Process each selected object
        for obj in selected:
            try:
                # Delete history if option is set
                if delete_history:
                    cmds.delete(obj, constructionHistory=True)
            
            except Exception as e:
                cmds.warning(f"Error cleaning up {obj}: {str(e)}")
        
        # Update status
        cmds.text(self.status_text, edit=True, label=f"Cleaned up {len(selected)} objects")
    
    def cleanup_scene(self, *args):
        """Cleanup the entire scene"""
        # Get options
        delete_history = cmds.checkBoxGrp(self.delete_history, query=True, value1=True)
        delete_unused_nodes = cmds.checkBoxGrp(self.delete_unused_nodes, query=True, value1=True)
        delete_display_layers = cmds.checkBoxGrp(self.delete_display_layers, query=True, value1=True)
        delete_anim_layers = cmds.checkBoxGrp(self.delete_anim_layers, query=True, value1=True)
        
        # Perform cleanup operations
        try:
            # Delete all history
            if delete_history:
                cmds.delete(all=True, constructionHistory=True)
            
            # Delete unused nodes
            if delete_unused_nodes:
                mel.eval("MLdeleteUnused;")
            
            # Delete display layers
            if delete_display_layers:
                layers = cmds.ls(type="displayLayer")
                # Remove the default layer from the list
                if "defaultLayer" in layers:
                    layers.remove("defaultLayer")
                if layers:
                    cmds.delete(layers)
            
            # Delete animation layers
            if delete_anim_layers:
                anim_layers = cmds.ls(type="animLayer")
                if anim_layers:
                    cmds.delete(anim_layers)
        
        except Exception as e:
            cmds.warning(f"Error during scene cleanup: {str(e)}")
        
        # Update status
        cmds.text(self.status_text, edit=True, label="Scene cleanup complete")
    
    def remove_namespaces(self, *args):
        """Remove all namespaces from the scene"""
        try:
            # Get all namespaces
            namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
            
            # Filter out default namespaces
            default_namespaces = ['UI', 'shared']
            namespaces = [ns for ns in namespaces if ns not in default_namespaces]
            
            # Sort namespaces by hierarchy depth (process child namespaces first)
            namespaces.sort(key=lambda x: x.count(':'), reverse=True)
            
            # Remove each namespace
            removed_count = 0
            for namespace in namespaces:
                try:
                    # Move all objects to root namespace
                    cmds.namespace(moveNamespace=[namespace, ':'], force=True)
                    # Remove the empty namespace
                    cmds.namespace(removeNamespace=namespace)
                    removed_count += 1
                except Exception as e:
                    cmds.warning(f"Error removing namespace {namespace}: {str(e)}")
            
            # Update status
            cmds.text(self.status_text, edit=True, label=f"Removed {removed_count} namespaces")
        
        except Exception as e:
            cmds.warning(f"Error removing namespaces: {str(e)}")
    
    def optimize_scene(self, *args):
        """Optimize the scene to reduce file size"""
        try:
            # Delete unused nodes
            mel.eval("MLdeleteUnused;")
            
            # Clear undo queue
            cmds.flushUndo()
            
            # Clear the construction history
            cmds.delete(all=True, constructionHistory=True)
            
            # Update status
            cmds.text(self.status_text, edit=True, label="Scene optimized")
        
        except Exception as e:
            cmds.warning(f"Error optimizing scene: {str(e)}")

# Function to run the tool
def run():
    CleanupTool()

# Auto-run when the script is imported
if __name__ == "__main__":
    run()