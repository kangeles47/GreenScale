#-------------------------------------------------------------------------------
# Name:        temperatureTest.py
# Purpose:     Green Scale Tool UnitTests (temperature test)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
import unittest
from datetime import datetime
import os
from gbXML import gbXML
from objects.Temperature import Temperature
from Weather import Weather
from objects.Area import Area


class transmittedSolarTest(unittest.TestCase):
    # For now, this test is giving solar transmittance to be 0, which makes sense for 3-4am in the USA.
    # Therefore, I am assuming these are calculating correctly at this time.

    def setUp(self):
        #self.gbxml = gbXML(os.path.join(os.path.dirname(__file__), 'input/Single_model.xml'))
        self.gbxml = gbXML(os.path.join(os.path.dirname(__file__), 'input/Two_Room_One_Floor_Model.xml'))
        self.temp = Temperature()
        self.shgc_dictionary = self.gbxml.shgc_dictionary
        self.temp_record = self.gbxml.temp_record
        self.spaces_dict = self.gbxml.spaces_dict
        self.shadow_record = self.gbxml.shadow_record
        self.shade_surf_list = self.gbxml.get_shades()
        self.surfaces_dict = self.gbxml.surfaces_dict
        # Get the first surface to check:
        spaces = self.gbxml.get_spaces()

        # Space 1 info, surface "su-8" is [7] and is the interior shared wall here
        space1 = spaces[0]
        surfaces_inspace1 = spaces[0].surfaces
        self.surface1_in_space1 = surfaces_inspace1[0]
        self.surface5_in_space1 = surfaces_inspace1[4]
        self.surface6_in_space1 = surfaces_inspace1[5]

        self.surface8_in_space1 = surfaces_inspace1[7]

        # Space 2 info, surface "su-8" is [7] and is the interior shared wall here
        #space2 = spaces[1]
        #surfaces_inspace2 = spaces[1].surfaces
        #self.surface8_in_space2 = surfaces_inspace1[7]

        # Create a fake weather
        self.weather = Weather('Washington', datetime(year=1997, month=1, day=1, hour=3), datetime(year=1997, month=1, day=1, hour=4))

        area = Area()
        #print "test"
        self.areaWinDict = area.getWinDictionary

        # And a timestep
        self.tstep2 = datetime(year=1997,month=1,day=1,hour=4)
        # get the weather at the tstep
        self.wtstep2 = self.weather.get_weather_step(self.tstep2)

        # And another timestep
        self.tstep = datetime(year=1997,month=1,day=1,hour=3)
        # get the weather at the tstep
        self.wtstep = self.weather.get_weather_step(self.tstep)

    def test_interior_wall(self):
        T_space = 293
        surface = self.surface8_in_space1
        T1 = self.wtstep["t_outside"]
        A = 12.77375
        A_noOp = 12.77375
        C = 317068.2     #set when next model is tested
        R3 = 0

        #Q_flux = 1
        Q_flux = self.temp.interior_wall(surface, A, C, R3, self.spaces_dict, T_space, self.temp_record)
        self.assertEqual(Q_flux, 1, 'Q_flux is currently: %s ' % Q_flux)

    def test_exterior_wall(self):
        T_space = 293
        surface = self.surface6_in_space1
        T1 = self.wtstep["t_outside"]
        A = 20.554798
        A_noOp = 19.439962
        A_noWin = 19.439962
        hc = 17.65859
        C = 270863.311519
        R3 = 1/0.729191
        ShadowsFlag = 0
        ns = ( len(self.shade_surf_list) + len(self.shadow_record) )

        Q_flux = self.temp.exterior_wall(surface, hc, T1, A, A_noWin, self.wtstep, R3, C, T_space, self.temp_record, ShadowsFlag, ns, self.shadow_record, self.shade_surf_list, self.surfaces_dict, self.areaWinDict)
        self.assertEqual(Q_flux, -7.230236, 'Q_flux is currently: %s ' % Q_flux)

    def test_roof(self):
        T_space = 293
        surface = self.surface5_in_space1
        T1 = self.wtstep["t_outside"]
        A = 18.580608
        A_noOp = 18.580608
        A_noWin = 18.580608
        hc = 15.24232
        C = 36873.89882
        R3 = 1/0.084111
        ShadowsFlag = 0
        ns = ( len(self.shade_surf_list) + len(self.shadow_record) )

        Q_flux = self.temp.roof(surface, hc, T1, A, A_noWin, self.wtstep, R3, C, A_noOp, T_space, self.temp_record, ShadowsFlag, ns, self.shadow_record, self.shade_surf_list, self.surfaces_dict, self.areaWinDict)
        self.assertEqual(Q_flux, -10.487022, 'Q_flux is currently: %s ' % Q_flux)

    def test_underground_wall(self):
        Q_flux = 1
        # Q_flux = self.temp.underground_wall(surface, hc_external, T1, A, A_noWin, weather, R3, C, A_noOp, shgc_dictionary)
        self.assertEqual(Q_flux, 1, 'Q_flux is currently: %s ' % Q_flux)




