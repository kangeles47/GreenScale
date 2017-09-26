%***********************************

% Get the "equivalent" thermal values for each surface 
% 1. Start from different categories of surface species 
% 2. Calculate an equivalent values that can combine the properties of both
%   opennings and walls in terms of solar absorbtance and emissivity 

%***********************************

function   [Transmitted_win,Is] = getTransmitted_solar(surface_id)    
global   Infor_surface Az_sun Alt_sun Incidence_angle i_time 

Conversion = pi/180;
tilt = Infor_surface{3, surface_id}.Tilt*Conversion;    
Transmitted_win = 0 ; 
Az_surface = Infor_surface{3, surface_id}.Azimuth*Conversion ;  
az_d = abs(Az_sun - Az_surface); 
Incidence = acos(sin(Alt_sun)*cos(tilt)+cos(az_d)*cos(Alt_sun)*sin(tilt));
Incidence1=sin(Alt_sun)*cos(tilt)+cos(az_d)*cos(Alt_sun)*sin(tilt);
Incidence_angle(surface_id,i_time+1)= Incidence1;
[Is] = getIs_surface(surface_id, tilt,Incidence,az_d); 

% if there is openning there, the U value need to be recalculated
if isstruct(Infor_surface{5,surface_id})  

 Num_openning = length(Infor_surface{5,surface_id});
     
       for i_openning = 1:Num_openning 
         
          % if the openning is window, there is tansmitted energy 
           if strcmp(Infor_surface{5, surface_id}(i_openning,1).ATTRIBUTE.openingType, 'OperableWindow')|| strcmp(Infor_surface{5, surface_id}(i_openning,1).ATTRIBUTE.openingType,'FixedWindow' )                  
            A_openning = getA_opening(surface_id,i_openning);   
            SHGC = getSHGC_win(surface_id,i_openning); 
            G_o = A_openning * SHGC * Is;     
            Transmitted_win = Transmitted_win + G_o ;           
           end 
           
       end 
      
end

end 