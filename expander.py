# Expand expander tags
# File last updated 9-29-25

import assets
from common import Common

class Expander:
    def __init__(self, expandedLibDict, sortedMappings, outFile, outPackage):
        self.version = "1.0-0"
        self.libs = expandedLibDict
        self.sortedMappings = sortedMappings
        self.outPackage = outPackage
        self.className = outFile
        self.stateInteriorLines = None
        self.classLines = None
        self.importLines = None


    def expandLine(self, line, type, mapping=None, mappingName=None, modifierName=None):
        # Do we have to run at all?
        if line.count("<~") == 0:
            return line

        out = ""
        while line.count("<~") > 0:
            tagStart = line.index("<~")
            # tagEnd = line.index(">")

            out += line[ : tagStart ]
            line = line[ tagStart : ]

            tagStart = line.index("<~")  # The previous line moved tagStart, so re-calculate it
            tagEnd = line.index(">")
            tag = line[ tagStart+2 : tagEnd ]

            line = line[ tagEnd+1 : ]  # Remove tag from beginning of line

            if tag.count(":") > 0:
                if tag.count(":") > 1:
                    Common.error("Can't have more than 1 colon per tag! Found in this line from somewhere:\n" + line)
                if type == "BaseAction":
                    out += self.processBaseActionColonTag(tag, mapping, mappingName, modifierName)
                elif type == "ExtensionAction":
                    out += self.processExtensionActionColonTag(tag, mapping, mappingName, modifierName)
                elif type == "Method":
                    out += self.processMethodColonTag(tag)
                elif type == "FilePath":
                    out += self.processFilePathColonTag(tag)
                elif type == "Template":
                    out += self.processTemplateColonTag(tag)
            else:
                if type == "BaseAction":
                    out += self.processBaseActionNormalTag(tag, mapping, mappingName, modifierName)
                elif type == "ExtensionAction":
                    out += self.processExtensionActionNormalTag(tag, mapping, mappingName, modifierName)
                elif type == "Method":
                    out += self.processMethodNormalTag(tag)
                elif type == "FilePath":
                    out += self.processFilePathNormalTag(tag)
                elif type == "Template":
                    out += self.processTemplateNormalTag(tag)

        out += line # Append whatever's left after the last tag
        return out


    # Meant to be called from other files
    def getAndExpandMethod(self, methodName):
        out = ""
        method = self.libs["Methods"][methodName]
        for line in method:
            out += "\t" + self.expandLine(line, "Method") + "\n"
        return out


    def processMethodColonTag(self, tag):
        colonIdx = tag.index(":")
        tagType = tag[ : colonIdx ]
        tagContent = tag[ colonIdx+1 : ]

        if tagType == "param":
            Common.error("There seems to be a 'param:' expander tag in a Method, where it doesn't belong.")

        elif tagType == "all":
            # Action exists
            if not (tagContent in self.libs["BaseActions"].keys() or tagContent in self.libs["ExtensionActions"].keys()):
                Common.error("'all:' tag refers to Action '" + tagContent + "' that doesn't seem to exist?")

            # mappingsForAction = self.sortedMappings[tagContent]

            # Expand and gather them all
            # out = ""
            # for mappingName in mappingsForAction.keys():
            #     mapping = mappingsForAction[mappingName]
            #     if len(mapping) > 1:
            #         for idx, modifierName in enumerate(mapping.keys()):
            #             modifier = mapping[modifierName]
            #             if idx > 1:
            #                 out += "else "
            #             if modifierName != "Default":
            #                 out += "if (" + modifierName.lower() + ".isActive) {\n"
            #                 out += self.getAndExpandActionForMapping(tagContent, modifier["Parameters"])
            #                 out += "\n}"
            #         out += "else {\n"
            #         out += self.getAndExpandActionForMapping(mapping, mapping["Default"])
            #         out += "}"
            #     else:
            #         out += self.getAndExpandActionForMapping(mapping, mapping["Default"])

            # Gather all Mappings mapped to this Action
            # mappingsToAdd = []
            # actionCodes = []
            outLines = []
            for mappingName in self.sortedMappings.keys():
                mapping = self.sortedMappings[mappingName]
                modifierCodes = []
                for modifierName in mapping.keys():
                    if mapping[modifierName]["Action"]["Name"] == tagContent:
                        modifierCodes.append( {
                            "Name" : modifierName,
                            "Code" : self.expandActionForModifier(mapping, mappingName, modifierName),
                        } )

                gamepadNumber = mappingName[:3]
                if len(modifierCodes) == 1:
                    if modifierCodes[0]["Name"] == "Default":
                        if len(mapping.keys()) > 1:
                            outLine = "\tif ( "
                            startLen = len(outLine)
                            for idx, modName in enumerate(mapping.keys()):
                                # outLines.append("if !( " + gamepadNumber + modName + ".isActive() ) {")
                                # outLines.extend( [ "\t"+line for line in modifierCodes[0]["Code"].split("\n") ] )
                                # outLines.append("}")
                                if modName != "Default":
                                    if len(outLine) > startLen:
                                        outLine += " && "
                                    outLine += "!" + gamepadNumber + modName + ".isActive()"
                            outLine += " ) {"
                            outLines.append(outLine)
                            outLines.extend( [ "\t\t\t"+line for line in modifierCodes[0]["Code"].split("\n") ] )
                            outLines.append("\t\t}")
                        else:
                            outLines.extend( [ "\t\t"+line for line in modifierCodes[0]["Code"].split("\n") ] )
                    else:
                        outLines.append("\tif (" + gamepadNumber + modifierCodes[0]["Name"] + ".isActive()) {")
                        outLines.extend( [ "\t\t\t"+line for line in modifierCodes[0]["Code"].split("\n") ] )
                        outLines.append("\t\t}")
                    # outLines.append(modifierCodes[0]["Code"])
                elif len(modifierCodes) > 1:
                    for modifierCode in modifierCodes:
                        outLines.append("\tif (" + gamepadNumber + modifierCode["Name"] + ".isActive()) {")
                        outLines.extend( [ "\t\t\t"+line for line in modifierCode["Code"].split("\n") ] )
                        outLines.append("\t\t}")

                # if len(modifierCodes) > 0:
                #     if not (len(modifierCodes) == 1 and modifierCodes[0]["Name"] == "Default"):
                #         for modifierCode in modifierCodes:
                #             outLines.append("if (" + modifierCode["Name"] + ".isActive()) {")
                #             outLines.extend( [ "\t"+line+"\n" for line in modifierCode["Code"].split("\n") ] )
                #             outLines.append("}")



                        # if modifierName != "Default":
                        #     outLines.append("if (" + modifierName + ".isActive()) {")
                        # actionCodeLines = self.getAndExpandActionForModifier(mapping, modifierName)
                        # Indent all lines of Action code
                        # actionCodeLines = ["\t"+line for line in actionCodeLines]
                        # for idx, line in enumerate(actionCodeLines):
                        #     actionCodeLines[idx] = "\t" + line
                        #     outLines.append(actionCodeLines[idx])
                        # outLines.extend(actionCodeLines)
                        # if modifierName != "Default":
                        #     outLines.append("}")
                        # mappingsToAdd.append(mapping)

            # Indent all lines of Action code
            # newout = ""
            # for line in out.split("\n"):
            #     newout += "\t"
            #     newout += line
            #     newout += "\n"

            # Expanded line is now many lines; reduce to one line and return
            newout = ""
            for line in outLines:
                newout += line + "\n"
            return newout

        else:
           Common.error("Invalid tag type in this tag from a Method: '" + tag + "'")


    def processMethodNormalTag(self, tag):
        Common.error("Only 'all:' tags are currently supported in Methods.")



    # This takes actions from *Mappings*, not from Libraries!
    def expandActionForModifier(self, mapping, mappingName, modifierName):
        actionName = mapping[modifierName]["Action"]["Name"]
        out = ""

        if actionName in self.libs["BaseActions"]:
            for line in self.libs["BaseActions"][actionName]["Code"]:
                out += self.expandLine(line, "BaseAction", mapping, mappingName, modifierName) + "\n"
        elif actionName in self.libs["ExtensionActions"]:
            for line in self.libs["ExtensionActions"][actionName]["Code"]:
                out += self.expandLine(line, "ExtensionAction", mapping, mappingName, modifierName) + "\n"
        else:
            Common.error("Tried to get code for Action '" + actionName + "' that doesn't seem to exist?")

        return out


    def processBaseActionColonTag(self, tag, mapping, mappingName, modifierName):
        colonIdx = tag.index(":")
        tagType = tag[ : colonIdx ]
        tagContent = tag[ colonIdx+1 : ]

        if tagType == "all":
            Common.error("There seems to be an 'all:' tag outside of a Method, in mapping '" + mappingName + "'.")

        elif tagType == "param":
            parameters = mapping[modifierName]["Action"]["Parameters"]
            if not tagContent in parameters.keys():
                Common.error("Found expander tag for Parameter '" + tagContent + "' in mapping '" + mappingName + "' that doesn't exist in Action '" + mapping["Action"]["Name"] + "'.")
            return str( parameters[tagContent]["Value"] )


    def processBaseActionNormalTag(self, tag, mapping, mappingName, modifierName):
        if tag == "myname":
            return mappingName + modifierName
        else:
            Common.error("Only 'myname' normal tags are currently supported in Actions.")


    def processExtensionActionColonTag(self, tag, mapping, mappingName, modifierName):
        colonIdx = tag.index(":")
        tagType = tag[ : colonIdx ]
        tagContent = tag[ colonIdx+1 : ]

        if tagType == "all":
            Common.error("Found an 'all:' tag in an Extension Action, in mapping '" + mappingName + "' modifier '" + modifierName + "'. You, Library writer, probably meant '<~base:___>'.")

        elif tagType == "base":
            actionCode = self.libs["BaseActions"][tagContent]["Code"]
            expandedLines = []
            for line in actionCode:
                expandedLines.append(self.expandLine(line, "BaseAction", mapping, mappingName, modifierName))
            return "\n".join(expandedLines)

        elif tagType == "param":
            parameters = mapping[modifierName]["Action"]["Parameters"]
            if not tagContent in parameters.keys():
                Common.error("Found expander tag for Parameter '" + tagContent + "' in mapping '" + mappingName + "' that doesn't exist in Action '" + mapping["Action"]["Name"] + "'.")
            return str( parameters[tagContent]["Value"] )

        else:
            Common.error("Unrecognized colon tag type '" + tagType + "' in Extension Action for mapping '" + mappingName + "' modifier '" + modifierName + "'.")


    def processExtensionActionNormalTag(self, tag, mapping, mappingName, modifierName):
        return self.processBaseActionNormalTag(tag, mapping, mappingName, modifierName)



    def processFilePathColonTag(self, tag):
        Common.error("Colon tags not (yet?) supported in file paths.")


    def processFilePathNormalTag(self, tag):
        if tag == "tc":
            return "org.firstinspires.ftc.teamcode"
        else:
            Common.error("Only 'tc' normal tags are currently supported in file paths.")



    def processTemplateColonTag(self, tag):
        Common.error("(internal error! report to a CTL2Java developer) Colon tags not (yet?) supported in templates.")


    def setStateInteriorLines(self, lines):
        self.stateInteriorLines = lines

    def setClassLines(self, lines):
        self.classLines = lines

    def setImportLines(self, lines):
        self.importLines = lines

    def processTemplateNormalTag(self, tag):
        if tag == "tc":
            return "org.firstinspires.ftc.teamcode"
        elif tag == "package":
            return self.expandLine( self.outPackage, "FilePath" )
        elif tag == "className":
            return self.className
        elif tag == "season":
            return self.libs["settersLib"]["Season"]
        elif tag == "seasonInterface":
            return self.expandLine( self.libs["settersLib"]["Interface"], "FilePath" )
        elif tag == "seasonInterfaceClass":
            expanded = self.expandLine( self.libs["settersLib"]["Interface"], "FilePath" )
            split = expanded.split(".")
            return split[-1]
        elif tag == "seasonState":
            return self.expandLine( self.libs["settersLib"]["State"], "FilePath" )
        elif tag == "seasonStateClass":
            expanded = self.expandLine( self.libs["settersLib"]["State"], "FilePath" )
            split = expanded.split(".")
            return split[-1]
        elif tag == "getClassLines":
            if self.classLines:
                return self.classLines
            else:
                Common.error("(internal error! report to a CTL2Java developer) Found <~getClassLines> before it became valid")
        elif tag == "getImportLines":
            if self.importLines:
                # out = ""
                # for line in self.importLines:
                #     out += "import " + self.expandLine( line, "FilePath" ) + ";\n"
                # return out
                return self.importLines
            else:
                Common.error("(internal error! report to a CTL2Java developer) Found <~getImportLines> before it became valid")
        elif tag == "getStateInteriorLines":
            if self.stateInteriorLines:
                return self.stateInteriorLines
            else:
                Common.error("(internal error! report to a CTL2Java developer) Found <~getStateInteriorLines> before it became valid")
        else:
            Common.error("(internal error! report to a CTL2Java developer) Invalid tag '" + tag + "' found in a template.")
