# CTL2Java CLI and linking fabric
# Also all File I/O happens here (I think)
# File last updated 9-29-25

import os
import sys
from argparse import ArgumentParser

from ctlconv import CTLConv
import assets
from common import Common
from preparer import Preparer
from expander import Expander
from generator import Generator

version = "1.0-0"

# Versions of the other modules are tracked independently
compatibleCTLConvVersions = ["1.0-0"]
compatiblePreparerVersions = ["1.0-0"]
compatibleExpanderVersions = ["1.0-0"]
compatibleGeneratorVersions = ["1.0-0"]

# ----- Command-line arguments -----
argparser = ArgumentParser()
argparser.add_argument("-ver", "--version", help="Print version then exit", action="store_true")
argparser.add_argument("-if1", "--infile1", help="Input file for gamepad1, otherwise use stdin", action="store")
argparser.add_argument("-if2", "--infile2", help="Input file for gamepad2", action="store")
argparser.add_argument("-of", "--outfile", help="Output class name (and output file name), otherwise use stdout. Omit the '.java' file extension.", action="store")
argparser.add_argument("-op", "--outpackage", help="Package that the output file resides in, otherwise assume TeamCode", action="store")
argparser.add_argument("-dt", "--drivetype", help="'Indy' (traditional) or 'Fieldy' (field-oriented). Assume Indy if this isn't set.", action="store")
argparser.add_argument("-f", "--verify", help="Only verify infile, do not generate control scheme", action="store_true")
argparser.add_argument("-d", "--debug", help="Enable some extra long debug output.", action="store_true")
args = argparser.parse_args()

# Handle --version immediately
if args.version:
    print(version)
    sys.exit(0)

# Process arguments
if args.outfile:
    outfile = args.outfile
else:
    outfile = "<~stdout>"

if args.outpackage:
    outpackage = args.outpackage
else:
    outpackage = "org.firstinspires.ftc.teamcode"

if args.drivetype:
    low = args.drivetype.lower()
    if low in ["indy", "fieldy"]:
        drivetype = low
    else:
        Common.error("Invalid drivetype specified. Must be 'Indy' or 'Fieldy'.")
else:
    drivetype = "indy"

if args.infile1:
    try:
        infile1 = open(args.infile1, encoding="utf-8-sig")
    except:
        Common.error("Could not open input file 1.", True)
else:
    infile1 = sys.stdin

if args.infile2:
    try:
        infile2 = open(args.infile2, encoding="utf-8-sig")
    except:
        Common.error("Could not open input file 2.", True)
else:
    infile2 = None


# ----- Convert files -----
converter1 = CTLConv(infile1, assets.gamepadRequiredFields)
print("Converting file for gamepad1:")
outdict1 = converter1.getVerifiedDict()
modifiers = [ "One" + x for x in outdict1["Modifiers"] ]
print("\n\n")
if infile2:
    converter2 = CTLConv(infile2, assets.gamepadRequiredFields)
    print("Converting file for gamepad2:")
    outdict2 = converter2.getVerifiedDict()
    modifiers.extend( [ "Two" + x for x in outdict2["Modifiers"] ] )
    print("\n\n")
else:
    outdict2 = None

# Debug output, if enabled
if args.debug:
    print("gamepad1:")
    Common.prettydict(outdict1)
    if infile2:
        print("gamepad2:")
        Common.prettydict(outdict2)

if args.verify:
    print("--verify argument is set, so exiting now")
    sys.exit(0)

# ----- Create libDict -----
# Create dict with needed categories but empty lists for values
libNameDict = assets.libDirs.copy()
for key in libNameDict.keys():
    libNameDict[key] = []

# Populate dict with filenames
for libType in assets.libDirs.keys():
    for filename in os.listdir(assets.libDirs[libType]):
        if filename[-5:] == ".json":
            libNameDict[libType].append(filename)

# Create dict to sort converted libs into
libDict = assets.libDirs.copy()
for key in libDict.keys():
    libDict[key] = {}

# Convert all libs
for libType in libNameDict.keys():
    for libName in libNameDict[libType]:
        try:
            libFile = open(assets.libDirs[libType] + "/" + libName)
        except:
            Common.error("Could not open Library file '" + libName + "'.")
        conv = CTLConv(libFile, assets.requiredFieldsByLibType[libType])
        newName = libName[:-5] # Remove file extension
        newLib = conv.getVerifiedDict()
        libDict[libType].update({newName : newLib})

# Debug output, if enabled
if args.debug:
    for libType in libDict.keys():
        print("Library type: " + libType)
        for libName in libDict[libType].keys():
            print(libName)
            Common.prettydict(libDict[libType][libName])


# ----- Preparer -----
preparer = Preparer(outdict1, outdict2, libDict)
expandedLibDict = preparer.expandLibDict()
sortedMappings = preparer.combineMappingsAndAddPrefixes()


# ----- Create expander -----
expander = Expander(expandedLibDict, sortedMappings, outfile, outpackage)


# ----- Create generator -----
generator = Generator(
    sortedMappings,
    expander,
    expandedLibDict["constructorLines"],
    expandedLibDict["classLines"],
    expandedLibDict["Setters"],
    expandedLibDict["settersLib"]["Imports"],
    modifiers,
    drivetype,
    args.debug
)
generatedLines = generator.getFile()

if args.debug:
    print("\nWriting these lines:")
    print(generatedLines)

if outfile == "<~stdout>":
    sys.stdout.writelines(generatedLines)
else:
    print("\nWriting to file '" + outfile + "'")
    with open(outfile + ".java", "w") as f:
        f.write( generator.stringify( generatedLines ) )
