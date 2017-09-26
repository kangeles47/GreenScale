#-------------------------------------------------------------------------------
# Name:        GreenscaleEE.py
# Purpose:     Green Scale Tool EE Material Module (Handles material level EE calculations)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
from objects.BaseElement import BaseElement
from dircache import listdir
import os
import time
import string
import math
import logging
from wsData import wsData
from GSUtility import GSUtility
EE_coder = logging.getLogger('EEcoder_V1')
EE_user = logging.getLogger('EEuser_V1')


#input_dir = os.path.dirname(__file__), '../objects/GreenScaleDBcsv.csv'


class GreenscaleEE(BaseElement):

    #openingType = dict()
    #MaterialVolumeDict = dict()
    db_file = ""

    def calculate_EE(self, input_dir, surface, this_material_area, h_surface, missing_materials, material_dictionary, MaterialDict):
        #if surface.cad is not None:
        #    print "shading surface types: ", surface.cad
        # Loops through the materials of a surface and collects the sum totals of the EE and EW for that surface

        EE = list()

        EE_total = 0
        EW_total = 0
        #print surface.obj_id
        for material in surface.construction[0].layer[0].material:
            EE_material = self.calculate_material_EE(input_dir, material, this_material_area, surface, h_surface, missing_materials, material_dictionary, surface.obj_id, surface.construction[0].obj_id, MaterialDict)
            #if surface.obj_id == "su-50":
            #    print surface.obj_id, EE_material, material.thickness
            # Total EE should be in Btu for the end result
            #print surface.obj_id
            EE_total += EE_material
            #print "EE_total: ", EE_material
            E_water = self.calculate_embodied_water(EE_material)
            # Total EE should be in Gallons for the end result
            EW_total += E_water
            #print "EW_total: ", EW_total
        EE_total = round(EE_total, 6)
        #print surface.obj_id, "gets: ", EE_total
        EW_total = round(EW_total, 6)
        EE.append(EE_total)
        EE.append(EW_total)
        #print "EE totals from the function doing just the total area or effective area for: ", surface.obj_id, ", ", EE

        return EE

    def calculate_EE_dict(self, input_dir, surface, key, this_material_area, h_surface, missing_materials, material_dictionary, MaterialDict):
        #print surface.obj_id
        #print "EE totals from the parts considering openings for: ", surface.obj_id
        # Loops through the materials of a surface and collects the sum totals of the EE and EW for that surface
        EE = list()
        EE_assembly_total = 0
        EW_assembly_total = 0
        test = 0
        # Remembering that "key" is the objcons_ref OR obj_type_ref so match it and find the corresponding materials
        # See if this opening is a door with layers or a window without layers from Revit
        #print "is it here?"
        count = 0
        #print surface.openings
        #for idc in surface.openings[0].material:
            #print idc.obj_id
            #count += 1
        #print "count, ", count
        #print "stop"
        count = 0

        #for item in surface.openings:
        #    print "with material", item.material[0].obj_id
        #    if key == item.material[0].obj_id:  #obj_id = obj_cons_ref
        #        if item.material[0].check == 0:   # This flag means this is not a window and has layers to calculate
        #            print "found the door ID: "
        #    count += 1
        #print "count2, ", count

        for idc in surface.openings:
        #for idc in surface.openings:
            #print idc.obj_id
            if key == idc.material[0].obj_id:  #obj_id = obj_cons_ref
                if idc.material[0].check == 0:   # This flag means this is not a window and has layers to calculate
                    #print "found door id: ", key
                    for material in idc.material[0].layer[0].material:   #instead here you want to match the surface.constructions to the its_key
                        EE_material = self.calculate_material_EE(input_dir, material, this_material_area, surface, h_surface, missing_materials, material_dictionary, surface.obj_id, key, MaterialDict)
                        #print "ee of material: ", EE_material
                        # Total EE should be in Btu for the end result
                        EE_assembly_total += EE_material
                        E_water = self.calculate_embodied_water(EE_material)
                        # Total EE should be in Gallons for the end result
                        EW_assembly_total += E_water
                    EE_assembly_total = round(EE_assembly_total, 6)
                    EW_assembly_total = round(EW_assembly_total, 6)
                    EE.append(EE_assembly_total)
                    EE.append(EW_assembly_total)
                    test = 1
                    #print "found door id: ", idc.obj_id, this_material_area
                    break
            else:
                continue
        if test == 0:  # if you still have not found a matching ID, check these:
            for idc in surface.openings:
                if key == idc.material[0].obj_id:  #obj_id = obj_type_ref
                    # This case is using self.lookup_EE_material() to use given values in the DB
                    parts_list, confidence = self.lookup_EE_material(input_dir, idc.material[0].obj_name, missing_materials)  #-------------------------------------------------------------------------!
                    EEval = parts_list[0]
                    #pieces = [EE, density, and thickness in feet]
                    #print idc.material[0].obj_name, parts_list[0], parts_list[1], parts_list[2]
                    MV = (parts_list[2]) * this_material_area  # Need material volume in cubic feet
                    MD = float(parts_list[1])  # if starting with gbXML units: (idc.density * 2.20462262) / 35.3146667
                    EE_assembly_total = EEval * MV * MD
                    #print "window stuff: ", EEval, MV, MD, EE_assembly_total, this_material_area, parts_list[2]

                    self.add_material_to_material_dictionary(idc.material[0].obj_name, parts_list[2], material_dictionary, confidence, surface.obj_id, key, EE_assembly_total, MaterialDict)

                    total_surface_area = "   "
                    namedstring = idc.material[0].obj_name
                    a = namedstring.replace(',', ' ')
                    EE_user.info("Material (Volume and EE):, %s, %s, Cubic Feet, %s, %s, Btu/lb" % (a, MV, total_surface_area, EE_assembly_total))

                    #print "found window id: ", idc.obj_id, this_material_area
                    EW_assembly_total = self.calculate_embodied_water(EE_assembly_total)
                    test = 1
                    break
                else:
                    continue
            EE_assembly_total = round(EE_assembly_total, 6)
            #print EE_assembly_total
            EW_assembly_total = round(EW_assembly_total, 6)
            #print EW_assembly_total
            EE.append(EE_assembly_total)
            EE.append(EW_assembly_total)
        #print "this: ", surface.openings[0].material, key, surface.obj_id
        if test == 0:
            #print "check: ", surface.openings[0].material, key, surface.obj_id
            #raise Exception("No Material Assembly ID found in windows or constructions")
            U = GSUtility()
            U.devPrint("No Material Assembly ID found in windows or constructions in GreenscaleEE.py")
        #print "This is the EE total for openings in: ", surface.obj_id, ", ", EE

        return EE

    def calculate_material_EE(self, input_dir, material, this_material_area, cadShade, h_surface, missing_materials, material_dictionary, surface_obj_id, cons_id, MaterialDict):
        # Call this from for each material in the surface.constructions.layers.materials
        # Calculates the EE for each material in the surface and sums the answers to get surface total
        #print cons_id

        # Store the material to be looked up and used int the comparison
        name = material.obj_id

        pieces, confidence = self.lookup_EE_material(input_dir, material.name, missing_materials)  #---------------------------------------------------------------------------------------------------!

        #for item in pieces:

        # In this case, we only want the first item passed back
        # This case is using self.lookup_EE_material() to use only the given EE in the DB, MV and MD from gbXML file
        #print "here ", pieces
        EE = pieces[0]

        MV = self.material_volume(material, this_material_area, cadShade, h_surface)
        #print "EE: ", MV
        MD = self.material_density(material)
        #print "MD, MV: ", MD, MV

        EE_material = EE * MV * MD
        #print "EE_material: ", EE_material
        #print material.name, MV, MD, EE, EE_material, this_material_area, "a"

        total_surface_area = "   "
        namedstring = material.name
        a = namedstring.replace(',', ' ')
        EE_user.info("Material (Volume and EE):, %s, %s, Cubic Feet, %s, %s, Btu/lb" % (a, MV, total_surface_area, EE_material))

        # Add the amount of this material to the
        # NOTE: May need an if/else to stop adding materials to the dict when the hour changes for the first time to only go through the materials once
        # However, this whole file may only need to run through and can look up in a dict for successive hours...
        self.add_material_to_material_dictionary(material.name, MV, material_dictionary, confidence, surface_obj_id, cons_id, EE_material, MaterialDict)

        return EE_material

    def lookup_EE_material(self, input_dir, material_to_lookup, missing_materials):
        #if material_to_lookup == '1/8 in Pilkington single glazing':
        #    print "material_to_lookup ", material_to_lookup
        parts = list()
        EE = -1
        confidence = 0
##        GSV1 = GreenScaleV1.GreenScaleV1()
##        wsData = GSV1.getDBMaterials()
        WSD = wsData()
##        DBData = WSD.getDBMaterials()
##        if len(DBData) > 0:
##            for item in DBData:
        item = WSD.getMaterial(material_to_lookup)
##                if material_to_lookup == item['namegbxml']:

        #print material_to_lookup, item
        #confidence = float(item['confidence'])
        #if not item['confidence'] in item:
        #    confidence = 0.00
        #    print "triggered"
        #else:
            #confidence = float(item['confidence'])
        #print "confidence", confidence

        if not item == -1:
            confidence = float(item['confidence'])
            EE = float(item['embodiedenergy'])
            MD = float(item['matdensityarch'])
            eeUnit = item['eeUnit']
            mdUnit = item['denUnit']
            if eeUnit['unitdesc'] == 'MJ/kg':
                EE *= 429.9
            #if mdUnit['unitdesc'] == 'kg/m^3':
            #    MD *= 0.06243
            parts.append(EE)

            if material_to_lookup == 'AirSpace':
                # Until real density and thickness are considered for air, set = 0 so units not included
                #print 'Air test'
                MD = float(item['matdensityarch'])
                parts.append(MD)
                thickness = 0.0
                parts.append(thickness)
            elif item['iswindow']:
                MD = float(item['matdensityarch'])
                mdUnit = item['denUnit']
                if mdUnit['unitdesc'] == 'kg/m^3':
                    MD *= 0.06243
                #print "getting window here with density---------------------: ", MD, material_to_lookup
                parts.append(MD)
                parts.append(float(item['thickness'])/12)
            else:
                parts.append(1)
                parts.append(1)

##          else:
##              raise Exception("No data returned from database")

        # Missing material logging before using dictionary:
        #if EE == -1:
        #    parts.append(0)
        #    parts.append(0)
        #    parts.append(0)
        #    EE_coder.info("DB needs material (fake data used until material exists)--if Air, is ok since already set to = 0: , %s," % (material_to_lookup))  # Material name that is not found in DB

        U = GSUtility()
        # Start tallying the missing materials without duplicates, if EE == -1, it is missing
        if EE == -1:
            parts.append(0)
            parts.append(0)
            parts.append(0)
            #for key in missing_materials:
            #    missing = missing_materials[key]
            if material_to_lookup not in missing_materials:
                missing_materials[material_to_lookup] = parts
                # Material name is missing and is not already in the dictionary
                EE_coder.info("DB needs material (fake data used until material exists)--if Air, is set to = 0: , %s," % (material_to_lookup))
                #missingm = "Missing Material: " + material_to_lookup
                #U.devPrint(missingm)

        return parts, confidence

    def lookup_EE_material_iterative(self, input_dir, material_to_lookup, missing_materials):
        #if material_to_lookup == "1/8 in Pilkington single glazing":
        #    print material_to_lookup
        material_to_lookup = str(material_to_lookup)
        parts = list()
        EE = -1
##        GSV1 = GreenScaleV1.GreenScaleV1()
##        wsData = GSV1.getDBMaterials()
        WSD = wsData()
        DBData = WSD.getDBMaterials()
        if len(DBData) > 0:
            for item in DBData:
                if material_to_lookup == item['namegbxml']:
                    EE = float(item['embodiedenergy'])
                    MD = float(item['matdensityarch'])
                    eeUnit = item['eeUnit']
                    mdUnit = item['denUnit']
                    if eeUnit['unitdesc'] == 'MJ/kg':
                        EE *= 429.9
                    #if mdUnit['unitdesc'] == 'kg/m^3':
                    #    MD *= 0.06243
                    parts.append(EE)

                    if material_to_lookup == 'AirSpace':
                        # Until real density and thickness are considered for air, set = 0 so units not included
                        #print 'Air test'
                        MD = float(item['matdensityarch'])
                        parts.append(MD)
                        thickness = 0.0
                        parts.append(thickness)
                    elif item['iswindow']:
                        MD = float(item['matdensityarch'])
                        mdUnit = item['denUnit']
                        if mdUnit['unitdesc'] == 'kg/m^3':
                            MD *= 0.06243
                        #print "getting window here with density---------------------: ", MD, material_to_lookup
                        parts.append(MD)
                        parts.append(float(item['thickness'])/12)
                    else:
                        parts.append(1)
                        parts.append(1)

        else:
            #raise Exception("No data returned from database")  # This exception seems to happen with material not in DB-changed to below to just add note to the output file
            EE_coder.info("DB needs material: , %s," % (material_to_lookup))  # Material name that is not found in DB
            #print material_to_lookup

        if EE == -1:
            parts.append(0)
            parts.append(0)
            parts.append(0)
            EE_coder.info("DB material not found: will use defaults until resolved--(ignore if Air) , %s" % (material_to_lookup))  # Material name that is not found in DB
            #print material_to_lookup
            #If this is the case, changing the "raise" statement to be: (-1,-1,-1) so will be negative values

            #print "missing material note: ", material_to_lookup, parts

            #raise Exception("No EE listing for this material: ", material_to_lookup)
        #print parts
        # Could calculate the EE and return, but for now leaving EE, density, and thickness as separate variables
        #print material_to_lookup, parts

        return parts

    def lookup_EE_material_old(self, input_dir, material_to_lookup):
        # Retrieves the EE for the given material: looks up the material EE from the dictionary or can read from file
        # Needs to return Btu/lb to the GSRP model
        #material_to_lookup = str(material_to_lookup)
        # Look for an input file ... only if this will only check file names and not whole DB...
        # Using the weather open_file process for the csv db at this time, opened to find each material
        #print "material: ", material_to_lookup
        #db_file = "GreenScaleDBcsv.csv"
        U = GSUtility()
        db_file = "DatabaseEE.csv"
        EE_CSV_file = None
        #print input_dir
        parts = list()

        for f in listdir(input_dir):
            if db_file in f:
                # DB is found in resources
                EE_CSV_file = f
                #print "DB found in the directory"
                break
        # If we dont have it, raise an error
        if not EE_CSV_file:
            #raise Exception("No EE DB file found in directory")
            U.devPrint("No EE DB file found in directory")

        try:
            f = open(os.path.join(input_dir,db_file), "r")
        except IOError:
            #print "Unable to open the DB file"
            U.devPrint("Unable to open the DB file")
            # Open it and create the weather

        f = open(os.path.join(input_dir, db_file), "r") # is not seeing f without this line ???
        line = f.readline()
        line_count = 0
        line_split = line.split(',')
        # Need a default case for EE if not found in DB
        EE = -1
        #print "Looking for a match..."

        while 1:
            line = f.readline()
            if not line:
                break
            line_count += 1
            # Only start reading at the 3rd line
            # Before that just Metadata
            if line_count < 2:
                continue
            # Split the line (Delimiter is ,)
            line_split = line.split(',')

            if material_to_lookup == 'Structure, Wood Joist/Rafter Layer, Batt Insulation: 3 1/2"':
                # This is a quick fix to the second comma problem, seems not efficient to scan all string for total ,-s
                # This is also the only instance of this right now...
                newMat = 'Structure, Wood Joist/Rafter Layer Batt Insulation: 3 1/2"'
                material_to_lookup = str(newMat)
                #print "this ",material_to_lookup

            # See if test ends with a " and if not then concat with line_split[2]
            # Find the last character
            #last_char = test[-1:]
            #if last_char == '"':
            #if test.startswith('"') and test.endswith('"'):
            #    test = str(line_split[1])
            flag = 0

            test = str(line_split[1])

            if test.startswith('"') and not test.endswith('"'):
                pieces = [test, str(line_split[2])]
                test = ",".join(pieces)  # may be a space char issue if not working
                flag = 1

            # get rid of extra quote character(s), if any, to compare to data format in material.name
            # what test is now is the cvs format, so need to adjust to match the gbXml format
            if material_to_lookup.endswith('"'):
                test = test[:-2]
                test = test[1:]
            elif ',' in material_to_lookup and not material_to_lookup.endswith('"'):
                test = test[:-1]
                test = test[1:]
            else:
                test = test
            # Marker here is 0 or 1, but is marked differently depending on certain materials with commas in names
            # Checking if the material is a window or not with the "marker" variable
            if material_to_lookup == test and flag == 0:
                    EE = float(line_split[4])
                    #print "This is the current EE: ", EE
                    if str(line_split[5]) == "BTU/lb":  # Check Units
                        parts.append(EE)  # If BTUs, then use it
                    elif str(line_split[5]) == "MJ/kg":
                        EE *= 429.9  # If MJ/kg, then change to BTUs
                        parts.append(EE)
                    else:
                        #print "Units not yet accounted for...", float(line_split[5])
                        thing1 = float(line_split[5])
                        thing1s = str(thing1)
                        thing1s = "Units not yet accounted for..." + thing1s
                        U.devPrint(thing1s)
                        #U.devPrint("Units not yet accounted for...", float(line_split[5]))
                    #parts.append(EE)
                    marker = int(line_split[3])
                    #print marker
                    if marker == 1:
                        MD = float(line_split[6])
                        if str(line_split[7]) == "lb/ft^3":  # Check Units
                            parts.append(MD)  # If BTUs, then use it
                        elif str(line_split[7]) == "kg/m^3":
                            MD *= 0.06243
                            parts.append(MD)
                        else:
                            #print "Units not yet accounted for...", float(line_split[5])                        # Assuming first part of string will contain the fraction in inches
                            thing1 = float(line_split[5])
                            thing1s = str(thing1)
                            thing1s = "Units not yet accounted for..." + thing1s
                            U.devPrint(thing1s)
                            #U.devPrint("Units not yet accounted for...", float(line_split[5]))
                        glass = material_to_lookup.split(' ')
                        glass1 = glass[0]
                        glass2 = glass1.split('/')
                        num = float(glass2[0])
                        den = float(glass2[1])
                        glassThickness = (num/den) / 12  # Thickness in feet if reading inches from database
                        # Will also change when we are considering thicknesses represented greater than 1" ("1 1/8 in")
                        glassThickness = round(glassThickness, 8)
                        parts.append(glassThickness)
                    if material_to_lookup == "AirSpace":
                        # Until real density and thickness are considered for air, set = 0 so units not included
                        MD = float(line_split[6])
                        parts.append(MD)
                        thickness = 0
                        parts.append(thickness)
                    #print "EE set to: "
                    #print EE
                    break
            elif material_to_lookup == test and flag == 1:
                    EE = float(line_split[5])
                    #print "This is the current EE: ", EE
                    if str(line_split[6]) == "BTU/lb":  # Check Units
                        parts.append(EE)  # If BTUs, then use it
                    elif str(line_split[6]) == "MJ/kg":
                        EE *= 429.9  # If MJ/kg, then change to BTUs
                        parts.append(EE)
                    else:
                        #print "Units not yet accounted for...", float(line_split[5])
                        thing1 = float(line_split[5])
                        thing1s = str(thing1)
                        thing1s = "Units not yet accounted for..." + thing1s
                        U.devPrint(thing1s)
                        #U.devPrint("Units not yet accounted for...", float(line_split[5]))
                    marker = int(line_split[4])
                    #print marker
                    if marker == 1:
                        MD = float(line_split[7])
                        if str(line_split[8]) == "lb/ft^3":  # Check Units
                            parts.append(MD)  # If BTUs, then use it
                        elif str(line_split[8]) == "kg/m^3":
                            MD *= 0.06243
                            parts.append(MD)
                        else:
                            #print "Units not yet accounted for...", float(line_split[5])
                            thing1 = float(line_split[5])
                            thing1s = str(thing1)
                            thing1s = "Units not yet accounted for..." + thing1s
                            U.devPrint(thing1s)
                            #U.devPrint("Units not yet accounted for...", float(line_split[5]))
                        # Assuming first part of string will contain the fraction in inches
                        glass = material_to_lookup.split(' ')
                        glass1 = glass[0]
                        glass2 = glass1.split('/')
                        num = float(glass2[0])
                        den = float(glass2[1])
                        glassThickness = (num/den) / 12  # Thickness in feet if reading inches from database
                        # Will also change when we are considering thicknesses represented greater than 1" ("1 1/8 in")
                        glassThickness = round(glassThickness, 8)
                        parts.append(glassThickness)
                        #print glassThickness
                    #print "EE set to: "
                    #print EE
                    break
            else:
                continue

        if EE == -1:
            parts.append(1)
            parts.append(1)
            parts.append(1)
            EE_coder.info("DB needs material (fake data used until material exists): , %s," % (material_to_lookup))  # Material name that is not found in DB
            #If this is the case, changing the "raise" statement to be: (-1,-1,-1) so will be negative values
            #print "missing material: ", material_to_lookup, parts
            thing1 = material_to_lookup
            thing2 = parts
            thing1s = str(thing1)
            thing2s = str(thing2)
            thing3s = "missing material: " + thing1s + " " + thing2s
            U.devPrint(thing3s)
            #U.devPrint("missing material: ", material_to_lookup, parts)
            #raise Exception("No EE listing for this material: ", material_to_lookup)
        #print parts
        # Could calculate the EE and return, but for now leaving EE, density, and thickness as separate variables
        #print material_to_lookup, parts
        return parts

    def material_volume(self, material, this_material_area, surface, h_surface):
        # Retrieves the MV (material volume) for the given material

        # Get the thickness - this will have to be converted
        thickness = material.thickness  # Given in Meters from the gbXML, needs to be in feet
        thickness_feet = thickness * 3.2808399       # 3.2808399 is the conversion from meters to feet

        #print material.name, " thickness_feet: ", thickness_feet
        #thickness_converted = thickness * 39.3700787
        # 39.3700787 is the conversion from meters to inches then /12 to feet
        #thickness_converted = thickness_inches / 12

        # Returned MV in the GSRP is using units of ft^3, so multiply by the effective area that is in ft^2
        # Area parameters come from the gbXML in width=feet, height=feet, areas=squareFeet, volumes=cubicFeet
        MV = thickness_feet * this_material_area

        # Adjustment for Foundation pieces
        shadeString = str(surface.cad)
        fnd1 = "Foundation"
        fnd2 = "foundation"
        if shadeString.find(fnd1) != -1 or shadeString.find(fnd2) != -1:
            # For surfaces that are foundation pieces, the T-by-2T rule can be applied since Footing Data is not in the gbxml
            #print MV
            if thickness_feet < 0.6666666667:
                # If it is foundation, then need to make sure thickness is at least 8 inches since re-assignment of cons-type may be to concrete floor of 4" thickness which is way off for foundations
                # If it is less than 8" then re-assign the thickness for this surface/material
                material.thickness = 0.6666666667
                thickness_feet = 0.6666666667
            MV = MV + ((2 * thickness_feet) * thickness_feet * surface.width)
            #print "new volume", MV

        # Adjustment for Stud Wall pieces
        name = str(material.name)
        #print "material.name: ", name
        #if name.startswith('Structure, Wood Joist/Rafter Layer') or name.startswith('Softwood, Lumber: 3 1/2"'):
        if name.find('Structure, Wood Joist/Rafter Layer') != -1 or name.find('Softwood, Lumber: 3 1/2"') != -1 or name.find('Lumber') != -1 or name.find('Structure') != -1 or name.find('Joist') != -1 or name.find('Rafter') != -1:
            # This is a temporary fix to a naming problem until DB rules can be applied
            if name.find('Structure, Wood Joist/Rafter Layer, Batt Insulation') != -1:
                #print "using temp rule for assembly"
                MV = MV
            else:
                MV = thickness_feet * this_material_area * 0.15
                #print "material.name: ", name, MV

        # Adjustment for Insulation layers
        ins1 = "insulation"
        ins2 = "Insulation"
        r1 = "Rigid"
        r2 = "rigid"
        b1 = "Blown"
        b2 = "blown"
        s1 = "Spray"
        s2 = "spray"
        c1 = "Cellulose"
        c2 = "cellulose"
        b3 = "Batt"
        b4 = "batt"
        #if name != 'Structure, Wood Joist/Rafter Layer, Batt Insulation: 3 1/2"':
        if name.find('Structure, Wood Joist/Rafter Layer, Batt Insulation') == -1:
            # Means this is a type of insulation and not the special assembly case
            if name.find(ins1) != -1 or name.find(ins2) != -1:
                if name.find(r1) != -1 or name.find(r2) != -1 or name.find(s1) != -1 or name.find(s2) != -1:
                    # It is insulation but of rigid type or behaves as such so do not reduce
                    #print "rigid"
                    MV = MV
                elif name.find(b1) != -1 or name.find(b2) != -1 or name.find(c1) != -1 or name.find(c2) != -1 \
                    or name.find(b3) != -1 or name.find(b4) != -1:
                    # It is insulation that behaves as Batt insulation so reduce
                    #print "batt no compound occurance"
                    MV = thickness_feet * this_material_area * 0.85
                else:
                    # It is insulation but not of rigid type so reduce as the default situation
                    #print "other"
                    MV = thickness_feet * this_material_area * 0.85


        #if name == 'Rigid insulation: 2"':
        #    MV = thickness_feet * this_material_area * 0.85
        #    #print "material.name: ", name, MV

        #print material.name, this_material_area, MV

        # Handle extra cases of where columns are standing in the spaces (special case to get right dimensions)
        if material.obj_id == "mat-COL":
            # This is a column "surface" so need to use the cross-section and room height to get volume
            if surface.columnType == "round":
                dia = material.thickness / 12  # This is the cross-section diameter in inches to feet for a column element
                area = math.pi * ((dia/2) ** 2)
                h_surface = h_surface * 3.2808399       # 3.2808399 is the conversion from meters to feet
                MV = h_surface * area
                #print "rd", h_surface, area
            if surface.columnType == "square":
                cross = material.thickness / 12  # This is the cross-section diameter in inches to feet for a column element
                area = cross * cross
                h_surface = h_surface * 3.2808399       # 3.2808399 is the conversion from meters to feet
                # Divided by 4 since square surfaces are put into the gbxml x4 (once each side so if not /4 is 4x too large of EE)
                MV = (h_surface * area) / 4
                #print "sq", h_surface, area

        return MV

    def material_density(self, material):
        # Retrieves the MD (material density) for the given material in units of Kg per Cubic M
        density = material.density  # Replaced this value to read from the DB instead
        WSD = wsData()
        DBData = WSD.getDBMaterials()
        if len(DBData) > 0:
            for item in DBData:
                if material.name == item['namegbxml']:
                    density = float(item['matdensityarch'])
                    densityunit = item['denUnit']
                    if densityunit['unitdesc'] == 'kg/m^3':
                        #print material, "this was changed......"
                        density *= 0.06243

                    #mdUnit = item['denUnit']
                    #if mdUnit['unitdesc'] == 'kg/m^3':
                    #    MD *= 0.06243

        #Returned MV in the GSRP is using units of lb/ft^3 so convert MD to this
        #density_converted = density * 0.0624279606
        #density *= 2.20462262                     # Kgs to Lbs
        #density_converted = density / 35.3146667  # cubicMeters to CubicFeet
        #density *= 0.06243  # If kg/m^3, then change to lb/ft^3
        #density_converted = density

        #MD = density_converted
        #print material.name, " density: ", MD

        return density

    def calculate_embodied_water(self, EE_material):
        # Calculates the Embodied Water for each material for from the EE for that same material
        # Needs to return gallons/lb to the GSRP model

        #EW = EE_material * (2.79 * 10**(-4))
        EW = EE_material * 0.000279

        return EW

    def add_material_to_material_dictionary(self, material, MV, MaterialVolumeDict, confidence, surface_obj_id, cons_id, EEmaterial, MaterialDict):
        materialIn = material
        # Set up dictionary by building volume totals and total EEs for each material for whole building
        if material not in MaterialVolumeDict:
            # If this entry is not there, add it to the dictionary with this MV value
            zero = 0
            MaterialVolumeDict[material] = (MV, confidence, EEmaterial, zero)
            #print "if: ", MV
        else:
            # If it does exist, add the current MV to the existing total for the new total
            new_material_MVtotal = MaterialVolumeDict[material][0] + MV
            new_material_EEtotal = MaterialVolumeDict[material][2] + EEmaterial
            zero = 0
            MaterialVolumeDict[material] = (new_material_MVtotal, confidence, new_material_EEtotal, zero)
            #print "else: ", new_material_total

        # Check for the existing cons_id, then the existing material name within that, & tallies for each material type within a construction
        # So, creating a dictionary of lists
        m = list()
        if cons_id not in MaterialDict:
            # If this entry is not there, add it with all material data for this material
            #print cons_id
            mSet = (material, MV, confidence, EEmaterial)
            m.append(mSet)
            MaterialDict[cons_id] = m
            #print "if part", MaterialDict[cons_id]
        else:
            # Exists so check for existing material already
            check = 0
            counter = 0
            #print "reaching the else clause"
            for a_m in MaterialDict[cons_id]:
                if a_m[0] == materialIn:
                    # Found existing material list so add on the new values by updating
                    v_new = a_m[1] + MV
                    e_new = a_m[3] + EEmaterial
                    m_new = (material, v_new, confidence, e_new)
                    MaterialDict[cons_id][counter] = m_new
                    check = 1
                    #print "updated", MaterialDict[cons_id][0], "at counter ", counter
                    break
                counter += 1
            if check == 0:
                # Construction ID exists but this material doesn't yet exist so append new material data
                mSet2 = (material, MV, confidence, EEmaterial)
                MaterialDict[cons_id].append(mSet2)
                #print "new material", MaterialDict[cons_id]

        return



