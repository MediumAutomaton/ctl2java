# Prepare all the imported stuff (Action & Method libraries & Mappings) in a way
# that will be convenient later. Sort stuff and do some higher-level checks than
# ctlconv did.
# File last updated 9-8-25

import assets
from common import Common


class Preparer:
    def __init__(self, mappings1, mappings2, libDict):
        self.version = "1.0-0"
        self.mappings1 = mappings1
        self.mappings2 = mappings2
        self.libDict = libDict

        # Some initial verification
        if self.mappings2:
            if not self.mappings1["Season"] == self.mappings2["Season"]:
                Common.error("Mismatched Seasons between gamepads.")

        self.season = self.mappings1["Season"]
        self.settersLib = self.libDict["Setters"][self.season]

        if not self.settersLib["Season"] == self.mappings1["Season"]:
            Common.error("Gamepads' Season does not match Setters' Season.")

        # self.season = self.settersLib["Season"]

        # Libraries are valid for this Season
        newLibDict = {}
        for category in self.libDict.keys():
            newLibDict.update( { category : {} } )
            for libName in self.libDict[category]:
                libSeason = self.libDict[category][libName]["Season"]
                if libSeason != self.season and libSeason != "":
                    if category == "BaseActions":
                        print("Base Action ", end="")
                    elif category == "ExtensionActions":
                        print("Extension Action ", end="")
                    elif category == "Methods":
                        print("Method ", end="")
                    elif category == "Setters":
                        print("Setters ", end="")
                    else:
                        print("UNKNOWN ", end="")
                    print("Library '" + libName + "' is not valid for this Season (mismatched with Setters' Season); ignoring.")
                else:
                    newLibDict[category].update( { libName : self.libDict[category][libName] } )
        self.libDict = newLibDict
        self.baseLibs = self.libDict["BaseActions"]
        self.extensionLibs = self.libDict["ExtensionActions"]
        self.methodLibs = self.libDict["Methods"]
        # self.settersLib = self.libDict["Setters"][self.season]

        # Gamepads were given as expected
        # try:  # Should be in ctlconv.py
        #     self.mappings1["Gamepad"] = int(self.mappings1["Gamepad"])
        #     self.mappings2["Gamepad"] = int(self.mappings2["Gamepad"])
        # except:
        #     Common.error("Your 'Gamepad' fields in the mapping files are of the wrong type!")
        if not self.mappings1["Gamepad"] == 1:
            Common.error("Got gamepad" + self.mappings1["Gamepad"] + " where I expected gamepad1")
        if self.mappings2:
            if not self.mappings2["Gamepad"] == 2:
                Common.error("Got gamepad" + self.mappings2["Gamepad"] + " where I expected gamepad2")


        # Expand libDict and combine all Libraries in each category together
        # self.baseLibs = libDict["BaseActions"]
        self.base = {}
        for libName in self.baseLibs.keys():
            for actionName in self.baseLibs[libName]["Actions"].keys():
                self.base.update( {actionName : self.baseLibs[libName]["Actions"][actionName]} )

        # self.extensionLibs = libDict["ExtensionActions"]
        self.extension = {}
        for libName in self.extensionLibs.keys():
            for actionName in self.extensionLibs[libName]["Actions"].keys():
                self.extension.update( {actionName : self.extensionLibs[libName]["Actions"][actionName]} )

        # self.methodLibs = libDict["Methods"]
        self.methods = {}
        self.constructorLines = []
        self.classLines = []
        for libName in self.methodLibs.keys():
            for methodName in self.methodLibs[libName]["Methods"].keys():
                if methodName == "(constructor)":
                    methodCode = self.methodLibs[libName]["Methods"][methodName]
                    for line in methodCode:
                        self.constructorLines.append(line)
                elif methodName == "(class)":
                    methodCode = self.methodLibs[libName]["Methods"][methodName]
                    for line in methodCode:
                        self.classLines.append(line)
                else:
                    self.methods.update( {methodName : self.methodLibs[libName]["Methods"][methodName]} )

        # self.settersLib = libDict["Setters"]
        self.setters = self.settersLib["Setters"]


        # Method names are valid
        for methodName in self.methods.keys():
            if methodName.count("<~") > 0:
                if methodName.count("<~") > 1:
                    Common.error("Too many tags in name of Method '" + methodName + "'.")
                elif methodName.count(">") < 1:
                    Common.error("Unclosed tag in name of Method '" + methodName + "'.")

                tagStart = methodName.index("<~")+1
                tagEnd = methodName.index(">")
                if tagEnd < tagStart:
                    Common.error("Backwards tag brackets in name of Method '" + methodName + "'.")
                if tagStart != 1:
                    Common.error("The drive type tag in a Method name should be at the start. It is not for Method '" + methodName + "'.")

                tagContents = methodName[tagStart+1 : tagEnd]
                if tagContents not in assets.validDriveTypes:
                    Common.error("Invalid drive type for Method '" + methodName + "'. Must be in this list: " + str(assets.validDriveTypes))


        # All Setters are implemented by Methods
        happySetters = []
        for methodName in self.methods.keys():
            # Strip drive type tag, if it's there
            # tagEnd = methodName.find(">")
            # if tagEnd > 0:
            #     methodName = methodName[tagEnd+1:]

            if methodName not in happySetters:
                happySetters.append(methodName)

        unhappySetters = []
        for setter in self.setters:
            if setter not in happySetters:
                if setter[:5] == "<~dt>":
                    if not "<~indy>" + setter[5:] in happySetters:
                        if not "<~fieldy>" + setter[5:] in happySetters:
                            unhappySetters.append(setter)
                else:
                    unhappySetters.append(setter)

        if len(unhappySetters) > 0:
            Common.error("The following Setters are not implemented by Methods: " + str(unhappySetters))


    # def sortMappingsByAction(self):
    #     primitives = self.mappings1["Buttons"]
    #     primitives.update(self.mappings1["Axes"])
    #     if self.mappings2:
    #         primitives.update(self.mappings2["Buttons"])
    #         primitives.update(self.mappings2["Axes"])
    #
    #     actionDict = {}
    #     for primitiveName in primitives.keys():
    #         primitive = primitives[primitiveName]
    #         action = primitive["Action"]
    #         if action["Name"] not in actionDict.keys():
    #             actionDict.update( { action["Name"] : {primitiveName : primitive } } )
    #         actionDict[action["Name"]].update( {primitiveName : primitive} )

        # actionDict = {}
        # for primitiveName in primitives.keys():
        #     primitive = primitives[primitiveName]
        #     primitiveDict = {}
        #     modifierDict = {}
        #     for modifierName in primitive.keys():
        #         modifier = primitive[modifierName]
        #         # modifierDict = {}
        #         action = modifier["Action"]
        #         modifierDict.update( { modifierName : action["Parameters"] } )
        #     primitiveDict.update( { primitiveName : modifierDict } )
        #     actionDict.update( { action["Name"] : primitiveDict } )

        # return actionDict


    def addPrefixes(self, primitives, gamepadNumber):
        newPrimitives = {}
        for primitiveName in primitives.keys():
            primitive = primitives[primitiveName]
            newPrimitiveName = str(gamepadNumber) + primitiveName
            newPrimitives.update( { newPrimitiveName : primitive } )
            # for modifierName in primitive.keys():
            #     modifier = primitive[modifierName]
            #     newModifierName = str(gamepadNumber) + modifierName
            #     newPrimitives.update( { newModifierName : modifier } )
        return newPrimitives


    def combineMappingsAndAddPrefixes(self):
        outdict = {}

        primitives1 = self.mappings1["Buttons"]
        primitives1.update(self.mappings1["Axes"])
        outdict.update(self.addPrefixes(primitives1, "One"))

        if self.mappings2:
            primitives2 = self.mappings2["Buttons"]
            primitives2.update(self.mappings2["Axes"])
            outdict.update(self.addPrefixes(primitives2, "Two"))

        return outdict


    def expandLibDict(self):
        # We already did it in __init__() - we're just returning the results
        return {
            "BaseActions": self.base,
            "ExtensionActions": self.extension,
            "Methods": self.methods,
            "Setters": self.setters,
            "settersLib": self.settersLib,  # Expander needs this
            "constructorLines": self.constructorLines,  # Generator needs this
            "classLines": self.classLines,  # Generator needs this
            }
