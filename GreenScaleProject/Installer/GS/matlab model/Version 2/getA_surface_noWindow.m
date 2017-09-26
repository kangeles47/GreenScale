function [A] = getA_surface_noWindow(surface_id)
% Notice that the unit in gbXML file is feet. 
% first check whether this surface contains opennings. 
% this is 
global Infor_surface 

A0 = 0; 
A=Infor_surface{3,surface_id}.Height*Infor_surface{3,surface_id}.Width*0.3048*0.3048; 
if isstruct(Infor_surface{5,surface_id})    
      %consider a surface may have multiple windows and doors. 
      Num_openning = length(Infor_surface{5,surface_id}); 
   for opening_id=1:Num_openning 
      
     if  strcmp(Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.openingType, 'OperableWindow') || strcmp(Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.openingType,'FixedWindow' )
      temp = Infor_surface{5, surface_id}(opening_id,1).RectangularGeometry.Height*0.3048*Infor_surface{5, surface_id}(opening_id,1).RectangularGeometry.Width*0.3048;
      A0 = A0+temp; 
     end    
   end 

A=A-A0;         
end 
end