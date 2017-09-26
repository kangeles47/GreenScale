function Q_floor = getGround_heat(surface_id,G_space,T_space,R3,C)
global Tp Tp_interior... 
       Ground_tem i_time  i_space Infor_surface
        
        A = Infor_surface{8, surface_id};
        Tp_interior(surface_id, 2)= i_space ; 
        dt=3600;
        hc = 0.948 ; % assume it is reduced convection T_space1>T2 
        R5 = 1/(hc); 
        
        C2 = C/2; 
        A1=C2/dt*Tp_interior(surface_id,i_time+2)+T_space/R5+Ground_tem/R3+G_space; 
        A2=C2/dt+1/R5+1/R3; 
        T_in=A1/A2; 
      
        if T_space < T_in
          hc = 4.04; 
          R5 = 1/hc;  
          A1=C2/dt*Tp_interior(surface_id,i_time+2)+T_space/R5+Ground_tem/R3+G_space; 
          A2=C2/dt+1/R5+1/R3;
          T_in=A1/A2;  
        end
        
        Tp(surface_id, i_time+3) = Ground_tem; 
        Tp_interior(surface_id,i_time+3)=T_in; 
        Q_floor =  hc * A *(T_in-T_space);  
        
end 