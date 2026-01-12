import maya.cmds as cmds
import maya.mel as mel

class SkinningTool:
    def __init__(self):
        # Initialize variables to store selections
        self.selected_joints = []
        self.selected_meshes = []
        
        # Create the UI
        self.create_ui()
    
    def create_ui(self):
        """Create the UI for the Skinning tool"""
        # Check if the window already exists and delete it
        window_name = "skinningToolUI"
        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name)
        
        # Create the window
        window = cmds.window(window_name, title="Skinning Tool", widthHeight=(450, 600))
        
        # Create the main layout
        main_layout = cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=10, columnWidth=450)
        
        # Add a header
        cmds.text(label="Skinning Tool", font="boldLabelFont", height=30)
        cmds.separator(height=10)
        
        # Add description
        cmds.text(label="This tool helps you bind meshes to joints using Geodesic Voxel Binding (GVB).", align="left")
        
        cmds.separator(height=20)
        
        # Create tab layout for the two forms
        self.tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        
        # ===== JOINTS TAB =====
        joints_tab = cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=10)
        
        cmds.text(label="Step 1: Select Joints for Skinning", font="boldLabelFont", height=30)
        cmds.text(label="Select the joints you want to use for skinning.", align="left")
        
        # Add buttons for joint selection
        cmds.button(label="Select All Joints in Scene", 
                   command=self.select_all_joints, 
                   height=30)
        
        cmds.button(label="Select Root Joint and Hierarchy", 
                   command=self.select_joint_hierarchy, 
                   height=30)
        
        cmds.separator(height=10)
        
        # Add button to store selected joints
        cmds.button(label="Store Selected Joints", 
                   command=self.store_selected_joints, 
                   height=40,
                   backgroundColor=[0.2, 0.6, 0.2])
        
        # Add text field to display selected joints
        cmds.text(label="Selected Joints:", align="left")
        self.joints_text_field = cmds.scrollField(editable=False, wordWrap=True, height=150)
        
        # Add button to clear selected joints
        cmds.button(label="Clear Selected Joints", 
                   command=self.clear_selected_joints, 
                   height=30)
        
        cmds.setParent("..")  # Exit joints tab layout
        
        # ===== MESHES TAB =====
        meshes_tab = cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=10)
        
        cmds.text(label="Step 2: Select Meshes and Bind", font="boldLabelFont", height=30)
        cmds.text(label="Select the meshes you want to bind to the stored joints.", align="left")
        
        # Add buttons for mesh selection
        cmds.button(label="Select All Meshes in Scene", 
                   command=self.select_all_meshes, 
                   height=30)
        
        cmds.separator(height=10)
        
        # Add buttons for mesh selection
        cmds.button(label="Store Selected Meshes", 
                   command=self.store_selected_meshes, 
                   height=30,
                   backgroundColor=[0.2, 0.6, 0.2])
        
        cmds.button(label="Check & Fix Mesh Geometry", 
                   command=self.check_and_fix_meshes, 
                   height=30,
                   backgroundColor=[0.6, 0.6, 0.2],
                   annotation="Check stored meshes for non-manifold geometry and fix issues")
        
        cmds.button(label="Clear Stored Meshes", 
                   command=self.clear_selected_meshes, 
                   height=30)
        
        cmds.text(label="Selected Meshes:", align="left")
        self.meshes_text_field = cmds.scrollField(editable=False, wordWrap=True, height=150)
        
        cmds.button(label="Clear Selected Meshes", 
                   command=self.clear_selected_meshes, 
                   height=30)
        
        cmds.setParent("..")  # Exit meshes tab layout
        
        # Set the tab labels
        cmds.tabLayout(self.tabs, edit=True, tabLabel=((joints_tab, "Joints Selection"), (meshes_tab, "Meshes & Binding")))
        
        cmds.setParent(main_layout)  # Return to main layout
        
        # Add skinning options
        cmds.separator(height=20)
        cmds.frameLayout(label="Binding Options", collapsable=True, collapse=False)
        
        options_layout = cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=5)
        
        # Add binding method options
        self.binding_method = cmds.optionMenuGrp(label="Binding Method:", columnWidth=[(1, 120), (2, 250)])
        cmds.menuItem(label="Default")
        cmds.menuItem(label="Quick Rig (HumanIK)")
        cmds.menuItem(label="Geodesic Voxel")
        cmds.menuItem(label="Heat Map")
        
        # Add max influences option
        self.max_influences = cmds.intSliderGrp(label="Max Influences:", field=True, 
                                              minValue=1, maxValue=10, value=4, 
                                              columnWidth=[(1, 120), (2, 50), (3, 200)])
        
        # Add normalize weights option
        self.normalize_weights = cmds.checkBoxGrp(label="Normalize Weights:", value1=True, 
                                                columnWidth=[(1, 120), (2, 250)])
        
        # Add post-smooth option
        self.post_smooth = cmds.intSliderGrp(label="Post Smooth:", field=True, 
                                           minValue=0, maxValue=10, value=2, 
                                           columnWidth=[(1, 120), (2, 50), (3, 200)])
        
        cmds.setParent("..")  # Exit options layout
        cmds.setParent("..")  # Exit frame layout
        
        # Add bind button
        cmds.separator(height=20)
        cmds.button(label="BIND SKIN", 
                   command=self.bind_skin, 
                   height=60,
                   backgroundColor=[0.8, 0.3, 0.3])
        
        # Add status text
        self.status_text = cmds.text(label="Ready", align="center")
        
        # Show the window
        cmds.showWindow(window)
    
    def select_all_joints(self, *args):
        """Select all joints in the scene"""
        all_joints = cmds.ls(type="joint")
        if all_joints:
            cmds.select(all_joints)
            cmds.text(self.status_text, edit=True, label=f"Selected {len(all_joints)} joints")
        else:
            cmds.confirmDialog(title="No Joints", 
                              message="No joints found in the scene.",
                              button=["OK"])
            cmds.text(self.status_text, edit=True, label="No joints found")
    
    def select_joint_hierarchy(self, *args):
        """Select a root joint and its hierarchy"""
        # Prompt user to select a root joint
        cmds.confirmDialog(title="Select Root Joint", 
                          message="Please select a root joint in the scene, then click OK.",
                          button=["OK"])
        
        # Get the selected joint
        selected = cmds.ls(selection=True, type="joint")
        
        if not selected:
            cmds.confirmDialog(title="No Selection", 
                              message="No joint selected.",
                              button=["OK"])
            return
        
        # Get the first selected joint
        root_joint = selected[0]
        
        # Select the joint and its hierarchy
        joint_hierarchy = cmds.listRelatives(root_joint, allDescendents=True, type="joint", fullPath=True) or []
        joint_hierarchy.append(root_joint)
        
        cmds.select(joint_hierarchy)
        cmds.text(self.status_text, edit=True, label=f"Selected {len(joint_hierarchy)} joints in hierarchy")
    
    def store_selected_joints(self, *args):
        """Store the currently selected joints"""
        selected_joints = cmds.ls(selection=True, type="joint")
        
        if not selected_joints:
            cmds.confirmDialog(title="No Selection", 
                              message="No joints selected.",
                              button=["OK"])
            return
        
        # Store the selected joints
        self.selected_joints = selected_joints
        
        # Update the text field
        joints_text = "\n".join(selected_joints)
        cmds.scrollField(self.joints_text_field, edit=True, text=joints_text)
        
        # Update status
        cmds.text(self.status_text, edit=True, label=f"Stored {len(selected_joints)} joints")
        
        # Switch to the meshes tab
        cmds.tabLayout(self.tabs, edit=True, selectTabIndex=2)
    
    def clear_selected_joints(self, *args):
        """Clear the stored joints"""
        self.selected_joints = []
        cmds.scrollField(self.joints_text_field, edit=True, text="")
        cmds.text(self.status_text, edit=True, label="Cleared stored joints")
    
    def select_all_meshes(self, *args):
        """Select all meshes in the scene"""
        # Find all mesh shapes
        all_mesh_shapes = cmds.ls(type="mesh")
        
        # Get the transform nodes (parents) of the mesh shapes
        all_meshes = []
        for mesh_shape in all_mesh_shapes:
            parents = cmds.listRelatives(mesh_shape, parent=True, fullPath=True)
            if parents:
                all_meshes.extend(parents)
        
        # Remove duplicates
        all_meshes = list(set(all_meshes))
        
        if all_meshes:
            cmds.select(all_meshes)
            cmds.text(self.status_text, edit=True, label=f"Selected {len(all_meshes)} meshes")
        else:
            cmds.confirmDialog(title="No Meshes", 
                              message="No meshes found in the scene.",
                              button=["OK"])
            cmds.text(self.status_text, edit=True, label="No meshes found")
    
    def store_selected_meshes(self, *args):
        """Store the currently selected meshes"""
        # Get selected objects
        selected = cmds.ls(selection=True, long=True)
        
        # Filter for mesh objects
        selected_meshes = []
        for obj in selected:
            # Check if the object is a transform with a mesh shape
            shapes = cmds.listRelatives(obj, shapes=True, type="mesh")
            if shapes:
                selected_meshes.append(obj)
        
        if not selected_meshes:
            cmds.confirmDialog(title="No Selection", 
                              message="No meshes selected.",
                              button=["OK"])
            return
        
        # Store the selected meshes
        self.selected_meshes = selected_meshes
        
        # Update the text field
        meshes_text = "\n".join(selected_meshes)
        cmds.scrollField(self.meshes_text_field, edit=True, text=meshes_text)
        
        # Update status
        cmds.text(self.status_text, edit=True, label=f"Stored {len(selected_meshes)} meshes")
    
    def clear_selected_meshes(self, *args):
        """Clear the stored meshes"""
        self.selected_meshes = []
        cmds.scrollField(self.meshes_text_field, edit=True, text="")
        cmds.text(self.status_text, edit=True, label="Cleared stored meshes")
    
    def check_and_fix_meshes(self, *args):
        """Check stored meshes for non-manifold geometry and offer to fix them"""
        if not self.selected_meshes:
            cmds.confirmDialog(title="No Meshes", 
                              message="No meshes have been stored. Please store some meshes first.",
                              button=["OK"])
            return
        
        # Track results
        checked_count = 0
        fixed_count = 0
        problem_count = 0
        skipped_count = 0
        
        # Process each stored mesh
        for mesh in self.selected_meshes:
            # Check if the mesh still exists
            if not cmds.objExists(mesh):
                continue
            
            checked_count += 1
            
            try:
                # Select the mesh
                cmds.select(mesh)
                # Check for non-manifold geometry
                non_manifold_verts = cmds.polyInfo(nonManifoldVertices=True) or []
                non_manifold_edges = cmds.polyInfo(nonManifoldEdges=True) or []
                
                if non_manifold_verts or non_manifold_edges:
                    problem_count += 1
                    # Ask user if they want to fix this mesh
                    result = cmds.confirmDialog(
                        title="Non-Manifold Geometry Detected",
                        message=f"Mesh {mesh} has non-manifold geometry which may cause binding issues.\nWould you like to fix this mesh?",
                        button=["Fix", "Skip", "Stop Checking"],
                        defaultButton="Fix",
                        cancelButton="Stop Checking",
                        dismissString="Stop Checking")
                    
                    if result == "Fix":
                        # Try to fix the mesh
                        fixed = self.fix_non_manifold_geometry(mesh)
                        if fixed:
                            fixed_count += 1
                            cmds.warning(f"Fixed non-manifold geometry on {mesh}.")
                        else:
                            cmds.warning(f"Could not fully fix non-manifold geometry on {mesh}.")
                    elif result == "Skip":
                        skipped_count += 1
                        continue
                    else:  # Stop Checking
                        break
            except Exception as e:
                cmds.warning(f"Error checking mesh {mesh}: {str(e)}")
        
        # Update status
        status_msg = f"Checked {checked_count} meshes. Found {problem_count} with issues. Fixed {fixed_count}. Skipped {skipped_count}."
        cmds.text(self.status_text, edit=True, label=status_msg)
        
        # Show summary dialog
        cmds.confirmDialog(title="Mesh Check Complete", 
                          message=status_msg,
                          button=["OK"])
    
    def fix_non_manifold_geometry(self, mesh):
        """Attempt to fix non-manifold geometry on the given mesh"""
        try:
            # Select the mesh
            cmds.select(mesh)
            
            # Make a duplicate to work on
            temp_mesh = cmds.duplicate(mesh, name=f"{mesh}_cleanup_temp")[0]
            
            # Try to fix non-manifold vertices
            cmds.select(temp_mesh)
            cmds.polyCleanupArgList(1, [
                "0",            # Apply to all selected objects
                "1",            # Consider non-manifold vertices
                "1",            # Consider non-manifold edges
                "0",            # Consider lamina faces
                "1",            # Consider zero-area faces
                "0",            # Consider zero-length edges
                "0",            # Consider zero-map-area faces
                "0",            # Consider face with holes
                "0",            # Consider holed faces
                "0",            # Consider non-planar faces
                "0",            # Consider concave faces
                "0",            # Consider self-intersecting faces
                "0",            # Consider object with invalid components
                "1",            # Delete selected components
                "0",            # Don't fix selected components
                "0.0001"        # Tolerance
            ])
            
            # Check if the cleanup was successful
            cmds.select(temp_mesh)
            non_manifold_verts_after = cmds.polyInfo(nonManifoldVertices=True) or []
            non_manifold_edges_after = cmds.polyInfo(nonManifoldEdges=True) or []
            
            if not non_manifold_verts_after and not non_manifold_edges_after:
                # Cleanup successful, transfer the cleaned shape back to original
                # First, delete the original shape
                orig_shapes = cmds.listRelatives(mesh, shapes=True) or []
                if orig_shapes:
                    cmds.delete(orig_shapes)
                
                # Then, duplicate the cleaned shape and parent it to the original transform
                temp_shapes = cmds.listRelatives(temp_mesh, shapes=True, fullPath=True) or []
                for shape in temp_shapes:
                    cmds.parent(shape, mesh, shape=True, relative=True)
                
                # Delete the temporary mesh transform
                cmds.delete(temp_mesh)
                
                # Rename the shape node
                new_shapes = cmds.listRelatives(mesh, shapes=True) or []
                for i, shape in enumerate(new_shapes):
                    cmds.rename(shape, f"{mesh}Shape{i if i > 0 else ''}")
                
                return True
            else:
                # Cleanup wasn't fully successful
                cmds.delete(temp_mesh)
                return False
        
        except Exception as e:
            cmds.warning(f"Error fixing non-manifold geometry: {str(e)}")
            # Try to clean up if temp mesh exists
            if cmds.objExists(f"{mesh}_cleanup_temp"):
                cmds.delete(f"{mesh}_cleanup_temp")
            return False
    
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
    
    def bind_skin(self, *args):
        """Bind the stored meshes to the stored joints"""
        # Check if we have both joints and meshes
        if not self.selected_joints:
            cmds.confirmDialog(title="No Joints", 
                              message="No joints have been stored. Please go to the Joints tab and store some joints first.",
                              button=["OK"])
            return
        
        if not self.selected_meshes:
            cmds.confirmDialog(title="No Meshes", 
                              message="No meshes have been stored. Please store some meshes first.",
                              button=["OK"])
            return
        
        # Get binding options
        binding_method_index = cmds.optionMenuGrp(self.binding_method, query=True, select=True)
        max_influences = cmds.intSliderGrp(self.max_influences, query=True, value=True)
        normalize = cmds.checkBoxGrp(self.normalize_weights, query=True, value1=True)
        post_smooth = cmds.intSliderGrp(self.post_smooth, query=True, value=True)
        
        # Check if using Quick Rig method
        use_quick_rig = (binding_method_index == 2)  # Quick Rig is option 2
        
        # Set the binding method - using integer values as Maya expects
        binding_method = None
        use_bind_method_flag = True
        
        if binding_method_index == 3:  # Geodesic Voxel
            binding_method = 2  # Integer value for Geodesic Voxel binding
        elif binding_method_index == 4:  # Heat Map
            binding_method = 1  # Integer value for Heat Map binding
        elif binding_method_index == 1:  # Default
            binding_method = 0  # Integer value for Closest Distance binding
        else:  # Quick Rig (2)
            use_bind_method_flag = False  # Don't use bindMethod flag for Quick Rig
        
        # Perform the binding for each mesh
        bound_count = 0
        for mesh in self.selected_meshes:
            try:
                # Check if the mesh still exists
                if not cmds.objExists(mesh):
                    continue
                
                # Check mesh for non-manifold geometry before binding
                has_non_manifold = False
                try:
                    # Select the mesh
                    cmds.select(mesh)
                    # Check for non-manifold geometry using Maya's cleanup tool
                    non_manifold_verts = cmds.polyInfo(nonManifoldVertices=True) or []
                    non_manifold_edges = cmds.polyInfo(nonManifoldEdges=True) or []
                    
                    if non_manifold_verts or non_manifold_edges:
                        has_non_manifold = True
                        # Ask user if they want to attempt to fix the mesh
                        result = cmds.confirmDialog(
                            title="Non-Manifold Geometry Detected",
                            message=f"Mesh {mesh} has non-manifold geometry which may cause binding issues.\nWould you like to attempt to fix the mesh?",
                            button=["Fix and Continue", "Continue Without Fixing", "Skip This Mesh"],
                            defaultButton="Fix and Continue",
                            cancelButton="Skip This Mesh",
                            dismissString="Skip This Mesh")
                        
                        if result == "Fix and Continue":
                            # Try to fix the mesh
                            fixed = self.fix_non_manifold_geometry(mesh)
                            if fixed:
                                has_non_manifold = False
                                cmds.warning(f"Fixed non-manifold geometry on {mesh}.")
                            else:
                                cmds.warning(f"Could not fully fix non-manifold geometry on {mesh}. Using closest distance binding.")
                        elif result == "Skip This Mesh":
                            cmds.warning(f"Skipping binding for mesh {mesh}.")
                            continue
                        else:  # Continue Without Fixing
                            cmds.warning(f"Continuing with non-manifold geometry on {mesh}. Using closest distance binding.")
                except Exception as e:
                    # If check fails, assume it might have issues
                    cmds.warning(f"Error checking mesh geometry: {str(e)}")
                
                # If using heat map or geodesic and mesh has non-manifold geometry, fall back to closest distance
                if has_non_manifold and binding_method in [1, 2]:  # Heat map or geodesic
                    binding_method = 0  # Fall back to closest distance
                
                # Handle binding based on the selected method
                if use_quick_rig:
                    # Check if HumanIK is available
                    hik_available = True
                    try:
                        # Try to run a simple HumanIK command to check if it's available
                        mel.eval('hikGlobalUtils')
                    except Exception:
                        hik_available = False
                    
                    if not hik_available:
                        cmds.warning(f"HumanIK not available. Using default binding method for {mesh}")
                        # Fall back to default binding
                        cmds.select(self.selected_joints, mesh)
                        skin_cluster = cmds.skinCluster(
                            self.selected_joints,
                            mesh,
                            tsb=True,  # To selected bones
                            bm=0,  # Default binding method (closest distance)
                            nw=normalize,  # Use nw instead of normalizeWeights
                            mi=max_influences,  # Use mi instead of maximumInfluences
                            n=f"{mesh.split('|')[-1]}_skinCluster"  # Use n instead of name
                        )
                    else:
                        # Use Quick Rig (HumanIK) method
                        # First select the mesh, then the joints
                        cmds.select(mesh, replace=True)
                        cmds.select(self.selected_joints, add=True)
                        
                        try:
                            # Use the Quick Rig binding method via MEL
                            mel.eval(f'hikBindToSelectedJoints {int(normalize)} {max_influences}')
                            
                            # Get the created skin cluster name
                            skin_cluster = self.find_skin_clusters(mesh)[0] if self.find_skin_clusters(mesh) else None
                        except Exception as e:
                            cmds.warning(f"Error using Quick Rig binding: {str(e)}. Using default binding method for {mesh}")
                            # Fall back to default binding
                            cmds.select(self.selected_joints, mesh)
                            skin_cluster = cmds.skinCluster(
                                self.selected_joints,
                                mesh,
                                tsb=True,  # To selected bones
                                bm=0,  # Default binding method (closest distance)
                                nw=normalize,  # Use nw instead of normalizeWeights
                                mi=max_influences,  # Use mi instead of maximumInfluences
                                n=f"{mesh.split('|')[-1]}_skinCluster"  # Use n instead of name
                            )
                else:
                    # Select the mesh and joints
                    cmds.select(self.selected_joints, mesh)
                    
                    # Bind the skin
                    if use_bind_method_flag and binding_method is not None:
                        # Use specific binding method with integer value
                        skin_cluster = cmds.skinCluster(
                            self.selected_joints,
                            mesh,
                            tsb=True,  # To selected bones
                            bm=binding_method,  # Use bm instead of bindMethod
                            nw=normalize,  # Use nw instead of normalizeWeights
                            mi=max_influences,  # Use mi instead of maximumInfluences
                            n=f"{mesh.split('|')[-1]}_skinCluster"  # Use n instead of name
                        )
                    else:
                        # Use default binding method
                        skin_cluster = cmds.skinCluster(
                            self.selected_joints,
                            mesh,
                            tsb=True,  # To selected bones
                            nw=normalize,  # Use nw instead of normalizeWeights
                            mi=max_influences,  # Use mi instead of maximumInfluences
                            n=f"{mesh.split('|')[-1]}_skinCluster"  # Use n instead of name
                        )
                
                # Apply post-smooth if specified
                if post_smooth > 0:
                    cmds.skinCluster(skin_cluster, edit=True, smoothWeights=post_smooth)
                
                bound_count += 1
                
            except Exception as e:
                cmds.warning(f"Error binding {mesh}: {str(e)}")
        
        # Update status
        if bound_count > 0:
            cmds.text(self.status_text, edit=True, label=f"Successfully bound {bound_count} meshes")
            cmds.confirmDialog(title="Binding Complete", 
                              message=f"Successfully bound {bound_count} meshes to {len(self.selected_joints)} joints.",
                              button=["OK"])
        else:
            cmds.text(self.status_text, edit=True, label="No meshes were bound")

# Function to run the tool
def run():
    SkinningTool()

# Auto-run when the script is imported
if __name__ == "__main__":
    run()