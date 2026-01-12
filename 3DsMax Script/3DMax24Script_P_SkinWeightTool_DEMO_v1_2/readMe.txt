Thank you for your purchase. This document serves as a detailed introduction and provides precautions for several functions.

P_Scipts~ will be install in the following path c:\Users\<Username>\AppData\Local\Autodesk\3dsMax\<Version>\ENU\scripts\

The "Select Mirror Bone" feature primarily searches for mirror bones by name. If a mirrored bone cannot be identified, the bone closest to the symmetrical position based on their positions is guessed as the mirror. The frame used to check the symmetry of the bone is the Reference Frame, with a default setting of 0 frames. In other words, the bone must be symmetrical at 0 frames to function properly.

The "Next Ring" feature only functions correctly on wireframes where loops are properly listed.

The "Select Bone" feature does not support undo functionality.

Some functions, such as the "Hide" function, can only be used when the Edit Poly and Editable Poly modifiers are present under the Skin modifier.

Please note that not all functions in the Bones tab are guaranteed to be undoable. It's advisable to always create a backup before performing important tasks.

For additional questions and requests, please visit:
https://discord.gg/MUGhNgu
Email: aksmfakt132@gmail.com

-- Updata 

v1.1 : - 'Copy Weights From Closest Vertices' can also be used between different objects
        (It's somewhat slow. This function is used to copy only part of another skin object. To copy the entire thing, use the skin wrap modifier)
        - 'Turn Off Cross Sections' has been enhanced. It's now divided into two buttons instead of using a toggle button
        - Minor Error fixes