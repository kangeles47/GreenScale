function  [Q_floor,Tp,Tp_interior] = getRaisedFloor_heat(surface_id,G_space,T_space,R3,C,Tp,Tp_interior,i_time,Wind_speed_temp,A,h_surface)

% for a interiorfloor which is a top of the space, the transmitted solar energy of another
% side also need to be calculated
% global   Tp Tp_interior
%         i_time Wind_speed_temp
dt = 3600 ;
% Wind_speed = Wind_speed_temp *(Z_surface/10)^0.5;   % Stable air above human inhabited areas:
% hc_external= 8.23+4*Wind_speed-0.057*Wind_speed^2;

 
Wind_speed_corrected = Wind_speed_temp *(270/10)^0.14*(h_surface/Terrain_cof.sigma).^Terrain_cof.a;
hc_external= D+E*Wind_speed_corrected+F*Wind_speed_corrected^2;

[Transmitted_win,Is] = getTransmitted_solar(surface_id);
Is = 0.7*Is;
disp(['Is: ',num2str(Is)]);

C2 = C/2;
C4 = C/2;


hc = 4.04 ; % assume it is reduced convection T_space <T2
R5 = 1/(hc);
R1 = 1/hc_external;

M1=C2/dt+1/R1+1/R3;
M2=C2/dt*Tp(surface_id,i_time+2) + T_outside_temp/R1+Is;
M3=C4/dt+1/R3+1/R5;
M4=C4/dt*Tp_interior(surface_id,i_time+2)+T_space/R5;

T_out= (M4*R3+M3*M2*R3^2+R3*G_space)/(M3*M1*R3^2-1); % T_out is the exterior surface's temperature
T_in= (M1*T_out-M2)*R3;                     % T_in is the interior surface's temperature

if T_space > T_in
    
    hc = 0.948;
    R5 = 1/(hc);
    
    M1=C2/dt+1/R1+1/R3;
    M2=C2/dt*Tp(surface_id,i_time+2) + T_outside_temp/R1+Is;
    M3=C4/dt+1/R3+1/R5;
    M4=C4/dt*Tp_interior(surface_id,i_time+2)+T_space/R5;
    
    T_out= (M4*R3+M3*M2*R3^2+R3*G_space)/(M3*M1*R3^2-1); % T_out is the exterior surface's temperature
    T_in= (M1*T_out-M2)*R3;                    % T_in is the interior surface's temperature
    
end

Tp(surface_id, i_time+3) = T_out;
Tp_interior(surface_id, i_time+3) = T_in;

Q_floor =  hc * A *(T_in-T_space);
%disp(['Q_floor_raised: ',num2str(Q_floor)]);
%disp('here');
end