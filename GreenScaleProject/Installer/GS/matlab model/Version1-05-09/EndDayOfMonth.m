function daysofmonth=EndDayOfMonth(month)
if month==1|month==3|month==5|month==7|month==8|month==10|month==12
    daysofmonth=31;
elseif month==4|month==6|month==9|month==11 
    daysofmonth=30;
else month==2 
    daysofmonth=28;
end 