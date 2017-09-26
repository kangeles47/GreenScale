%***********************************

%This function is used for research purpose and do validations  

%***********************************

function  Weather_infor = Fakeweather(Weather_infor1)


%%  ########################################################### 
% 6 Dry Bulb Temperature {C}
% Weather_infor1(:,6)=3;                                          

%%  ###########################################################

% 7 Dew Point Temperature  {C}
Weather_infor1(:,7)=99.9;

% 8 Relative Humidity  {%}  effect the radiation 
Weather_infor1(:,8)=999;

% 9 Atmospheric Station Pressure {Pa}
Weather_infor1(:,9)=999999;

% 
% Radiation:
% 10 Extraterrestrial Horizontal  {W/m2}
Weather_infor1(:,10)=9999;

% 11 Extraterrestrial Direct Normal  {W/m2}
Weather_infor1(:,11)=9999;

% 12 Horizontal Infrared Radiation from Sky   {W/m2}
% Weather_infor1(:,12)=0;
% Weather_infor1(:,12)=328.6365;
% Weather_infor1(:,12)=282;

% 13 Global Horizontal   {W/m2}
Weather_infor1(:,13)=9999;

%%  ###########################################################
% 14 Direct Normal       {W/m2}
% Weather_infor1(:,14)=0;
% Weather_infor1(:,14)=10;

% aa = [1 2 3 4 5 6 7 17 18 19 20 21 22 23 24]
% for i=1:744
% 
%     if Weather_infor1(i,4) == 1||Weather_infor1(i,4) == 2||Weather_infor1(i,4) == 3||Weather_infor1(i,4) == 4||Weather_infor1(i,4) == 5||Weather_infor1(i,4) == 6||...
%             Weather_infor1(i,4) == 7||Weather_infor1(i,4) == 17||Weather_infor1(i,4) == 18||Weather_infor1(i,4) == 19||Weather_infor1(i,4) == 20||Weather_infor1(i,4) == 21||...
%             Weather_infor1(i,4) == 22||Weather_infor1(i,4) == 23||Weather_infor1(i,4) == 24
%         Weather_infor1(i,14) = 0; 
%     else 
%          Weather_infor1(i,14)=10;
%     end 
% 
% end 

% 15 Diffuse Horizontal   {W/m2}
%   Weather_infor1(:,15)=0;
% for i=1:744
%     if Weather_infor1(i,4) == 1||Weather_infor1(i,4) == 2||Weather_infor1(i,4) == 3||Weather_infor1(i,4) == 4||Weather_infor1(i,4) == 5||Weather_infor1(i,4) == 6||...
%             Weather_infor1(i,4) == 7||Weather_infor1(i,4) == 17||Weather_infor1(i,4) == 18||Weather_infor1(i,4) == 19||Weather_infor1(i,4) == 20||Weather_infor1(i,4) == 21||...
%             Weather_infor1(i,4) == 22||Weather_infor1(i,4) == 23||Weather_infor1(i,4) == 24
%         Weather_infor1(i,15) = 0; 
%     else 
%          Weather_infor1(i,15)=20;
%     end 
% 
% end 
 
%%  ###########################################################
% Illuminance:
% 16 Global Horizontal   {lux}
Weather_infor1(:,16)=999999;

% 17 Direct Normal       {lux}
Weather_infor1(:,17)=999999;
% 18 Diffuse Horizontal   {lux}
Weather_infor1(:,18)=999999;
% 19 Zenith Luminance     {Cd/m2}  candela per square metre
Weather_infor1(:,19)=9999;
 


%%  ###########################################################
% Wind:
% 20 Direction   {deg}

% Weather_infor1(:,20)=30;
% Weather_infor1(:,20)=30;
% 21 Speed       {m/s}

% Weather_infor1(:,21)=3.1;
%  Weather_infor1(:,21)=3.1;
 
%%  ###########################################################


% Sky cover:
% 22 Total      {.1}
Weather_infor1(:,22)=99;
% 23 Opaque      {.1}
Weather_infor1(:,23)=99;
% 24 Visibilty   {km}
Weather_infor1(:,24)=9999;
% 25 Ceiling Height  {m}
Weather_infor1(:,25)=99999;
% Present weather:
% 26 Observation 
% 27 Codes 
% 
% 28 Precipitation Water mm
Weather_infor1(:,28)=999;
% 29 Aerosol Optical Depth  0.001
Weather_infor1(:,29)=0.999;
% 
% Snow:
% 30 Depth 
Weather_infor1(:,30)=999;
% 31 Days since Last Snowfall 
Weather_infor1(:,31)=99;
 
% 32 albedo  
Weather_infor1(:,32)=999;
 % 33 Liquid precifpitation depth mm
 Weather_infor1(:,33)=999;
  
% 34 Liquid Precipitation Quantity hr
Weather_infor1(:,34)=99;
Weather_infor = Weather_infor1 ; 
end 