#-------------------------------------------------------------------------------
# Name:        mainTest.py
# Purpose:     Green Scale Tool UnitTests (main TM test)
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
from ModelV1 import ModelV1
from objects.Area import Area
from GSUtility import GSUtility

class ModelTest(unittest.TestCase):
    def setUp(self):
        self.model = ModelV1()
        self.model.location = 'Washington'
        self.model.gbxml = os.path.join(os.path.dirname(__file__), 'input/Single_model.xml')
        #self.model.gbxml = os.path.join(os.path.dirname(__file__), 'input/Two_Room_One_Floor_Model.xml')
        #self.model.gbxml = os.path.join(os.path.dirname(__file__), 'input/Two_Room_One_Floor_Model.xml')
        #self.model.gbxml = os.path.join(os.path.dirname(__file__), 'input/Four_Room_Two_Floors_Model.xml')

        area = Area()
        area.createAreaDictionary()
        area.createWinAreaDictionary()
        self.areaWinDict = area.getWinDictionary()
        self.areaDict = area.getDictionary()

        U = GSUtility()
        devflag = '1'
        U.setDevFlag(devflag)

        self.model.Q_total = 0
        self.Q_total = self.model.Q_total
        # Set desired thermal capacitance multiplier, 0.45 for example
        self.model.Coeff = 1
        self.Coeff = self.model.Coeff
        # Set 0 to ignore shadow factors, set 1 if you do want to include calculations from shadows
        self.model.ShadowsFlag = 0  # 1 means calculate shadows, 0 means ignore shadows
        self.ShadowsFlag = self.model.ShadowsFlag
        self.model.terrain = "Flat or Open Countryside"      # User Input Terrain Type
        self.terrain = self.model.terrain
        self.model.timestep = 1
        self.timestep = self.model.timestep

        # Need to use version with the year=1997 to pass the Weather Test Cases
        #self.model.start_date = datetime(year=1997, month=1, day=1, hour=3)
        #self.model.end_date = datetime(year=1997, month=1, day=1, hour=4)

        #self.model.start_date = datetime(year=1997, month=1, day=1, hour=0)
        #self.model.end_date = datetime(year=1997, month=1, day=1, hour=23)
        self.model.start_date = datetime(year=1997, month=1, day=1, hour=0)
        self.model.end_date = datetime(year=1997, month=12, day=31, hour=23)
        self.model.run()

        spaces = self.model.gbxml.get_spaces()
        self.space1 = spaces[0]
        self.temp_record = self.model.gbxml.temp_record
        self.spaces_dict = self.model.gbxml.spaces_dict
        self.shgc_dictionary = self.model.gbxml.shgc_dictionary
        self.shadow_record = self.model.gbxml.shadow_record
        self.surfaces_dict = self.model.gbxml.surfaces_dict
        self.shade_surface_total = self.model.gbxml.shade_surface_total
        self.shade_surf_list = self.model.gbxml.get_shades()


    def test_space_Q_hour_W(self):
        # Model One Room
        #Coeff = 1
        #terrain = "Flat or Open Countryside"
        A = 0
        #timestep = 1
        one_room = self.model.space_Q_hour_W(self.spaces_dict, self.shgc_dictionary, self.temp_record, self.Coeff, self.shadow_record, self.shade_surf_list, self.surfaces_dict, A, self.terrain, self.timestep, self.areaDict, self.areaWinDict)
        one_room = round(one_room, 6) #Before was 3320.66609954
        self.assertEqual(one_room, 3320.6661, 'heatflux for one_room model is: %s ' % one_room)


