%% deal with interiorfloor surface, which acts as a floor instead of a top
function [Q_floor,Tp,Tp_interior] = getFloor_heat(i_surface,G_space,T_space,R3,C,Infor_space_simp,Tp,Tp_interior,i_time,i_space,A,Infor_surface_simp)
% global  Infor_surface Tp Tp_interior...
% i_time i_space

dt=3600;
Tp_interior(i_surface, 2)= i_space ;
Ground_tem = T_space-2;
%disp([' ', num2str(C)])
if  strncmp(Infor_surface_simp(1, i_surface).Name,'B',1)  % for "bottom" surface, it has two adjacent spaces with the same name.
    %disp([' ', num2str(Infor_surface_simp(1, i_surface).Name)])
    hc1 = 0.948 ; % assume it is reduced convection T_space1>T2
    R5 = 1/hc1;
    
    A1=C/dt*Tp_interior(i_surface,i_time+2)+T_space/R5+Ground_tem/R3+G_space;
    A2=C/dt+1/R5+1/R3;
    T_in=A1/A2;
    %disp([' ', num2str(T_in)])
    
    if T_space < T_in
        hc1 = 4.04;
        R5 = 1/hc1;
        A1=C/dt*Tp_interior(i_surface,i_time+2)+T_space/R5+Ground_tem/R3+G_space;
        A2=C/dt+1/R5+1/R3;
        T_in=A1/A2;
    end
    
    T_out = Ground_tem;
    
else  % strncmp(Infor_surface_simp(1, i_surface).Name,'T',1)   % Intermediate Floor
    
    C2=C/2;
    C4=C/2;
    
    
    % the another side's space name
    Space_id2 = Infor_surface_simp(1, i_surface).RelatedSpace(1,1);
    if Space_id2 == i_space
        Space_id2 = Infor_surface_simp(1, i_surface).RelatedSpace(1,2);
    end
    
    
    T_space =  Infor_space_simp(1, i_space).SpaceTemp;
    T_space2 =  Infor_space_simp(1, Space_id2).SpaceTemp;
    
    
    hc1 = 0.948;   % T_space >T_in
    hc2 = 4.04 ;  % T_space >T_out
    R5 = 1/hc2;
    R1= 1/hc1;
    
    % T_in is the interior surface temperature in the space that we pick.
    T_in = (C4*Tp(i_surface, i_time+2)/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*Tp_interior(i_surface, i_time+2)/dt+T_space/R1+G_space)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
    T_out = (C2*Tp_interior(i_surface, i_time+2)/dt+T_space/R1+(C2/dt+1/R3+1/R1)*(C4*Tp(i_surface, i_time+2)/dt+T_space2/R5)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
    %disp([' ', num2str(T_in)])
    if T_in > T_space && T_out > T_space2
        hc1 = 4.04 ;
        hc2 = 0.948 ;
        R5 = 1/hc2;
        R1= 1/hc1;
        
        % T_in is the interior surface temperature in the space that we pick.
        T_in = (C4*Tp(i_surface, i_time+2)/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*Tp_interior(i_surface, i_time+2)/dt+T_space/R1+G_space)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
        T_out = (C2*Tp_interior(i_surface, i_time+2)/dt+T_space/R1+(C2/dt+1/R3+1/R1)*(C4*Tp(i_surface, i_time+2)/dt+T_space2/R5)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
        %disp([' one ', num2str(T_in)])
    elseif T_in > T_space && T_out < T_space2
        hc1 = 4.04 ;
        hc2 = 4.04 ;
        R5 = 1/hc2;
        R1= 1/hc1;
        
        % T_in is the interior surface temperature in the space that we pick.
        T_in = (C4*Tp(i_surface, i_time+2)/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*Tp_interior(i_surface, i_time+2)/dt+T_space/R1+G_space)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
        T_out = (C2*Tp_interior(i_surface, i_time+2)/dt+T_space/R1+(C2/dt+1/R3+1/R1)*(C4*Tp(i_surface, i_time+2)/dt+T_space2/R5)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
        %disp([' two ', num2str(T_in)])
    else  % T_in < T_space && T_out > T_space2;
        hc1 = 0.948 ;
        hc2 = 0.948;
        R5 = 1/hc2;
        R1= 1/hc1;
        
        % T_in is the interior surface temperature in the space that we pick.
        T_in = (C4*Tp(i_surface, i_time+2)/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*Tp_interior(i_surface, i_time+2)/dt+T_space/R1+G_space)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
        T_out = (C2*Tp_interior(i_surface, i_time+2)/dt+T_space/R1+(C2/dt+1/R3+1/R1)*(C4*Tp(i_surface, i_time+2)/dt+T_space2/R5)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
        %disp([' three ', num2str(T_in)])
    end
end


Q_floor =  hc1 * A *(T_in-T_space);
Tp(i_surface, i_time+3) = T_out;
Tp_interior(i_surface, i_time+3) = T_in;

%disp(['Q_floor: ',num2str(A)]);

end

