function A=GetSurfaceArea(Coordinates, azi_surf,tilt_surf)

azi_surf_rad=azi_surf*pi/180;
tilt_surf_rad=tilt_surf*pi/180;
X=Coordinates;
Xref=Coordinates(1,:);
%[X1,u1,v1,w1]=wc2rc(X,Xref,azi_surf,tilt_surf);
[X1]=wc2rc(X,Xref,azi_surf_rad,tilt_surf_rad);

A=polyarea_q(X1(:,1),X1(:,2));

end 