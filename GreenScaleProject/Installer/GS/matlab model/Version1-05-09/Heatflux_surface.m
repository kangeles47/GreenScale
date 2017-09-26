%***********************************

% Loop on each surface
% 1. Start from different categories of surface species

%***********************************

function [ Q_flux, Transmitted_win ,T2] = Heatflux_surface(surface_id)
global Wind_speed_dir Infor_surface Tp T_outside_temp ...
    Ground_tem i_time Infor_space Num_space Space_name T_sky_temp
Surface_type = Infor_surface{7, surface_id}.surfaceType;
tilt = Infor_surface{3, surface_id}.Tilt*pi/180;
A = getA_surface(surface_id);
Transmitted_win = 0 ;
Az_surface = Infor_surface{3, surface_id}.Azimuth; % in celcius

%lee ward surface will take only half of the outdoor convectionb
%coefficient. and windward surface take the whole.

if strcmp(Surface_type,'ExteriorWall')
    hc = 3.076;
    % decide the space temperature
    for i_space = 1:Num_space
        if strcmp(Infor_space{8,i_space}.id, Space_name)
            T1 = Infor_space{9, i_space};
            break;
        end
    end
    Z_surface=0.5*Infor_surface{3,surface_id}.Height*0.3048;
    disp('------------------');
    surface_id
    [hc_external] = get_hc_external(Z_surface,Az_surface)
    
    [hr_sky,hr_air,Alpha_e,Epsilon_e,U,Transmitted_win,Is] = Equivalent_value(surface_id);
    
    Down = Epsilon_e *(hr_sky+hr_air)+U + hc_external;
    B1 = (Alpha_e*Is+Epsilon_e*(hr_sky*T_sky_temp+hr_air*T_outside_temp)+hc_external*T_outside_temp)/Down;
    B2 = U/Down;
    
    
    T2 = (T1 +U*B1/hc)/((1-B2)*U/hc+1);  % hc is the natural convection coefficient; T2 is the interior surface temperature.
    T_ex =  B1 + B2 * T2;
    Tp(surface_id, i_time+2) = T_ex;
    
    
    
elseif   strcmp(Surface_type, 'Roof')  % roof is also an exterior surface
    disp('------------------');
    surface_id
    Z_surface = Infor_surface{3, surface_id}.CartesianPoint.Coordinate{1,3}*0.3045;
    [hc_external] = get_hc_external(Z_surface,Az_surface)
    
    if tilt >0
        if 100 < abs(Wind_speed_dir-Az_surface) < 260
            hc_external = 0.5* hc_external; % if lee ward, then hc is only half.
        end
    end
    
    for i_space = 1:Num_space
        if strcmp(Infor_space{8,i_space}.id, Space_name)
            T1 = Infor_space{9, i_space};
            break;
        end
    end
    
    hc = 0.948 ; % assume it is reduced convection T2 >T1
    
    [hr_sky,hr_air,Alpha_e,Epsilon_e,U,Transmitted_win,Is] = Equivalent_value(surface_id);
    
    Down = Epsilon_e *(hr_sky+hr_air)+U + hc_external;
    B1 = (Alpha_e*Is+Epsilon_e*(hr_sky*T_sky_temp+hr_air*T_outside_temp)+hc_external*T_outside_temp)/Down;
    B2 = U/Down;
    
    
    T2 = (T1 +U*B1/hc)/((1-B2)*U/hc+1);
    % hc is the natural convection coefficient; T2 is the interior surface temperature.
    
    if T1 > T2
        hc = 4.04;
        Down = Epsilon_e *(hr_sky+hr_air)+U + hc_external;
        B1 = (Alpha_e*Is+Epsilon_e*(hr_sky*T_sky_temp+hr_air*T_outside_temp)+hc_external*T_outside_temp)/Down;
        B2 = U/Down;
        T2 = (T1+U*B1/hc)/((1-B2)*U/hc+1);
    end
    
    T_ex =  B1 + B2 * T2;
    Tp(surface_id, i_time+2) = T_ex;
    
    
elseif  strcmp(Surface_type,'RaisedFloor')
    disp('------------------');
    surface_id
    Z_surface = Infor_surface{3, surface_id}.CartesianPoint.Coordinate{1,3};
    [hc_external] = get_hc_external(Z_surface,Az_surface)
    
    if tilt >0
        if 100 < abs(Wind_speed_dir-Az_surface) < 260
            hc_external = 0.5* hc_external; % if lee ward, then hc is only half.
        end
    end
    
    for i_space = 1:Num_space
        if strcmp(Infor_space{8,i_space}.id, Space_name)
            T1 = Infor_space{9, i_space};
            break;
        end
    end
    
    hc = 0.948 ; % assume it is reduced convection T2 >T1
    [G_solar, G_longwave,Denominator,U,Transmitted_win] = get_absorbed1(surface_id);
    
    Down = U + hc_external + Denominator;
    
    B1 = (G_solar + G_longwave + hc_external*T_outside_temp )/Down;
    B2 = U/Down;
    
    T2 = (T1 +U*B1/hc)/((1-B2)*U/hc+1);  % hc is the natural convection coefficient; T2 is the interior surface temperature.
    
    if T1 > T2
        hc = 4.04;
        Down = U + hc_external + Denominator;
        B1 = (G_solar + G_longwave + hc_external*T_outside_temp )/Down;
        B2 = U/Down;
        T2 = (T1+U*B1/hc)/((1-B2)*U/hc+1);
    end
    
    T_ex =  B1 + B2 * T2;
    Tp(surface_id, i_time+2) = T_ex;
    
    
elseif  strcmp(Surface_type,'InteriorFloor')
    [U] = getU_surface(surface_id);
    
    if  strncmp(Infor_surface{1, surface_id},'B',1)  % for "bottom" surface, it has two adjacent spaces with the same name.
        
        for i_space = 1:Num_space
            if strcmp(Infor_space{8,i_space}.id, Space_name)
                T1 = Infor_space{9, i_space};
                break;
            end
        end
        
        hc = 0.948 ; % assume it is reduced convection T1 >T2
        T2 =( T1*hc/U+Ground_tem)/(hc/U+1);
        if T1 < T2
            hc = 4.04;
            T2 =( T1*hc/U+Ground_tem)/(hc/U+1);
        end
        
        
    else strncmp(Infor_surface{1, surface_id},'T',1)  % Intermediate Floor
        
        Space_name1 = Infor_surface{2, surface_id}(1, 1).ATTRIBUTE.spaceIdRef;
        Space_name2 = Infor_surface{2, surface_id}(2, 1).ATTRIBUTE.spaceIdRef;
        
        % Space_name
        for i_space = 1:Num_space
            
            if strcmp(Infor_space{8,i_space}.id, Space_name1)
                T_space1 = Infor_space{9, i_space};
                break;
            else strcmp(Infor_space{8,i_space}.id, Space_name2)
                T_space2 = Infor_space{9, i_space};
                break;
            end
        end
        
        
        if strcmp(Space_name, Space_name1)
            T1 = T_space1;
            
            hc1 = 0.948 ; % assume it is reduced convection:  Tspace1 >Tk1 , then Tk1>Tk2 > Tspace2
            hc2 = 4.04 ;
            B1 = hc1/U;
            B2 = hc2/U;
            T2 = ((B2+1)*B1*T_space1+B2*T_space2)/(B1*B2+B1+B2);
            if T1 < T2
                hc1 = 4.04;
                hc2 = 0.948;
                B1 = hc1/U;
                B2 = hc2/U;
                T2 = ((B2+1)*B1*T_space1+B2*T_space2)/(B1*B2+B1+B2);
            end
            hc = hc1;
            
        else strcmp(Space_name, Space_name2)
            T1 = T_space2;
            hc2 = 0.948 ; % assume it is reduced convection:  Tspace1 >Tk1 , then Tk1>Tk2 > Tspace2
            hc1 = 4.04 ;
            B1 = hc1/U;
            B2 = hc2/U;
            T2 = ((B1+1)*B2*T_space2+B2*T_space1)/(B1*B2+B1+B2);
            if T1 < T2
                hc2 = 4.04;
                hc1 = 0.948;
                B1 = hc1/U;
                B2 = hc2/U;
                T2 = ((B1+1)*B2*T_space2+B2*T_space1)/(B1*B2+B1+B2);
            end
            hc = hc2;
        end
        
    end
    
    
elseif strcmp(Surface_type,'InteriorWall')
    [U] = getU_surface(surface_id);
    
    Space_name1 = Infor_surface{2, surface_id}(1, 1).ATTRIBUTE.spaceIdRef;
    Space_name2 = Infor_surface{2, surface_id}(2, 1).ATTRIBUTE.spaceIdRef;
    
    % Space_name
    for i_space = 1:Num_space
        
        if strcmp(Infor_space{8,i_space}.id, Space_name1)
            T_space1 = Infor_space{9, i_space};
            break;
        else strcmp(Infor_space{8,i_space}.id, Space_name2)
            T_space2 = Infor_space{9, i_space};
            break;
        end
    end
    
    hc = 3.076; Bi = hc/U;    % assume that interior walls are always vertical. Vertical walls have constant convection coefficient
    if strcmp(Space_name, Space_name1)
        T1 = T_space1;
        T2 = ((Bi)*T_space1+T_space2)/(2+l*Bi);
    else strcmp(Space_name, Space_name2)
        T1 = T_space2;
        T2 = ((Bi)*T_space2+T_space1)/(2+l*Bi);
    end
    
    
    
elseif strcmp(Surface_type,'UndergroundSlab')|| strcmp(Surface_type,'SlabOnGrade')
    [U] = getU_surface(surface_id);
    
    for i_space = 1:Num_space
        if strcmp(Infor_space{8,i_space}.id, Space_name)
            T1 = Infor_space{9, i_space};
            break;
        end
    end
    
    hc = 0.948 ; % assume it is reduced convection T2 >T1
    T2 =( T1*hc/U+Ground_tem)/(hc/U+1);
    if T1 > T2
        hc = 4.04;
        T2 =( T1*hc/U+Ground_tem)/(hc/U+1);
    end
    
else strcmp(Surface_type,'UndergroundWall')
    [U] = getU_surface(surface_id);
    for i_space = 1:Num_space
        if strcmp(Infor_space{8,i_space}.id, Space_name)
            T1 = Infor_space{9, i_space};
            break;
        end
    end
    
    hc = 3.076 ; %  assume all walls are vertical
    T2 =( T1*hc/U+Ground_tem)/(hc/U+1);
    
end

disp('------------------');
         surface_id
Q_flux =  hc * A *(T1-T2)

end