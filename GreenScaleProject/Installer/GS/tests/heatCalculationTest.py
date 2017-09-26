#-------------------------------------------------------------------------------
# Name:        heatCalculationTest.py
# Purpose:     Green Scale Tool UnitTests (heat calculation test)
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
from objects.Surface import Surface
from objects.HeatCalculation import HeatCalculation
from objects.Area import Area


class HeatCalculationTest(unittest.TestCase):

    def setUp(self):
        self.gbxml = gbXML(os.path.join(os.path.dirname(__file__), 'input/Single_model.xml'))
        #self.gbxml = gbXML(os.path.join(os.path.dirname(__file__), 'input/Four_Room_Two_Floors_Model.xml')) # To test middle interior floor
        area = Area()
        area.createAreaDictionary()
        area.createWinAreaDictionary()
        self.areaWinDict = area.getWinDictionary()
        self.areaDict = area.getDictionary()

        spaces = self.gbxml.get_spaces()
        surfaces = spaces[0].surfaces
        self.heat = HeatCalculation()
        self.temp_record = self.gbxml.temp_record
        self.spaces_dict = self.gbxml.spaces_dict
        self.shgc_dictionary = self.gbxml.shgc_dictionary
        self.shadow_record = self.gbxml.shadow_record
        self.shade_surf_list = self.gbxml.get_shades()
        self.surfaces_dict = self.gbxml.surfaces_dict

        self.space1 = spaces[0]
        #surfaces1 = spaces[0].surfaces
        #self.space2 = spaces[1]
        #surfaces2 = spaces[1].surfaces
        #self.surface6 = surfaces1[5]   # su-6
        #self.surface11 = surfaces2[5]  # su-11

        self.surface1 = surfaces[0]
        self.surface2 = surfaces[1]
        self.surface3 = surfaces[2]
        self.surface4 = surfaces[3]
        self.surface5 = surfaces[4]
        self.surface6 = surfaces[5]

        self.G_space_record = dict()
        self.G_space_record["sp-1-Room"] = 0

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

    def test_get_floor_heat(self):  # done with the four room model as gbxml input above
        A_noOp_floor = 9.290304
        G_space = 0
        #floor_heat = self.heat.get_floor_heat(self.surface6, self.wtstep, G_space, self.spaces_dict, A_noOp_floor, self.temp_record)
        #self.assertEqual(floor_heat, -16.112311, 'top heat for surface 6: %s ' % floor_heat)  #Getting -16.112311 but need to check these with Na, also the G_space
        Coeff = 1
        A_noOp_floor = 9.290304
        G_space = 0
        floor_heat = self.heat.get_floor_heat(self.space1, self.surface6, self.wtstep, G_space, self.spaces_dict, A_noOp_floor, self.temp_record, Coeff, self.areaDict, self.areaWinDict)
        floor_heat = round(floor_heat, 3)
        self.assertEqual(floor_heat, -1.984, 'top heat for surface 11: %s ' % floor_heat)  #Getting -16.112311 but need to check these with Na, also the G_space

    def test_get_top_heat(self):
        Coeff = 1
        floor_heat = self.heat.get_top_heat(self.space1, self.surface4, self.wtstep, self.spaces_dict, self.temp_record, Coeff, self.G_space_record, self.areaDict, self.areaWinDict)
        floor_heat = round(floor_heat, 15)
        self.assertEqual(floor_heat, -0.00000000000236, 'top heat for surface 5 (roof): %s ' % floor_heat)

    def test_get_raised_floor_heat(self):
        A_noOp_floor = 18.580608
        G_space = 0
        h_surface = 0
        terrain = "Flat or Open Countryside"
        Coeff = 1
        self.wtstep["t_outside"] = 280  # Fake Temp Value
        #self.wtstep["ground_temperature_K"] = 280  # Fake Temp Value
        floor_heat = self.heat.get_raised_floor_heat(self.surface6, self.wtstep, G_space, A_noOp_floor, self.temp_record, self.space1, self.spaces_dict, h_surface, terrain, Coeff, self.areaDict, self.areaWinDict)
        self.assertEqual(floor_heat, -5.492465, 'floor heat for surface 6: %s ' % floor_heat)  #Getting -40.221503 with G_space = 0, will need updating for model 1

    def test_get_ground_heat(self):
        A_noOp_floor = 18.580608
        G_space = 0
        Coeff = 1
        ground_heat = self.heat.get_ground_heat(self.surface6, self.wtstep, G_space, A_noOp_floor, self.temp_record, self.space1, self.spaces_dict, Coeff, self.areaDict, self.areaWinDict)
        self.assertEqual(ground_heat, -3.720495, 'ground heat for surface 6: %s ' % ground_heat)  #Getting -38.264154 with G_space = 0, will need updating for model 1


