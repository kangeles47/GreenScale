% get the equivalent C value for the surface (including door and wall but not window)

function C = getC_surface(surface_id)
global Infor_surface Num_cons Infor_cons Coef 
A = Infor_surface{8, surface_id};
A_noOpenning = Infor_surface{9, surface_id};
C = 0; 

if strncmp(Infor_surface{1, surface_id},'X',1) 
    C_wall = 0 ; 
else
    Name_cons = Infor_surface{7,surface_id}.constructionIdRef;

for i_cons = 1:Num_cons
        
        if strcmp(Infor_cons{6, i_cons}.id,Name_cons)
            
            C_wall = Infor_cons{8, i_cons};  % the surface wall 
            break;
            
        end
        
end
end 

if isstruct(Infor_surface{5,surface_id}) 
 Num_openning = length(Infor_surface{5,surface_id});
   for i_openning = 1:Num_openning 
                 
          % if the openning is window, there is tansmitted energy 
        if strcmp(Infor_surface{5, surface_id}(i_openning,1).ATTRIBUTE.openingType, 'NonSlidingDoor')                 
            A_openning = Infor_surface{5, surface_id}(i_openning,1).RectangularGeometry.Height*0.3048*Infor_surface{5, surface_id}(i_openning,1).RectangularGeometry.Width*0.3048; 
            Door_cons = Infor_surface{5, surface_id}.ATTRIBUTE.constructionIdRef; 
          
           for i_cons = 1:Num_cons
             if strcmp(Infor_cons{6, i_cons}.id,Door_cons)  
           Door_C = Infor_cons{8, i_cons};  % the surface wall 
            break;            
             end
           end
           
           C = C +1/(A_openning*Door_C); 
           C=0;
        else 
            C = 0; 
         end 
           
   end
   C = 1/(C_wall*A_noOpenning) + C; 
   C=1/C/A; 
   
%      C = C_wall;
else
    C = C_wall; 
end 
C=Coef*C;

end 