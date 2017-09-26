%****************************************************

% This is the main work place of this code. The aim can be used to calculate the
% thermal energy consumpiton of a building during any certain time. 
%Basic Structure:
% 1. Read building geometry (gbXML file, also containing the materials)
% 2. Read the weather file.  
% 3. Prepare building information for calculation 
% 4. Go to the loop of time integration, space, and surface 

% Updated Date:  May 9th 2013  
%****************************************************

clc;
clear; 

global Infor_surface Infor_cons Infor_space Infor_win ...
       Num_space Num_surface Num_cons Num_win...
       Tem_space Weather_infor...
       i_space i_time... 
       Ground_tem T_outside_temp Wind_speed_temp Wind_speed_dir...
       Alt_sun Az_sun I_df I_dn Space_name T_sky_temp Conversion Tp...
       I_sky_temp  Tp_interior
    

tic; 
%% Store geometry information 
[tree, RootName, DOMnode] = xml_read('Single model.xml');

%% Store the weather data based on the input of location city name and simulation period 

 [Weather_infor,month1,day1,month2,day2] = Weather_read('Washington',[1,1,1],[1,1,4]);   

Ground_tem = 18+273; % Set the default ground temperature as 18C 
T_outside = Weather_infor(:,6)+273;   
Length_weather = length(T_outside); 

Conversion = pi/180;
sigma = 5.67e-8; 
T_sky = (Weather_infor(:,12)/sigma).^0.25; 
I_sky = Weather_infor(:,12); 
Dec = Weather_infor(:,36); 
Alt = Weather_infor(:,37); 
Hour_anlge = Weather_infor(:,35)/Conversion; 
Az = Weather_infor(:,38);  
Num_space=length(tree.Campus.Building.Space); 

disp('Reading geometry and weather takes time:');
toc; 
tic; 

%% Store space information  
Tem_space = zeros(Num_space,1); 

 % set the desired temperature as the same for this moment 
for i = 1:Num_space 
    Tem_space(i,1)=22+273; 
end

 Infor_space = struct2cell(tree.Campus.Building.Space); 
 
 for i = 1:Num_space 
     Infor_space{9,i} = Tem_space(i);
 end 

%% Store surface information 
Num_surface=length(tree.Campus.Surface);
Infor_surface=struct2cell(tree.Campus.Surface); 

%deal with the openning issue for surface infor. When the first surface did not contain window, then the struct of the Infor_surface need to be adjusted. 
% 5 openning 6 CADOjectId 7 Attribute ----------  correct  
% 5 CADOjectId 6 Attribute 7 openning
 
if isempty(Infor_surface{7, 1})   % if there is no openning, then adjust the order 
    for i=1:Num_surface
    temp_surface{1,i}=Infor_surface{7, i};
     Infor_surface{7, i}= Infor_surface{6, i};
      Infor_surface{6, i}= Infor_surface{5, i};
       Infor_surface{5, i}=temp_surface{1,i};
    end    
end 

% Store every time step's temperature of an exterior surface. 
Num_exterior = 0; 
for surface_id = 1 : Num_surface 
if strcmp(Infor_surface{7, surface_id}.surfaceType,'ExteriorWall') ||  strcmp(Infor_surface{7, surface_id}.surfaceType,'Roof') ...
        || strcmp(Infor_surface{7, surface_id}.surfaceType,'RaisedFloor')
  Num_exterior = Num_exterior +1;
  Tp(Num_exterior,1)= surface_id; 
  Tp(Num_exterior,2)= 14.5+273; 
  Tp_interior (Num_exterior,1)=surface_id; 
  Tp_interior (Num_exterior,2)=0;
end 
end 


%% Store the materials of regular surfaces and opennings 
Num_cons = length(tree.Construction);
Infor_cons = struct2cell(tree.Construction); 

Num_win = length(tree.WindowType);
Infor_win = struct2cell(tree.WindowType);

disp('Storing information for space and surface takes time:');
toc; 
 
%% Begin the loop to integrate through time and spaces, and calculate the heat flux for each floor 
% clear tree;
tic; 

Q_space = zeros(1,Num_space); 
Q_hour_W = zeros(Num_space,Length_weather);
Q_hour_J = zeros(Num_space,Length_weather);
Q_total=0; 


for i_space = 1:Num_space    % (assume that the names of spaces are ordered from 1)
 
    Space_name = Infor_space{8, i_space}.id ; 

 for i_time = 1:Length_weather

T_outside_temp = T_outside(i_time);  
Wind_speed_dir =  Weather_infor(i_time,20);
Wind_speed_temp =  Weather_infor(i_time,21);
I_sky_temp =  Weather_infor(i_time,12); 
Alt_sun =  Alt(i_time);
Az_sun = Az (i_time);
T_sky_temp = T_sky(i_time); 
I_dn = Weather_infor(i_time,14) ; 
I_df = Weather_infor(i_time,15) ;
  
if Az_sun < 0 
Az_sun = Az_sun + 2*pi; 
end 

[Q_hour_W(i_space,i_time),G_space] = HeatFlux_space();   %record each hour's heat for each single space in Watts 
Q_hour_J(i_space,i_time) = Q_hour_W(i_space,i_time)*3600; %record each hour's heat in J 
Q_space(i_space) = Q_space(i_space) + Q_hour_J(i_space,i_time) ;  % integrate each space's heat through the whole year time 
G_transmitted_win(i_time) = G_space ; 
 end 

 Q_total = Q_total+Q_space(i_space);   % sum the total heat based on the spaces 

end 
disp('Calculation takes time:');

toc;

Q_total 
Tpp=Tp-273;
Tpp_interior = Tp_interior-273; 
 

plot(Q_hour_W); title('Q_hour_W');
title('Total heat, W'); 
xlabel('Hours');
ylabel('Total_heat');

 