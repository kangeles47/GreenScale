#-------------------------------------------------------------------------------
# Name:        HeatCalculation.py
# Purpose:     Green Scale Tool TM Heat Calculation Module (Calculates heat flux for horizontal surfaces)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
import math
from objects.BaseElement import BaseElement
from objects.Surface import Surface
from objects.TransmittedSolar import TransmittedSolar
from GSUtility import GSUtility
import logging
import datetime
TM_user = logging.getLogger('TMuser_V1')


class HeatCalculation(BaseElement):
    # Sub-routines for top heat, floor type heat, and ground heat
    # Called from Space.py and used after surface heatflux is called
    # shgc_dictionary = dict()
    # may need an order_of_spaces = list()  # or multiples ???

    def get_top_heat(self, space, surface, weather, spaces_dict, temp_record, Coeff, G_space_record, areaDict, areaWinDict):
        # Calculates the heat flux for the top-most horizontal surface
        surf = Surface()
        A_total = surf.get_A(surface, areaDict, areaWinDict)
        A_noOp = surf.get_A_noOp(surface, areaDict, areaWinDict)
        T_space = spaces_dict[space.obj_id][1]
        T2 = temp_record[surface.obj_id + "_inside_surface-1"]   # A2 in Nas new set of code
        T3 = temp_record[surface.obj_id + "_outside_surface-1"]  # A1 in Nas new set of code
        T1 = weather["t_outside"]
        #print T2

        # need the surface related information, T_space, U, R3
        U = surf.get_U_surface_e(A_total, A_noOp, surface, areaWinDict)
        R3 = 1/U
        # Using calculations from: self.surface.constr.layer.C
        C = surf.get_C_surface(A_total, A_noOp, surface, Coeff, areaWinDict)
        #print C
        dt = 3600
        C2 = C/2
        C4 = C/2

        #if weather["hour"] == 8:
            #print weather.hour

        if surface.adjacent_space_id == "none":  # If there is not an adjacent space use current space temperature
            T_space2 = T_space
            space2 = space.obj_id
        else:                                    # If there is an adjacent space use the temperature of that space
            # Eventually may have to loop to consider spanning shared surfaces, but there's only be one option now...
            space2 = surface.adjacent_space_id
            T_space2 = spaces_dict[space2][1]

        #print "lookup: ", space2

        transmitted_space2 = G_space_record[space2]
        #T_in = round(transmitted_space2, 6)
        hc1 = 4.04   # T_space-AnoOp > T_in
        hc2 = 0.948  # T_space-AnoOp > T_out
        R5 = 1/hc2
        R1 = 1/hc1

        #print ((C2*T3/dt+T_space/R1)*R3)
        # T_in is the interior surface temperature in the space that we pick
        T_in = (transmitted_space2+C4*T2/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*T3/dt+T_space/R1)*R3) / ((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3)
        #T_in = (Transmitted_space+C4*A2/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*A1/dt+T_space/R1)*R3)/  ((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
        T_out = ((((C2/dt)+(1/R1)+(1/R3))*T_in)-(C2/dt*T3)-(T_space/R1))*R3
        #T_out = ((  C2/dt+  1/R1+  1/R3)* T_in-  C2/dt*A1-  T_space/R1)*R3;
        #print T_in
        #T_in = round(T_in, 6)
        #T_out = round(T_out, 6)

        if T_in > T_space and T_out > T_space2:
            hc1 = 0.948
            hc2 = 4.04
            R5 = 1/hc2
            R1 = 1/hc1
            # T_in is the interior surface temperature in the space that we pick
            T_in = (transmitted_space2+C4*T2/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*T3/dt+T_space/R1)*R3) / ((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3)
            #T_in = ( Transmitted_space+C4*A2/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*A1/dt+T_space/R1)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3);
            T_out = ((C2/dt+1/R1+1/R3)*T_in-C2/dt*T3-T_space/R1)*R3
            #T_out = ((C2/dt+1/R1+1/R3)*T_in-C2/dt*A1-T_space/R1)*R3;
            #T_in = round(T_in, 6)
            #T_out = round(T_out, 6)
            #print "one", T_in #, T_space2, T_out, T_in
            #print transmitted_space2
        elif T_in > T_space and T_out < T_space2:
            hc1 = 0.948
            hc2 = 0.948
            R5 = 1/hc2
            R1 = 1/hc1
            # T_in is the interior surface temperature in the space that we pick
            T_in = (transmitted_space2+C4*T2/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*T3/dt+T_space/R1)*R3) / ((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3)
            T_out = ((C2/dt+1/R1+1/R3)*T_in-C2/dt*T3-T_space/R1)*R3
            #T_in = round(T_in, 6)
            #T_out = round(T_out, 6)
            #print "two", T_in #, T_space2, T_out, T_in
        else: #T_in < T_space and T_out > T_space2:
            hc1 = 4.04
            hc2 = 4.04
            R5 = 1/hc2
            R1 = 1/hc1
            # T_in is the interior surface temperature in the space that we pick
            T_in = (transmitted_space2+C4*T2/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*T3/dt+T_space/R1)*R3) / ((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3)
            T_out = ((C2/dt+1/R1+1/R3)*T_in-C2/dt*T3-T_space/R1)*R3
            #T_in = round(T_in, 6)
            #T_out = round(T_out, 6)
            #print "three", T_in #, T_space2, T_out, T_in

        # Update temp_record dictionary
        # Add the newly calculated numbers into the dictionary:
        temp_record[surface.obj_id + "_outside_surface"] = T_out
        temp_record[surface.obj_id + "_inside_surface"] = T_in
        #print T_out, T_in

        # from: Q_top =  hc1 * A *(T_in-T_space)
        #Q_top = round(hc1 * A_total * (T_in-T_space), 6)
        Q_top = hc1 * A_total * (T_in-T_space)

        return Q_top

    def get_floor_heat(self, space, surface, weather, G_space, spaces_dict, A_noOp_floor, temp_record, Coeff, areaDict, areaWinDict):
        # for a top roof / interiorfloor, the transmitted solar energy of another- the side also need to be calculated
        surf = Surface()
        A_total = surf.get_A(surface, areaDict, areaWinDict)
        A_noOp = surf.get_A_noOp(surface, areaDict, areaWinDict)

        T_space = spaces_dict[space.obj_id][1]
        T2 = temp_record[surface.obj_id + "_inside_surface-1"]
        T3 = temp_record[surface.obj_id + "_outside_surface-1"]
        T1 = weather["t_outside"]
        ground_temp = (T_space - 2)

        # Using calculations from: self.surface.constr.layer.C
        C = surf.get_C_surface(A_total, A_noOp, surface, Coeff, areaWinDict)
        #print C

        if surface.adjacent_space_id == "none":  # If there is not an adjacent space use current space temperature
            T_space2 = T_space
            space2 = space.obj_id
        else:                                    # If there is an adjacent space use the temperature of that space
            # Eventually may have to loop to consider spanning shared surfaces, but there's only be one option now...
            space2 = surface.adjacent_space_id
            T_space2 = spaces_dict[space2][1]

        # need the surface related information, T_space, U, R3
        #A_noOp_floor = surf.get_A_noOp(current_floor)
        U = surf.get_U_surface_e(A_total, A_noOp, surface, areaWinDict)
        R3 = 1/U
        dt = 3600

        #print surface.obj_id, surface.adjacent_space_id

        if surface.adjacent_space_id == "none":
            # Means there is no adjacent space or space temp so thus the floor must be the bottom floor
            # assuming it is reduced convection T_space1 > T2
            #print surface.obj_id
            hc1 = 0.948
            R5 = 1/hc1
            A1 = C/dt*T2 + T_space/R5 + ground_temp/R3 + G_space
            A2 = C/dt + 1/R5 + 1/R3
            T_in = A1/A2
            #print T_in
            if T_space < T_in:
                hc1 = 4.04
                R5 = 1/hc1
                A1 = C/dt*T2 + T_space/R5 + ground_temp/R3 + G_space
                A2 = C/dt + 1/R5 + 1/R3
                T_in = A1/A2
            T_out = ground_temp
            #T_in = round(T_in, 6)
            #T_out = round(T_out, 6)
        else:
            #print surface.obj_id
            # This is an Intermediate Floor, so it will have an adjacent space temp T_space2
            C2 = C/2
            C4 = C/2
            # else continues but indents seem to make the following outside of this else...???
            #h_space = self.get_height_floorspace(surface)
            #h_surface = self.get_height(surface)
            #print "h_space: ", h_space
            #print "h_surface: ", h_surface
            hc1 = 0.948   # T_space-AnoOp > T_in
            hc2 = 4.04  # T_space-AnoOp > T_out
            R5 = 1/hc2
            R1 = 1/hc1
            T_in = (C4*T3/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*T2/dt+T_space/R1+G_space)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3)
            T_out = (C2*T2/dt+T_space/R1+(C2/dt+1/R3+1/R1)*(C4*T3/dt+T_space2/R5)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3)
            #T_in = round(T_in, 6)
            #T_out = round(T_out, 6)

            #if h_space == h_surface:
            #    # if the interiorfloor is the space's floor
            #    hc1 = 0.948   # T_space-AnoOp > T_in
            #    hc2 = 4.04  # T_space-AnoOp > T_out
            #    R5 = 1/hc2
            #    R1 = 1/hc1
                # T_in is the interior surface temperature in the space that we pick, or of the current_space
            #    T_in = (C4*T2/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*T3/dt+T_space/R1+G_space)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3)
            #    T_out = (C2*T3/dt+T_space/R1+(C2/dt+1/R3+1/R1)*(C4*T2/dt+T_space2/R5)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3)
            if T_in > T_space and T_out > T_space2:
                hc1 = 4.04
                hc2 = 0.948
                R5 = 1/hc2
                R1 = 1/hc1
                # T_in is the interior surface temperature in the space that we pick
                T_in = (C4*T3/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*T2/dt+T_space/R1+G_space)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3)
                T_out = (C2*T2/dt+T_space/R1+(C2/dt+1/R3+1/R1)*(C4*T3/dt+T_space2/R5)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3)
                #T_in = round(T_in, 6)
                #T_out = round(T_out, 6)
                #print "one", T_in
            elif T_in > T_space and T_out < T_space2:
                hc1 = 4.04
                hc2 = 4.04
                R5 = 1/hc2
                R1 = 1/hc1
                # T_in is the interior surface temperature in the space that we pick
                T_in = (C4*T3/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*T2/dt+T_space/R1+G_space)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3)
                T_out = (C2*T2/dt+T_space/R1+(C2/dt+1/R3+1/R1)*(C4*T3/dt+T_space2/R5)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3)
                #T_in = round(T_in, 6)
                #T_out = round(T_out, 6)
                #print "two", T_in
            else:  # T_in < T_space and T_out > T_space2:  # This was what was intended, but will cause the else below to trigger if not left in the current format...
                hc1 = 0.948
                hc2 = 0.948
                R5 = 1/hc2
                R1 = 1/hc1
                # T_in is the interior surface temperature in the space that we pick
                T_in = (C4*T3/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*T2/dt+T_space/R1+G_space)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3)
                T_out = (C2*T2/dt+T_space/R1+(C2/dt+1/R3+1/R1)*(C4*T3/dt+T_space2/R5)*R3)/((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3)
                #T_in = round(T_in, 6)
                #T_out = round(T_out, 6)
                #print "three", T_in
            #else:
            #    print "Surface Floor Not Found matching case?: ", surface.obj_id, surface.obj_type
            #    if surface.obj_id not in missing_surfaces:
            #        missing_surfaces[surface.obj_id] = surface.obj_type
            #    #raise Exception("Did not meet any condition in get_floor_heat() for surface id: ", surface.obj_id)

        # Update temp_record dictionary
        # Add the newly calculated numbers into the dictionary:
        temp_record[surface.obj_id + "_outside_surface"] = T_out
        temp_record[surface.obj_id + "_inside_surface"] = T_in
        temp_record[surface.obj_id + "_outside_surface-1"] = T_out
        temp_record[surface.obj_id + "_inside_surface-1"] = T_in

        #Q_floor = round(hc1 * A_total * (T_in-T_space), 6)
        Q_floor = hc1 * A_total * (T_in-T_space)
        #print A_total

        return Q_floor

    def get_raised_floor_heat(self, surface, weather, G_space, A_noOp_floor, temp_record, space, spaces_dict, h_surface, terrain, Coeff, areaDict, areaWinDict):
        # For an interior floor that is a top of a space, the transmitted solar energy also needs to be calculated
        dt = 3600
        surf = Surface()
        A_total = surf.get_A(surface, areaDict, areaWinDict)
        A_noOp = A_noOp_floor  # T_space = Infor_space{9, i_space}

        T_space = spaces_dict[space.obj_id][1]
        T2 = temp_record[surface.obj_id + "_inside_surface-1"]
        T3 = temp_record[surface.obj_id + "_outside_surface-1"]
        T1 = weather["t_outside"]
        ground_temp = (T_space - 2)

        hc_external = surf.get_hc_external(weather, surface, h_surface, terrain)
        solarIs = TransmittedSolar()
        Is = 0
        transmitted_win = 0
        transmitted_win, Is = solarIs.get_transmitted_solar(weather, surface, 0, areaWinDict)
        Is *= 0.7
        #print Is

        # Assuming it is reduced convection T_space1 <T2
        hc = 4.04
        R5 = 1/hc
        R1 = 1/hc_external
        U = surf.get_U_surface_e(A_total, A_noOp, surface, areaWinDict)
        R3 = 1/U
        # Using calculations from: self.surface.constr.layer.C
        C = surf.get_C_surface(A_total, A_noOp, surface, Coeff, areaWinDict)
        C2 = C/2
        C4 = C/2

        # Assuming we continue to assign Tp = (weather.hour - 1) and Tp_interior = T2:inside temp and T_space = A_noOp
        M1 = (C2/dt) + (1/R1) + (1/R3)
        M2 = ((C2/dt) * T3) + (T1/R1) + Is
        M3 = (C4/dt) + (1/R3) + (1/R5)
        M4 = (C4/dt)*T2 + (T_space/R5)
        T_out = (M4*R3 + M3*M2*(R3**2) + R3*G_space) / (M3*M1*(R3**2) - 1)  # exterior temp
        T_in = (M1*T_out - M2) * R3                                         # interior temp
        if T_space > T_in:
            hc = 0.948
            R5 = 1/hc
            M1 = (C2/dt) + (1/R1) + (1/R3)
            M2 = ((C2/dt) * T3) + (T1/R1) + Is
            M3 = (C4/dt) + (1/R3) + (1/R5)
            M4 = (C4/dt)*T2 + (T_space/R5)
            T_out = (M4*R3 + M3*M2*(R3**2) + R3*G_space) / (M3*M1*(R3**2) - 1)  # exterior temp
            T_in = (M1*T_out - M2) * R3                                         # interior temp

        # Update temp_record dictionary
        # Add the newly calculated numbers into the dictionary:
        temp_record[surface.obj_id + "_outside_surface-1"] = T_out
        temp_record[surface.obj_id + "_inside_surface-1"] = T_in

        Q_flux = hc * A_total * (T_in-T_space)

        return round(Q_flux, 6)

    def get_ground_heat(self, surface, weather, G_space, A_noOp_floor, temp_record, space, spaces_dict, Coeff, areaDict, areaWinDict):
        # Calculate the ground heat flux for a floor surface
        #print "here"
        surf = Surface()
        A_total = surf.get_A(surface, areaDict, areaWinDict)
        A_noOp = A_noOp_floor
        # The T2 is the inside surface temperature
        T_space = spaces_dict[space.obj_id][1]
        T2 = temp_record[surface.obj_id + "_inside_surface-1"]
        T1 = weather["t_outside"]
        ground_temp = (T_space - 2)
        # need the surface related information, T_space, U, R3
        U = surf.get_U_surface_e(A_total, A_noOp, surface, areaWinDict)
        R3 = 1/U
        # Using calculations from: self.surface.constr.layer.C
        C = surf.get_C_surface(A_total, A_noOp, surface, Coeff, areaWinDict)
        dt = 3600.0
        # Assuming it is reduced convection T_space1>T2
        hc = 0.948
        R5 = 1/hc
        C2 = C/2
        A1 = ((C2/dt) * T2) + (T_space/R5) + (ground_temp/R3) + G_space
        A2 = C2/dt + 1/R5 + 1/R3
        T_in = A1/A2
        if T_space < T_in:
            hc = 4.04
            R5 = 1/hc
            A1 = C2/dt*T2 + T_space/R5 + ground_temp/R3 + G_space
            A2 = C2/dt + 1/R5 + 1/R3
            T_in = A1/A2

        # Update temp_record dictionary
        # Add the newly calculated numbers into the dictionary:
        temp_record[surface.obj_id + "_inside_surface-1"] = T_in

        Q_floor = hc * A_total * (T_in-T_space)

        return round(Q_floor, 6)




