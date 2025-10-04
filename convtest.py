# Test individual Passes of ctlconv.py

import assets
from ctlconv import CTLConv

from argparse import ArgumentParser

argparser = ArgumentParser()
argparser.add_argument("-1", "--overall", help="Pass 1: Verify Fields Overall", action="store_true")
argparser.add_argument("-2", "--modifiers", help="Pass 2: Verify Modifiers", action="store_true")
argparser.add_argument("-3", "--buttons", help="Pass 3: Verify Buttons", action="store_true")
argparser.add_argument("-4", "--axes", help="Pass 4: Verify Axes", action="store_true")
argparser.add_argument("-5", "--actions", help="Pass 5: Verify Actions", action="store_true")
argparser.add_argument("-6", "--methods", help="Pass 6: Verify Methods", action="store_true")
argparser.add_argument("-7", "--setters", help = "Pass 7: Verify Setters", action="store_true")

argparser.add_argument("--file", help="JSON file to test against", action="store")
args = argparser.parse_args()

file = open(args.file)

rF = ["Version", "Season"]
if args.overall:
    pass
if args.modifiers:
    rF.append("Modifiers")
if args.buttons:
    rF.append("Buttons")
    rF.append("Gamepad")
if args.axes:
    if not "Gamepad" in rF:
        rF.append("Gamepad")
    rF.append("Axes")
if args.actions:
    rF.append("Actions")
if args.methods:
    rF.append("Methods")
    rF.append("Bases")
    rF.append("Extensions")
if args.setters:
    rF.append("Setters")
    rF.append("Interface")
    rF.append("State")

conv = CTLConv(file, rF)
assets.prettydict(conv.getVerifiedDict())
