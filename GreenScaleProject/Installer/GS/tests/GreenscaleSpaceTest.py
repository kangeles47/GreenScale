#-------------------------------------------------------------------------------
# Name:        GreenscaleSpaceTest.py
# Purpose:     Green Scale Tool UnitTests (GS EE space level test)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
import unittest
import os
from objects.GreenscaleSpace import GreenscaleSpace
from GreenScaleV1 import GreenScaleV1
from gbXML import gbXML
from objects.Area import Area


class GreenscaleSpaceTest(unittest.TestCase):
    # Again, resulsts test the function of the code, and not the actual values until the DB has proper material values

    def setUp(self):
        self.gbxml = gbXML(os.path.join(os.path.dirname(__file__), 'input/Single_model.xml'))
        #self.gbxml = gbXML(os.path.join(os.path.dirname(__file__), 'input/Two_Room_One_Floor_Model.xml'))

        area = Area()
        area.createAreaDictionary()
        area.createWinAreaDictionary()
        self.areaWinDict = area.getWinDictionary()
        self.areaDict = area.getDictionary()

        #self.db = GreenScaleV1(os.path.join(os.path.dirname(__file__), '..\objects'))
        self.db = os.path.join(os.path.dirname(__file__), '..\objects')

        #self.db.db_file = 'GreenScaleDBcsv.csv'
        self.EEspace = GreenscaleSpace()
        self.duplicates = list()  # This is going to have to be optimized for large buildings with many surfaces

        # Get the first surface to check:
        spaces = self.gbxml.get_spaces()
        # Space 1 info, surface "su-8" is [7] and is the interior shared wall here
        self.space1 = spaces[0]
        surfaces = spaces[0].surfaces
        self.surface1 = surfaces[0]  # Ext. Wall with window
        self.surface2 = surfaces[1]  # Ext. Wall no openings
        self.surface3 = surfaces[2]  # Ext. Wall with window
        self.surface4 = surfaces[3]  # Ext. Wall with Door
        self.surface5 = surfaces[4]  # Roof
        self.surface6 = surfaces[5]  # Floor


    def test_calculate_surfaceEE(self):
        assembly = dict()
        assembly_descript = dict()
        spacecalc = self.EEspace.calculate_spaceEE(self.db, self.space1, self.duplicates, assembly, assembly_descript, self.areaDict, self.areaWinDict)
        self.assertEqual(spacecalc, [92302689.648048, 25752.450411], 'Space 1 EE:  %s ' % spacecalc)

        self.assertEqual(self.surface1.obj_type, "ExteriorWall", 'Space 1 Type:  %s ' % spacecalc)
        self.assertEqual(self.surface2.obj_type, "ExteriorWall", 'Space 1 Type:  %s ' % spacecalc)
        self.assertEqual(self.surface3.obj_type, "ExteriorWall", 'Space 1 Type:  %s ' % spacecalc)
        self.assertEqual(self.surface4.obj_type, "ExteriorWall", 'Space 1 Type:  %s ' % spacecalc)
        self.assertEqual(self.surface5.obj_type, "Roof", 'Space 1 Type:  %s ' % spacecalc)
        self.assertEqual(self.surface6.obj_type, "InteriorFloor", 'Space 1 Type:  %s ' % spacecalc)






