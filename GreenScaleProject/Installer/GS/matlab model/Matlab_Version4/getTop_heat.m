% for a interiorfloor which is a top of the space, the transmitted solar energy of another
% side also need to be calculated

function [Q_top,Tp,Tp_interior] = getTop_heat(i_surface,T_space,R3,C,A,Infor_surface_simp,Tp,Tp_interior,i_space,i_time,G_space_record,Infor_space_simp)
% global  Infor_surface Tp Tp_interior...
%         i_time Infor_space i_space

dt = 3600;
C2 = C/2;
C4 = C/2;
Tp_interior(i_surface, 2)= i_space ;

%% to make the InteriorWall and InteriorFloor use the correct temperature information, A1 and A2 are used to exchanged every timestep
A1=Tp(i_surface, i_time+2);
A2=Tp_interior(i_surface, i_time+2);
%disp([' ', num2str(A2)])
%disp([' ', num2str(A1)])
%disp([' ', num2str(C)])

% the another side's space name
Space_id2 = Infor_surface_simp(1, i_surface).RelatedSpace(1,1);
if Space_id2 == i_space
    Space_id2 = Infor_surface_simp(1, i_surface).RelatedSpace(1,2);
end


Transmitted_space = G_space_record(Space_id2,i_time);
T_space2 = Infor_space_simp(1, Space_id2).SpaceTemp;
%disp([' ', num2str(Transmitted_space)])

%%
hc1 = 4.04;   % T_space >T_in
hc2 = 0.948 ;  % T_space >T_out
R5 = 1/hc2;
R1= 1/hc1;

%disp([' ', num2str((C2*A1/dt+T_space/R1)*R3)])
% T_in is the interior surface temperature in the space that we pick.
T_in = (Transmitted_space+C4*A2/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*A1/dt+T_space/R1)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
T_out = ((C2/dt+1/R1+1/R3)*T_in-C2/dt*A1-T_space/R1)*R3;
%disp([' ', num2str(T_in)])


if T_in > T_space && T_out > T_space2
    hc1 = 0.948 ;
    hc2 = 4.04 ;
    R5 = 1/hc2;
    R1= 1/hc1;
    % T_in is the interior surface temperature in the space that we pick.
    T_in = ( Transmitted_space+C4*A2/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*A1/dt+T_space/R1)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
    T_out = ((C2/dt+1/R1+1/R3)*T_in-C2/dt*A1-T_space/R1)*R3;
    %disp([' ', num2str(Transmitted_space)])
    %disp([' one ', num2str(T_space)])
    %disp([' one ', num2str(T_space2)])
    %disp([' one ', num2str(T_out)])
    %disp([' one ', num2str(T_in)])
elseif T_in > T_space && T_out < T_space2
    hc1 = 0.948 ;
    hc2 = 0.948 ;
    R5 = 1/hc2;
    R1= 1/hc1;
    
    % T_in is the interior surface temperature in the space that we pick.
    T_in = ( Transmitted_space+C4*A2/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*A1/dt+T_space/R1)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
    T_out = ((C2/dt+1/R1+1/R3)*T_in-C2/dt*A1-T_space/R1)*R3;
    %disp([' two ', num2str(T_space)])
    %disp([' two ', num2str(T_space2)])
    %disp([' two ', num2str(T_out)])
    %disp([' two ', num2str(T_in)])
else  %T_in < T_space && T_out > T_space2;
    hc1 = 4.04 ;
    hc2 = 4.04;
    R5 = 1/hc2;
    R1= 1/hc1;
    
    % T_in is the interior surface temperature in the space that we pick.
    T_in = ( Transmitted_space+C4*A2/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*A1/dt+T_space/R1)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
    T_out = ((C2/dt+1/R1+1/R3)*T_in-C2/dt*A1-T_space/R1)*R3;
    %disp([' three ', num2str(T_space)])
    %disp([' three ', num2str(T_space2)])
    %disp([' three ', num2str(T_out)])
    %disp([' three ', num2str(T_in)])
end

Tp(i_surface, i_time+3) = T_out;
Tp_interior(i_surface, i_time+3) = T_in;

Q_top =  hc1 * A *(T_in-T_space);

%disp([' ', num2str(T_in)])
end