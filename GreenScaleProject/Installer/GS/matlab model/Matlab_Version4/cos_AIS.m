function [cos_theta, CS1, CS2, CS3, CW1, CW2, CW3]=cos_AIS(azi_sun,tilt_sun,azi_surf,tilt_surf)

% Use to find the cosine of the angle of incidence of the sun's rays on the
% surface

% Date create: 8/16/2013 by Saran Salakij
% See EnergyPlus manual Engineering p.150

% Input:    azi_sun     ==azimuth angle of the sun [rad]
%           tilt_sun    ==tilt angle of the sun [rad]
%           azi_surf    ==azimuth angle of the surface [rad]
%           tilt_surf   ==tilt angle of the surface [rad]

% Note: If cos_theta > 0, surface is facing the sun.
%azi_sun
%tilt_sun
%azi_surf
%tilt_surf
%sun direction cosines
CS1=sin(azi_sun).*cos(tilt_sun);
%CS1
CS2=cos(azi_sun).*sin(tilt_sun);
%CS2
CS3=cos(tilt_sun);
%CS3
%surface direction cosines
CW1=sin(azi_surf).*cos(tilt_surf);
%CW1
CW2=cos(azi_surf).*sin(tilt_surf);
%CW2
CW3=cos(tilt_surf);

cos_theta=CS1*CW1+CS2*CW2+CS3*CW3;
end