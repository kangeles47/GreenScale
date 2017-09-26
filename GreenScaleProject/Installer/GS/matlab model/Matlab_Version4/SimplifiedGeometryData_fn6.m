function [Infor_space_simp, Infor_surface_simp, Infor_cons_simp, Infor_win_simp,Terrain_cof]=SimplifiedGeometryData_fn6(tree,Coef,Tem_space,Terrain_type)

%Use this to simplify geometry detail
%Modify from SimplifiedGeometryData_fn3
%Date: 10/10/2013
%Corrected error about space-surface relation
%Add floor id of each space
%Add Coef to adjust the thermal capacitance value


%Modifying date: 02/12/2014 
% Modifying the method of calculating surface area based on coordinates
% instead of width and height. 

%Input: tree == variable of information of geometry obtained from XML file by xml_read function

%Output: Infor_space_simp, Infor_surface_simp, Infor_cons_simp, Infor_win_simp

%Short codes for identifying surface type
%Exterior: 0 == Interior
%          1 == Exterior
%          2 == Shading
%Class:    1 == Wall
%          2 == Floor
%          3 == Roof
%          4 == Shading
%Surface type named with number value
%          1 == ExteriorWall
%          2 == Roof
%          3 == InteriorWall
%          4 == UndergroundWall
%          5 == InteriorFloor
%          6 == RaisedFloor
%          7 == UndergroundSlab
%          8 == SlabOnGrade

%Short codes for identifying opening type
%WinDoor:    1 == Window
%            2 == Door


%Terrain type decides the coefficient to calculate the wind speed
%1= flat, open country
%2= rough, wooded country
%3= towns and cites
%4= ocean
%5= urban, industrial, forest

%% Sample input
% clear all
% [tree, RootName, DOMnode] = xml_read('Four Room Two Floors.xml');
% load('tree_4R2F.mat');

%% decide terrain type
if Terrain_type==1
    sigma=270;
    a=0.14;
elseif Terrain_type==2
    sigma=370;
    a=0.22;
elseif Terrain_type==3
    sigma=460;
    a=0.33;
elseif Terrain_type==4
    sigma=210;
    a=0.10;
elseif Terrain_type==5
    sigma=370;
    a=0.22;
end
Terrain_cof=struct('sigma',0,...
    'a',0);
Terrain_cof.sigma=sigma;
Terrain_cof.a=a;
%% Store space information
Num_space = length(tree.Campus.Building.Space);
% Infor_space = struct2cell(tree.Campus.Building.Space);

% Comfirm the length's unit to make sure the output from this file are all
% in meter
if strcmp(tree.ATTRIBUTE.lengthUnit ,'Feet')
    A=0.3048;
else
    strcmp(tree.ATTRIBUTE.lengthUnit ,'Meter')
    A=1;
end
AA=A^2;
%Pre-allocate data
clear Infor_space_simp
Infor_space_simp(1:Num_space)=struct('Name', [], ...
    'FloorCoordinate', zeros(4,3), ...
    'FloorSurfaceId', 0, ...
    'FloorHeight', 0, ...
    'Area', 0, ...
    'Volume', 0, ...
    'RelatedSurface', zeros(1,6), ...
    'ExteriorSurface',zeros(1,10),...
    'NonExterior',zeros(1,10),...
    'NeighborSpace', [],...
    'SpaceTemp',0);

%Assign space info
for i_space=1:Num_space
    %Get space name
    Infor_space_simp(i_space).Name=tree.Campus.Building.Space(i_space,1).Name;
    
    %Get coordinate of floor surface
    %np == number of points of coordinates of surface
    [np,temp]=size(tree.Campus.Building.Space(i_space,1).PlanarGeometry.PolyLoop.CartesianPoint); %#ok<*NASGU>
    for i_coor=1:np
        Infor_space_simp(i_space).FloorCoordinate(i_coor,:)=cell2mat(tree.Campus.Building.Space(i_space,1).PlanarGeometry.PolyLoop.CartesianPoint(i_coor,:).Coordinate)*A;
    end
    %Get Area
    Infor_space_simp(i_space).Area=tree.Campus.Building.Space(i_space,1).Area*AA;
    
    %Get Volume
    Infor_space_simp(i_space).Volume=tree.Campus.Building.Space(i_space,1).Volume*A^3;
    
    %Post processing
    %Get related surface id
    n_surface=length(tree.Campus.Building.Space(i_space,1).SpaceBoundary);
    RelatedSurface=zeros(1,n_surface);
    for i_surface=1:n_surface
        surfaceIdRef=tree.Campus.Building.Space(i_space,1).SpaceBoundary(i_surface,1).ATTRIBUTE.surfaceIdRef;
        surfaceIdRef_id=regexp(surfaceIdRef,'-','split');
        RelatedSurface(i_surface)=str2double(surfaceIdRef_id(end));
    end
    
    Infor_space_simp(i_space).RelatedSurface=RelatedSurface;
    
%     % Get each space's exterior surface list 
%     k=1;
%     for i_surface=1:length(RelatedSurface)
%     
%               if Infor_surface_simp(1, i_surface).Type==1 ...         %ExteriorWall
%                 || Infor_surface_simp(1, i_surface).Type==2 ... %Roof
%                 || Infor_surface_simp(1, i_surface).Type==6     %RaisedFloor
%              k=k+1;     
%             ExteriorSurface(i_space,k)=i_surface;         
%               end
%     end 
%      ExteriorSurface(ExteriorSurface==0)=[];
%      
    %Get floor height
    FloorHeight=(max(Infor_space_simp(i_space).FloorCoordinate(:,3))+min(Infor_space_simp(i_space).FloorCoordinate(:,3)))/2;
    Infor_space_simp(i_space).FloorHeight=FloorHeight;
end

%Post processing
%Get neighboring space id
Nsum_NeighborSpace=zeros(1,Num_space);


for i_space=1:Num_space
    ii=0;
    for j_space=1:Num_space
        if (i_space ~= j_space) && ~isempty(intersect(Infor_space_simp(i_space).RelatedSurface,Infor_space_simp(j_space).RelatedSurface))
            %Share the same surface
            ii=ii+1; % NeighborSpace(ii)=j_space;
        end
    end
    
    Nsum_NeighborSpace(i_space)=ii;
    %     NeighborSpace_infor=[];
    %
    %
    %     Infor_space_simp(i_space).NeighborSpace.space=NeighborSpace_infor; % in this term, the first value will be the neighbour space ID and the left are the sharing surfaces, which is more than 1 for some special cases
    Infor_space_simp(i_space).SpaceTemp=Tem_space(i_space);
end


 
for i_space=1:Num_space
    ii=0;
    N_NeighborSpace=Nsum_NeighborSpace(i_space);
    Infor_space_simp(i_space).('NeighborSpace')=struct('NeighborSpaceID', [], ...
        'NeighborSurfacesID', []);
    Infor_space_simp(i_space).NeighborSpace(1:N_NeighborSpace)=struct('NeighborSpaceID', 0, ...
        'NeighborSurfacesID',zeros(1,6));
    for j_space=1:Num_space
        if (i_space ~= j_space) && ~isempty(intersect(Infor_space_simp(i_space).RelatedSurface,Infor_space_simp(j_space).RelatedSurface))
            %Share the same surface
            ii=ii+1; % NeighborSpace(ii)=j_space;
            Infor_space_simp(i_space).NeighborSpace(ii).NeighborSpaceID=j_space;  %#ok<AGROW>
            Infor_space_simp(i_space).NeighborSpace(ii).NeighborSurfacesID=intersect(Infor_space_simp(i_space).RelatedSurface,Infor_space_simp(j_space).RelatedSurface); %Shared_surface
            %             NeighborSpace_infor=[j_space NeighborSurfaces];
        end
    end
    
end


%% Store the materials of regular surfaces
Num_cons = length(tree.Construction);
% Infor_cons = struct2cell(tree.Construction);

%Pre-allocate data
clear Infor_cons_simp
Infor_cons_simp(1:Num_cons)=struct('Name', [], ...
    'U', 0, ...
    'C', 0, ...
    'Absorptance', 0, ...
    'Roughness', [], ...
    'LayerId', [], ...
    'id', []);

%Assign construction info
for i_cons=1:Num_cons
    %Get construction name
    Infor_cons_simp(i_cons).Name=tree.Construction(i_cons,1).Name;
    
    %Get U [W/m^2.K]
    Infor_cons_simp(i_cons).U=tree.Construction(i_cons,1).U_DASH_value.CONTENT;
    
    %Get absorbtance
    if ~isempty(tree.Construction(i_cons, 1).Absorptance)
        Infor_cons_simp(i_cons).Absorptance=tree.Construction(i_cons, 1).Absorptance.CONTENT;
    end
    
    %Roughness
    if ~isempty(tree.Construction(i_cons, 1).Roughness)
        Infor_cons_simp(i_cons).Roughness=tree.Construction(i_cons, 1).Roughness.ATTRIBUTE.value;
    end
    
    %LayerId
    Infor_cons_simp(i_cons).LayerId=tree.Construction(i_cons, 1).LayerId.ATTRIBUTE.layerIdRef;
    
    %Id
    Infor_cons_simp(i_cons).id=tree.Construction(i_cons, 1).ATTRIBUTE.id;
    
    %Post processing
    % Calculate the C value for each surface. C = density * specific heat * thickness
    for i_layer =1:length(tree.Layer)
        %Matching construction with layer
        if strcmp(Infor_cons_simp(i_cons).LayerId, tree.Layer(i_layer, 1).ATTRIBUTE.id)
            %Matched layer
            Num_mat_layer=length(tree.Layer(i_cons, 1).MaterialId); %Number of layers
            C_layer=zeros(1,Num_mat_layer);
            %Calculate for C of each layer
            for i_mat_layer=1:Num_mat_layer
                for i_mat =1:length(tree.Material)
                    %Matching material of each layer with material list
                    if strcmp(tree.Layer(i_cons, 1).MaterialId(i_mat_layer, 1).ATTRIBUTE.materialIdRef, tree.Material(i_mat, 1).ATTRIBUTE.id)
                        %Matched material
                        C_layer(i_mat_layer) = (tree.Material(i_mat, 1).Density.CONTENT* tree.Material(i_mat, 1).SpecificHeat.CONTENT * tree.Material(i_mat, 1).Thickness.CONTENT);
                        break;
                    end
                end
            end
            break;
        end
    end
    Infor_cons_simp(i_cons).C=sum(C_layer); %[J/m^2.K]
    
    
end


%% Store the materials of windows
if isfield(tree,'WindowType')
    Num_win = length(tree.WindowType);
else
    Num_win = 0;
end
% Infor_win = struct2cell(tree.WindowType);

%Pre-allocate data
clear Infor_win_simp
Infor_win_simp(1:Num_win)=struct('Name', [], ...
    'U', 0, ...
    'SHGC', zeros(2,7), ...
    'Transmittance', 0, ...
    'id', []);

%Assign construction for window info
for i_win=1:Num_win
    %Name
    Infor_win_simp(i_win).Name=tree.WindowType(i_win,1).Name;
    
    %U
    Infor_win_simp(i_win).U=tree.WindowType(i_win,1).U_DASH_value.CONTENT; %[W/m^2.K]
    
    %SHGC
    Num_SHGC=length(tree.WindowType(i_win,1).SolarHeatGainCoeff);
    %Row 1 == Value
    Infor_win_simp(i_win).SHGC(1,:)=[tree.WindowType(i_win,1).SolarHeatGainCoeff(1:end-1, 1).CONTENT, 0];
    %Row 2 == Incident angle [degree]
    for i_SHGC=1:Num_SHGC-1
        Infor_win_simp(i_win).SHGC(2,i_SHGC)=[tree.WindowType(i_win,1).SolarHeatGainCoeff(i_SHGC, 1).ATTRIBUTE.solarIncidentAngle];        
    end
    Infor_win_simp(i_win).SHGC(2,7)=90;
    
    %Transmittance
    Infor_win_simp(i_win).Transmittance=tree.WindowType(i_win,1).Transmittance.CONTENT;
    
    %id
    Infor_win_simp(i_win).id=tree.WindowType(i_win,1).ATTRIBUTE.id;
end

%% Store surface information
Num_surface=length(tree.Campus.Surface);
% Infor_surface=struct2cell(tree.Campus.Surface);

%Pre-allocate data
clear Infor_surface_simp
Infor_surface_simp(1:Num_surface)=struct('Name', [], ...
    'Coordinate',zeros(4,3), ...
    'Azimuth',0, ...
    'Tilt',0, ...
    'Height',0, ...
    'Width',0, ...
    'Area',0, ...
    'Area_noOpen', 0, ...
    'Area_noDoor', 0, ...
    'SurfaceHeight', 0, ... % the height of a surface refering to the ground
    'FloorOfSpace', 0, ... %If this is floor, identify what space related to
    'Type', int8(0), ...
    'TypeName', [], ...
    'ConsId', [], ...
    'U', 0, ...
    'U_ave', 0, ...
    'C', 0, ...
    'C_ave', 0, ...
    'Absorptance', 0, ...
    'Roughness', [], ...
    'Exterior', int8(0), ...
    'Class', int8(0), ...
    'RelatedSpace', [], ...
    'NeighborSurface', [], ...
    'N_open', 0, ...
    'N_door',0, ...
    'N_win',0,...
    'Opening', [],...
    'RoughnessCof',zeros(1,3),...
    'WindowSurface',0,...
    'DoorSurface',0);

% Assign surface infor
for i_surface=1:Num_surface
    
    
    %Get surface name
    Surf_name=tree.Campus.Surface(i_surface,1).Name;
    Infor_surface_simp(i_surface).Name=Surf_name;
    
    %Get coordinate of each surface
    %np == number of points of coordinates of surface
    [np,temp]=size(tree.Campus.Surface(i_surface,1).PlanarGeometry.PolyLoop.CartesianPoint); %#ok<*NASGU>
    for i_coor=1:np
        Infor_surface_simp(i_surface).Coordinate(i_coor,:)=cell2mat(tree.Campus.Surface(i_surface,1).PlanarGeometry.PolyLoop.CartesianPoint(i_coor,:).Coordinate)*A;
    end
    
    % Get azimuth and tilt angle
    Infor_surface_simp(i_surface).Azimuth=tree.Campus.Surface(i_surface,1).RectangularGeometry.Azimuth;  % [degree]
    Infor_surface_simp(i_surface).Tilt=tree.Campus.Surface(i_surface,1).RectangularGeometry.Tilt;  % [degree]
    
    % Get Height and Width
    Infor_surface_simp(i_surface).Height=tree.Campus.Surface(i_surface,1).RectangularGeometry.Height*A; %[m]
    Infor_surface_simp(i_surface).Width=tree.Campus.Surface(i_surface,1).RectangularGeometry.Width*A; %[m]
    
    
    
    %     Infor_surface_simp(i_surface).SurfaceHeight = getHeight_surface(i_surface);
    %Get type
    % ExteriorWall 1, Roof 2, InteriorWall 3, UndergroundWall 4,
    % InteriorFloor 5, RaisedFloor 6, UndergroundSlab 7, SlabOnGrade,8
    Type=tree.Campus.Surface(i_surface,1).ATTRIBUTE.surfaceType;
    Infor_surface_simp(i_surface).TypeName=Type;
    if strcmp(Type,'ExteriorWall')
        Infor_surface_simp(i_surface).Type=int8(1);
    elseif strcmp(Type,'Roof')
        Infor_surface_simp(i_surface).Type=int8(2);
    elseif strcmp(Type,'InteriorWall')
        Infor_surface_simp(i_surface).Type=int8(3);
    elseif strcmp(Type,'UndergroundWall')
        Infor_surface_simp(i_surface).Type=int8(4);
    elseif strcmp(Type,'InteriorFloor')
        Infor_surface_simp(i_surface).Type=int8(5);
    elseif strcmp(Type,'RaisedFloor')
        Infor_surface_simp(i_surface).Type=int8(6);
    elseif strcmp(Type,'UndergroundSlab')
        Infor_surface_simp(i_surface).Type=int8(7);
    elseif strcmp(Type,'SlabOnGrade')
        Infor_surface_simp(i_surface).Type=int8(8);
    end
    % Post-process values
    %Get Area 
    %% Modifying: calculate the surface area for any shape of surface based on coordinates 
    % Infor_surface_simp(i_surface).Area=Infor_surface_simp(i_surface).Height*Infor_surface_simp(i_surface).Width; %[sq. m]
    
   Infor_surface_simp(i_surface).Area=GetSurfaceArea(Infor_surface_simp(i_surface).Coordinate,Infor_surface_simp(i_surface).Azimuth,Infor_surface_simp(i_surface).Tilt);
    %SurfaceHeight (Z value at middle of surface)
    Infor_surface_simp(i_surface).SurfaceHeight=(max(Infor_surface_simp(i_surface).Coordinate(:,3))+min(Infor_surface_simp(i_surface).Coordinate(:,3)))/2; %[m]
    
    %Identify detail type of surface
    Surf_name_id=regexp(Surf_name,'-','split');
    
    %Interior or Exterior? / Related spaces
    if Surf_name_id{end-2}=='E'
        %Exterior
        Exterior=int8(1);
        
        %Rel_space=str2double(Surf_name_id{2});
        %surface name is not reliable!!! (Check Two Room One Floor)
        for i_space=1:Num_space
            if ismember(i_surface,Infor_space_simp(i_space).RelatedSurface)
                Rel_space=i_space;
            end
        end
        
    elseif Surf_name_id{end-2}=='I'
        %Interior
        Exterior=int8(0);
        
        %         if Surf_name_id{2}==Surf_name_id{3}
        %             Rel_space=str2double(Surf_name_id{2});
        %         else
        %             Rel_space=[str2double(Surf_name_id{2}) str2double(Surf_name_id{3})];
        %         end
        %surface name is not reliable!!! (Check Two Room One Floor)
        if Surf_name_id{2}==Surf_name_id{3}
            for i_space=1:Num_space
                if ismember(i_surface,Infor_space_simp(i_space).RelatedSurface)
                    Rel_space=i_space;
                end
            end
        else
            Rel_space=zeros(1,2);
            temp=0;
            for i_space=1:Num_space
                if ismember(i_surface,Infor_space_simp(i_space).RelatedSurface)
                    temp=temp+1;
                    Rel_space(temp)=i_space;
                end
            end
        end
        
    else
        %Shading
        Exterior=int8(2);
        Rel_space=[];
    end
    
    %Wall, Floor, Roof or Shading?
    if Exterior==2
        %Shading
        surf_class=int8(4);
    elseif Surf_name_id{end-1}=='W'
        %Wall
        surf_class=int8(1);
    elseif Surf_name_id{end-1}=='F'
        %Floor
        surf_class=int8(2);
    else  %Surf_name_id{end-1}=='R'
        %Roof
        surf_class=int8(3);
    end
    
    Infor_surface_simp(i_surface).Exterior=Exterior;
    Infor_surface_simp(i_surface).Class=surf_class;
    Infor_surface_simp(i_surface).RelatedSpace=Rel_space;
    
    if surf_class~=4
        %For non-shading type get construction id and thermal properties
        %ConsId
        Infor_surface_simp(i_surface).ConsId=tree.Campus.Surface(i_surface, 1).ATTRIBUTE.constructionIdRef;
        
        %Surface thermal properties
        %U
        for i_cons=1:Num_cons
            %Matching construction
            if strcmp(Infor_cons_simp(i_cons).id,Infor_surface_simp(i_surface).ConsId)
                %Matched construction
                %U
                Infor_surface_simp(i_surface).U=Infor_cons_simp(i_cons).U;
                
                %C
                Infor_surface_simp(i_surface).C=Coef*Infor_cons_simp(i_cons).C; % adjust the thermal capacitance value
                
                %Absorptance
                Infor_surface_simp(i_surface).Absorptance=Infor_cons_simp(i_cons).Absorptance;
                
                %Roughness
                Infor_surface_simp(i_surface).Roughness=Infor_cons_simp(i_cons).Roughness;
                
                break;
            end
        end
    end
    
    
    % Opening detail
    %Get number of openning
    if isfield(tree.Campus.Surface(i_surface,1), 'Opening')
        N_opening=length(tree.Campus.Surface(i_surface,1).Opening);
    else
        N_opening=0;
    end
    Infor_surface_simp(i_surface).N_open=N_opening;
    
    if N_opening > 0
        %Pre-allocate opening info
        Infor_surface_simp(i_surface).('Opening')=struct('Name', [], ...
            'Coordinate',zeros(4,3), ...
            'Height',0, ...
            'Width',0, ...
            'Area',0, ...
            'Type', [], ...
            'TypeId', [], ...
            'WinDoor', int8(0),...
            'U', 0, ...
            'C', 0, ...
            'SHGC', 0, ...
            'Transmittance', 0);
        Infor_surface_simp(i_surface).Opening(1:N_opening)=struct('Name', [], ...
            'Coordinate',zeros(4,3), ...
            'Height',0, ...
            'Width',0, ...
            'Area',0, ...
            'Type', [], ...
            'TypeId', [], ...
            'WinDoor', int8(0),...
            'U', 0, ...
            'C', 0, ...
            'SHGC', 0, ...
            'Transmittance', 0);
        
        % Assign opening info
        WindowSurface=0;
        DoorSurface=0;
        N_win=0;
        N_door=0;
        for i_open=1:N_opening
            %Opening name
            Open_name=tree.Campus.Surface(i_surface,1).Opening(i_open,1).Name;
            Infor_surface_simp(i_surface).Opening(i_open).Name=Open_name;
            %
           % 
            %Coordinates
            %np == number of points of coordinates
            [np,temp]=size(tree.Campus.Surface(i_surface,1).Opening(i_open,1).PlanarGeometry.PolyLoop.CartesianPoint); %#ok<*NASGU>
            for i_coor=1:np
                Infor_surface_simp(i_surface).Opening(i_open).Coordinate(i_coor,:)=cell2mat(tree.Campus.Surface(i_surface,1).Opening(i_open,1).PlanarGeometry.PolyLoop.CartesianPoint(i_coor,:).Coordinate)*A;
            end
            
            %Height and Width
            Infor_surface_simp(i_surface).Opening(i_open).Height=tree.Campus.Surface(i_surface,1).Opening(i_open,1).RectangularGeometry.Height*A; %[m]
            Infor_surface_simp(i_surface).Opening(i_open).Width=tree.Campus.Surface(i_surface,1).Opening(i_open,1).RectangularGeometry.Width*A; %[m]
            
            %Type
            Infor_surface_simp(i_surface).Opening(i_open).Type=tree.Campus.Surface(i_surface,1).Opening(i_open,1).ATTRIBUTE.openingType;
            
            
            %Post-process values
            %Area
            Infor_surface_simp(i_surface).Opening(i_open).Area=Infor_surface_simp(i_surface).Opening(i_open).Height*Infor_surface_simp(i_surface).Opening(i_open).Width; % [sq. m]
            
            
            %Identify class of opening and get U and C for each opening
            Open_name_id=regexp(Open_name,'-','split');
            
            if Open_name_id{end-1}=='W'
                N_win=N_win+1;
                %Win 1, Door 2
                Infor_surface_simp(i_surface).Opening(i_open).WinDoor=1;
                %Window
                Infor_surface_simp(i_surface).Opening(i_open).Class=int8(1);
                
                %TypeId
                Infor_surface_simp(i_surface).Opening(i_open).TypeId=tree.Campus.Surface(i_surface, 1).Opening(i_open, 1).ATTRIBUTE.windowTypeIdRef;
                
                %Window surface area
                WindowSurface=WindowSurface+Infor_surface_simp(i_surface).Opening(i_open).Area;
                
                %Window thermal properties
                for i_win=1:Num_win
                    %Matching window construction
                    if strcmp(Infor_win_simp(i_win).id,Infor_surface_simp(i_surface).Opening(i_open).TypeId)
                        %Matched window
                        %U
                        Infor_surface_simp(i_surface).Opening(i_open).U=Infor_win_simp(i_win).U;
                        
                        %C ****C of window = 0, No need to adjust****
                        %Infor_surface_simp(i_surface).Opening(i_open).C=0;
                        
                        %SHGC
                        Infor_surface_simp(i_surface).Opening(i_open).SHGC=Infor_win_simp(i_win).SHGC;
                        
                        %Transmittance
                        Infor_surface_simp(i_surface).Opening(i_open).Transmittance=Infor_win_simp(i_win).Transmittance;
                        break;
                    end
                end
            else %Open_name_id{end-1}=='D'
                %Win 1, Door 2
                Infor_surface_simp(i_surface).Opening(i_open).WinDoor=2;
                
                %Door
                Infor_surface_simp(i_surface).Opening(i_open).Class=int8(2);
                
                %TypeId
                Infor_surface_simp(i_surface).Opening(i_open).TypeId=tree.Campus.Surface(i_surface, 1).Opening(i_open, 1).ATTRIBUTE.constructionIdRef;
                
                %Sum door's surface area
                DoorSurface=DoorSurface+Infor_surface_simp(i_surface).Opening(i_open).Area;
                
                %Door thermal properties
                for i_cons=1:Num_cons
                    %Matching construction
                    if strcmp(Infor_cons_simp(i_cons).id,Infor_surface_simp(i_surface).Opening(i_open).TypeId)
                        %Matched construction
                        %U
                        Infor_surface_simp(i_surface).Opening(i_open).U=Infor_cons_simp(i_cons).U;
                        
                        %C
                        Infor_surface_simp(i_surface).Opening(i_open).C=Coef*Infor_cons_simp(i_cons).C;   % adjust the thermal capacitance value
                        
                        %Ignore SGHC and Transmittance for door
                        break;
                    end
                end
            end
        end
        
        %A_noOpen
        A_noOpen=Infor_surface_simp(i_surface).Area - sum([Infor_surface_simp(i_surface).Opening(:).Area]);
        Infor_surface_simp(i_surface).Area_noOpen=A_noOpen;
        
        %A_noDoor to calculate how much is the surface area of a wall when
        %the door is open due to people moving in the room
%         s=0;
%         for i_opening=1:length(Infor_surface_simp(i_surface).Opening(:))
%         if Infor_surface_simp(1,i_surface).Opening(i_opening).WinDoor==2
%         s=Infor_surface_simp(1, 8).Opening(i_opening).Area+s;
%         end 
%         end 
%         Infor_surface_simp(i_surface).Area_noDoor=Infor_surface_simp(i_surface).Area-s;
        Infor_surface_simp(i_surface).WindowSurface=WindowSurface;
        
        %U_ave (Area averaged of U of this surface)
        UA=Infor_surface_simp(i_surface).U*A_noOpen + sum([Infor_surface_simp(i_surface).Opening(:).U].*[Infor_surface_simp(i_surface).Opening(:).Area]);
        Infor_surface_simp(i_surface).U_ave=UA/Infor_surface_simp(i_surface).Area;
        
        %C_ave (Area averaged of C of this surface)
        CA=Infor_surface_simp(i_surface).C*A_noOpen + sum([Infor_surface_simp(i_surface).Opening(:).C].*[Infor_surface_simp(i_surface).Opening(:).Area]);
        Infor_surface_simp(i_surface).C_ave=CA/Infor_surface_simp(i_surface).Area;
        
    else %No opening
        %A_noOpen
        Infor_surface_simp(i_surface).Area_noOpen=Infor_surface_simp(i_surface).Area;
        
        %U_ave
        Infor_surface_simp(i_surface).U_ave=Infor_surface_simp(i_surface).U;
        
        %C_ave
        Infor_surface_simp(i_surface).C_ave=Infor_surface_simp(i_surface).C;
        
    end
    
    %Roughness coefficient
    % Very Rough 1, Rough 2, Medium Rough 3, Medium Smooth 4, Smooth 5,
    % Very smooth 6.
    Roughness=Infor_surface_simp(1, i_surface).Roughness;
    if strcmp(Roughness,'VeryRough')
        Infor_surface_simp(i_surface).RoughnessCof = [11.58 5.894 0];
    elseif strcmp(Roughness, 'Rough')
        Infor_surface_simp(i_surface).RoughnessCof = [12.49 4.065 0.028];
    elseif strcmp(Roughness, 'MediumRough')
        Infor_surface_simp(i_surface).RoughnessCof = [10.79 4.192 0.0];
    elseif strcmp(Roughness, 'MediumSmooth')
        Infor_surface_simp(i_surface).RoughnessCof = [8.23 4.0 -0.057];
    elseif strcmp(Roughness, 'Smooth')
        Infor_surface_simp(i_surface).RoughnessCof = [10.22 3.1 0.0];
    elseif strcmp(Roughness, 'VerySmooth')
        Infor_surface_simp(i_surface).RoughnessCof = [8.23 3.33 -0.036];
    end
    
end

%Post processing
%Get neighboring surface id
for i_surface=1:Num_surface
    NeighborSurface=[];
    ii=0;
    for j_surface=1:Num_surface
        if (i_surface ~= j_surface)
            %Find number of matched coordinate
            [m_rows_match,n_rows_match]=size(intersect(Infor_surface_simp(i_surface).Coordinate,Infor_surface_simp(j_surface).Coordinate,'rows'));
            if m_rows_match > 1
                %Share more than 1 point of coordinate
                ii=ii+1;
                NeighborSurface(ii)=j_surface;  %#ok<AGROW>
            end
        end
    end
    
    Infor_surface_simp(i_surface).NeighborSurface=NeighborSurface;
end

%% Post processing - Identify floor surface of each space
for i_space=1:Num_space
    for i_surface=Infor_space_simp(i_space).RelatedSurface
        if Infor_surface_simp(i_surface).SurfaceHeight==Infor_space_simp(i_space).FloorHeight
            Infor_space_simp(i_space).FloorSurfaceId=i_surface;
            Infor_surface_simp(i_surface).FloorOfSpace=i_space;
            break
        end
    end
end


%% Get each space's exterior surface list and non-exterior surfaces list
for i_space=1:Num_space
    k=1;
    h=1;
    for i_surface=1:length(Infor_space_simp(i_space).RelatedSurface)
        
        if Infor_surface_simp(1, Infor_space_simp(i_space).RelatedSurface(i_surface)).Type==1 ...         %ExteriorWall
                || Infor_surface_simp(1, Infor_space_simp(i_space).RelatedSurface(i_surface)).Type==2 ... %Roof
                || Infor_surface_simp(1, Infor_space_simp(i_space).RelatedSurface(i_surface)).Type==6     %RaisedFloor
            k=k+1;
            Infor_space_simp(i_space).ExteriorSurface(k)=Infor_space_simp(i_space).RelatedSurface(i_surface);
        else
            h=h+1;
            Infor_space_simp(i_space).NonExterior(h)=Infor_space_simp(i_space).RelatedSurface(i_surface);
        end
    end
    ExteriorSurface=Infor_space_simp(i_space).ExteriorSurface;
    Infor_space_simp(i_space).ExteriorSurface(ExteriorSurface==0)=[];
    
    NonExterior=Infor_space_simp(i_space).NonExterior;
    Infor_space_simp(i_space).NonExterior(NonExterior==0)=[];
end


end
