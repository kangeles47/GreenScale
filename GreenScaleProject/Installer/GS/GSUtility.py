#-------------------------------------------------------------------------------
# Name:        GSUtility
# Purpose:
#
# Author:      ScottS
#
# Created:     14/08/2014
# Copyright:   (c) ScottS 2014
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------

class GSUtility:

    def main():
        pass

    def setDevFlag(self, flag):
        global devflag
        devflag = flag

    def devPrint(self, thisString):
        if (devflag == '1'):
            print thisString


if __name__ == '__main__':
    main()
