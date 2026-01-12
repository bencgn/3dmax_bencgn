import bpy
import bmesh
from bpy.props import StringProperty

class MATERIAL_PT_CheckBaseColorTexture(bpy.types.Panel):
    """Panel for checking materials with Base Color connected to textures"""
    bl_label = "Check Base Color Texture"
    bl_idname = "MATERIAL_PT_check_base_color_texture"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    
    def draw(self, context):
        layout = self.layout
        
        # Check button
        row = layout.row()
        row.operator("material.check_base_color_texture", text="Check Base Color")
        
        # Info text
        box = layout.box()
        box.label(text="Selects faces with materials")
        box.label(text="that have Base Color connected")
        box.label(text="to a texture node")
        
        # Separator
        layout.separator()
        
        # Material rename section
        box = layout.box()
        box.label(text="Change Material Names")
        
        # Prefix input
        box.prop(context.scene, "material_name_prefix", text="New Prefix")
        
        # Buttons
        row = box.row()
        row.operator("material.add_prefix_to_selected", text="Add Prefix to Selected")
        
        row = box.row()
        row.operator("material.add_prefix_to_all", text="Add Prefix to All")


class MATERIAL_OT_CheckBaseColorTexture(bpy.types.Operator):
    """Select faces with materials that have Base Color connected to a texture"""
    bl_idname = "material.check_base_color_texture"
    bl_label = "Check Base Color Texture"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Ensure we're in edit mode
        if context.object.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        # Switch to face selection mode
        bpy.ops.mesh.select_mode(type='FACE')
        
        # Deselect all faces first
        bpy.ops.mesh.select_all(action='DESELECT')
        
        obj = context.active_object
        mesh = obj.data
        
        # Get material slots and their indices
        material_slots = obj.material_slots
        textured_material_indices = []
        
        # Find materials that have Base Color connected to a texture
        for i, slot in enumerate(material_slots):
            if slot.material and slot.material.use_nodes:
                material = slot.material
                
                # Check if Base Color is connected to a texture
                has_base_color_texture = False
                
                # Get the Principled BSDF node
                principled_node = None
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        principled_node = node
                        break
                
                # If we found a Principled BSDF node, check its Base Color input
                if principled_node:
                    base_color_input = principled_node.inputs.get('Base Color')
                    
                    # Check if Base Color input has any links
                    if base_color_input and base_color_input.links:
                        # Get the node connected to Base Color
                        from_node = base_color_input.links[0].from_node
                        
                        # Check if it's a texture node or connected to a texture node
                        if from_node.type in ['TEX_IMAGE', 'TEX_ENVIRONMENT', 'TEX_NOISE', 'TEX_VORONOI', 'TEX_WAVE', 'TEX_MAGIC']:
                            has_base_color_texture = True
                        else:
                            # Check if this node is connected to a texture node (e.g., through a MixRGB or ColorRamp)
                            texture_found = self.check_node_for_texture_connection(from_node, material.node_tree)
                            if texture_found:
                                has_base_color_texture = True
                
                # If material has Base Color connected to a texture, add to list
                if has_base_color_texture:
                    textured_material_indices.append(i)
        
        if not textured_material_indices:
            self.report({'INFO'}, "No materials found with Base Color connected to textures")
            return {'CANCELLED'}
        
        # Need to use bmesh for face selection by material index
        bm = bmesh.from_edit_mesh(mesh)
        
        # Select faces with textured materials
        for face in bm.faces:
            if face.material_index in textured_material_indices:
                face.select = True
        
        # Update the mesh
        bmesh.update_edit_mesh(mesh)
        
        self.report({'INFO'}, f"Selected faces with Base Color connected to textures: {len(textured_material_indices)} materials")
        return {'FINISHED'}
    
    def check_node_for_texture_connection(self, node, node_tree, depth=0):
        """Recursively check if a node is connected to a texture node"""
        # Prevent infinite recursion
        if depth > 5:
            return False
            
        # Check all inputs of this node
        for input_socket in node.inputs:
            if input_socket.links:
                for link in input_socket.links:
                    from_node = link.from_node
                    
                    # Check if this is a texture node
                    if from_node.type in ['TEX_IMAGE', 'TEX_ENVIRONMENT', 'TEX_NOISE', 'TEX_VORONOI', 'TEX_WAVE', 'TEX_MAGIC']:
                        return True
                    
                    # Recursively check the connected node
                    if self.check_node_for_texture_connection(from_node, node_tree, depth + 1):
                        return True
        
        return False


class MATERIAL_OT_AddPrefixToSelected(bpy.types.Operator):
    """Add prefix to names of materials used by selected faces"""
    bl_idname = "material.add_prefix_to_selected"
    bl_label = "Add Prefix to Selected Materials"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        prefix = context.scene.material_name_prefix
        
        if not prefix:
            self.report({'ERROR'}, "Please enter a prefix")
            return {'CANCELLED'}
        
        # Ensure we're in edit mode
        if context.object.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        obj = context.active_object
        mesh = obj.data
        
        # Use bmesh to get selected faces
        bm = bmesh.from_edit_mesh(mesh)
        
        # Get material indices from selected faces
        selected_material_indices = set()
        for face in bm.faces:
            if face.select:
                selected_material_indices.add(face.material_index)
        
        if not selected_material_indices:
            self.report({'INFO'}, "No faces selected")
            return {'CANCELLED'}
        
        # Get materials from selected indices
        material_slots = obj.material_slots
        renamed_materials = 0
        
        for i in selected_material_indices:
            if i < len(material_slots) and material_slots[i].material:
                material = material_slots[i].material
                
                # Skip if material already has the prefix
                if not material.name.startswith(prefix):
                    material.name = prefix + material.name
                    renamed_materials += 1
        
        self.report({'INFO'}, f"Added prefix to {renamed_materials} materials")
        return {'FINISHED'}


class MATERIAL_OT_AddPrefixToAll(bpy.types.Operator):
    """Add prefix to names of all materials in the object"""
    bl_idname = "material.add_prefix_to_all"
    bl_label = "Add Prefix to All Materials"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        prefix = context.scene.material_name_prefix
        
        if not prefix:
            self.report({'ERROR'}, "Please enter a prefix")
            return {'CANCELLED'}
        
        obj = context.active_object
        
        # Get all materials in the object
        material_slots = obj.material_slots
        renamed_materials = 0
        
        for slot in material_slots:
            if slot.material:
                material = slot.material
                
                # Skip if material already has the prefix
                if not material.name.startswith(prefix):
                    material.name = prefix + material.name
                    renamed_materials += 1
        
        self.report({'INFO'}, f"Added prefix to {renamed_materials} materials")
        return {'FINISHED'}


# Registration
classes = (
    MATERIAL_PT_CheckBaseColorTexture,
    MATERIAL_OT_CheckBaseColorTexture,
    MATERIAL_OT_AddPrefixToSelected,
    MATERIAL_OT_AddPrefixToAll,
)

def register():
    # Register properties
    bpy.types.Scene.material_name_prefix = StringProperty(
        name="Material Name Prefix",
        description="Prefix to add to material names",
        default=""
    )
    
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Remove properties
    del bpy.types.Scene.material_name_prefix

if __name__ == "__main__":
    register()