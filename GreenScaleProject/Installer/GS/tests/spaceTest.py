#-------------------------------------------------------------------------------
# Name:        spaceTest.py
# Purpose:     Green Scale Tool UnitTests (space test)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
from datetime import datetime
import os
import unittest
from Weather import Weather
from gbXML import gbXML
from objects.Space import Space
from objects.Area import Area


class SpaceTest(unittest.TestCase):

    def setUp(self):
        self.gbxml = gbXML(os.path.join(os.path.dirname(__file__), 'input/Single_model.xml'))
        #self.gbxml = gbXML(os.path.join(os.path.dirname(__file__), 'input/Four_Room_Two_Floors_Model.xml')) # To test middle interior floor
        area = Area()
        area.createAreaDictionary()
        area.createWinAreaDictionary()
        self.areaWinDict = area.getWinDictionary()
        self.areaDict = area.getDictionary()

        spaces = self.gbxml.get_spaces()
        self.volume = Space()
        self.temp_record = self.gbxml.temp_record
        self.spaces_dict = self.gbxml.spaces_dict
        self.shgc_dictionary = self.gbxml.shgc_dictionary
        self.shadow_record = self.gbxml.shadow_record
        self.shade_surf_list = self.gbxml.get_shades()
        self.surfaces_dict = self.gbxml.surfaces_dict

        self.space1 = spaces[0]
        surfaces = spaces[0].surfaces
        self.surface6 = surfaces[5]
        self.surface5 = surfaces[4]
        self.surface4 = surfaces[3]
        self.surface3 = surfaces[2]
        self.surface2 = surfaces[1]
        self.surface1 = surfaces[0]

        # Create a fake weather
        self.weather = Weather('Washington',datetime(year=1997,month=1,day=1,hour=3),datetime(year=1997,month=1,day=1,hour=4))

        # And a timestep
        self.tstep2 = datetime(year=1997,month=1,day=1,hour=4)
        # get the weather at the tstep
        self.wtstep2 = self.weather.get_weather_step(self.tstep2)

        # And another timestep
        self.tstep = datetime(year=1997,month=1,day=1,hour=3)
        # get the weather at the tstep
        self.wtstep = self.weather.get_weather_step(self.tstep)


    def test_calculate_space_heatflux(self):
        Coeff = 1
        ShadowsFlag = 0
        terrain = "Flat or Open Countryside"
        A = 0
        missing_surfaces = dict()  # Should not matter for this test case
        G_space_record = dict()
        G_space_record["su-1"] = 0
        G_space_record["su-2"] = 0
        G_space_record["su-3"] = 0
        G_space_record["su-4"] = 0
        G_space_record["su-5"] = 0
        G_space_record["su-6"] = 0
        ns = ( len(self.shade_surf_list) + len(self.shadow_record) )
        heatflux = self.volume.calculate_space_heatflux(self.space1, self.wtstep, self.spaces_dict, self.temp_record, Coeff, ShadowsFlag, ns, self.shadow_record, self.shade_surf_list, self.surfaces_dict, A, missing_surfaces, terrain, G_space_record, self.areaDict, self.areaWinDict)
        self.assertEqual(heatflux, 45.659443, 'heatflux for this space is: %s ' % heatflux)  # Getting 45.256363 for single model until compare with Na


    def test_get_height(self):
        x = self.temp_record
        height = self.volume.get_height(self.surface5)
        self.assertEqual(height, 3.37185, 'height for surface 5: %s ' % height)

        height = self.volume.get_height(self.surface6)
        self.assertEqual(height, 0, 'height for surface 6: %s ' % height)  #This is the floor level = 0

        height = self.volume.get_height(self.surface1)
        self.assertEqual(height, 1.685925, 'height for surface 1: %s ' % height)

        height = self.volume.get_height(self.surface2)
        self.assertEqual(height, 1.685925, 'height for surface 2: %s ' % height)

        height = self.volume.get_height(self.surface3)
        self.assertEqual(height, 1.685925, 'height for surface 3: %s ' % height)

        height = self.volume.get_height(self.surface4)
        self.assertEqual(height, 1.685925, 'height for surface 4: %s ' % height)


    def test_get_height_floorspace(self):
        height = self.volume.get_height_floorspace(self.space1)
        #print "height is: ", height
        self.assertEqual(height[0], 0, 'height for surface 6: %s ' % height[0]) # 6 is the only floor to test here

