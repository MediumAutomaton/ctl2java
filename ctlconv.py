# File last updated 8-23-25

# Convert CTL file to dictionary, verify integrity and fix known bugs from graphical editors
# A rather lenient checker that lets graphical editors hide their own data all over the place if they want to.
# This will just remove anything that CTL2Java doesn't need.
# Uses an unhealthy mix of stuff from assets.py and hard-coded checks.
# To modify the checking, you'll probably have to modify both files.
# TODO: Not quite; there's a few spots that fail when extra keys are present instead of just skipping them. I'd like to change these.

# Big picture outline of what this does:
# - Use json.load() to convert an exported Snap! list to a Python dictionary
# - Thoroughly check the dictionary to make sure it is formatted the way we expect.
#    - Along the way, we'll turn things that should be ints rather than strings into ints.
#    - Along the way, we'll fix any known export bugs from graphical editors

# Remember while reading through this code:
#
# >>> dictionary = {"a": {"b": "c"}, "1": "2"}
# >>> a = dictionary["a"]
# >>> a["b"] = "hello"
# >>> dictionary["a"]["b"]
# "hello"
#
# Try it, it really works!
# If you don't understand references, you might be confused!
#
# If you need a copy instead:
# >>> copiedDict = dictionary.copy()

import json
import traceback
import sys

import assets

class CTLConv:
    def __init__(self, infile, requiredFields):
        self.version = "1.0-0"
        self.infile = infile
        self.requiredFields = requiredFields
        self.convertedDict = {} # just json.load(), for getConverted()
        try:
            self.convertedDict = json.load(infile)
        except:
            self.error("Initial file conversion failed!", True)
        self.outdict = self.convertedDict # outdict will be updated by getVerified()
        self.warnings = []

    # --- Setup ---
    # Define utility methods
    def error(self, msg, exc=False):
        if exc:
            print(msg + " More detailed info. below.")
            print(traceback.format_exc())
        else:
            print(msg)
        sys.exit(1)


    def getConvertedDict(self):
        return self.outdict

    def tryConvert(self, value, type, failMsg):
        if type in ["byte", "short", "int", int, "long"]:
            if not isinstance(value, int):
                try:
                    return int(value)
                except:
                    self.error(failMsg)
        elif type in ["float", float, "double"]:
            if not isinstance(value, float):
                try:
                    return float(value)
                except:
                    self.error(failMsg)
        elif type in ["boolean", bool]:
            if not isinstance(value, bool):
                try:
                    if isinstance(value, str):
                        return value.lower() == "true"
                    else:
                        return bool(value)
                except:
                    self.error(failMsg)
        elif type in ["char", "String" ,str]:
            if not isinstance(value, str):
                try:
                    return str(value)
                except:
                    self.error(failMsg)
        return value # No conversion needed

    # --- Methods used by getVerifiedDict() ---
    def verifyAction(self, buttonName, modifier, action):
        # Action mapping contains correct keys
        for key in assets.actionTypes.keys():
            try:
                action[key] = self.tryConvert(action[key], assets.actionTypes[key], "Failed to convert value for key '" + key + " of Action mapping for Button '" + buttonName + "' modifier '" + modifier + "' to the correct type.")
            except KeyError:
                if key == "Parameters":
                    action.update({"Parameters" : None})
                else:
                    self.error("Malformed Action mapping for Primitive '" + buttonName + "' modifier '" + modifier + "'.")

        # Remove unnecessary keys
        keysToDel = []
        for key in action.keys():
            if not key in assets.actionTypes.keys():
                keysToDel.append(key)
        for key in keysToDel:
            del action[key]

        # Values are of correct types
        for key in action.keys():
            if not isinstance(action[key], assets.actionTypes[key]):
                if not (key == "Parameters" and action[key] == None): # Empty Parameters are OK
                    self.error("Value for key '" + str(key) + "' of Action mapping for Primitive '" + buttonName + "' modifier '" + modifier + "' is of the wrong type.")

        # Verify Parameters
        try:
            parameters = action["Parameters"]
        except KeyError:
            parameters = None
        if parameters:
            for paramName in parameters.keys():
                param = parameters[paramName]

                # Parameter is a dictionary
                if not isinstance(param, dict):
                    self.error("Parameter '" + paramName + "' of Action mapped to Primitive '" + buttonName + "' modifier '" + modifier + "' is not a dictionary.")

                # Parameter contains the correct keys
                for key in assets.parametersTypes.keys():
                    if key not in param.keys():
                        if key == "Range":
                            param.update({"Range" : None})
                        else:
                            self.error("Malformed Parameter '" + paramName + "' of Action mapped to Primitive '" + buttonName + "' modifier '" + modifier + "'.")

                # Type is a valid Java data type
                type = param["Type"]
                if type not in assets.validDataTypes:
                    self.error("Invalid data type for Parameter '" + paramName + "' of Action mapped to Primitive '" + buttonName + "' modifier '" + modifier + "'.")

                # Range is properly formatted
                range = param["Range"]
                fail = False
                if range:
                    if range.count("/") == 1:
                        slashidx = range.index("/")
                        if range[:slashidx].isnumeric() and range[slashidx+1:].isnumeric():
                            fail = False
                        else:
                            fail = True
                    else:
                        fail = True
                if fail:
                    print("Malformed Range for Parameter '" + paramName + "of Action mapped to Primitive '" + buttonName + "' modifier '" + modifier + "'.")

                # Value is of correct type
                failMsg = "Failed to convert Value for Parameter '" + paramName + "of Action mapped to Primitive '" + buttonName + "' modifier '" + modifier + "' to correct type."
                param["Value"] = self.tryConvert(param["Value"], type, failMsg)


    # --- Verify / Fix dict ---
    def getVerifiedDict(self):
        # Setup
        self.warnings = []

        print("Pass 1: Verify Fields Overall")

        fields = list(self.outdict.keys())

        # Have all required fields
        for item in self.requiredFields:
            if not item in fields:
                self.error("Missing required field '" + item + "'.")

        toPop = []
        emptyFields = []
        print("Fields:")
        for idx, field in enumerate(fields):

            # Field is valid
            if not field in assets.validCTLFields:
                toPop.append(idx)
                print("[unrecognized, ignoring] ", end="")

            # Field is not empty
            elif self.outdict[field] in [None, "", [], {}]:
                if field in self.requiredFields:
                    emptyFields.append(field)
                    print("[empty, required, will skip later] ", end="")
                else:
                    toPop.append(idx)
                    print("[empty, skipping] ", end="")

            elif field not in assets.usableCTLFields:
                toPop.append(idx)
                print("[not used by CTL2Java, skipping] ", end="")

            else:
                # Value is of correct type
                if not isinstance(self.outdict[field], assets.ctlFieldTypes[field]):
                    if not (field == "Season" and isinstance(self.outdict[field], list)): # "Season" may be a list
                        self.outdict[field] = self.tryConvert(self.outdict[field], assets.ctlFieldTypes[field], "Value for field '" + str(field) + "' is of wrong type.")

            print(field)
        toPop.reverse() # pop from end to start, otherwise the first pop will make all later indices invalid
        for idx in toPop:
            del self.outdict[fields[idx]]
            fields.pop(idx)

        # After pruning, we still have all required fields
        for item in self.requiredFields:
            if not item in fields:
                self.error("Missing required field '" + item + "'.")

        # Further inspect metadata fields
        version = self.tryConvert(self.outdict["Version"], int, "Failed to convert 'Version' field to int.")
        if version < 1:
            print("That's an interesting version number. I'm not going to try working with this one. Exiting now.")
            sys.exit(1)
        if version > 1:
            print("What's up, future people? Do you know what's up? I don't, but I do know it's not my version number (" + self.version + ")! I don't know what to do with a file this new! You want me to try anyway?")
            user = input("[y/n]")
            if user.lower() in ["y", "yes"]:
                print("Alright! Let's try it...")
            else:
                print("Yeah, let's look for a newer version of me instead. Exiting now.")
                sys.exit(0)

        if "Gamepad" in fields:
            gamepad = self.tryConvert(self.outdict["Gamepad"], int, "Failed to convert 'Gamepad' field to int.")
            if gamepad < 1 or gamepad > 2:
                print("'Gamepad' should be either 1 or 2.")
                sys.exit(1)
        else:
            if "Buttons" in fields or "Axes" in fields:
                self.error("Gamepad mappings must specify which Gamepad they apply to with the 'Gamepad' field!")

        print("Completed Pass 1\n")


        # Pass 2: Verify Modifiers
        print("Pass 2: Verify Modifiers")
        modifiers = []
        if "Modifiers" in fields:
            for modifier in self.outdict["Modifiers"]: # Field type already verified in Pass 1
                if modifier in assets.validButtons:
                    print(modifier)
                    modifiers.append(modifier)
                else:
                    self.error("Invalid modifier '" + str(modifier) + "'.")
        else:
            print("No 'Modifiers' field, so skipping Pass 2\n")


        # Pass 3: Verify Buttons
        print("Pass 3: Verify Buttons")
        if "Buttons" in fields and "Buttons" not in emptyFields:
            buttons = self.outdict["Buttons"]
            buttonsToDel = []
            for idx, buttonName in enumerate(buttons.keys()):

                # Button exists
                # if buttonName not in assets.validButtons:
                #     buttonsToDel.append(buttonName)
                #     print("[unrecognized, ignoring] ", end="")
                if False: # We actually want to allow any Button name, to allow for fake Buttons.
                    pass

                # Button is not already a modifier
                elif buttonName in modifiers: # 'modifiers' was set in Pass 2
                    self.error("Modifier button '" + buttonName + "' should not have Action mappings!")

                else:
                    button = buttons[buttonName]

                    # Button is a dict
                    if not isinstance(button, dict):
                        self.error("Button '" + buttonName + "' is not valid.")

                    # Check modifier mappings
                    buttonModifiers = list(button.keys())
                    modifiersToDel = []
                    for modifier in buttonModifiers:
                        # Modifier is valid
                        if modifier not in (modifiers + ["Default"]):
                            modifiersToDel.append(modifier)
                            print("\t[unusable; that button isn't a modifier] ", end="")
                            self.warnings.append("Button mapping '" + buttonName + "'/'" + str(modifier) + "' is unusable; that button is not mapped as a modifier.")
                        else:
                            # Action mappings are valid
                            mapping = button[modifier]

                            # Mapping is a dict
                            if not isinstance(mapping, dict):
                                self.error("Action mapping for button '" + buttonName + "' modifier '" + modifier + "' is not a dict!")

                            # Mapping contains the correct keys
                            if not mapping.keys() == assets.buttonMappingTypes.keys():
                                self.error("Malformed mapping for button '" + buttonName + "' modifier '" + modifier + "'.")

                            # Values for keys are of correct types
                            for key in assets.buttonMappingTypes.keys():
                                if not isinstance(mapping[key], assets.buttonMappingTypes[key]):

                                    # An empty field here should be None, but Snap! exports it as ""
                                    if mapping[key] == "":
                                        mapping[key] = None

                                    elif mapping[key] != None: # Empty fields are OK, just not malformed ones
                                        # Check for CTLedit 1.0 known bug
                                        if key == "Action" and isinstance(mapping["Action"], list):
                                            action = mapping["Action"]
                                            name = action[0]
                                            action[1].update({"Name" : name})
                                            mapping["Action"] = action[1]
                                        else:
                                            self.error("Value for key '" + str(key) + "' in modifier mapping '" + modifier + "' in button '" + buttonName + "' is of the wrong type.")


                            # Verify Button Type
                            if not mapping["Type"] in assets.validButtonTypes:
                                if mapping["Type"] == "":
                                    modifiersToDel.append(modifier)
                                    warning = "Button '" + buttonName + "' modifier '" + modifier + "' has no Type set and will be ignored."
                                    print(warning)
                                    self.warnings.append(warning)
                                else:
                                    self.error("Invalid Type set for button '" + buttonName + "' modifier '" + modifier + "'.")

                            # Verify Action mapping
                            if action in list[None, "", [], {}]:
                                modifiersToDel.append(modifier)
                                print("Button '" + buttonName + "' modifier '" + modifier + "' has no Action set and will be ignored.")
                            else:
                                self.verifyAction(buttonName, modifier, mapping["Action"])

                        print("\t" + modifier)
                    for key in modifiersToDel:
                        del button[key]
                print(buttonName)
            for key in buttonsToDel:
                del buttons[key]
        else:
            print("'Buttons' field is empty, so skipping Pass 3\n")


        # Pass 4: Verify Axes
        print("Pass 4: Verify Axes")
        if "Axes" in fields and "Axes" not in emptyFields:
            axes = self.outdict["Axes"]
            axesToDel = []
            for idx, axisName in enumerate(axes.keys()):

                # Axis exists
                # if axisName not in assets.validAxes:
                #     axesToDel.append(axisName)
                #     print("[unrecognized, ignoring] ", end="")
                if False: # We actually want to allow any Axis name, to allow for fake / merged Axes.
                    pass

                else:
                    axis = axes[axisName]

                    # Axis is a dict
                    if not isinstance(axis, dict):
                        self.error("Axis '" + axisName + "' is not valid.")

                    # Check modifier mappings
                    axisModifiers = list(axis.keys())
                    modifiersToDel = []
                    for modifier in axisModifiers:
                        # Modifier is valid
                        if modifier not in (modifiers + ["Default"]):
                            modifiersToDel.append(modifier)
                            print("\t[unusable; that button isn't a modifier] ", end="")
                            self.warnings.append("Axis mapping '" + axisName + "'/'" + str(modifier) + "' is unusable; that button is not mapped as a modifier.")
                        else:
                            # Action mappings are valid
                            mapping = axis[modifier]

                            # Mapping is a dict
                            if not isinstance(mapping, dict):
                                self.error("Action mapping for Axis '" + axisName + "' modifier '" + modifier + "' is not a dict!")

                            # Keys exist and their values are of correct types
                            for key in assets.axisMappingTypes.keys():
                                # Key exists
                                try:
                                    temp = mapping[key]
                                except KeyError:
                                    self.error("Malformed mapping for Axis '" + axisName + "' modifier '" + modifier + "'.")

                                if not isinstance(mapping[key], assets.axisMappingTypes[key]):

                                    # An empty field here should be None, but Snap! exports it as ""
                                    if mapping[key] == "":
                                        mapping[key] = None

                                    elif mapping[key] != None: # Empty fields are OK, just not malformed ones
                                        # Check for CTLedit 1.0 known bug
                                        if key == "Action" and isinstance(mapping["Action"], list):
                                            action = mapping["Action"]
                                            name = action[0]
                                            action[1].update({"Name" : name})
                                            mapping["Action"] = action[1]
                                        else:
                                            mapping[key] = self.tryConvert(mapping[key], assets.axisMappingTypes[key], "Failed to convert value for key '" + str(key) + "' in modifier mapping '" + modifier + "' in Axis '" + axisName + "' to the correct type.")


                            # Verify Axis Type
                            if not mapping["Type"] in assets.validAxisTypes:
                                if mapping["Type"] == "":
                                    modifiersToDel.append(modifier)
                                    warning = "Axis '" + axisName + "' modifier '" + modifier + "' has no Type set and will be ignored."
                                    print(warning)
                                    self.warnings.append(warning)
                                else:
                                    self.error("Invalid Type set for Axis '" + axisName + "' modifier '" + modifier + "'.")

                            # Verify Action mapping
                            if mapping["Action"] in [None, "", [], {}]:
                                if modifiersToDel.count(modifier) == 0:
                                    modifiersToDel.append(modifier)
                                warning = "Axis '" + axisName + "' modifier '" + modifier + "' has no Action set and will be ignored."
                                print(warning)
                                self.warnings.append(warning)
                            else:
                                self.verifyAction(axisName, modifier, mapping["Action"])

                        print("\t" + modifier)
                    for key in modifiersToDel:
                        del axis[key]
                print(axisName)
            for key in axesToDel:
                del axes[key]
        else:
            print("'Axes' field is empty, so skipping Pass 4\n")

        # Pass 5: Verify Actions
        if "Actions" in fields and "Actions" not in emptyFields:
            actions = self.outdict["Actions"]
            for actionName in actions.keys():
                action = actions[actionName]

                # Action must be a dict
                if not isinstance(action, dict):
                    self.error("Action '" + actionName + "' is not a dict.")

                # Action has all required fields
                for requiredField in assets.libActionRequiredFields:
                    if not requiredField in action.keys():
                        self.error("Action '" + actionName + "' is missing required field '" + requiredField + "'.")

                # Verify Type (required)
                type = action["Type"]
                if not isinstance(type, str):
                    self.error("'Type' field for Action '" + actionName + "' is not a string.")
                if not type in assets.validLibActionTypes:
                    self.error("'" + type + "' for Action '" + actionName + "' is not a valid Action type!")
                print("Type")

                # Verify Code (required)
                code = action["Code"]
                if not isinstance(code, list):
                    self.error("'Code' field for Action '" + actionName + "' is not a list.")
                for idx, line in enumerate(code):
                    if not isinstance(line, str):
                        self.error("Line [" + str(idx) + "] of Code for Action '" + actionName + "' is not a string.")
                print("Code")

                # Verify Safety Multiplier (optional)
                if "SafetyMultiplier" in action.keys():
                    safeMult = action["SafetyMultiplier"]
                    self.tryConvert(safeMult, float, "'SafetyMultiplier' for Action '" + actionName + "' is not a float.")
                print("SafetyMultiplier")

                # Verify Parameters (optional)
                if "Parameters" in action.keys():
                    parameters = action["Parameters"]
                    if not isinstance(parameters, dict):
                        self.error("'Parameters' for Action '" + actionName + "' is not a dict.")

                    # # Check for required keys
                    # for key in assets.libActionParamFields:
                    #     if not key in parameters.keys():
                    #         self.error("'Parameters' for Action '" + actionName + "' is missing required field '" + key + "'.")
                    #
                    # # Remove unused keys
                    # toDel = []
                    # for key in parameters.keys():
                    #     if key not in assets.libActionParamFields:
                    #         toDel.append(key)
                    #         print("[unrecognized, skipping] ", end="")
                    #     print(key)
                    # for key in toDel:
                    #     del parameters[key]

                    # Verify individual Parameters
                    for paramName in parameters.keys():
                        param = parameters[paramName]

                        # Must be a dict
                        if not isinstance(param, dict):
                            self.error("Parameter '" + paramName + "' of Action '" + actionName + "' is not a dict.")

                        # Check for required keys
                        for key in assets.libActionParamFields:
                            if not key in param.keys():
                                self.error("Parameter '" + paramName + "' of Action '" + actionName + "' is missing required field '" + key + "'.")

                        # Remove extra fields
                        toDel = []
                        for key in param.keys():
                            if not key in assets.libActionParamFields:
                                toDel.append(key)
                                print("[unrecognized, skipping] ", end="")
                            print(key)
                        for key in toDel:
                            del param[key]

                        # Verify fields
                        type = param["Type"]
                        if not isinstance(type, str):
                            self.error("Type of Parameter '" + paramName + "' of Action '" + actionName + "' is not a string.")
                        if not type in assets.validDataTypes:
                            self.error("Type of Parameter '" + paramName + "' of Action '" + actionName + "' is not a valid Java data type.")

                        param["Value"] = self.tryConvert(param["Value"], type.lower(), "Failed to convert Value of Parameter '" + paramName + "' of Action '" + actionName + "' to the correct type.")

                        print(paramName)

                    print("Parameters")

                print(actionName)
        else:
            print("'Actions' field is empty, so skipping Pass 5\n")

        # Pass 6: Verify Methods
        if "Methods" in fields and "Methods" not in emptyFields:
            if not ("Bases" in fields or "Bases" in emptyFields):
                self.error("Method library is missing 'Bases' field.")
            if not ("Extensions" in fields or "Extensions" in emptyFields):
                self.error("Method library is missing 'Extensions' field.")

            methods = self.outdict["Methods"]
            for methodName in methods.keys():
                method = methods[methodName]

                if not isinstance(method, list):
                    self.error("Method '" + methodName + "' is not a list.")

                for idx, line in enumerate(method):
                    if not isinstance(line, str):
                        self.error("Line [" + str(idx) + "] of Method '" + methodName + "' is not a string.")
        else:
            print("'Methods' field is empty, so skipping Pass 6\n")

        # Pass 7: Verify Setters
        if "Setters" in fields and "Setters" not in emptyFields:
            setters = self.outdict["Setters"]
            for idx, line in enumerate(setters):
                if not isinstance(line, str):
                    self.error("Line [" + str(idx) + "] of Setters is not a string.")
        else:
            print("'Setters' field is empty, so skipping Pass 7\n")

        print("\nFile fully converted and verified.")
        if len(self.warnings) > 0:
            print("The following warnings were generated and may negatively affect the output:")
            for warning in self.warnings:
                print(warning)
            print("[end of warnings]")
        return self.outdict