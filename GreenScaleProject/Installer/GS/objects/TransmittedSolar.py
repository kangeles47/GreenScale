#-------------------------------------------------------------------------------
# Name:        TransmittedSolar.py
# Purpose:     Green Scale Tool TM Transmitted Solar Module (handles transmittance through a surface)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
import math
from objects.BaseElement import BaseElement
from objects.Area import Area
import numpy
import scipy
from GSUtility import GSUtility
from scipy.interpolate import interp1d
import logging

class TransmittedSolar(BaseElement):

    #surface = Surface()

    def get_transmitted_solar(self, weather, surface, AreaShadowOnlyWin, areaWinDict):
        conversion = math.pi/180
        tilt = surface.tilt * conversion
        transmitted_win = 0
        azimuth_sun = weather["az_sun"]
        #if azimuth_sun < 0:  # This was only part of matlab version 2 and 3 but not currently version 4
            #azimuth_sun += (2*math.pi)
        azimuth_surface = surface.azimuth * conversion
        az_d = math.fabs(azimuth_sun - azimuth_surface)

        # Incidence = acos(sin(Alt_sun)*cos(tilt)+cos(az_d)*cos(Alt_sun)*sin(tilt));
        alt_sun = weather["alt_sun"]
        incidence = math.acos( math.sin(alt_sun)*math.cos(tilt) + math.cos(az_d)*math.cos(alt_sun)*math.sin(tilt) )
        #print incidence
        check = math.cos(incidence)
        # Incidence_angle=sin(Alt_sun)*cos(tilt)+cos(az_d)*cos(Alt_sun)*sin(tilt);
        #incidence_angle = (math.sin(alt_sun)*math.cos(tilt)) + (math.cos(az_d)*math.cos(alt_sun)*math.sin(tilt))
        #angle = (math.fabs(incidence_angle)) / (math.pi/180)
        #print "incidence_angle: ", angle
        # But according to above, needs to be of weather+1 ???
        Is = self.get_is_surface(surface, tilt, incidence, az_d, alt_sun, weather)

        # If there is an opening here, the U-value will need to be adjusted:
        # If the opening is a window, there is transmitted energy
        for opening in surface.openings:
            if opening.obj_type == "OperableWindow" or opening.obj_type == "FixedWindow" or opening.obj_type == "OperableSkylight":
                # Takes the surface number and opening number in that surface
                shgc = 1
                #area = Area()
                #A_this_window = area.surfaceArea(opening.ocps, surface.azimuth, surface.tilt, surface)
                A_this_window = areaWinDict[opening.obj_id]
                #A_this_window = opening.height * opening.width * 0.3048 * 0.3048
                A_this_opening = A_this_window - AreaShadowOnlyWin
                # From 0 to upper limit of math.cos(math.pi/2)
                if 0 < check < 0.999624216859:
                    # Used to be using the shgc_dictionary set up in 3gbxml.py
                    #incidence = 80*math.pi/180
                    #shgc = self.get_shgc_opening(angle, shgc_dictionary)  # before version 3 y is decsending, x is ascending
                    #   (0, 0.698,          0.873,          1.047,          1.222,          1.396         )
                    x = (0, 40*math.pi/180, 50*math.pi/180, 60*math.pi/180, 70*math.pi/180, 80*math.pi/180, 90*math.pi/180)
                    #y = (0.42, 0.67, 0.78, 0.82, 0.84, 0.86, 0.90)
                    y = (0.86, 0.84, 0.82, 0.78, 0.67, 0.42, 0)
                    f = scipy.interpolate.interp1d(x, y, kind='cubic')  #, bounds_error='false', fill_value=0.86
                    shgc = f(abs(incidence))

                else:
                    shgc = 1
                #print shgc
                #shgc = 1

                transmitted = A_this_opening * shgc * Is
                #print A_this_opening
                # The summation of every opening on that surface added to the transmitted_win variable
                transmitted_win += transmitted
        #print transmitted_win
        return transmitted_win, Is

    def get_is_surface(self, surface, tilt, incidence, az_d, alt_sun, weather):
        Is = 0
        I_dn = weather["I_dn"]  # 0
        I_df = weather["I_df"]  # 0
        # The following comments are a note from the Matlab model:
        #        if cos(Incidence)> -0.2
        #            Y = 0.55+0.437*cos(Incidence)+0.313*(cos(Incidence))^2;
        #        else
        #            Y= 0.45;
        y = 1  # This will probably be replaced with the above if/else statements
        c = 0.118
        rho = 0.2
        #Ig = I_dn*(c + math.sin(alt_sun))*rho*(1 - math.cos(tilt))/2

        # Roof is different from walls - cases for Roof, RaisedFloor, and Other
        if surface.obj_type == "Roof":
            if tilt == 0:
                Is = I_dn*math.fabs(math.cos(incidence)) + I_df*(1 + math.cos(tilt))/2
            else:
                # else tilt > 0
                if az_d < math.pi/2 or az_d > 3*math.pi/2:
                    # Means this is toward the sun
                    Is = I_dn*math.fabs(math.cos(incidence)) + I_df*(1 + math.cos(tilt))/2
                else:
                    # Else is standing against the sun
                    Is = I_df*(1 + math.cos(tilt))/2
        elif surface.obj_type == "RaisedFloor":
            if az_d < math.pi/2 or az_d > 3*math.pi/2:
                # Means this is toward the sun
                Is = I_dn*abs(math.cos(incidence))+I_df*(1+math.cos(tilt))/2/y
            else:
                # Else is standing against the sun
                Is = I_df*(1+math.cos(tilt))/2/y
        else:
            # It is a normal wall surface toward the sun
            if az_d < math.pi/2 or az_d > 3*math.pi/2:
                Is = I_dn*abs(math.cos(incidence))+I_df*(1+math.cos(tilt))/2/y
            # It is a normal wall surface against the sun
            else:
                Is = I_df*(1+math.cos(tilt))/2/y

        return Is

    #def get_shgc_opening(self, incidence_angle, shgc_dictionary):
        # This was changed to a matching of a tuple in the dictionary "hgcs_dictionary" created in gbXML.py
        # Find the closest value to compare in the dictionary tuple values: 0,40,50,60,70,80

        # gives floating point answer, but if there are only 6 answers, a switch case may be simpler with less errors
        # options = [0, 40, 50, 60, 70, 80]
        # round(float(incidence_angle), -1)  # This was one found way to round to the nearest 10
        # This leaves the same window for each value except 0, will need to check if first should be 35.5 OR 20.0

        # 0 = 0, 40*pi/180 = 0.6981, 50 = 0.8727, 60 = 1.0472, 70 = 1.2217, 80 = 1.3963

        #if incidence_angle < 35.5:
        #    closest_sia = 0
        #elif incidence_angle >= 35 and incidence_angle < 45:
        #    closest_sia = 40
        #elif incidence_angle >= 45 and incidence_angle < 55:
        #    closest_sia = 50
        #elif incidence_angle >= 55 and incidence_angle < 65:
        #    closest_sia = 60
        #elif incidence_angle >= 65 and incidence_angle < 75:
        #    closest_sia = 70
        #elif incidence_angle >= 75:  # Does it follow to leave this out?  "and incidence_angle < 85.5"
        #    closest_sia = 80
        #else:
        #    closest_sia = 0  # giving it the smallest angle and thus largest-default heat-gain-coefficient for now

        #this_shgc = None
        #this_shgc = shgc_dictionary[closest_sia][1]
        #return this_shgc



