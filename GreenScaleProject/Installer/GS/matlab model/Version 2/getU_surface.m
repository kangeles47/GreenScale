function [U] = getU_surface(surface_id)
global Infor_surface Num_cons Infor_cons

if strncmp(Infor_surface{1, surface_id},'X',1) 
    U = 0 ; 
else
Name_cons = Infor_surface{7,surface_id}.constructionIdRef; 

for i_cons = 1:Num_cons
        
        if strcmp(Infor_cons{6, i_cons}.id,Name_cons)
            
            U = Infor_cons{2, i_cons}.CONTENT;  
            break;
            
        end
        
end
   

end

end 