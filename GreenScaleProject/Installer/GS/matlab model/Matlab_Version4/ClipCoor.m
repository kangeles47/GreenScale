function Xnew=ClipCoor(X)

%Use this function to clip-out part that z < 0
%Date create: 8/18/2013 by Saran Salakij

%Input: X == coordinate required to be clipped. 

%% Sample X
%X=[-11.0625000000000,-6.83013391122704,1.83011495674436;-11.0625000000000,-6.83016093014923,-8.16983824510963;-11.0625000000000,-26.8301539363976,-8.16983420726525;-11.0625000000000,-26.8301269174754,1.83011899458874];

%% Setup variable
tol_z=1e-5;

%Store size of matrix that need to be clipped.
[m,n]=size(X); %#ok<NASGU>

%Add additional row of point to first and last row of X to easily calcualte
Xtemp=[X(end,:); X; X(1,:)];
z=Xtemp(:,3);

%Pre-allocate Xnew
Xnew=zeros(2*m,3);


%% Clipping
jj=0;

for ii=2:m+1
    if z(ii) > -tol_z 
        %No need to be clipped.
        jj=jj+1;
        Xnew(jj,:)=Xtemp(ii,:);
        
    else
        %Need to be clipped.
        if z(ii-1) <= tol_z && z(ii+1) <= tol_z
            %Both neighbor points are negative --> get rid of this point.
     
        elseif z(ii-1) > tol_z && z(ii+1) > tol_z
            %Both neighbor points are positive --> interpolate to both points.
            %Get two new points
            jj=jj+1;
            Xnew(jj,:)=Xtemp(ii-1,:)-z(ii-1)*((Xtemp(ii,:)-Xtemp(ii-1,:))./(z(ii)-z(ii-1)));
            jj=jj+1;
            Xnew(jj,:)=Xtemp(ii+1,:)-z(ii+1)*((Xtemp(ii,:)-Xtemp(ii+1,:))./(z(ii)-z(ii+1)));
            
        elseif z(ii-1) > tol_z
            %Previous point is positive.
            jj=jj+1;
            Xnew(jj,:)=Xtemp(ii-1,:)-z(ii-1)*((Xtemp(ii,:)-Xtemp(ii-1,:))./(z(ii)-z(ii-1)));
        else % z(ii+1) > tol_z
            %Next point is positive.
            jj=jj+1;
            Xnew(jj,:)=Xtemp(ii+1,:)-z(ii+1)*((Xtemp(ii,:)-Xtemp(ii+1,:))./(z(ii)-z(ii+1)));
            
        end
    end
    
end

%Resize Xnew
Xnew=Xnew(1:jj,:);

end