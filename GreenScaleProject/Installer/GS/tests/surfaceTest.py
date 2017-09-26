#-------------------------------------------------------------------------------
# Name:        surfaceTest.py
# Purpose:     Green Scale Tool UnitTests (surface test)
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
from objects.Area import Area


class SurfaceTest(unittest.TestCase):

    def setUp(self):
        gbxml = gbXML(os.path.join(os.path.dirname(__file__), 'input/Single_model.xml'))
        area = Area()
        area.createAreaDictionary()
        area.createWinAreaDictionary()
        self.areaWinDict = area.getWinDictionary()
        self.areaDict = area.getDictionary()

        spaces = gbxml.get_spaces()
        surfaces = spaces[0].surfaces
        self.surface = Surface()

        self.surface1 = surfaces[0]
        self.surface2 = surfaces[1]
        self.surface3 = surfaces[2]
        self.surface4 = surfaces[3]
        self.surface5 = surfaces[4]
        self.surface6 = surfaces[5]

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


    def test_get_hc_external(self):
        # These numbers are giving values that are different than Ben's tests, not sure why/where they came from...
        h_surface = 1.685925
        terrain = "Flat or Open Countryside"
        hc1 = self.surface.get_hc_external(self.wtstep, self.surface1, h_surface, terrain)
        self.assertEqual(hc1, 25.82063, 'get_hc is on surface 1: %s ' % hc1)
        #Ben's test: self.assertEqual(self.surface1.get_hc_external(self.wtstep),17.5617,"Surface 1")

        hc2 = self.surface.get_hc_external(self.wtstep, self.surface2, h_surface, terrain)
        self.assertEqual(hc2, 25.82063, 'get_hc is on surface 2: %s ' % hc2)
        #Ben's test: self.assertEqual(self.surface2.get_hc_external(self.wtstep),8.7809,"Surface 2")

        hc5 = self.surface.get_hc_external(self.wtstep, self.surface5, h_surface, terrain)
        self.assertEqual(hc5, 25.82063, 'get_hc is on surface 5: %s ' % hc5)
        #Ben's test: self.assertEqual(self.surface5.get_hc_external(self.wtstep),18.4740,"Surface 5")

        hc6 = self.surface.get_hc_external(self.wtstep, self.surface6, h_surface, terrain)
        self.assertEqual(hc6, 25.82063, 'get_hc is on surface 6: %s ' % hc6)


    def test_get_A(self):
        A = self.surface.get_A(self.surface1, self.areaDict, self.areaWinDict)
        A = round(A, 3)
        self.assertEqual(A, 20.555, 'Total area of surface 1: %s ' % A)
        A = self.surface.get_A(self.surface2, self.areaDict, self.areaWinDict)
        A = round(A, 3)
        self.assertEqual(A, 10.277, 'Total area of surface 2: %s ' % A)
        A = self.surface.get_A(self.surface3, self.areaDict, self.areaWinDict)
        A = round(A, 3)
        self.assertEqual(A, 20.555, 'Total area of surface 3: %s ' % A)
        A = self.surface.get_A(self.surface4, self.areaDict, self.areaWinDict)
        A = round(A, 3)
        self.assertEqual(A, 10.277, 'Total area of surface 4: %s ' % A)
        A = self.surface.get_A(self.surface5, self.areaDict, self.areaWinDict)
        A = round(A, 3)
        self.assertEqual(A, 18.581, 'Total area of surface 5: %s ' % A)
        A = self.surface.get_A(self.surface6, self.areaDict, self.areaWinDict)
        A = round(A, 3)
        self.assertEqual(A, 18.581, 'Total area of surface 6: %s ' % A)

    def test_get_A_noWin(self):
        A = self.surface.get_A_noWin(self.surface1, self.areaDict, self.areaWinDict)
        A = round(A, 3)
        self.assertEqual(A, 19.440, 'A_no_windows for surface 1: %s ' % A)
        A = self.surface.get_A_noWin(self.surface2, self.areaDict, self.areaWinDict)
        A = round(A, 3)
        self.assertEqual(A, 10.277, 'A_no_windows for surface 2: %s ' % A)
        A = self.surface.get_A_noWin(self.surface3, self.areaDict, self.areaWinDict)
        A = round(A, 3)
        self.assertEqual(A, 19.440, 'A_no_windows for surface 3: %s ' % A)
        A = self.surface.get_A_noWin(self.surface4, self.areaDict, self.areaWinDict)  # same as total area because doors are not counted here
        A = round(A, 3)
        self.assertEqual(A, 10.277, 'A_no_windows for surface 4: %s ' % A)
        A = self.surface.get_A_noWin(self.surface5, self.areaDict, self.areaWinDict)
        A = round(A, 3)
        self.assertEqual(A, 18.581, 'A_no_windows for surface 5: %s ' % A)
        A = self.surface.get_A_noWin(self.surface6, self.areaDict, self.areaWinDict)
        A = round(A, 3)
        self.assertEqual(A, 18.581, 'A_no_windows for surface 6: %s ' % A)

    def test_get_A_noOp(self):
        A = self.surface.get_A_noOp(self.surface1, self.areaDict, self.areaWinDict)
        A = round(A, 3)
        self.assertEqual(A, 19.440, 'A_no_openings for surface 1: %s ' % A)
        A = self.surface.get_A_noOp(self.surface2, self.areaDict, self.areaWinDict)
        A = round(A, 3)
        self.assertEqual(A, 10.277, 'A_no_openings for surface 2: %s ' % A)
        A = self.surface.get_A_noOp(self.surface3, self.areaDict, self.areaWinDict)
        A = round(A, 3)
        self.assertEqual(A, 19.440, 'A_no_openings for surface 3: %s ' % A)
        A = self.surface.get_A_noOp(self.surface4, self.areaDict, self.areaWinDict)  # same as total area because doors are not counted here
        A = round(A, 3)
        self.assertEqual(A, 8.419, 'A_no_openings for surface 4: %s ' % A)
        A = self.surface.get_A_noOp(self.surface5, self.areaDict, self.areaWinDict)
        A = round(A, 3)
        self.assertEqual(A, 18.581, 'A_no_openings for surface 5: %s ' % A)
        A = self.surface.get_A_noOp(self.surface6, self.areaDict, self.areaWinDict)
        A = round(A, 3)
        self.assertEqual(A, 18.581, 'A_no_openings for surface 6: %s ' % A)

    def test_get_C_surface(self):
        A_total = 20.554798
        A_noOp = 19.439962
        Coeff = 1
        C = self.surface.get_C_surface(A_total, A_noOp, self.surface1, Coeff, self.areaWinDict)
        # Currently calculating the effective C to be 270863.311519, check against Matlab output
        self.assertEqual(C, 270863.311519, 'C of surface 1: %s ' % C)

        A_total = 10.277399
        A_noOp = 8.419338
        Coeff = 1
        # Test surface door which does have a door
        C = self.surface.get_C_surface(A_total, A_noOp, self.surface4, Coeff, self.areaWinDict)
        # Currently calculating the effective C to be 270863.311519, check against Matlab output
        self.assertEqual(C, 242487.186765, 'C of surface 4: %s ' % C)

        A_total = 18.580608
        A_noOp = 18.580608
        Coeff = 1
        # Test surface door which does have a door
        C = self.surface.get_C_surface(A_total, A_noOp, self.surface5, Coeff, self.areaWinDict)
        # Currently calculating the effective C to be 270863.311519, check against Matlab output
        self.assertEqual(C, 36873.89882, 'C of surface 5: %s ' % C)

    def test_get_U_surface(self):
        A_noOp = 19.439962
        U = self.surface.get_U_surface(A_noOp, self.surface1)
        self.assertEqual(U, 0.386384, 'U of surface 1: %s ' % U)

        A_noOp = 18.580608
        U = self.surface.get_U_surface(A_noOp, self.surface5)
        self.assertEqual(U, 0.084111, 'U of surface 5: %s ' % U)

    def test_get_U_win(self):
        U = self.surface.get_U_win(self.surface1)
        self.assertEqual(U, 0.0, 'U of surface 1: %s ' % U)
        U = self.surface.get_U_win(self.surface2)
        self.assertEqual(U, 0, 'U of surface 2: %s ' % U)
        U = self.surface.get_U_win(self.surface3)
        self.assertEqual(U, 0.0, 'U of surface 3: %s ' % U)
        U = self.surface.get_U_win(self.surface4)
        self.assertEqual(U, 0, 'U of surface 4: %s ' % U)
        U = self.surface.get_U_win(self.surface5)
        self.assertEqual(U, 0, 'U of surface 5: %s ' % U)
        U = self.surface.get_U_win(self.surface6)
        self.assertEqual(U, 0, 'U of surface 6: %s ' % U)

    def test_get_U_opening(self):
        U = self.surface.get_U_opening(self.surface1)
        self.assertEqual(U, 0, 'U of surface 1: %s ' % U)

        U = self.surface.get_U_opening(self.surface2)
        self.assertEqual(U, 0, 'U of surface 2: %s ' % U)

        U = self.surface.get_U_opening(self.surface3)
        self.assertEqual(U, 0, 'U of surface 3: %s ' % U)

        U = self.surface.get_U_opening(self.surface4)
        self.assertEqual(U, 0.0, 'U of surface 4: %s ' % U)

        U = self.surface.get_U_opening(self.surface5)
        self.assertEqual(U, 0, 'U of surface 5: %s ' % U)

        U = self.surface.get_U_opening(self.surface6)
        self.assertEqual(U, 0, 'U of surface 6: %s ' % U)


    def test_get_U_surface_e(self):
        # Check all these against Matlab output
        A_total = 20.554798
        A_noOp = 19.439962
        # Test surface which does have a window
        U = self.surface.get_U_surface_e(A_total, A_noOp, self.surface1, self.areaWinDict)
        self.assertEqual(U, 0.729192, 'C of surface 1: %s ' % U)

        A_total = 10.277399
        A_noOp = 8.419338
        # Test surface which does have a door
        U = self.surface.get_U_surface_e(A_total, A_noOp, self.surface4, self.areaWinDict)
        self.assertEqual(U, 0.985835, 'C of surface 4: %s ' % U)

        A_total = 18.580608
        A_noOp = 18.580608
        U = self.surface.get_U_surface_e(A_total, A_noOp, self.surface5, self.areaWinDict)
        self.assertEqual(U, 0.084111, 'C of surface 5: %s ' % U)

        A_total = 18.580608
        A_noOp = 18.580608
        U = self.surface.get_U_surface_e(A_total, A_noOp, self.surface6, self.areaWinDict)
        self.assertEqual(U, 5.147638, 'C of surface 6: %s ' % U)

