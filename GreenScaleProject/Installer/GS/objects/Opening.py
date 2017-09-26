#-------------------------------------------------------------------------------
# Name:        Opening.py
# Purpose:     Green Scale Tool Opening Module (Class for "Openings")
#
# Author:      Holly Tina Ferguson
#
# Created:     15/09/2013
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
from objects.BaseElement import BaseElement


class Opening(BaseElement):
    def get_A(self, opening):
        """
        Calculates the A of the surface.
        """
        return round(opening.height * opening.width * 0.3048 * 0.3048, 4)


