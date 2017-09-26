#-------------------------------------------------------------------------------
# Name:        shadowTest.py
# Purpose:     Green Scale Tool UnitTests (shadow test)
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
from objects.Shadow import Shadow
from Weather import Weather


class transmittedSolarTest(unittest.TestCase):

    def setUp(self):
        self.gbxml = gbXML(os.path.join(os.path.dirname(__file__), 'input/Single_model.xml'))

        # Get the first surface to check:
        spaces = self.gbxml.get_spaces()
        self.shadow_record = self.gbxml.shadow_record
        self.shade_surf_list = self.gbxml.get_shades()
        self.surfaces_dict = self.gbxml.surfaces_dict
        self.ns = ( len(self.shade_surf_list) + len(self.shadow_record) )
        #space_boundaries = list()
        #space_boundaries = spaces[0].surfaces
        surfaces = spaces[0].surfaces
        self.surface1 = surfaces[0]

        self.shade = Shadow()

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


    def test_shadowsSection(self):
        # for this hour use one of:
        #alt = -0.714277  ,  az = 1.535298
        #alt = -0.511189  ,  az = 1.694248
        azi_sun_rad = 1.535298
        tilt_sun_rad = -0.714277
        Ashadow_no_win, Ashadow_win = self.shade.shadowsSection(self.surface1, azi_sun_rad, tilt_sun_rad, self.ns, self.shadow_record, self.shade_surf_list, self.surfaces_dict)
        self.assertEqual(Ashadow_no_win, 0, 'Ashadow_no_win: %s ' % Ashadow_no_win)
        self.assertEqual(Ashadow_win, 0, 'Ashadow_win: %s ' % Ashadow_win)

