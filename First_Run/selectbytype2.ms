try(destroyDialog SelectByType)catch()

rollout SelectByType "Select By Type"
(
	--UI CONTROL DEFINITIONS
		label lab1 "Goes for all objects in scene"
		button selectGeometry "Select Geometry" width:140
		button selectShapes "Select Shapes" width:140
		button selectEditPoly "Select Editable Polys" width:140		
		button selectEditMesh "Select Editable Meshes" width:140
		button selectCameras "Select Cameras" width:140
		button selectLights "Select Lights" width:140
		button selectHelpers "Select Helpers" width:140
		button selectSpaceWarps "Select Space Warps" width:140
		button selectRiggedSystems "Select Rigged Systems" width:140


	--CONTROL EVENT HANDLERS
	--Geometry
	on selectGeometry pressed do
		(
			select (for o in geometry collect o)
		)
		
	--Shapes
	on selectShapes pressed do
		(
			select (for s in shapes collect s)
		)
		
	--Editable Polys
	on selectEditPoly pressed do   
		(
			select (for o in geometry where classOf o == editable_poly collect o)
		)
		
	--Editable Meshes
	on selectEditMesh pressed do   
		(
			select (for o in geometry where classOf o == editable_mesh collect o)
		)
		
	--Cameras
	on selectCameras pressed do
		(
			select (for c in cameras collect c)
		)
		
	--Lights
	on selectLights pressed do
		(
			select (for l in lights collect l)
		)
		
	--Helpers
	on selectHelpers pressed do
		(
			select (for h in helpers where h.category == #standard collect h)
		)
		
	--Space Warps
	on selectSpaceWarps pressed do
		(
			select (for s in spacewarps collect s)
		)
		
	--Rigged Systems
	on selectRiggedSystems pressed do
        (
			select (for b in objects where classOf b == boneGeometry or classOf b == Biped_Object collect b)
        )

)
createDialog SelectByType width:180