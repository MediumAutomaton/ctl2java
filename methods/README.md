A Methods Library provides implementations of methods to set the
controls state's setters.
The code generator will string these together into the generated state.
Not all Method Libraries need to implement all Setters, but all Setters for the
selected Season need to be implemented by Methods. It can be covered by multiple
Method Libraries.
Use Expander tags to get the code lines from Actions that Primitives are
mapped to. More details on this a little later.
Each Method is written as a list of lines. This is a compromise that makes it
relatively easy for the user to write and for the program to handle while
following JSON syntax requirements.

The "Bases" and "Extensions" lists declare the Action Libraries that your Method
Library depends on.

"strafer.json" serves as a good example of how to create a Method Library.

The following Expander tags are available when writing Method code:
- <~all:[Action]> - Include the code snippet for every primitive that [Action]
                    is mapped to

Additionally, use <indy> or <fieldy> in Method names to denote the drive type it
is applicable for. If there's a method for one drive type, there should be one
for the other drive type too!