-- Title     :  Hard Edges Selection (maxscripts pack)
--
--              MAXscripts, allows quick select hard edges on the Editable Poly object or Edit Poly modifier. 
--
-- Copyright :	2024 veda3d.com, All rights reserved
-- Author    :	Royal Ghost
--
-- Version   :	1.0.0 - Initial release for 3DS MAX 2024.
--
-- Homepage  :	https://www.veda3d.com
---------------------------------------------------------------------------------------------
--             MODIFY THIS AT YOUR OWN RISK


macroScript Hard_Edges_Sel category:"Veda3d.com" tooltip:"Hard Edges Selection" buttontext:"Hard Edges Selection"
(
    obj = modPanel.getCurrentObject()
    if obj != undefined then
    (
        case (classof obj) of
        (
        Edit_Poly:obj.setoperation #SelectHardEdges 
        Editable_Poly:obj.selectHardEdges()
        )
    )
     
)
macroScript Hard_Edges_Sel_Expand category:"Veda3d.com" tooltip:"Hard Edges Selection (Expand)" buttontext:"Hard Edges Selection (Expand)"
(
    obj = modPanel.getCurrentObject()
    if obj != undefined then
    (
        case (classof obj) of
        (
        Edit_Poly:		(
						initialEdgeSelection = obj.GetSelection #edge
						obj.setoperation #SelectHardEdges
						hardSelectionEdges_arry = (obj.GetSelection #edge) as array
						obj.Select #Edge #{1..(obj.GetNumEdges())} select:false
						obj.Commit()
						res_arry =#()
						pass_arry = #()
			
							for i = 1 to hardSelectionEdges_arry.count do
							(
								if i == 1 then 
								(
								verts =#{}
								obj.getVertsUsingEdge verts initialEdgeSelection --bitarray
								connectedEdges = #{}
								obj.getEdgesUsingVert connectedEdges verts
								connectedEdges = connectedEdges as array
									
									for ed = 1 to connectedEdges.count do
									(
										if findItem hardSelectionEdges_arry connectedEdges[ed] == true then appendifUnique res_arry connectedEdges[ed]
									)
								)
								else
								(
									verts =#{}
									obj.getVertsUsingEdge verts (res_arry as BitArray)

									connectedEdges = #{}
									obj.getEdgesUsingVert connectedEdges verts
									connectedEdges = (connectedEdges - (pass_arry as BitArray)) as Array

									connectedEdges = connectedEdges as array
									res_arry = res_arry as array
									
									for ed = 1 to connectedEdges.count do
									(
										if findItem hardSelectionEdges_arry connectedEdges[ed] == true then appendifUnique res_arry connectedEdges[ed]
									)					
									pass_arry = join pass_arry connectedEdges
								)
								
							)
							res_arry = res_arry as BitArray
							obj.select #Edge res_arry
							obj.Commit() 
						)
        Editable_Poly:	(
						initialEdgeSelection = polyop.getEdgeSelection obj as array
						obj.selectHardEdges()
						hardSelectionEdges_arry = polyop.getEdgeSelection obj as array

			
						res_arry =#()
						pass_arry = #()
							for i = 1 to hardSelectionEdges_arry.count do
							(
								if i == 1 then 
								(
								connectedEdges = polyop.getEdgesUsingVert obj (polyop.getVertsUsingEdge obj initialEdgeSelection) as array
									
									for ed = 1 to connectedEdges.count do
									(
										if findItem hardSelectionEdges_arry connectedEdges[ed] == true then appendifUnique res_arry connectedEdges[ed]
									)
								)
								else
								(
									connectedEdges = polyop.getEdgesUsingVert obj (polyop.getVertsUsingEdge obj res_arry) as array
									connectedEdges = ((connectedEdges as bitarray)-(pass_arry as bitarray)) as array
									
									for ed = 1 to connectedEdges.count do
									(
										if findItem hardSelectionEdges_arry connectedEdges[ed] == true then appendifUnique res_arry connectedEdges[ed]
									)
									pass_arry = join pass_arry connectedEdges									
								)
							)
							polyop.setEdgeSelection obj res_arry
						)
        )
    )
      
)
