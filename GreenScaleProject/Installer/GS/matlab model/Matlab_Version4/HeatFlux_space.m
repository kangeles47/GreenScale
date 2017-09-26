%***********************************

% Loop in each space

%***********************************

function [Q_space,Tp,Tp_interior,G_space_record] = HeatFlux_space(Infor_surface_simp, i_space, Infor_space_simp, G_space_record, i_time,Tp,Tp_interior,T_outside_temp,Wind_speed_temp,Az_sun,Alt_sun,I_dn,I_df,Terrain_cof,ShadowModuleFlag)
% global Infor_surface i_space Infor_space G_space_record i_time

G_space = 0;
Q_space = 0;

% for each space, we know its bounding surfaces
Length_Bounding = length(Infor_space_simp(1, i_space).RelatedSurface);
%  Space_surface = zeros(Length_Bounding,1);

%  for i = 1:Length_Bounding
%   str = Infor_space_simp{7, i_space}(i, 1).ATTRIBUTE.surfaceIdRef ;
%   par_cell = regexp(str,'-','split');
%   Space_surface(i) = str2double(par_cell{1,2}) ;  % store surface order number in each "Space_surface"
%  end
%h_space =  Infor_space_simp(1, i_space).FloorHeight;
%disp([' ', num2str(h_space)])

for surface_order = 1:Length_Bounding
    i_surface = Infor_space_simp(1, i_space).RelatedSurface(surface_order);
    Surface_type = Infor_surface_simp(1, i_surface).Type;
    
    % store the surface related information, T_space, U, R3, and height
    % h_space and h_surface
    T_space = Infor_space_simp(1, i_space).SpaceTemp;
    U = Infor_surface_simp(1, i_surface).U_ave;
    %disp([' ',num2str(U)]);
    C = Infor_surface_simp(1, i_surface).C_ave;
    %disp([' ',num2str(C)]);
    
    h_space =  Infor_space_simp(1, i_space).FloorHeight;

    %disp([' ', num2str(h_space)])
    %Infor_surface_simp(1, i_space).Name
    %Infor_surface_simp(1, i_space).TypeName
    
    h_surface = Infor_surface_simp(1, i_surface).SurfaceHeight;
    
    %disp([' ', num2str(h_surface)])
    %Infor_surface_simp(1, i_surface).TypeName
    %Infor_surface_simp(1, i_surface).Coordinate
    
    A=Infor_surface_simp(1, i_surface).Area;
    
    if ismember(Surface_type,[1,2,3,4])
        
        [Q_surface,G_window,Tp,Tp_interior] = Heatflux_surface(i_surface,T_space,1/U,C,Infor_surface_simp,Tp,Tp_interior,T_outside_temp,i_time,Infor_space_simp,i_space,Wind_speed_temp,Az_sun,Alt_sun,I_dn,I_df,A,G_space_record,Terrain_cof,ShadowModuleFlag);
        %Infor_surface_simp(1, i_surface).TypeName
        %disp([' ',num2str(Q_surface)]);
        
        %Infor_surface_simp(1, i_surface).TypeName
        %Infor_surface_simp(1, i_surface).Name
        %disp([' ', num2str(h_surface)])
        
        Q_space = Q_space+Q_surface;
        G_space = G_space + G_window ;
        %if ismember(Surface_type,[2])
            %disp([' ', num2str(Infor_surface_simp(1, i_surface).Name)])
            %disp([' ', num2str(Q_surface)])
        %end
    elseif Surface_type==5 && h_space < h_surface  % strcmp(Surface_type,'InteriorWall') top
        [Q_top,Tp,Tp_interior] = getTop_heat(i_surface,T_space,1/U,C,A,Infor_surface_simp,Tp,Tp_interior,i_space,i_time,G_space_record,Infor_space_simp);
        Q_space = Q_space + Q_top; 
        %disp([' ', num2str(Q_top)])
%     elseif  ismember(Surface_type,[5,6,7,8])&& h_space == h_surface  % strcmp(Surface_type,'InteriorWall') floor
%         floor_surface_order = i_surface;
    end
    
end

floor_surface_order=Infor_space_simp(1, i_space).FloorSurfaceId;
A = Infor_surface_simp(1, floor_surface_order).Area;
G_space = G_space/A;
%disp([' ',num2str(G_space)]);
G_space_record(i_space,i_time+1) = G_space;
T_space = Infor_space_simp(1, i_space).SpaceTemp;
U = Infor_surface_simp(1, floor_surface_order).U_ave;
C = Infor_surface_simp(1, floor_surface_order).C_ave;
%disp([' ',num2str(C)]);

Surface_type = Infor_surface_simp(1,floor_surface_order).Type;
%Infor_surface_simp(1,floor_surface_order).Type

if Surface_type==5
    [Q_floor,Tp,Tp_interior] = getFloor_heat(floor_surface_order,G_space,T_space,1/U,C,Infor_space_simp,Tp,Tp_interior,i_time,i_space,A,Infor_surface_simp);
    %disp([' ',num2str(Q_floor)]);
elseif Surface_type==6
    [Q_floor,Tp,Tp_interior]= getRaisedFloor_heat(floor_surface_order,G_space,T_space,1/U,C,Tp,Tp_interior,i_time,Wind_speed_temp,A,h_surface);
    
elseif ismember(Surface_type,[7,8]); %     UndergroundSlab and SlabOnGrade are like floor, and there is only one space
    [Q_floor,Tp,Tp_interior] = getGround_heat(floor_surface_order,G_space,T_space,1/U,C,Tp,Tp_interior,i_time,i_space,A);
end

Q_space = Q_space + Q_floor;

if Q_space <0
    Q_space = abs(Q_space);
end

end

