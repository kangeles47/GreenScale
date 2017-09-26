#-------------------------------------------------------------------------------
# Name:        ModelV1.py
# Purpose:     Green Scale Tool Main Thermal Model Module (starts thermal model)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
import datetime
from Weather import Weather
from gbXML import gbXML
from objects.Space import Space
from objects.Area import Area
from objects.newShadowCalc import Shadow
import os
import time
from GSUtility import GSUtility
import logging
#logging.getLogger('TM_V1').addHandler(logging.NullHandler())
#TM_coder = logging.getLogger('TMcoder_V1')
TM_user = logging.getLogger('TMuser_V1')


class ModelV1():
    # Input parameters
    location = ""
    gbxml = ""
    start_date = ""
    end_date = ""

    # Internal parameters
    weather = ""
    spaces = list()
    spaces_dict = dict()
    shgc_dictionary = dict()
    shadow_record = dict()     # Set of exterior surfaces on which to test shading
    temp_record = dict()
    shade_devices = list()     # Total number of exterior surfaces on which to test shading
    surfaces_dict = dict()
    materials = list()
    # Output parameters
    Q_total = ''
    # Set desired thermal capacitance multiplier, 0.45 for example
    Coeff = ''
    # Set 0 to ignore shadow factors, set 1 if you do want to include calculations from shadows
    ShadowsFlag = ''  # 1 means calculate shadows, 0 means ignore shadows
    terrain = ''      # User Input Terrain Type
    timestep = ''     # Will be set at 1 for every hour every day or 2 for every hour every other day
    opengl_stat = 0

    def run(self):
        """
        Main run function
        """
        #c1 = time.clock()  # Start Time

        # First, Initializes the weather
        U = GSUtility()
        U.devPrint("Reaching Weather function...")
        #print "Reaching Weather function..."
        self.weather = Weather(self.location,self.start_date,self.end_date)

        # Then the GBXML
        self.gbxml = gbXML(self.gbxml)
        U.devPrint("Reaching gbXML function...")
        #print "Reaching gbXML function..."

        # Retrieve the spaces
        self.spaces = self.gbxml.get_spaces()

        # Get the dictionary of space Ids to pass values to other files instead of all the space data
        # This dictionary should contain an entry for each space and its space Id tag
        self.spaces_dict = self.gbxml.spaces_dict
        self.shgc_dictionary = self.gbxml.shgc_dictionary
        self.temp_record = self.gbxml.temp_record
        self.shadow_record = self.gbxml.shadow_record           # Record of exterior surfaces to be used in Shadow.py
        #self.shadesurf_check = self.gbxml.shade_surface_total  # Will be ns for Shadow.py
        self.shade_devices = self.gbxml.get_shades()            # Shade surfaces defined separate from other surfaces
        self.surfaces_dict = self.gbxml.surfaces_dict

        area_flag = 0  # 0 = has not yet recorded usable surface areas for the model, will set to = 1 after first hour
        area = Area()
        areaDict = area.getDictionary()
        areaWinDict = area.getWinDictionary()
        #print "length: ", len(areaWinDict)
        #for item in areaWinDict:
        #    x = areaWinDict[item]
        #    print "area dictionary item: ", item, x

        # For each spaces, calculate the Q_hour_W
        #for space in self.spaces:
        #c3 = time.clock()  # Start Time Without SetUp
        self.space_Q_hour_W(self.spaces_dict, self.shgc_dictionary, self.temp_record, self.Coeff, self.shadow_record, self.shade_devices, self.surfaces_dict, area_flag, self.terrain, self.timestep, areaDict, areaWinDict)
        #c4 = time.clock()  # Complete Time Without SetUp
        #nosetup = c4-c3
        #TM_coder.info("Time Without SetUp: %s Seconds" % (nosetup))
        #print "Time Without SetUp: ", c4-c3

        #c2 = time.clock()  # Complete Time
        #withsetup = c2-c1
        #TM_coder.info("Total time: %s Seconds" % (withsetup))
        #print "Total time: ", c2-c1

        return None

    def space_Q_hour_W(self, spaces_dict, shgc_dictionary, temp_record, Coeff, shadow_record, shade_surf_list, surfaces_dict, A, terrain, timestep, areaDict, areaWinDict):
        """
        Process the hourly Q in Watts for a given space
        Collecting the data as it is returned from the space, n turn the surfaces
        """
        U = GSUtility()
        U.devPrint("Reaching space_Q_hour_W function...")
        #print "Reaching space_Q_hour_W function..."
        #TM_coder.info("   Entering function: space_Q_hour_W()")
        shadowRatios = dict()
        shadowRatioIndex = dict()


        temp_date = self.start_date
        Q_total = 0
        building_Q_hour_W = list()
        counter = 1
        x = 0
        #hour_marker = 1
        monthTotal = 0
        monthTotalforYear_timeStepis2 = 0
        previous = 0
        len_weather = 0       # Hour counter for time_step = 2
        len_weather_year = 0  # To adjust the Q_Total if the timestep used is = 2
        day_counter = 1

        leftover_flux_monthNotCompleted = 0

        Q_hour_J = list()

        #for item in temp_record:
        #    # Set each space G_space value to be 0 initially
        #    print "item: ", item, temp_record[item]
        #    #print G_space_record[space.obj_id], space.obj_id

        G_space_record = dict()
        for space in self.spaces:
            # Set each space G_space value to be 0 initially
            G_space_record[space.obj_id] = 0
            #print G_space_record[space.obj_id], space.obj_id

        missing_surfaces = dict()

        ns = ( len(shade_surf_list) + len(shadow_record) )
        #print ns
        # Add all shade surfaces to surface dictionary
        #for surf in shade_surf_list:
        #    surfaces_dict[surf.obj_id] = surf
        # Go from the start date to the end date by incrementing one
        # For each of the hours, calculate the sum of the Qs for every surface of the space.
        while temp_date <= self.end_date:
            len_weather_year += 1
            len_weather += 1
            space_hour_q = 0
            building_flux_thisHour = 0
            #print "temp_date: ", temp_date

            # Slice the weather to calculate for this hour slice
            # Comes from the tstep variable in Weather.py
            weather_slice = self.weather.get_weather_step(temp_date)
            #print "slice: ", weather_slice

            if (self.ShadowsFlag == 1):
                shadows = Shadow()
                shadowRatios, shadowRatioIndex = shadows.shadowMain(self.opengl_stat, self.surfaces_dict, weather_slice)
            #print "returning here", shadowRatioIndex

            # This is the Q_space from Na's file
            # For each spaces, calculate the Q_hour_W
            current_space = Space()
            for space in self.spaces:
                #if A == 0:
                    # If it is the first surface of the space, label the space ID in the log file:
                    #l = str(space.obj_id)
                    #TM_user.info("Space ID,%s,," % (l))
                #TM_user.info(" ")
                #l = str(space.obj_id)
                #TM_user.info("Space ID,%s,," % (l))

                space_hour_q = current_space.calculate_space_heatflux(space, weather_slice, spaces_dict, temp_record, Coeff, self.ShadowsFlag, ns, shadow_record, shade_surf_list, surfaces_dict, A, missing_surfaces, terrain, G_space_record, areaDict, areaWinDict, shadowRatios, shadowRatioIndex)
                #TM_coder.info("Space-Hour-Flux is: %s Watts" % (space_hour_q))
                # Calculations in Watts
                building_flux_thisHour = building_flux_thisHour + space_hour_q
                # Get overall total for entire timestamp---instead of adding up list later
                #print space_hour_q
                Q_total = Q_total + space_hour_q
                leftover_flux_monthNotCompleted += space_hour_q
                #print Q_total
                #A = 1  #Taking this out because you want data for all spaces each hour, not just the first space each loop...
            A = 0

            #TM_coder.info("Total Bldg Flux this Hour is: %s Watts" % (Q_total))

            #ctest = time.clock()  # Test Clock since these operations are not part of the program function
##            if (temp_date.month == 1 and temp_date.day == 29 and temp_date.hour == 23):
##                U.devPrint(temp_date)
            # Get a month total
            # Every hour for every day:
            if timestep == 1:
                if temp_date.day == 1 and temp_date.hour == 0 and temp_date.month == 2:
                    monthTotal = monthTotal/1000
                    Jan = (int(temp_date.month) - 1)
                    TM_user.info("Total Bldg Flux for Month %s is: %s KWatts" % (Jan, monthTotal))
                    thing1s = str(monthTotal)
                    #U.devPrint(thing1s)
                    print "M1,", monthTotal
                if temp_date.day == 1 and temp_date.hour == 0:
                    if temp_date.month >= 3:
                        monthTotal = monthTotal/1000
                        monNum = (int(temp_date.month) - 1)
                        TM_user.info("Total Bldg Flux for Month %s is: %s KWatts" % (monNum, monthTotal))
                        thing1s = str(monthTotal)
                        #U.devPrint(thing1s)
                        mx = str("M" + str(monNum) + ",")
                        print mx, monthTotal
                    monthTotal = building_flux_thisHour
                else:
                    monthTotal += building_flux_thisHour
                if temp_date.day == 31 and temp_date.hour == 23 and temp_date.month == 12:
                    monthTotal = monthTotal/1000
                    TM_user.info("Total Bldg Flux for Month %s is: %s KWatts" % (temp_date.month, monthTotal))
                    thing1s = str(monthTotal)
                    #U.devPrint(thing1s)
                    print "M12,", monthTotal
            # Every hour for every other day
            if timestep == 2:
                if temp_date.month == 2 and temp_date.hour == 0:  # Every other day will hit this condition when January finishes
                    if temp_date.day == 1 or temp_date.day == 2:  # Every other day will hit only one or the other of these two days
                        if day_counter % 2 == 0:
                            monthTotal *= 2
                        else:
                            monthTotal = monthTotal * ((2*day_counter) - 1) / (day_counter)
                            #monthTotal = monthTotal - (monthTotal*(1/day_counter))
                        monthTotal = monthTotal/1000
                        Jan = (int(temp_date.month) - 1)
                        TM_user.info("Total Bldg Flux for Month %s is: %s KWatts" % (Jan, monthTotal))
                        thing1s = str(monthTotal)
                        #U.devPrint(thing1s)
                        print "M1,", monthTotal
                        #print monthTotal  #, 2*day_counter
                        monthTotalforYear_timeStepis2 += monthTotal
                        day_counter = 1
                if temp_date.day == 1 or temp_date.day == 2:
                    if temp_date.hour == 0 and temp_date.month != 1:  # For other months aside from January
                        if temp_date.month >= 3:                      # Equal to 3 is for Feb, since 3 means the month - 1 total currently exists
                            if day_counter % 2 == 0:
                                monthTotal *= 2
                            else:
                                monthTotal = monthTotal * ((2*day_counter) - 1) / (day_counter)
                                #monthTotal = monthTotal - (monthTotal*(1/day_counter))
                            monthTotal = monthTotal/1000
                            monNum = (int(temp_date.month) - 1)
                            TM_user.info("Total Bldg Flux for Month %s is: %s KWatts" % (monNum, monthTotal))
                            thing1s = str(monthTotal)
                            #U.devPrint(thing1s)
                            mx = str("M" + str(monNum) + ",")
                            print mx, monthTotal
                            #print monthTotal  #, 2*day_counter
                            monthTotalforYear_timeStepis2 += monthTotal
                    monthTotal = building_flux_thisHour
                    len_weather = 0  # Re-Zero out the len_weather so that month totals have new hour count
                    day_counter = 1
                else:
                    monthTotal += building_flux_thisHour
                if temp_date.hour == 23 and temp_date.month == 12:
                    if temp_date.day == 31 or temp_date.day == 30:
                        if day_counter % 2 == 0:
                            monthTotal *= 2
                        else:
                            monthTotal = monthTotal * ((2*day_counter) - 1) / (day_counter)
                            #monthTotal = monthTotal - (monthTotal*(1/day_counter))
                        monthTotal = monthTotal/1000
                        TM_user.info("Total Bldg Flux for Month %s is: %s KWatts" % (temp_date.month, monthTotal))
                        thing1s = str(monthTotal)
                        #U.devPrint(thing1s)
                        print "M12,", monthTotal
                        #print monthTotal  #, 2*day_counter
                        monthTotalforYear_timeStepis2 += monthTotal
                if temp_date.hour < 23:
                    if temp_date.month == 1 and temp_date.day < 31:
                        pass

                    # Otherwise check if the hour is less than the final hour and day is less than final day of the month

            #c2test = time.clock()  # Test
            #x = x + (c2test-ctest)

            # Add total building heatflux for this hour to the list...to use for graphing later
            # ***Should this be appending the current total to have [34.543658, 68.487829] or leave as only for that hour [34.543658, 33.944171]???
            building_Q_hour_W.append(building_flux_thisHour)

            # Go to the next hour
            temp_date, day_counter = self.get_next_temp_date(temp_date, timestep, day_counter)
            #temp_date += datetime.timedelta(hours=1)

        TM_user.info("   ")
        for key in missing_surfaces:
            TM_user.info("Missing Type of Surface, Contact Developers: , %s, %s" %(key, missing_surfaces[key]))  # Record the Building's EE, EW by Assembly
        TM_user.info("   ")
        #print "last total: ", dayTotal    # Will need to put this back in................

        # Calculations in Joules and Related Output Checks
        # This first "if" commented here was using Na's original timestep every other day method...now printing my version that applies the formula each month
        # This by-month sum reaches an estimation that is not as close as Na's value to the every hour every day result, but used since by-month totals are desired.
        #if timestep == 2:
        #    if len_weather_year % 2 == 0:
        #        Q_total *= 2
        #    else:
        #        Q_total = Q_total * ((2*len_weather_year/24) - 1) / (len_weather_year/24)
        # Else Q_total equals the same as would have gotten from above so can use it as is
        #print "Q_total: ", Q_total      # Heatflux value is in Watts

        if timestep == 2:
            if monthTotalforYear_timeStepis2 == 0:
                # End of January is not yet reached
                Q_total = Q_total
                #Q_total = monthTotal
            else:
                Q_total = monthTotalforYear_timeStepis2 #added monthTotal
        thing1 = Q_total
        thing1s = str(thing1)
        thing1s = "Q_total: " + thing1s
        U.devPrint(thing1s)
        #U.devPrint("Q_total: ", Q_total)
        #print "Q_total: ", Q_total      # Heatflux value is in Watts


        Q_total_KWattsH = Q_total/1000  # Heatflux value is in KWatts*Hr
        thing1 = Q_total_KWattsH
        thing1s = str(thing1)
        thing1s = "Q_total_KWattsH: " + thing1s
        U.devPrint(thing1s)

        print "Total TM: ", Q_total_KWattsH
        #U.devPrint("Q_total_KWattsH: ", Q_total_KWattsH)
        #print "Q_total_KWattsH: ", Q_total_KWattsH

        J_total = Q_total * 3600        # Heatflux value is in Joules
        #print "J_total: ", J_total

        #TM_user.info("   ")
        TM_user.info("Total KWatts for Defined Time Span: %s" % (Q_total_KWattsH))
        TM_user.info("Total Joules for Defined Time Span: %s" % (J_total))

        return Q_total_KWattsH

    def get_next_temp_date(self, temp_date, timestep, day_counter):
        # Get the next temp_data considering ends of days and months.
        if timestep == 1:
            temp_date += datetime.timedelta(hours=1)
        if timestep == 2:
            if temp_date.hour == 23:
                temp_date += datetime.timedelta(days=1)
                temp_date += datetime.timedelta(hours=1)
                day_counter += 1
            else:
                temp_date += datetime.timedelta(hours=1)
            #print temp_date.day

        return temp_date, day_counter

