macroScript P_Scripts category:"P_Scripts" tooltip:"P_Scripts"
(

fn getWindowClass =
(
   local source  = "using System;"
   source += "using System.Runtime.InteropServices;"
   source += "public class Window"
   source += "{"
   source += "   [DllImport(\"user32.dll\")]"
   source += "   public static extern IntPtr GetForegroundWindow();"
   source += "}"

   local csharpProvider = dotNetObject "Microsoft.CSharp.CSharpCodeProvider"
   local compilerParams = dotNetObject "System.CodeDom.Compiler.CompilerParameters"
   compilerParams.GenerateInMemory = true
   compilerParams.ReferencedAssemblies.Add "System.dll"
   local compilerResults = csharpProvider.CompileAssemblyFromSource compilerParams #(source)
   compilerResults.CompiledAssembly.CreateInstance "Window"
)
if NOT isKindOf ::window dotNetObject do window = getWindowClass()
try destroyDialog ::focusTest catch()
----- check_Focus_HWND



(   
   global P_dialog, _cate , _btnname,  now_P
   local Start_Script , Help_Btn , util_Btn , Fix_Btn , Modifiers_Btn, Create_P_Dialog, get_Btn_List
   local  InputBox, hForm ,pre_fix_info
   Button_Count=0
   NBL=#()
   folder=""      --
   Button_List=#()  --Button's_List
   
   
   setting_info=(fileIn ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Setting_Info.ms"))
   TheBGColor=setting_info[1]
   TheBGColor2=setting_info[2]
   TheBGColor3=setting_info[3]
   TheBorderColor=setting_info[4]
   TheFontColor=setting_info[5]
   TheDisfocusFontColor=setting_info[6]
   TheFont = setting_info[7]
   TheFont_1 = setting_info[8]
   Original_Button_Width=setting_info[9]
   Original_Button_Height=setting_info[10]
)
----- Variable



(
   function ClickEvent arg ee=
   (
      d=dotNetClass "Control"
      if ee.button==d.MouseButtons.Left do (Start_Script (arg.text); return true)
      if ee.button==d.MouseButtons.right do 
      (
         fileIn ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\Mini_Button_Setting.ms")
         _cate folder
         _btnname arg.text
         return false
      )
   )
   
   function keyevent ee=
   (
      key=ee.KeyCode
      case key of 
      (
         (ee.KeyCode.F1):
         (
            Start_Script #F1
         )
         (ee.KeyCode.F2):
         (
            Start_Script #F2
         )
         (ee.KeyCode.F3):
         (
            Start_Script #F3
         )
         (ee.KeyCode.F4):
         (
            Start_Script #F4
         )
         default:
         (
            input_value=InputBox.text
            InputBox.text=""
            Start_Script input_value[1]
         )
      )
   )
   
   function keyDownevent ee=
   (
      key=ee.KeyCode
      
      if (ee.Modifiers == key.Control) then
      (
         if key == key.Z then (max undo)
         else if key == key.Y then (actionMan.executeAction 0 "40016")
      )
      
      if key == ee.KeyCode.Enter or key == ee.KeyCode.Space or key == ee.KeyCode.Escape then 
      (
         
      )
   )
)
----- Mouse and Keyboard Event


fn close_P_Dialog=
(   
   Button_Count=0
   InputBox=undefined
   hForm=undefined
   Button_List=#()
   P_dialog.close()
   P_dialog=undefined
   
   --Addbutton=undefined
   --test_Condition=undefined
   --Gc ()
)
----- Close_Dialog Fn




fn Start_Script Input_Text non_close:false=
(
   local scriptname
   
   
   case Input_Text of
   (
      undefined : 
      (
         return false
      )
      #F1 : 
      (
         pre_fix_info=P_dialog.location
         close_P_Dialog(); 
         
         Button_List=#()
         P_dialog=Create_P_Dialog "Default"
         hForm.FormBorderStyle = (dotnetclass "System.Windows.Forms.FormBorderStyle").none
         return false
      )
	  
      #TAB : 
      (
		Fav_num="1)Favorite"
		 case folder of
		 (
			 "1)Favorite" : (Fav_num="2)Favorite")
			 "2)Favorite" : (Fav_num="3)Favorite")
			 default :()
		 )
         pre_fix_info=P_dialog.location
         close_P_Dialog(); 
         
         Button_List=#()
         P_dialog=Create_P_Dialog Fav_num
         hForm.FormBorderStyle = (dotnetclass "System.Windows.Forms.FormBorderStyle").none
         return false
      )
      
      #F2: 
      (
         fileIn ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Utility.ms")
         return false
      )
      
      #F3 :
      (      
         pre_fix_info=P_dialog.location
         close_P_Dialog()
         fileIn ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Help.ms")
         return false
      )
      
      #F4 :
      (
         close_P_Dialog()
		  fileIn ((getdir #UserScripts)+"\\P_Scripts\\P_Scripts(FIX).ms")
         --close_P_Dialog()
         return false
      )
      " " :
      (
         (
            InputBox.Focus()
         )
         fileIn ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Modifiers.ms")
      )
      "`" :
      (
		Fav_num="1)Favorite"
		 case folder of
		 (
			 "1)Favorite" : (Fav_num="2)Favorite")
			 "2)Favorite" : (Fav_num="3)Favorite")
			 default :()
		 )
         pre_fix_info=P_dialog.location
         close_P_Dialog(); 
         
         Button_List=#()
         P_dialog=Create_P_Dialog Fav_num
		 now_P=Fav_num
         hForm.FormBorderStyle = (dotnetclass "System.Windows.Forms.FormBorderStyle").none
         return false
      )
      default:()
      
   )
   if Input_Text.count==1 then
   (
      Input_Text=toUpper Input_Text
      for i in Button_List do
      (
         if i[1]==Input_Text do 
            (
            scriptname= (i[2].text)
            exit;
         )
      )
      if scriptname == undefined do 
      (
         return false
      )
   )
   ----- Case of HotKey // Find ScriptName
      
   else
   (
      scriptname=Input_Text
   )
   ----- Case of Title // Scriptname=Title

   
   (
      if scriptname[scriptname.count]==")" do
      (
         scriptname=substring scriptname 1 (scriptname.count-4)
      )  -----if ScriptTitle has Shortcut, Do substring
         close_P_Dialog()
   )
   
   ----- Ready For Start Script
   case folder of
   ( 
      "None":
      (
         if (doesFileExist (((getdir #UserScripts)+"\\P_Scripts\\None\\"+scriptname+".ms")))
         then (undo on (fileIn ((getdir #UserScripts)+"\\P_Scripts\\None\\"+scriptname+".ms")))
         else if (doesFileExist (((getdir #UserScripts)+"\\P_Scripts\\None\\"+scriptname+".mse")))
         then (undo on(fileIn ((getdir #UserScripts)+"\\P_Scripts\\None\\"+scriptname+".mse")))
      )
      "Default":
      (
         if $selection.count>0 then
         (
            if (doesFileExist (((getdir #UserScripts)+"\\P_Scripts\\Default\\"+scriptname+".ms")))
            then (undo on(fileIn ((getdir #UserScripts)+"\\P_Scripts\\Default\\"+scriptname+".ms")))
            else if (doesFileExist (((getdir #UserScripts)+"\\P_Scripts\\Default\\"+scriptname+".mse")))
            then (undo on(fileIn ((getdir #UserScripts)+"\\P_Scripts\\Default\\"+scriptname+".mse")))
         )
         else
            (messagebox "It doesn't comply with the condition ")
      )
      "Bone":
      (
         if (classof $selection[1])==BoneGeometry then
         (
            if (doesFileExist (((getdir #UserScripts)+"\\P_Scripts\\BoneGeometry\\"+scriptname+".ms")))
            then (undo on(fileIn ((getdir #UserScripts)+"\\P_Scripts\\BoneGeometry\\"+scriptname+".ms")))
            else if (doesFileExist (((getdir #UserScripts)+"\\P_Scripts\\BoneGeometry\\"+scriptname+".mse")))
            then (undo on(fileIn ((getdir #UserScripts)+"\\P_Scripts\\BoneGeometry\\"+scriptname+".mse")))
         )
         else
            (messagebox "It doesn't comply with the condition ")
      )
      "Biped_Object":
      (
         if (classof $selection[1])==Biped_Object then
         (
            if (doesFileExist (((getdir #UserScripts)+"\\P_Scripts\\Biped_Object\\"+scriptname+".ms")))
            then (undo on(fileIn ((getdir #UserScripts)+"\\P_Scripts\\Biped_Object\\"+scriptname+".ms")))
            else if (doesFileExist (((getdir #UserScripts)+"\\P_Scripts\\Biped_Object\\"+scriptname+".mse")))
            then (undo on(fileIn ((getdir #UserScripts)+"\\P_Scripts\\Biped_Object\\"+scriptname+".mse")))
         )
         else
            (messagebox "It doesn't comply with the condition ")
      )
      "Shape":
      (
         if (superclassof $selection[1])==Shape then
         (
            if (doesFileExist (((getdir #UserScripts)+"\\P_Scripts\\Shape\\"+scriptname+".ms")))
            then (undo on(fileIn ((getdir #UserScripts)+"\\P_Scripts\\Shape\\"+scriptname+".ms")))
            else if (doesFileExist (((getdir #UserScripts)+"\\P_Scripts\\Shape\\"+scriptname+".mse")))
            then (undo on(fileIn ((getdir #UserScripts)+"\\P_Scripts\\Shape\\"+scriptname+".mse")))
         )
         else
            (messagebox "It doesn't comply with the condition ")
      )
      "Camera":
      (
         if (superclassof $selection[1])==Camera then
         (
            if (doesFileExist (((getdir #UserScripts)+"\\P_Scripts\\Camera\\"+scriptname+".ms")))
            then (undo on(fileIn ((getdir #UserScripts)+"\\P_Scripts\\Camera\\"+scriptname+".ms")))
            else if (doesFileExist (((getdir #UserScripts)+"\\P_Scripts\\Camera\\"+scriptname+".mse")))
            then (undo on(fileIn ((getdir #UserScripts)+"\\P_Scripts\\Camera\\"+scriptname+".mse"))
         ))
         else
            (messagebox "It doesn't comply with the condition ")
      )
      "Light":
      (
         if (superclassof $selection[1])==Light then
         (
            if (doesFileExist (((getdir #UserScripts)+"\\P_Scripts\\Light\\"+scriptname+".ms")))
            then (undo on(fileIn ((getdir #UserScripts)+"\\P_Scripts\\Light\\"+scriptname+".ms")))
            else if (doesFileExist (((getdir #UserScripts)+"\\P_Scripts\\Light\\"+scriptname+".mse")))
            then (undo on(fileIn ((getdir #UserScripts)+"\\P_Scripts\\Light\\"+scriptname+".mse")))
         )
         else
            (messagebox "It doesn't comply with the condition ")
      )
      default:
      (
            if (doesFileExist ( ((getdir #UserScripts)+"\\P_Scripts\\"+folder+"\\"+scriptname+".ms")))
            then (undo on(fileIn ((getdir #UserScripts)+"\\P_Scripts\\"+folder+"\\"+scriptname+".ms")))
            else if (doesFileExist (((getdir #UserScripts)+"\\P_Scripts\\"+folder+"\\"+scriptname+".mse")))
            then (undo on(fileIn ((getdir #UserScripts)+"\\P_Scripts\\"+folder+"\\"+scriptname+".mse")))
      )
      
      
      
   )
   /*
   undo on 
   (
      if (test_Condition()) then
      (
         fileIn ((getdir #UserScripts)+"\\P_Scripts\\"+folder+"\\"+scriptname+".ms")   
      )
      else 
      (
         messagebox "It doesn't comply with the condition "
      )
   )*/
   ----- Start Script
)
----- Start Script Fn



function addbutton Title Shortcut _Across:0=
(
   Button_W=Original_Button_Width
   Button_X_Position=0
   if _Across == 1 then 
   (
      Button_W=(Original_Button_Width/2)
   )
   else if _Across == 2 then 
   (
      Button_W=(Original_Button_Width/2); Button_X_Position=(Original_Button_Width/2)
   )
   else if _Across == 3 then 
   (
      Button_Count+=1
   )
   ----- Setup of Button's Position and Width
   
   Title__=Title
   if Shortcut!="" do (Title__=Title+" ("+Shortcut+")")
   
   BTN = dotNetObject "System.windows.forms.button"
   BTN.text = Title__
   BTN.flatStyle=BTN.flatStyle.flat
   BTN.BackColor = TheBGColor
   BTN.flatappearance.bordercolor = TheBorderColor
   BTN.size = dotNetObject "System.Drawing.Size" (Button_W) (Original_Button_Height)
   BTN.location = dotNetObject "System.Drawing.Point" (Button_X_Position) (Original_Button_Height*(Button_Count+1))
   BTN.font=TheFont
      
   append Button_List #(Shortcut,BTN)
   hForm.controls.add BTN
   dotnet.addEventHandler BTN "MouseDown" ClickEvent
   
   if _Across !=1 do (Button_Count+=1)
)
------ AddButton Fn



fn Create_P_Dialog Type=
(   
   local new_Btn_List
   new_Btn_List=#()
   hForm = dotNetObject "MaxCustomControls.MaxForm" pos:[0,0]   
   folder=Type
   if (doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\"+Type)) do
   (
      
      function get_Btn_List= (fileIn ((getdir #UserScripts)+"\\P_Scripts\\"+folder+"\\Info\\Add_Button.ms"))
      new_Btn_List=get_Btn_List()
      for i in new_Btn_List do
      (
         addbutton i[1] i[2] _Across:i[3]
      )
   )
   
   
   /*
   if (doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\"+Type)) do
   (fileIn ((getdir #UserScripts)+"\\P_Scripts\\"+Type+"\\_"+Type+"_List.ms"))
   */
   
   ----- Add Button

   (   
         
         
      Modifiers_Btn = dotNetObject "System.windows.forms.button"
      Modifiers_Btn.text = "M"
      Modifiers_Btn.flatStyle=Modifiers_Btn.flatStyle.flat
      Modifiers_Btn.BackColor = TheBGColor
      Modifiers_Btn.flatappearance.bordercolor = TheBorderColor
      Modifiers_Btn.size = dotNetObject "System.Drawing.Size" (Original_Button_Width/4) Original_Button_Height
      Modifiers_Btn.location = dotNetObject "System.Drawing.Point" 0 0
      Modifiers_Btn.font=TheFont
      hForm.controls.add Modifiers_Btn
      fn Modifiers_Btn_event=
      (   
            close_P_Dialog()
         fileIn ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Modifiers.ms")
      )
         
      util_Btn = dotNetObject "System.windows.forms.button"
      util_Btn.text = "U"
      util_Btn.flatStyle=util_Btn.flatStyle.flat
      util_Btn.BackColor = TheBGColor
      util_Btn.flatappearance.bordercolor = TheBorderColor
      util_Btn.size = dotNetObject "System.Drawing.Size" (Original_Button_Width/4) Original_Button_Height 
      util_Btn.location = dotNetObject "System.Drawing.Point" (Original_Button_Width/4) 0
      util_Btn.font=TheFont
      hForm.controls.add util_Btn
      fn util_btn_event=
      (
         fileIn ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Utility.ms")
         
         --for i=1 to (Utility_rollout.ddl1.items.count) do
            close_P_Dialog()
      )

      Help_Btn = dotNetObject "System.windows.forms.button"
      Help_Btn.text = "H"
      Help_Btn.flatStyle=Help_Btn.flatStyle.flat
      Help_Btn.BackColor = TheBGColor2
      Help_Btn.flatappearance.bordercolor = TheBorderColor
      Help_Btn.size = dotNetObject "System.Drawing.Size" (Original_Button_Width/4) Original_Button_Height 
      Help_Btn.location = dotNetObject "System.Drawing.Point" ((Original_Button_Width/4)*2) 0
      Help_Btn.font=TheFont
      hForm.controls.add Help_Btn
      fn Help_Btn_event=
      (
            pre_fix_info=P_dialog.location
            close_P_Dialog()
         fileIn ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Help.ms")
      )
         
         
      Fix_Btn = dotNetObject "System.windows.forms.button"
      Fix_Btn.text = "F"
      Fix_Btn.flatStyle=Fix_Btn.flatStyle.flat
      Fix_Btn.BackColor = TheBGColor3
      Fix_Btn.flatappearance.bordercolor = TheBorderColor
      Fix_Btn.size = dotNetObject "System.Drawing.Size" (Original_Button_Width/4) Original_Button_Height
      Fix_Btn.location = dotNetObject "System.Drawing.Point" ((Original_Button_Width/4)*3) 0
      Fix_Btn.font=TheFont
      hForm.controls.add Fix_Btn
      fn Fix_btn_event=
         (
         close_P_Dialog()
		  fileIn ((getdir #UserScripts)+"\\P_Scripts\\P_Scripts(FIX).ms")
         )
   )
   ----- Add 4 Utility Button
   
   (
      InputBox=dotNetObject "System.windows.forms.TextBox"
      InputBox.location = dotNetObject "System.Drawing.Point" -20 -20
      hForm.controls.add InputBox

      cursor = dotnetclass "System.Windows.Forms.Cursor"
      p = cursor.Position
      hform.StartPosition = hform.StartPosition.Manual
      hForm.Location=dotnetobject "System.Drawing.Point" (p.x-(Original_Button_Width/2)) (p.y+0-(Original_Button_Height*(Button_Count+1)+10)/2)
      if Button_Count==0 do Button_Count=1
      hForm.size=dotNetObject "System.Drawing.Size" (Original_Button_Width+16) ((Original_Button_Height+(39/Button_Count))*(Button_Count+1))
      hForm.FormBorderStyle = (dotnetclass "System.Windows.Forms.FormBorderStyle").none
      hForm.text=folder
      hForm.MaximizeBox = false;
      hForm.MinimizeBox = false;
   )
   ----- Inputbox And Dialog Setting

   (
   function LostfocusEvent =
   (
      if hForm==undefined do 
      (
         return 0
      )
      if (hForm.handle!= (window.getForegroundWindow())) then
         (
            close_P_Dialog()
         )
      for i in Button_List do
      (
         i[2].ForeColor=TheDisFocusFontColor
         Help_Btn.ForeColor=TheDisFocusFontColor
         Fix_Btn.ForeColor=TheDisFocusFontColor
         Modifiers_Btn.ForeColor=TheDisFocusFontColor
         util_Btn.ForeColor=TheDisFocusFontColor
      )
   )


   function GotfocusEvent=
   (
      InputBox.Focus()
   )
      

   function GotfocusEvent2=
   (
      for i in Button_List do
      (
         i[2].ForeColor=TheFontColor
         Help_Btn.ForeColor=TheFontColor
         Fix_Btn.ForeColor=TheFontColor
         Modifiers_Btn.ForeColor=TheFontColor
         util_Btn.ForeColor=TheFontColor
      )
   )
      
   --hForm.AllowTransparency=true
      
   dotnet.addEventHandler InputBox "KeyDown" keyDownevent
   dotnet.addEventHandler InputBox "KeyUp" keyevent
   dotnet.addEventHandler InputBox "LostFocus" LostfocusEvent
   dotnet.addEventHandler InputBox "GotFocus" GotfocusEvent2
   dotnet.addEventHandler Fix_Btn "Click" Fix_btn_event
   dotnet.addEventHandler Modifiers_Btn "Click" Modifiers_Btn_event
   dotnet.addEventHandler util_Btn "Click" util_Btn_event
   dotnet.addEventHandler Help_Btn "Click" Help_Btn_event
   dotnet.addEventHandler hForm "GotFocus" GotfocusEvent
   )
   ----- Event Setting
      
   hForm.showmodeless()
   InputBox.Focus()

   return hForm
)
------ Create Dialog Fn






(
   
   if M_dialog!=undefiend do
   (
      M_dialog.close()
   )
   
   if P_dialog!=undefined do 
   (
      pre_fix_info=P_dialog.location
      close_P_Dialog(); 
   )
   (
      function Check_Current_Selected_Type=
         (
            function get_Modify_List=
            (
               a=filein ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_List.ms")
               return a
            )

            Modify_List=get_Modify_List()

            fn Check_Folder_Exist dir=( return doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\"+dir+"\\Info"))
            
            Select_List=selection as array
               
            if Select_List.count==0 then 
            (
               return "None"
            )
            
            current_modify=(modpanel.getCurrentObject()) as string
            namefilter=findstring current_modify ":"
            if namefilter!=undefined do (current_modify=substring current_modify 1 (namefilter-1))

            if current_modify!="undefined" then
            (
               if (Check_Folder_Exist (current_modify)) and (finditem Modify_List (current_modify))!=0 do
               (
                        return current_modify as string
               )
               case current_modify of 
               (
                  "Edit_Poly" :
                  (
                     return "Editable Poly"
                  )
                  "Line" :
                  (
                     return "Editable Spline"
                  )
                  "Edit_Spline" :
                  (
                     return "Editable Spline"
                  )
                  /*default : 
                  (
                     return "Default"
                  )*/
               )
            )
            --else
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
      now_P=Check_Current_Selected_Type()
      P_dialog=Create_P_Dialog (now_P)
	
      
   )
   
   if (pre_fix_info!=undefined) and (P_dialog!=undefined) do 
   (
      P_dialog.location= pre_fix_info
      hForm.FormBorderStyle = (dotnetclass "System.Windows.Forms.FormBorderStyle").FixedToolWindow
   )
   ----- Position Override
)



)