
                                      ---- Auto Pivot v1.2 ----



 -- INSTALLATION
 
 1. Launch 3dsMax using right click -> Run as administrator
 
 2. Execute the AutoPivot_Bottom.mzp file using "Scripting -> Run Script"
    Execute the AutoPivot_Center.mzp file using "Scripting -> Run Script"
  
 3. Click on "Customize -> Customize User Interface" and Click on "Toolbars" tab
 
 4. In "Category", select "Visuali Studio" and drag&drop "AutoPivot_Bottom" and "AutoPivot_Center" in 3dsMax UI to add it as a button
 
 
 -- HOW TO USE IT
 
 Simply select the object(s) you want and press the "AutoPivot_Bottom" or "AutoPivot_Center" icon
 
 
 -- NOTE
 
 The script uses vertex computation to find the center of mass so the speed of execution depends on the complexity of the object.
 Be aware that you may experience slowness with high polygon objects.
 
 Remember that the Group object itself has no mass so its center will always coincide with the center of the Selection brackets.