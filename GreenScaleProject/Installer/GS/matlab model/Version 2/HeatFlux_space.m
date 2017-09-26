%***********************************

% Loop in each space 

%***********************************

function [Q_space,G_space1] = HeatFlux_space()
global Infor_surface i_space Infor_space

G_space = 0; 
Q_space = 0; 
flag = 1 ;


 % for each space, we know its bounding surfaces 
 Length_Bounding = length(Infor_space{7,i_space}); 
 Space_surface = zeros(Length_Bounding,1); 
 
 for i = 1:Length_Bounding 
  str = Infor_space{7, i_space}(i, 1).ATTRIBUTE.surfaceIdRef ; 
  par_cell = regexp(str,'-','split');
  Space_surface(i) = str2double(par_cell{1,2}) ;  % store surface order number in each "Space_surface"
 end 
 

for surface_order = 1:Length_Bounding   
     i_surface = Space_surface(surface_order);
%   i_surface =1; 
     Surface_type = Infor_surface{7, i_surface}.surfaceType;  
     
    if  strncmp(Infor_surface{1, i_surface},'X',1)   
    flag = 0; 
    end 

   if flag == 1 
    % store the surface related information, T_space, U, R3 
     T_space = Infor_space{9, i_space}; 
     U = Infor_surface{11,i_surface}; 
     R3 = 1/U ; 
     C = Infor_surface{10, i_surface} ; 
     
     h_space = Infor_space{10,i_space}; 
     h_surface = Infor_surface{13,i_surface}; 
     
    %%%%%%
    if  strcmp(Surface_type,'ExteriorWall')  ||  strcmp(Surface_type,'Roof') ||strcmp(Surface_type,'InteriorWall')||  strcmp(Surface_type,'UndergroundWall')
                 
               [Q_surface,G_window] = Heatflux_surface(i_surface,T_space,R3,C); 
               Q_space = Q_space+Q_surface;  
               G_space = G_space + G_window ;        

    elseif strcmp(Surface_type,'InteriorFloor')&& h_space < h_surface  % strcmp(Surface_type,'InteriorWall') top 
        [Q_top] = getTop_heat(i_surface,T_space,R3,C);
        Q_space = Q_space + Q_top; 
    elseif strcmp(Surface_type,'InteriorFloor')&& h_space == h_surface  % strcmp(Surface_type,'InteriorWall') floor 
        floor_surface_order =i_surface; 
    end 
   end 

flag =1 ; 
end 
%  i_surface=4; 
     i_surface = floor_surface_order;
      A = Infor_surface{8, i_surface};
      G_space1 = G_space; 
      G_space = 1*G_space1/A; 
     T_space = Infor_space{9, i_space}; 
     U = Infor_surface{11, i_surface}; 
     R3 = 1/U ;
     C = Infor_surface{10, i_surface} ;
     
   
     Surface_type = Infor_surface{7, i_surface}.surfaceType; 

             if strcmp(Surface_type,'InteriorFloor')     
                  Q_floor = getFloor_heat(i_surface,G_space,T_space,R3,C);
          
             elseif strcmp(Surface_type,'RaisedFloor')     
                  Q_floor = getRaisedFloor_heat(i_surface,G_space,T_space,R3,C);
                  
             elseif strcmp(Surface_type,'UndergroundSlab')|| strcmp(Surface_type,'SlabOnGrade'); %     UndergroundSlab and SlabOnGrade are like floor, and there is only one space 
                  Q_floor = getGround_heat(i_surface,G_space,T_space,R3,C);         
             end       
 

Q_space=Q_space+Q_floor; 

if Q_space >0
    Q_space = Q_space - 0*G_space1; 
else 
    Q_space = abs(Q_space) +0*G_space1;
end 

end 

