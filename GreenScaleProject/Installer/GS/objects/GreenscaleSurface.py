#-------------------------------------------------------------------------------
# Name:        GreenscaleSurface.py
# Purpose:     Green Scale Tool EE Surface Module (Handles surface level EE calculations)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
import math
from objects.BaseElement import BaseElement
from objects.Area import Area
from objects.GreenscaleEE import GreenscaleEE
import logging
from GSUtility import GSUtility
EE_coder = logging.getLogger('EEcoder_V1')
EE_user = logging.getLogger('EEuser_V1')
Assembly = logging.getLogger('Assembly_V1')


class GreenscaleSurface(BaseElement):
    # Cartesian point
    cartesian_point = None

    # Space the surface is in
    space = None
    gbxml = ""

    # opening types
    #openingTypes = dict()

    # Openings
    openings = list()
    constructions = list()
    layers = list()
    materials = list()
    #assembly = dict()

    def calculate_surfaceEE(self, input_dir, surface, assembly, assembly_descript, areaDict, areaWinDict, h_surface, missing_materials, material_dictionary, MaterialDict):
        tempEE = 0
        tempEW = 0
        surfaceEE = 0
        surfaceEW = 0
        # Class instance for each material set in a given surface
        energy = GreenscaleEE()
        total_surface_area = self.get_A(surface, areaDict, areaWinDict)
        #print total_surface_area
        solid_surface_area = self.get_A_noOp(surface, total_surface_area, areaDict, areaWinDict)
        effective_area = self.get_A_effective(surface, total_surface_area, areaDict, areaWinDict)
        openingTypes = dict()  # Start an empty dictionary each iteration
        surfaceEEtotal = list()

        #print "the effective area of this surface: ", surface.obj_id, " is: ", effective_area

        # Can just do the whole surface at once if no windows or doors or openings: (may need to adjust for a single wall of two solid surface types)
        if total_surface_area == solid_surface_area:
            double = list()
            double = energy.calculate_EE(input_dir, surface, total_surface_area, h_surface, missing_materials, material_dictionary, MaterialDict)
            surfaceEE += double[0]
            surfaceEW += double[1]
            surfaceEEtotal.append(surfaceEE)
            surfaceEEtotal.append(surfaceEW)
            #print surface.obj_id, surfaceEE

            if surface.construction[0].obj_id not in assembly:
                assembly[surface.construction[0].obj_id] = double[0]
                #if surface.construction[0].obj_id == "cons-2":
                #    print double[0]
            else:
                assembly[surface.construction[0].obj_id] = double[0] + assembly[surface.construction[0].obj_id]
                #if surface.construction[0].obj_id == "cons-2":
                #    print double[0]

            if surface.construction[0].obj_id not in assembly_descript:
                mat_list = list()
                for material in surface.construction[0].layer[0].material:
                    mat_list.append(material.name)
                assembly_descript[surface.construction[0].obj_id] = mat_list

            EE_user.info("Total Surface Energy:, %s, %s, Sq.Feet, %s, %s, Btu/lb, %s, Gal/lb" % (surface.obj_id, total_surface_area, surface.obj_type, surfaceEE, surfaceEW))  # Record the S-ID, Area, S-Type, EE, EW
        else:
            # Get effective surface area EE
            double = list()
            double = energy.calculate_EE(input_dir, surface, effective_area, h_surface, missing_materials, material_dictionary, MaterialDict)
            surfaceEE += double[0]
            surfaceEW += double[1]
            #print surface.obj_id

            if surface.construction[0].obj_id not in assembly:
                assembly[surface.construction[0].obj_id] = double[0]
                #if surface.construction[0].obj_id == "cons-2":
                    #print double[0]
            else:
                assembly[surface.construction[0].obj_id] = double[0] + assembly[surface.construction[0].obj_id]
                #if surface.construction[0].obj_id == "cons-2":
                    #print double[0]

            if surface.construction[0].obj_id not in assembly_descript:
                mat_list = list()
                for material in surface.construction[0].layer[0].material:
                    mat_list.append(material.name)
                assembly_descript[surface.construction[0].obj_id] = mat_list

            # Create dictionary of opening types and the total areas for that opening type in the surface
            for opening in surface.openings:
                #print "check: ", surface.obj_id, opening.obj_id, opening.obj_type
                if opening.obj_cons_ref is None:
                    #if opening.obj_cons_ref is None and opening.obj_type_ref is not None:
                    if opening.obj_type_ref not in openingTypes:
                        this_area = opening.width * opening.height
                        openingTypes[opening.obj_type_ref] = this_area
                    else:
                        this_area = opening.width * opening.height
                        openingTypes[opening.obj_type_ref] = openingTypes[opening.obj_type_ref] + this_area
                    #print opening.obj_id, opening.obj_type, opening.obj_type_ref
                elif opening.obj_type_ref is None:
                    #elif opening.obj_type_ref is None and opening.obj_cons_ref is not None:
                    if opening.obj_cons_ref not in openingTypes:
                        this_area = opening.width * opening.height
                        openingTypes[opening.obj_cons_ref] = this_area
                    else:
                        this_area = opening.width * opening.height
                        openingTypes[opening.obj_cons_ref] = openingTypes[opening.obj_cons_ref] + this_area
                    #print opening.obj_id, opening.obj_type, opening.obj_cons_ref
                else:
                    #print "for this: ", opening.obj_type_ref, opening.obj_id
                    #raise Exception("No Construction ID or Window Construction ID found for this opening in the loop")
                    U = GSUtility()
                    U.devPrint("No Construction ID or Window Construction ID found for this opening in the loop in GreenscaleSurface.py")
                #print opening.obj_id, opening.obj_type, opening.obj_cons_ref

            # Calculate the EE for each of the types listed in the dictionary and add it to the surfaceEE
            for key, entry in openingTypes.items():
                # Assuming entry here is the area stores at that location
                # This is returning the EE list of two items: EE and EW, so tempEE is a list
                double2 = list()
                double2 = energy.calculate_EE_dict(input_dir, surface, key, entry, h_surface, missing_materials, material_dictionary, MaterialDict)
                surfaceEE += double2[0]
                #print surfaceEE, surface.obj_id
                surfaceEW += double2[1]
                #print key, entry

                if key not in assembly:
                    assembly[key] = double2[0]
                    #print "check this key: ", key, double2[0]
                else:
                    assembly[key] = double2[0] + assembly[key]
                    #if surface.construction[0].obj_id == "cons-2":
                    #    print "there", surface.obj_id, double2[0], assembly[key], key
                    #print "check this key: ", key, double2[0]

                #if surface.construction[0].obj_id not in assembly_descript: #There is an error distinguishing btw door with const id and windows...
                    #mat_list = list()
                    #for material in surface.construction[0].layer[0].material:
                    #    mat_list.append(material.name)
                    #assembly_descript[surface.construction[0].obj_id] = mat_list

                # surfaceEE = solidEE + windowEE + doorEE + any unknown types...i.e. the dictionary per each surface
            surfaceEEtotal.append(surfaceEE)
            surfaceEEtotal.append(surfaceEW)
            EE_user.info("Total Surface Energy:, %s, %s, Sq.Feet, %s, %s, Btu/lb, %s, Gal/lb" % (surface.obj_id, total_surface_area, surface.obj_type, surfaceEE, surfaceEW))  # Record the S-ID, Area, S-Type, EE, EW

        #print surfaceEEtotal[0]
        #print "."

        return surfaceEEtotal

    def get_A(self, surface, areaDict, areaWinDict):   #  These area calcualtions can eventually be done with the Area() class method but needs further testing
        # Calculates the total A of the surface.
        # Was: A = round(surface.height * surface.width * 0.3048 * 0.3048, 6)...took out the conversion to leave it feet
        area = Area()
        #A = area.surfaceArea(surface.cps, surface.azimuth, surface.tilt, surface)
        #A = round(surface.height * surface.width, 6)
        #A = area.getArea(surface.obj_id)
        #if areaDict is not None:
        #    print "areaDict = not None", areaDict
        #print "test here", surface.obj_id
        A = areaDict[surface.obj_id]
        A /= 0.09290304  # The Area() is calculating and storing metric so needs to be put back into imperial for EE
        #print "1", A
        return A

    def get_A_effective(self, surface, A, areaDict, areaWinDict):
        # Calculates the total A of the surface.
        # Was: A = round(surface.height * surface.width * 0.3048 * 0.3048, 6)...took out the conversion to leave it feet
        area = Area()
        #A = area.surfaceArea(surface.cps, surface.azimuth, surface.tilt, surface)
        #A = round(surface.height * surface.width, 6)
        #print "A: total area: ", A
        # The remove the A of each of the openings
        for opening in surface.openings:
            # Only any opening type
            if opening.obj_type == "OperableWindow" or opening.obj_type == "FixedWindow" or opening.obj_type == "NonSlidingDoor" or opening.obj_type == "SlidingDoor" or opening.obj_type == "OperableSkylight" or opening.obj_type == "Air":
                #A -= area.surfaceArea(opening.ocps, surface.azimuth, surface.tilt, opening)
                #A -= (opening.height * opening.width)
                Ametric = areaWinDict[opening.obj_id]
                Ametric /= 0.09290304  # The Area() is calculating and storing metric so needs to be put back into imperial for EE
                A -= Ametric
            #print opening.height, opening.width
        #print "A is: ", A
        #print "2", A
        return A

    def get_A_noWin(self, surface, A, areaDict, areaWinDict):
        # Calculates the area of the surface in cm2 minus all the window openings
        area = Area()
        #A = area.surfaceArea(surface.cps, surface.azimuth, surface.tilt, surface)
        #A = round(surface.height * surface.width, 6)

        # The remove the A of each of the openings
        for opening in surface.openings:
            # Only subtract if window
            if opening.obj_type == "OperableWindow" or opening.obj_type == "FixedWindow":
                #A -= area.surfaceArea(opening.ocps, surface.azimuth, surface.tilt, opening)
                #A -= (opening.height * opening.width)
                Ametric = areaDict[opening.obj_id]
                Ametric /= 0.09290304  # The Area() is calculating and storing metric so needs to be put back into imperial for EE
                A -= Ametric
        #print "3", A
        return A

    def get_A_noOp(self, surface, A, areaDict, areaWinDict):
        # Calculates the area of the surface in cm2 minus all the window openings
        area = Area()
        #A = area.surfaceArea(surface.cps, surface.azimuth, surface.tilt, surface)
        #A = round(surface.height * surface.width, 6)
        #print A

        # The remove the A of each of the openings
        for opening in surface.openings:
            # Only subtract if opening...may be more types to handle later on.....
            if opening.obj_type == "OperableWindow" or opening.obj_type == "FixedWindow" or opening.obj_type == "NonSlidingDoor" or opening.obj_type == "OperableSkylight" or opening.obj_type == "Air":
                #A -= area.surfaceArea(opening.ocps, surface.azimuth, surface.tilt, opening)
                #A -= (opening.height * opening.width)
                Ametric = areaWinDict[opening.obj_id]
                Ametric /= 0.09290304  # The Area() is calculating and storing metric so needs to be put back into imperial for EE
                A -= Ametric
        #print "4", A
        return A


