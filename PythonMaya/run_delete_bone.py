import maya.cmds as cmds
import os
import sys

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Add the directory to Python's path if it's not already there
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Import and run the delete bone module
try:
    # Force reload in case the module was already imported
    if 'deleteselectbone' in sys.modules:
        import importlib
        importlib.reload(sys.modules['deleteselectbone'])
    else:
        import deleteselectbone
    
    # Run the tool
    import deleteselectbone
    deleteselectbone.run()
    
    print("Delete Selected Bone Tool launched successfully!")
except Exception as e:
    cmds.warning("Error launching Delete Selected Bone Tool: {}".format(str(e)))
