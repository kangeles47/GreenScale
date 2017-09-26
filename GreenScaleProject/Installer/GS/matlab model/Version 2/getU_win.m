function U_win=getU_win(surface_id,openning_id)
 global Num_win Infor_surface Infor_win  
 
%  if isempty(Infor_surface{5, 1}) 
 
 Name_cons = Infor_surface{5, surface_id}(openning_id,1).ATTRIBUTE.windowTypeIdRef; 
    
    for i_win=1:Num_win
         
        if strcmp(Infor_win{6, i_win}.id,Name_cons )
            
            U_win = Infor_win{3, i_win}.CONTENT; 
            break; 
        end
        
    end
%  else 
%      U_win = 0 ; 
%  end
end 