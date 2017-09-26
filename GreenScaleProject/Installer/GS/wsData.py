#-------------------------------------------------------------------------------
# Name:        WebServiceData
# Purpose:     Provides a method for retrieving data from the remote database
#              via web service, taking a list of material names as its input.
#
# Author:      ScottS
#
# Created:     29/05/2014
# Copyright:   (c) NDCRC 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import json
import urllib2
import sqlite3
from GSUtility import GSUtility
class wsData:

    def main():
        pass

    def getmaterials(self, nameList):
        global dbmaterials
        global materialsIndex
        materialsIndex = dict()
        wsMode = ''

        U = GSUtility()

        mymaterials = []
        if internet_on():
            #print "internet"
            # Initialize variables
            gbxmlnames = ''
            nameCount = 0

            #Iterate through the list of names
            for name in nameList:
                # If this is the first name, start the string and increment the counter
                if gbxmlnames == '':
                    gbxmlnames = name
                    nameCount += 1
                else:
                # Add to the string, inserting a pipe character as delimiter. Increment the counter
                    gbxmlnames = gbxmlnames + '|' + name
                    nameCount += 1

                # If we have more than 30 items, we want to hit the web service before the URL gets too long.
                # We reset the counter for the next run, form the URL and reset the string.
                if nameCount == 30:
                    nameCount = 0
                    #URL = 'http://greenscale-ws.crc.nd.edu/api/gsws/?limit=30&format=json&namegbxml__in=' + gbxmlnames.replace(' ', '%20')
                    URL = 'https://db.greenscale.org/api/gsws/?mode=' + wsMode + '&limit=30&format=json&namegbxml__in=' + gbxmlnames.replace(' ', '%20')
                    gbxmlnames = ''
                    #print URL
                    # Retrieves information from the web service, and extracts the material info into the list of dictionaries
                    mats = json.load(urllib2.urlopen(URL))
                    for section, data in mats.iteritems():
                        if section == 'objects':
                            mymaterials += data

            # When we're all done, if there are names left in the string, we need to get the information
            # from the web service and add it to the list of dictionaries.
            if gbxmlnames != '':
                #URL = 'http://greenscale-ws.crc.nd.edu/api/gsws/?limit=30&format=json&namegbxml__in=' + gbxmlnames.replace(' ', '%20')
                URL = 'https://db.greenscale.org/api/gsws/?mode=' + wsMode + '&limit=30&format=json&namegbxml__in=' + gbxmlnames.replace(' ', '%20')
                #print URL
                mats = json.load(urllib2.urlopen(URL))
                for section, data in mats.iteritems():
                    if section == 'objects':
                        mymaterials += data

        else:
            #print "local database"
            #TODO: Build list of items for use in where clause
            conn = sqlite3.connect('db.sqlite3')
            c = conn.cursor()
            #TODO: Develop query to return values for joined tables
            for row in c.execute('SELECT * FROM gsws_materials WHERE namegbxml IN ("Brick, Common: 8""", "Rigid insulation: 2""") '):
                print row
                # TODO: Convert to array of dictionary objects.

            conn.close()

        # Add the default materials
        mymaterials = self.addDefaultMaterials(mymaterials)
        U.devPrint(mymaterials)

        self.makeIndexDictionary(mymaterials)

        # Set the global variable to the list of dictionaries for use by the calling software.
        dbmaterials = mymaterials

    def addDefaultMaterials(self, materials):
        #Default Window
        thisMaterial = dict(unitcostmle='10.17', confidence=0, iswindow=True, matdensitygbxml='2500', maintenancefactor='0', lifeexpectancy='0', namearch='none', unitcostttl='13.35', finUnit={'unitdesc': '$/SF', 'id': 3, 'resource_uri': ''}, embodiedenergy='18.5', matdensityarch='2500', denUnit={'unitdesc': 'kg/m^3', 'id': 1, 'resource_uri': u''}, namegbxml='Default 1/8 in Pilkington single glazing', unitcostmat='4.82', thickness='0.125', id=3, eeUnit={'unitdesc': 'MJ/kg', 'id': 2, 'resource_uri': ''}, resource_uri='/api/gsws/3/')
        materials.append(thisMaterial)
        thisMaterial = dict(unitcostmle='0', confidence=0, iswindow=False, matdensitygbxml='0', maintenancefactor='0', lifeexpectancy='0', namearch='none', unitcostttl='0', finUnit={'unitdesc': '$/CY', 'id': 3, 'resource_uri': ''}, embodiedenergy='25', matdensityarch='7824', denUnit={'unitdesc': 'kg/m^3', 'id': 1, 'resource_uri': u''}, namegbxml='Default Metal surface', unitcostmat='0', thickness='0', id=3, eeUnit={'unitdesc': 'MJ/kg', 'id': 2, 'resource_uri': ''}, resource_uri='/api/gsws/3/')
        materials.append(thisMaterial)
        thisMaterial = dict(unitcostmle='0', confidence=0, iswindow=False, matdensitygbxml='0', maintenancefactor='0', lifeexpectancy='0', namearch='none', unitcostttl='0', finUnit={'unitdesc': '$/SF', 'id': 3, 'resource_uri': ''}, embodiedenergy='7.4', matdensityarch='510', denUnit={'unitdesc': 'kg/m^3', 'id': 1, 'resource_uri': u''}, namegbxml='Default 1 1/2 in wood', unitcostmat='0', thickness='0', id=3, eeUnit={'unitdesc': 'MJ/kg', 'id': 2, 'resource_uri': ''}, resource_uri='/api/gsws/3/')
        materials.append(thisMaterial)

        return materials

    def getDBMaterials(self):
        return dbmaterials

    def makeIndexDictionary(self, materials):
        counter = 0
        for mat in materials:
            materialsIndex[mat['namegbxml']]=counter
            counter += 1

    def getMaterial(self, index):
        thisListKey = materialsIndex.get(index, -1)
        if thisListKey >= 0:
            return dbmaterials[thisListKey]
        else:
            return thisListKey

def internet_on():
    try:
        response=urllib2.urlopen('https://db.greenscale.org/api/gsws/?next=/gsws/',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False


if __name__ == '__main__':
    main()
