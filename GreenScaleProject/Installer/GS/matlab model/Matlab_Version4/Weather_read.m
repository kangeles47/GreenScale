%***********************************

%This function is used for research purpose and do validations  

%***********************************

function [Weather_infor1,month1,day1,month2,day2]=Weather_read(City, Begin_t, End_t,flag)

month1=Begin_t(1);
day1=Begin_t(2);
hour1=Begin_t(3);

month2=End_t(1);
day2=End_t(2);
hour2=End_t(3);

DateInError=0;   % 1 true 0 false 

% judge whether the datas are in the right range 
if month1>=1&&month1<=12
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

if hour1<1 || hour1>24 
    DateInError=1;
end 

if month2>=1&&month2<=12
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

if hour2<1 || hour2>24 
    DateInError=1;
end 

if DateInError 
     disp('Error with input: Invalid Date!');
end 

% use dir to select the weather file that contains the city name 

% File =  dir('D:\study and research\summer research\programming\codes\Main code\Main code\Weather'); 
File =  dir(strcat(pwd,'\Weather')); 
n = length(File); 

for i = 3 : n

[City_name ] = regexp(File(i, 1).name, City, 'match');
if strcmp(City_name, City); 
%    fid = fopen(strcat('D:\study and research\summer research\programming\codes\Main code\Main code\Weather\',File(i, 1).name));
   fid = fopen(strcat(pwd,'\Weather\',File(i, 1).name));
   break; 
end 

end 
% 
% to get the latitude information 
Conversion=pi/180; 
str=fgetl(fid);
par_cell=regexp(str,',','split');
Lat=str2double(par_cell{1,7})*Conversion  ;
Lontitude=str2double(par_cell{1,8}) ;
Time_Meridian = str2double(par_cell{1,9});

C = textscan(fid, '%f%f%f%f%f%s%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f','delimiter',',','HeaderLines',7);
% the matrix size 8760*35, except that the 6th volume is string format, the
% others are floating values , and using the following loop, we eliminate
% the 6th volume, and get a 8760*34 matrix,

C={C{1:5},C{7:35}};
AA=zeros(8760,34);
for i=1:34
for j=1:8760
    AA(j,i)=C{i}(j,1);   % getting data from cells 
end 
end 

 
for j=1:8760
if AA(j,2)==month1&&AA(j,3)==day1&&AA(j,4)==hour1 
    m1=j; 
end 
if AA(j,2)==month2&&AA(j,3)==day2&&AA(j,4)==hour2 
    m2=j; 
end 
end 

i=1; 
Weather_infor=zeros(m2-m1+1,34);
for k=m1:m2
    Weather_infor(i,:)=AA(k,:);
    i=i+1; 
end 

%% To get the declination angle, the altitude angle, azimuth angle (0~2*pi, clockwise)  

for i = 1:m2-m1+1
    
if Weather_infor(i,2) == 1
    j=Weather_infor(i,3); 
elseif Weather_infor(i,2) == 2
         j=Weather_infor(i,3)+31; 
elseif Weather_infor(i,2) == 3
             j=Weather_infor(i,3)+59;
elseif  Weather_infor(i,2) == 4
                 j=Weather_infor(i,3)+90;
elseif Weather_infor(i,2) == 5
                     j=Weather_infor(i,3)+120;
elseif Weather_infor(i,2) == 6
                             j=Weather_infor(i,3)+151;
elseif Weather_infor(i,2) == 7
                                     j=Weather_infor(i,3)+181;
elseif Weather_infor(i,2) == 8
                                             j=Weather_infor(i,3)+212;
elseif Weather_infor(i,2) == 9
                                                     j=Weather_infor(i,3)+243;
elseif  Weather_infor(i,2) == 10
                                                             j=Weather_infor(i,3)+273;
elseif  Weather_infor(i,2) == 11
                                                                     j=Weather_infor(i,3)+304;
else %Weather_infor(i,2)== 12
                                                                     j=Weather_infor(i,3)+334;
                                                                  
    
end

      % to calculate the hour angle.  j is the number of day
      B = 360*(j-81)/364; % degrees 
      B = B*Conversion; 
      ET = 0.165*sin(B)-0.126*cos(B)-0.025*sin(B); 
      Weather_infor(i,35) = Conversion *( 15*(12-(Weather_infor(i,4)+ET))+ Time_Meridian*15-Lontitude);% store the solar hour angle 
      Weather_infor(i,36)=-23.45*cos(2*pi*(j+10)/365)*Conversion; % store the information of the declination angle of each day. all angles use units of rad (-pi/2,pi/2)     
      Weather_infor(i,37)=asin(sin(Weather_infor(i,36))*sin(Lat)+cos(Weather_infor(i,36))*cos(Lat)*cos(Weather_infor(i,35)));  % store the altitude angle of each hour  (-pi/2,pi/2)     
      Weather_infor(i,38)=acos((sin(Weather_infor(i,36))-sin(Weather_infor(i,37))*sin(Lat))/(cos(Weather_infor(i,37))*cos(Lat)));  % azimuth angle   (0, 2pi) from north clockwise direction  
     
  if Weather_infor(i,35)<0  %   the azimuth angle is greater than 180 degrees when the hour angle, h, is positive(negative in this way ...since I am taking hour angle in the opposite way) (afternoon).
   Weather_infor(i,38)= 2*pi- Weather_infor(i,38);
  end 
end 

fclose(fid);

if flag == 1 || day2==day1 
    %% 1. Every one hour every day
    Weather_infor1 = Weather_infor;
    
else
    %% 2. Every one hour every other day (This can save half time)
 
    m=1;
    for n_day=1:2:(day2-day1+1)
        n_day1=(n_day-1)*24+1;
        for n_hour_o=1:24
            n_hour=1+(n_hour_o-1)*1;
            for j=1:38
                Weather_infor1(24*(m-1)+1+n_hour-1,j) = Weather_infor(n_day1+n_hour-1,j);
            end
        end
        m=m+1;
    end
 
end

end 
