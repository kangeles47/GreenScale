clc;
clear; 
[Weather_infor1,month1,day1,month2,day2] = Weather2('Washington',[1,1,1],[1,1,24]); 
 Weather_infor = Fakeweather(Weather_infor1) ;
 
 Dec = Weather_infor(:,36); 
Alt = Weather_infor(:,37); 
% Hour_anlge = Weather_infor(:,35)/Conversion; 
% Alt_d = Alt /Conversion; 
Az = Weather_infor(:,38);
Conversion = pi/180;
Az_surface = 330*Conversion; 
n=length(Dec);
tilt=pi/2; 
I_dn = Weather_infor(:,14);
I_df =  Weather_infor(:,15);


for i=1:n
Az_sun=Az(i); 
az_d = abs(Az_sun - Az_surface); 
Alt_sun = Alt(i);

Incidence(i) = acos(sin(Alt_sun)*cos(tilt)+cos(az_d)*cos(Alt_sun)*sin(tilt));

Iss(i) =I_dn(i)*abs(cos(Incidence(i)))+I_df(i)*(1+cos(tilt))/2;

end 



%  plot(G_transmitted_win(1:24))