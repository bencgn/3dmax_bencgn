"""
3ds Max Script: Extrude Vertices to Spline
This script extrudes selected vertices in +Z direction and converts the edges to a spline.
"""

from pymxs import runtime as rt

def extrude_vertices_to_spline(extrude_distance=100.0):
    """Main function to extrude vertices and convert to spline"""
    try:
        # Get the selected object
        if rt.selection.count == 0:
            rt.messageBox("No object selected!", title="Error")
            return
            
        obj = rt.selection[0]
        
        # Check if object is an Editable Poly
        if not rt.classOf(obj) == rt.Editable_Poly:
            # Try to convert to Editable Poly
            rt.convertTo(obj, rt.Editable_Poly)
        
        # Get selected vertices at sub-object level
        vert_selection = rt.polyOp.getVertSelection(obj)
        
        if vert_selection.isEmpty:
            rt.messageBox("No vertices selected!\n\nPlease select vertices in vertex sub-object mode.", title="Error")
            return
        
        # Convert BitArray to list - iterate through all vertices and check if selected
        selected_verts = []
        num_verts = rt.polyOp.getNumVerts(obj)
        for i in range(1, num_verts + 1):
            if vert_selection[i]:
                selected_verts.append(i)
        
        if len(selected_verts) == 0:
            rt.messageBox("No vertices selected!", title="Error")
            return
        
        # Store original vertex positions and create new vertices
        new_verts = []
        edge_pairs = []
        
        rt.polyOp.setVertSelection(obj, vert_selection)
        
        # For each selected vertex, create a new vertex above it
        for vert_idx in selected_verts:
            # Get vertex position in local space
            vert_pos = rt.polyOp.getVert(obj, vert_idx)
            
            # Create new vertex position (offset in +Z)
            new_pos = rt.Point3(vert_pos.x, vert_pos.y, vert_pos.z + extrude_distance)
            
            # Create new vertex
            new_vert_idx = rt.polyOp.createVert(obj, new_pos)
            new_verts.append(new_vert_idx)
            
            # Store edge pair (original vertex, new vertex)
            edge_pairs.append((vert_idx, new_vert_idx))
        
        # Create edges between original and new vertices
        created_edges = []
        for old_vert, new_vert in edge_pairs:
            # Create edge
            edge_idx = rt.polyOp.createEdge(obj, old_vert, new_vert)
            if edge_idx is not None:
                created_edges.append(edge_idx)
        
        # Convert edges to spline
        if len(created_edges) > 0:
            # Create spline from selected edges
            splines = []
            for i, edge_idx in enumerate(created_edges):
                # Get edge vertices
                edge_verts = rt.polyOp.getEdgeVerts(obj, edge_idx)
                
                # Get vertex positions (MAXScript uses 1-based indexing!)
                v1_pos = rt.polyOp.getVert(obj, edge_verts[1])
                v2_pos = rt.polyOp.getVert(obj, edge_verts[2])
                
                # Transform positions to world space
                v1_world = v1_pos * obj.transform
                v2_world = v2_pos * obj.transform
                
                # Create spline
                spline = rt.SplineShape()
                spline.name = "ExtrudedSpline_" + str(i+1)
                
                # Add knot at start position
                rt.addNewSpline(spline)
                rt.addKnot(spline, 1, rt.Name("corner"), rt.Name("line"), v1_world)
                rt.addKnot(spline, 1, rt.Name("corner"), rt.Name("line"), v2_world)
                
                # Update spline
                rt.updateShape(spline)
                
                splines.append(spline)
            
            # Clear edge selection and exit sub-object mode
            rt.polyOp.setEdgeSelection(obj, rt.BitArray())
            rt.subobjectLevel = 0
            
            # Success message
            rt.messageBox("Successfully created " + str(len(created_edges)) + " spline(s) from " + str(len(selected_verts)) + " vertex/vertices!", title="Success")
            
        else:
            rt.messageBox("No edges were created!", title="Error")
            
    except Exception as e:
        rt.messageBox("Error: " + str(e), title="Error")
        print("Error details: " + str(e))


# Create the UI using MAXScript
def create_ui():
    """Create the UI using MAXScript rollout"""
    rollout_code = """
    rollout VertexToSplineRollout "Vertex to Spline Extruder" width:300 height:180
    (
        spinner extrudeDistSpinner "Extrude Distance (Z):" range:[0.1, 10000, 100] type:#float fieldwidth:60 align:#left
        
        label infoLabel1 "Select vertices and click the button below." align:#left
        label infoLabel2 "Vertices will be extruded upward (+Z)" align:#left
        label infoLabel3 "and converted to splines." align:#left
        
        button extrudeBtn "Extrude to Spline" width:260 height:40 align:#center
        
        on extrudeBtn pressed do
        (
            local dist = extrudeDistSpinner.value
            python.execute ("import __main__; __main__.extrude_vertices_to_spline(" + dist as string + ")")
        )
    )
    
    -- Close existing dialog if open
    try(closeRolloutFloater vertexToSplineFloater) catch()
    
    -- Create and show the dialog
    global vertexToSplineFloater = newRolloutFloater "Vertex to Spline Tool" 320 220
    addRollout VertexToSplineRollout vertexToSplineFloater
    """
    
    rt.execute(rollout_code)


# Run the script
if __name__ == "__main__":
    create_ui()
