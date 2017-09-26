#-------------------------------------------------------------------------------
# Name:        GreenscaleSpace.py
# Purpose:     Green Scale Tool EE Space Module (Handles space level EE calculations)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
from objects.BaseElement import BaseElement
import math
from objects.GreenscaleSurface import GreenscaleSurface
from numpy import *
from GSUtility import GSUtility
import logging
EE_coder = logging.getLogger('EEcoder_V1')
EE_user = logging.getLogger('EEuser_V1')
Assembly = logging.getLogger('Assembly_V1')


class GreenscaleSpace(BaseElement):

    # Desired temperature (in K)
    # Default is 22C
    #desired_temp_K = 22+273  #Infor_space{10,i_space} desired temp for the SPACE...T_space been worked into a dictionary set up from the file

    # Surfaces belonging to the space
    surfaces = list()

    def calculate_spaceEE(self, input_dir, space, duplicates, assembly, assembly_descript, areaDict, areaWinDict, missing_materials, material_dictionary, MaterialDict):
        surfaceEE = GreenscaleSurface()
        EEspaceTotal = list()

        sqr = 0
        rnd = 0
        EE_total_col = 0
        EW_total_col = 0
        h_surface = 0
        #print space.obj_id
        for surface in space.surfaces:
            if surface.obj_type == "ExteriorWall" or surface.obj_type == "InteriorWall" or surface.obj_type == "UndergroundWall":
                h_surface = self.get_height(surface)
                #print surface.obj_id, surface.obj_type, h_surface
                break
        for surface in space.surfaces:
            if surface.obj_type == "Column":
                if surface.columnType == "round":
                    #surface.columnSize
                    EE_col = surfaceEE.calculate_surfaceEE(input_dir, surface, assembly, assembly_descript, areaDict, areaWinDict, h_surface, missing_materials, material_dictionary, MaterialDict)
                    EE_total_col += EE_col[0]
                    EW_total_col += EE_col[1]
                if surface.columnType == "square":
                    #surface.columnSize
                    EE_col = surfaceEE.calculate_surfaceEE(input_dir, surface, assembly, assembly_descript, areaDict, areaWinDict, h_surface, missing_materials, material_dictionary, MaterialDict)
                    EE_total_col += EE_col[0]
                    EW_total_col += EE_col[1]

        space_EE = 0
        space_EW = 0
        for surface in space.surfaces:
            #print "type: ", surface.obj_type
            # We do not need to add surfaces of Air to Sum Embodied Energy
            if surface.obj_type == "Air":
                #print "skipped: ", surface.obj_id, " since it is labeled as AIR"
                continue
            if surface.obj_type == "Column":
                #print "skipped: ", surface.obj_id, " since it was calculated above"
                continue
            # Check if this surface EE has already been added - occurs with shared walls and floors
            if surface.obj_id not in duplicates:
                duplicates.append(surface.obj_id)
                # EE_surface in this case returns a list pair of surface EE and surface EW
                EE_surface = list()
                EE_surface = surfaceEE.calculate_surfaceEE(input_dir, surface, assembly, assembly_descript, areaDict, areaWinDict, h_surface, missing_materials, material_dictionary, MaterialDict)
                #if surface.obj_id == "su-60" or surface.obj_id == "su-146" or surface.obj_id == "su-154":
                    #tempEE = tempEE + EE_surface[0]
                    #print surface.obj_id, EE_surface[0]
                space_EE += EE_surface[0]
                space_EW += EE_surface[1]
            else:
                continue
        EE_user.info("check for duplicates in space:, %s" % (duplicates))  # Record the S-ID, S-Type, EE, EW
        #print "check for duplicates: ", duplicates

        #print "space_EE: ", space_EE  # Giving 81726813.4385 for model with one room
        #print "space_EW: ", space_EW  # Giving 22801.780949 for model with one room
        space_EE = EE_total_col + space_EE
        space_EW = EW_total_col + space_EW
        EEspaceTotal.append(round(space_EE, 6))
        EEspaceTotal.append(round(space_EW, 6))

        #print "EEspaceTotal: ", EEspaceTotal  # Giving [81726813.438525, 22801.780949] for one room model

        # Return the EE and EW of this whole space from the sum of the surface calculations
        return EEspaceTotal

    def get_height(self, surface):
        # Altered from space.py to get a height of a space for the volume calculation of column surfaces

        rowAdded = surface.cps
        # This if statement is giving an extra coordinate to triangular walls as matlab does...but shouldn't---this if section should be removed for accuracy but is currently being used for validation against other matlab calculations
        # contacted Na and asked her to revise this section...
        #if len(surface.cps) == 3:
        #    square = (0, 0, 0)
        #    rowAdded.append(square)

        z = zeros((len(rowAdded), 1))
        row = 0
        while row < len(z):
            col = 0
            z[row] = surface.cps[row][2]
            row += 1

        #z_surface = float(surface.cps[0][2])*0.3048
        #print max(z[:, 0]), min(z[:, 0])
        z_surface = ( max(z[:, 0]) - min(z[:, 0]) )
        #print z_surface

        return round(z_surface, 6)
