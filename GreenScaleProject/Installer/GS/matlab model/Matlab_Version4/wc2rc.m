function [X1,u1,v1,w1]=wc2rc(X,Xref,azi_surf,tilt_surf)

% Use to transform world coordinate to relative coordinate
% Date create: 8/16/2013 by Saran Salakij
% See Kenneth Joy UC Davis COORDINATE CONVERSION BETWEEN THE CARTESIAN FRAME AND AN ARBITRARY FRAME (Cartesian-Frame-to-Frame.pdf)

% Input:    X == vector coordinate (x,y,z)
%           Xref == referenced coordinate
%           azi_surf == azimuth angle of referenced surface [rad]
%           tilt_surf == tilt angle of referenced surface [rad]            

% Direct method
% V1=X(2,:)-X(1,:);
% V2=X(3,:)-X(1,:);
% 
% % ang_V=acos(dot(V1,V2)/(norm(V1)*norm(V2)));
% 
% CV=cross(V1,V2);
% 
% u=V1/norm(V1);
% %v=V2/norm(V2);
% w=CV/norm(CV);
% 
% v=cross(w,u);

% % Avoid error of azi_surf == +/-45 degree of tilt_surf == +/-45, +/-90 degree, slightly alter azi_surf or tilt_surf
% err=1e-5;
% 
% if ismember(abs(azi_surf),[pi()/4,pi()/2])
%     azi_surf=azi_surf+err;
% end
% if abs(tilt_surf)==pi()/4
%     tilt_surf=tilt_surf+err;
% end

% Calculate for unit vectors represented new coordinate system (relative to interexted plane)  
% from azi_surf and tilt_surf
u1=[sin(azi_surf)*cos(tilt_surf)  cos(azi_surf)*cos(tilt_surf) -sin(tilt_surf)];
w1=[sin(azi_surf)*sin(tilt_surf)  cos(azi_surf)*sin(tilt_surf)  cos(tilt_surf)];

% v1=cross(w1,u1);
%Result from cross(w1,u1)
% v1=[ - cos(azi_surf)*cos(tilt_surf)^2 - cos(azi_surf)*sin(tilt_surf)^2, sin(azi_surf)*cos(tilt_surf)^2 + sin(azi_surf)*sin(tilt_surf)^2, 0]
v1=[-cos(azi_surf), sin(azi_surf), 0];

% Translate
xp=X(:,1)-Xref(1);
yp=X(:,2)-Xref(2);
zp=X(:,3)-Xref(3);

X1_temp=[xp yp zp ones(size(xp))];


% Rotate
X1_temp=[xp yp zp ones(size(xp))]*[1 0 0; 0 1 0; 0 0 1; 0 0 0]/[u1; v1; w1; 0 0 0];

X1=X1_temp(:,1:3);

end