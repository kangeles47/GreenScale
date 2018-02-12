#-------------------------------------------------------------------------------
# Name:        main.py
# Purpose:     Green Scale Tool Main Module
#
# Author:      Holly Tina Ferguson
#
# Created:     15/02/2014
# Copyright:   (c) Holly Tina Ferguson 2013
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------
#!/usr/bin/python
import sys
import getopt
import logging
from datetime import datetime
import os
import unittest
from ModelV1 import ModelV1
from GreenScaleV1 import GreenScaleV1
from objects.Area import Area
from ctypes import *
import time
from GSUtility import GSUtility

# Default values are primarily for testing. It's expected that in use values will be passed in.
def main(argv, inputfile='D:/Users/Karen/Documents/Revit 2016/NIBS/GBXMLs/RC_FRAME.xml', outputpath='C:/Users/Karen/Desktop/GreenScale Project/GreenScale Project/Installer/GS/Output/', modelflag='3', devflag="1", shadowflag="0", locationfile = 'C:/Users/Karen/Desktop/GreenScale Project/GreenScale Project/Installer/GS/Locations/USA_MO_St.Louis-Lambert.Intl.AP.724340_TMY3.epw'):
    if len(sys.argv) == 8:
        inputfile = sys.argv[1] #2 for python, 1 for .NET, due to indexing differences. Comment out to run with defaults.
        outputpath = sys.argv[2] #3 for python, 2 for .NET, due to indexing differences. Comment out to run with defaults.
        modelflag = sys.argv[3]
        devflag = sys.argv[4]
        shadowflag = sys.argv[5]
        locationfile = sys.argv[6]

        # 2016 Version testing with Single Room Model
        #C:/Users/hfergus2/Desktop/MyPythonExport/Single_Room_2016.xml
        #Four_Room_2016.xml
        #Avon_Bldg_2016.xml
        #Vet_Center_2016.xml
        #L_1Floor_2016.xml
        #L_2Floor_2016.xml

        # 2014 Single Room Model
        #C:/Users/hfergus2/Desktop/GSbranch/tests/input/Single_model.xml

    U = GSUtility()
    U.setDevFlag(devflag)

    U.devPrint("Started the Python!")

    #print modelflag
    #print locationfile

    #Fall2013RLMVCRevit_v2_MarcValidation
    #Four_Room_Two_Floors_Model
    #Two_Room_One_Floor_Model
    #Single_model
    #Avon
    #L_ShapeFloor
    #FourRoom_with_Zones
    #FourRoomRoundColumn
    #FourRoomSquareColumn
    #/orientation/Avon_Position_E.xml

    # Report writer (CSV)
    # We want to log error logging (verbosity 1 of 3), check-pointing (verbosity 2 of 3), etc.
    #DEBUG      Detailed information, typically of interest only when diagnosing problems.
    #INFO       Confirmation that things are working as expected.
    #WARNING    An indication that something unexpected happened, or indicative of some problem in the near future (e.g. disk space low). The software is still working as expected.
    #ERROR      Due to a more serious problem, the software has not been able to perform some function.
    #CRITICAL   A serious error, indicating that the program itself may be unable to continue running.
    with open(outputpath + 'TM_coder.log', 'w'):
        pass
    with open(outputpath + 'TM_user.log', 'w'):
        pass
    with open(outputpath + 'EE_coder.log', 'w'):
        pass
    with open(outputpath + 'EE_user.log', 'w'):
        pass
    with open(outputpath + 'aggr.log', 'w'):
        pass
    with open(outputpath + 'Assembly.log', 'w'):
        pass
    with open(outputpath + 'Coder.log', 'w'):
        pass

    logging.basicConfig(filemode='w', filename=outputpath + "aggr.log", level=logging.INFO)
    aggr = logging.getLogger('aggr')
    aggr.setLevel(logging.INFO)
    # Create the logging file handler
    fh = logging.FileHandler(outputpath + "aggr.log")
    formatter = logging.Formatter('%(asctime)s,%(name)s,%(levelname)s,%(message)s,')
    fh.setFormatter(formatter)
    # Add handler to logger object
    aggr.addHandler(fh)
    aggr.info("Started")

    logging.basicConfig(filemode='w', filename=outputpath + "Assembly.log", level=logging.INFO)
    Assembly = logging.getLogger('Assembly_V1')
    Assembly.setLevel(logging.INFO)
    # Create the logging file handler
    fh = logging.FileHandler(outputpath + "Assembly.log")
    formatter = logging.Formatter('%(asctime)s,%(name)s,%(levelname)s,%(message)s,')
    fh.setFormatter(formatter)
    # Add handler to logger object
    Assembly.addHandler(fh)
    Assembly.info("Assembly Totals:")
    #TM_coder.info(inputfile)
    #TM_coder.info(outputpath)

    logging.basicConfig(filemode='w', filename=outputpath + "Coder.log", level=logging.INFO)
    Coder = logging.getLogger('Coder_V1')
    Coder.setLevel(logging.INFO)
    # Create the logging file handler
    # C:\Users\hfergus2\Desktop\pygscale\TM_user.log
    fh = logging.FileHandler(outputpath + "Coder.log")
    formatter = logging.Formatter('%(asctime)s,%(name)s,%(levelname)s,%(message)s,')
    fh.setFormatter(formatter)
    # Add handler to logger object
    Coder.addHandler(fh)
    Coder.info("Data For Developers: Notes from gbxml.py")

    logging.basicConfig(filemode='w', filename=outputpath + "TM_user.log", level=logging.INFO)
    TM_user = logging.getLogger('TMuser_V1')
    TM_user.setLevel(logging.INFO)
    # Create the logging file handler
    # C:\Users\hfergus2\Desktop\pygscale\TM_user.log
    fh = logging.FileHandler(outputpath + "TM_user.log")
    formatter = logging.Formatter('%(asctime)s,%(name)s,%(levelname)s,%(message)s,')
    fh.setFormatter(formatter)
    # Add handler to logger object
    TM_user.addHandler(fh)
    TM_user.info("Thermal Model User Program Started")

    logging.basicConfig(filemode='w', filename=outputpath + "EE_coder.log", level=logging.INFO)
    EE_coder = logging.getLogger('EEcoder_V1')
    EE_coder.setLevel(logging.INFO)
    # Create the logging file handler
    fh = logging.FileHandler(outputpath + "EE_coder.log")
    formatter = logging.Formatter('%(asctime)s,%(name)s,%(levelname)s,%(message)s,')
    fh.setFormatter(formatter)
    # Add handler to logger object
    EE_coder.addHandler(fh)
    EE_coder.info("Embodied Energy Coder Program Started")

    logging.basicConfig(filemode='w', filename=outputpath + "EE_user.log", level=logging.INFO)
    EE_user = logging.getLogger('EEuser_V1')
    EE_user.setLevel(logging.INFO)
    # Create the logging file handler
    fh = logging.FileHandler(outputpath + "EE_user.log")
    formatter = logging.Formatter('%(asctime)s,%(name)s,%(levelname)s,%(message)s,')
    fh.setFormatter(formatter)
    # Add handler to logger object
    EE_user.addHandler(fh)
    EE_user.info("Embodied Energy User Program Started")

    # Surface Area Dictionary
    area = Area()
    area.createAreaDictionary()
    area.createWinAreaDictionary()

    #Check if EE model should be run
    if (modelflag == '1' or modelflag == '3'):
        # Input parameters for Embodied Energy Model (EEM)
        EE_coder.info(" ")
        EE_coder.info(" ") # Spacing for the excel to be more readable for the students
        EE_coder.info(" ")
        EE_coder.info("Missing Materials Data")

        EEstart = time.clock()
        EE_user.info("Embodied Energy Data:")
        pathStr = str(inputfile)
        EE_user.info("Model File Path:, %s" % pathStr)  # Record Model Identifier or Path for Log
        EE_user.info("Location: " + locationfile)
        model2 = GreenScaleV1()
        model2.gbxml = inputfile
        model2.input_dir = os.path.join(os.path.dirname(__file__), 'objects')
        U.devPrint("Reaching EE_Model.run function...")
        model2.run()
        EE_coder.info(" ")
        EE_coder.info(" ") # Spacing for the excel to be more readable for the students
        EE_coder.info(" ")
        EEend = time.clock()
        U.devPrint("Time for EE Module: " + str(EEend-EEstart))


    print "==================================================================================="
    print "==================================================================================="
    print "==================================================================================="

    #Check if TM model should be run
    if (modelflag == '2' or modelflag == '3'):
        # Input parameters for Thermal Model (TM)
        TMstart = time.clock()
        TM_user.info("Thermal Model Data")
        pathStr = str(inputfile)
        TM_user.info("Model File Path:, %s" % pathStr)  # Record Model Identifier or Path for Log
        TM_user.info("   ")
        TM_user.info("St.Louis,Hours 1-24,January 1-December 31,Coeff = 1,No Shadows")
        #TM_user.info("   ")
        model1 = ModelV1()
        model1.gbxml = inputfile
        model1.location = locationfile
        #print "check:  ", model1.location
        model1.start_date = datetime(year=1997, month=1, day=1, hour=0)
        model1.end_date = datetime(year=1997, month=12, day=31, hour=23)
        model1.Coeff = 1        # Currently using 0.25, 0.45, 1.00
        model1.ShadowsFlag = int(shadowflag)  # 1 means calculate shadows, 0 means ignore shadow module
        model1.Q_total = 0
        # Zones are part of the gbxml.py but not sure at this point how to have them set from here...
        model1.terrain = 'Towns and City Scapes'  # Will be one of these from a list of options offered to the user:
            #   'Flat or Open Countryside'
            #   'Rough or Wooded Country'
            #   'Towns and City Scapes'
            #   'Ocean Front Areas'
            #   'Urban, Industrial, or Forest'
        # Using Na's formula for month totals instead of annual total only is currently giving an underestimation for the total heat flux
        model1.timestep = 1  # Will be set at 1 for every hour every day or 2 for every hour every other day
        U.devPrint("Reaching TM_Model.run function...")
        model1.run()
        TMend = time.clock()
        U.devPrint("Time for TM Module: " + str(TMend-TMstart))

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["inputfile=", "outputfile="])
    except getopt.GetoptError:
        #print 'test.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            #print 'test.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-h", "--help"):
            #usage()
            sys.exit()
        elif opt == "-d":
            global _debug
            _debug = 1
            sys.exit()
        elif opt in ("-i", "--inputfile"):
            inputfile = arg
        elif opt in ("-o", "--outputfile"):
            outputfile = arg

    #logging.basicConfig(filename='output.log', level=logging.DEBUG)                # Appends new logging
    #logging.basicConfig(filename='output.log', filemode='w', level=logging.DEBUG)  # Replaces whole logging file with level
    #logging.debug('Tool is functional... ')
    #logging.warning('Check for correctness: ')
    #logging.warn('Check for correctness: ')
    #logging.error('Not passing... ')
    #logging.critical('Verify this number: ')

    #log = logging.getLogger('TM_V1')
    # This error will log the file and line number of errors
    #try:
    #    raise RuntimeError
    #except Exception, err:
    #    log.exception("Error!")

    #print 'Input file is "', inputfile
    #print 'Output file is "', outputfile

    Assembly.info(" ")
    Assembly.info(" ")
    Assembly.info(" ")
    EE_coder.info("EE Coder Version Finished")
    EE_user.info("EE User Version Finished")
    Assembly.info("Assembly Finished")
    #TM_coder.info("TM Coder Version Finished")
    TM_user.info("TM User Version Finished")

    # Create the .csv reporter [model, KWatts, Joules, EETotal, EWTotal, Cost...][surface area reporting]
    # This worked before passing in from C#:
    #outputfile = open('output.csv', 'w')
    #with open("TM_user.log", 'r') as f:
    #    for line in f:
    #        outputfile.write(line)
    #outputfile.close()
    # This worked for passing in from C#:
    # Embodied Energy Model for Excel:
    outputfile = open(outputpath + 'ModelOutput.csv', 'w') #C:\Users\hfergus2\Desktop\pygscale\output_EE.csv
    #outputfileTest.write("Is able to write to this file type...")
    with open(outputpath + "TM_user.log", 'r') as f:  # TM Data by Month and Year Totals
        for line in f:
            outputfile.write(line)
    with open(outputpath + "EE_coder.log", 'r') as f:  # EE Model Data
        for line in f:
            outputfile.write(line)
    with open(outputpath + "EE_user.log", 'r') as f:  # EE Missing Material Section, if any
        for line in f:
            outputfile.write(line)
    with open(outputpath + "Assembly.log", 'r') as f:  # EE Missing Material Section, if any
        for line in f:
            outputfile.write(line)
    # This should be somewhere noted for a user, but is not necessary to be shown now in the Output file
    #with open(outputpath + "Coder.log", 'r') as f:  # Coder notes from gbxml missing data/tag handling, if any
    #    for line in f:
    #        outputfile.write(line)
    outputfile.close()
    sys.stdout.write("Models Finished")

if __name__ == "__main__":
    #logging.basicConfig()
    main(sys.argv[1:])
    #main(inputfile, outputfile)



