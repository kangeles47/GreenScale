clc; clear;

[Weather_infor4,month1,day1,month2,day2] = Weather_fake('Fakeweather',[1,1,1],[12,31,24]); 
Weather_infor5= Fakeweather2(Weather_infor4);
dlmwrite('myfile.epw', Weather_infor5,  'precision', 6); 


fidA=fopen('Weather_head.txt','r');
fidB=fopen('myfile.epw','r');
DataA=fread(fidA);
DataB=fread(fidB);
fidC=fopen('Weather_Washigton_2.epw','w');
fwrite(fidC,DataA);
fprintf(fidC,'\n');
fwrite(fidC,DataB);
fprintf(fidC,'\n');
fclose(fidA);
fclose(fidB);
fclose(fidC);

