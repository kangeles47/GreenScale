%***********************************

% Get the Solar Transmittance and absorbtance for the windows 
  
%***********************************

function [ Ts , Alph] = getTs_win(surface_id,opening_id)  

 global Num_win Infor_surface Infor_win  
 
 Name_cons=Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.windowTypeIdRef; 
    
    for i_win=1:Num_win
         
        if strcmp(Infor_win{6, i_win}.id,Name_cons )
           
            SHGC = Infor_win{4, i_win}(7, 1).CONTENT ;          
            
        end
        
    end 

[U] = getU_opening(surface_id,opening_id)  % get the U_value of window.  

if U > 4.5
    
    if SHGC < 0.7206 
        Ts =(0.939998*SHGC^2)+0.20332*SHGC ; 
    else 
        Ts = 1.30415*SHGC-0.30515; 
    end 
elseif U < 3.4 
     if SHGC > 0.15
        Ts = 0.085775*SHGC^2+0.963954*SHGC-0.084958; 
    else 
        Ts = 0.41040*SHGC; 
    end 
    
else  % U : 3.4~4.5 
    
    % single window 
     if SHGC < 0.7206 
        Ts1 =(0.939998*SHGC^2)+0.20332*SHGC ; 
    else 
        Ts1 = 1.30415*SHGC-0.30515; 
     end   
    % double window
     if SHGC > 0.15
        Ts2 = 0.085775*SHGC^2+0.963954*SHGC-0.084958; 
    else 
        Ts2 = 0.41040*SHGC; 
     end 
     
     Ts = Ts2 +(Ts1-Ts2)*(3.5-4.5)/(U-4.5) ; 
    
     
end 

Alph = SHGC - Ts; 
 

end 
