function [R3,C]=getR3(surface_id)

global Infor_surface coef

 C=0; 
 [U] = getU_surface_e(surface_id);  
 A_nowin = getA_surface_noWindow(surface_id);
 A = getA_surface(surface_id);

% if there is door there, the U value need to be recalculated
if isstruct(Infor_surface{5,surface_id})  
     Num_openning = length(Infor_surface{5,surface_id});
     
       for i_openning = 1:Num_openning  
                
         if strcmp(Infor_surface{5, surface_id}(i_openning,1).ATTRIBUTE.openingType, 'NonSlidingDoor')         
          [U_openning,C0] = getU_opening(surface_id,i_openning);   
          C = C+1/C0; 
         end            
       end 
       
    [U1,C1]= getU_surface(surface_id); 
     C=C+1/C1; 
     C=1/C;
       
 else % no openning         
     [U,C]= getU_surface(surface_id);    
       
end

R3=1/(U); 
C=coef*C*A_nowin/A;

end 