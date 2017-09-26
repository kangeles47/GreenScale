%***********************************

% Loop on each surface
% 1. Start from different surface species

%***********************************

% calculate four surfaces: exterior wall,roof, interior wall and undergroundwall(no transmitted solar energy)

function [ Q_flux, Transmitted_win,Tp,Tp_interior] = Heatflux_surface(i_surface,T_space,R3,C,Infor_surface_simp,Tp,Tp_interior,T_outside_temp,i_time,Infor_space_simp,i_space,Wind_speed_temp,Az_sun,Alt_sun,I_dn,I_df,A,G_space_record,Terrain_cof,ShadowModuleFlag)
% global  Tp Tp_interior T_outside_temp ...
%         i_time Infor_space ...
%        Wind_speed_temp Infor_surface_simp Az_sun Alt_sun

Surface_type = Infor_surface_simp(1, i_surface).Type;
Transmitted_win = 0 ;
Alph_opaque = Infor_surface_simp(1, i_surface).Absorptance;
dt = 3600 ;
A_noWin = Infor_surface_simp(1, i_surface).Area-Infor_surface_simp(i_surface).WindowSurface;
h_surface = Infor_surface_simp(1, i_surface).SurfaceHeight;

Ground_tem = T_space-2;

D=Infor_surface_simp(i_surface).RoughnessCof(1,1);
E=Infor_surface_simp(i_surface).RoughnessCof(1,2);
F=Infor_surface_simp(i_surface).RoughnessCof(1,3);

% store the space name to each surface's side temperature
Tp_interior(i_surface, 2) = i_space ;

if Surface_type==1 %,'ExteriorWall')
    %disp(['Alt_sun: ',num2str(Alt_sun)]);
    if ShadowModuleFlag==1 && Alt_sun > 0
        [Ashadow_wo_win,Ashadow_win]=ShadowModule_fn4(Infor_surface_simp,i_surface,Az_sun,Alt_sun);
    else
        Ashadow_wo_win=0;
        Ashadow_win=0;        
    end
    
    %disp([' ',num2str(C)]);
    
    hc = 3.076;
    % decide the space temperature, assuming the space name will be put
    % in order
     
    Wind_speed_corrected = Wind_speed_temp *(270/10)^0.14*(h_surface/Terrain_cof.sigma).^Terrain_cof.a;
    
    hc_external= D+E*Wind_speed_corrected+F*Wind_speed_corrected^2;
    
    %disp(['Tp_interior(i_surface,i_time+2): ',num2str(Tp_interior(i_surface,i_time+2))]);
    %disp(['Tp(i_surface,i_time+2): ',num2str(Tp(i_surface,i_time+2))]);
    
    R5 = 1/hc;
    R1 = 1/hc_external;
    %disp([' ',num2str(hc_external)]);
    [Transmitted_win,Is] = getTransmitted_solar(i_surface,Ashadow_win,Infor_surface_simp,Az_sun,Alt_sun,I_dn,I_df);
    %disp([' ',num2str(Is)]);
    %Is = Is*A_noWin/(A-Ashadow_wo_win);
    Is = Is*(A_noWin-Ashadow_wo_win)/A;
    
    C2 = C/2;
    C4 = C/2;
    
    M1=C2/dt+1/R1+1/R3;
    M2=C2/dt*Tp(i_surface,i_time+2) + T_outside_temp/R1+Alph_opaque*Is;
    M3=C4/dt+1/R3+1/R5;
    M4=C4/dt*Tp_interior(i_surface,i_time+2)+T_space/R5;
    
    %disp([' ',num2str(R3)]);
    
    T_out= (M4*R3+M3*M2*R3^2)/(M3*M1*R3^2-1);    % T_out is the exterior surface's temperature
    T_in= (M1*T_out-M2)*R3;                        % T_in is the interior surface's temperature
    %disp([' ',num2str(T_in)]);
    
    Tp(i_surface, i_time+3) = T_out;
    Tp_interior(i_surface, i_time+3) = T_in;
    
    
    %%
elseif   Surface_type==2 % 'Roof')  % roof is also an exterior surface
    if ShadowModuleFlag==1 && Alt_sun > 0
        [Ashadow_wo_win,Ashadow_win]=ShadowModule_fn4(Infor_surface_simp,i_surface,Az_sun,Alt_sun);
    else
        Ashadow_wo_win=0;
        Ashadow_win=0;
    end
    tilt = Infor_surface_simp(1, i_surface).Tilt*pi/180;
 
    Wind_speed_corrected = Wind_speed_temp *(270/10)^0.14*(h_surface/Terrain_cof.sigma).^Terrain_cof.a;
    
    hc_external= D+E*Wind_speed_corrected+F*Wind_speed_corrected^2;
    
    [Transmitted_win,Is] = getTransmitted_solar(i_surface,Ashadow_win,Infor_surface_simp,Az_sun,Alt_sun,I_dn,I_df);
%     Is = Is*A_noWin/(A-Ashadow_wo_win);
    Is = Is*(A_noWin-Ashadow_wo_win)/A;
    
    if  tilt==0% flat roof
        hc = 0.948 ; % assume it is reduced convection T_space1 <T2
        R5 = 1/(hc);
        R1 = 1/hc_external;
        
        C2 = C/2;
        C4 = C/2;
        
        M1=C2/dt+1/R1+1/R3;
        M2=C2/dt*Tp(i_surface,i_time+2) + T_outside_temp/R1+Alph_opaque*Is;
        M3=C4/dt+1/R3+1/R5;
        M4=C4/dt*Tp_interior(i_surface,i_time+2)+T_space/R5;
        
        T_out= (M4*R3+M3*M2*R3^2)/(M3*M1*R3^2-1); % T_out is the exterior surface's temperature
        T_in= (M1*T_out-M2)*R3;                     % T_in is the interior surface's temperature
        
        if T_space > T_in
            
            hc = 4.04;
            R5 = 1/(hc);
            
            M1=C2/dt+1/R1+1/R3;
            M2=C2/dt*Tp(i_surface,i_time+2) + T_outside_temp/R1+Alph_opaque*Is;
            M3=C4/dt+1/R3+1/R5;
            M4=C4/dt*Tp_interior(i_surface,i_time+2)+T_space/R5;
            
            T_out= (M4*R3+M3*M2*R3^2)/(M3*M1*R3^2-1); % T_out is the exterior surface's temperature
            T_in= (M1*T_out-M2)*R3;                    % T_in is the interior surface's temperature
            
        end
        
    else     % tiled roof
        
        hc = 2.281 ; % assume it is reduced convection T_space1 <T2
        R5 = 1/(hc);
        R1 = 1/hc_external;
        
        C2 = C/2;
        C4 = C/2;
        
        M1=C2/dt+1/R1+1/R3;
        M2=C2/dt*Tp(i_surface,i_time+2) + T_outside_temp/R1+Alph_opaque*Is;
        M3=C4/dt+1/R3+1/R5;
        M4=C4/dt*Tp_interior(i_surface,i_time+2)+T_space/R5;
        
        T_out= (M4*R3+M3*M2*R3^2)/(M3*M1*R3^2-1); % T1 is the exterior surface's temperature
        T_in= (M1*T_out-M2)*R3;                     % T2 is the interior surface's temperature
        
        if T_space > T_in
            
            hc = 3.87;
            R5 = 1/(hc);
            
            M1=C2/dt+1/R1+1/R3;
            M2=C2/dt*Tp(i_surface,i_time+2) + T_outside_temp/R1+Alph_opaque*Is;
            M3=C4/dt+1/R3+1/R5;
            M4=C4/dt*Tp_interior(i_surface,i_time+2)+T_space/R5;
            
            T_out= (M4*R3+M3*M2*R3^2)/(M3*M1*R3^2-1); % T1 is the exterior surface's temperature
            T_in= (M1*T_out-M2)*R3;                    % T2 is the interior surface's temperature
            
        end
    end
    
    Tp(i_surface, i_time+3) = T_out;
    Tp_interior(i_surface, i_time+3) = T_in;
    
    %%       there is no solar transmitted energy through the interior wall
elseif Surface_type==3 % interior wall
    
    C2=C/2;
    C4=C/2;
    hc = 3.076;
    R5 = 1/hc;
    R1= 1/hc;
    
    % the another side's space name
    Space_id2 = Infor_surface_simp(1, i_surface).RelatedSpace(1,1);
    if Space_id2 == i_space
        Space_id2 = Infor_surface_simp(1, i_surface).RelatedSpace(1,2);
    end
    
    T_space = Infor_space_simp(1, i_space).SpaceTemp;
    T_space2 = Infor_space_simp(1, Space_id2).SpaceTemp;
    
    %% to make the InteriorWall and InteriorFloor use the correct temperature information, A1 and A2 are used to excanged every timestep 
    T2=Tp(i_surface, i_time+2);
    T3=Tp_interior(i_surface, i_time+2);
    % assume that interior walls are always vertical. Vertical walls have constant convection coefficient
    % T_in is the interior surface temperature in the space that we pick.
    %     T_in = (C4*Tp(i_surface, i_time+2)/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*Tp_interior(i_surface, i_time+2)/dt+T_space/R1)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
    %     T_out = (C2*Tp_interior(i_surface, i_time+2)/dt+T_space/R1+(C2/dt+1/R3+1/R1)*(C4*Tp(i_surface, i_time+2)/dt+T_space2/R5)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
    T_in = (C4*T3/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*T2/dt+T_space/R1)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
    T_out = (C2*T2/dt+T_space/R1+(C2/dt+1/R3+1/R1)*(C4*T3/dt+T_space2/R5)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
    
    Tp(i_surface, i_time+3) = T_out ;
    Tp_interior(i_surface, i_time+3) = T_in;
    
    %%
elseif Surface_type==4 %'UndergroundWall')
    hc = 3.096 ;
    R5 = 1/hc;
    C2 = C/2;
    A1=C2/dt*Tp_interior(i_surface,i_time+2)+T_space/R5+Ground_tem/R3+G_space_record(i_space,i_time);
    A2=C2/dt+1/R5+1/R3;
    T_in=A1/A2;
    
    Tp(i_surface, i_time+3) = Ground_tem;
    Tp_interior(i_surface,i_time+3)=T_in;
end

%disp(['D: ',num2str(D)]);
%disp(['E: ',num2str(E)]);
%disp(['F: ',num2str(F)]);
%disp(['R3: ',num2str(R3)]);
Q_flux =  hc * A *(T_in-T_space);
%if Surface_type==3
%    disp(['',num2str(Q_flux)]);
%end
end