function Z_surface = getHeight_surface(surface_id,Infor_surface_simp)
% global Infor_surface
tilt = Infor_surface_simp(1, surface_id).Tilt; 

if tilt == 0 || tilt == 180   % the height will be any Z coordinate  
     Z_surface = Infor_surface_simp(1, surface_id).Coordinate(1,3)*0.3048;
     %Z_surface
else  % for other non-flat surfaces. the height will always be the average value of the maximum and minimum Z coordinates. 
    le = length(Infor_surface_simp(1, surface_id).Coordinate); 
    a_data = zeros(le,1);
    for i =1:le
        a_data(i) = Infor_surface_simp(1, surface_id).Coordinate(i,3);       
    end 
     Z_surface = 0.5*(max(a_data)+min(a_data))*0.3048;
end 
Z_surface         
end 


    