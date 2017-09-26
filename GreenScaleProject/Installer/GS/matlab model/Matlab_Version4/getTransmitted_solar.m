%***********************************

% Get the "equivalent" thermal values for each surface
% 1. Start from different categories of surface species
% 2. Calculate an equivalent values that can combine the properties of both
%   opennings and walls in terms of solar absorbtance and emissivity

%***********************************

function   [Transmitted_win,Is] = getTransmitted_solar(i_surface,Ashadow_win,Infor_surface_simp,Az_sun,Alt_sun,I_dn,I_df)
% global   Infor_surface Az_sun Alt_sun Incidence_angle i_time

Conversion = pi/180;
tilt = Infor_surface_simp(1,i_surface).Tilt*Conversion;

Transmitted_win = 0 ;
Az_surface = Infor_surface_simp(1,i_surface).Azimuth*Conversion ;
az_d = abs(Az_sun - Az_surface);

Incidence = acos(sin(Alt_sun)*cos(tilt)+cos(az_d)*cos(Alt_sun)*sin(tilt));
%disp([' ', num2str(Incidence)])
% Incidence1=sin(Alt_sun)*cos(tilt)+cos(az_d)*cos(Alt_sun)*sin(tilt);
% Incidence_angle(surface_id,i_time+1)= cos(Incidence1);
[Is] = getIs_surface(i_surface, tilt, Incidence,az_d,I_dn,I_df,Infor_surface_simp);

% if there is openning there, the U value need to be recalculated
Num_openning = Infor_surface_simp(1, i_surface).N_open;

if Num_openning > 0
    
    for i_opening = 1:Num_openning
        
        % if the openning is window, there is tansmitted energy
        if  Infor_surface_simp(i_surface).Opening(i_opening).WinDoor==1;
            A_openning_noWin = Infor_surface_simp(1,i_surface).Opening(i_opening,1).Area-Ashadow_win(i_opening);
            if cos(Incidence)> 0
                x=[0 40 50 60 70 80 90]*pi/180;
                y=Infor_surface_simp(1,i_surface).Opening(1,i_opening).SHGC(1,:);
                SHGC = interp1(x,y,abs(Incidence),'spline');
            else
                SHGC = 1;
            end
            G_o = A_openning_noWin * SHGC * Is;
            %disp([' ', num2str(A_openning_noWin)])
            Transmitted_win = Transmitted_win + G_o ;
        end
        
    end
    
end
%disp([' ', num2str(Transmitted_win)])
end