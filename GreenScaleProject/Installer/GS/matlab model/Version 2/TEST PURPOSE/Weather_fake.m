%% This file is to read the weather database(EPW) from Energy Plus 
% By input the name of the country, state, detailed address and the end and
% beging time, we can get a matrix with 34 columns. Each meaning of the
% column refers to comments in this code. 
%  The input format: AA=Weather('USA', 'IL', 'Chicago_OHare.Intl.AP.725300_TMY3.txt',[1,1,1],[1,2,10])

% Begin_t=[month,day,hour];

function [BB,month1,day1,month2,day2]=Weather_fake(City, Begin_t, End_t)

month1=Begin_t(1);
day1=Begin_t(2);
hour1=Begin_t(3);

month2=End_t(1);
day2=End_t(2);
hour2=End_t(3);

DateInError=0;   % 1 true 0 false 
% judge whether the datas are in the right range 
if month1>=1&month1<=12
   % month number is valid 
   if month1~=2
       if day1>EndDayOfMonth(month1)
           DateInError=1;
       end 
   elseif day1>EndDayOfMonth(month1)+1 
       DateInError=1;
   end
else 
    DateInError=1; 
end 

if hour1<1 | hour1>24 
    DateInError=1;
end 

if month2>=1&month2<=12
   % month number is valid 
   if month2~=2
       if day2>EndDayOfMonth(month2)
           DateInError=1;
       end 
   elseif day2>EndDayOfMonth(month2)+1 
       DateInError=1;
   end
else 
    DateInError=1; 
end 

if hour2<1 | hour2>24 
    DateInError=1;
end 

if DateInError 
     disp('Error with input: Invalid Date!');
end 

% use dir to select the weather file that contains the city name 

File =  dir('D:\study and research\summer research\programming\codes\Main code\Main code\Weather'); 
n = length(File); 

% fid=fopen('USA_IL_Chicago_OHare.Intl.AP.725300_TMY3.epw','r');


for i = 3 : n
%     File_names(i) = File(i, 1).name ; 
[City_name ] = regexp(File(i, 1).name, City, 'match');
if strcmp(City_name, City); 
   fid = fopen(strcat('D:\study and research\summer research\programming\codes\Main code\Main code\Weather\',File(i, 1).name));
   break; 
end 

end 
%  [m ] = regexp('USA_IL_Chicago-OHare.Intl.AP.725300_TMY31', 'Chicago', 'match')
% name=strcat(Country,'_',State,'_',City); 
% name='USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.txt';
% to get the latitude , which is the seventh number in the first line of
% the weather file   LOCATION,Minqin,Gansu,CHN,CSWD,526810,38.63,103.08,8.0,1367.5
% [Location,City, State,Country,Data_source, WMO_number, Latitude, longitude,Time_zone,Elevation] = textscan('USA_IL_Chicago_OHare.Intl.AP.725300_TMY3.epw', ...
% '%s%s%s%s%s%f%f%f%f%f', 'delimiter',',',1)

% to get the latitude information 
str=fgetl(fid);
par_cell=regexp(str,',','split');
Lat=str2double(par_cell{1,7});

% fid = fopen(name);  % the weather database of Chicago 



C = textscan(fid, '%f%f%f%f%f%s%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f','delimiter',',','HeaderLines',7);
% the matrix size 8760*35, except that the 6th volume is string format, the
% others are floating values , and using the following loop, we eliminate
% the 6th volume, and get a 8760*34 matrix, with all the meanings
% commented. 

% C={C{1:5},C{7:35}};
% C{6}=999;
for i=1:35
    
for j=1:8760
    if i == 6 
        AA(j,i)=999999; 
    else 
    AA(j,i)=C{i}(j,1);   % getting data from cells 
end 
    end 
end 

 
for j=1:8760
if AA(j,2)==month1&AA(j,3)==day1&AA(j,4)==hour1 
    m1=j; 
end 
if AA(j,2)==month2&AA(j,3)==day2&AA(j,4)==hour2 
    m2=j; 
end 
end 

i=1; 
BB=zeros(m2-m1+1,35);
for k=m1:m2
    BB(i,:)=AA(k,:);
    i=i+1; 
end 

%% to get the declination angle, the altitude angle, azimuth angle (0~2*pi, clockwise)  
w=pi/12; %per hour
Conversion=pi/180; 


% Lat = 38.98*Conversion; 
% for i =1:24:m2-m1+1
%     for k =1:24
%     BB(k-1+i,35)=j;  %days 
%     BB(k-1+i,36)=asin(sin(23.45*Conversion)*sin(360/365*(BB(k-1+i,35)-81)*Conversion)); % store the information of the declination angle of each day. all angles use units of rad
%     BB(k-1+i,37)=asin(sin(BB(k-1+i,36))*sin(Lat)-cos(BB(k-1+i,36))*cos(Lat)*cos(w*k));  % store the altitude angle of each hour 
%     BB(k-1+i,38)=asin(-sin(w*k)*cos(BB(k-1+i,36))/cos( BB(k-1+i,37)));                  % Azimuth angle     
% %     BB(k-1+i,38)=acos();
%     end
%    j=j+1;     
% end

%%more accurate way to calculate the declination angle for each day 
% for i = 1:m2-m1+1
%     
% if BB(i,2) == 1
%     j=BB(i,3); 
% elseif BB(i,2) == 2
%          j=BB(i,3)+31; 
% elseif BB(i,2) == 3
%              j=BB(i,3)+59;
% elseif  BB(i,2) == 4
%                  j=BB(i,3)+90;
% elseif BB(i,2) == 5
%                      j=BB(i,3)+120;
% elseif BB(i,2) == 6
%                              j=BB(i,3)+151;
% elseif BB(i,2) == 7
%                                      j=BB(i,3)+181;
% elseif BB(i,2) == 8
%                                              j=BB(i,3)+212;
% elseif BB(i,2) == 9
%                                                      j=BB(i,3)+243;
% elseif  BB(i,2) == 10
%                                                              j=BB(i,3)+273;
% elseif  BB(i,2) == 11
%                                                                      j=BB(i,3)+304;
% else BB(i,2)== 12
%                                                                      j=BB(i,3)+334;
%                                                                   
%     
% end 
%     
%     BB(i,36)=j;  %days 
%     t = BB(i,4);
%     BB(i,37)=asin(sin(23.45*Conversion)*sin(360/365*(BB(i,35)-81)*Conversion)); % store the information of the declination angle of each day. all angles use units of rad
%     BB(i,38)=asin(sin(BB(i,36))*sin(Lat)-cos(BB(i,36))*cos(Lat)*cos(w*t));  % store the altitude angle of each hour 
% %     BB(i,38)=acos(sin(w*t)*cos(BB(i,36))/cos( BB(i,37)))+pi/2;     % azimuth angle  
%      BB(i,39)=acos((sin(BB(i,36))-sin(BB(i,37))*sin(Lat))/(cos(BB(i,37))*cos(Lat))); 
%   if BB(i,4)>12 
%    BB(i,39)= 2*pi- BB(i,38);
%   end 
% end 

fclose(fid);
end 
 

% v1 WYear
% v2 month1
% v3 day1
% v4 Whour 
% v5 Wminute 
% v6 DryBlub 
% v7 DewPoint
% v8 RelHum
% v9 AtmPress
% v10 ETHoriz
% v11 ETDirect
% v12 IRHoriz
% v13 GLBHoriz
% v14 DirectRad
% v15 DiffuseRad
% v16 GLBHorizIllum
% v17 DirectNrmIllum
% v18 DiffuseHorizIllum
% v19 ZenLum
% v20 WindDir
% v21 WindSpeed
% v22 TotalSkyCover
% v23 OpaqueSkyCover
% v24 Visibility
% v25 CeilHeight
% v26 PresWeathObs
% v27 PresWeathConds
% v28 PrecipWater
% v29 AerosolOptDepth
% v30 SnowDepth
% v31 DaysSinceLastSnow
% v32 Albedo
% v33 LiquidPrecip
% v34 seems the Fortran file only gives 33 terms' meanings except the last
% one 

