#-------------------------------------------------------------------------------
# Name:        GreenscaleEETest.py
# Purpose:     Green Scale Tool UnitTests (GS EE material level test)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
import unittest
import os
from gbXML import gbXML
from objects.GreenscaleEE import GreenscaleEE
#from GreenScaleV1 import GreenScaleV1
from objects.Area import Area


class GreenscaleEETest(unittest.TestCase):
    # Again, results test the function of the code, and not the actual values until the DB has proper material values

    def setUp(self):
        #self.model = GreenScaleV1()
        #self.gbxml = os.path.join(os.path.dirname(__file__), 'input/EDIT One Room Flat Roof with Materials.xml')
        self.gbxml = gbXML(os.path.join(os.path.dirname(__file__), 'input/Single_model.xml'))
        #self.gbxml = gbXML(os.path.join(os.path.dirname(__file__), 'input/Two_Room_One_Floor_Model.xml'))
        #self.gbxml = gbXML(os.path.join(os.path.dirname(__file__), 'input/Four_Room_Two_Floors_Model.xml'))
        #self.gbxml = gbXML(os.path.join(os.path.dirname(__file__), 'input/Vet_Center_V2.xml'))

        #self.db = GreenScaleV1(os.path.join(os.path.dirname(__file__), '..\objects'))
        self.db = os.path.join(os.path.dirname(__file__), '..\objects')

        #self.db.db_file = 'GreenScaleDBcsv.csv'
        self.EEtest = GreenscaleEE()

        # Get the first surface to check:
        spaces = self.gbxml.get_spaces()

        # This is for the Single_model.xml:
        # Space 1 info, surface "su-8" is [7] and is the interior shared wall here
        space1 = spaces[0]
        surfaces = spaces[0].surfaces
        self.surface1 = surfaces[0]  # Ext. Wall with window
        self.surface2 = surfaces[1]  # Ext. Wall no openings
        self.surface3 = surfaces[2]  # Ext. Wall with window
        self.surface4 = surfaces[3]  # Ext. Wall with Door
        self.surface5 = surfaces[4]  # Roof
        self.surface6 = surfaces[5]  # Floor

        area = Area()
        #print "test"
        self.areaWinDict = area.getWinDictionary
        self.areaDict = area.getDictionary


    def test_calculate_EE_dict(self):
        # Test with a door construction
        key = "MDOOR"
        this_material_area = 19.999999 # One door at 19.999999 sq. ft. in this surface
        h_surface = 10
        EE_withOpenings = self.EEtest.calculate_EE_dict(self.db, self.surface4, key, this_material_area, h_surface)
        self.assertEqual(EE_withOpenings, [801035.152794, 223.488808], 'Surface with Door surface4 EE:  - %s ' % EE_withOpenings)

        # Test with a window
        key = "GSP4R"
        h_surface = 10
        this_material_area = 12  # One window at 12 sq. ft. in this surface
        EE_withOpenings = self.EEtest.calculate_EE_dict(self.db, self.surface3, key, this_material_area, h_surface)
        self.assertEqual(EE_withOpenings, [155155.915648, 43.2885], 'Surface with Window surface3 EE:  - %s ' % EE_withOpenings)


    def test_calculate_EE(self):

        # The EE total calculated from 4 materials of surface 2:
        #EE_total:  2361711017.53
        #EE_total:   204946419.74
        #EE_total:   140873717.45
        #EE_total:   104973413.66
        #Total Surface Sum: 2,812,504,568
        h_surface = 10

        this_material_area = 110.625
        EE = self.EEtest.calculate_EE(self.db, self.surface2, this_material_area, h_surface)
        self.assertEqual(EE, [13367883.466804, 3729.639487], 'Total EE for surface2: - %s ' % EE)

        this_material_area = 200.000  # Roof
        lookup_EE_material = self.EEtest.calculate_EE(self.db, self.surface5, this_material_area, h_surface)
        self.assertEqual(lookup_EE_material, [8481391.017892, 2366.308094], 'Total EE for surface5: - %s ' % lookup_EE_material)

        this_material_area = 200.000  # Floor
        lookup_EE_material = self.EEtest.calculate_EE(self.db, self.surface6, this_material_area, h_surface)
        self.assertEqual(lookup_EE_material, [7819594.411886, 2181.666841], 'Total EE for surface6: - %s ' % lookup_EE_material)


    def test_lookup_EE_material(self):
        material_to_lookup = '1/8 in Pilkington single glazing'
        lookup_EE_material = self.EEtest.lookup_EE_material(self.db, material_to_lookup)
        #[18.5 MJ = BTUs, 2500kg/m^3, 0.125"]  ==>  [7953.15(18.5*429.9), 40046.15(2500*16.01846), 0.01041667(0.125/12)]
        self.assertEqual(lookup_EE_material, [7953.15, 156.0699, 0.010416666666666666], 'Expected: 1/8 in Pilkington single glazing with EE parts list - %s ' % lookup_EE_material)

        material_to_lookup = 'Brick, Common: 8"'
        lookup_EE_material = self.EEtest.lookup_EE_material(self.db, material_to_lookup)
        self.assertEqual(lookup_EE_material[0], 1289.77, 'Expected: Brick, Common: 8" with EE=1289.77 - %s ' % lookup_EE_material)

        material_to_lookup = 'Structure, Wood Joist/Rafter Layer: 11 1/2"'
        lookup_EE_material = self.EEtest.lookup_EE_material(self.db, material_to_lookup)
        self.assertEqual(lookup_EE_material[0], 3663.5, 'Structure, Wood Joist/Rafter Layer: 11 1/2" with EE=3663.5 - %s ' % lookup_EE_material)

        material_to_lookup = 'Gypsum Wall Board: 1/2"'
        lookup_EE_material = self.EEtest.lookup_EE_material(self.db, material_to_lookup)
        self.assertEqual(lookup_EE_material[0], 1292.48, 'Gypsum Wall Board: 1/2" with EE=1292.48 - %s ' % lookup_EE_material)

        material_to_lookup = 'Plywood, Sheathing: 3/4"'
        lookup_EE_material = self.EEtest.lookup_EE_material(self.db, material_to_lookup)
        self.assertEqual(lookup_EE_material[0], 6448.8, 'Plywood, Sheathing: 3/4" with EE=6448.8 - %s ' % lookup_EE_material)

        material_to_lookup = 'Rigid insulation: 2"'
        lookup_EE_material = self.EEtest.lookup_EE_material(self.db, material_to_lookup)
        self.assertEqual(lookup_EE_material[0], 30171, 'Rigid insulation: 2" with EE=30171 - %s ' % lookup_EE_material)

        material_to_lookup = 'Softwood, Lumber: 3 1/2"'
        lookup_EE_material = self.EEtest.lookup_EE_material(self.db, material_to_lookup)
        self.assertEqual(lookup_EE_material[0], 3663.5, 'Soft wood, Lumber: 3 1/2" with EE=3663.5 - %s ' % lookup_EE_material)

        material_to_lookup = 'Metal surface'
        lookup_EE_material = self.EEtest.lookup_EE_material(self.db, material_to_lookup)
        self.assertEqual(lookup_EE_material[0], 10747.5, 'Metal surface with EE=10747.5 - %s ' % lookup_EE_material)

        #These 3 may be using the old .csv lookup elements
        #material_to_lookup = '5/8 in plywood'
        #lookup_EE_material = self.EEtest.lookup_EE_material(self.db, material_to_lookup)
        #self.assertEqual(lookup_EE_material[0], 6448.8, '5/8 in plywood with EE=6448.8 - %s ' % lookup_EE_material)

        #material_to_lookup = 'Structure, Wood Joist/Rafter Layer: 5 1/2"'
        #lookup_EE_material = self.EEtest.lookup_EE_material(self.db, material_to_lookup)
        #self.assertEqual(lookup_EE_material[0], 3663.5, 'Structure, Wood Joist/Rafter Layer: 5 1/2 with EE=3663.5 - %s ' % lookup_EE_material)

        #material_to_lookup = 'Oak Flooring: 1 1/2"'
        #lookup_EE_material = self.EEtest.lookup_EE_material(self.db, material_to_lookup)
        #self.assertEqual(lookup_EE_material[0], 3353.22, "Oak Flooring: 1' with EE=3353.22 - %s " % lookup_EE_material)

if __name__ == '__main__':
    unittest.main()

