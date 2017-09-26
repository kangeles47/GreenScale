#-------------------------------------------------------------------------------
# Name:        gbxmlTest.py
# Purpose:     Green Scale Tool UnitTests (gbxml test)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
import os
import unittest
from gbXML import gbXML


class gbxmlTest(unittest.TestCase):
    def setUp(self):
        self.gbxml = gbXML(os.path.join(os.path.dirname(__file__), 'input/Single_model.xml'))


    def test_gbxml_get_spaces(self):
        # Get the spaces
        spaces = self.gbxml.get_spaces()

        # We should find only one space
        self.assertEqual(len(spaces), 1, "Find one space")
        self.assertEqual(spaces[0].obj_id, "sp-1-Room", "Correct space ID")

        # This space should have 6 surfaces
        self.assertEqual(len(spaces[0].surfaces), 6, "Space has 6 surfaces")


    def test_gbxml_get_surfaces(self):
        # Get the surfaces for the first space
        spaces = self.gbxml.get_spaces()
        #space_boundaries = list()
        space_boundaries = spaces[0].surfaces
        #surfaces = self.gbxml.get_surfaces(spaces, space_boundaries, "sp-1-Room")

        # We should find 6 surfaces
        #self.assertEqual(len(space_boundaries), 6, "Find 6 surfaces??? %s" % len(surfaces))
        #print "# of test surfaces", len(space_boundaries)
        #print "surface cps: ", space_boundaries[0].cps[3]

        #surfaces = self.gbxml.get_surfaces(spaces[0], space_boundaries, "sp-1-Room")

        self.assertEqual(space_boundaries[0].obj_id, "su-1", "Correct surface ID")
        self.assertEqual(space_boundaries[1].obj_id, "su-2", "Correct surface ID")
        self.assertEqual(space_boundaries[5].obj_id, "su-6", "Correct surface ID")

        self.assertEqual(space_boundaries[0].obj_type, "ExteriorWall", "Correct surface type")
        self.assertEqual(space_boundaries[5].obj_type, "InteriorFloor", "Correct surface type")

        self.assertEqual(space_boundaries[0].is_exterior(), True, "Is ExteriorWall exterior ?")
        self.assertEqual(space_boundaries[5].is_exterior(), False, "Is InteriorFloor exterior ?")

        self.assertEqual(space_boundaries[0].width, 20.0, "Surface width correct ?")
        self.assertEqual(space_boundaries[1].width, 10.0, "Surface width correct ?")
        self.assertEqual(space_boundaries[0].height, 11.0625, "Surface height correct ?")
        self.assertEqual(space_boundaries[1].height, 11.0625, "Surface height correct ?")

        self.assertEqual(space_boundaries[0].azimuth, 330, "Surface azimuth correct ?")
        self.assertEqual(space_boundaries[1].azimuth, 240, "Surface azimuth correct ?")

        self.assertEqual(space_boundaries[0].tilt, 90, "Surface Tilt correct ?")
        self.assertEqual(space_boundaries[4].tilt, 0, "Surface Tilt correct ?")

        # Points in the gbxml are set to metric in the gbXML.py file, so testing metric points here:
        self.assertEqual(space_boundaries[0].cps[3], (-1.8181941792, 6.2060654136, 0.0), "Surface 0 cartesian point %s" % str(space_boundaries[0].cps[3]))
        self.assertEqual(space_boundaries[1].cps[0], (-7.0974850176, 3.1580654136, 0.0), "Surface 1 cartesian point %s" % str(space_boundaries[1].cps[0]))
        self.assertEqual(space_boundaries[2].cps[0], (-5.5734850176, 0.5184199944, 0.0), "Surface 2 cartesian point %s" % str(space_boundaries[2].cps[0]))

        self.assertEqual(len(space_boundaries[0].openings), 1, "Openings in surface")

        for surface in space_boundaries:
            print "to get C surface from surfaces...: ", surface.construction[0].layer[0].C_Total
        #print space_boundaries[8]


    def test_gbxml_get_openings(self):
        # Get the openings for the first surface
        spaces = self.gbxml.get_spaces()
        #space_boundaries = list()
        #space_boundaries = spaces[0].surfaces
        surfaces = spaces[0].surfaces
        #openings = self.gbxml.get_openings(surfaces[0], surfaces[0])

        openings = surfaces[0].openings
        details = openings[0].material
        #for opening in openings:
        #    print "found a window: ", opening.obj_id_test

        self.assertEqual(openings[0].obj_id, "su-1-op-1", "Opening ID")
        self.assertEqual(openings[0].obj_type, "OperableWindow", "Opening type")
        self.assertEqual(openings[0].width, 3, "Opening width")
        self.assertEqual(openings[0].height, 4, "Opening height")

        #print "see if this gives the construction details: ", openings[0].material[0].obj_name, ".....", openings[0].material[0].u_value
        #print openings[8]








