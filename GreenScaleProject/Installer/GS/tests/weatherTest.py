#-------------------------------------------------------------------------------
# Name:        weatherTest.py
# Purpose:     Green Scale Tool UnitTests (weather test)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
from datetime import datetime
import unittest
from Weather import Weather

'''
class WeatherTest(unittest.TestCase):

    def setUp(self):
        # Rome 9-10 1987, Omsk 10-11 1999, Sapporo 10-11 1988, Sydney 12-13 1986, Mexico 12-13 1991, Lima 13-14 1985, Johannesurg 14-15 1986
        # Note: There seems to be an known issue with the test from Australia-may be the calulator used online to check or this code
        #start = datetime(year=1986,month=1,day=1,hour=14)
        #end = datetime(year=1986,month=1,day=1,hour=15)
        #self.weather = Weather("Johannesburg",start,end)
        #self.assertEqual(len(self.weather.weather),4)

        #Washington
        #start = datetime(year=1997,month=1,day=1,hour=7)
        #end = datetime(year=1997,month=1,day=1,hour=8)
        #self.weather = Weather("Washington",start,end)
        #self.assertEqual(len(self.weather.weather),4)

        start = datetime(year=1997,month=1,day=1,hour=3)
        end = datetime(year=1997,month=1,day=1,hour=4)
        self.weather = Weather("Washington",start,end)
        self.assertEqual(len(self.weather.weather),22)

    def test_weather_step(self):
        step =self.weather.get_weather_step(datetime(year=1997,month=1,day=1,hour=4))
        self.assertEqual(step["wind_speed_dir"],40,"Wind Speed dir (40 - %s)" % step["wind_speed_dir"])
        self.assertEqual(step["wind_speed"],3.1,"Wind Speed")
        self.assertEqual(step["t_sky"],264.6156,"T Sky temperature")
        self.assertEqual(step["t_outside"],272.4,"Outside temperature")
        self.assertEqual(step["az_sun"],1.5353,"Sun azimuth %s" % step["az_sun"] )
        #self.assertEqual(step["az_sun"],1.535039594490872,"Sun azimuth %s" % step["az_sun"] )

        step =self.weather.get_weather_step(datetime(year=1997,month=1,day=1,hour=3))
        self.assertEqual(step["wind_speed_dir"],30,"Wind Speed dir (30 - %s)" % step["wind_speed_dir"])
        self.assertEqual(step["wind_speed"],3.1,"Wind Speed")
        self.assertEqual(step["t_sky"],264.6156,"Sky temperature")
        self.assertEqual(step["t_outside"],272.4,"Outside temperature")
        self.assertEqual(step["az_sun"],1.3415,"Sun azimuth %s" % step["az_sun"] )
        #self.assertEqual(step["az_sun"],1.341124150866685,"Sun azimuth %s" % step["az_sun"] )


        #Johannesburg SA test
        #step =self.weather.get_weather_step(datetime(year=1986,month=1,day=1,hour=15))
        #self.assertEqual(step["az_sun"],5,"Sun azimuth %s" % step["az_sun"] )

        #Lima Peru test
        #step =self.weather.get_weather_step(datetime(year=1985,month=1,day=1,hour=14))
        #self.assertEqual(step["az_sun"],5,"Sun azimuth %s" % step["az_sun"] )

        #Mexico City test
        #step =self.weather.get_weather_step(datetime(year=1991,month=1,day=1,hour=13))
        #self.assertEqual(step["az_sun"],5,"Sun azimuth %s" % step["az_sun"] )

        #Sydney Australia test
        #step =self.weather.get_weather_step(datetime(year=1986,month=1,day=1,hour=12))
        #self.assertEqual(step["az_sun"],5,"Sun azimuth %s" % step["az_sun"] )

        #Omsk Russia test
        #step =self.weather.get_weather_step(datetime(year=1999,month=1,day=1,hour=10))
        #self.assertEqual(step["az_sun"],5,"Sun azimuth %s" % step["az_sun"] )

        #Rome Italy test
        #step =self.weather.get_weather_step(datetime(year=1987,month=1,day=1,hour=10))
        #self.assertEqual(step["az_sun"],5,"Sun azimuth %s" % step["az_sun"] )

        #Sapporo Japan test
        #step =self.weather.get_weather_step(datetime(year=1988,month=1,day=1,hour=11))
        #self.assertEqual(step["az_sun"],5,"Sun azimuth %s" % step["az_sun"] )

        #--------------

        #step =self.weather.get_weather_step(datetime(year=1997,month=1,day=1,hour=8))
        #self.assertEqual(step["az_sun"],5,"Sun azimuth %s" % step["az_sun"] )

        #step =self.weather.get_weather_step(datetime(year=1997,month=1,day=1,hour=7))
        #self.assertEqual(step["az_sun"],5,"Sun azimuth %s" % step["az_sun"] )
'''

'''
        step =self.weather.get_weather_step(datetime(year=1997,month=1,day=1,hour=4))
        self.assertEqual(step["wind_speed_dir"],40,"Wind Speed dir (40 - %s)" % step["wind_speed_dir"])
        self.assertEqual(step["wind_speed"],3.1,"Wind Speed")
        self.assertEqual(step["t_sky"],264.6156,"T Sky temperature")
        self.assertEqual(step["t_outside"],272.4,"Outside temperature")
        self.assertEqual(step["az_sun"],1.535039594490872,"Sun azimuth %s" % step["az_sun"] )

        step =self.weather.get_weather_step(datetime(year=1997,month=1,day=1,hour=3))
        self.assertEqual(step["wind_speed_dir"],30,"Wind Speed dir (30 - %s)" % step["wind_speed_dir"])
        self.assertEqual(step["wind_speed"],3.1,"Wind Speed")
        self.assertEqual(step["t_sky"],264.6156,"Sky temperature")
        self.assertEqual(step["t_outside"],272.4,"Outside temperature")
        self.assertEqual(step["az_sun"],1.341124150866685,"Sun azimuth %s" % step["az_sun"] )
'''



