#-------------------------------------------------------------------------------
# Name:        Area.py
# Purpose:     Green Scale Tool Area Module (Calculates surface area based on any set of coordinates)
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
import math
from objects.BaseElement import BaseElement
from objects.Shadow import Shadow
from numpy import *
import numpy


class Area(BaseElement):
    # Cartesian point
    cartesian_point = None

    # Elements
    openings = list()
    constructions = list()
    layers = list()
    materials = list()

    def surfaceArea(self, coordinates, az, tilt, surface):
        """
        Determines the area of an object from a set of coordinate points (window, surface, etc.)
        """
        azi_surf_rad = az*(math.pi/180)
        tilt_surf_rad = tilt*(math.pi/180)
        X_rec = coordinates  #coordinates == surface.cps  # [4][3] set of coordinates of surface

        #z = zeros((len(coordinates), 1))
        #row = 0
        #while row < len(z):
        #    col = 0
        #    z[row] = surface.cps[row][2]
        #    row += 1

        #print X_rec
        #print X_rec[0]
        self.shadow = Shadow()
        X1, u1, v1, w1 = self.shadow.wc2rc(X_rec, X_rec[0], azi_surf_rad, tilt_surf_rad)
        area = self.shadow.polyarea2(X1)

        return area

    def createAreaDictionary(self):
        global areaDictionary
        areaDictionary = dict()

    def addArea(self, index, value):
        areaDictionary[index] = value
        #print index, value

    def getArea(self, index):
        return areaDictionary.get(index)

    def getDictionary(self):
        return areaDictionary

    def createWinAreaDictionary(self):
        global areaWinDictionary
        areaWinDictionary = dict()

    def addWinArea(self, index, value):
        areaWinDictionary[index] = value
        #print index, value

    def getWinArea(self, index):
        return areaWinDictionary.get(index)

    def getWinDictionary(self):
        return areaWinDictionary