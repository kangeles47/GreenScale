#-------------------------------------------------------------------------------
# Name:        Space.py
# Purpose:     Green Scale Tool TM Space Module (handles model at the space level)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
from objects.BaseElement import BaseElement
import math
from objects.Surface import Surface
from objects.HeatCalculation import HeatCalculation
from objects.TransmittedSolar import TransmittedSolar
import numpy
from GSUtility import GSUtility
from numpy import *
import logging
#TM_coder = logging.getLogger('TMcoder_V1')
TM_user = logging.getLogger('TMuser_V1')


class Space(BaseElement):

    # Desired temperature (in K)
    # Default is 22C

    # Surfaces belonging to the space
    surfaces = list()

    # Calculation from the model
    # Energy required hourly (in watts)
    Q_hour_W = list()

    def calculate_space_heatflux(self, space, weather, spaces_dict, temp_record, Coeff, ShadowsFlag, ns, shadow_record, shade_surf_list, surfaces_dict, A, missing_surfaces, terrain, G_space_record, areaDict, areaWinDict, shadowRatios, shadowRatioIndex):
        #print "Reaching Space function..."
        #l = space.obj_id
        #TM_coder.info("   Entering function: calculate_space_heatflux()")

        surf = Surface()
        space_hour_q = 0
        heat_calculation = HeatCalculation()
        transmitted_solar = TransmittedSolar()
        G_space = 0
        Q_space = 0
        Q_floor = 0
        floorID = "none"
        A_noOp_floor = 0
        current_floor = 0
        Q_top = 0
        #h_space = self.get_height_floorspace(space) # This will need to get rid of the extra 0,0,0 coordinate appended to match matlab eventually, check that its commented out below
        #print "h_space: ", space.obj_id, h_space
        h_surface = 0

        h_space, current_floor = self.get_height_floorspace(space)  # Finds the floor surface and gets the height from the ground---note (0,0,0 problem not resolved from Matlab)
        A_noOp_floor = surf.get_A_noOp(current_floor, areaDict, areaWinDict)
        current_floor_type = current_floor.obj_type
        #print h_space

        for surface in space.surfaces:
            #print "found one: ", surface.obj_id, surface.obj_type
            #h_space, current_floor = self.get_height_floorspace(space)
            #A_noOp_floor = surf.get_A_noOp(current_floor)
            #print "h_space: ", space.obj_id, h_space
            #print surface.obj_id
            # Regardless of the type of surface, calculate the heatflux for this surface, adjusting as appropriate
            #h_space = self.get_height_floorspace(space)
            # h_space = Infor_surface{13,i_space} = getHeightSurface
            h_surface = self.get_height(surface)  # Finds the midpoint of the surface from the ground for all surface locations---note (0,0,0 problem not resolved from Matlab)
            #print "h_surface: ", surface.obj_type, surface.obj_id, h_surface

            # Assuming all floors will be flat--does not yet account for surfaces that are slanted!
            if surface.obj_type == "Ceiling":
                #print "found one: ", surface.obj_id
                #loop coordinates to check for z similarities to determine if it is horizontal or vertical
                z0 = surface.cps[0][2]
                z1 = surface.cps[1][2]
                z2 = surface.cps[2][2] # If a surface is defined as at least three points
                #for x, y, z in surface.cps:
                #    print z
                if z0 == z1 and z1 == z2:
                    surface.obj_type = "InteriorFloor"
                    #print z0, z1, z2
                else:
                    surface.obj_type = "InteriorWall"
                    #print z0, z1, z2
                #print surface.obj_type

            if surface.obj_type == "ExteriorWall" or surface.obj_type == "Roof" or surface.obj_type == "InteriorWall" or surface.obj_type == "UndergroundWall":
                G_window, Q_surface = surf.calculate_surface_heatflux(weather, spaces_dict, surface, temp_record, Coeff, space, h_surface, ShadowsFlag, ns, shadow_record, shade_surf_list, surfaces_dict, A, terrain, areaDict, areaWinDict, shadowRatios, shadowRatioIndex)
                #print "h_surface: ", surface.obj_type, surface.obj_id, h_surface
                Q_space += Q_surface
                #print Q_surface
                G_space += G_window
            elif surface.obj_type == "Air":
                # According to Na, should skip surfaces of Air for thermal calculations
                continue
            elif surface.obj_type == "InteriorFloor" and h_space < h_surface:
                # means this is the top
                Q_top = heat_calculation.get_top_heat(space, surface, weather, spaces_dict, temp_record, Coeff, G_space_record, areaDict, areaWinDict)
                Q_space += Q_top
                #if surface.obj_id == "su-6":
                    #print Q_top    # Known issue with the heat flux for this calculation
                #A_noOp_floor = surf.get_A_noOp(surface)  # for now we are assuming there are no openings in a floor, will have to be adjusted later
                if A == 0:
                    # If it is the first surface of the space, label the space ID in the log file:
                    la = str(surface.obj_id)
                    lb = str(surface.obj_type)
                    #TM_user.info("%s,surface area,%s,%s" % (la, A_noOp_floor, lb))
            elif surface.obj_type == "Column":
                # Not considering columns in the middle of a space for TM for now...embedded in the wall may need further attention
                pass
            # As of version 4 of MatLab, this elif and else was removed...?
            """
            elif surface.obj_type == "InteriorFloor" or surface.obj_type == "RaisedFloor" or surface.obj_type == "UndergroundSlab" or surface.obj_type == "SlabOnGrade":
                if h_space == h_surface:
                    floorSurface = surface
                    current_floor_type = surface.obj_type
                    A_noOp_floor = surf.get_A_noOp(surface)  # for now we are assuming there are no openings in a floor, will have to be adjusted later
                if A == 0:
                    # If it is the first surface of the space, label the space ID in the log file:
                    la = str(surface.obj_id)
                    lb = str(surface.obj_type)
                    TM_user.info("%s,surface area,%s,%s" % (la, A_noOp_floor, lb))

            else:
                print "Surface Not Found: ", surface.obj_type
                if surface.obj_type not in missing_surfaces:
                    missing_surfaces[surface.obj_type] = surface.obj_id
                TM_user.info("Need object type: ,%s" % surface.obj_type)
            """
            #if surface.obj_type == "InteriorFloor" or surface.obj_type == "RaisedFloor" or surface.obj_type == "UndergroundSlab" or surface.obj_type == "SlabOnGrade" or surface.obj_type == "ExteriorWall" or surface.obj_type == "Roof" or surface.obj_type == "InteriorWall" or surface.obj_type == "UndergroundWall":
            #    pass
            #else:
            #    print "Surface Not Found: ", surface.obj_type
            #    if surface.obj_type not in missing_surfaces:
            #        missing_surfaces[surface.obj_type] = surface.obj_id
            #    TM_user.info("Need object type: ,%s" % surface.obj_type)

                #raise Exception("Surface Type Not Found So Nothing Calculated...for this surface")
            #elif surface.obj_type == "InteriorFloor" and h_space == h_surface:
                # means this is the bottom
                #current_floor_type = surface.obj_type
                #A_noOp_floor = surface.get_A_noOp(surface)  # for now we are assuming there are no openings in a floor, will have to be adjusted later
                #Q_floor = self.calculate_Q_floor(space, surface, current_floor_type, A_noOp_floor, weather, G_space, spaces_dict, temp_record, Coeff)
                # could make a seperate floor list to save int he next loop, but since only about 6-12 surfaces, may not be worth another list...
                # may also have to adjust later for multi-floored spaces
            #print "Q_space: ", Q_space

        G_space1 = G_space
        G_space = G_space1/A_noOp_floor  #Area of the floor, but want noOp eventually to omit stairwell spaces in area as I have accounted for here
        #print "floor type: ", floorSurface.obj_type
        #print "G_space: ", G_space
        #print space.obj_id
        G_space_record[space.obj_id] = G_space
        #print G_space, G_space_record[space.obj_id]
        #C = surf.get_C_surface(A_noOp_floor, A_noOp_floor, current_floor, Coeff)
        #print C, current_floor.obj_type, current_floor.obj_id

        if current_floor_type == "InteriorFloor":
            Q_floor = heat_calculation.get_floor_heat(space, current_floor, weather, G_space, spaces_dict, A_noOp_floor, temp_record, Coeff, areaDict, areaWinDict)
            #print Q_floor

        elif current_floor_type == "RaisedFloor":
            # UndergroundSlab and SlabOnGrade are like floor, and there is only one space
            Q_floor = heat_calculation.get_raised_floor_heat(current_floor, weather, G_space, A_noOp_floor, temp_record, space, spaces_dict, h_surface, terrain, Coeff, areaDict, areaWinDict)
            #print "Q_floor: ", Q_floor

        elif current_floor_type == "UndergroundSlab" or current_floor_type == "SlabOnGrade":
            Q_floor = heat_calculation.get_ground_heat(current_floor, weather, G_space, A_noOp_floor, temp_record, space, spaces_dict, Coeff, areaDict, areaWinDict)
            #print "Q_floor: ", Q_floor

        else:
            Q_floor = 0
            print "Surface Floor Not Found: ", current_floor_type
            if current_floor_type not in missing_surfaces:
                missing_surfaces[current_floor_type] = current_floor_type
            #raise Exception("Surface Type Not Found So Nothing Calculated...for this surface")
            TM_user.info("Need object type: ,%s" % current_floor_type)

        # Sum all the Q for the surfaces of the space
        space_hour_q = Q_space + Q_floor
        if space_hour_q < 0:
            space_hour_q = math.fabs(space_hour_q)

        # Return the heat flux of this whole space from the sum of the surface calculations for this hour
        return round(space_hour_q, 6)

    def get_height_floorspace(self, space):
        # Calculating the height of the floor relative to the ground, i.e. ground floor surface == 0

        z_space = 0
        current_floor_type = "Floor"  #Given a Default of 'InteriorFloor' --- May adjust later as needed
        missing_floors = list()
        for surface in space.surfaces:
            if surface.obj_type == "InteriorFloor" or surface.obj_type == "RaisedFloor" or surface.obj_type == "UndergroundSlab" or surface.obj_type == "SlabOnGrade":
                z_space = self.get_height(surface)
                current_floor_type = surface
                #print "FloorHeight: ", surface.obj_type, z_space
                break
            else:
                # While floor types are not found, add to list and write them to the log file, giving defualt in the mean time
                missing_floors.append(surface.obj_type)
        if current_floor_type == "Floor":
            for item in missing_floors:
                TM_user.info("Need object type (Have set to be InteriorFloor until resolved): ,%s" % (item))
                #print "these floor types: ", item
            current_floor_type = "InteriorFloor"

        #check_cp = 0
        #max_height = 0
        #min_height = 0
        #temp_min = 0
        #check_cp2 = 0
        #height_iterator = 0
        #test = 0
        # Non-flat surfaces: Is the average value of the maximum & minimum Z-coordinates
        #print "surface.cps: ", surface.cps  #print a list of 3-item tuples
        # Find max and minimum wall points to count for the cases when floor surface is not constant (i.e. stairs/ramps)
        #for x, y, z in space.scps:
        #    if check_cp == 0:
        #        max_height = z
        #        min_height = z
        #        check_cp = 1
        #    else:
        #        if z > max_height:
        #            max_height = z
        #        elif z < min_height:
        #            min_height = z

        # This will yield 0 for z_surface when it is a ground level floor
        #z_space = 0.5*(max_height + min_height) * 0.3048
        #z_space = ((max_height + min_height) * 0.3048)/2

        return round(z_space, 6), current_floor_type

    def get_height(self, surface):
        # Getting the height of a surface at the surface center point relative to the ground
        # SurfaceHeight=(max(Infor_surface_simp(i_surface).Coordinate(:,3))+min(Infor_surface_simp(i_surface).Coordinate(:,3)))/2;
        #conversion = math.pi/180
        #print "function used"

        rowAdded = surface.cps
        # This if statement is giving an extra coordinate to triangular walls as matlab does...but shouldn't---this if section should be removed for accuracy but is currently being used for validation against other matlab calculations
        # contacted Na and asked her to revise this section...
        #if len(surface.cps) == 3:
        #    square = (0, 0, 0)
        #    rowAdded.append(square)

        #print len(surface.cps)

        z = zeros((len(rowAdded), 1))
        row = 0
        while row < len(z):
            col = 0
            z[row] = surface.cps[row][2]
            #print surface.obj_id, row
            row += 1


        #z_surface = float(surface.cps[0][2])*0.3048
        #print surface.obj_id, z_surface
        z_surface = math.fabs( ( max(z[:, 0]) + min(z[:, 0]) ) / 2 )
        #print surface.obj_id, z_surface

        return round(z_surface, 6)

    #def get_A_floor(self, surface):
        # Calculates the area of the surface in cm2 minus all the window openings
        #A = round(self.height * self.width * 0.3048 * 0.3048, 4)
        # The remove the A of each of the openings
        #for opening in self.openings:
            # Only subtract if window
           # if opening.obj_type == "Air, FixedWindow, or OperableSkylight...if string ID of the Floor minus openings like those created by staircases":
                #A -= opening.get_A_noOp()

        #return A

