import maya.cmds as cmds
import os
import sys

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Add the directory to Python's path if it's not already there
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Import and run the mirror bone module
try:
    # Force reload in case the module was already imported
    if 'mirroringbone' in sys.modules:
        import importlib
        importlib.reload(sys.modules['mirroringbone'])
    else:
        import mirroringbone
    
    # Run the tool
    import mirroringbone
    mirroringbone.run()
    
    print("Mirror Bone Tool launched successfully!")
except Exception as e:
    cmds.warning("Error launching Mirror Bone Tool: {}".format(str(e)))
