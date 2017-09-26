%***********************************

% Get the U value of opennings 
  
%***********************************

function [U] = getU_opening(surface_id,opening_id)
% Get  U value of each opening. Doors and windows are different 
 global Num_win Infor_surface Infor_win Num_cons Infor_cons
 
if strcmp(Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.openingType, 'OperableWindow')
    Name_cons=Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.windowTypeIdRef; 
    
    for i_win=1:Num_win
         
        if strcmp(Infor_win{6, i_win}.id,Name_cons )
            U=Infor_win{3, i_win}.CONTENT; 
        end
        
    end 
    
    
elseif strcmp(Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.openingType, 'NonSlidingDoor')
    
    Name_cons=Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.constructionIdRef;  
     
     for i_cons=1:Num_cons
        
        if  strcmp(Infor_cons{6, i_cons}.id,Name_cons)
            U=Infor_cons{2, i_cons}.CONTENT;     % w/m2.k
        end
        
    end 

    
elseif strcmp(Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.openingType,'OperableSkylight')
        printf('Not available'); 
        
elseif strcmp(Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.openingType,'FixedWindow' )
        printf('Not available'); 
        
elseif strcmp(Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.openingType, 'Air')
        printf('Not available'); 
        
end


end 



