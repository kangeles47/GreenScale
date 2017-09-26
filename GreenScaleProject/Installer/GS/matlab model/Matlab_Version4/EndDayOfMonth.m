function daysofmonth=EndDayOfMonth(month)
if ismember(month,[1,3,5,7,8,10,12])     
    daysofmonth=31;
elseif ismember(month,[4,6,9,11])
    daysofmonth=30;
else %month==2 
    daysofmonth=28;
end 