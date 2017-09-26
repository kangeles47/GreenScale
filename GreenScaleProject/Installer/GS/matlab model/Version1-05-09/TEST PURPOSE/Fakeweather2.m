%  Make Energy+ run the same fake weather file 
% 1.	Investigate role of radiation.  Set the outside temperature the same with inside temperature. And wind-speed 0. 
% 2.	Investigate role of conduction and convection. Set radiation 0. 
% 3.	Choose one day to test. 
%%****************************************************
% [Weather_infor4,month1,day1,month2,day2] = Weather_fake('Fakeweather',[1,1,1],[12,31,24]); 
% Weather_infor5= Fakeweather2(Weather_infor4);
% dlmwrite('myfile.epw', Weather_infor5,  'precision', 6); 
%%****************************************************
function  Weather_infor = Fakeweather2(Weather_infor1)


%%  ###########################################################
 
% 7 Dry Bulb Temperature {C}
% Weather_infor1(3,7)=3; 
% % 
% for i= 28:33
% Weather_infor1(i,7)=22; 
% end 

%  Weather_infor1(:,7)=3; 

%%  ###########################################################

% 8 Dew Point Temperature  {C}
Weather_infor1(:,8)=99.9;

% 9 Relative Humidity  {%}  effect the radiation 
Weather_infor1(:,9)=999;

% 10 Atmospheric Station Pressure {Pa}
Weather_infor1(:,10)=999999;

% 
% Radiation:
% 11 Extraterrestrial Horizontal  {W/m2}
Weather_infor1(:,11)=9999;

% 12 Extraterrestrial Direct Normal  {W/m2}
Weather_infor1(:,12)=9999;

% 13 Horizontal Infrared Radiation from Sky   {W/m2}
% Weather_infor1(:,13)=9999;
%  Weather_infor1(:,13)=282;
% Weather_infor1(:,13)=0;
Weather_infor1(:,13)=328.6365;

% 14 Global Horizontal   {W/m2}
Weather_infor1(:,14)=9999;


%%  ###########################################################
% 15 Direct Normal       {W/m2}
% Weather_infor1(:,15)=9999;
% Weather_infor1(:,15)=10;
Weather_infor1(:,15)=0;

% 16 Diffuse Horizontal   {W/m2}
%This is the Diffuse Horizontal Radiation in Wh/m2. 
%(Amount of solar radiation in Wh/m2 received from the sky (excluding the solar disk) on a horizontal surface during the number of minutes preceding the time indicated.)
%   Weather_infor1(:,16)=9999;
% Weather_infor1(:,16)=20;
Weather_infor1(:,16)=0;
 
%%  ########################################################### 
  
% Illuminance:
% 17 Global Horizontal   {lux}
Weather_infor1(:,17)=999999;

% 18 Direct Normal       {lux}
Weather_infor1(:,18)=999999;
% 19 Diffuse Horizontal   {lux}
Weather_infor1(:,19)=999999;
% 20 Zenith Luminance     {Cd/m2}  candela per square metre
Weather_infor1(:,20)=9999;


%%  ###########################################################
% Wind:
% 21 Direction   {deg}
% Weather_infor1(:,21)=999;
 Weather_infor1(:,21)=30;

% 22 Speed       {m/s}
% Weather_infor1(:,22)=999;
 Weather_infor1(:,22)=3.1;

%%  ########################################################### 

% Sky cover:
% 23 Total      {.1}
Weather_infor1(:,23)=99;
% 24 Opaque      {.1}
Weather_infor1(:,24)=99;
% 25 Visibilty   {km}
Weather_infor1(:,25)=9999;
% 26 Ceiling Height  {m}
Weather_infor1(:,26)=99999;
% Present weather:
% 27 Observation 
% 28 Codes 
% 
% 29 Precipitation Water mm
Weather_infor1(:,29)=999;
% 30 Aerosol Optical Depth  0.001
Weather_infor1(:,30)=0.999;
% 
% Snow:
% 31 Depth 
Weather_infor1(:,31)=999;
% 32 Days since Last Snowfall 
Weather_infor1(:,32)=99;

% 33 albedo  
Weather_infor1(:,33)=999;
 % 34 Liquid precifpitation depth mm
 Weather_infor1(:,34)=999;
  
% 35 Liquid Precipitation Quantity hr
Weather_infor1(:,35)=99;


 Weather_infor =  Weather_infor1; 
end 