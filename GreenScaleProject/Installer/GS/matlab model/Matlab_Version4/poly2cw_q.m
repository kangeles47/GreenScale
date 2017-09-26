function [x_cw,y_cw,cw_flag]=poly2cw_q(x,y)
%Use to quickly transform 2D coordinates to order in clockwise direction
%Assume X already in order of either CW or CCW

%Date create: 8/18/2013 by Saran Salakij

%Input: X == 2D coordinate

if isempty(x) || isempty(y)
    x_cw=[];
    y_cw=[];
    cw_flag=1;
 
else

    X(:,1)=x; X(:,2)=y;
    A=0.5*(    sum(    x(1:end-1).*y(2:end)-x(2:end).*y(1:end-1)    ) + x(end).*y(1)-x(1).*y(end)    );
    
    if A > 0
        %CCW
        Xcw=X(end:-1:1,:);
        cw_flag=0;
    else
        %CW
        Xcw=X;
        cw_flag=1;
    end
    
    x_cw=Xcw(:,1); y_cw=Xcw(:,2);

end
end