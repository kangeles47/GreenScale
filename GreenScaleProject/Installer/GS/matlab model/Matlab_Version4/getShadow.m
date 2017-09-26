function Xshadow=getShadow(X,azi_sun,tilt_sun,azi_surf,tilt_surf)

% Use to find location of shadow

% Date create: 8/16/2013 by Saran Salakij
% See EnergyPlus manual Engineering p.151

%Use together with cos_AIS

% Input:    X           ==Coordinate of casting surface referenced to recieveing surface (x, y z) 
%           azi_sun     ==azimuth angle of the sun [rad]
%           tilt_sun    ==tilt angle of the sun [rad]
%           azi_surf    ==azimuth angle of the surface [rad]
%           tilt_surf   ==tilt angle of the surface [rad]

x=X(:,1); y=X(:,2); z=X(:,3);
%Find cos_theta and CS
[cos_theta, CS1, CS2, CS3]=cos_AIS(azi_sun,tilt_sun,azi_surf,tilt_surf);

a= sin(azi_surf).*CS1                   -cos(azi_surf).*CS2;
b=-cos(azi_surf).*cos(tilt_surf).*CS1   -sin(azi_surf).*cos(tilt_surf).*CS2     +sin(tilt_surf).*CS3;

%Get coordinate of shadow (in 2D)
xp=x-z.*a./cos_theta;
yp=y-z.*b./cos_theta;

Xshadow=[xp yp];

end
