function  Q_flux = getRaisedFloor_heat(surface_id,G_space) 
global  Tp Tp_interior T_outside_temp ... 
        i_time Infor_space Num_space Space_name
    
        Z_surface = getHeight_surface(surface_id); 
        [hc_external] = get_hc_external(Z_surface,Az_surface);
        dt=3600;
        A = getA_surface(surface_id); 
        G_space = G_space/A; 
        
    for i_space = 1:Num_space
     if strcmp(Infor_space{8,i_space}.id, Space_name)
       T_space1 = Infor_space{9, i_space}; 
       break; 
     end 
    end 
         hc = 4.04 ; % assume it is reduced convection T_space1 <T2 
    
         R5 = 1/(hc); 
         R1 = 1/hc_external; 
 
         [R3,C,Transmitted_win,Is] = Equivalent_value(surface_id); 
         C2 = C/2; 
         C4 = C/2; 
         
         M1=C2/dt+1/R1+1/R3; 
         M2=C2/dt*Tp(surface_id,i_time+2) + T_outside_temp/R1+Alph_opaque*Is; 
         M3=C4/dt+1/R3+1/R5; 
         M4=C4/dt*Tp_interior(surface_id,i_time+2)+T_space1/R5+G_space;
         
         T1= (M4*R3+M3*M2*R3^2)/(M3*M1*R3^2-1); % T1 is the exterior surface's temperature 
         T2= (M1*T1-M2)*R3;                     % T2 is the interior surface's temperature       
         
         if T_space1 > T2
             
         hc = 0.948;         
         R5 = 1/(hc); 
          
         M1=C2/dt+1/R1+1/R3; 
         M2=C2/dt*Tp(surface_id,i_time+2) + T_outside_temp/R1+Alph_opaque*Is; 
         M3=C4/dt+1/R3+1/R5; 
         M4=C4/dt*Tp_interior(surface_id,i_time+2)+T_space1/R5+G_space;
         
         T1= (M4*R3+M3*M2*R3^2)/(M3*M1*R3^2-1); % T1 is the exterior surface's temperature 
         T2= (M1*T1-M2)*R3;                    % T2 is the interior surface's temperature
         
         end 

       Tp(surface_id, i_time+3) = T1; 
       Tp_interior(surface_id, i_time+3) = T2; 
       Q_flux =  hc * A *(T2-T_space1); 
       
        %% store the space name to each surface's side temperature 
        if i_time == 1  % store only one time 
            str = Space_name ; 
            par_cell=regexp(str,',','split');
            Tp_interior(surface_id, 2)= str2double(par_cell{1,2}) ; 
        end 
end 