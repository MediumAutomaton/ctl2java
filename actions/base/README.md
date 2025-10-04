Base actions are those which directly map to Setters, and/or directly represent
core Robot actions.
Theoretically these can provide building blocks for Extension actions to build
upon. (How that's going to work out I'm not quite sure yet, though.)

See "strafer.json" as an example of how to write a Base Actions Library.
It'll show you better than I could hope to explain here.

The following expander tags are available for writing Action code:
- <~myname> - The name of the primitive that's currently being mapped
- <~param:[Param]> - The value of Parameter [Param] set in the current Primitive