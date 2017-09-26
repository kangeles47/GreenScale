#-------------------------------------------------------------------------------
# Name:        mainGreenScaleV1Test.py
# Purpose:     Green Scale Tool UnitTests (main EE test)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
import unittest
import os
from datetime import datetime
from objects.GreenscaleSpace import GreenscaleSpace
from GreenScaleV1 import GreenScaleV1
from gbXML import gbXML
from objects.Area import Area
from GSUtility import GSUtility


class GreenScaleV1Test(unittest.TestCase):
    # Again, resulsts test the function of the code, and not the actual values until the DB has proper material values

    def setUp(self):
        self.model = GreenScaleV1()
        self.model.gbxml = os.path.join(os.path.dirname(__file__), 'input/Single_model.xml')
        #self.model.gbxml = os.path.join(os.path.dirname(__file__), 'input/Two_Room_One_Floor_Model.xml')
        #self.model.gbxml = os.path.join(os.path.dirname(__file__), 'input/Four_Room_Two_Floors_Model.xml')
        #self.model.gbxml = os.path.join(os.path.dirname(__file__), 'input/Fall2013RLMVCRevit_v2_MarcValidation.xml')
        #self.model.gbxml = os.path.join(os.path.dirname(__file__), 'input/Avon.xml')
        #self.model.gbxml = os.path.join(os.path.dirname(__file__), 'input/L_ShapeFloor.xml')
        #self.model.gbxml = os.path.join(os.path.dirname(__file__), 'input/FourRoom_with_Zones.xml')
        #self.model.gbxml = os.path.join(os.path.dirname(__file__), 'input/FourRoomRoundColumn.xml')
        #self.model.gbxml = os.path.join(os.path.dirname(__file__), 'input/FourRoomSquareColumn.xml')

        self.model.input_dir = os.path.join(os.path.dirname(__file__), '..\objects')
        self.db = self.model.input_dir

        area = Area()
        area.createAreaDictionary()
        area.createWinAreaDictionary()
        self.areaWinDict = area.getWinDictionary()
        self.areaDict = area.getDictionary()

        U = GSUtility()
        devflag = '1'
        U.setDevFlag(devflag)

        # Get the surfaces in the space:
        self.model.run()
        spaces = self.model.gbxml.get_spaces()
        self.space1 = spaces[0]
        self.shade_surfaces = self.model.gbxml.get_shades()
        surfaces = spaces[0].surfaces

    def test_buildingEE(self):
        # One Room Model
        #area = Area()
        #area.createAreaDictionary()
        #area.createWinAreaDictionary()
        #global areaWinDict
        #areaWinDict = area.getWinDictionary
        #global areaDict

        #print "inTestcase ", len(self.shade_surfaces), self.areaDict
        ee, ew = self.model.buildingEE(self.db, self.shade_surfaces, self.areaDict, self.areaWinDict)

        self.assertEqual(ee, 92302689.648048, 'Space 1 EE:  %s ' % ee)
        self.assertEqual(ew, 25752.450411, 'Space 1 EW:  %s ' % ew)

        #  Two Room One Floor Model
        #  Su-8 is the shared wall that should not appear twice in duplicates[], this is true
        #ee, ew = self.model.buildingEE(self.db, self.shade_surfaces, self.areaDict, self.areaWinDict)
        #self.assertEqual(ee, 138246120.400036, 'Two Spaces EE:  %s ' % ee)
        #self.assertEqual(ew, 38570.667590000005, 'Two Spaces EW:  %s ' % ew)

        #  Four Room Two Floors Model
        #  Su-8, etc, are the shared walls that should not appear twice in duplicates[], this is true as well
        #ee, ew = self.model.buildingEE(self.db, self.shade_surfaces, self.areaDict, self.areaWinDict)
        #self.assertEqual(ee, 178593683.400733, 'Four Spaces EE:  %s ' % ee)
        #self.assertEqual(ew, 49827.637666999995, 'Four Spaces EW:  %s ' % ew)

        #  Fall2013RLMVCRevit_v2_MarcValidation
        #ee, ew = self.model.buildingEE(self.db, self.shade_surfaces, self.areaDict, self.areaWinDict)
        #self.assertEqual(ee, 2552509597.654998, 'Vet Center Spaces EE:  %s ' % ee)
        #self.assertEqual(ew, 712150.1777539998, 'Vet Center Spaces EW:  %s ' % ew)

        #  Avon
        #ee, ew = self.model.buildingEE(self.db, self.shade_surfaces, self.areaDict, self.areaWinDict)
        #self.assertEqual(ee, 2655029038.3667574, 'Vet Center Spaces EE:  %s ' % ee)
        #self.assertEqual(ew, 740753.1017069999, 'Vet Center Spaces EW:  %s ' % ew)

        #  L_ShapeFloor
        #ee, ew = self.model.buildingEE(self.db, self.shade_surfaces, self.areaDict, self.areaWinDict)
        #self.assertEqual(ee, 890860881.0526211, 'Vet Center Spaces EE:  %s ' % ee)
        #self.assertEqual(ew, 248550.18581599992, 'Vet Center Spaces EW:  %s ' % ew)

        #  FourRoom_with_Zones
        #ee, ew = self.model.buildingEE(self.db, self.shade_surfaces, self.areaDict, self.areaWinDict)
        #self.assertEqual(ee, 178593683.400733, 'Vet Center Spaces EE:  %s ' % ee)
        #self.assertEqual(ew, 49827.637666999995, 'Vet Center Spaces EW:  %s ' % ew)

        #  FourRoomRoundColumn
        #ee, ew = self.model.buildingEE(self.db, self.shade_surfaces, self.areaDict, self.areaWinDict)
        #self.assertEqual(ee, 180591163.98342, 'Vet Center Spaces EE:  %s ' % ee)
        #self.assertEqual(ew, 50384.934748, 'Vet Center Spaces EW:  %s ' % ew)

        #  FourRoomSquareColumn
        #ee, ew = self.model.buildingEE(self.db, self.shade_surfaces, self.areaDict, self.areaWinDict)
        #self.assertEqual(ee, 180736089.047848, 'Vet Center Spaces EE:  %s ' % ee)
        #self.assertEqual(ew, 50425.368836, 'Vet Center Spaces EW:  %s ' % ew)







