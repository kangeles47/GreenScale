#-------------------------------------------------------------------------------
# Name:        transmittedSolarTest.py
# Purpose:     Green Scale Tool UnitTests (transmitted solar test)
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
from objects.TransmittedSolar import TransmittedSolar
from objects.Area import Area
from Weather import Weather


class transmittedSolarTest(unittest.TestCase):
    # For now, this test is giving solar transmittance to be 0, which makes sense for 3-4am in the USA.
    # Therefore, I am assuming these are calculating correctly at this time.

    def setUp(self):
        self.gbxml = gbXML(os.path.join(os.path.dirname(__file__), 'input/Single_model.xml'))

        # Get the first surface to check:
        spaces = self.gbxml.get_spaces()
        #space_boundaries = list()
        #space_boundaries = spaces[0].surfaces
        surfaces = spaces[0].surfaces
        self.surface1 = surfaces[0]

        self.solar = TransmittedSolar()

        area = Area()
        #print "test"
        self.areaWinDict = area.getWinDictionary

        # Create a fake weather
        self.weather = Weather('Washington', datetime(year=1997, month=1, day=1, hour=3), datetime(year=1997, month=1, day=1, hour=4))

        # And a timestep
        self.tstep2 = datetime(year=1997,month=1,day=1,hour=4)
        # get the weather at the tstep
        self.wtstep2 = self.weather.get_weather_step(self.tstep2)

        # And another timestep
        self.tstep = datetime(year=1997,month=1,day=1,hour=3)
        # get the weather at the tstep
        self.wtstep = self.weather.get_weather_step(self.tstep)


    def test_get_transmitted_solar(self):
        AreaShadowOnlyWin = 0
        transmitted_win = self.solar.get_transmitted_solar(self.wtstep, self.surface1, AreaShadowOnlyWin, self.areaWinDict)
        self.assertEqual(transmitted_win, 0, 'transmitted_win is currently: %s ' % transmitted_win)


    #def test_get_transmitted_solar_Is(self):  # No longer in the module
    #    Is_calc = self.solar.get_transmitted_solar_Is(self.wtstep, self.surface1)
    #    self.assertEqual(Is_calc, 0, 'transmitted_win is currently: %s ' % Is_calc)


    def test_get_is_surface(self):
        # Assuming for this example that the solar heat gain for the windows in this surface is 0 from 3-4am...true
        tilt = self.surface1.tilt
        incidence = 1.74842841126
        az_d = 4.41808653158
        alt_sun = self.wtstep["alt_sun"]

        Is = self.solar.get_is_surface(self.surface1, tilt, incidence, az_d, alt_sun, self.wtstep)
        self.assertEqual(Is, 0, 'get_Is_surface is currently: %s ' % Is)

    """
    def test_get_shgc_opening(self):  # No longer in the module
        incidence_angle = 25.8
        function_result = self.solar.get_shgc_opening(incidence_angle, self.shgc_dictionary)
        self.assertEqual(function_result, 0.86, 'function_result with IAngle = 25.8 - %s ' % function_result)

        incidence_angle = 37.2
        function_result = self.solar.get_shgc_opening(incidence_angle, self.shgc_dictionary)
        self.assertEqual(function_result, 0.84, 'function_result with IAngle = 37.2 - %s ' % function_result)

        incidence_angle = 48.4
        function_result = self.solar.get_shgc_opening(incidence_angle, self.shgc_dictionary)
        self.assertEqual(function_result, 0.82, 'function_result with IAngle = 48.4 - %s ' % function_result)

        incidence_angle = 61.0
        function_result = self.solar.get_shgc_opening(incidence_angle, self.shgc_dictionary)
        self.assertEqual(function_result, 0.78, 'function_result with IAngle = 61.0 - %s ' % function_result)

        incidence_angle = 74.9
        function_result = self.solar.get_shgc_opening(incidence_angle, self.shgc_dictionary)
        self.assertEqual(function_result, 0.67, 'function_result with IAngle = 74.9 - %s ' % function_result)

        incidence_angle = 109.8
        function_result = self.solar.get_shgc_opening(incidence_angle, self.shgc_dictionary)
        self.assertEqual(function_result, 0.42, 'function_result with IAngle = 109.8 - %s ' % function_result)
    """





