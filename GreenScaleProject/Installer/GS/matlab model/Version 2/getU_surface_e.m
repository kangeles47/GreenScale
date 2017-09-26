function [U] = getU_surface_e(surface_id)

global  Infor_surface  

[A] = Infor_surface{8, surface_id};
[A_noOpenning] = Infor_surface{9, surface_id};
UA = 0; 
UA_win=0;

if isstruct(Infor_surface{5,surface_id})  

 Num_openning = length(Infor_surface{5,surface_id});
     
       for i_openning = 1:Num_openning 
                 
          % if the openning is window, there is tansmitted energy 
           if strcmp(Infor_surface{5, surface_id}(i_openning,1).ATTRIBUTE.openingType, 'OperableWindow')|| strcmp(Infor_surface{5, surface_id}(i_openning,1).ATTRIBUTE.openingType,'FixedWindow' )             
             U_win = getU_win(surface_id,i_openning);     
            A_openning = Infor_surface{5, surface_id}(i_openning,1).RectangularGeometry.Height*0.3048*Infor_surface{5, surface_id}(i_openning,1).RectangularGeometry.Width*0.3048;         
            UA_win = UA_win + U_win*A_openning;
          
              % if the openning is door     
           else strcmp(Infor_surface{5, surface_id}(i_openning,1).ATTRIBUTE.openingType, 'NonSlidingDoor')        
           A_openning = Infor_surface{5, surface_id}(i_openning,1).RectangularGeometry.Height*0.3048*Infor_surface{5, surface_id}(i_openning,1).RectangularGeometry.Width*0.3048; 
           U_openning = getU_opening(surface_id,i_openning);
           UA = UA + U_openning*A_openning;                       
           end 
           
       end 
       
       [U1]= getU_surface(surface_id); 
       UA = UA + U1*A_noOpenning + UA_win; % the equvalent conductivity of the whole surface wall including the window, door and wall is calculated;
       U = UA/A;   
  
 else % no openning    
       [U]= getU_surface(surface_id);    
end

end 