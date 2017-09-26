function Z_space_floor = getHeight_space_floor(i_space)
global Infor_space 

   le = length(Infor_space{4,i_space}.PolyLoop.CartesianPoint ); 
    a_data = zeros(le,1);
    for i =1:le
        a_data(i) = Infor_space{4,i_space}.PolyLoop.CartesianPoint(i, 1).Coordinate{1, 3} ;       
    end 
     Z_space_floor = 0.5*(max(a_data)+min(a_data))*0.3048;

end 


    