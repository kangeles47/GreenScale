%  
% Heat_exact = xlsread('D:\study and research\2013spring\Intermediate Heat Transfer\project1\models\Flat_model.csv', 'Flat_model', 'EO2:EO25');
% 
% Heat_model = Q_hour_W;
% 
% for i =1 :24
% D (i) = abs(Heat_exact(i)) -  Heat_model(i) ; 
% 
% end 
% 
% n = 1:24; n=n'; 
% plot(n,abs(Heat_exact),'r', n, Heat_model,'*');
% legend('Exact','Code');
% title('heat, W');
% xlabel('Hour');
% mean(D)
% % 
% 
%  a1=xlsread('D:\study and research\2013spring\Intermediate Heat Transfer\project1\models\Flat_model.csv', 'Flat_model', 'EF2:EF8761');
%   b1=xlsread('D:\study and research\2013spring\Intermediate Heat Transfer\project1\models\Flat_model.csv', 'Flat_model', 'EG2:EG8761');

%% compare the exterior temperature: 
n=Tpp(2,3:26);
%  save Out_temp.mat n
 
 plot(n,'b-*');
 
 hold on; 
 plot(T_outside-273, 'r')
 
 T_e=xlsread('D:\study and research\summer research\Work Plan Record\Work-3-15\work 4-8\Tests0501\Fixed with 0 radiation\Flat_model_single wall _Cp_0.csv', 'Flat_model_single wall _Cp_0', 'CJ410:CJ433');
 
 hold on; 
  plot(T_e, 'y')
  
%   legend('Matlab Code','Environment','Energy+')
%   
%   title('The exterior surface temperature of Surface 2')
%   xlabel('Hours, on Februrary 1')
%   ylabel('Temperature, C')
%   
  
  m=Tpp_interior(2,2:25);
   plot(m,'g-*');
   
    hold on; 
   T_space=ones(1,24)*22; 
    
 plot(T_space, 'k')
 
   hold on; 
T_in = xlsread('D:\study and research\summer research\Work Plan Record\Work-3-15\work 4-8\Tests0501\Fixed with 0 radiation\Flat_model_single wall _Cp_0.csv', 'Flat_model_single wall _Cp_0', 'CI410:CI433');
 plot(T_in, 'p')
 
   legend('Matlab Code','Environment','Energy+')
  
%   title('The interior surface temperature of Surface 2')
  title('The interior and exterior surface temperature of Surface 2')
  xlabel('Hours, on Februrary 1')
  ylabel('Temperature, C')
  
  
   plot(n,'b');hold on; 
   plot(T_outside-273, 'r');hold on;
   plot(T_e, 'g');hold on;
   plot(m,'g-*');hold on;
   plot(T_space, 'k')
 
  legend('Exterior_Matlab','Outdoor Temp','Exterior_Energy+','Interior_Matlab','Interior_Energy+')
  title('The interior and exterior surface temperature of Surface 2')
  xlabel('Hours, on Februrary 1')
  ylabel('Temperature, C')
  
  
  %% energy 
  
  Q_e_767 = xlsread('D:\study and research\summer research\Work Plan Record\Work-3-15\work 4-8\Tests0501\Fixed with 0 radiation\Flat_model_single wall_Cp767.csv', 'Flat_model_single wall_Cp767', 'ET98:ET121');
  Q_e_0 = xlsread('D:\study and research\summer research\Work Plan Record\Work-3-15\work 4-8\Tests0501\Fixed with 0 radiation\good test\Flat_model_single wall _Cp_0_july2.csv', 'Flat_model_single wall _Cp_0_ju', 'ERS26:ES49');
  plot(Q_e_767,'b');  hold on ;
  plot(Q_e_0,'r'); 
  legend('Cp=767','Cp=0')
  
   Q_767 = xlsread('D:\study and research\summer research\Work Plan Record\Work-3-15\work 4-8\Tests0501\Fixed with 0 radiation\Flat_model_single wall_Cp767.csv', 'Flat_model_single wall_Cp767', 'ER26:ER49');
   plot(Q_767); title ('Fixed external temperature, Normal Cp')
   
   
   
   Q_matlab = Q_hour_W(1:192); 
   Q_e = xlsread('D:\study and research\summer research\Work Plan Record\Work-3-15\work 4-8\Tests0501\Fixed with 0 radiation\second case_normal temp\Flat_model_single wall_Cp767_copy.csv', 'Flat_model_single wall_Cp767_co', 'ES2:ES193');
   plot(Q_matlab,'b');
   hold on; 
   plot(Q_e,'r'); 
   legend('Matlab','Energy+')
   title('Heat energy,Cp=767, W')
   xlabel('Hour')
   ylabel('Heat Energy')
   
      Q_matlab = Q_hour_W(1:192); 
   Q_e = xlsread('D:\study and research\summer research\Work Plan Record\Work-3-15\work 4-8\Tests0501\Fixed with 0 radiation\second case_normal temp\Flat_model_single wall _Cp_0_copy.csv', 'Flat_model_single wall _Cp_0_co', 'ES2:ES193');
   plot(Q_matlab,'b');
   hold on; 
   plot(Q_e,'r'); 
   legend('Matlab','Energy+')
   title('Heat energy,Cp=0,6.25~7.2 W')
   xlabel('Hour')
   ylabel('Heat Energy')
   
   
    plot(T_outside); title('The outside door Temperature during 6.25~7.2'); xlabel('Hours');ylabel('Temperature,C');
    
    
    T_interior = xlsread('D:\study and research\summer research\Work Plan Record\Work-3-15\work 4-8\Tests0501\Fixed with 0 radiation\second case_normal temp\Flat_model_single wall_Cp767_copy.csv', 'Flat_model_single wall_Cp767_co', 'CI2:CI193');
   plot(Tpp_interior(2,2:193),'b');
   hold on; 
   plot(T_interior,'r'); 
%    hold on;
%    plot(T_outside-273,'g')
   legend('Matlab','Energy+')
   title('Interior Temp pf surface 2,Cp=767,6.25~7.2 W')
   xlabel('Hour')
   ylabel('Interior surface Temp, C')
   
   
       Q_cool = xlsread('D:\study and research\summer research\Work Plan Record\Work-3-15\work 4-8\Tests0501\Fixed with 0 radiation\second case_normal temp\Flat_model_single wall_Cp767_wholeyear.csv', 'Flat_model_single wall_Cp767_wh', 'EQ2:EQ8761');
       Q_heat = xlsread('D:\study and research\summer research\Work Plan Record\Work-3-15\work 4-8\Tests0501\Fixed with 0 radiation\second case_normal temp\Flat_model_single wall_Cp767_wholeyear.csv', 'Flat_model_single wall_Cp767_wh', 'ER2:ER8761');
       Q_e= Q_cool/3600+Q_heat; 
       
   plot(Q_hour_W,'b');
   hold on; 
   plot(Q_e,'r'); 
%    hold on;
%    plot(T_outside-273,'g')
   legend('Matlab','Energy+')
   title('Whole year simulation,Cp=767, W')
   xlabel('Hour')
   ylabel('Heat, W')
   
   
  
   
          Q_cool = xlsread('D:\study and research\summer research\Work Plan Record\Work-3-15\work 4-8\Tests0501\Fixed with 0 radiation\second case_normal temp\ Flat_model_single wall _Cp_0_wh.csv', ' Flat_model_single wall _Cp_0_wholeyear', 'EQ2:EQ8761');
       Q_heat = xlsread('D:\study and research\summer research\Work Plan Record\Work-3-15\work 4-8\Tests0501\Fixed with 0 radiation\second case_normal temp\ Flat_model_single wall _Cp_0_wh', 'ER2:ER8761');
       Q_e= Q_cool/3600+Q_heat; 