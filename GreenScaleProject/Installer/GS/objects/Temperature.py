#-------------------------------------------------------------------------------
# Name:        Temperature.py
# Purpose:     Green Scale Tool TM Temperature Module (handles temperature change of a surface)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
import math
from objects.BaseElement import BaseElement
from objects.TransmittedSolar import TransmittedSolar
#from objects.Shadow import Shadow
from objects.newShadowCalc import Shadow
from GSUtility import GSUtility
import logging


class Temperature(BaseElement):
    # Sub-routines for each wall type based on the returned hc_external
    # Calculates Inside and Outside Temperatures for each of these surfaces, from Heatflux_surface.m
    # ["ExteriorWall", "Roof", "InteriorWall", "UndergroundWall", "RaisedFloor"]
    # LeeWard surface will only take half of the outdoor convection coefficient
    # Windward surface takes the whole
    opengl_stat = 0

    def ratio(self, shadowRatios, surface, areaDict, areaWinDict, shadowRatioIndex):
        shadows = Shadow()
        A = areaDict[surface.obj_id]
        r = shadowRatios[surface.obj_id]
        newA = A * r

        Aw = 0
        Ar = 0
        i = 0
        for opening in surface.openings:
            if opening.obj_type != "NonSlidingDoor":
                Aw += areaWinDict[opening.obj_id]
                #print "getting to here"
                additional_ratio = shadows.get_shadow_ratio(shadowRatioIndex[surface.obj_id], opening.ocps)
                Ar += additional_ratio
                i += 0
        #print "areas: ", surface.obj_id, Aw, Ar
        newAw = Aw * Ar

        AreaShadowOnlyWin = newA
        AreaShadowNoWin = newA - A

        return AreaShadowNoWin, AreaShadowOnlyWin

    def exterior_wall(self, surface, hc_external, T1, A, A_noWin, weather, R3, C, T_space, temp_record, ShadowsFlag, ns, shadow_record, shade_surf_list, surfaces_dict, areaWinDict, shadowRatios, areaDict, shadowRatioIndex):
        #shadows = Shadow()
        alt = weather["alt_sun"]  # Units here is in Radians
        az = weather["az_sun"]    # Units here is in Radians
        if ShadowsFlag == 1 and alt > 0:
            AreaShadowNoWin, AreaShadowOnlyWin = self.ratio(shadowRatios, surface, areaDict, areaWinDict, shadowRatioIndex)
            #AreaShadowNoWin = 0
            #AreaShadowOnlyWin = 0
        else:
            AreaShadowNoWin = 0
            AreaShadowOnlyWin = 0

        alpha_opaque = surface.construction[0].absorptance
        dt = 3600
        hc = 3.076
        R5 = 1/hc
        #print "R5: ", R5
        R1 = 1/hc_external
        #print hc_external
        solar = TransmittedSolar()
        transmitted_win = 0
        Is = 0
        transmitted_win, Is = solar.get_transmitted_solar(weather, surface, AreaShadowOnlyWin, areaWinDict)
        #print transmitted_win
        Is = Is*(A_noWin - AreaShadowNoWin)/A
        C2 = C/2
        C4 = C/2
        T3 = temp_record[surface.obj_id + "_inside_surface"]
        T2 = temp_record[surface.obj_id + "_outside_surface"]
        M1 = (C2/dt) + (1/R1) + (1/R3)
        #print R3
        M2 = ((C2/dt) * T2) + (T1/R1) + (alpha_opaque*Is)
        M3 = (C4/dt) + (1/R3) + (1/R5)
        M4 = (C4/dt)*T3 + (T_space/R5)

        T_out = (M4*R3 + M3*M2*(R3 ** 2))/((M3*M1*(R3**2))-1)  # T_out is the exterior surface's temperature
        T_in = ((M1*T_out)-M2)*R3                            # T_in is the interior surface's temperature
        #print T_in
        #print "T_out: ",T_out

        # Update temp_record dictionary
        # Add the newly calculated numbers into the dictionary:
        temp_record[surface.obj_id + "_outside_surface"] = T_out
        temp_record[surface.obj_id + "_inside_surface"] = T_in

        #print "outter current: ", temp_record[surface.obj_id + "_outside_surface"][1]
        #print "inner current: ", temp_record[surface.obj_id + "_inside_surface"][1]

        Q_flux = round(hc * A * (T_in-T_space), 6)
        #print Q_flux

        return transmitted_win, Q_flux

    def roof(self, surface, hc_external, T1, A, A_noWin, weather, R3, C, A_noOp, T_space, temp_record, ShadowsFlag, ns, shadow_record, shade_surf_list, surfaces_dict, areaWinDict, shadowRatios, areaDict, shadowRatioIndex):
        #shadows = Shadow()
        alt = weather["alt_sun"]  # Units here is in Radians
        az = weather["az_sun"]    # Units here is in Radians
        #print alt, " , ", az
        if ShadowsFlag == 1 and alt > 0:
            AreaShadowNoWin, AreaShadowOnlyWin = self.ratio(shadowRatios, surface, areaDict, areaWinDict, shadowRatioIndex)
            #AreaShadowNoWin = 0
            #AreaShadowOnlyWin = 0
        else:
            AreaShadowNoWin = 0
            AreaShadowOnlyWin = 0

        # if tilt = 0 or flat roof and assuming reduced convection for T_space1 < T2
        #else if is a tilted roof tilt != 0 and assuming reduced convection for T_space1 < T2
        alpha_opaque = surface.construction[0].absorptance
        dt = 3600
        tilt = surface.tilt*(math.pi/180)
        R1 = 1/hc_external
        solar = TransmittedSolar()
        transmitted_win = 0
        Is = 0
        transmitted_win, Is = solar.get_transmitted_solar(weather, surface, AreaShadowOnlyWin, areaWinDict)
        Is = Is*(A_noWin - AreaShadowNoWin)/A
        C2 = C/2
        C4 = C/2

        if tilt == 0:
            #if T_space > T_in and a flat roof
            hc = 0.948
            R5 = 1/hc
            M1 = C2/dt + 1/R1 + 1/R3
            T2 = temp_record[surface.obj_id + "_outside_surface"]
            M2 = C2/dt*T2 + T1/R1 + alpha_opaque*Is
            M3 = C4/dt + 1/R3 + 1/R5
            T3 = temp_record[surface.obj_id + "_inside_surface"]
            M4 = C4/dt*T3 + T_space/R5
            T_out = (M4*R3 + M3*M2*R3 ** 2) / ((M3*M1*R3 ** 2) - 1)
            T_in = (M1*T_out - M2)*R3
            if T_space > T_in:
                # second condition: T_space <= T_in and flat roof
                hc = 4.04
                R5 = 1/hc
                M1 = C2/dt + 1/R1 + 1/R3
                T2 = temp_record[surface.obj_id + "_outside_surface"]
                M2 = C2/dt*T2 + T1/R1 + alpha_opaque*Is
                M3 = C4/dt + 1/R3 + 1/R5
                T3 = temp_record[surface.obj_id + "_inside_surface"]
                M4 = C4/dt*T3 + T_space/R5
                T_out = (M4*R3 + M3*M2*R3 ** 2) / ((M3*M1*R3 ** 2) - 1)
                T_in = (M1*T_out - M2)*R3

            Q_flux = round(hc * A * (T_in-T_space), 6)

        else:  # Tilted roof condition
            hc = 2.281
            R5 = 1/hc
            M1 = C2/dt + 1/R1 + 1/R3
            T2 = temp_record[surface.obj_id + "_outside_surface"]
            M2 = C2/dt*T2 + T1/R1 + alpha_opaque*Is
            M3 = C4/dt + 1/R3 + 1/R5
            T3 = temp_record[surface.obj_id + "_inside_surface"]
            M4 = C4/dt*T3 + T_space/R5
            T_out = (M4*R3 + M3*M2*R3 ** 2) / ((M3*M1*R3 ** 2) - 1)
            T_in = (M1*T_out - M2)*R3
            if T_space > T_in:
                # second condition: T_space <= T_in and tilted roof
                hc = 3.87
                R5 = 1/hc
                M1 = C2/dt + 1/R1 + 1/R3
                T2 = temp_record[surface.obj_id + "_outside_surface"]
                M2 = C2/dt*T2 + T1/R1 + alpha_opaque*Is
                M3 = C4/dt + 1/R3 + 1/R5
                T3 = temp_record[surface.obj_id + "_inside_surface"]
                M4 = C4/dt*T3 + T_space/R5
                T_out = (M4*R3 + M3*M2*R3 ** 2) / ((M3*M1*R3 ** 2) - 1)
                T_in = (M1*T_out - M2)*R3

            Q_flux = round(hc * A * (T_in-T_space), 6)

        # Update temp_record dictionary
        # Add the newly calculated numbers into the dictionary:
        temp_record[surface.obj_id + "_outside_surface"] = T_out
        temp_record[surface.obj_id + "_inside_surface"] = T_in

        return transmitted_win, Q_flux

    def interior_wall(self, surface, A, C, R3, spaces_dict, T_space, temp_record):
        transmitted_win = 0
        dt = 3600
        hc = 3.076
        C2 = C/2
        C4 = C/2
        R5 = 1/hc
        R1 = 1/hc

        if surface.adjacent_space_id == "none":  # If there is not an adjacent space use current space temperature
            T_space2 = T_space
            space2 = surface.obj_id
        else:                                    # If there is an adjacent space use the temperature of that space
            # Eventually may have to loop to consider spanning shared surfaces, but there's only be one option now...
            space2 = surface.adjacent_space_id
            T_space2 = spaces_dict[space2][1]

        # Assuming interior walls are always vertical which do have constant convection coefficients
        # T_in is the interior surface temperature in the given space
        T2 = temp_record[surface.obj_id + "_outside_surface"]
        T3 = temp_record[surface.obj_id + "_inside_surface"]
        T_in = (C4*T3/dt+T_space2/R5+(C4/dt+1/R3+1/R5)*(C2*T2/dt+T_space/R1)*R3) / ((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3)
        T_out = (C2*T2/dt+T_space/R1+(C2/dt+1/R3+1/R1)*(C4*T3/dt+T_space2/R5)*R3) / ((C4/dt+1/R3+1/R5)*(C2/dt+1/R3+1/R1)*R3-1/R3)

        # Update temp_record dictionary
        # Add the newly calculated numbers into the dictionary:
        temp_record[surface.obj_id + "_outside_surface"] = T_out
        temp_record[surface.obj_id + "_inside_surface"] = T_in

        Q_flux = round(hc * A *(T_in-T_space), 6)
        #print Q_flux

        return transmitted_win, Q_flux

    def underground_wall(self, surface, A, R3, C, T_space, temp_record):
        transmitted_win = 0
        dt = 3600
        hc = 3.096
        R5 = 1/hc
        C2 = C/2
        # Set the default ground temperature as 18 C from Weather.py
        ground_temp = (T_space - 2)
        T3 = temp_record[surface.obj_id + "_inside_surface"]
        A1 = C2/dt*T3 + (T_space/R5) + (ground_temp/R3) # +G_space_record(i_space,i_time);
        A2 = C2/dt + 1/R5 + 1/R3
        T_in = A1/A2
        T_out = ground_temp

        # Update temp_record dictionary
        # Add the newly calculated numbers into the dictionary:
        temp_record[surface.obj_id + "_outside_surface"] = T_out
        temp_record[surface.obj_id + "_inside_surface"] = T_in

        Q_flux = round(hc * A * (T_in-T_space), 6)

        return transmitted_win, Q_flux

    def raised_floor(self, surface, hc_external, T1, A, A_noWin, weather, R3, C, A_noOp, T_space, temp_record):
        # this condition was not a part of version 2
        pass



