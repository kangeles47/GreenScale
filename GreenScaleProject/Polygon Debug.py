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
print first2D
psurf = Polygon(first2D)
print psurf

second2D = []
second2D.append([-51.1551409,-117.02575544])
second2D.append([0.,0.])
second2D.append([0.53551983,2.38008813])
second2D.append([-101.77476198,-231.67142275])
print second2D
pshad = Polygon(second2D)
print pshad

print "Answer:"
pint = psurf & pshad
print pint

ptest = psurf
pint2 = ptest & psurf
print pint2

foo = []
foo.append( [ 0, 0 ] )
foo.append( [ 1, 2 ] )
foo.append( [ 2, 1 ] )

bar = []
bar.append( [ -1, -1 ] )
bar.append( [ -1, -2 ] )
bar.append( [ -2, -1 ] )

f = Polygon( foo )
b = Polygon( bar )

print f & b

poly = Polygon()
print poly
