function A=polyarea_q(x,y)

%Use this to find area of 2-D polygon
%Alternate to polyarea(x,y) but quicker

%Date create: 8/18/2013 by Saran Salakij
%Modified on 9/16/2013 to correct over-range case

%Input: x,y == coordinate can be either in column or row

max_range=1e10;

%Skip point that show value NaN
i_temp=(~isnan(x) & ~isnan(y));

x=x(i_temp);
y=y(i_temp);


if isempty(x)
    A=0;
elseif range(x)>max_range || range(y)>max_range
    %Cannot work when range is too large
    A=polyarea(x,y);
else    
    A=0.5*abs(sum(x(1:end-1).*y(2:end)-x(2:end).*y(1:end-1)) + x(end).*y(1)-x(1).*y(end));
end

end