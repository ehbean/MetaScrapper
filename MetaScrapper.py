import argparse
from datetime import datetime
from GPSPhoto import gpsphoto
import json
import os
from os.path import dirname
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# Creates a parser as "par"
par = argparse.ArgumentParser()

# Arguments
par.add_argument("-fp", "--folderPath", dest="fp", required=True, help="path\\to\\the\\folder where the target images are.")
par.add_argument("-o", "--outputType", dest="ot", required=True, help="Determines what information is given. \n 1: Gives GPS coordinates and additional file date. \n 2: Gives just a list of GPS coordinates. \n 3: Gives GPS coordinates with a file name.")

# Parse the Arguments
args = par.parse_args()

# Stores arguments are variables
filePath = args.fp
outputType = int(args.ot)

imageList = []

# Searches the directory "filePath" and returns a list of all the .png and .jpg picture files therein.
def FilterImages(filePath):
    for x in os.listdir(filePath):
        if (x.endswith(".jpg") or x.endswith(".JPG") or x.endswith(".png") or x.endswith(".PNG")):
            imageList.append(x)
            print(imageList)
    return imageList

# Processes the targetImage for any GPS coordinate metadata and stores it in a dictionary
def GetGPS(targetImage):
    global gpsDict
    global gpsLat
    global gpsLong
    global gpsAlt
    global gpsDead
    gpsDead = 0
    gpsDict = gpsphoto.getGPSData(targetImage)

#Attempts to find the Latitude of the picture.
    try: 
        if "Latitude" in gpsDict and not None:
            gpsLat = gpsDict["Latitude"]
        else:
            gpsDict["Latitude"] = 0.0
            print("Latitude Not Found in " + targetImage)
    finally:
        print("Latitude Finalized in " + targetImage +"\n")

#Attempts to find the Longitude of the picture.
    try:
        if "Longitude" in gpsDict and not None:
            gpsLong = gpsDict["Longitude"]
        else:
            gpsDict["Longitude"] = 0.0
            print("Longitude Not Found in " + targetImage)
    finally:
        print("Longitude Finalized in " + targetImage +"\n")

#Attempts to find  the Altitude of the picture.
    try:
        if "Altitude" in gpsDict and not None:
            gpsAlt = gpsDict["Altitude"]
        else:
            gpsDict["Altitude"] = 0.0
            print("Altitude Not Found in " + targetImage)
    finally:
        print("Altitude Finalized in " + targetImage +"\n")

    return gpsDict


# Processes the targetImage for dateTime, Make and Model if found and returns it as a dictionary.
def GetMisc(targetImage, i):
    image = Image.open(targetImage)
    metaData = image.getexif()
    global metaDict
    global dateTime
    global metaMake
    global metaModel
    metaDict = {}
    
    try:
        for tag, value in image.getexif().items():
            if tag in TAGS:
                metaDict[TAGS[tag]] = value
    except:
        metaDict[TAGS[tag]] = "-"

    #Finds the Datetime stamp, if there is data for it. 
    if "DateTime" in metaDict:
        dateTime = metaDict["DateTime"]
    else:
        dateTime = "-"

    #Finds the Make of the picture, if there is data for it.
    if "Make" in metaDict:
        metaMake = metaDict["Make"]
    else:
        metaMake = "-"

    #Finds the Model of the picture, if there is data for it.
    if "Model" in metaDict:
        metaModel = metaDict["Model"]
    else:
        metaModel = "-"

    global miscDict
    miscDict = {"File": imageList[i], "DateTime": dateTime, "Make": metaMake, "Model": metaModel}

    return miscDict

# Merges the GPS coordinates and the targetImage file name and returns it as a dictionary.
def MergeGPSandName(targetImage, i):
    image = Image.open(targetImage)
    global gpsNameDict
    gpsNameDict = {"File": imageList[i]}
    gpsNameDict.update(gpsDict)
    print(gpsNameDict)
    return gpsNameDict

# Merges the miscDict and gpsDict into a single dictionary named fullDict
def Merge():
    global fullDict
    fullDict = {}
    fullDict.update(miscDict)
    fullDict.update(gpsDict)
    print(fullDict)
    return fullDict

# This outputs a JSON file at folderPath that contains all metadata gathered.
def FullDetailJSON():
    now = datetime.now()
    formatNow = now.strftime("%d-%m-%Y_%H-%M")
    reportName = "FullDetailFile" + formatNow + ".json"
    reportPath = filePath + "\\" + reportName

    with open(reportPath, "a") as output:
        json.dump(fullDict, output)
        output.write("\n")

# This outputs a JSON file that just contains gps coordinates and no further information.
def GPSOnlyJSON():
    now = datetime.now()
    formatNow = now.strftime("%d-%m-%Y_%H-%M")
    reportName = "GPSCoordsFile" + formatNow + ".json"
    reportPath = filePath + "\\" + reportName

    with open(reportPath, "a") as output:
        json.dump(gpsDict, output)
        output.write("\n")

# This outputs a JSON file with the targetimage name and it's GPS coordinates.
def GPSandNameJSON():
    now = datetime.now()
    formatNow = now.strftime("%d-%m-%Y_%H-%M")
    reportName = "GPSandNameFile" + formatNow + ".json"
    reportPath = filePath + "\\" + reportName

    with open(reportPath, "a") as output:
        json.dump(gpsNameDict, output)
        output.write("\n")

# Function that tests the argument given for which type of output was asked for.
def Output(outputType):
    match outputType:
        case 1:
            print("Adding to too FullDetail file\n")
            FullDetailJSON()
        case 2:
            print("Adding to GPSCoords file\n")
            GPSOnlyJSON()
        case 3:
            print("Adding to GPSandName file\n")
            GPSandNameJSON()

# Executes all other functions, with conditional outcomes depending on the given arguments.
def Run():
    FilterImages(filePath)
    for i in range(len(imageList)):
        targetImage = str(filePath) + "\\" + imageList[i]
        print(targetImage)
        GetGPS(targetImage)
        GetMisc(targetImage, i)
        Merge()
        MergeGPSandName(targetImage, i)
        print(fullDict)
        Output(outputType)
    
    print("Finished!")
Run()