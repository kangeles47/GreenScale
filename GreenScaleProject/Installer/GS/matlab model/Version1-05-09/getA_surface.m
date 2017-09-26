function [A] = getA_surface(surface_id)
% Notice that the unit in gbXML file is feet. 
% first check whether this surface contains opennings. 
global Infor_surface 

% A0 = 0; 
% temp=0; 
A=Infor_surface{3,surface_id}.Height*Infor_surface{3,surface_id}.Width*0.3048*0.3048; 

% if isstruct(Infor_surface{5,surface_id}) 
%     
%     % Q1 window and doors 
%       %consider a surface may have multiple windows and doors. 
%       Num_openning = length(Infor_surface{5,surface_id}); 
%       
%    for i_openning1=1:Num_openning 
%     
%       temp = getA_opening(surface_id, i_openning1);
%       A0 = A0+temp; 
%    end 
%     % Cancel the opennings surface area 
%     
% A=A-A0;         
% end 


end