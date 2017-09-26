%***********************************

% Get the "equivalent" thermal values for each surface 
% 1. Start from different categories of surface species 
% 2. Calculate an equivalent values that can combine the properties of both
%   opennings and walls in terms of solar absorbtance and emissivity 

%***********************************

function [hr_sky,hr_air,Alpha_e,Epsilon_e,U,Transmitted_win,Is] = Equivalent_value(surface_id)
global  T_outside_temp Tp i_time Infor_surface Az_sun Alt_sun T_sky_temp

sigma= 5.67e-8; 
Conversion = pi/180;
tilt = Infor_surface{3, surface_id}.Tilt*Conversion; 
Beta = ((1+cos(tilt))/2)^0.5; 

Epsilon_win = 0.84;    % default emissivity of window from Energy+  
Epsilon_opaque= 0.9 ;  % thermal emissivity  wal = door = roof any construction material 

Alph_opaque = 0.7;     % solar absorbtance

Transmitted_win = 0 ; 
A_total_openning = 0 ;
A= getA_surface(surface_id); 
UA = 0; 

M_sky = Beta*(1+cos(tilt))/2;
M_air = (1-Beta)*(1+cos(tilt))/2+(1-cos(tilt))/2; 

hr_sky = sigma*M_sky*(Tp(surface_id,i_time+1)^4-T_sky_temp^4)/(Tp(surface_id,i_time+1)-T_sky_temp)
hr_air = sigma*M_air*(Tp(surface_id,i_time+1)^4-T_outside_temp^4)/(Tp(surface_id,i_time+1)-T_outside_temp) 

Alpa_win=0; 
Az_surface = Infor_surface{3, surface_id}.Azimuth*Conversion ; 
A_nowin=getA_surface_noWindow(surface_id); 
az_d = abs(Az_sun - Az_surface); 
Incidence = acos(sin(Alt_sun)*cos(tilt)+cos(az_d)*cos(Alt_sun)*sin(tilt));

[Is] = getIs_surface(surface_id, tilt,Incidence,az_d) 

% if there is openning there, the U value and radiation need to be reconsidered 
if isstruct(Infor_surface{5,surface_id})  
     Num_openning = length(Infor_surface{5,surface_id});
     
       for i_openning = 1:Num_openning 
           % if the openning is door 
          G_o = 0 ;   
          
          % if the openning is window, there is tansmitted energy through
          % windows 
           if strcmp(Infor_surface{5, surface_id}(i_openning,1).ATTRIBUTE.openingType, 'OperableWindow')|| strcmp(Infor_surface{5, surface_id}(i_openning,1).ATTRIBUTE.openingType,'FixedWindow' )   
          
            [Ts , Alph_win1] = getTs_win(surface_id,i_openning); 
            Alpa_win = Alph_win1 ;
            A_openning = getA_opening(surface_id,i_openning);        
            G_o = A_openning * Ts * Is;     
            
           end
     
      Transmitted_win = Transmitted_win + G_o ;  
      A_openning = getA_opening(surface_id,i_openning);
      A_total_openning = A_total_openning + A_openning;  
      U_openning = getU_opening(surface_id,i_openning);
      UA = UA + U_openning*A_openning;                       
       
       end 
      
       UA = UA + getU_surface(surface_id)*(A-A_total_openning); % the equvalent conductivity of the whole surface wall including the window, door and wall is calculated;
       U = UA/A       
       Epsilon_e = (A_nowin*Epsilon_opaque+(A-A_nowin)*Epsilon_win)/A
       Alpha_e = (A_nowin*Alph_opaque+(A-A_nowin)*Alpa_win)/A   
       
 else % no openning    
     
       U = getU_surface(surface_id) 
       Epsilon_e = Epsilon_opaque
       Alpha_e = Alph_opaque    
       
end

end 