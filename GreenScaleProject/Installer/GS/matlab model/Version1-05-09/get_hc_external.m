%***********************************

% Get the external convection coefficient of exterior surfaces  
  
%***********************************

function [hc_external] =  get_hc_external(Z_surface,Az_surface)
global  Wind_speed_temp Wind_speed_dir 


   Wind_speed = Wind_speed_temp *(Z_surface/10)^0.14;
   
   hc_external= 8.23+4*Wind_speed-0.057*Wind_speed^2;
   
   if 100 < abs(Wind_speed_dir-Az_surface) && abs(Wind_speed_dir-Az_surface) < 260
       hc_external = 0.5* hc_external; % if lee ward, then hc is only half. 
   end 

end 