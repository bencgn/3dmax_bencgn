
(

rollout SnapVerts "SnapVerts v2.0" width:202 height:72 (
	pickButton pickTarget "Pick target (snap to)" pos:[8,8] width:140 height:32 tooltip:"Pick target. After clicking 'SNAP' selected vertices will snap to vertices of target"
	button btnSnap "SNAP" pos:[154,8] width:40 height:32 tooltip:"Snap selected vertices to vertices of target"
	spinner spinDistance "Max distance: " pos:[6,46] width:182 range:[0,9999999999,100] type:#Float tooltip:"SNAP won't work for vertices with distance above this number"
	
	on pickTarget picked obj do (
		pickTarget.caption = obj.name
	)
	
	on btnSnap pressed do (
		if pickTarget.object != undefined then (
			obj = pickTarget.object
			mDist = spinDistance.value
			for v in $.selectedVerts do (
				md = mDist
				d = md
				mv = [0,0,0]
				for v2 in obj.verts do (
					d = distance v.pos v2.pos
					if d < md then (
						md = d
						mv = v2.pos
					)
				)
				if md < mDist do (
					v.pos = mv
				)
			)
		)else (
			messagebox "Pick target before you use SNAP"
		)
	)
)
createDialog SnapVerts style:#(#style_titlebar, #style_border, #style_sysmenu, #style_minimizebox, #style_maximizebox)

)