 %****************************************************

% This is the main work place of this code. The aim can be used to calculate the
% thermal energy consumpiton of a building during any certain time.
%Basic Structure:
% 1. Read building geometry and construction materials from gbXML file
% 2. Read the weather file.
% 3. Prepare building information for calculation
% 4. Go to the loop of time integration with each space and then each surface

% Updated Date:  Sep 16th 2013
%****************************************************

% Updated Date: 02-13-2014
% 1. Surface area is modified and calculated based on coordinates instead of width and
% height.
% 2. Terrain type modified: the wind speed and the convection coefficients of all exterior
% surfaces, including exterior wall, roof, raised floor, ceiling, and
% interior floor typr but with the same adjacent spaces, are dependent on
% the terrain type of the ground. 
%( terrain type decides the coefficients to calculate the wind speed
%1= flat, open country 
%2= rough, wooded country 
%3= towns and cites 
%4= ocean 
%5= urban, industrial, forest )
% The values of terrain_cof.sigma and terrain_cof.a can be refered from the
% 55th lin in SimplifiedGeometryData_fn6.m 

% This Terrain type will influence the calculation of the
% wind_speed_corrected 
% example: 
% Wind_speed_corrected = Wind_speed_temp *(270/10)^0.14*(h_surface/Terrain_cof.sigma).^Terrain_cof.a;
% hc_external= D+E*Wind_speed_corrected+F*Wind_speed_corrected^2;
%
% Updated Date: 06-03-2014
% add heat calculation of wall surface with ceiling type
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 1. a bit assumption: all the surfaces and spaces are in ordered number in
%    the gbXML file
% 2. In the current version, people and electric equipment schedule are not
%    considered yet
% 3. Desired temperature can be set; Simulation period and location can be chosen
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


clc;
clear;
%
% global Infor_surface Infor_cons Infor_win ...
%     Num_space Num_surface Num_cons Num_win...
%     Tem_space Weather_infor...
%     i_space i_time G_space_record...
%     T_outside_temp Wind_speed_temp...
%     Alt_sun Az_sun I_df I_dn Space_name Tp...
%     Tp_interior Coef

tic;
Coef =1;   % to adjust the thermal capacitance value. A better option is 0.45
Desired_temp = 22;
ShadowModuleFlag=0; %use 1 to include shading calculation
flag =1;  % use 1 for hourly , and 0 for every hour every other day

% Terrain type
Terrain_type =1;  % terrain type decides the coefficients to calculate the wind speed
%1= flat, open country 
%2= rough, wooded country 
%3= towns and cites 
%4= ocean 
%5= urban, industrial, forest 

%% Store geometry information
% tree = xml_read('Single model.xml');
% tree = xml_read('Two Room One Floor.xml');
% tree = xml_read('Four Room Two Floors.xml');
% tree = xml_read('Project1_withrooms.xml');
% tree = xml_read('Single_Room_225.xml');
% tree = xml_read('4Roomtest_0.xml');
% tree = xml_read('4_Room_45.xml');
% tree = xml_read('4_Room_180.xml');
tree = xml_read('4_Room_225.xml');

Num_space = length(tree.Campus.Building.Space);
Num_surface=length(tree.Campus.Surface);
Tem_space=zeros(1,Num_space);
for i = 1:Num_space
    Tem_space(i,1)=Desired_temp+273;
end
% [Infor_space_simp, Infor_surface_simp, Infor_cons_simp, Infor_win_simp]=SimplifiedGeometryData_fn3(tree,Tem_space);
[Infor_space_simp, Infor_surface_simp, Infor_cons_simp, Infor_win_simp,Terrain_cof]=SimplifiedGeometryData_fn6(tree,Coef,Tem_space,Terrain_type);

%% Store the weather data based on the input of location city name and simulation period

[Weather_infor,month1,day1,month2,day2] = Weather_read('Washington',[1,1,1],[12,31,24],flag);
%  flag ==1 hourly
%  flag ==0 every hour every other day
T_outside = Weather_infor(:,6)+273;
Alt = Weather_infor(:,37);
Az = Weather_infor(:,38);
Length_weather = length(T_outside);

disp('Reading geometry and weather takes time:');
toc;
tic;

%% Store space information
% Tem_space = zeros(Num_space,1);
% G_space_record = zeros(Num_space,Length_weather+1); % per surface area

% set the desired temperature as the same for this moment


% Infor_space = struct2cell(tree.Campus.Building.Space);
%
% for i = 1:Num_space
%     Infor_space{9,i} = Tem_space(i);
%     Infor_space{10,i} = getHeight_space_floor(i);   % Store the height for each space's height
% end

%% Store surface information

% Infor_surface=struct2cell(tree.Campus.Surface);

%% Store the materials of regular surfaces and opennings
% Num_cons = length(tree.Construction);
% Infor_cons = struct2cell(tree.Construction);
%
% Num_win = length(tree.WindowType);
% Infor_win = struct2cell(tree.WindowType);

% Calculate the C value for each surface. C = density * specific heat * thickness
% for i =1:Num_cons
% C=0;
%     for i_layer =1:Num_cons
%     if strcmp( Infor_cons{5, i}.ATTRIBUTE.layerIdRef, tree.Layer(i_layer, 1).ATTRIBUTE.id)
%        for j=1:length(tree.Layer(i_layer, 1).MaterialId)
%         for  k =1:length(tree.Material)
%             if strcmp(tree.Layer(i_layer, 1).MaterialId(j, 1).ATTRIBUTE.materialIdRef, tree.Material(k, 1).ATTRIBUTE.id)
%                 C0 = (tree.Material(k, 1).Thickness.CONTENT * tree.Material(k, 1).Density.CONTENT* tree.Material(k, 1).SpecificHeat.CONTENT);
%                C = C+C0;
%                 C0=0;
%                break;
%             end
%
%         end
%        end
%     end
%     end
%   Infor_cons{8, i}  = C;
% end

%deal with the openning issue for surface infor. When the first surface did not contain window, then the struct of the Infor_surface need to be adjusted.
% 5 openning 6 CADOjectId 7 Attribute ----------  correct
% 5 CADOjectId 6 Attribute 7 openningif isempty(Infor_surface{7, 1})   % if there is no openning, then adjust the order
% if isempty(Infor_surface{7, 1})
%     for i=1:Num_surface
%       temp_surface{1,i}=Infor_surface{7, i};
%       Infor_surface{7, i}= Infor_surface{6, i};
%       Infor_surface{6, i}= Infor_surface{5, i};
%        Infor_surface{5, i}=temp_surface{1,i};
%
%     end
% end
%
% for  i=1:Num_surface
%         Infor_surface{8, i}= Infor_surface{3,i}.Height*Infor_surface{3,i}.Width*0.3048*0.3048;  % store the total surface area
%         Infor_surface{9, i}=  getA_surface_noOpenning(i); % store the surface_area_no_openning for each surface
%         Infor_surface{10, i}= getC_surface(i);            % store the Cp for each surface
%         Infor_surface{11, i} = getU_surface_e(i);         % store the U_e for each surface
%         Infor_surface{12, i} = 0 ;                        %
%         Infor_surface{13, i} = getHeight_surface(i);     % store the height of the surface so as to calculate the convection coefficient
%         Infor_surface{14, i} = getA_surface_noWindow(i); % A_noWin is used for the Is incident on the exteiror surfaces
% end


%% Store every time step's temperature of each surface.
G_space_record = zeros(Num_space,Length_weather+1);
Tp=zeros(Num_surface,Length_weather+3);
Tp_interior=zeros(Num_surface,Length_weather+3);
for surface_id = 1 : Num_surface
    Tp(surface_id,1) = surface_id;    %% Tp(surface_id,2) and Tp_interior(surface_id,2) store the space names
    Tp(surface_id,3) = Desired_temp + 273;  %% Tp(surface_id,3) and Tp_interior(surface_id,3) initialize the surface temperaure
    Tp_interior (surface_id,1) = surface_id;
    Tp_interior (surface_id,3) = Desired_temp + 273;
end

disp('Storing information for space and surface takes time:');
toc;

%% Begin the loop to integrate with time and spaces, and calculate the heat flux for each floor
% clear tree;
tic;

Q_space = zeros(Num_space,1);
Q_hour_W = zeros(Num_space,Length_weather);

for i_time = 1:Length_weather
    for i_space = 1:Num_space    % (assume that the names of spaces are ordered from 1 consistently)
        Space_name =  Infor_space_simp(1, i_space).Name;
        
        T_outside_temp = T_outside(i_time);
        Wind_speed_temp =  Weather_infor(i_time,21);
        Alt_sun =  Alt(i_time);
        Az_sun = Az(i_time);
        I_dn = Weather_infor(i_time,14) ;
        I_df = Weather_infor(i_time,15) ;
        
        if Az_sun < 0
            Az_sun = Az_sun + 2*pi;
        end
        
        [Q_hour_W(i_space,i_time),Tp,Tp_interior,G_space_record] = HeatFlux_space(Infor_surface_simp, i_space, Infor_space_simp, G_space_record, i_time,Tp,Tp_interior,T_outside_temp,Wind_speed_temp,Az_sun,Alt_sun,I_dn,I_df,Terrain_cof,ShadowModuleFlag);   %record each hour's heat for each single space in Watts
        %disp([' ', num2str(Q_hour_W(i_space,i_time))])
    end
end

Q_total=0;

for i_space = 1:Num_space
    Q_space(i_space,1) = sum(Q_hour_W(i_space,:));
    Q_total = Q_total+Q_space(i_space,1);   % sum the total heat based on the spaces
end


%% 1. One hour time step

if flag ==0
%% 2. Every one hour every other day (This can save half time)
    if mod(Length_weather/24,2)==0
        Q_total=2*Q_total;
    else
        Q_total = Q_total*(2*Length_weather/24-1)/(Length_weather/24);
    end
end
Total_Q = Q_total/1000;  % transform K to KW.h 

%% to reorganize the monthly loads 
 Q_hour_total=zeros(1,8760);
for i=1:8760
 Q_hour_total(i) =sum(Q_hour_W(:,i));
end

Q_month=zeros(12,1);
 Q_month(1)=sum(Q_hour_total(1:31*24));
  Q_month(2)=sum(Q_hour_total(745:744+672));
   Q_month(3)=sum(Q_hour_total(744+672+1:744+672+744));
    Q_month(4)=sum(Q_hour_total(744+672+744+1:744+672+744+720));
     Q_month(5)=sum(Q_hour_total(744+672+744+720+1:744+672+744+720+744));
      Q_month(6)=sum(Q_hour_total(744+672+744+720+744+1:744+672+744+720+744+720));
       Q_month(7)=sum(Q_hour_total(744+672+744+720+744+720+1:744+672+744+720+744+720+744));
        Q_month(8)=sum(Q_hour_total(744+672+744+720+744+720+744+1:744+672+744+720+744+720+744+744));
         Q_month(9)=sum(Q_hour_total(744+672+744+720+744+720+744+744+1:744+672+744+720+744+720+744+744+720));
          Q_month(10)=sum(Q_hour_total(744+672+744+720+744+720+744+744+720+1:744+672+744+720+744+720+744+744+720+744));
           Q_month(11)=sum(Q_hour_total(744+672+744+720+744+720+744+744+720+744+1:744+672+744+720+744+720+744+744+720+744+720));
            Q_month(12)=sum(Q_hour_total(744+672+744+720+744+720+744+744+720+744+720+1:744+672+744+720+744+720+744+744+720+744+720+744));
            
Q_month

            bar1=bar([1:1:12],Q_month/1000,'BarWidth',0.4);
labelID = ['Jan';'Feb'; 'Mar'; 'Apr'; 'May';'Jun';'Jul';'Aug';'Sep';'Oct';'Nov';'Dec']; 
 set(gca,'XTick',1:1:12);set(gca,'XTickLabel',labelID,'FontSize',11)
 xlabel('Month','FontSize',11);
ylabel('Monthly thermal loads (kW \cdot h)','FontSize',11);
 
disp('Calculation takes time:');

toc;

disp(['Annual total thermal load is ', num2str(Total_Q, '%5.2f'), ' kW.h'])
