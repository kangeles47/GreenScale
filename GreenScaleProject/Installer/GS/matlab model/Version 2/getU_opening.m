%***********************************

% Get the U value of opennings except windows  
  
%***********************************

function [U,C] = getU_opening(surface_id,opening_id)
% Get  U value of each opening. Doors and windows are different 
 global Infor_surface Num_cons Infor_cons
   
if strcmp(Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.openingType, 'NonSlidingDoor')
    
    Name_cons=Infor_surface{5, surface_id}(opening_id,1).ATTRIBUTE.constructionIdRef;  
     
     for i_cons=1:Num_cons
        
        if  strcmp(Infor_cons{6, i_cons}.id,Name_cons)
            U=Infor_cons{2, i_cons}.CONTENT;     % w/m2.k
            C = Infor_cons{8, i_cons};
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



