function [A] = getA_surface_noOpenning(surface_id)
% Notice that the unit in gbXML file is feet. 
% first check whether this surface contains opennings. 
global Infor_surface 

A0 = 0; 
A = Infor_surface{8, surface_id};

if isstruct(Infor_surface{5,surface_id})    
      %consider a surface may have multiple windows and doors. 
      Num_openning = length(Infor_surface{5,surface_id}); 
      
   for opening_id=1:Num_openning      
     if  strcmp(Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.openingType, 'OperableWindow') || strcmp(Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.openingType,'FixedWindow' )...
        || strcmp(Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.openingType,'NonSlidingDoor') 
      temp = Infor_surface{5, surface_id}(opening_id,1).RectangularGeometry.Height*0.3048*Infor_surface{5, surface_id}(opening_id,1).RectangularGeometry.Width*0.3048;
      A0 = A0+temp; 
     end      
   end 
    
A=A-A0;   

end 


end