%***********************************

% Loop in each space 

%***********************************

function [Q_space,G_space] = HeatFlux_space()
global Infor_surface Num_surface Space_name Tp_interior i_time

G_space = 0; 
Q_space = 0; 


%For each space, judge first which surfaces belonging to this space and
%calculate the corresponding heat flux 

for i_surface = 1:Num_surface     
        if length(Infor_surface{2,i_surface}) == 1
           
            if strcmp(Infor_surface{2, i_surface}.ATTRIBUTE.spaceIdRef,Space_name)
                
               [Q_surface,G_window,T2] = Heatflux_surface(i_surface); 
               Tp_interior (i_surface,i_time+1)=T2; 
               Q_space = Q_space+Q_surface;  
               G_space = G_space + G_window ; 
            end         
                   
        elseif length(Infor_surface{2,i_surface}) == 2 
        
            if strcmp(Infor_surface{2, i_surface}(1, 1).ATTRIBUTE.spaceIdRef,Space_name) ...
                    || strcmp(Infor_surface{2, i_surface}(2, 1).ATTRIBUTE.spaceIdRef,Space_name)
                
               [Q_surface,G_window] = Heatflux_surface(i_surface);  
               Q_space = Q_space+Q_surface; 
               G_space = G_space + G_window ; 
               
            end 
                        
        else length(Infor_surface{2,i_surface})== 3  
            printf('Suppose the adjacent spaces are less than 3');
        end 
            
end 

  if Q_space >0
           Q_space = Q_space - G_space;    % need heating 
   else 
           Q_space = abs(Q_space) + G_space ;   % need cooling 
   end 


end 

