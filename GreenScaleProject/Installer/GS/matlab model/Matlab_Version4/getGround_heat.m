function  [Q_floor,Tp,Tp_interior] = getGround_heat(i_surface,G_space,T_space,R3,C,Tp,Tp_interior,i_time,i_space,A)
% global Tp Tp_interior... 
%        Ground_tem i_time  i_space Infor_surface
        
        Tp_interior(i_surface, 2)= i_space ; 
        dt=3600;
        hc = 0.948 ; % assume it is reduced convection T_space1>T2 
        R5 = 1/(hc); 
        
        A1=C/dt*Tp_interior(i_surface,i_time+2)+T_space/R5+Ground_tem/R3+G_space; 
        A2=C/dt+1/R5+1/R3; 
        T_in=A1/A2; 
      
        if T_space < T_in
          hc = 4.04; 
          R5 = 1/hc;  
          A1=C/dt*Tp_interior(i_surface,i_time+2)+T_space/R5+Ground_tem/R3+G_space; 
          A2=C/dt+1/R5+1/R3;
          T_in=A1/A2;  
        end
        
        Tp(i_surface, i_time+3) = Ground_tem; 
        Tp_interior(i_surface,i_time+3)=T_in; 
        Q_floor =  hc * A *(T_in-T_space);  
        
end 