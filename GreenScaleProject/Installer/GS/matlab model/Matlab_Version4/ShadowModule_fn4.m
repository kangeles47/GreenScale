function [Ashadow_wo_win,Ashadow_win,Ashadow]=ShadowModule_fn4(Infor_surface_simp,surface_id,azi_sun_rad,tilt_sun_rad)

%Calculate for shading area on the surface
%Modified from ShadowModule_fn3.m
%Date: 9/6/2013 by Saran Salakij
%Corrected the over-range shadow projecting case
%Corrected unround values

%*****REQUIRE to run SimplifiedGeometryData_fn.m first*****

%Input: Infor_surface_simp == Simplified surface information get from SimplifiedGeometryData.m
%       surface_id == Index of receiving surface 
%       azi_sun_rad == Azimuth angle of sun [rad]
%       tilt_sun_rad == Altitude angle of sun [rad]

%Output: Ashadow_wo_win == Area of shadow on receiving surface, but not windows [m^2]
%        Ashadow_win    == Area of shadow on each windows [m^2]
%        Ashadow        == Area of shadow on receiving surface included windows [m^2]   

%Use together with ShadowCoor, wc2rc, poly2cw_q, polyarea_q


%% Get surface info
%disp(['azi_sun_rad ', num2str(azi_sun_rad)])
X_rec=Infor_surface_simp(surface_id).Coordinate; %[m m m]
%disp(['break', num2str('0')])
azi_rec_rad=Infor_surface_simp(surface_id).Azimuth*pi()/180; %[rad]
tilt_rec_rad=Infor_surface_simp(surface_id).Tilt*pi()/180; %[rad]
A_rec=Infor_surface_simp(surface_id).Area; %[m^2] 

%Get window info (if any)
n_o=Infor_surface_simp(surface_id).N_open;
if n_o > 0
    %preallocate
    X_win(1:n_o)=struct('C',zeros(4,3));
    A_win=zeros(1,n_o);
    
    for i_open=1:n_o
        if Infor_surface_simp(surface_id).Opening(i_open).WinDoor==1 %Window  
            X_win(i_open).C=Infor_surface_simp(surface_id).Opening(i_open).Coordinate; %[m m m]
            %disp(['X_win(i_open).C: ',num2str(X_win(i_open).C)]);
            A_win(i_open)=Infor_surface_simp(surface_id).Opening(i_open).Area; %[m^2]
            %A_win(i_open)
        end
    end
end
% %% Convert degree to rad
% azi_sun_rad=azi_sun*pi()/180; %[rad]
% tilt_sun_rad=tilt_sun*pi()/180; %[rad]


%% Transform coordinate of receiving surface from world to point on surface
Xsr_rec=wc2rc(X_rec,X_rec(1,:),azi_rec_rad,tilt_rec_rad);

%sort coordinates of receiving surface to clockwise order

[Xcw_rec1,Xcw_rec2]=poly2cw_q(Xsr_rec(:,1),Xsr_rec(:,2));

%% Transform windows
if n_o > 0
    
    Xsr_win(1:n_o)=struct('C',zeros(4,3));
    Xcw_win1(1:n_o)=struct('C',zeros(4,1));
    Xcw_win2(1:n_o)=struct('C',zeros(4,1));
    
    for i_open=1:n_o
        if A_win(i_open) > 0
            Xsr_win(i_open).C=wc2rc(X_win(i_open).C,X_rec(1,:),azi_rec_rad,tilt_rec_rad);
            
            %sort coordinates
            [Xcw_win1(i_open).C,Xcw_win2(i_open).C]=poly2cw_q(Xsr_win(i_open).C(:,1),Xsr_win(i_open).C(:,2));
        end
    end
end

%%

%Initialize non-shading coordinates for surface
x_nonshading=Xcw_rec1;
y_nonshading=Xcw_rec2;

if n_o > 0
    %Initialize non-shading coordinates for windows    
    x_nonshading_w=Xcw_win1;
    y_nonshading_w=Xcw_win2;
end

%ns == Number of surfaces
[temp,ns]=size(Infor_surface_simp); %#ok<ASGLU> 

Shadow_flag=zeros(1,ns);


for i_surface=1:ns
    
    %% Get shadow coordinate relative to receiving surface
    %Infor_surface_simp(i_surface).TypeName
    %Skip interior surface, consider only exterior and shading
    if Infor_surface_simp(i_surface).Exterior==0
        %Skip interior surface
        %Infor_surface_simp(i_surface).TypeName
        
    else
        
        X_cas=Infor_surface_simp(i_surface).Coordinate; %[ m m m]
        if ~isequal(X_cas,X_rec)
            %Infor_surface_simp(i_surface).TypeName
            %Avoid evaluate the case that casting surface is the same surface as receiving surface
            [Xshadow, facesun_flag, Shadow_flag(i_surface)]=ShadowCoor(X_cas,X_rec,azi_rec_rad,tilt_rec_rad,azi_sun_rad,tilt_sun_rad); %#ok<ASGLU>
            
        end
    end
    
    %% Get non-shading area by substracting shadow from receiving surface   
    if Shadow_flag(i_surface) && ~isempty(x_nonshading)  
        %sort coordinates of casting surface to clockwise order
        [Xcw_shadow1,Xcw_shadow2]=poly2cw_q(Xshadow(:,1),Xshadow(:,2));
        %Get non-shading coordinates
        %Surface
        %x_nonshading
        %y_nonshading
        %Xcw_shadow1
        %Xcw_shadow2
        [x_nonshading,y_nonshading]=polybool('-',x_nonshading,y_nonshading,Xcw_shadow1,Xcw_shadow2);
        %x_nonshading
        %y_nonshading
        %Windows
        if n_o > 0
            for i_open=1:n_o
                if A_win(i_open) > 0
                    [x_nonshading_w(i_open).C,y_nonshading_w(i_open).C]=polybool('-',x_nonshading_w(i_open).C,y_nonshading_w(i_open).C,Xcw_shadow1,Xcw_shadow2);
                end
            end
        end
        
    end
    
end

Ashadow_win=zeros(1,n_o);
if sum(Shadow_flag)
    %Get shadowing area
    Ashadow=roundn(A_rec-polyarea_q(x_nonshading,y_nonshading),-5);
   
    %Windows
    if n_o >0
        for i_open=1:n_o
            if A_win(i_open) > 0
                %Get shadow area on windows
                Ashadow_win(i_open)=roundn(A_win(i_open)-polyarea_q(x_nonshading_w(i_open).C,y_nonshading_w(i_open).C),-5);
            end
        end
    end
    Ashadow_wo_win=Ashadow-sum(Ashadow_win);
    
else
    Ashadow=0;
    Ashadow_wo_win=0;
    
end

%Avoid error
if isnan(Ashadow)
    Ashadow=0;
end

if isnan(Ashadow_wo_win)
    Ashadow_wo_win=0;
end


end
