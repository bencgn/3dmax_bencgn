(
	function get_Modify_List=
	(
		a=filein ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_List.ms")
		return a
	)

	Modify_List=get_Modify_List()

	fn Check_Folder_Exist dir=( return doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\"+dir+"\\Info"))
	
	Select_List=selection as array
	current_modify=classof (modpanel.getCurrentObject())
	if Select_List.count==0 then 
	(
		return "None"
	)

	else if current_modify!=UndefinedClass then
	(
		if (Check_Folder_Exist (current_modify as string)) and (finditem Modify_List (current_modify as string))!=0 do
		(
			return current_modify as string
		)
			return "Default"
	)
	else
	(
		if Select_List.count > 1 do
		(
			for i=2 to Select_List.count do
			(
				if (Superclassof Select_List[i]) != (Superclassof Select_List[i-1]) do
				(
					return "Default"
				)
			)
		)
		
		case (Superclassof Select_List[1]) of
		(
		GeometryClass:
			(
				if Select_List.count > 1 do
				(
					for i=2 to Select_List.count do
					(
						if (classof Select_List[i]) != (classof Select_List[i-1]) do
						(
							return "Default"
						)
					)
				)
				case (classof (Select_List[1])) of 
				(
				Biped_Object:
					(
						if (Check_Folder_Exist "Biped_Object") and ((finditem Modify_List "Biped_Object")!=0) do (return "Biped_Object")
						return "Default"		
					)
				BoneGeometry:
					(
						if (Check_Folder_Exist "BoneGeometry") and ((finditem Modify_List "BoneGeometry")!=0) do (return "BoneGeometry")
						return "Default"
					)
				Default:
					(
						return "Default"
					)
				)
			)
		Shape:
			(
				if (Check_Folder_Exist "Shape") and ((finditem Modify_List "Shape")!=0) do (return "Shape")
				return "Default"
			)
		Helper:
			(
				if (Check_Folder_Exist "Helper") and ((finditem Modify_List "Helper")!=0) do (return "Helper")
				return "Default"
			)
		Camera:
			(
				if (Check_Folder_Exist "Camera") and ((finditem Modify_List "Camera")!=0) do (return "Camera")
				return "Default"
			)
		Light:
			(
				if ((Check_Folder_Exist "Light")==true) and ((finditem Modify_List "Light")!=0) do (return "Light")
				return "Default"
			)
		)
	)
)
