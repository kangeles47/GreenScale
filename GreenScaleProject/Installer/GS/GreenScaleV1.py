#-------------------------------------------------------------------------------
# Name:        GreenScaleV1.py
# Purpose:     Green Scale Tool Main EE Model Module (starts embodied energy model)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
import datetime
from Weather import Weather
import os
from gbXML import gbXML
from objects.GreenscaleSpace import GreenscaleSpace
from objects.GreenscaleSurface import GreenscaleSurface
from objects.Area import Area
from objects.Confidence import Confidence
import logging
from wsData import wsData
from GSUtility import GSUtility
EE_coder = logging.getLogger('EEcoder_V1')
EE_user = logging.getLogger('EEuser_V1')
Assembly = logging.getLogger('Assembly_V1')


class GreenScaleV1():
    # Input parameters
    input_dir = ""
    gbxml = ""

    # Output parameters
    #buildingEEtotal = 0
    #buildingEWtotal = 0

    # Internal parameters
    spaces = list()
    materials = list()
    shade_devices = list()     # Total number of exterior surfaces to add to EE total
    #def __init__(self, db):
        # set the first temperature by default
        #self.input_dir = db

    def run(self):
        """
        Main run function
        """
        # Initialize the GBXML
        self.gbxml = gbXML(self.gbxml)
        # Get the materials list
        materials = self.gbxml.get_allMaterials() #looks for all material tags in gbxml from Revit AEC database
        remoteData = wsData() #creates a remoteData object that is a wsData type
        remoteData.getmaterials(materials)
        # Retrieve the spaces
        self.spaces = self.gbxml.get_spaces()
        self.shade_devices = self.gbxml.get_shades()            # Shade surfaces defined separate from other surfaces

        area = Area()
        areaDict = area.getDictionary()
        areaWinDict = area.getWinDictionary()

        # For each spaces, calculate Embodied Energy and Embodied Water for a given building
        EE_spaces=self.buildingEE(self.input_dir, self.shade_devices, areaDict, areaWinDict) #accumulators
        print(EE_spaces)
        return None

    def getDBMaterials(self):
        return dbmaterials

    def buildingEE(self, input_dir, shade_surfaces, areaDict, areaWinDict):
        """
        Process the overall Embodied Energy and Embodied Water for a given building
        Collecting the data as it is returned from the space, n turn the surfaces
        """
        # Need to monitor for potential duplicate surfaces-so they are not added twice
        # This is going to have to be optimized for large buildings with many surfaces

        #print "Reaching buildingEE function..."
        U = GSUtility()
        U.devPrint("Reaching buildingEE function...")

        duplicates = list()
        assembly = dict()
        assembly_descript = dict()
        missing_materials = dict()
        MaterialVolumeDict = dict()
        MaterialDict = dict()

        # For each spaces, calculate the buildingEE
        buildingEEtotal = 0
        buildingEWtotal = 0
        #tempEE = 0
        current_space = GreenscaleSpace()
        current_shade_surface = GreenscaleSurface()
        for space in self.spaces:
            EE_user.info("---------------single space calculations for space named: , %s" % (space.obj_id))  # Mark New Space Section
            spaceEnergy = list()
            # Returns list of EE and EW for each space
            spaceEnergy = current_space.calculate_spaceEE(input_dir, space, duplicates, assembly, assembly_descript, areaDict, areaWinDict, missing_materials, MaterialVolumeDict, MaterialDict)
            # Get the total sum of all the spaces
            buildingEEtotal = spaceEnergy[0] + buildingEEtotal
            buildingEWtotal = spaceEnergy[1] + buildingEWtotal
            #tempEE += tempE
            EE_user.info("-----End of data for this Room------")
            EE_user.info(" ")
        #EE_user.info("   ")
        #EE_user.info("Total Building Energy:, %s, Btu/lb, %s, Gal/lb," % (buildingEEtotal, buildingEWtotal))  # Record the Building's EE, EW
        #EE_user.info("   ")
        #print "tempEE: ", tempEE

        #tempEEE = 0
        shade_EE_total = 0
        shade_EW_total = 0
        for device in shade_surfaces:
            #print "type: ", surface.obj_type
            # We do not need to add surfaces of Air to Sum Embodied Energy
            if device.obj_type == "Air":
                continue
            # Check if this surface EE has already been added - occurs with shared walls and floors
            if device.obj_id not in duplicates:
                duplicates.append(device.obj_id)
                # EE_surface in this case returns a list pair of surface EE and surface EW
                EE_surface = list()
                EE_surface = current_shade_surface.calculate_surfaceEE(input_dir, device, assembly, assembly_descript, areaDict, areaWinDict, 0, missing_materials, MaterialVolumeDict, MaterialDict)
                #if device.obj_constr == "cons-2":
                    #print device.obj_id
                    #tempEEE += EE_surface[0]
                shade_EE_total += EE_surface[0]
                shade_EW_total += EE_surface[1]
            else:
                continue
            #print device.obj_id, device.construction[0].layer[0].material[0].thickness
        #print "tempEE", tempEE + tempEEE

        # Also add the shade EE/EW totals to the space totals for below:
        buildingEEtotal = buildingEEtotal + shade_EE_total
        buildingEWtotal = buildingEWtotal + shade_EW_total
        EE_user.info("   ")
        EE_user.info("Total Building Energy:, %s, BTU, %s, GAL," % (buildingEEtotal, buildingEWtotal))  # Record the Building's EE, EW
        EE_user.info("   ")
        EE_user.info("Section Recording Building Element EE from Parapets and Overhangs Etc.")
        EE_user.info("   ")

        Assembly.info("   ")
        #for key in assembly_descript:
            #print "assembly_descript ", assembly_descript[key]
        for key in assembly:
            amountEE = assembly[key]
            if key not in assembly_descript:
                Assembly.info("Assembly Dictionary Item:, %s, %s, %s" % (key, amountEE, key))  # Record the Building's EE, EW by Assembly
                print "assembly_descript ", key, amountEE, key #uncomment in order to see embodied energy per assembly
            else:
                assemblyParts = assembly_descript[key]
                assemblyParts = str(assemblyParts)
                assemblyParts = assemblyParts.replace(',', ' + ')
                Assembly.info("Assembly Dictionary Item:, %s, %s, %s" % (key, amountEE, assemblyParts))  # Record the Building's EE, EW by Assembly
                print "assembly_descript ", key, amountEE, assemblyParts #uncomment in order to see embodied energy per assembly
        Assembly.info("   ")

        # Add this to the overall return parameters
        buildingTotal = list()
        buildingTotal.append(buildingEEtotal)
        buildingTotal.append(buildingEWtotal)

        #print "buildingTotal ", buildingTotal
        thing1 = buildingTotal
        thing1s = str(thing1)
        thing1s = "buildingTotal " + thing1s
        U.devPrint(thing1s)

        #mm = "Number of Missing Materials: ", str(len(missing_materials))
        #U.devPrint(mm)
        mm = str(len(missing_materials))
        print "Number of Missing Materials: ", mm
        for item in missing_materials:
            #print item
            U.devPrint(item)

        ee = buildingTotal[0]
        ew = buildingTotal[1]
        print "Total EE: ", ee

        self.uncertaintyFactors(MaterialVolumeDict, MaterialDict)

        return ee, ew

    def uncertaintyFactors(self, MaterialVolumeDict, MaterialDict):
        """
        Process Building material uncertainties based upon the Material Volume per building and confidence factors
        This will be the starting point for further uncertainty calculations as time permits
        """
        C = Confidence()
        c = C.calculate_confidence_values(MaterialVolumeDict, MaterialDict)
