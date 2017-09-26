%***********************************

% Get the surface area of an openning 

%***********************************
function [Ao] = getA_opening(surface_id,opening_id)

global Infor_surface

        height=Infor_surface{5, surface_id}(opening_id,1).RectangularGeometry.Height*0.3048;
        width=Infor_surface{5, surface_id}(opening_id,1).RectangularGeometry.Width*0.3048;
        Ao=height*width; 
        
end