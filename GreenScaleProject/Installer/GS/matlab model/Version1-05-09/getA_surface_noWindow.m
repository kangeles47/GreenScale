function [A] = getA_surface_noWindow(surface_id)
% Notice that the unit in gbXML file is feet. 
% first check whether this surface contains opennings. 
global Infor_surface 

A0 = 0; 
% temp = 0; 
% flag =1; 
A=Infor_surface{3,surface_id}.Height*Infor_surface{3,surface_id}.Width*0.3048*0.3048; 

if isstruct(Infor_surface{5,surface_id}) 
    
      %consider a surface may have multiple windows and doors. 
      Num_openning = length(Infor_surface{5,surface_id}); 
      
   for opening_id=1:Num_openning 
      
     if  strcmp(Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.openingType, 'OperableWindow') || strcmp(Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.openingType,'FixedWindow' )
%         flag = 0 ;  % only eliminate window surface areas from total walls. 
%      end 
     
%      if flag == 0
      temp = getA_opening(surface_id, opening_id);
      A0 = A0+temp; 
     end 
     
   end 
    % Cancel the opennings surface area 
    
A=A-A0;         
end 

A
end