#-------------------------------------------------------------------------------
# Name:        Confidence.py
# Purpose:     Green Scale Tool EE Confidence Module (handles confidence factor calculations)
#              NOTE: Module sufficient only for user-declared confidence until real confidence values can be used
#
# Author:      Holly Tina Ferguson
#
# Created:     11/11/2014
# Copyright:   (c) Holly Tina Ferguson 2014
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
from objects.BaseElement import BaseElement
import math
import os
from GSUtility import GSUtility


class Confidence(BaseElement):

    # Material Name Key and Tuple Value of (confidence-factor, loss-factor)
    M_ConfidenceTuplesDict = dict()
    # Material Name Key and Single Value of (EE in whole building of that material)
    M_DictEEPercents = dict()
    #A_ConfidenceTuplesDict = dict()
    #A_DictEEPercents = dict()
    # Construction ID Key and Volume Percent of that whole assembly throughout the building
    ConsVol = dict()

    def calculate_confidence_values(self, MaterialVolumeDict, MaterialDict):
        # Dictionary #1:
        # Dictionary MaterialVolumeDict[] = total volume and EE by material building-wide
        # Data per [Material Name Key] = (building_total_volume, confidence, building_total_EE, percentVol=0)
        #
        # Dictionary #2:
        # Dictionary MaterialDict[] = building-wide Assembly totals of values by construction ID
        # Data per [Construction ID Key] = (list of lists of materials that make up this assembly type called "m[X_materials_in_assembly]")
        #   "m[X_materials_in_assembly]" = (material_name, total_volume_per_assembly_type, confidence, total_EE_within_assembly_type) x (X materials in assembly)
        # example: MaterialDict[cons_id_2] = [((m1 data list), (m2 data list), (m3 data list), etc)]

        #print "MaterialVolumeDict:"
        #for item in MaterialVolumeDict:
        #    print item, MaterialVolumeDict[item]
        #print "MaterialDict:"
        #for item in MaterialDict:
        #    print item, MaterialDict[item]

        # Create Confidence Data and EE Data for two new dictionaries by MATERIAL for whole building--------------------
        building_volume = 0
        building_ee = 0
        for entry in MaterialVolumeDict:
            building_volume = MaterialVolumeDict[entry][0] + building_volume
            building_ee = MaterialVolumeDict[entry][2] + building_ee
        print "total_building_volume in cubic feet: ", building_volume
        print "total_building_ee for confidence #s: ", building_ee
        CF_sum_total = 0
        LF_sum_total = 0
        for entry in MaterialVolumeDict:
            v = MaterialVolumeDict[entry][0]
            c = (MaterialVolumeDict[entry][1]/100)
            e = MaterialVolumeDict[entry][2]
            if building_volume > 0:
                cp = v / building_volume
            else:
                cp = 0
            if building_ee > 0:
                ep = e / building_ee
            else:
                ep = 0
            MaterialVolumeDict[entry] = (v, c, e, cp)
            CF = c * cp
            CF_sum_total = CF + CF_sum_total
            LF = cp - CF
            LF_sum_total = LF + LF_sum_total
            self.M_ConfidenceTuplesDict[entry] = (c, CF, LF, cp)
            self.M_DictEEPercents[entry] = ep

        # Print Confidence Data and EE Data from two new dictionaries by MATERIAL for whole building--------------------
        total_materials = len(self.M_ConfidenceTuplesDict)
        print "total_materials: ", total_materials
        print "Confidence and EE Data from M_ConfidenceTuplesDict and M_DictEEPercents by material for whole building-----------------"
        print "list_key per ID below: material, c, CF, LF, volume_%, ee_%"
        summ = 0
        summ2 = 0
        num_materials = 1
        for item in self.M_ConfidenceTuplesDict:
            summ = self.M_ConfidenceTuplesDict[item][3] + summ
            summ2 = self.M_DictEEPercents[item] + summ2
            # Material names have been stripped of commas for print out
            dict_entry1 = item.replace(",", "")
            printkey = str("mtl" + str(num_materials) + "," + dict_entry1 + "," + str(self.M_ConfidenceTuplesDict[item][0]) + "," + str(self.M_ConfidenceTuplesDict[item][1]) + "," + str(self.M_ConfidenceTuplesDict[item][2]) + "," + str(self.M_ConfidenceTuplesDict[item][3]) + "," + str(self.M_DictEEPercents[item]))
            print printkey
            num_materials += 1
        print "CF_sum_total: ", CF_sum_total
        print "LF_sum_total: ", LF_sum_total
        print "Sum of volume percents by material is 1?", summ
        print "Sum of ee percents by material is 1?", summ2



        # Create Confidence Data and EE Data for two new dictionaries by ASSEMBLY for whole building--------------------
        # (material_name, total_volume_per_assembly_type, confidence, total_EE_within_assembly_type)
        building_tee = 0
        for entry in MaterialDict:
            totalVolInCons = 0
            totalEEInCons = 0
            for a_m in MaterialDict[entry]:
                building_tee = a_m[3] + building_tee
                totalVolInCons = a_m[1] + totalVolInCons
                totalEEInCons = a_m[3] + totalEEInCons
            # Now have ConsVol[] dictionary of cons ID and volume in building that that cons takes up
            self.ConsVol[entry] = (totalVolInCons, totalEEInCons)
        sum_pv_cons = 0
        sum_pe_cons = 0
        for cons in self.ConsVol:
            v = self.ConsVol[cons][0]
            e = self.ConsVol[cons][1]
            if building_volume > 0:
                pv_cons = v / building_volume
            else:
                pv_cons = 0
            if building_tee > 0:
                pe_cons = e / building_tee
            else:
                pe_cons = 0
            sum_pv_cons = pv_cons + sum_pv_cons
            sum_pe_cons = pe_cons + sum_pe_cons
            self.ConsVol[cons] = (v, pv_cons, e, pe_cons)
            print str(str(cons) + "," + str(pv_cons) + "," + str(pe_cons))
        print "Sum of Cons Vol Percents is 1? ", sum_pv_cons
        print "Sum of Cons EE Percents is 1? ", sum_pe_cons

        # Print Confidence Data and EE Data from two new dictionaries by ASSEMBLY for whole building--------------------
        print "Confidence and EE Data from A_ConfidenceTuplesDict and A_DictEEPercents by ASSEMBLY for whole building-----------------"
        CF_sum_totalb = 0
        LF_sum_totalb = 0
        print "total_MaterialDict_ee: ", building_tee
        for entry in MaterialDict:
            CF_sum_totalc = 0
            LF_sum_totalc = 0
            for a_m in MaterialDict[entry]:
                m = a_m[0]
                v = a_m[1]
                c = (a_m[2]/100)
                e = a_m[3]
                # Per this material in this one construction type compared to whole building
                if building_tee > 0:
                    epb = e / building_tee
                else:
                    epb = 0
                if building_volume > 0:
                    cpb = v / building_volume
                else:
                    cpb = 0
                CFb = c * cpb
                CF_sum_totalb = CFb + CF_sum_totalb
                LFb = cpb - CFb
                LF_sum_totalb = LFb + LF_sum_totalb
                # Per this material in this one construction type compared to assembly type
                if self.ConsVol[entry][2] > 0:
                    epc = e / self.ConsVol[entry][2]
                else:
                    epc = 0
                if self.ConsVol[entry][0] > 0:
                    cpc = v / self.ConsVol[entry][0]
                else:
                    cpc = 0
                CFc = c * cpc
                CF_sum_totalc = CFc + CF_sum_totalc
                LFc = cpc - CFc
                LF_sum_totalc = LFc + LF_sum_totalc
                # New MaterialDict[] Entry
                MaterialDict[entry] = (m, v, c, e, epb, cpb, CFb, LFb, epc, cpc, CFc, LFc)

            print str("CF_sum_total_at_assembly_level" + "," + str(entry) + "," + str(CF_sum_totalc))
            print str("LF_sum_total_at_assembly_level" + "," + str(entry) + "," + str(LF_sum_totalc))
        print str("CF_sum_total_at_building_level_from_assembly_calc: " + str(CF_sum_totalb))
        print str("LF_sum_total_at_building_level_from_assembly_calc: " + str(LF_sum_totalb))

        # Additional prints for Assemblies can be added as needed

        return 0
