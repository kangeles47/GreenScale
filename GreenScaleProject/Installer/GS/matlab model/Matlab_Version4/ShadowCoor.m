function [Xshadow, facesun_flag, Shadow_flag, Xsr_cas, Xsr_cas_new]=ShadowCoor(X_cas,X_rec,azi_rec,tilt_rec,azi_sun,tilt_sun)

%Use this function to get coordinate of shadow in term of coodinate
%referenced to receiving surface coordinate

%Date create: 8/18/2013 by Saran Salakij 

%Use together with cos_AIS, wc2rc, ClipCoor, getShadow

%Input: X_cas    == Coordinate of casting surface
%       X_rec    == Coordinate of receiving surface
%       azi_rec  == Azimuth angle of normal vector of receiving surface [rad]  
%       tilt_rec == Tilt angle of receiving surface [rad]     
%       azi_sun  == Azimuth angle of the sun [rad]  
%       tilt_sun == Altitude angle of the sun [rad]

%Output: Xshadow == Coordinate of shadow in 2D (relative to receiving surface)    
%        facesun_flag == 1 if receiving surface facing sun
%        Shadow_flag == 1 if shadow exist

%% Initial setup
% Referenced point

Xref=X_rec(1,:);
% tolerance introduced by coordinate transformation
tol_z=1e-5;

%% Check if surface is facing the sun
cos_theta=cos_AIS(azi_sun,tilt_sun,azi_rec,tilt_rec);

if cos_theta < 0
    
    %Receiving surface is not facing the sun.
    facesun_flag=0;
    Xsr_cas=[];
    Xsr_cas_new=[];
    Xshadow=[];
    
else
    %Receiving surface is facing the sun.
    facesun_flag=1;
    
    %% Check if casting surface is behind or below the receiving surface
    if max(X_cas(:,3)) < min(X_rec(:,3))
        %Casting surface is below --> no shadow
        Xsr_cas=[];
        Xsr_cas_new=[];
        Xshadow=[];
    else
        %Transform coordinate of potential casting surface
        
        Xsr_cas=wc2rc(X_cas,Xref,azi_rec,tilt_rec);
        
        %Xsr_cas
        if max(Xsr_cas(:,3)) < tol_z %(not a single zsr > 0)
            %Casting surface is behind --> no shadow
            Xsr_cas_new=[];
            Xshadow=[];
        else
            %Clipping surface behind (zsr < 0)
            Xsr_cas_new=ClipCoor(Xsr_cas);
        
            %Project shadow onto receiving surface referenced to receiving
            %surface
            Xshadow=getShadow(Xsr_cas_new,azi_sun,tilt_sun,azi_rec,tilt_rec);
        end
    end
end

%Check if shadow exist
if isempty(Xshadow)
    Shadow_flag=0;
elseif max(range(Xshadow))>1e5 %over-range shadow projecting case
    Shadow_flag=0;
else
    Shadow_flag=1;
end

end

