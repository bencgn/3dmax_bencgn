
(
modify="Bend"
Parameter_="Direction"
value_Size=1
Shift_Size=10
Value_senser=1
min_=undefined
max_=undefined
   
	 tool AssignParameter
                (
					
                                local viewpoint_x=0
								local original=execute ("$.modifiers[#"+modify+"]."+Parameter_)
								local val=0
					
								fn round_to val n =
								(
									local mult = 10.0 ^ n
									(floor ((val * mult) + 0.5)) / mult
								)
					
								fn setweight mode= 
								(
									execute ("$.modifiers[#"+modify+"]."+Parameter_+"="+val as string)
                                )                                 
                                on mousePoint clickno do (      
									if clickno > 1 then (
									return  #stop)     
									
                                    viewpoint_x=viewPoint.x
									   
                                )
                                on mouseAbort clickno do (
									setweight false
                                )
                                on mouseMove clickno do (
									 if shiftKey==true then 
									(
										val = ((viewPoint.x-viewpoint_x)*Shift_Size*Value_senser+original)
										if min_!=undefined and val<min_ do val=min_
										if max_!=undefined and val>max_ do val=max_
										setweight false
									)
									else 
									(
										val = ((viewPoint.x-viewpoint_x)*value_Size*Value_senser+original)
										if min_!=undefined and val<min_ do val=min_
										if max_!=undefined and val>max_ do val=max_
										setweight false
									)
									
                                )
                )
startTool AssignParameter
			)