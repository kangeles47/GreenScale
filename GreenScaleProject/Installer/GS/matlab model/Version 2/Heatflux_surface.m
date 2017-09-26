%***********************************

% Loop on each surface  
% 1. Start from different surface species 

%***********************************


 % calculate four surfaces: exterior wall,roof, interior wall and undergroundwall(no transmitted solar energy)  

function [ Q_flux, Transmitted_win] = Heatflux_surface(surface_id,T_space,R3,C)
global Infor_surface Tp Tp_interior T_outside_temp ... 
       Ground_tem i_time Infor_space IS_record Solar_win i_space...
       Wind_speed_temp 
 
   Surface_type = Infor_surface{7, surface_id}.surfaceType; 
   Transmitted_win = 0 ;
   Alph_opaque = 0.7; 
   dt = 3600 ; 
   A = Infor_surface{8, surface_id};
   A_noWin = Infor_surface{14, surface_id}; 
   Z_surface =  Infor_surface{13,surface_id}; 
   
 % store the space name to each surface's side temperature    
   Tp_interior(surface_id, 2)= i_space ; 
  
   %lee ward surface will take only half of the outdoor convectionb
   %coefficient. and windward surface take the whole. 
   Is=0;
   %% 
   if strcmp(Surface_type,'ExteriorWall')  
       hc = 3.076;  
       % decide the space temperature, assuming the space name will be put
       % in order 
         Wind_speed = Wind_speed_temp *(Z_surface/10)^0.5;   % Stable air above human inhabited areas:
         hc_external = 8.23+4*Wind_speed-0.057*Wind_speed^2; 
   
         R5 = 1/hc; 
         R1 = 1/hc_external; 
 
         [Transmitted_win,Is] = getTransmitted_solar(surface_id); 
         Is = Is*A_noWin/A; 

         C2 = C/2; 
         C4 = C/2; 
         
         M1=C2/dt+1/R1+1/R3; 
         M2=C2/dt*Tp(surface_id,i_time+2) + T_outside_temp/R1+Alph_opaque*Is; 
         M3=C4/dt+1/R3+1/R5; 
         M4=C4/dt*Tp_interior(surface_id,i_time+2)+T_space/R5;
         
         T_out= (M4*R3+M3*M2*R3^2)/(M3*M1*R3^2-1);    % T1 is the exterior surface's temperature 
         T_in= (M1*T_out-M2)*R3;                        % T2 is the interior surface's temperature
         
         Tp(surface_id, i_time+3) = T_out; 
         Tp_interior(surface_id, i_time+3) = T_in; 
        
         
        %%
   elseif   strcmp(Surface_type, 'Roof')  % roof is also an exterior surface 
        tilt = Infor_surface{3, surface_id}.Tilt*pi/180;    
        Wind_speed = Wind_speed_temp *(Z_surface/10)^0.5;   % Stable air above human inhabited areas:
        hc_external= 8.23+4*Wind_speed-0.057*Wind_speed^2; 
        
        if  tilt==0% flat roof 
         hc = 0.948 ; % assume it is reduced convection T_space1 <T2 
         R5 = 1/(hc); 
         R1 = 1/hc_external; 
 
         [Transmitted_win,Is] = getTransmitted_solar(surface_id); 
         Is = Is*A_noWin/A; 
         C2 = C/2; 
         C4 = C/2; 
         
         M1=C2/dt+1/R1+1/R3; 
         M2=C2/dt*Tp(surface_id,i_time+2) + T_outside_temp/R1+Alph_opaque*Is; 
         M3=C4/dt+1/R3+1/R5; 
         M4=C4/dt*Tp_interior(surface_id,i_time+2)+T_space/R5;
         
         T_out= (M4*R3+M3*M2*R3^2)/(M3*M1*R3^2-1); % T1 is the exterior surface's temperature 
         T_in= (M1*T_out-M2)*R3;                     % T2 is the interior surface's temperature       
         
         if T_space > T_in
             
         hc = 4.04;         
         R5 = 1/(hc); 
          
         M1=C2/dt+1/R1+1/R3; 
         M2=C2/dt*Tp(surface_id,i_time+2) + T_outside_temp/R1+Alph_opaque*Is; 
         M3=C4/dt+1/R3+1/R5; 
         M4=C4/dt*Tp_interior(surface_id,i_time+2)+T_space/R5;
         
         T_out= (M4*R3+M3*M2*R3^2)/(M3*M1*R3^2-1); % T1 is the exterior surface's temperature 
         T_in= (M1*T_out-M2)*R3;                    % T2 is the interior surface's temperature
         
         end

       Tp(surface_id, i_time+3) = T_out; 
       Tp_interior(surface_id, i_time+3) = T_in;
       
        else  tilt ~= 0  % tiled roof 
            
         hc = 2.281 ; % assume it is reduced convection T_space1 <T2   
         R5 = 1/(hc); 
         R1 = 1/hc_external; 
 
         [Transmitted_win,Is] = getTransmitted_solar(surface_id); 
         C2 = C/2; 
         C4 = C/2; 
         
         M1=C2/dt+1/R1+1/R3; 
         M2=C2/dt*Tp(surface_id,i_time+2) + T_outside_temp/R1+Alph_opaque*Is; 
         M3=C4/dt+1/R3+1/R5; 
         M4=C4/dt*Tp_interior(surface_id,i_time+2)+T_space/R5;
         
         T_out= (M4*R3+M3*M2*R3^2)/(M3*M1*R3^2-1); % T1 is the exterior surface's temperature 
         T_in= (M1*T_out-M2)*R3;                     % T2 is the interior surface's temperature       
         
         if T_space > T_in
             
         hc = 3.87;         
         R5 = 1/(hc); 
          
         M1=C2/dt+1/R1+1/R3; 
         M2=C2/dt*Tp(surface_id,i_time+2) + T_outside_temp/R1+Alph_opaque*Is; 
         M3=C4/dt+1/R3+1/R5; 
         M4=C4/dt*Tp_interior(surface_id,i_time+2)+T_space/R5;
         
         T_out= (M4*R3+M3*M2*R3^2)/(M3*M1*R3^2-1); % T1 is the exterior surface's temperature 
         T_in= (M1*T_out-M2)*R3;                    % T2 is the interior surface's temperature
         
          end 

       Tp(surface_id, i_time+3) = T_out; 
       Tp_interior(surface_id, i_time+3) = T_in;  
        end 
        
      % store the space name to each surface's side temperature 

  %%       there is no solar transmitted energy through the interior wall 
   elseif strcmp(Surface_type,'InteriorWall')       
   
       C2=C/2;
       C4=C/2; 
       hc = 3.076; 
       R5 = 1/hc; 
       R1= 1/hc;
       
     % the another side's space name 
         str = Infor_surface{2, surface_id}(2, 1).ATTRIBUTE.spaceIdRef; 
         par_cell = regexp(str,'-','split');
         Space_id2 = str2double(par_cell{1,2});
        if Space_id2 == i_space 
         str = Infor_surface{2, surface_id}(1, 1).ATTRIBUTE.spaceIdRef; 
         par_cell = regexp(str,'-','split');
         Space_id2 = str2double(par_cell{1,2});
        end 
     
         T_space = Infor_space{9, i_space};  
         T_space2 = Infor_space{9, Space_id2};
                
        % assume that interior walls are always vertical. Vertical walls have constant convection coefficient        
        % T_in is the interior surface temperature in the space that we pick.  
         T_in = (C4*Tp(surface_id, i_time+2)/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*Tp_interior(surface_id, i_time+2)/dt+T_space/R1)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
         T_out = (C2*Tp_interior(surface_id, i_time+2)/dt+T_space/R1+(C2/dt+1/R3+1/R1)*(C4*Tp(surface_id, i_time+2)/dt+T_space2/R5)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);        
     
         Tp(surface_id, i_time+3) = T_out; 
         Tp_interior(surface_id, i_time+3) = T_in;

%%       
   else strcmp(Surface_type,'UndergroundWall')        
         hc = 3.096 ; 
         R5 = 1/hc; 
         C2 = C/2; 
         A1=C2/dt*Tp_interior(surface_id,i_time+2)+T_space/R5+Ground_tem/R3+G_space; 
         A2=C2/dt+1/R5+1/R3; 
         T_in=A1/A2; 
       
        Tp(surface_id, i_time+3) = Ground_tem; 
        Tp_interior(surface_id,i_time+3)=T_in;       
   end
   
   Q_flux =  hc * A *(T_in-T_space);  
   IS_record(surface_id,i_time+1) = Is; 
   Solar_win(surface_id,i_time+1)=Transmitted_win;
end 