#-------------------------------------------------------------------------------
# Name:        gbXML.py
# Purpose:     Green Scale Tool gbxml Module (sets up tree struct from gbxml file)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
from lxml import etree
from objects.Opening import Opening
from objects.Space import Space
from objects.Surface import Surface
from objects.Construction import Construction
from objects.Layer import Layer
from objects.Material import Material
from objects.Area import Area
from wsData import wsData
import time
import logging
import re
from GSUtility import GSUtility
coder = logging.getLogger('Coder_V1')


class gbXML():

    tree = None
    namespaces = {'gb': "http://www.gbxml.org/schema"}
    spaces_dict = dict()
    zones_dict = dict()
    surfaces_dict = dict()
    shgc_dictionary = dict()
    temp_record = dict()
    shadow_record = dict()
    shade_surface_total = list()

    # To solve the case of not constr or window ID in file:
    windowsID_dict = dict()
    constrID_dict = dict()
    DefaultDoorConsId = "none"
    DefaultWindowConsId = "none"
    surface_rename = 0

    # Data Error Flags to tell if all construction, layer, or material tag sets exist in the gbxml
    # Sub-tags may still be missing and will cause model to fail, but decided to leave until found to be an issue (pending Revit output behavior)
    DE1 = 0
    DE2 = 0
    DE3 = 0


    def __init__(self, input_file):
        """
        Init the GBXML class with the file.
        """

        # Open/parse the file
        self.tree = etree.parse(input_file)
        self.shgc_dictionary = dict()
        # Has SolarHeatGainCoeff with unit and solarIncidentAngle (0 40 50 60 70 80 oneWithoutTheTag)
        # Dictionary of the possible SHGCs with matching solarIncidentAngle, just hard-coded for now...
        #hgcs = opening.xpath("./gb:SolarHeatGainCoeff", namespaces = self.namespaces)
        #hgcs_dictionary = dict()
        # OR ... = [int(hgc.get("solarIncidentAngle")), float(hgc.text)] ?
        # 0 = 0, 40*pi/180 = 0.6981, 50 = 0.8727, 60 = 1.0472, 70 = 1.2217, 80 = 1.3963
        self.shgc_dictionary[0] = [0, 0.86]
        self.shgc_dictionary[40] = [40, 0.84]
        self.shgc_dictionary[50] = [50, 0.82]
        self.shgc_dictionary[60] = [60, 0.78]
        self.shgc_dictionary[70] = [70, 0.67]
        self.shgc_dictionary[80] = [80, 0.42]

        constructions = self.tree.xpath("/gb:gbXML/gb:Construction", namespaces=self.namespaces)
        window_types = self.tree.xpath("/gb:gbXML/gb:WindowType", namespaces=self.namespaces)
        temp_flagd = 0
        temp_flagw = 0
        d1 = "Door"
        d2 = "DOOR"
        d3 = "door"
        w1 = "Window"
        w2 = "WINDOW"
        w3 = "window"
        for constr in constructions:
            name = constr.get("id")
            if temp_flagd == 0:
                if name.find(d1) != -1 or name.find(d2) != -1 or name.find(d3) != -1:  # By default will use the first door found in list if Revit has not specified one
                    self.DefaultDoorConsId = name
                    temp_flagd = 1
                    #print "testing the defaults1: ", self.DefaultDoorConsId
                elif name.find("cons") == -1:
                    # take first name found not starting in "cons" but this is also an assumption at this point to find strings like "MDOOR"
                    self.DefaultDoorConsId = name
                    temp_flagd = 1
                    #print "testing the defaults2: ", self.DefaultDoorConsId
                #else:
                    #print "Cannot find a Default Door Cons Id with string matching in line 70 of gbxml.py"
            if not name in self.constrID_dict:
                # If you do not have this already, then add it
                self.constrID_dict[name] = name
        for wind in window_types:
            name = wind.get("id")
            if temp_flagw == 0:
                if name.find(w1) != -1 or name.find(w2) != -1 or name.find(w3) != -1:  # By default will use the first window found in list if Revit has not specified one
                    self.DefaultWindowConsId = name
                    temp_flagw = 1
                    #print "testing the defaults3: ", self.DefaultWindowConsId
                else:
                    # Otherwise use first window in set since it is a know window set (i.e. GSP4R is the only one and does not contain "window")
                    self.DefaultWindowConsId = name
                    temp_flagw = 1
                    #print "testing the defaults4: ", self.DefaultWindowConsId
            if not name in self.windowsID_dict:
                # If you do not have this already, then add it
                self.windowsID_dict[name] = name
        # If for some reason the DefaultDoorConsId and DefaultWindowConsId are still "none", then no opening types were
        # available to use in the gbxml, even though there may be openings in surfaces that need them, so given default
        # of the same surface type around the opening below in the get_openings function with sequence like:
        #if self.DefaultDoorConsId == "none":
        #    # Make sure it has a type
        #    # Then set the default ID
        #    pass
        #if self.DefaultWindowConsId == "none":
        #    # Make sure it has a type
        #    # Then set the default ID
        #    pass

        # Pull a set of ZONES to know how many to give the user...
        spaces = self.tree.xpath("/gb:gbXML/gb:Campus/gb:Building/gb:Space", namespaces=self.namespaces)
        zones = self.tree.xpath("/gb:gbXML/gb:Zone", namespaces=self.namespaces)
        foundFlag = 0
        #if len(zones) == 0:
        for zoneID in spaces:
            #new_space.obj_id = space.get("id")
            #new_space.floor_level = space.get("buildingStoreyIdRef")
            zone_id = zoneID.get("zoneIdRef")
            if not zone_id:
                zone_id = "defaultZone"
                self.zones_dict[zone_id] = [295.0]
                #print zone_id
            else:
                # If there is a zone id to be found in the xml space
                if zone_id not in self.zones_dict:
                    for zone in zones:
                        # Does the zone ID match? If yes, then add it here with the zone_id
                        zoneName = zone.get("id")
                        # Pull temp and unit from gbxml
                        current_zone_temp = float(zone.xpath("./gb:DesignHeatT", namespaces=self.namespaces)[0].text)
                        zunits = zone.xpath("./gb:DesignHeatT", namespaces=self.namespaces)
                        for zvalue in zunits:
                            zunit = zvalue.get("unit")
                        if zoneName == zone_id:
                            # Convert to K ... K = C + 273 and C = (F - 32)*(5/9)
                            if zunit == "F":
                                C = (current_zone_temp - 32) * 0.5555555555
                                convertedFtoK = (C + 273)
                                self.zones_dict[zoneName] = [convertedFtoK]
                                foundFlag = 1
                            if zunit == "C":
                                convertedFtoK = (current_zone_temp + 273)
                                self.zones_dict[zoneName] = [convertedFtoK]
                                foundFlag = 1
                            if zunit == "K":
                                self.zones_dict[zoneName] = [current_zone_temp]
                                foundFlag = 1
                    if foundFlag == 0:
                        # Zone section must be left out of gbxml so give same default here too for this zone-id or if no match found in "zones"
                        self.zones_dict[zone_id] = [295.0]

    def get_shades(self):
        """
        Get the shading devices specified in the XML
        """
        shadowsparts = self.tree.xpath("/gb:gbXML/gb:Campus/gb:Surface", namespaces=self.namespaces)

        construction_names = self.tree.xpath("/gb:gbXML/gb:Construction", namespaces=self.namespaces)
        # Need dictionary to map found construction id back to the construction type from surface level information
        #matchingTypes = dict()
        #for c in construction_names:
        #    cid = c.get("id")
        #    if cid not in matchingTypes:
        #        matchingTypes[cid] = "none"
        #for s in shadowsparts:
        #    ref = s.get("constructionIdRef")
        #    tp = s.get("surfaceType")
        #    if tp != "Shade": # Want settings for surfaces other than the shading devices
        #        if ref in matchingTypes:
        #            matchingTypes[ref] = tp
        #for item in matchingTypes:
        #    print "matchingTypes", matchingTypes[item], item

        # For each create the object
        shadows_list = list()
        for device in shadowsparts:
            # Create the new shadow and set the different properties
            new_shadeTest = Surface()
            new_shadeTest.sobj_type = device.get("surfaceType")
            check = new_shadeTest.sobj_type
            #print "this: ", check
            if check == "Shade":
                #print "found shade device"
                new_shade = Surface()
                new_shade.obj_id = device.get("id")
                #print new_shade.obj_id
                new_shade.obj_type = check
                new_shade.width = float(device.xpath("./gb:RectangularGeometry/gb:Width", namespaces = self.namespaces)[0].text)
                new_shade.height = float(device.xpath("./gb:RectangularGeometry/gb:Height", namespaces = self.namespaces)[0].text)
                new_shade.tilt = float(device.xpath("./gb:RectangularGeometry/gb:Tilt", namespaces = self.namespaces)[0].text)
                new_shade.azimuth = float(device.xpath("./gb:RectangularGeometry/gb:Azimuth", namespaces = self.namespaces)[0].text)

                # Add the CadObjectIds to be able to get the EE for these additional pieces---minus the last 9 characters to omit instance identifier
                # This will add all these IDs here regardless of what is hardcoded after...will need updating as a proper solution becomes available
                cad = str(device.xpath("./gb:CADObjectId", namespaces=self.namespaces)[0].text)
                new_shade.cad = cad[:-9]
                #print new_shade.obj_id, new_shade.cad

                category, typec = self.inString(new_shade.cad)  # category = send current shade string to check for device category type
                category = str(category)
                typec = str(typec)
                #print category, typec
                #cadString = str(new_shade.cad)
                for c in construction_names:  # Use category type to find match in existing construction types
                    # is category in the name string?
                    name = str(c.xpath("./gb:Name", namespaces=self.namespaces)[0].text)
                    if name.find(typec) != -1:
                        # Found construction type with known category identifier so set the construction type and construction ID
                        new_shade.obj_constr = c.get("id")
                        new_shade.obj_type = category
                        break  #??
                        #print new_shade.obj_id, new_shade.obj_constr, new_shade.obj_type, "................", new_shade.cad
                    if typec == "Roof" and name.find(typec) == -1:
                        #  This is a special case (labeled roof and may only be ceiling to be found)...may be others in the future
                        typec2 = "Ceiling"  # Then try Ceiling type
                        if name.find(typec2) != -1:
                            new_shade.obj_constr = c.get("id")
                            new_shade.obj_type = category
                            break  #??
                    #if typec == "Exterior" and name.find(typec) == -1:
                    #    #  This is a special case (labeled exterior and may only be facade to be found)...may be others in the future
                    #    typec = "Facade"
                    #    if name.find(typec) != -1:
                    #        new_shade.obj_constr = c.get("id")
                    #        new_shade.obj_type = category
                if new_shade.obj_type == "Shade":
                    # Log that no match was found to reset the values and default of cons-1 was used
                    coder.info("Default Construction-1 used for  %s" % new_shade.cad)
                    U = GSUtility()
                    thing1 = new_shade.cad
                    thing1s = str(thing1)
                    thing1s = "This CadObjectId is not yet handled: " + thing1s
                    U.devPrint(thing1s)
                    #U.devPrint("This CadObjectId is not yet handled: ", new_shade.cad)
                    #print "This CadObjectId is not yet handled: ", new_shade.cad
                    # Give some default values for now
                    new_shade.obj_type = "ExteriorWall"
                    new_shade.obj_constr = "cons-1"
                new_shade.construction = self.get_constr(new_shade, device, new_shade.obj_constr)

                """
                # Now attach appropriate constructions to get proper EE summation for shading devices
                if new_shade.cad == 'Basic Wall: 5-Wythe Exterior Wall':
                    new_shade.obj_type = "ExteriorWall"
                    new_shade.obj_constr = "cons-2"
                elif new_shade.cad == 'Basic Wall: 3-Wythe Parapet Wall':
                    # cons-2 altered and added to gbxXML for this type specified in the excel, now called cons-7
                    new_shade.obj_type = "ExteriorWall"
                    new_shade.obj_constr = "cons-7"
                elif new_shade.cad == 'Basic Wall: 2x4 Partition Wall':
                    new_shade.obj_type = "InteriorWall"
                    new_shade.obj_constr = "cons-3"
                elif new_shade.cad == 'Basic Wall: 2x6 Partition Wall':
                    new_shade.obj_type = "InteriorWall"
                    new_shade.obj_constr = "cons-4"
                elif new_shade.cad == 'Basic Wall: Foundation - 12" Concrete':
                    new_shade.obj_type = "UndergroundWall"  # Although technically this is not always true to be underground...
                    new_shade.obj_constr = "cons-8"
                elif new_shade.cad == 'Basic Wall: Exterior Front':
                    new_shade.obj_type = "ExteriorWall"
                    new_shade.obj_constr = "cons-2"
                elif new_shade.cad == 'Basic Roof: Wood Rafter 8" - Asphalt Shingle - Insulated':
                    new_shade.obj_type = "Roof"
                    new_shade.obj_constr = "cons-1"
                elif new_shade.cad == 'Basic Roof: Typical Roof':  # Added to include data from Four Room Model
                    new_shade.obj_type = "Roof"
                    new_shade.obj_constr = "cons-1"
                elif new_shade.cad == 'Basic Roof: Generic - 12"':  # Added to include data from Two Room Model
                    new_shade.obj_type = "Roof"
                    new_shade.obj_constr = "cons-1"
                elif new_shade.cad == 'Basic Roof: Avon Roof':  # Added to include data from Avon Theater
                    new_shade.obj_type = "Roof"
                    new_shade.obj_constr = "cons-4"
                elif new_shade.cad == 'Basic Wall: Avon Exterior':  # Added to include data from Avon Theater
                    new_shade.obj_type = "ExteriorWall"
                    new_shade.obj_constr = "cons-2"
                elif new_shade.cad == 'Basic Wall: Avon Facade':  # Added to include data from Avon Theater
                    new_shade.obj_type = "ExteriorWall"
                    new_shade.obj_constr = "cons-1"
                else:
                    print "This CadObjectId is not yet handled: ", new_shade.cad
                    # Give some default values for now
                    new_shade.obj_type = "ExteriorWall"
                    new_shade.obj_constr = "cons-1" # Because this is the only number you can guarentee is there
                #print new_shade.obj_type, new_shade.obj_constr, new_shade.cad
                new_shade.construction = self.get_constr(new_shade, device, new_shade.obj_constr)
                """

                # Retrieve the geometry from here...
                new_shade = self.getRectangularGeometry(new_shade, device)
                rects = device.xpath("./gb:RectangularGeometry/gb:CartesianPoint/gb:Coordinate", namespaces=self.namespaces)
                rec = list()
                for arect in rects:
                    rec.append(float(arect.text) * 0.3048)
                new_shade.rec = rec
                #print "this should be a 3-item list: ", new_shade.rec

                coordinate_sets = device.xpath("./gb:PlanarGeometry/gb:PolyLoop/gb:CartesianPoint", namespaces=self.namespaces)
                cps = list()
                for coordinate_list in coordinate_sets:
                    cp = list()
                    cartesian_points = coordinate_list.xpath("./gb:Coordinate", namespaces=self.namespaces)
                    #print "this should be 3 locations: ", cartesian_points
                    for point in cartesian_points:
                        cp.append(float(point.text) * 0.3048)
                    cartesian_point = tuple(cp)
                    cps.append(cartesian_point)
                new_shade.cps = cps  # now returning a list of tuples for non-square walls to get max/min heights
                #print "cps list of tuples: ", new_shade.cps

                self.surfaces_dict[new_shade.obj_id] = new_shade

                area = Area()
                A = area.surfaceArea(new_shade.cps, new_shade.azimuth, new_shade.tilt, device)
                #print "here"
                area.addArea(new_shade.obj_id, A)

                #self.surfaces_dict[new_shade.obj_id] = new_shade
                #print self.surfaces_dict[new_shade.obj_id]

                # Add to the return list
                shadows_list.append(new_shade)

        return shadows_list

    def inString(self, cadID):
        #  These are the known different types of CadObjectIds
        #  But they have to be set as one of the code-known surface types handled in space.py:
        #  ("ExteriorWall", "Roof", "InteriorWall", "UndergroundWall", "InteriorFloor", "RaisedFloor", "UndergroundSlab", "SlabOnGrade")
        ext = "Exterior"
        para = "Parapet"
        part = "Partition"
        fnd = "Foundation"
        roof = "Roof"
        fac = "Facade"
        ceil = "Ceiling"
        foot = "Footing"
        flr = "Floor"

        if cadID.find(ext) != -1 or cadID.find(para) != -1:
            category = "ExteriorWall"
            typec = ext
        elif cadID.find(fac) != -1:
            category = "ExteriorWall"
            typec = fac
        elif cadID.find(part) != -1:
            category = "InteriorWall"
            typec = part
        elif cadID.find(fnd) != -1 or cadID.find(foot) != -1:
            category = "UndergroundWall"
            typec = fnd
        elif cadID.find(flr) != -1:
            category = "InteriorFloor"
            typec = flr
        elif cadID.find(roof) != -1:
            category = "Roof"
            typec = roof
        elif cadID.find(ceil) != -1:
            category = "Ceiling"
            typec = ceil
        else:
            #default is category = "Exterior"
            category = "ExteriorWall"
            typec = ext
            coder.info("Default type category used for  %s" % cadID)
        return category, typec

    def get_spaces(self):
        """
        Get the spaces in the XML
        """
        g1 = time.clock()  # GBXML Tree Time

        spaces = self.tree.xpath("/gb:gbXML/gb:Campus/gb:Building/gb:Space", namespaces=self.namespaces)

        # For each create the object
        spaces_list = list()
        i = 1
        for space in spaces:
            # Create the new space and set the different properties
            new_space = Space()
            new_space.obj_id = space.get("id")
            new_space.floor_level = space.get("buildingStoreyIdRef")

            #new_space.Q_hour_W = list()
            #new_space.Q_hour_J = list()
            new_space.EE = list()

            # Surfaces in this space:
            space_boundaries = space.xpath("./gb:SpaceBoundary", namespaces=self.namespaces)
            #Rename surface ID tags here too to match in temperature calculations
            #for surface in space_boundaries:
            #    new_space.check_obj_id = surface.get("surfaceIdRef")
            #    print "check for temp: ", new_space.check_obj_id

            new_space.surfaces = self.get_surfaces(space, space_boundaries, new_space.obj_id)

            this  = new_space.obj_id
            #self.spaces_dict  # append all the space #s with Ids to the dict, pass the dictionary somehow instead of the spaces in the ModelV1
            # This second added value of 295 may need re-defining when zones are introduces--as in may need to be set within the interface...
            # Currently, every space is set to initialize at 295K
            new_space.zone_id = space.get("zoneIdRef")
            if not new_space.zone_id:
                new_space.zone_id = "defaultZone"
            # Get the temp for the space based on the zone id from the zones_dict()
            #self.spaces_dict[this] = [new_space, 295.0]
            matching_zone_temp = self.zones_dict[new_space.zone_id]
            #print matching_zone_temp[0]
            self.spaces_dict[this] = [new_space, matching_zone_temp[0]]
            #for item in self.spaces_dict:
            #    print "here this space", item, self.spaces_dict[item]
            i += 1
            #print "dictionary: ", self.spaces_dict[this]

            space_coordinate_set = space.xpath("./gb:PlanarGeometry/gb:PolyLoop/gb:CartesianPoint", namespaces=self.namespaces)
            scps = list()
            for coordinate_list in space_coordinate_set:
                cp = list()
                cartesian_points = coordinate_list.xpath("./gb:Coordinate", namespaces=self.namespaces)
                #print "this should be 3 locations: ", cartesian_points
                for point in cartesian_points:
                    cp.append(float(point.text) * 0.3048)
                cartesian_point = tuple(cp)
                scps.append(cartesian_point)
            new_space.scps = scps  # now returning a list of tuples for non-square walls to get max/min heights
            #print "cps list of tuples: ", new_space.scps

            # Add to the return list
            spaces_list.append(new_space)

        g2 = time.clock()  # Tree Finish Time
        treetime = g2-g1
        #TM_coder.info("Total gbxml time: %s Seconds" % (treetime))
        #print "Total gbxml time: ", g2-g1

        return spaces_list

    def getRectangularGeometry(self,element,parent_node):
        """
        Retrieve the rectangular geometry of an element.
        parent_node represents the parent XML node
        """
        element.width = float(parent_node.xpath("./gb:RectangularGeometry/gb:Width",namespaces = self.namespaces)[0].text)
        element.height = float(parent_node.xpath("./gb:RectangularGeometry/gb:Height",namespaces = self.namespaces)[0].text)
        element.azimuth = float(parent_node.xpath("./gb:RectangularGeometry/gb:Azimuth",namespaces = self.namespaces)[0].text)
        element.tilt = float(parent_node.xpath("./gb:RectangularGeometry/gb:Tilt",namespaces = self.namespaces)[0].text)

        return element

    def get_surfaces(self, space, space_boundaries, current_space_id):
        """
        Get the surfaces out of the GBXML for a given space
        """
        surfaces = self.tree.xpath("/gb:gbXML/gb:Campus/gb:Surface", namespaces=self.namespaces)
        #print "length of surfaces: ", len(surfaces)  # does give 6 for model 1

        # For each surface create the object
        surfaces_list = list()
        for bounding in space_boundaries:
            new_check = Surface()
            new_check.check_obj_id = bounding.get("surfaceIdRef")
            #print new_check.check_obj_id

            for surface in surfaces:
                check = surface.get("id")
                #typesur = surface.get("surfaceType")

                # Check if the surface belongs to the right space
                # if surface.xpath("./gb:AdjacentSpaceId",namespaces = self.namespaces)[0].get("spaceIdRef") != space.obj_id:
                if check == new_check.check_obj_id:
                    # Set up the previous/current temperature dictionary
                    # Each listing tuple represents the surface (interior_side_temp, opposite_side_temp)
                    inside = check + "_inside_surface"
                    outside = check + "_outside_surface"
                    self.temp_record[inside] = 295.0     # self.temp_record[inside_surface] = [previous-insisde-surface-temp, current-insisde-surface-temp]
                    self.temp_record[outside] = 295.0   # self.temp_record[outside_surface] = [previous-outside-surface-temp, current-outside-surface-temp]
                    # to solve current temp problem
                    inside = check + "_inside_surface-1"
                    outside = check + "_outside_surface-1"
                    self.temp_record[inside] = 295.0     # self.temp_record[inside_surface] = [previous-insisde-surface-temp, current-insisde-surface-temp]
                    self.temp_record[outside] = 295.0   # self.temp_record[outside_surface] = [previous-outside-surface-temp, current-outside-surface-temp]
                    # print "this T_space: ", self.temp_record[check + "_space"][1]

                    # Create the new surface and set the different properties
                    new_surface = Surface()
                    new_surface.obj_id = surface.get("id")
                    #print new_surface.obj_id
                    new_surface.obj_type = surface.get("surfaceType")
                    #print new_surface.obj_type

                    # Special section to handle Columns and Missing ConstrIDs in Surfaces
                    new_surface.obj_constr = surface.get("constructionIdRef")
                    new_surface.columnType = None
                    new_surface.columnSize = 0
                    if new_surface.obj_type == "Air":
                        cad = "Air"
                    else:
                        cad = str(surface.xpath("./gb:CADObjectId", namespaces=self.namespaces)[0].text)
                    new_surface.cad = cad[:-9]
                    CadString = str(new_surface.cad)
                    if new_surface.obj_constr is None:
                        # There was no construction ID for this whole surface...may need a default or may be a column
                        #col1 = "column"
                        #col2 = "Column"
                        numbers = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")
                        getInchesOfColumn = 0
                        if CadString.find("column") != -1 or CadString.find("Column") != -1:
                            # Then it is a column piece so determine round or square (rectangles handled as a square)
                            if CadString.find("Square") != -1 or CadString.find("square") != -1:
                                for character in CadString:
                                    if character not in numbers:
                                        #print CadString[1:]
                                        CadString = CadString[1:]
                                    else:  # It has found the first number
                                        break
                                stopCounter = 0
                                for character in CadString:
                                    if character in numbers:
                                        stopCounter += 1
                                    else:
                                        break
                                    #else:  # Found the first in new string not in numbers
                                #print "stopCounter", stopCounter
                                length = len(CadString)
                                remove = length - stopCounter
                                CadString = CadString[:-remove]
                                #print "here", CadString[:stopCounter]
                                getInchesOfColumn = float(CadString)
                                new_surface.columnType = "square"
                                new_surface.columnSize = getInchesOfColumn  # Inches are assumed since that has been standard in the gbxml files
                                new_surface.obj_type = "Column"
                                new_surface.obj_constr = "ColumnConcrete"
                                #print "getInchesOfColumn",getInchesOfColumn
                            elif CadString.find("Round") != -1 or CadString.find("round") != -1:
                                for character in CadString:
                                    if character not in numbers:
                                        #print CadString[1:]
                                        CadString = CadString[1:]
                                    else:  # It has found the first number
                                        break
                                stopCounter = 0
                                for character in CadString:
                                    if character in numbers:
                                        stopCounter += 1
                                    else:
                                        break
                                    #else:  # Found the first in new string not in numbers
                                #print "stopCounter", stopCounter
                                length = len(CadString)
                                remove = length - stopCounter
                                CadString = CadString[:-remove]
                                #print "here", CadString[:stopCounter]
                                getInchesOfColumn = float(CadString)
                                new_surface.columnType = "round"
                                new_surface.columnSize = getInchesOfColumn  # Inches are assumed since that has been standard in the gbxml files
                                new_surface.obj_type = "Column"
                                new_surface.obj_constr = "ColumnConcrete"
                                #print "getInchesOfColumn2",getInchesOfColumn
                            else:
                                # Some other column type but assume its square for now...
                                for character in CadString:
                                    if character not in numbers:
                                        #print CadString[1:]
                                        CadString = CadString[1:]
                                    else:  # It has found the first number
                                        break
                                stopCounter = 0
                                for character in CadString:
                                    if character in numbers:
                                        stopCounter += 1
                                    else:
                                        break
                                    #else:  # Found the first in new string not in numbers
                                #print "stopCounter", stopCounter
                                length = len(CadString)
                                remove = length - stopCounter
                                CadString = CadString[:-remove]
                                #print "here", CadString[:stopCounter]
                                getInchesOfColumn = float(CadString)
                                new_surface.columnType = "square"
                                new_surface.columnSize = getInchesOfColumn  # Inches are assumed since that has been standard in the gbxml files
                                new_surface.obj_type = "Column"
                                new_surface.obj_constr = "ColumnConcrete"
                        else:
                            # It is missing a constr ID and is not a column...
                            coder.info("No Constr Type for this Surface - default used %s" % new_surface.obj_id)
                            new_surface.obj_constr = "cons-1"

                    adjacent_items = surface.xpath("./gb:AdjacentSpaceId", namespaces=self.namespaces)
                    for adjacent in adjacent_items:
                        new_surface.adjacent_space_id = adjacent.get("spaceIdRef")
                        found = new_surface.adjacent_space_id
                        #print new_surface.adjacent_space_id, "   ", current_space_id
                        if new_surface.adjacent_space_id == current_space_id:
                            new_surface.adjacent_space_id = "none"
                        else:
                            new_surface.adjacent_space_id = found
                            #print "space id from gbxml", new_surface.adjacent_space_id
                            #new_surface.adjacent_space_id = "not meeting either"
                            #print new_surface.adjacent_space_id
                            #if new_surface.obj_id == "su-4" or new_surface.obj_id == "su-6" or new_surface.obj_id == "su-11" or new_surface.obj_id == "su-10":
                            #    if new_surface.obj_type == "InteriorFloor" or new_surface.obj_type == "RaisedFloor" or new_surface.obj_type == "UndergroundSlab" or new_surface.obj_type == "SlabOnGrade":
                            #        print current_space_id, new_surface.obj_id, new_surface.adjacent_space_id
                            break

                    #adjacent_item = list()  # Trying to create a new sublist each time for all adjacent spaces
                    #new_item = Surface()
                    #new_item.adjacent = adjacent.get("spacedIdRef")
                    #adjacent_item.append(adjacent_item)
                    #new_surface.space = space

                    # Retrieve the geometry from here...
                    new_surface = self.getRectangularGeometry(new_surface, surface)
                    recs = surface.xpath("./gb:RectangularGeometry/gb:CartesianPoint/gb:Coordinate", namespaces=self.namespaces)
                    rec = list()
                    for arec in recs:
                        rec.append(float(arec.text) * 0.3048)
                    new_surface.rec = rec
                    #print "this should be a 3-item list: ", new_surface.rec

                    # Add the openings
                    new_surface.openings = self.get_openings(new_surface, surface)

                    coordinate_set = surface.xpath("./gb:PlanarGeometry/gb:PolyLoop/gb:CartesianPoint", namespaces=self.namespaces)
                    cps = list()
                    for coordinate_list in coordinate_set:
                        cp = list()
                        cartesian_points = coordinate_list.xpath("./gb:Coordinate", namespaces=self.namespaces)
                        #print "this should be 3 locations: ", cartesian_points
                        for point in cartesian_points:
                            cp.append(float(point.text) * 0.3048)
                        cartesian_point = tuple(cp)
                        cps.append(cartesian_point)
                    new_surface.cps = cps  # now returning a list of tuples for non-square walls to get max/min heights
                    #print "cps list of tuples: ", new_surface.cps

                    # Add the layers of the current surface
                    # C value are calculated below in the Layer and Material Objects
                    #new_surface.construction = self.get_constr(surface, new_surface.obj_constr)
                    #if new_surface.obj_id == "su-4" or new_surface.obj_id == "su-10":
                    #    print new_surface.obj_id
                    if new_surface.obj_type == "Column":
                        new_surface.construction = self.defaultColumn(new_surface, surface, new_surface.obj_constr, new_surface.columnSize)
                    else:
                        new_surface.construction = self.get_constr(new_surface, surface, new_surface.obj_constr)

                    area = Area()
                    A = area.surfaceArea(new_surface.cps, new_surface.azimuth, new_surface.tilt, surface)
                    area.addArea(new_surface.obj_id, A)

                    # Add to the list
                    surfaces_list.append(new_surface)

                    self.surfaces_dict[new_surface.obj_id] = new_surface

                    if new_surface.obj_type == "ExteriorWall" or new_surface.obj_type == "Roof":
                        d = 0
                        self.shade_surface_total.append(d)
                        self.shadow_record[new_surface.obj_id] = new_surface
                    #print "to get C surface from surfaces...: ", new_surface.construction[0].layer[0].C_Total    # this works as well to get down to the C_Total from materials
                    break
                else:
                    continue
                #if typesur == "Shade":
                    #continue

        return surfaces_list

    def get_openings(self, new_surface, surface):
        """
        Get the openings for a given surface
        """
        # First retrieve the surface XML node
        #surface_node = self.tree.xpath("/gb:gbXML/gb:Campus/gb:Surface[@id='%s']" % new_surface.obj_id ,namespaces = self.namespaces)[0]

        # Then retrieve the openings
        openings = surface.xpath("./gb:Opening", namespaces=self.namespaces)

        # Create the return list
        openings_lists = list()
        #windows_list = list()

        # Create each openings
        for opening in openings:
            windows_list = list()
            new_opening = Opening()
            new_opening.obj_id = opening.get("id")

            typeTest = opening.get("openingType")
            if typeTest is None:
                # If no Type Tag is in the gbxml, then give it a default for now and log it
                coder.info("No Type Tag for this gbxml opening - default given as OperableWindow %s" % new_opening.obj_id)
                new_opening.obj_type = "OperableWindow"
            else:
                # There is one as expected and will use that one
                new_opening.obj_type = typeTest
            obj_type_ref_test = opening.get("windowTypeIdRef")    # if it is a window will have the tag windowTypeIdRef
            obj_cons_ref_test = opening.get("constructionIdRef")  # if it is a door will have the tag constructionIdRef
            #stop = opening.xpath.xpath("./gb:Stop", namespaces=self.namespaces)

            # Retrieve the geometry
            new_opening = self.getRectangularGeometry(new_opening,opening)

            # Get the cartesian points for this particular window
            cartesian_points = opening.xpath("./gb:RectangularGeometry/gb:CartesianPoint/gb:Coordinate", namespaces=self.namespaces)
            wcp = list()
            for point in cartesian_points:
                wcp.append(float(point.text) * 0.3048)
            new_opening.cartesian_point = tuple(wcp)

            coordinate_seta = opening.xpath("./gb:PlanarGeometry/gb:PolyLoop/gb:CartesianPoint", namespaces=self.namespaces)
            ocps = list()
            for coordinate_list in coordinate_seta:
                ocp = list()
                cartesian_pointsa = coordinate_list.xpath("./gb:Coordinate", namespaces=self.namespaces)
                #print "this should be 3 locations: ", cartesian_points
                for point in cartesian_pointsa:
                    ocp.append(float(point.text) * 0.3048)
                cartesian_point = tuple(ocp)
                ocps.append(cartesian_point)
            new_opening.ocps = ocps  # now returning a list of tuples for non-square walls to get max/min heights

            area = Area()
            A = area.surfaceArea(new_opening.ocps, new_opening.azimuth, new_opening.tilt, opening)
            area.addWinArea(new_opening.obj_id, A)

            if obj_type_ref_test is None and obj_cons_ref_test is not None:
                # Verify what you have been handed is a actually a construction
                if not obj_cons_ref_test in self.constrID_dict:
                    if not obj_cons_ref_test in self.windowsID_dict:
                        # Not in either
                        new_opening.obj_type = "NonSlidingDoor"
                        new_opening.obj_type_ref = None
                        new_opening.obj_cons_ref = self.DefaultDoorConsId
                        new_opening.material = self.get_constr(opening, new_opening.obj_cons_ref, new_opening.obj_cons_ref)
                    elif obj_cons_ref_test in self.windowsID_dict:
                        # But it is in Windows
                        new_opening.obj_type_ref = self.windowsID_dict[obj_cons_ref_test]
                        new_opening.obj_type = "OperableWindow"
                        new_opening.obj_cons_ref = None  # Null previous existing window ID
                        new_opening.material = self.window_detail(new_opening, opening, new_opening.obj_type_ref, windows_list)
                    else:
                        x = 0
                else:
                    # Yes it is a construction as expected
                    new_opening.obj_cons_ref = obj_cons_ref_test
                    new_opening.obj_type_ref = None
                    new_opening.material = self.get_constr(opening, new_opening.obj_cons_ref, new_opening.obj_cons_ref)
                    #print "see if this gives the construction details: ", new_opening.material[0].obj_name, ".....", new_opening.material[0].u_value
            elif obj_cons_ref_test is None and obj_type_ref_test is not None:
                # Verify what you have been handed is a actually a window
                if not obj_type_ref_test in self.windowsID_dict:
                    if not obj_type_ref_test in self.constrID_dict:
                        # Not in either
                        new_opening.obj_type = "NonSlidingDoor"
                        new_opening.obj_type_ref = None
                        new_opening.obj_cons_ref = self.DefaultDoorConsId
                        new_opening.material = self.get_constr(opening, new_opening.obj_cons_ref, new_opening.obj_cons_ref)
                    elif obj_type_ref_test in self.constrID_dict:
                        # But it is in Constructions
                        new_opening.obj_cons_ref = self.constrID_dict[obj_type_ref_test]
                        new_opening.obj_type = "NonSlidingDoor"
                        new_opening.obj_type_ref = None  # Null previous existing window ID
                        new_opening.material = self.get_constr(opening, new_opening.obj_cons_ref, new_opening.obj_cons_ref)
                    else:
                        x = 0
                else:
                    # Yes it is a window as expected
                    new_opening.obj_type_ref = obj_type_ref_test
                    new_opening.obj_cons_ref = None
                    new_opening.material = self.window_detail(new_opening, opening, new_opening.obj_type_ref, windows_list)
                    #print "see if this gives the window details: ", new_opening.material[0].u_value, ".....", new_opening.material[0].obj_name
            elif new_opening.obj_type == "Air":
                x = 0
                # An object type of Air will obviously not have any type of ID so check the obj_type
                new_opening.obj_cons_ref = "AirSpace"
                new_opening.obj_type_ref = None
                #new_opening.obj_type = "AirSpace"
                # Adding Air Surface Default Values...need to have a second case of plain glass values here instead
                new_opening.material = self.air_surface(opening, new_opening.obj_cons_ref, new_opening.obj_cons_ref)
            elif obj_cons_ref_test is None and obj_type_ref_test is None:
                # This will have to be some default case where it is not air and needs some ID type and file gives none
                # For now, will use the temp value set up in the __init__ above:
                w = "Window"
                d = "Door"
                currentType = new_opening.obj_type  # Will be "NonSlidingDoor" or "OperableWindow", for example
                if currentType.find(d) == -1:  # This this is not a Door Type, so assume its a window
                    new_opening.obj_cons_ref = None
                    if self.DefaultWindowConsId == "none":
                        #print "reaching here", new_opening.obj_id
                        # But if there was no ID tag and the default set was to "none" then:
                        new_opening.obj_type_ref = 'GSP4R'
                        new_opening.material = self.defaultWindow(new_opening, opening, new_opening.obj_type_ref, windows_list)
                        coder.info("No ID tag in gbxml or window types - default window used %s" % new_opening.obj_type_ref)
                    else:
                        new_opening.obj_type_ref = self.DefaultWindowConsId
                        new_opening.material = self.window_detail(new_opening, opening, new_opening.obj_type_ref, windows_list)
                elif currentType.find(w) == -1:  # This this is not a Window Type, so assume its a door
                    new_opening.obj_type_ref = None
                    if self.DefaultDoorConsId == "none":
                        #print "reaching there", new_opening.obj_id
                        # But if there was no ID tag and the default set was to "none" then:
                        new_opening.obj_cons_ref = 'MDOOR'
                        new_opening.material = self.defaultConstr(opening, new_opening.obj_cons_ref)
                        coder.info("No ID tag in gbxml or door types - default door used %s" % new_opening.obj_cons_ref)
                    else:
                        new_opening.obj_cons_ref = self.DefaultDoorConsId
                        new_opening.material = self.get_constr(opening, new_opening.obj_cons_ref, new_opening.obj_cons_ref)
                    #print "here"

                else:
                    coder.info("No windowTypeIdRef or constructionIdRef for this opening %s" % new_opening.obj_id)
                    U = GSUtility()
                    thing1 = new_opening.obj_id
                    thing1s = str(thing1)
                    thing1s = "There is no windowTypeIdRef or constructionIdRef for this surface opening: " + thing1s
                    U.devPrint(thing1s)
                    #U.devPrint("There is no windowTypeIdRef or constructionIdRef for this surface opening: ", new_opening.obj_id)
                    #print "There is no windowTypeIdRef or constructionIdRef for this surface opening: ", new_opening.obj_id

            else:
                coder.info("Missing windowTypeIdRef or constructionIdRef %s" % new_opening.obj_id)
                U = GSUtility()
                thing1 = new_opening.obj_id
                thing1s = str(thing1)
                thing1s = "Missing windowTypeIdRef or constructionIdRef: " + thing1s
                U.devPrint(thing1s)
                #U.devPrint("Missing windowTypeIdRef or constructionIdRef: ", new_opening.obj_id)
                #print "Missing windowTypeIdRef or constructionIdRef: ", new_opening.obj_id
                #new_opening.material = self.air_surface()  # Adding Air Surface Default Values

            # Add to the list
            openings_lists.append(new_opening)
            #if new_opening.obj_id == "su-19-op-1" or new_opening.obj_id == "su-19-op-2":
                #print "just added: ", new_opening.obj_id

        return openings_lists

    def window_detail(self, new_opening, opening, window_type_in_surface, windows_list):
        """
        Get the window detail for a given opening in the XML
        """
        # First retrieve the window XML node
        window_types = self.tree.xpath("/gb:gbXML/gb:WindowType", namespaces=self.namespaces)
        # Then retrieve the materials in that construction
        #window_types_in_surface = new_opening.xpath("./gb:WindowType", namespaces = self.namespaces)
        # For each create the object
        #windows_list = list()
        for window_type in window_types:
            # Check if the surface belongs to the right space this is a check that can be added later
            # If surface.xpath("./gb:Construction",namespaces = self.namespaces)[0].get("id") != surface.obj_constr:
            #    continue
            new_window = Material()
            new_window.obj_id = window_type.get("id")
            new_window.check = 1
            this_window_id = new_window.obj_id

            if this_window_id == window_type_in_surface:
                # Add attributes of this material in this layer: Name Description U-value SolarHeatGainCoeff Transmittance
                # values
                new_window.obj_name = str(window_type.xpath("./gb:Name", namespaces=self.namespaces)[0].text)
                #print new_window.obj_name

                new_window.description = str(window_type.xpath("./gb:Description", namespaces=self.namespaces)[0].text)
                #print new_window.description

                new_window.u_value = float(window_type.xpath("./gb:U-value", namespaces=self.namespaces)[0].text)
                #print new_window.u_value
                units = window_type.xpath("./gb:U-value", namespaces=self.namespaces)
                for unit in units:
                    new_window.u_value_unit = unit.get("unit")
                #print new_window.u_value_unit

                # Moved the SHGC dictionary to __init__

                new_window.transmittance = float(window_type.xpath("./gb:Transmittance", namespaces=self.namespaces)[0].text)
                #print new_window.transmittance
                transmit = window_type.xpath("./gb:Transmittance", namespaces=self.namespaces)
                for unit in transmit:
                    new_window.transmittance_unit = unit.get("unit")
                    new_window.transmittance_type = unit.get("type")
                #print new_window.transmittance_unit
                #print new_window.transmittance_type

                # Add to the return list and repeat as needed for each material of this construction
                windows_list.append(new_window)

                break
            else:
                continue

        return windows_list

    def get_constr(self, new_surface, surface, obj_constr):
        # self, current node, parent node
        """
        Get the constructions for a given surface in the XML
        """
        # First retrieve the matching construction XML node

        constructions = self.tree.xpath("/gb:gbXML/gb:Construction", namespaces=self.namespaces)
        if not constructions:
            if self.DE1 == 0:
                print "Data Error 1: Missing Construction Tags"
                self.DE1 = 1

        # For each create the object
        constr_list = list()
        layers_list = list()
        #for surface in surface:                               #something to tie it to the surface or group of surfaces it is on
        for constr in constructions:
            check = constr.get("id")
            if check == obj_constr:
                # Create the new construction and set the different properties
                new_constr = Construction()
                new_constr.obj_id = obj_constr
                new_constr.check = 0

                new_constr.obj_name = str(constr.xpath("./gb:Name", namespaces=self.namespaces)[0].text)
                # print new_constr.obj_name

                units = constr.xpath("./gb:U-value", namespaces=self.namespaces)
                if not units:
                    new_constr.u_value = None
                    new_constr.u_value_unit = None
                else:
                    new_constr.u_value = float(constr.xpath("./gb:U-value", namespaces=self.namespaces)[0].text)
                    # print new_constr.u_value
                    for unit in units:
                        new_constr.u_value_unit = unit.get("unit")

                absorp = constr.xpath("./gb:Absorptance", namespaces=self.namespaces)
                if not absorp:
                    #print "no tag for this: "
                    new_constr.absorptance = None
                    new_constr.absorptance_unit = None
                    new_constr.absorptance_type = None
                else:
                    new_constr.absorptance = float(constr.xpath("./gb:Absorptance", namespaces=self.namespaces)[0].text)
                    #print new_constr.absorptance
                    for item in absorp:
                        new_constr.absorptance_unit = item.get("unit")
                        #print new_constr.absorptance_unit
                        new_constr.absorptance_type = item.get("type")
                        #print new_constr.absorptance_type

                rough = constr.xpath("./gb:Roughness", namespaces=self.namespaces)
                if not rough:
                    new_constr.roughness = None
                    new_constr.roughness_unit = None
                else:
                    new_constr.roughness = str(constr.xpath("./gb:Roughness", namespaces=self.namespaces)[0].text)
                    #print new_constr.roughness
                    for value in rough:
                        new_constr.roughness_unit = value.get("value")
                        # print new_constr.roughness_unit

                layerSet = constr.xpath("./gb:LayerId", namespaces=self.namespaces)
                if not layerSet:
                    new_constr.layer_id = None
                else:
                    for layer in layerSet:
                        new_constr.layer_id = layer.get("layerIdRef")
                        new_constr.layer = self.get_layer(new_constr, constr, new_constr.layer_id, layers_list)
                        #append new layer object

                #print "look here: ", new_constr.layer[0].C_Total    # This is working to call the C_Total below, gives one answer for each surface

                # Add to the return list
                constr_list.append(new_constr)

                break
            else:
                continue

        return constr_list

    def get_layer(self, new_constr, constr, layer_id, layers_list):
        # self, current node, parent node
        """
        Get the layers for a given construction in the XML
        """
        # First retrieve the layer XML node
        layers = self.tree.xpath("/gb:gbXML/gb:Layer", namespaces=self.namespaces)
        if not layers:
            if self.DE2 == 0:
                print "Data Error 2: Missing Layer Tags"
                self.DE2 = 1
        bit = 0
        i = 0
        #layers = layer_node.xpath("./gb:MaterialId", namespaces = self.namespaces)

        # For each create the object
        #layers_list = list()
        materials_list = list()
        for layer in layers:
            check = layer.get("id")
            if check == layer_id:
                # Create the new layer and set the different properties
                new_layer = Layer()
                new_layer.layer_id = layer.get("id")
                # Add material ids of this level of the surface: materialIdRef
                elements = layer.xpath("./gb:MaterialId", namespaces=self.namespaces)
                for element in elements:
                    new_layer.material_id_num = element.get("materialIdRef")
                    #print new_layer.material_id_num

                    # Add the material data by layer number as labeled in the XML
                    new_layer.material = self.get_material(new_layer, layer, new_layer.material_id_num, materials_list)

                    # Should have retrieved the C-value for each material below to sum up here
                    if bit == 0:
                        new_layer.C_total = new_layer.material[i].C
                        #print "get the C value up in layers"
                        #print new_layer.C_total
                        bit = 1
                        i += 1
                    else:
                        new_layer.C_total = new_layer.C_total + new_layer.material[i].C
                        i += 1
                new_layer.C_Total = new_layer.C_total
                #print "C_total for the gbXML is: ", new_layer.C_total
                # Add to the return list
                layers_list.append(new_layer)
                #print "current C total after the addition of this material: ", new_layer.C_total
                #print "Total C for this surface/ wall assembly is: ", new_layer.C_total
            else:
                continue

        return layers_list

    def get_allMaterials(self):
        names = list()
        materials = self.tree.xpath("/gb:gbXML/gb:Material", namespaces=self.namespaces)
        for material in materials:
            names.append(str(material.xpath("./gb:Name", namespaces=self.namespaces)[0].text))
        windows = self.tree.xpath("/gb:gbXML/gb:WindowType", namespaces=self.namespaces)
        for window in windows:
            names.append(str(window.xpath("./gb:Name", namespaces=self.namespaces)[0].text))
        return names

    def get_material(self, new_layer, layer, material_id_num, materials_list):
        # self, current node, parent node
        """
        Get the layers for a given surface in the XML
        """
        # First retrieve the surface XML node
        materials = self.tree.xpath("/gb:gbXML/gb:Material", namespaces=self.namespaces)
        if not materials:
            if self.DE3 == 0:
                print "Data Error 3: Missing Materials Tags"
                self.DE3 = 1
        # For each create the object

        #materials_list = list()
        for material in materials:
            check = material.get("id")
            if check == material_id_num:
                new_material = Material()
                new_material.obj_id = material.get("id")
                #print new_material.obj_id

                # Add attributes of this material in this layer: Name U-value Absorptance Roughness LayerId
                new_material.name = str(material.xpath("./gb:Name", namespaces=self.namespaces)[0].text)
                #print new_material.name

                # Description left out of DOOR Materials and doors have no R-value, need to use the U-value

                rvalue = material.xpath("./gb:R-value", namespaces=self.namespaces)
                if not rvalue:
                    new_material.r_value = None
                    new_material.r_value_unit = None
                else:
                    new_material.r_value = float(material.xpath("./gb:R-value", namespaces=self.namespaces)[0].text)
                    #print "r-value:"
                    #print new_material.r_value
                    for value in rvalue:
                        new_material.r_value_unit = value.get("unit")
                        #print new_material.r_value_unit

                new_material.thickness = float(material.xpath("./gb:Thickness", namespaces=self.namespaces)[0].text)
                #print "thickness:"
                #print new_material.thickness
                thickness = material.xpath("./gb:Thickness", namespaces=self.namespaces)
                for value in thickness:
                    new_material.thickness_unit = value.get("unit")
                #print new_material.thickness_unit

                new_material.conductivity = float(material.xpath("./gb:Conductivity", namespaces=self.namespaces)[0].text)
                #print "conductivity:"
                #print new_material.conductivity
                conductivity = material.xpath("./gb:Conductivity", namespaces=self.namespaces)
                for value in conductivity:
                    new_material.conductivity_unit = value.get("unit")
                #print new_material.conductivity_unit

                #WSD = wsData()
                #DBData = WSD.getDBMaterials()
                #if len(DBData) > 0:
                #    for item in DBData:
                #        if new_material.name == item['namegbxml']:
                #            new_material.density = float(item['matdensityarch'])
                #            new_material.densityunit = item['denUnit']
                #            if new_material.densityunit == 'kg/m^3':
                #                new_material.density *= 0.06243

                new_material.density = float(material.xpath("./gb:Density", namespaces=self.namespaces)[0].text)
                #print "density:"
                #print new_material.density
                density = material.xpath("./gb:Density", namespaces=self.namespaces)
                for value in density:
                    new_material.density_unit = value.get("unit")
                #print new_material.density_unit

                new_material.specific_heat = float(material.xpath("./gb:SpecificHeat", namespaces=self.namespaces)[0].text)
                #print "heat:"
                #print new_material.specific_heat
                heat = material.xpath("./gb:SpecificHeat", namespaces=self.namespaces)
                for value in heat:
                    new_material.specific_heat_unit = value.get("unit")
                #print new_material.specific_heat_unit

                # Calculate the C value for each material of the surface. C = density * specific heat * thickness
                # The new_material.C is what will be used in the summation once back in the get_layers function
                new_material.C = new_material.density * new_material.specific_heat * new_material.thickness
                #print "C-value for this material: ", new_material.C

                # Add to the return list and repeat as needed for each material of this construction
                materials_list.append(new_material)

                #stop = materials.xpath.xpath("./gb:Stop", namespaces=self.namespaces)

            else:
                continue

        #return materials_list
        return materials_list

    def air_surface(self, opening, new_opening, air_construction):
        #<Opening id="su-63-op-1" openingType="NonSlidingDoor">  # Error Fix: No Construction ID for this Opening=Air
        #<Opening id="su-19-op-1" openingType="Air">             # Error Fix: No Construction ID for this Opening=Air

        # For each create the object
        constr_list = list()
        layers_list = list()
        materials_list = list()

        new_constr = Construction()
        new_constr.obj_id = air_construction
        new_constr.obj_name = "AirSpace"
        new_constr.check = 1
        new_constr.u_value = 0.610
        new_constr.u_value_unit = "WPerSquareMeterK"
        new_constr.absorptance = 0
        new_constr.absorptance_unit = "Fraction"
        new_constr.absorptance_type = "VerySmooth"
        new_constr.roughness = 0
        new_constr.roughness_unit = None
        new_constr.layer_id = "AirSpace"

        new_layer = Layer()
        new_layer.layer_id = "AirSpace"

        new_material = Material()
        new_material.obj_id = "AirSpace"
        new_material.r_value = 1.639
        new_material.r_value_unit = "SquareMeterKPerW"
        new_material.thickness = 0
        new_material.thickness_unit = "Meters"
        new_material.conductivity = 0.0271
        new_material.conductivity_unit = "WPerMeterK"
        new_material.density = 1.127
        new_material.density_unit = "KgPerCubicM"
        new_material.specific_heat = 1.005
        new_material.specific_heat_unit = "JPerKgK"
        new_material.C = new_material.density * new_material.specific_heat * new_material.thickness
        materials_list.append(new_material)

        new_layer.material = materials_list
        # Do not need to pull from the material list because thickness = 0 makes C-value always 0
        new_layer.C_Total = 0
        layers_list.append(new_layer)

        new_constr.layer = layers_list
        constr_list.append(new_constr)

        #print "constr_list, ", constr_list

        return constr_list

    def defaultWindow(self, new_opening, opening, window_type_in_surface, windows_list):
        """
        Get a default window detail when window material data nowhere in the XML
        """
        new_window = Material()
        new_window.obj_id = window_type_in_surface
        new_window.check = 1
        new_window.obj_name = 'Default 1/8 in Pilkington single glazing'
        new_window.description = '1/8 in (3 mm) Pilkington single glazing'
        new_window.u_value = 6.7069
        new_window.u_value_unit = 'WPerSquareMeterK'
        new_window.transmittance = 0.90
        new_window.transmittance_unit = 'Fraction'
        new_window.transmittance_type = 'Visible'
        windows_list.append(new_window)

        return windows_list

    def defaultConstr(self, opening, obj_constr):
        new_constr = Construction()
        constr_list = list()
        layers_list = list()
        new_constr.obj_id = obj_constr
        new_constr.obj_name = "Metal"
        new_constr.check = 0  # 0 = not a window in GreenscaleEE.py
        new_constr.u_value = 3.7021
        new_constr.u_value_unit = "WPerSquareMeterK"
        new_constr.absorptance = None
        new_constr.absorptance_unit = None
        new_constr.absorptance_type = None
        new_constr.roughness = None
        new_constr.roughness_unit = None
        new_constr.layer_id = "lay-MDOOR"
        new_constr.layer = self.defaultDoorLayers(new_constr, new_constr.layer_id, layers_list)
        constr_list.append(new_constr)

        return constr_list

    def defaultDoorLayers(self, new_constr, layer_id, layers_list):
        new_layer = Layer()
        bit = 0
        i = 0
        materials_list = list()
        new_layer.layer_id = "lay-MDOOR"
        elements = list()
        elements.append("mat-AF08")
        elements.append("mat-860")
        elements.append("mat-AF08")
        for element in elements:
            new_layer.material_id_num = element
            new_layer.material = self.defaultDoorMaterials(new_layer, new_layer.material_id_num, materials_list)
            # Should have retrieved the C-value for each material below to sum up here
            if bit == 0:
                new_layer.C_total = new_layer.material[i].C
                bit = 1
                i += 1
            else:
                new_layer.C_total = new_layer.C_total + new_layer.material[i].C
                i += 1
            new_layer.C_Total = new_layer.C_total
            layers_list.append(new_layer)

        return layers_list

    def defaultDoorMaterials(self, new_layer, material_id_num, materials_list):
        if material_id_num == "mat-AF08":
            new_material = Material()
            new_material.obj_id = "mat-AF08"
            new_material.name = "Default Metal surface"
            new_material.r_value = None
            new_material.r_value_unit = None
            new_material.thickness = 0.0008
            new_material.thickness_unit = "Meters"
            new_material.conductivity = 45.28
            new_material.conductivity_unit = "WPerMeterK"
            new_material.density = 7824
            new_material.densityunit = "KgPerCubicM"
            new_material.specific_heat = 500
            new_material.specific_heat_unit = "JPerKgK"
            new_material.C = new_material.density * new_material.specific_heat * new_material.thickness
            materials_list.append(new_material)
        if material_id_num == "mat-860":
            new_material = Material()
            new_material.obj_id = "mat-860"
            new_material.name = "Default 1 1/2 in wood"
            new_material.r_value = None
            new_material.r_value_unit = None
            new_material.thickness = 0.0376
            new_material.thickness_unit = "Meters"
            new_material.conductivity = 0.15
            new_material.conductivity_unit = "WPerMeterK"
            new_material.density = 608
            new_material.densityunit = "KgPerCubicM"
            new_material.specific_heat = 1630
            new_material.specific_heat_unit = "JPerKgK"
            new_material.C = new_material.density * new_material.specific_heat * new_material.thickness
            materials_list.append(new_material)

        return materials_list

    def defaultColumn(self, new_surface, surface, obj_constr, colSize):
        new_constr = Construction()
        constr_list = list()
        layers_list = list()
        new_constr.obj_id = obj_constr
        new_constr.obj_name = "Concrete Column"
        new_constr.check = 0  # 0 = not a window in GreenscaleEE.py
        new_constr.u_value = 5.147638
        new_constr.u_value_unit = "WPerSquareMeterK"
        new_constr.absorptance = 0.100000
        new_constr.absorptance_unit = "Fraction"
        new_constr.absorptance_type = "ExtIR"
        new_constr.roughness = None
        new_constr.roughness_unit = "VeryRough"
        new_constr.layer_id = "lay-COLUMN"
        new_constr.layer = self.defaultColumnLayers(new_constr, new_constr.layer_id, layers_list, colSize)
        constr_list.append(new_constr)

        return constr_list

    def defaultColumnLayers(self, new_constr, layer_id, layers_list, colSize):
        new_layer = Layer()
        bit = 0
        i = 0
        materials_list = list()
        new_layer.layer_id = "lay-COLUMN"
        elements = list()
        elements.append("mat-COL")
        for element in elements:
            new_layer.material_id_num = element
            new_layer.material = self.defaultColumnMaterials(new_layer, new_layer.material_id_num, materials_list, colSize)
            # Should have retrieved the C-value for each material below to sum up here
            if bit == 0:
                new_layer.C_total = new_layer.material[i].C
                bit = 1
                i += 1
            else:
                new_layer.C_total = new_layer.C_total + new_layer.material[i].C
                i += 1
            new_layer.C_Total = new_layer.C_total
            layers_list.append(new_layer)

        return layers_list

    def defaultColumnMaterials(self, new_layer, material_id_num, materials_list, colSize):
        new_material = Material()
        new_material.obj_id = "mat-COL"
        new_material.name = 'Concrete, Precast: 8"'
        new_material.r_value = 0.194264
        new_material.r_value_unit = "SquareMeterKPerW"
        new_material.thickness = colSize  # Left in inches since passing in TM and inches used in EE, rest in metric
        new_material.thickness_unit = "Meters"
        new_material.conductivity = 1.046000
        new_material.conductivity_unit = "WPerMeterK"
        new_material.density = 2300.000000
        new_material.densityunit = "KgPerCubicM"
        new_material.specific_heat = 657.000000
        new_material.specific_heat_unit = "JPerKgK"
        new_material.C = new_material.density * new_material.specific_heat * new_material.thickness
        materials_list.append(new_material)

        return materials_list


