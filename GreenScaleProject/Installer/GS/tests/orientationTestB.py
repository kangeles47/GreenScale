#-------------------------------------------------------------------------------
# Name:        orientationTestA.py
# Purpose:     Green Scale Tool UnitTests (TM orientation test A: Single Room Facing North)
#
# Author:      Holly Tina Ferguson
#
# Created:     08/04/2014
# Copyright:   (c) Holly Tina Ferguson 2014
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
from datetime import datetime
import os
import unittest
from ModelV1 import ModelV1
from objects.Area import Area
from GSUtility import GSUtility


class OrientationA_Test(unittest.TestCase):
    def setUp(self):
        self.model = ModelV1()
        self.model.location = 'Washington'
        self.model.gbxml = os.path.join(os.path.dirname(__file__), 'input/OrientationTestModel_A.xml')

        area = Area()
        area.createAreaDictionary()
        area.createWinAreaDictionary()
        self.areaWinDict = area.getWinDictionary()
        self.areaDict = area.getDictionary()

        U = GSUtility()
        devflag = '1'
        U.setDevFlag(devflag)

        self.model.Q_total = 0
        # Set desired thermal capacitance multiplier, 0.45 for example
        self.model.Coeff = 1
        # Set 0 to ignore shadow factors, set 1 if you do want to include calculations from shadows
        self.model.ShadowsFlag = 0  # 1 means calculate shadows, 0 means ignore shadows
        self.model.terrain = "Flat or Open Countryside"      # User Input Terrain Type
        self.model.timestep = 1

        # Need to use version with the year=1997 to pass the Weather Test Cases
        #self.model.start_date = datetime(year=1997, month=1, day=1, hour=3)
        #self.model.end_date = datetime(year=1997, month=1, day=1, hour=4)
        self.model.start_date = datetime(year=1997, month=1, day=1, hour=10)
        self.model.end_date = datetime(year=1997, month=1, day=1, hour=11)
        self.model.run()

        spaces = self.model.gbxml.get_spaces()
        self.space1 = spaces[0]
        surfaces = spaces[0].surfaces
        self.surface6 = surfaces[5]
        self.surface5 = surfaces[4]
        self.surface4 = surfaces[3]
        self.surface3 = surfaces[2]
        self.surface2 = surfaces[1]
        self.surface1 = surfaces[0]

        self.temp_record = self.model.gbxml.temp_record
        self.spaces_dict = self.model.gbxml.spaces_dict
        self.shgc_dictionary = self.model.gbxml.shgc_dictionary
        self.shadow_record = self.model.gbxml.shadow_record
        self.surfaces_dict = self.model.gbxml.surfaces_dict
        self.shade_surface_total = self.model.gbxml.shade_surface_total
        self.shade_surf_list = self.model.gbxml.get_shades()


    def test_space_Q_hour_W(self):
        su1 = self.surface1.azimuth
        self.assertEqual(su1, 0, 'azimuth of su1 is: %s ' % su1)

        su2 = self.surface2.azimuth
        self.assertEqual(su2, 90, 'azimuth of su2 is: %s ' % su2)

        su3 = self.surface3.azimuth
        self.assertEqual(su3, 180, 'azimuth of su3 is: %s ' % su3)

        su4 = self.surface4.azimuth
        self.assertEqual(su4, 270, 'azimuth of su4 is: %s ' % su4)

        su5 = self.surface5.azimuth
        self.assertEqual(su5, 0, 'azimuth of su5 is: %s ' % su5)

        su6 = self.surface6.azimuth
        self.assertEqual(su6, 0, 'azimuth of su6 is: %s ' % su6)


        #Coeff = 1
        #terrain = "Flat or Open Countryside"
        #A = 0
        #timestep = 1
        #one_room = self.model.space_Q_hour_W(self.spaces_dict, self.shgc_dictionary, self.temp_record, Coeff, self.shadow_record, self.shade_surf_list, self.surfaces_dict, A, terrain, timestep, self.areaDict, self.areaWinDict)
        #one_room = 1
        #self.assertEqual(one_room, 1, 'heatflux for one_room model is: %s ' % one_room)  # Getting 1 for single model until compare with BEAM





