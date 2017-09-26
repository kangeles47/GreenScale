%***********************************

% Get the Solar Radiation from each window with a particular incidence angle 
  
%***********************************

function [Is] = getIs_surface(surface_id, tilt, Incidence,az_d ) 
global  Infor_surface I_dn I_df 
disp('GET IS SURFACE')
tilt
Incidence
az_d
I_dn 
I_df 

% Roof is different from walls 
if strcmp(Infor_surface{7, surface_id}.surfaceType, 'Roof')
if tilt == 0 

          Is =I_dn*abs(cos(Incidence))+I_df*(1+cos(tilt))/2;
           
else tilt > 0; 
    
      if  az_d < pi/2 ||   az_d > 3*pi/2 % toward the sun 

          Is = I_dn*abs(cos(Incidence))+I_df*(1+cos(tilt))/2;
           
        else  % standing against sun 
            
          Is = I_df*(1+cos(tilt))/2;

      end 
end 

elseif strcmp(Infor_surface{7, surface_id}.surfaceType, 'RaisedFloor')
    
    if tilt == 0 

          Is =I_df*(1+cos(tilt))/2;
           
    else tilt > 0; 
    
        if  az_d < pi/2 ||   az_d > 3*pi/2 % toward the sun 

          Is = I_dn*abs(cos(Incidence))+I_df*(1+cos(tilt))/2;
           
        else  % standing against sun 
            
          Is = I_df*(1+cos(tilt))/2;

        end 
   end 

% Normal wall surfaces 
else 
    
    if az_d < pi/2  ||   az_d > 3*pi/2  % toward the sun 

          Is = I_dn*abs(cos(Incidence))+I_df*(1+cos(tilt))/2;
           
        else  % standing against sun 
            
          Is = I_df*(1+cos(tilt))/2;
    
    end 
end 