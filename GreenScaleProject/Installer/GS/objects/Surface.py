#-------------------------------------------------------------------------------
# Name:        Surface.py
# Purpose:     Green Scale Tool TM Surface Module (handles model at the surface level)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
import math
from objects.BaseElement import BaseElement
from objects.Temperature import Temperature
from objects.Area import Area
from GSUtility import GSUtility
import logging
#TM_coder = logging.getLogger('TMcoder_V1')
TM_user = logging.getLogger('TMuser_V1')


class Surface(BaseElement):
    # Cartesian point
    cartesian_point = None

    # Space the surface is in
    space = None
    gbxml = ""

    # Openings
    openings = list()
    constructions = list()
    layers = list()
    materials = list()

    #def __init__(self):
        # set the first temperature by default
        #self.Tp.append(14.5+273)

    def is_exterior(self):
        """
        Determines if the surface is exterior or interior
        """
        exterior_types = ["ExteriorWall", "Roof", "InteriorWall", "UndergroundWall", "RaisedFloor"]
        return self.obj_type in exterior_types

    def calculate_surface_heatflux(self, weather, spaces_dict, surface, temp_record, Coeff, space, h_surface, ShadowsFlag, ns, shadow_record, shade_surf_list, surfaces_dict, Aflag, terrain, areaDict, areaWinDict, shadowRatios, shadowRatioIndex):
        """
        Calculates the heatflux of the surface.
        Different for each type.
        Takes a weather for a certain tstep.
        """
        #print "Reaching Surface function..."

        # First get the As
        A_total = self.get_A(surface, areaDict, areaWinDict)
        if Aflag == 0:
            # If it is the first surface of the space, label the space ID in the log file:
            la = str(surface.obj_id)
            lb = str(surface.obj_type)
            #TM_user.info("%s,surface area,%s,%s" % (la, A_total, lb))
        A_noWin = self.get_A_noWin(surface, areaDict, areaWinDict)
        A_noOp = self.get_A_noOp(surface, areaDict, areaWinDict)
        T_space = spaces_dict[space.obj_id][1]
        T1 = weather["t_outside"]
        hc_external = float(self.get_hc_external(weather, surface, h_surface, terrain))
        transmitted_win = 0
        Q_flux = 0

        # need the surface related information, T_space, U, R3
        U = self.get_U_surface_e(A_total, A_noOp, surface, areaWinDict)  # U = Infor_surface{11,i_surface}; Defined Below
        #print U
        R3 = 1/U
        # Using calculations from: self.surface.constr.layer.C  # Infor_surface{10, i_surface} ; from gbXML
        C = self.get_C_surface(A_total, A_noOp, surface, Coeff, areaWinDict)  # need to pass surface and opening ids
        #print C

        temperature = Temperature()

        #Sub-routines for each wall type based on the returned hc_external
        # This hc is different for each surface type so moved under this sub-routine area
        #hc = 3.076 sent this to the Temperature Object
        if surface.obj_type == "ExteriorWall":
            transmitted_win, Q_flux = temperature.exterior_wall(surface, hc_external, T1, A_total, A_noWin, weather, R3, C, T_space, temp_record, ShadowsFlag, ns, shadow_record, shade_surf_list, surfaces_dict, areaWinDict, shadowRatios, areaDict, shadowRatioIndex)
            #print Q_flux
        if surface.obj_type == "Roof":
            transmitted_win, Q_flux = temperature.roof(surface, hc_external, T1, A_total, A_noWin, weather, R3, C, A_noOp, T_space, temp_record, ShadowsFlag, ns, shadow_record, shade_surf_list, surfaces_dict, areaWinDict, shadowRatios, areaDict, shadowRatioIndex)
            #print Q_flux  # Matches for Four Room
        if surface.obj_type == "InteriorWall":
            transmitted_win, Q_flux = temperature.interior_wall(surface, A_total, R3, C, spaces_dict, T_space, temp_record)
            #print Q_flux  # Matches for Four Room
        if surface.obj_type == "UndergroundWall":
            transmitted_win, Q_flux = temperature.underground_wall(surface, A_total, R3, C, T_space, temp_record)  # No instance of yet to test
        if surface.obj_type == "RaisedFloor":
            # This will eventually need some values when we start using raised floors
            transmitted_win, Q_flux = temperature.raised_floor(surface, hc_external, T1, A_total, A_noWin, weather, R3, C, A_noOp, T_space, temp_record)  # Not instance of yet to test

        return transmitted_win, Q_flux

    def get_hc_external(self, weather, surface, h_surface, terrain):
        """
        Get the external convection coefficient of exterior surfaces
        """
        roughness = surface.construction[0].roughness_unit  # Change back to this line...left as below to match Na's
        if roughness == "VeryRough":
            D = 11.58
            E = 5.894
            F = 0
        elif roughness == "Rough":
            D = 12.49
            E = 4.065
            F = 0.028
        elif roughness == "MediumRough":
            D = 10.79
            E = 4.192
            F = 0.0
        elif roughness == "MediumSmooth":
            D = 8.23
            E = 4.0
            F = -0.057
        elif roughness == "Smooth":
            D = 10.22
            E = 3.1
            F = 0.0
        elif roughness == "VerySmooth":
            D = 8.23
            E = 3.33
            F = -0.036
        else:
            D = 8.23
            E = 4.0
            F = -0.057
            print "No Roughness Value Found so Set Default Values of 8.23,4.0,-0.057"

        wind_speed_temp = weather["wind_speed"]
        # Terrain Lookup Table
        if terrain == 'Flat or Open Countryside':
            sigma = 270
            a = 0.14
        elif terrain == 'Rough or Wooded Country':
            sigma = 370
            a = 0.22
        elif terrain == 'Towns and City Scapes':
            sigma = 460
            a = 0.33
        elif terrain == 'Ocean Front Areas':
            sigma = 210
            a = 0.10
        elif terrain == 'Urban, Industrial, or Forest':
            sigma = 370
            a = 0.22
        else:
            sigma = 370
            a = 0.22
            print "No Terrain Type Found so Set Default Values of 370,0.22"
        terrain_sigma = sigma
        terrain_cof = a

        # Adjust the wind speed...Stable air above human inhabited areas:
        #wind_speed = wind_speed_temp * ((h_surface / 10) ** 0.5)  # This was the line used to get wind_speed before terrain was added
        # Wind speed corrected for terrain differences;
        wind_speed = wind_speed_temp * ((270/10) ** 0.14) * (h_surface/terrain_sigma) ** terrain_cof
        #print wind_speed
        # Calculate the hc_external
        # hc_external= D+E*Wind_speed+F*Wind_speed^2
        hc_external = D + (E * wind_speed) + (F * wind_speed ** 2)

        # depending on the direction of the wind adjust the hc_external...as of versions 3 and 4 this part seems omitted
        #x = abs(wind_speed_dir - azimuth)
        #if x > 100:
        #    if x < 260:
        #        hc_external *= 0.5
        #print "hc_external : ", hc_external, D, E, F

        return round(hc_external, 5)

    def get_A(self, surface, areaDict, areaWinDict):
        # Calculates the total A of the surface.
        #A = round(surface.height * surface.width * 0.3048 * 0.3048, 6)
        #print A
        #area = Area()
        #A = area.surfaceArea(surface.cps, surface.azimuth, surface.tilt, surface)
        #A = area.getArea(surface.obj_id)
        A = areaDict[surface.obj_id]
        #print "from TM", A
        return A

    def get_A_noWin(self, surface, areaDict, areaWinDict):
        # Calculates the area of the surface in cm2 minus all the window openings
        #A = round(surface.height * surface.width * 0.3048 * 0.3048, 6)
        #area = Area()
        #A = area.surfaceArea(surface.cps, surface.azimuth, surface.tilt, surface)
        #A = area.getArea(surface.obj_id)
        A = areaDict[surface.obj_id]

        # The remove the A of each of the openings
        for opening in surface.openings:
            if opening.obj_type != "Air":
                # Only subtract if window
                if opening.obj_type == "OperableWindow" or opening.obj_type == "FixedWindow":
                    #A -= (opening.height * opening.width * 0.3048 * 0.3048)
                    #A -= area.surfaceArea(opening.ocps, surface.azimuth, surface.tilt, opening)
                    #A -= area.getArea(opening.obj_id)
                    A -= areaWinDict[opening.obj_id]
                    #print A
        #print surface.obj_id
        return A

    def get_A_noOp(self, surface, areaDict, areaWinDict):
        # Calculates the area of the surface in cm2 minus all the window openings
        #A = round(surface.height * surface.width * 0.3048 * 0.3048, 6)
        #area = Area()
        #A = area.surfaceArea(surface.cps, surface.azimuth, surface.tilt, surface)
        #A = area.getArea(surface.obj_id)
        A = areaDict[surface.obj_id]

        # The remove the A of each of the openings
        for opening in surface.openings:
            if opening.obj_type != "Air":
                # Only subtract if window
                if opening.obj_type == "OperableWindow" or opening.obj_type == "FixedWindow" or opening.obj_type == "NonSlidingDoor":
                    #A -= (opening.height * opening.width * 0.3048 * 0.3048)
                    #A -= area.surfaceArea(opening.ocps, surface.azimuth, surface.tilt, opening)
                    #A -= area.getArea(opening.obj_id)
                    #A -= areaWinDict[opening.obj_id]
                    A -= areaWinDict[opening.obj_id]
        #print A
        return round(A, 6)

    def get_U_surface_e(self, A_total, A_noOp, surface, areaWinDict):
        # Calculates the U for the whole surface: surface, windows, and doors combined
        #UA=Infor_surface_simp(i_surface).U*A_noOpen + sum([Infor_surface_simp(i_surface).Opening(:).U].*[Infor_surface_simp(i_surface).Opening(:).Area]);
        #Infor_surface_simp(i_surface).U_ave=UA/Infor_surface_simp(i_surface).Area;

        ua = 0
        ua_win = 0
        UA_openings = 0
        #area = Area()
        #print "number of openings: ", len(surface.openings)
        if len(surface.openings) > 0:
            for opening in surface.openings:
                if opening.obj_type != "Air":
                    # Only subtract if window
                    if opening.obj_type == "OperableWindow" or opening.obj_type == "FixedWindow":
                        u_win = self.get_U_win(opening)
                        #A_Op = round(opening.height * opening.width * 0.3048 * 0.3048, 6)
                        #A_Op = area.surfaceArea(opening.ocps, surface.azimuth, surface.tilt, opening)
                        #A_Op = area.getArea(opening.obj_id)
                        A_Op = areaWinDict[opening.obj_id]
                        ua_win += u_win * A_Op
                    elif opening.obj_type == "NonSlidingDoor":
                        u_op = self.get_U_opening(opening)
                        #A_Op = round(opening.height * opening.width * 0.3048 * 0.3048, 6)
                        #A_Op = area.surfaceArea(opening.ocps, surface.azimuth, surface.tilt, opening)
                        #A_Op = area.getArea(opening.obj_id)
                        A_Op = areaWinDict[opening.obj_id]
                        ua += u_op * A_Op

            U1 = self.get_U_surface(A_noOp, surface)
            UA = U1*A_noOp + (ua_win + ua)

            U = UA / A_total
            # Get the total with the surface, windows, and doors:
            #UA = UA + U1*A_noOp + UA_win
            #U = UA/A_total
        else:
            U = self.get_U_surface(A_noOp, surface)

        #if surface.obj_id == "su-3":
            #print "This is the U-value: ", U

        return round(U, 6)

    def get_U_win(self, opening):
        # Want the U-value of the windows only
        # if isempty(Infor_surface{5, 1}) ???
        U_win = 0
        #for opening in surface.openings:
        if opening.obj_type != "Air":
            # Want only the windows, so proceed only if the opening in the list is a known window type
            if opening.obj_type == "OperableWindow" or opening.obj_id == "FixedWindow":
                U_win = opening.material[0].u_value
            else:
                U_win = 0

        return round(U_win, 4)

    def get_U_opening(self, opening):
        # Want the U-value of the openings other than windows
        # Get U value of each opening. Doors and windows are different
        U = 0
        #for opening in surface.openings:
        if opening.obj_type != "Air":
            if opening.obj_type == "NonSlidingDoor":
                U = opening.material[0].u_value
            elif opening.obj_type == "OperableSkylight":
                U = opening.material[0].u_value  # Set to zero for now due to the fact that these do not get a U-value from Revit
            elif opening.obj_type == "FixedWindow":
                U = opening.material[0].u_value  # Set to zero for now due to the fact that these do not get a U-value from Revit
            elif opening.obj_type == "Air":
                U = 0  # Set to zero for now due to the fact that these do not get a U-value from Revit
            else:
                U = 0  # Set to zero for now due to the fact that these do not get a U-value from Revit

        return round(U, 6)

    def get_U_surface(self, A_noOp, surface):
        # if strncmp(Infor_surface{1, surface_id},'X',1)
        # U = 0 ;  # I do not think this is necessary since the effective area is what is considered in python
        U = 0
        if A_noOp <= 0:
            U = 0
        else:
            U = surface.construction[0].u_value
            #print "U for this surface from gbxml tree: ", U

        return round(U, 6)

    def get_C_surface(self, A_total, A_noOp, surface, Coeff, areaWinDict):
        # Calculates the C of the whole surface from the C value we already have for each material layer
        #area = Area()
        #CA=Infor_surface_simp(i_surface).C*A_noOpen + sum([Infor_surface_simp(i_surface).Opening(:).C].*[Infor_surface_simp(i_surface).Opening(:).Area]);
        #Infor_surface_simp(i_surface).C_ave=CA/Infor_surface_simp(i_surface).Area;
        #print "reaching this C"

        #Coeff = 1  # Passed from Main so that this can be set as desired easily later on, Na's Ex is 0.45
        C = 0
        C_door = 0
        C_door_total = 0

        # get the C_total calculated in gbXML tree from the layers function for this surface
        C_wall = surface.construction[0].layer[0].C_Total
        C_wall_total = (C_wall*A_noOp)
        #print "wall ", C_wall, "  ", A_total, "  ", A_noOp

        # get the total C for the total door area in this surface (C value of a window = 0)
        for opening in surface.openings:
            if opening.obj_type != "Air":
                if opening.obj_type == "NonSlidingDoor":
                    #A_this_door = round(opening.height * opening.width * 0.3048 * 0.3048, 6)
                    #A_this_door = area.surfaceArea(opening.ocps, surface.azimuth, surface.tilt, opening)
                    #A_this_door = area.getArea(opening.obj_id)
                    A_this_door = areaWinDict[opening.obj_id]
                    #print "area of door is: ", A_this_door
                    C_door = opening.material[0].layer[0].C_Total
                    #print "c of door is: ", C_door
                    C_door_total += (A_this_door * C_door)
                    # C = 0 # resets in Na's code ???
        #print "door: ",C_door_total

        C = C_wall_total + C_door_total
        C = C/A_total
        C = Coeff*C
        #C = float(C)

        return round(C, 6)



