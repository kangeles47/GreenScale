function [Q_floor] = getFloor_heat(surface_id,G_space,T_space,R3,C)
global  Infor_surface Tp Tp_interior... 
       Ground_tem i_time Infor_space i_space

        dt=3600;
        A = Infor_surface{8, surface_id};   
        C2 = C/2; 
        Tp_interior(surface_id, 2)= i_space ; 
        
        if  strncmp(Infor_surface{1, surface_id},'B',1)  % for "bottom" surface, it has two adjacent spaces with the same name.

           hc1 = 0.948 ; % assume it is reduced convection T_space1>T2        
           R5 = 1/hc1;  
           
           A1=C2/dt*Tp_interior(surface_id,i_time+2)+T_space/R5+Ground_tem/R3+G_space; 
           A2=C2/dt+1/R5+1/R3; 
           T_in=A1/A2; 
      
        if T_space < T_in
          hc1 = 4.04; 
          R5 = 1/hc1;  
          A1=C2/dt*Tp_interior(surface_id,i_time+2)+T_space/R5+Ground_tem/R3+G_space; 
          A2=C2/dt+1/R5+1/R3;
          T_in=A1/A2;  
        end
        
          T_out = Ground_tem; 
        
        else strncmp(Infor_surface{1, surface_id},'T',1)  % Intermediate Floor
            
        C2=C/2;
        C4=C/2; 
             
        h_space = getHeight_space_floor(i_space); 
        h_surface = getHeight_surface(surface_id);
       
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

         % compare the space's floor height with the "interior surface" 's
         % Z coornidate; 
         if  h_space == h_surface     % if the interiorfloor is the space's floor
                           hc1 = 0.948;   % T_space >T_in 
               hc2 = 4.04 ;  % T_space >T_out 
               R5 = 1/hc2; 
               R1= 1/hc1;
               
         % T_in is the interior surface temperature in the space that we pick.  
         T_in = (C4*Tp(surface_id, i_time+2)/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*Tp_interior(surface_id, i_time+2)/dt+T_space/R1+G_space)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
         T_out = (C2*Tp_interior(surface_id, i_time+2)/dt+T_space/R1+(C2/dt+1/R3+1/R1)*(C4*Tp(surface_id, i_time+2)/dt+T_space2/R5)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);

         
             if T_in > T_space && T_out > T_space2
             hc1 = 4.04 ;
             hc2 = 0.948 ; 
             R5 = 1/hc2; 
             R1= 1/hc1;
               
         % T_in is the interior surface temperature in the space that we pick.  
         T_in = (C4*Tp(surface_id, i_time+2)/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*Tp_interior(surface_id, i_time+2)/dt+T_space/R1+G_space)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
         T_out = (C2*Tp_interior(surface_id, i_time+2)/dt+T_space/R1+(C2/dt+1/R3+1/R1)*(C4*Tp(surface_id, i_time+2)/dt+T_space2/R5)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
         
             elseif T_in > T_space && T_out < T_space2
             hc1 = 4.04 ;
             hc2 = 0.948 ; 
             R5 = 1/hc2; 
             R1= 1/hc1;
               
         % T_in is the interior surface temperature in the space that we pick.  
         T_in = (C4*Tp(surface_id, i_time+2)/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*Tp_interior(surface_id, i_time+2)/dt+T_space/R1+G_space)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
         T_out = (C2*Tp_interior(surface_id, i_time+2)/dt+T_space/R1+(C2/dt+1/R3+1/R1)*(C4*Tp(surface_id, i_time+2)/dt+T_space2/R5)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
         
             else  T_in < T_space && T_out > T_space2;
             hc1 = 0.948 ;
             hc2 = 0.948; 
             R5 = 1/hc2; 
             R1= 1/hc1;
               
         % T_in is the interior surface temperature in the space that we pick.  
         T_in = (C4*Tp(surface_id, i_time+2)/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*Tp_interior(surface_id, i_time+2)/dt+T_space/R1+G_space)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
         T_out = (C2*Tp_interior(surface_id, i_time+2)/dt+T_space/R1+(C2/dt+1/R3+1/R1)*(C4*Tp(surface_id, i_time+2)/dt+T_space2/R5)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
             end
         end 
        end 
        
         Q_floor =  hc1 * A *(T_in-T_space);  
         Tp(surface_id, i_time+3) = T_out; 
         Tp_interior(surface_id, i_time+3) = T_in; 
        
end 

        