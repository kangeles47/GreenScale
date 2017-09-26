function [A] = getA_surface(surface_id)
% Notice that the unit in gbXML file is feet. 
% first check whether this surface contains opennings. 

global Infor_surface 

A=Infor_surface{3,surface_id}.Height*Infor_surface{3,surface_id}.Width*0.3048*0.3048; 

end