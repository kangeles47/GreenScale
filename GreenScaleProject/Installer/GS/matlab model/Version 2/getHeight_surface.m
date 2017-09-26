function Z_surface = getHeight_surface(surface_id)
global Infor_surface
tilt = Infor_surface{3, surface_id}.Tilt; 

if tilt == 0 || tilt == 180   % the height will be any Z coordinate  
     Z_surface = Infor_surface{4, surface_id}.PolyLoop.CartesianPoint(1, 1).Coordinate{1, 3}*0.3048;
else  % for other non-flat surfaces. the height will always be the average value of the maximum and minimum Z coordinates. 
    le = length(Infor_surface{4, surface_id}.PolyLoop.CartesianPoint); 
    a_data = zeros(le,1);
    for i =1:le
        a_data(i) = Infor_surface{4, surface_id}.PolyLoop.CartesianPoint(i, 1).Coordinate{1, 3} ;       
    end 
     Z_surface = 0.5*(max(a_data)+min(a_data))*0.3048;

end 
         
end 


    