import bpy
from bpy.props import StringProperty, FloatProperty

class MATERIAL_PT_CleanByPrefix(bpy.types.Panel):
    """Panel for cleaning/selecting faces by material name prefix"""
    bl_label = "Clean by Material Prefix"
    bl_idname = "MATERIAL_PT_clean_by_prefix"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Text input for prefix
        layout.prop(scene, "material_prefix", text="Prefix")
        
        # Clean button
        row = layout.row()
        row.operator("material.clean_by_prefix", text="Clean")
        
        # Separator
        layout.separator()
        
        # White material settings
        box = layout.box()
        box.label(text="White Material Settings")
        box.prop(scene, "white_threshold", text="White Threshold")
        
        # Check white material button
        row = box.row()
        row.operator("material.check_white", text="Check Material White")
        
        # Dark material settings
        box = layout.box()
        box.label(text="Dark Material Settings")
        box.prop(scene, "dark_threshold", text="Dark Threshold")
        
        # Check dark material button
        row = box.row()
        row.operator("material.check_dark", text="Check Material Dark")


class MATERIAL_OT_CleanByPrefix(bpy.types.Operator):
    """Select faces with materials matching the prefix"""
    bl_idname = "material.clean_by_prefix"
    bl_label = "Clean by Material Prefix"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        prefix = context.scene.material_prefix
        
        if not prefix:
            self.report({'ERROR'}, "Please enter a material prefix")
            return {'CANCELLED'}
        
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
        matching_slot_indices = []
        
        # Find materials with matching prefix
        for i, slot in enumerate(material_slots):
            if slot.material and slot.material.name.startswith(prefix):
                matching_slot_indices.append(i)
        
        if not matching_slot_indices:
            self.report({'INFO'}, f"No materials found with prefix: {prefix}")
            return {'CANCELLED'}
        
        # Enter edit mode and select faces with matching materials
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Need to use bmesh for face selection by material index
        import bmesh
        bm = bmesh.from_edit_mesh(mesh)
        
        # Select faces with matching material indices
        for face in bm.faces:
            if face.material_index in matching_slot_indices:
                face.select = True
        
        # Update the mesh
        bmesh.update_edit_mesh(mesh)
        
        self.report({'INFO'}, f"Selected faces with materials matching prefix: {prefix}")
        return {'FINISHED'}


class MATERIAL_OT_CheckWhite(bpy.types.Operator):
    """Select faces with white materials (no texture and white base color)"""
    bl_idname = "material.check_white"
    bl_label = "Check White Materials"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        threshold = context.scene.white_threshold
        
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
        white_material_indices = []
        
        # Find materials that are white with no texture
        for i, slot in enumerate(material_slots):
            if slot.material:
                material = slot.material
                
                # Check if material has no texture
                has_texture = False
                if material.use_nodes:
                    for node in material.node_tree.nodes:
                        if node.type in ['TEX_IMAGE', 'TEX_ENVIRONMENT', 'TEX_NOISE', 'TEX_VORONOI', 'TEX_WAVE', 'TEX_MAGIC']:
                            has_texture = True
                            break
                
                # Check if base color is white (value between threshold and 1.0)
                is_white = False
                if material.use_nodes:
                    for node in material.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            # Get base color
                            base_color = node.inputs['Base Color'].default_value
                            # Convert to HSV
                            import colorsys
                            h, s, v = colorsys.rgb_to_hsv(base_color[0], base_color[1], base_color[2])
                            # Check if value is high (white) and saturation is low
                            if v >= threshold and s < 0.1:
                                is_white = True
                                break
                elif hasattr(material, 'diffuse_color'):  # For materials not using nodes
                    base_color = material.diffuse_color
                    import colorsys
                    h, s, v = colorsys.rgb_to_hsv(base_color[0], base_color[1], base_color[2])
                    if v >= threshold and s < 0.1:
                        is_white = True
                
                # If material has no texture and is white, add to list
                if not has_texture and is_white:
                    white_material_indices.append(i)
        
        if not white_material_indices:
            self.report({'INFO'}, "No white materials found with threshold: {:.1f}".format(threshold))
            return {'CANCELLED'}
        
        # Need to use bmesh for face selection by material index
        import bmesh
        bm = bmesh.from_edit_mesh(mesh)
        
        # Select faces with white materials
        for face in bm.faces:
            if face.material_index in white_material_indices:
                face.select = True
        
        # Update the mesh
        bmesh.update_edit_mesh(mesh)
        
        self.report({'INFO'}, "Selected faces with white materials (threshold: {:.1f})".format(threshold))
        return {'FINISHED'}


class MATERIAL_OT_CheckDark(bpy.types.Operator):
    """Select faces with dark/black materials (no texture and dark base color)"""
    bl_idname = "material.check_dark"
    bl_label = "Check Dark Materials"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        threshold = context.scene.dark_threshold
        
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
        dark_material_indices = []
        
        # Find materials that are dark/black with no texture
        for i, slot in enumerate(material_slots):
            if slot.material:
                material = slot.material
                
                # Check if material has no texture
                has_texture = False
                if material.use_nodes:
                    for node in material.node_tree.nodes:
                        if node.type in ['TEX_IMAGE', 'TEX_ENVIRONMENT', 'TEX_NOISE', 'TEX_VORONOI', 'TEX_WAVE', 'TEX_MAGIC']:
                            has_texture = True
                            break
                
                # Check if base color is dark/black (value between 0.0 and threshold)
                is_dark = False
                if material.use_nodes:
                    for node in material.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            # Get base color
                            base_color = node.inputs['Base Color'].default_value
                            # Convert to HSV
                            import colorsys
                            h, s, v = colorsys.rgb_to_hsv(base_color[0], base_color[1], base_color[2])
                            # Check if value is low (dark/black)
                            if v <= threshold:
                                is_dark = True
                                break
                elif hasattr(material, 'diffuse_color'):  # For materials not using nodes
                    base_color = material.diffuse_color
                    import colorsys
                    h, s, v = colorsys.rgb_to_hsv(base_color[0], base_color[1], base_color[2])
                    if v <= threshold:
                        is_dark = True
                
                # If material has no texture and is dark, add to list
                if not has_texture and is_dark:
                    dark_material_indices.append(i)
        
        if not dark_material_indices:
            self.report({'INFO'}, "No dark materials found with threshold: {:.1f}".format(threshold))
            return {'CANCELLED'}
        
        # Need to use bmesh for face selection by material index
        import bmesh
        bm = bmesh.from_edit_mesh(mesh)
        
        # Select faces with dark materials
        for face in bm.faces:
            if face.material_index in dark_material_indices:
                face.select = True
        
        # Update the mesh
        bmesh.update_edit_mesh(mesh)
        
        self.report({'INFO'}, "Selected faces with dark materials (threshold: {:.1f})".format(threshold))
        return {'FINISHED'}


# Registration
classes = (
    MATERIAL_PT_CleanByPrefix,
    MATERIAL_OT_CleanByPrefix,
    MATERIAL_OT_CheckWhite,
    MATERIAL_OT_CheckDark,
)

def register():
    # Register the material prefix property
    bpy.types.Scene.material_prefix = StringProperty(
        name="Material Prefix",
        description="Prefix of material names to select",
        default=""
    )
    
    # Register the white threshold property
    bpy.types.Scene.white_threshold = FloatProperty(
        name="White Threshold",
        description="Threshold for detecting white materials (0.7-1.0)",
        default=0.7,
        min=0.0,
        max=1.0,
        step=0.1
    )
    
    # Register the dark threshold property
    bpy.types.Scene.dark_threshold = FloatProperty(
        name="Dark Threshold",
        description="Threshold for detecting dark materials (0.0-0.7)",
        default=0.3,
        min=0.0,
        max=1.0,
        step=0.1
    )
    
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Remove properties
    del bpy.types.Scene.material_prefix
    del bpy.types.Scene.white_threshold
    del bpy.types.Scene.dark_threshold

if __name__ == "__main__":
    register()