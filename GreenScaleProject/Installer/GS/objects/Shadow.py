#-------------------------------------------------------------------------------
# Name:        Shadow.py
# Purpose:     Green Scale Tool TM Shadow Module (handles shadow calculations for a surface)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
import logging
import math
from objects.BaseElement import BaseElement
from numpy import *
import scipy
import scipy.linalg
import numpy
from numpy import matrix
from numpy import linalg
#import Polygon #commented so that we can run GreenScale without Shadow calcs
from GSUtility import GSUtility
#import Polygon.IO #commented so that we can run GreenScale without Shadow calcs
# Recheck shade + exterior is included in set
# Check overall structure
# Check pictures
# Check area substitution
# Overall areas...to finish
# Command Line


class Shadow(BaseElement):
    # Cartesian point
    # Double check the dots function multip/div   "./" for example
    # Also check through each to match operators used and :: operations
    # Also that the weather is being used in Radians...
    # All of the coordinates passed in via the tree values are in meters (cps*0.3048)-same as in Matlab version
    cartesian_point = None
    svg = 1

    def shadowsSection(self, surface, azi_sun_rad, tilt_sun_rad, nsd, shadow_record, shade_surf_list, surfaces_dict):
        # Calculate the shaded area on the surface, including calculations for over-shading regions
        # Output:  Ashadow_wo_win == Area of shadow on receiving surface, but not windows [m^2]
        #          Ashadow_win    == Area of shadow on each windows [m^2]
        #          Ashadow        == Area of shadow on receiving surface included windows [m^2]
        #          x_rec_rad      == x value of the receiving surface (current surface) in radians
        # Get surface information to use:

        X_rec = surface.cps  # [4][3] set of coordinates of surface
        azi_rec_rad = (surface.azimuth * math.pi)/180
        tilt_rec_rad = (surface.tilt * math.pi)/180
        A_rec = (surface.height * surface.width * 0.3048 * 0.3048)
        temp2 = mat([]) # Empty matrix for IsEmpty testing below

        #  Get window information for this surface if there is any
        opening_count = 0
        X_win = list()
        A_win = list()

        # Set up the non-door openings with their coordinates and corresponding areas
        open_coor = list()
        open_area = list()
        for opening in surface.openings:
            # Matlab is not including doors at this point, so skipping in the calculations below
            # Glass doors will have to be adjusted for in future iterations...
            # Also, eventually non-square windows will need to be handled
            if opening.obj_type != "NonSlidingDoor":
                opening_count += 1
                #X_win = [4][3]
                X_win = opening.ocps  # [4][3] set of coordinates of opening
                open_coor.append(X_win)
                A_win = (opening.height * opening.width * 0.3048 * 0.3048)
                open_area.append(A_win)

        listof_Xsr_rec = list()  # Appending each returned matrix Xsr_rec of size [4][3]
        Xsr_rec, u1, v1, w1 = self.wc2rc(X_rec, X_rec[0], azi_rec_rad, tilt_rec_rad)  #X1, u1, v1, w1
        #print Xsr_rec
        listof_Xsr_rec.append(Xsr_rec)
        Xcw_rec1, Xcw_rec2, cw_flag = self.poly2cw(Xsr_rec[:, 0], Xsr_rec[:, 1])

        listof_Xsr_win = list()  # Appending each returned matrix Xsr_win of size [4][3]
        listof_Xcw_win1 = list()  #[4][1]
        listof_Xcw_win2 = list()  #[4][1]
        m = 0
        for opening in open_area:
            #if opening > 0:
            # Xsr_win(i_open).C=wc2rc(X_win(i_open).C,X_rec(1,:),azi_rec_rad,tilt_rec_rad);
            Xsr_win, u1, v1, w1 = self.wc2rc(open_coor[m], X_rec[0], azi_rec_rad, tilt_rec_rad)  # Returns 4x3 matrix#   change back to X_win
            listof_Xsr_win.append(Xsr_win)
            # [Xcw_win1(i_open).C,Xcw_win2(i_open).C]=poly2cw_q(Xsr_win(i_open).C(:,1),Xsr_win(i_open).C(:,2));
            Xcw_win1, Xcw_win2, cw_flag = self.poly2cw(Xsr_win[:, 0], Xsr_win[:, 1])
            listof_Xcw_win1.append(Xcw_win1)
            listof_Xcw_win2.append(Xcw_win2)
            m += 1

        #x_nonshading_new = list()
        #y_nonshading_new = list()
        x_nonshading = Xcw_rec1
        y_nonshading = Xcw_rec2
        ag = Xcw_rec1
        ab = Xcw_rec2

        #x_nonshading_w = list()
        #y_nonshading_w = list()
        if opening_count > 0:
            x_nonshading_w = listof_Xcw_win1  # For all the respective openings...sending list of all window matricies Xcw_win1
            y_nonshading_w = listof_Xcw_win2  # For all the respective openings...sending list of all window matricies Xcw_win2
        #print nsd              # INTEGER of the total exterior surfaces PLUS the shade device surfaces stored seperate
        # Matlab is finding here if a surface is exterior or shade, so the two room model ends up considering 16/19 surfaces (= minus interiors)
        #print shade_surf_list  # Is a list of 4 surfaces called "Shade"
        #print shadow_record    # Is a list of the exterior surfaces and roof planes: shadow_record is None for the single model or where there are none
        #print surfaces_dict    # This is a dictionary of all surfaces minus shade devices, including interior surfaces...need to get total of all
        #r = len(shade_surf_list) + len(surfaces_dict)
        #ns = zeros((1, r))
        Shadow_flag = 0
        Shadow_flag_list = list()  # This is being created from an dictionary, problems later could ba an order issue...
        Xshadow0 = mat([])
        Xshadow1 = mat([])
        ordered_surfacesD = dict()
        ordered_surfaces = list()
        #arrayLength = len(surfaces_dict)
        #print "arrayLength = ", arrayLength
        for currentsurface in surfaces_dict:
            ordered_surfaces.append(0)
            Shadow_flag_list.append(0)
        for currentsurface in surfaces_dict:
            sur = surfaces_dict[currentsurface]
            cur_id = sur.obj_id
            h = cur_id[3:]  # Take off "su-"
            newid = int(h)
            ordered_surfaces[newid-1] = sur
        k = 0
        #P1 = P1.sort(key=P1[1])
        cnt = 0
        for currentsurface in ordered_surfaces:  # Matlab doesnt seem to omit interior walls, so using surfaces_dict instead of (shadow_record+shade_surf_list)
            #for surface in shadow_record+shade_surf_list:
            # if Infor_surface_simp(i_surface).Exterior==0
            # else  # to avoid interior walls, but shadow_record already does this only the matlab model still goes through all...?
            #sur = surfaces_dict[currentsurface]
            #su = sur.obj_type
            # Add [0,0,0] to sets that are not square?
            su = currentsurface.obj_type
            if su == "ExteriorWall" or su == "Roof" or su == "Shade":
                #X_cas_cps = surfaces_dict[currentsurface]
                X_cas = currentsurface.cps
                if len(X_cas) == 3:
                    newSet = tuple((0, 0, 0))
                    X_cas.append(newSet)  #X_cas = X_cas.append((0, 0, 0))  # Add row of zeros to the ones with only three rows (roofs), but three should still process correctly
                if X_cas != X_rec:
                    #X_cas is not adding zeros to make square surfaces like Matlab is doing...?
                    #print X_cas
                    Xshadow0, Xshadow1, facesun_flag, Shadow_flag, Xsr_cas, Xsr_cas_new = self.shadow_coordinates(X_cas, X_rec, azi_rec_rad, tilt_rec_rad, azi_sun_rad, tilt_sun_rad)
                    Shadow_flag_list[k] = Shadow_flag
                #else:
                    #Shadow_flag_list.append(0)
            #x_nonshading = x_nonshading1
            # Assuming equal: if Shadow_flag(i_surface) && ~isempty(x_nonshading...altered loop from here for overall below 2 to the left
            if Shadow_flag == 1:
                if x_nonshading == temp2:
                    p = 0
                else:
                    Xcw_shadow1, Xcw_shadow2, cw_flag = self.poly2cw(Xshadow0, Xshadow1)

                    #print "this is passed to polybool"
                    #print x_nonshading
                    #print y_nonshading
                    cnt += 1

                    #This is an example for the first items as from MatLab that are passed to polybool, does not give back all rows needed
                    #x_nonshading = mat([[-3.6195],[-3.6195],[0],[0]])
                    #y_nonshading = mat([[0],[3.0480],[3.0480],[0]])
                    #Xcw_shadow1 = mat([[-3.6195],[-1.8638],[3.2357]])
                    #Xcw_shadow2 = mat([[0],[2.2156],[-2.7439]])

                    x_nonshading, y_nonshading = self.python_polybool(x_nonshading, y_nonshading, Xcw_shadow1, Xcw_shadow2, cnt)
                    Xs = concatenate((x_nonshading,  y_nonshading), 1)
                    #print "Xs" #Left off here from finals (polybool)
                    #print Xs

                    i = 0
                    for opening in open_area:  # This is assuming it means the openings in this surface so use the list of areas made above
                        if opening > 0:
                            cnt += 1
                            #print "in"
                            x_nonshading_w[i], y_nonshading_w[i] = self.python_polybool(x_nonshading_w[i], y_nonshading_w[i], Xcw_shadow1, Xcw_shadow2, cnt)
                        i += 1  #moved this out one
            k += 1
        #Ashadow_win = zeros((len(surfaces_dict)))
        Ashadow_win = list()
        Shadow_flag_sum = 0
        #if opening_count > 0:
            #for opening in surface.openings:  # Assuming this is the surface passed to this module
                #Ashadow_win.append(0)  # array of length number_of_openings initialized to 0s

        #print Shadow_flag_list
        for m in Shadow_flag_list:
            Shadow_flag_sum += m
        #print Shadow_flag_list
        if Shadow_flag_sum > 0:  # or if sum exists
            #i = 0
            x_y_for_polyarea = concatenate((x_nonshading, y_nonshading), 1)
            #print "x_y_for_polyarea: ", x_y_for_polyarea
            Ashadow = (A_rec - (self.polyarea2(x_y_for_polyarea)))  # rounded to -5 in matlab at this point...this is taking one parameter below...may have to combine these two...

            if opening_count > 0:
                j = 0
                for opening in open_area:  # Assuming this is the surface passed to this module
                    #print opening
                    if opening > 0:  # open_area is the list of A_win
                        x_y_for_polyareaWin = concatenate((x_nonshading_w[j],  y_nonshading_w[j]), 1)
                        # Ashadow_win(i_open)=roundn(A_win(i_open)-polyarea_q(x_nonshading_w(i_open).C,y_nonshading_w(i_open).C),-5);
                        current_Ashadow_win = (opening - (self.polyarea2(x_y_for_polyareaWin))) # there are two polyareas below...see which is correct
                        Ashadow_win.append(current_Ashadow_win)
                        #print "this : ", current_Ashadow_win, opening
                        j += 1
                    else:
                        Ashadow_win.append(0)
                        j += 1
            Ashadow_no_win = Ashadow - sum(Ashadow_win)
        else:
            Ashadow = 0
            Ashadow_no_win = 0

        if not Ashadow:
        #if isnan(Ashadow)
            Ashadow = 0
        if not Ashadow_no_win:
        #if isnan(Ashadow_no_win)
            Ashadow_no_win = 0

        #print "Ashadow_no_win", Ashadow_no_win
        #print "Ashadow       ", Ashadow

        return Ashadow_no_win, Ashadow

    def python_polybool(self, x_nonshading, y_nonshading, Xcw_shadow1, Xcw_shadow2, cnt):
        # From http://www.j-raedler.de/tag/polygon/

        rec_surf = concatenate((x_nonshading, y_nonshading), 1)  # Combined x_nonshading and y_nonshading
        x_y_cast = concatenate((Xcw_shadow1, Xcw_shadow2), 1)  # Combined Xcw_shadow1 and Xcw_shadow2
        #print "rec_surf  ", rec_surf

        e = list()
        f = list()

        row = len(rec_surf)
        while row >= 1:
            col = 0
            temp = list()
            temp.append(rec_surf[row-1, col])
            temp.append(rec_surf[row-1, col+1])
            #temp.append(0)
            e.append(temp)
            row -= 1
        row = len(x_y_cast)
        while row >= 1:
            col = 0
            temp2 = list()
            temp2.append(x_y_cast[row-1, col])
            temp2.append(x_y_cast[row-1, col+1])
            #temp.append(0)
            f.append(temp2)
            row -= 1

        #print "e"
        #print e
        #print "f"
        #print f

        a = numpy.array(e)
        A = Polygon.Polygon(a)
        b = numpy.array(f)
        B = Polygon.Polygon(b)
        polybool = A - B
        #Polygon.IO.writeSVG('test.svg', (polybool,), fill_color=((0, 0, 255),))

        #if cnt < 7:
        #    first = str(cnt)
        #    first = first + "aa"
        #    sec = str(cnt)
        #    sec = sec + "bb"
        #    third = str(cnt)
        #    third = third + "cc"
        #    Polygon.IO.writeSVG(first+'.svg', (A,), fill_color=((0, 255, 0),))
        #    Polygon.IO.writeSVG(sec+'.svg', (B,), fill_color=((255, 0, 0),))
        #    Polygon.IO.writeSVG(third+'.svg', (polybool,), fill_color=((0, 0, 255),))

        #polybool = numpy.array(polybool) # Missing (0,0.4029) the repeated last point of the MatLab polybool output
        #polybool_out = Polygon.Polygon(polybool)

        le = len(polybool[0])  # le is the number of points in the new polygon
        row = 0
        x_non = zeros((le, 1))
        y_non = zeros((le, 1))
        while row < le:
            col = 0
            x_non[row] = polybool[0][row][0]
            y_non[row] = polybool[0][row][1]
            row += 1
        #print x_non
        #print y_non


        '''
        Polygon.IO.writeSVG('1_poly.svg', (A,))
        Polygon.IO.writeSVG('2_poly.svg', (B,))
        Polygon.IO.writeSVG('3_poly.svg', (polybool,))

        # MatLab outputs
        m = ((-3.6195, 0), (-3.6195, 3.0480), (0, 3.0480), (0, 0))
        l = numpy.array(m)
        v = Polygon.Polygon(l)
        Polygon.IO.writeSVG('4rec_poly.svg', (v,))

        m = ((-3.6195, 0), (-1.8638, 2.2156), (3.2357, -2.7439))
        l = numpy.array(m)
        v = Polygon.Polygon(l)
        Polygon.IO.writeSVG('4shade_poly.svg', (v,))

        m = ((-3.2376, 4.5706), (-3.6195, 6.0960), (-1.8638, 5.3546), (3.2357, -2.7439))
        l = numpy.array(m)
        v = Polygon.Polygon(l)
        Polygon.IO.writeSVG('4testShade_poly.svg', (v,))

        m = ((0.0, 0.4029), (-1.8638, 2.2156), (-3.6195, 0), (-3.6195, 3.0480), (0,3.0480), (0,0.4029))
        l = numpy.array(m)
        v = Polygon.Polygon(l)
        Polygon.IO.writeSVG('4total_poly.svg', (v,))
        '''

        #q = Polygon.Polygon(((0.0, 0.0), (10.0, 0.0), (10.0, 5.0), (0.0, 5.0)))
        #t = Polygon.Polygon(((1.0, 1.0), (3.0, 1.0), (2.0, 3.0)))
        #a = q - t # gives a rectangle with a triangular hole
        #print "a"
        #print a
        #print Polygon.withNumPy

        #import Polygon
        #import Polygon.IO
        #q = Polygon.Polygon(((0.0, 0.0), (10.0, 0.0), (10.0, 5.0), (0.0, 5.0)))
        #t = Polygon.Polygon(((1.0, 1.0), (3.0, 1.0), (2.0, 3.0)))
        #a = q - t
        #Polygon.IO.writeSVG('q_poly.svg', (q,))
        #Polygon.IO.writeSVG('t_poly.svg', (t,))
        #Polygon.IO.writeSVG('a_poly.svg', (a,))

        return x_non, y_non

    def wc2rc(self, X, Xref, azi_surf, tilt_surf):
        # Passes in: (X_win, X_rec[0], azi_rec_rad, tilt_rec_rad)
        # Transforms world coordinates to relative coordinates
        # Input:    X == vector coordinate (x,y,z)
        #           Xref == referenced coordinate
        #           azi_surf == azimuth angle of referenced surface [rad]
        #           tilt_surf == tilt angle of referenced surface [rad]
        # Calculate for unit vectors represented new coordinate system (relative to interexted plane) from azi_surf and tilt_surf         az  5.75,   tilt  1.57
        #u1=      [sin(azi_surf)*     cos(tilt_surf)       cos(azi_surf)*     cos(tilt_surf)       -sin(tilt_surf)];
        #print "X", X
        #print "X", Xref
        u1 = (math.sin(azi_surf)*math.cos(tilt_surf), math.cos(azi_surf)*math.cos(tilt_surf), -math.sin(tilt_surf))
        w1 = (math.sin(azi_surf)*math.sin(tilt_surf), math.cos(azi_surf)*math.sin(tilt_surf), math.cos(tilt_surf))
        # v1=cross(w1,u1);
        # Result from cross(w1,u1)
        # v1=[ - cos(azi_surf)*cos(tilt_surf)^2 - cos(azi_surf)*sin(tilt_surf)^2, sin(azi_surf)*cos(tilt_surf)^2 + sin(azi_surf)*sin(tilt_surf)^2, 0]
        #vi = (((-math.cos(azi_surf)*(math.cos(tilt_surf)**2)) - (cos(azi_surf)*(math.sin(tilt_surf)**2))), ((math.sin(azi_surf)*math.cos(tilt_surf)**2) + (math.sin(azi_surf)*math.sin(tilt_surf)**2)), 0)
        v1 = (-1*math.cos(azi_surf), math.sin(azi_surf), 0)

        # Translate
        #xp=X(:,1)-Xref(1); #yp=X(:,2)-Xref(2); #zp=X(:,3)-Xref(3);
        # This should take the entire row of X[] based on: http://wiki.scipy.org/NumPy_for_Matlab_Users#head-3ad4144208bdb8910ff1488c3e5bcd93e764dbc4
        # Also, this explains differneces in numpy right matrix divide: http://stackoverflow.com/questions/1001634/array-division-translating-from-matlab-to-python
        #X1 = mat([[X[0][0], X[0][1], X[0][2]], [X[1][0], X[1][1], X[1][2]], [X[2][0], X[2][1], X[2][2]], [X[3][0], X[3][1], X[3][2]]])
        # The above may need to become a loop when walls of different shapes are considered, i.e with more than 4 corners of coordinates
        #Xany = zeros((len(X), 3))
        #row = 0
        #while row < len(X):                 # this is not outputting in column formats
        #    col = 0
        #    #Xany[row, :] = X[row][col]
        #    Xany[row, col] = X[row][col]
        #    Xany[row, col + 1] = X[row][col + 1]
        #    Xany[row, col + 2] = X[row][col + 2]
        #    row += 1
        #X1 = Xany  # if this is the same as X1 above

        #Xany2 = zeros((len(X), 3))
        #print len(X)
        row = 0
        check = 0
        temp_mat = zeros((len(X), 3))
        while row < len(X):
            if check == 0:
                row = 0
                temp_mat = mat([X[row][0], X[row][1], X[row][2]])
                check = 1
            else:
                temp_mat2 = mat([X[row][0], X[row][1], X[row][2]])
                temp_mat = concatenate((temp_mat, temp_mat2))
                check = 1
            row += 1
        #print "temp_mat check: ", temp_mat
        #print temp_mat[:, 0]

        Xref1 = mat([Xref[0], Xref[1], Xref[2]])
        #print X1
        #print "test" ,X1[:, 0]
        #print temp_mat

        #Xrec = zeros((len(Xref), 3))
        #row = 0
        #while row < len(Xref):
        #    col = 0
        #    Xrec[row, col] = Xref[row][col]
        #    Xrec[row, col + 1] = Xref[row][col + 1]
        #    Xrec[row, col + 2] = Xref[row][col + 2]
        #    row += 1
        #Xref = Xrec  # if this is the same as Xref above

        xp = temp_mat[:, 0] - Xref1[:, 0]   # x
        xpp = temp_mat[:, 0] - Xref1[:, 0]  # duplicate for use below
        yp = temp_mat[:, 1] - Xref1[:, 1]   # y
        zp = temp_mat[:, 2] - Xref1[:, 2]   # z

        # Rotate
        ones = mat(xpp)
        k = 0  # To get the total rows the matrix w below will have
        for i, row in enumerate(ones):
            ones[i] = 1
            k += 1
        #X1_temp = [xp yp zp ones(size(xp))]  *  [1 0 0; 0 1 0; 0 0 1; 0 0 0]  /  [u1; v1; w1; 0 0 0]
        #This used matrix and not array to divide: http://stackoverflow.com/questions/211160/python-inverse-of-a-matrix
        #A = dot(array([xp, yp, zp, ones]), array([[1., 0., 0.],  [0., 1., 0.], [0., 0., 1.], [0., 0., 0.]]))
        v = mat([[1., 0., 0.],  [0., 1., 0.], [0., 0., 1.], [0., 0., 0.]])

        #w = ([[xp], [yp], [zp], [ones]]), so create versions of this here:
        w = concatenate((xp, yp, zp, ones), 1)
        #w = zeros((k, 4))
        #row = 0
        #while row < k:
        #    col = 0
        #    w[row, col] = xp[:, col]
        #    w[row, col + 1] = yp[:, col + 1]
        #    w[row, col + 2] = zp[:, col + 2]
        #    w[row, col + 3] = ones[:, col + 3]
        #    row += 1
        A = w * v

        B = zeros((4, 3))
        row = 0
        while row < 4:
            col = 0
            if row == 0:
                B[row, col] = u1[0]
                B[row, col + 1] = u1[1]
                B[row, col + 2] = u1[2]
            if row == 1:
                B[row, col] = v1[0]
                B[row, col + 1] = v1[1]
                B[row, col + 2] = v1[2]
            if row == 2:
                B[row, col] = w1[0]
                B[row, col + 1] = w1[1]
                B[row, col + 2] = w1[2]
            if row == 3:
                B[row, col] = 0
                B[row, col + 1] = 0
                B[row, col + 2] = 0
            row += 1

        # Some of these values render as -3.0616169978683855e-17 for "0" possibly because matlab is rounding to 0?
        # Inverse of B, multiply by A to get A / B
        # http://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.pinv.html
        B = numpy.linalg.pinv(B)
        X1_temp = A * B

        # Return the first three columns of this matrix
        X1 = (X1_temp[:, 0:3])
        #print "X1_temp: ", X1
        return X1, u1, v1, w1

    def poly2cw(self, x, y):
        # Quickly transforms in Matlab 2D coordinates to order in clockwise direction
        # Assume X already in order of either CW or CCW
        # Input: X == 2D coordinate
        # x, y here are the first two columns of the matrix calculated for the last function
        test = mat([])  # Alternate way to compare to determine if the passed matricies are empty or not
        if x == test or y == test:
        #if x is None or y is None:
            # If x or y does not exist/have any values...assuming this is correct syntax
            x_cw = list()
            y_cw = list()
            cw_flag = 1
        else:
            X = concatenate((x, y), 1)
            l = 0
            s = 0
            # Need to knw the number of rows in x and y to get the last-1th element in the "A" calculation below
            # [-1] to access the last matrix element was not working in all cases...so using these two loops
            for row in x:
                l += 1
            for row in y:
                s += 1

            #A=0.5*(sum   (x(1:end-1).*y(2:end)   -   x(2:end).*y(1:end-1))   +   x(end).*y(1)   -   x(1).*y(end)   );
            A = 0.5 * (sum( multiply(x[0:l-1], y[1:s]) - multiply(x[1:l], y[0:s-1])) + multiply(x[-1], y[0]) - multiply(x[0], y[-1]) )
            #print A
            if A > 0:
                # CWW
                #Xcw = X(end:-1:1,:);
                # For the first row, go from end to front...a matrix with rows in reverse order
                Xcw = X[::-1, :]
                # so Xcw = (y, x) if integers
                cw_flag = 0
            else:
                #CW
                Xcw = X
                # otherwise Xcw = (x, y)
                cw_flag = 1

            #x_cw = Xcw[:, 0]  # First element is assigned to x_cw  # This format does not make a column
            #y_cw = Xcw[:, 1]  # Second element is assigned to y_cw
            x_cw = zeros((len(Xcw), 1))
            y_cw = zeros((len(Xcw), 1))
            row = 0
            while row < len(x_cw):
                col = 0
                x_cw[row, col] = Xcw[row, col]
                y_cw[row, col] = Xcw[row, col + 1]
                row += 1

        return x_cw, y_cw, cw_flag  # Xcw_rec1, Xcw_rec2 and may need to add flag above

    def shadow_coordinates(self, X_cas, X_rec, azi_rec, tilt_rec, azi_sun, tilt_sun):
        # Finds the coordinates of a shadow in terms of coordinates
        # Referenced to receiving surface coordinate
        # Input: X_cas    == Coordinate of casting surface
        #        X_rec    == Coordinate of receiving surface
        #        azi_rec  == Azimuth angle of normal vector of receiving surface [rad]
        #        tilt_rec == Tilt angle of receiving surface [rad]
        #        azi_sun  == Azimuth angle of the sun [rad]
        #        tilt_sun == Altitude angle of the sun [rad]
        # Output: Xshadow == Coordinate of shadow in 2D (relative to receiving surface)
        #        facesun_flag == 1 if receiving surface facing sun
        #        Shadow_flag == 1 if shadow exist
        # Referenced
        #Xref=X_rec(1,:);
        #print "X_cas: ", X_cas

        XrefA = zeros((len(X_rec), 3))
        row = 0
        while row < len(X_rec):
            col = 0
            XrefA[row, col] = X_rec[row][col]
            XrefA[row, col + 1] = X_rec[row][col + 1]
            XrefA[row, col + 2] = X_rec[row][col + 2]
            row += 1
        Xref = XrefA[0, :]  # Get the first row...

        XcasA = zeros((len(X_cas), 3))
        row = 0
        while row < len(X_cas):
            col = 0
            XcasA[row, col] = X_cas[row][col]
            XcasA[row, col + 1] = X_cas[row][col + 1]
            XcasA[row, col + 2] = X_cas[row][col + 2]
            row += 1
        # Tolerance introduced by coordinate transformation
        ztol = 0.00001
        cos_theta, CS1, CS2, CS3, CW1, CW2, CW3 = self.cos_AIS(azi_sun, tilt_sun, azi_rec, tilt_rec)
        # Check if the surface is/is not facing the sun
        if cos_theta < 0:
            # This means the receiving surface is not facing the sun
            facesun_flag = 0
            Xsr_cas = mat([])
            Xsr_cas_new = mat([])
            Xshadow = mat([])
        else:
            # This means the receiving surface is facing the sun
            facesun_flag = 1
            # Check if the casting surface is behind or below the receiving surface
            if max(XcasA[:, 2]) < min(XrefA[:, 2]):
                #print "found"
                # Casting surface is below so there is no shadow
                Xsr_cas = mat([])
                Xsr_cas_new = mat([])
                Xshadow = mat([])
            else:
                # Transform coordinate of potential casting surface
                #Xref needs to be a list (x, y, z) and assuming we are taking a row of size 3
                x = Xref[0]
                y = Xref[1]
                z = Xref[2]
                reformat_list = (x, y, z)
                #reformat_list = (-4.567569732, 3.2357074224, 0.0)         !!!!!!!!!!!!!!!!!!! using BOTTOM here
                #print X_cas
                Xsr_cas, u1, v1, w1 = self.wc2rc(X_cas, reformat_list, azi_rec, tilt_rec)
                #Xsr_cas_fake = mat([[-3.4290, -3.3020, 0.2540], [-3.6195, -3.048, 0], [-3.6195, -3.048, -6.0960], [-3.4290, -3.3020, -6.3500]])  # Take out the fake and put new back in this section

                if max(Xsr_cas[:, 2]) < ztol:  # (not a single zsr > 0) # change Xsr_cas_fake back to Xsr_cas  !!!!!!!
                    # Casting surface is behind so there is no shadow
                    Xsr_cas_new = mat([])
                    Xshadow = mat([])
                else:
                    # Clipping surface is behind (zsr < 0)
                    Xsr_cas_new = self.clipCoor(Xsr_cas)  # Passing a matrix                # change Xsr_cas_fake back to Xsr_cas  !!!!!!! and remove the surface tilt below:
                    #azi_rec = 4.7124
                    # Project shadow onto receiving surface referenced to receiving surface
                    Xshadow = self.get_shadow(Xsr_cas_new, azi_sun, tilt_sun, azi_rec, tilt_rec)
                    #print Xshadow
                    #print ""

        #Remedy MatLab: elseif max(range(Xshadow))>1e5    # changed because not finding 0 index when empty
        emp = numpy.empty([0, 0])

        if (len(Xshadow)-1) == len(emp):
            # This should mean is empty and will error on index = 0....made same "if not" as below:
            # This means is empty and will error on index = 0....made same "if not" as below:
            #print "max(Xshadow[:, 0]): ", Xshadow
            Xshadowmax = 0
        else:
            #print "max(Xshadow[:, 0]): ", Xshadow
            r_one = (max(Xshadow[:, 0]) - min(Xshadow[:, 0]))
            r_two = (max(Xshadow[:, 1]) - min(Xshadow[:, 1]))
            range_list = (r_one, r_two)
            Xshadowmax = max(range_list)
        #print Xshadow
        #print "Xshadowmax: "
        #print Xshadowmax

        # Now, check if a current shadow exists:
        #Xshadow2 = mat([])
        #print Xshadow
        if (len(Xshadow)-1) == len(emp):  # If Xshadow is empty (or equal to an empty matrix)
            #print "first"
            Shadow_flag = 0
        elif Xshadowmax > 1e5:  # Over-range shadow projecting case   MatLab: elseif max(range(Xshadow))>1e5
            #print "second ", Xshadowmax
            Shadow_flag = 0
        else:
            #print "third"
            Shadow_flag = 1

        if (len(Xshadow)-1) == len(emp):
            Xshadow0 = mat([])
            Xshadow1 = mat([])
        else:
            Xshadow0 = zeros((len(Xshadow), 1))
            Xshadow1 = zeros((len(Xshadow), 1))
            row = 0
            while row < len(Xshadow):
                col = 0
                Xshadow0[row] = Xshadow[row][col]
                Xshadow1[row] = Xshadow[row][col + 1]
                row += 1

        return Xshadow0, Xshadow1, facesun_flag, Shadow_flag, Xsr_cas, Xsr_cas_new

    def cos_AIS(self, azi_sun, tilt_sun, azi_surf, tilt_surf):
        # To find the cosine of the angle of incidence of the sun rays on this surface
        # Note: If cos_theta > 0, this means this surface is facing the sun
        # Sun Direction Cosines:
        CS1 = math.sin(azi_sun) * math.cos(tilt_sun)
        CS2 = math.cos(azi_sun) * math.sin(tilt_sun)
        CS3 = math.cos(tilt_sun)

        # Surface Direction Cosines:
        CW1 = math.sin(azi_surf) * math.cos(tilt_surf)
        CW2 = math.cos(azi_surf) * math.sin(tilt_surf)
        math.cos(tilt_surf)
        CW3 = math.cos(tilt_surf)
        #x = math.cos(1.5708)
        #print "x: ", x
        #print CW3  # This was where there is a problem, the cos(1.5708) = 0.999
        cos_theta = (CS1*CW1) + (CS2*CW2) + (CS3*CW3)
        #print "this one is the test: ", cos_theta

        return cos_theta, CS1, CS2, CS3, CW1, CW2, CW3

    def clipCoor(self, coor_set):
        # Clips the passed in value...this clips out or subtracts the part where z < 0
        # Pass in coordinate list with coordinates in list form (x, y, z)....assuming always 3 rows
        # sample set passed in: X=[-11.0625,-6.8301,1.8301;-11.0625,-6.8301,-8.1698;-11.0625,-26.8301,-8.1698;-11.0625,-26.8301,1.8301]
        #print "coor_set:"
        #print coor_set
        ztol = 1e-5
        count = 1
        m = len(coor_set)
        n = 3
        #blank = ([[0., 0., 0.]])
        #print blank
        #matrixOrig = [coor_set[-1, :]; coor_set; coor_set[0, :]]
        matrixOrig = coor_set
        last = matrixOrig[-1, :]
        first = matrixOrig[0, :]
        matrixOrig = concatenate((last, matrixOrig))
        matrixOrig = concatenate((matrixOrig, first))
        z = matrixOrig[:, 2]
        Xnew = zeros((2*m, 3))

        # Clipping The Matrix
        j = -1
        i = 2
        while i <= m + 1:
            # for ii=2:m+1 ... This needs to start at i = 1 due to Matlab indexing from 1 not 0
            if z[i - 1] > -ztol:
                # Clipping is unnecessary in this case
                j += 1
                Xnew[j, :] = matrixOrig[i - 1, :]
            else:
                # Otherwise, this needs clipping:
                if z[i - 2] <= ztol and z[i + 0] <= ztol:
                    # Both neighbor points are negative so get rid of this point
                    p = 0
                elif z[i - 2] > ztol and z[i + 0] > ztol:
                    # Both neighbor points positive so interpolate to both points and get two new points
                    j += 1
                    #Xnew(jj,:)=Xtemp(ii-1,:)-z(ii-1)                     *((Xtemp(ii,:)-Xtemp(ii-1,:))      ./(z(ii)-z(ii-1)));
                    Xnew[j, :] = (matrixOrig[i - 2, :])-(z[i - 2]) * (( matrixOrig[i - 1, :]-matrixOrig[i - 2, :]) / (z[i - 1]-z[i - 2]) )
                    j += 1
                    #Xnew(jj,:)=Xtemp(ii+1,:)-z(ii+1)*((Xtemp(ii,:)-Xtemp(ii+1,:))./(z(ii)-z(ii+1)));
                    Xnew[j, :] = (matrixOrig[i + 0, :])-(z[i + 0]) * (( matrixOrig[i - 1, :]-matrixOrig[i + 0, :]) / (z[i - 1]-z[i + 0]) )
                elif z[i - 2] > ztol:
                    # Previous point is positive
                    j += 1
                    #Xnew(jj,:)=Xtemp(ii-1,:)-z(ii-1)*((Xtemp(ii,:)-Xtemp(ii-1,:))./(z(ii)-z(ii-1)));
                    Xnew[j, :] = (matrixOrig[i - 2, :])-(z[i - 2]) * (( matrixOrig[i - 1, :]-matrixOrig[i - 2, :]) / (z[i - 1]-z[i - 2]) )
                else:
                    # Next point is positive because: [z(ii+1) > tol_z] or [matrixOrig[row+1][3] > ztol]
                    j += 1
                    #Xnew(jj,:)=Xtemp(ii+1,:)-z(ii+1)*((Xtemp(ii,:)-Xtemp(ii+1,:))./(z(ii)-z(ii+1)));
                    Xnew[j, :] = (matrixOrig[i + 0, :])-(z[i + 0]) * (( matrixOrig[i - 1, :]-matrixOrig[i + 0, :]) / (z[i - 1]-z[i + 0]) )
                    #Xnew(jj,:)=Xtemp(ii+1,:)-z(ii+1)*((Xtemp(ii,:)-Xtemp(ii+1,:))./(z(ii)     -z(ii+1)))
            i += 1

        #print j  # J here is = 2, so below should have done the first 3 rows: 0, 1, and 2, but its not so use j+1
        matrixNew = Xnew[0:j+1, :]
        #print "matrixNew: "
        #print matrixNew

        return matrixNew  # but this may need to be a list structure again...try printing this too

    def get_shadow(self, coordinate, azi_sun, tilt_sun, azi_surf, tilt_surf):
        # Find location of a shadow by passing coordinate (x, y, z)
        # Input:    X           ==Coordinate of casting surface referenced to receiving surface (x, y z)
        #           azi_sun     ==azimuth angle of the sun [rad]
        #           tilt_sun    ==tilt angle of the sun [rad]
        #           azi_surf    ==azimuth angle of the surface [rad]
        #           tilt_surf   ==tilt angle of the surface [rad]
        #x=X(:,1); y=X(:,2); z=X(:,3);
        #x = coordinate[:, 0]  #x = coordinate.x
        #print coordinate
        #x = zeros((len(coordinate), 1))
        #x = coordinate[:, 0]  #This is giving a row from the first column of coordinate, not usable?
        #print x
        #y = coordinate[:, 1]
        #z = coordinate[:, 2]
        #print z

        x = zeros((len(coordinate), 1))
        y = zeros((len(coordinate), 1))
        z = zeros((len(coordinate), 1))
        row = 0
        while row < len(coordinate):
            col = 0
            x[row] = coordinate[row][col]
            y[row] = coordinate[row][col + 1]
            z[row] = coordinate[row][col + 2]
            row += 1
        #print z
        #print "y"
        #print y
        #print "z"
        #print z
        cos_theta, CS1, CS2, CS3, CW1, CW2, CW3 = self.cos_AIS(azi_sun, tilt_sun, azi_surf, tilt_surf)

        a = ( (math.sin(azi_surf) * CS1) - (math.cos(azi_surf) * CS2) )
        b = ((-1) * math.cos(azi_surf) * math.cos(tilt_surf) * CS1) - (math.sin(azi_surf) * math.cos(tilt_surf) * CS2) + (math.sin(tilt_surf) *CS3)  # Values fine up to here

        #xp = x - ((z * a) / cos_theta)
        #yp = y - ((z * b) / cos_theta)
        # Multiplication is ok
        #x1 = (z * a) / cos_theta
        #y1 = ((z * b) / cos_theta)

        xp = zeros((len(x), 1))
        yp = zeros((len(y), 1))
        row = 0
        while row < len(y):
            xrow = ((z[row] * a) / cos_theta)
            xp[row] = x[row] - xrow
            yrow = ((z[row] * b) / cos_theta)
            yp[row] = y[row] - yrow
            row += 1

        shadow_coordinate_2D = concatenate((xp, yp), 1) # The first 3 and the last 3 matricies are wrong here???
        #print shadow_coordinate_2D
        #print " "
        # There is a lot of odd rounding/display errors or differences between Python and Matlab:
        # Matlab example:
        #Xshadow =
        #1.0e+15 *
        #[[-0.0000 ]
        # [-0.6533]
        # [-0.0000]]
        # And from Python:
        #[[ -3.42900000e+00]
        # [ -6.50851267e+14]
        # [ -3.61950000e+00]]

        return shadow_coordinate_2D

    #def polyarea(self, poly):
        # Quicker Version of a finding the area of a 2D Polygon
        # Takes an input of x,y coordinates in column or row
        #max_range = 1e10
        #%Skip point that show value NaN
        #i_temp=(~isnan(x) & ~isnan(y));  # This may not be the right translation below using isnan:
        #i_temp = numpy.isnan(poly[:, 0]) and numpy.isnan(poly[:, 1])
        #x=x(i_temp);
        #x = i_temp[:, 0]  #first column?
        #y=y(i_temp);
        #y = i_temp[:, 1]  #second column?

        #if not x:  # if x is empty
        #    area = 0
        #elif x > max_range or y > max_range:
            # Does not work if range is too large...so does this:
            # polyarea(x,y) from matlab, currently using python version below, may need to put the new x,y in a matrix for this input
        #    area = self.polyarea2(poly)
        #else:
            #from: A=0.5*abs(sum  (x(1:end-1).*y(2:end)-x(2:end).*y(1:end-1)) + x(end).*y(1)-x(1).*y(end));  # Check the sum function/order here
        #    area = 0.5 * math.fabs( multiply(x[0: 0], y[1:-1]) - multiply(x[1: -1], y[0:0]) + multiply(x[:, -1][0, 0], y[:, 0][0, 0]) - multiply(x[:, 0][0, 0], y[:, -1][0, 0]) )

        #return area

    def polyarea2(self, polyIn):
        #print polyIn
        # Area of polygon, poly, uses the following two functions
        # From: http://oco-carbon.com/2012/10/01/python-and-energyplus-polygon-areas-in-3d-space/
        # ...use it by passing it a set of vertices as a list of lists in the form [[x1,y1,z1],[x2,y2,z2],...,[xn,yn,zn]]
        z = zeros((len(polyIn), 1))
        poly = concatenate((polyIn, z), 1)
        row = 0
        new_list = list()
        while row < len(poly):
            new_tuple = list()
            col = 0
            x = poly[row, col]
            new_tuple.append(x)
            y = poly[row, col + 1]
            new_tuple.append(y)
            z = poly[row, col + 2]
            new_tuple.append(z)
            new_set = tuple(new_tuple)
            new_list.append(new_set)
            row += 1
        poly = new_list
        #print poly
        #print "poly is now: "  # This is a matrix, may need to change to a list
        #print poly
        if len(poly) < 3:  # not a polygon this is a line - no area so return o for total area
            return 0
        total = [0, 0, 0]
        N = len(poly)
        for i in range(N):
            vi1 = poly[i]
            vi2 = poly[(i+1) % N]
            prod = numpy.cross(vi1, vi2)
            total[0] += prod[0]
            total[1] += prod[1]
            total[2] += prod[2]
        result = numpy.dot(total, self.unit_normal(poly[0], poly[1], poly[2]))

        return abs(result/2)

    def unit_normal(self, a, b, c):
        # Unit normal vector of plane defined by points a, b, and c
        x = numpy.linalg.det([[1, a[1], a[2]], [1, b[1], b[2]], [1, c[1], c[2]]])
        y = numpy.linalg.det([[a[0], 1, a[2]], [b[0], 1, b[2]], [c[0], 1, c[2]]])
        z = numpy.linalg.det([[a[0], a[1], 1], [b[0], b[1], 1], [c[0], c[1], 1]])
        magnitude = (x**2 + y**2 + z**2)**.5

        return (x/magnitude, y/magnitude, z/magnitude)


