#-------------------------------------------------------------------------------
# Name:        Weather.py
# Purpose:     Green Scale Tool Weather Module (sets up weather dictionary from epw file)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
from datetime import datetime
from dircache import listdir
import os
import math
import logging

input_dir = os.path.join(os.path.dirname(__file__), 'tests', 'input')

class Weather():
    # Used in temperature(undergroundWall) and heatCalc(getGroundHeat) and heatCalc(getFloorHeat)
    # This value is going to be set in the code as (T_space-2) - An adjustment from Na's version 3
    #ground_temperature_K = 18 + 273

    # Line 66 is translating the .epw array data indexed from 1-24 for hours, for example, to a 0-23 indexing.
    # The indexing beginning from 0 is the format that the datetime module requires for "hours" only, rest start at 1.
    # Therefore, start_date and end_date are entered for a whole day will be hour = 0 to hour = 23 in the tests
    # The weather files use a different year for each month's data in the file....so currently has to ignore the year
    start = 0
    end = 0

    # Weather
    # Basically a dictionnary of dictionaries representing each timesteps
    # The key is the date of the timestep
    weather = dict()

    def __init__(self, location, start, end):
        """
        Initializes the weather
        """
        # Look for an input file that contains the location
##        weather_file = None
##        for f in listdir(input_dir):
##            if location in f:
##                weather_file = f
##                break
##
##        # If we dont have it, raise an error
##        if not weather_file:
##            raise("No weather file for this location")
##
##        # Open it and create the weather
##        f = open(os.path.join(input_dir,weather_file),"r")

        f = open(location,"r")

        line = f.readline()
        line_count = 0
        line_split = line.split(',')
        # Get only the data in the first line to know the Latitude, Longtitude, & Time_Meridian
        lat = float(line_split[6]) * (math.pi/180)
        longitude = float(line_split[7])
        time_meridian = float(line_split[8])

        while 1:
            # Read the current line
            line = f.readline()
            if not line:
                break

            line_count += 1

            # Only start reading at the 9th line
            # Before that just Metadata
            if line_count < 8:
                continue

            # Split the line (Delimiter is ,)
            line_split = line.split(',')

            # First retrieve the date
            # Need to use version with the year=1997 to pass the Weather Test Cases, this forces the year changes to be overlooked
            # Emmonak issue: Re-added the TMY3 fiel type for this location. Original Emmonak file from Matlab had indexing issue so may be version 2 file type
            t_step_date = datetime(year=1997, month=int(line_split[1]), day=int(line_split[2]), hour=(int(line_split[3]) - 1))

            # Test compare to our start and end date
            if t_step_date < start:
                continue
            elif t_step_date > end:
                break

            # We are in the range, get the other info
            conversion = math.pi/180
            sigma = 5.67e-8
            info = dict()
            info["wind_speed_dir"] = float(line_split[20])
            info["wind_speed"] = float(line_split[21])
            info["t_sky"] = round((float(line_split[12])/sigma)**.25,4)
            info["t_outside"] = float(line_split[6]) + 273
            info["az_sun"] = float(self.calc_azimuth(t_step_date.month, t_step_date.day, t_step_date.hour, lat, longitude, time_meridian ))
            info["alt_sun"] = float(self.hour_angle(t_step_date.month, t_step_date.day, t_step_date.hour, lat, longitude, time_meridian ))
            #print "azimuth ", info["az_sun"]
            info["I_dn"] = int(line_split[14])
            info["I_df"] = int(line_split[15])
            # Add it to the dict
            self.weather[t_step_date] = info

    def get_weather_step(self,tstep):
        return self.weather[tstep]

    def calc_azimuth(self, j, day, hour, lat, longitude, time_meridian):
        # Declination angle, Altitude angle, Azimuth angle (0~2*pi, clockwise)
        if j == 1:
            j = day
        elif j == 2:
            j = day + 31
        elif j == 3:
            j = day + 59
        elif j == 4:
            j = day + 90
        elif j == 5:
            j = day + 120
        elif j == 6:
            j = day + 151
        elif j == 7:
            j = day + 181
        elif j == 8:
            j = day + 212
        elif j == 9:
            j = day + 243
        elif j == 10:
            j = day + 273
        elif j == 11:
            j = day + 304
        else:
            j = day + 334
        # Calculate the hour angle.  j is the number of the day in the calendar year
        # Degrees:
        B = 360*(j-81)/364
        B = B*(math.pi/180)
        ET = ( 0.165*math.sin(B) )-( 0.126*math.cos(B) )-( 0.025*math.sin(B) )

        # store the solar hour angle
        solar_hour_angle = (math.pi/180) * ( (15*(12-((hour+1)+ET))) + ((time_meridian*15) - longitude) )
        #print "solar_hour_angle ", solar_hour_angle
        # store the information of the declination angle of each day. all angles use units of rad (-pi/2,pi/2)
        declination_angle = (-23.45) * math.cos((2*math.pi*(j+10))/365) * (math.pi/180)
        #print "declination_angle ",declination_angle
        # store the altitude angle of each hour  (-pi/2,pi/2)
        hr_altitude_angle = math.asin(( math.sin(declination_angle)*math.sin(lat)) + (math.cos(declination_angle)*math.cos(lat)*math.cos(solar_hour_angle)) )
        # azimuth angle   (0, 2pi) from north clockwise direction
        #print "hr_altitude_angle", hr_altitude_angle
        azimuth_angle = math.acos( (math.sin(declination_angle)-math.sin(hr_altitude_angle)*math.sin(lat))/(math.cos(hr_altitude_angle)*math.cos(lat)) )

        if solar_hour_angle < 0:
        # The azimuth angle is greater than 180 degrees when the hour angle, h, is positive(negative in this way ...since I am taking hour angle in the opposite way) (afternoon)--"Na"
            azimuth = (2*math.pi) - azimuth_angle
        else:
            azimuth = azimuth_angle

        return round(azimuth,6)

    def hour_angle(self, j, day, hour, lat, longitude, time_meridian):
        # Declination angle, Altitude angle, Azimuth angle (0~2*pi, clockwise)
        if j == 1:
            j = day
        elif j == 2:
            j = day + 31
        elif j == 3:
            j = day + 59
        elif j == 4:
            j = day + 90
        elif j == 5:
            j = day + 120
        elif j == 6:
            j = day + 151
        elif j == 7:
            j = day + 181
        elif j == 8:
            j = day + 212
        elif j == 9:
            j = day + 243
        elif j == 10:
            j = day + 273
        elif j == 11:
            j = day + 304
        else:
            j = day + 334
        # Calculate the hour angle.  j is the number of the day in the calendar year
        # Degrees:
        B = 360*(j-81)/364
        B = B*(math.pi/180)
        ET = ( 0.165*math.sin(B) )-( 0.126*math.cos(B) )-( 0.025*math.sin(B) )

        # store the solar hour angle
        solar_hour_angle = (math.pi/180) * ( (15*(12-((hour+1)+ET))) + ((time_meridian*15) - longitude) )
        #print "solar_hour_angle ", solar_hour_angle
        # store the information of the declination angle of each day. all angles use units of rad (-pi/2,pi/2)
        declination_angle = (-23.45) * math.cos((2*math.pi*(j+10))/365) * (math.pi/180)
        #print "declination_angle ",declination_angle
        # store the altitude angle of each hour  (-pi/2,pi/2)
        hr_altitude_angle = math.asin(( math.sin(declination_angle)*math.sin(lat)) + (math.cos(declination_angle)*math.cos(lat)*math.cos(solar_hour_angle)) )

        return round(hr_altitude_angle,6)

