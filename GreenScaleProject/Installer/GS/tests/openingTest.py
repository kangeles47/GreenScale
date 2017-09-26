#-------------------------------------------------------------------------------
# Name:        openingTest.py
# Purpose:     Green Scale Tool UnitTests (opening test)
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
from objects.Opening import Opening


class OpeningTest(unittest.TestCase):

    def setUp(self):
        gbxml = gbXML(os.path.join(os.path.dirname(__file__), 'input/Single_model.xml'))
        spaces = gbxml.get_spaces()
        surfaces = spaces[0].surfaces
        self.surface = Surface()
        self.open = Opening()

        self.surface1 = surfaces[0]
        self.opening1 = surfaces[0].openings[0]

        # Create a fake weather
        self.weather = Weather('Washington', datetime(year=1997,month=1,day=1,hour=3), datetime(year=1997,month=1,day=1,hour=4))

        # And a timestep
        self.tstep2 = datetime(year=1997,month=1,day=1,hour=4)
        # get the weather at the tstep
        self.wtstep2 = self.weather.get_weather_step(self.tstep2)

        # And another timestep
        self.tstep = datetime(year=1997,month=1,day=1,hour=3)
        # get the weather at the tstep
        self.wtstep = self.weather.get_weather_step(self.tstep)

    def test_opening_A(self):
        #self.assertEqual(self.open.get_A(),1.1148,"Opening 1 get A (expected 1.1148) - %s " % self.surface1.get_A())
        this_opening_area = self.open.get_A(self.opening1)
        self.assertEqual(this_opening_area, 1.1148, 'opening area test: %s ' % this_opening_area)
