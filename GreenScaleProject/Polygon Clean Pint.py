import sys
import numpy as np
from Polygon import *
from Polygon.Utils import pointList
from itertools import permutations
from random import sample
import math

first2D = []
first2D.append([0.00000000e+00,0.00000000e+00])
first2D.append([2.43959033e+00,1.66533454e-16])
first2D.append([5.35519830e-01,2.38008813e+00])
first2D.append([0.562039786,-.259342456])
pint = Polygon(first2D)
first2D = []
first2D.append([0.00000000e+00,0.00000000e+00])
first2D.append([2.43959033e+00,1.66533454e-16])
first2D.append([5.35519830e-01,2.38008813e+00])
first2D.append([0.562039786,-.259342456])
pint.addContour(first2D)
print "pint:"
print pint
print

clean = []
pintTemp = Polygon()
for Cont in range(0, len(pint)):
    for Pt in range(0, len(pint.contour(Cont))):
        clean.append([round(pint[Cont][Pt][0],4),round(pint[Cont][Pt][1],4)])
    pintTemp.addContour(clean)
    clean = []
pint = pintTemp



print "Clean pint:"
print pint
