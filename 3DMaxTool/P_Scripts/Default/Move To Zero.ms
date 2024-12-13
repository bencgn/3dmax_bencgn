
      (
         
         
         function get_floor num=(return (floor(num*1000))/1000)
         undo on(
         if $ !=undefined do
            (
               
               center=[0,0,0]
               center2=[0,0,0]
               
               for i in $selection do (center+=i.pos);    
               center=center/selection.count
               
               if (center.x==0 and center.y==0) then
                  (
                     check_x_y_zero=true; -- 모든 오브젝트의 x와 y가 0,0 인지 체크변수
                     for i2 in $selection do 
                        (if (i2.pos.x!=0 or i2.pos.y!=0) do ($selection.pos.x=0; $selection.pos.y=0; check_x_y_zero=false; break))
                     if check_x_y_zero==true do ($.pos.z=0)
                  )
                  
               else 
                  (
                     for i3 in $selection do
                     (i3.pos.x=i3.pos.x-center.x; i3.pos.y=i3.pos.y-center.y;)
                     for i in $selection do (center2+=i.pos);    
                     center2=center2/selection.count;
                     if ((get_floor center2.x==get_floor center.x) and (get_floor center2.y==get_floor center.y)) do ($selection.pos.x=0; $selection.pos.y=0;)
                  )
                  format "%, %, %이다\n" (get_floor center2.y) (get_floor center.y) center2
            )
         )   
      )
