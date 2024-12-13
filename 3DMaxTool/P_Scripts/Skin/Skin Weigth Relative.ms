
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
                  
								fn setweight= (
								if wt<=-1 then wt=-1 else if wt>=1 do wt=1
								skinOps.AddWeight $.modifiers[#Skin] wt
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
                                                setweight()
                                    
                                    
                                )
                                on mouseMove clickno do (
                                                wt = (viewpoint_x- (viewPoint.x ))*-0.0004
													viewpoint_x=viewPoint.x
                                    setweight()
                                                               
                                )
                )
            registerRedrawViewsCallback GW_displayObjectNames   
                startTool AssignSkinVertexWeightTool prompt:"Set Vertex Weight"
