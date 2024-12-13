
   global vv=[0,0,0], wt=0
   global GW_displayObjectNames
   fn GW_displayObjectNames=
   (
                                    completeredraw()
                                    gw.settransform(viewport.gettm())
                                    gw.wtext vv (wt as string)  color:(color 255 255 255)
                                    gw.enlargeUpdateRect #whole
                                    gw.updatescreen()
   )
                tool AssignSkinVertexWeightTool
                (
                                local original,viewpoint_x;
                  
                                fn setweight mode= (
                              if mode==true then (
                              if wt<=0 then wt=0 
                              else if wt<=0.1 then wt=0.1 
                              else if wt<=0.2 then wt=0.2
                              else if wt<=0.3 then wt=0.3 
                              else if wt<=0.4 then wt=0.4
                              else if wt<=0.5 then wt=0.5
                              else if wt<=0.6 then wt=0.6
                              else if wt<=0.7 then wt=0.7 
                              else if wt<=0.8 then wt=0.8
                              else if wt<=0.9 then wt=0.9
                              else wt=1 
                                 
                              skinOps.SetWeight $.modifiers[#Skin] wt)
                           else (
                              if wt<=0 then wt=0 else if wt>=1 do wt=1
                           skinOps.SetWeight $.modifiers[#Skin] wt)
                           vv=[viewPoint.x+20,viewPoint.y+20,0]
                           
                                )                                   
                                on mousePoint clickno do (                 
                                                            
                                                if clickno > 1 then (
                                       unregisterRedrawViewsCallback GW_displayObjectNames;  
                                       return  #stop       )           
                                                original = 0
                                    viewpoint_x=viewPoint.x
                                )
                                on mouseAbort clickno do (
                                                setweight false
                                    
                                    
                                )
                                on mouseMove clickno do (
                                                wt = (viewpoint_x- (viewPoint.x ))*-0.005
                                    if shiftKey==true then setweight true else setweight false
                                                               
                                )
                )
            registerRedrawViewsCallback GW_displayObjectNames   
                startTool AssignSkinVertexWeightTool prompt:"Set Vertex Weight"
