%***********************************

% Get the Solar Transmittance and absorbtance for the windows 
  
%***********************************

function [ SHGC] = getSHGC_win(surface_id,opening_id)  

 global Num_win Infor_surface Infor_win  
 
 Name_cons=Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.windowTypeIdRef; 
    
    for i_win=1:Num_win
         
        if strcmp(Infor_win{6, i_win}.id,Name_cons )
           
            SHGC = Infor_win{4, i_win}(7, 1).CONTENT ;          

            break; 
        end
        
    end 

end 
