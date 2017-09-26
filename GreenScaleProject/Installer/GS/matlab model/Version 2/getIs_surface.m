%***********************************

% Get the Solar Radiation from each window with a particular incidence angle 
  
%***********************************

function [Is] = getIs_surface(surface_id, tilt, Incidence,az_d ) 
global  Infor_surface I_dn I_df Alt_sun

% if cos(Incidence)> -0.2
%    Y = 0.55+0.437*cos(Incidence)+0.313*(cos(Incidence))^2; 
% else 
%     Y= 0.45;
% end; 

Y=1;
C = 0.118 ;
Rho_g = 0.2;
Ig = I_dn*(C+sin(Alt_sun))*Rho_g*(1-cos(tilt))/2; % zero for roof 
% Roof is different from walls 
if strcmp(Infor_surface{7, surface_id}.surfaceType, 'Roof')
if tilt == 0 

          Is =I_dn*abs(cos(Incidence))+I_df*(1+cos(tilt))/2;
           
else tilt > 0; 
    
      if  az_d < pi/2 ||   az_d > 3*pi/2 % toward the sun 

          Is = I_dn*abs(cos(Incidence))+I_df*(1+cos(tilt))/2++Ig;
           
        else  % standing against sun 
            
          Is = I_df*(1+cos(tilt))/2+Ig;

      end 
end 

elseif strcmp(Infor_surface{7, surface_id}.surfaceType, 'RaisedFloor')
    
    if tilt == 0 

          Is =I_df*(1+cos(tilt))/2+Ig;
           
    else tilt > 0; 
    
        if  az_d < pi/2 ||   az_d > 3*pi/2 % toward the sun 

          Is = I_dn*abs(cos(Incidence))+I_df*(1+cos(tilt))/2+Ig;
           
        else  % standing against sun 
            
          Is = I_df*(1+cos(tilt))/2+Ig;

        end 
   end 

% Normal wall surfaces 
else 
    
    if az_d < pi/2  ||   az_d > 3*pi/2  % toward the sun 

          Is = I_dn*abs(cos(Incidence))+I_df*(1+cos(tilt))/2/Y+Ig;
           
        else  % standing against sun 
            
          Is = I_df*(1+cos(tilt))/2/Y+Ig;
    
    end 
end 

end 