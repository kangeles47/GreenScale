 %****************************************************

% This is the main work place of this code. The aim can be used to calculate the
% thermal energy consumpiton of a building during any certain time. 
%Basic Structure:
% 1. Read building geometry (gbXML file, also containing the materials)
% 2. Read the weather file.  
% 3. Prepare building information for calculation 
% 4. Go to the loop of time integration, space, and surface 

% Updated Date:  June 25th 2013  
%****************************************************

%%%%%%%%%%%%%%%%%%%%%%%%%%%5
% a bid assumption: all the surfaces and spaces are in ordered number.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clc;
clear; 

global Infor_surface Infor_cons Infor_space Infor_win ...
       Num_space Num_surface Num_cons Num_win...
       Tem_space Weather_infor...
       i_space i_time... 
       Ground_tem T_outside_temp Wind_speed_temp Wind_speed_dir...
       Alt_sun Az_sun I_df I_dn Space_name T_sky_temp Conversion Tp...
       I_sky_temp  Tp_interior Coef IS_record Solar_win Incidence_angle

tic; 
Coef =1; 
%% Store geometry information 
[tree, RootName, DOMnode] = xml_read('Two Room One Floor.xml');   % Four Room Two Floors  Two Room One Floor

%% Store the weather data based on the input of location city name and simulation period 

 [Weather_infor1,month1,day1,month2,day2] = Weather_read('Washington',[1,1,1],[12,31,24]); 
 Weather_infor = Fakeweather(Weather_infor1) ;   % Fakeweather.m is used for validation    

Ground_tem = 18+273; % Set the default ground temperature as 18 C 
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
     Infor_space{10,i} = getHeight_space_floor(i);   % Store the height for each space's height 
 end 

%% Store surface information 
Num_surface=length(tree.Campus.Surface);
Infor_surface=struct2cell(tree.Campus.Surface); 

%% Store the materials of regular surfaces and opennings 
Num_cons = length(tree.Construction);
Infor_cons = struct2cell(tree.Construction); 

Num_win = length(tree.WindowType);
Infor_win = struct2cell(tree.WindowType);

% Calculate the C value for each surface. C = density * specific heat * thickness 
for i =1:Num_cons 
C=0; 
    for i_layer =1:Num_cons
    if strcmp( Infor_cons{5, i}.ATTRIBUTE.layerIdRef, tree.Layer(i_layer, 1).ATTRIBUTE.id)       
       for j=1:length(tree.Layer(i_layer, 1).MaterialId)
        for  k =1:length(tree.Material)
            if strcmp(tree.Layer(i_layer, 1).MaterialId(j, 1).ATTRIBUTE.materialIdRef, tree.Material(k, 1).ATTRIBUTE.id)
                C0 = (tree.Material(k, 1).Thickness.CONTENT * tree.Material(k, 1).Density.CONTENT* tree.Material(k, 1).SpecificHeat.CONTENT);     
               C = C+C0; 
                C0=0; 
               break;
            end 

        end       
       end 
    end 
    end  
  Infor_cons{8, i}  = C; 
end

%deal with the openning issue for surface infor. When the first surface did not contain window, then the struct of the Infor_surface need to be adjusted. 
% 5 openning 6 CADOjectId 7 Attribute ----------  correct  
% 5 CADOjectId 6 Attribute 7 openningif isempty(Infor_surface{7, 1})   % if there is no openning, then adjust the order
if isempty(Infor_surface{7, 1}) 
    for i=1:Num_surface
      temp_surface{1,i}=Infor_surface{7, i};
      Infor_surface{7, i}= Infor_surface{6, i};
      Infor_surface{6, i}= Infor_surface{5, i};
       Infor_surface{5, i}=temp_surface{1,i};
       
    end    
end 

for  i=1:Num_surface
        Infor_surface{8, i}= Infor_surface{3,i}.Height*Infor_surface{3,i}.Width*0.3048*0.3048;  % store the total surface area 
        Infor_surface{9, i}=  getA_surface_noOpenning(i); % store the surface_area_no_openning for each surface  
        Infor_surface{10, i}= getC_surface(i);            % store the Cp for each surface 
        Infor_surface{11, i} = getU_surface_e(i);         % store the U_e for each surface 
        Infor_surface{12, i} = 0 ;  %   
        Infor_surface{13, i} = getHeight_surface(i);     % store the height of the surface so as to calculate the convection coefficient 
        Infor_surface{14, i} = getA_surface_noWindow(i); % A_noWin is used for the Is incident on the exteiror surfaces  
end 

%% Store every time step's temperature of each surface. 
 
for surface_id = 1 : Num_surface 
  Tp(surface_id,1) = surface_id;    %% Tp(surface_id,2) and Tp_interior(surface_id,2) store the space names 
  Tp(surface_id,3) = 20+273; 
  Tp_interior (surface_id,1) = surface_id; 
  Tp_interior (surface_id,3) = 20+273; 
  IS_record(surface_id,1) = surface_id;   
  Solar_win(surface_id,1) = surface_id;
  Incidence_angle(surface_id,1) = surface_id;
end 



disp('Storing information for space and surface takes time:');
% toc; 
 
%% Begin the loop to integrate with time and spaces, and calculate the heat flux for each floor 
clear tree;
% tic; 

Q_space = zeros(1,Num_space); 
Q_hour_W = zeros(Num_space,Length_weather);
Q_hour_J = zeros(Num_space,Length_weather);
Q_total=0; 

for i_space = 1:Num_space    % (assume that the names of spaces are ordered from 1 consistently)
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

Q_total/3600
Tpp=Tp-273;
Tpp_interior = Tp_interior-273; 
 

% % plot(Q_hour_W); title('Q_hour_W');
% % title('Total heat, W'); 
% % xlabel('Hours');
% % ylabel('Total_heat');
% % 
% % n=1:24; n=n'; 

% figure(2)
%  
% % plot(n,Tpp(1,3:26),'r',n,Tpp(2,3:26),'b-o',n,Tpp(3,3:26),'g',n,Tpp(4,3:26),'y',n,Tpp(5,3:26),'k',n,T_outside-273,'r-*')
% plot(n,Tpp(1,27:50),'r',n,Tpp(2,27:50),'b-o',n,Tpp(3,27:50),'g',n,Tpp(4,27:50),'y',n,Tpp(5,27:50),'k',n,T_outside(25:48)-273,'r-*')
% title('exterior temperature')
 