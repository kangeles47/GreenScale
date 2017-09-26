% for a top roof / interiorfloor, the transmitted solar energy of another
% side also need to be calculated 

function [Q_top] = getTop_heat(surface_id,T_space,R3,C)
global  Infor_surface Tp Tp_interior... 
        i_time Infor_space i_space

        dt=3600;
        Transmitted_space2 = 0;
        A = Infor_surface{8, surface_id};   
        C2 = C/2;
        Tp_interior(surface_id, 2)= i_space ; 

       C4=C/2; 
%        h_space = Infor_space{10,i_space};  
%        h_surface = Infor_surface{13,surface_id};
       
     % the another side's space name 
         str = Infor_surface{2, surface_id}(2, 1).ATTRIBUTE.spaceIdRef; 
         par_cell = regexp(str,'-','split');
         Space_id2 = str2double(par_cell{1,2});
         
        if Space_id2 == i_space 
         str = Infor_surface{2, surface_id}(1, 1).ATTRIBUTE.spaceIdRef; 
         par_cell = regexp(str,'-','split');
         Space_id2 = str2double(par_cell{1,2});
        end 
         
        %%%% Space_id2 's solar transmitted energy (only consider exterior walls)
         Length_Bounding = length(Infor_space{7,Space_id2}); 
         Space_surface2 = zeros(Length_Bounding,1); 
 
        for i = 1:Length_Bounding 
        str = Infor_space{7, Space_id2}(i, 1).ATTRIBUTE.surfaceIdRef ; 
        par_cell = regexp(str,'-','split');
       Space_surface2(i) = str2double(par_cell{1,2}) ;  % store surface order number in each "Space_surface"
        end 
 

      for surface_order = 1:Length_Bounding   
       i_surface = Space_surface2(surface_order);
       Surface_type = Infor_surface{7, i_surface}.surfaceType;
         if  strcmp(Surface_type,'ExteriorWall')
        [Transmitted_win2,Is] = getTransmitted_solar(surface_id); 
        Transmitted_space2 = Transmitted_space2 + Transmitted_win2;  
         end
      end 
      Transmitted_space2 =1 *Transmitted_space2/A;  % 80% solar transmitted energy is heating the floor 
        %%%
        
      
         T_space2 = Infor_space{9, Space_id2};

         % compare the space's floor height with the "interior surface" 's
         % Z coornidate; 
       % h_surface > h_space ;     % if the interiorfloor is the space's ceiling / roof 
      %%       
               hc1 = 4.04;   % T_space >T_in 
               hc2 = 0.948 ;  % T_space >T_out 
               R5 = 1/hc2; 
               R1= 1/hc1;
               
         % T_in is the interior surface temperature in the space that we pick.  
          T_in = ( Transmitted_space2+C4*Tp(surface_id, i_time+2)/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*Tp_interior(surface_id, i_time+2)/dt+T_space/R1)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
          T_out = ((C2/dt+1/R1+1/R3)*T_in-C2/dt*Tp_interior(surface_id, i_time+2)-T_space/R1)*R3;
         
             if T_in > T_space && T_out > T_space2
             hc1 = 0.948 ;
             hc2 = 4.04 ; 
             R5 = 1/hc2; 
             R1= 1/hc1;
               
         % T_in is the interior surface temperature in the space that we pick.  
          T_in = ( Transmitted_space2+C4*Tp(surface_id, i_time+2)/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*Tp_interior(surface_id, i_time+2)/dt+T_space/R1)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
          T_out = ((C2/dt+1/R1+1/R3)*T_in-C2/dt*Tp_interior(surface_id, i_time+2)-T_space/R1)*R3;
         
             elseif T_in > T_space && T_out < T_space2
             hc1 = 0.948 ;
             hc2 = 0.948 ; 
             R5 = 1/hc2; 
             R1= 1/hc1;
               
         % T_in is the interior surface temperature in the space that we pick.  
          T_in = ( Transmitted_space2+C4*Tp(surface_id, i_time+2)/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*Tp_interior(surface_id, i_time+2)/dt+T_space/R1)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
          T_out = ((C2/dt+1/R1+1/R3)*T_in-C2/dt*Tp_interior(surface_id, i_time+2)-T_space/R1)*R3;
             else  T_in < T_space && T_out > T_space2;
             hc1 = 4.04 ;
             hc2 = 4.04; 
             R5 = 1/hc2; 
             R1= 1/hc1;
               
         % T_in is the interior surface temperature in the space that we pick.  
         T_in = ( Transmitted_space2+C4*Tp(surface_id, i_time+2)/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*Tp_interior(surface_id, i_time+2)/dt+T_space/R1)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
         T_out = ((C2/dt+1/R1+1/R3)*T_in-C2/dt*Tp_interior(surface_id, i_time+2)-T_space/R1)*R3;
             end                        
       
          
         Q_top =  hc1 * A *(T_in-T_space);  
         Tp(surface_id, i_time+3) = T_out; 
         Tp_interior(surface_id, i_time+3) = T_in;      
end 