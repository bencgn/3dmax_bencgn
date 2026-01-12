import maya.cmds as cmds
import maya.mel as mel
from functools import partial

def expand_all_outliner():
    """
    Function to expand all items in the currently selected Maya Outliner panel.
    """
    # Get all outliner panels
    outliner_panels = cmds.getPanel(type="outlinerPanel")
    
    if not outliner_panels:
        cmds.warning("No Outliner panels found.")
        return
    
    # Use the first outliner panel if multiple exist
    outliner_panel = outliner_panels[0]
    
    # Get the outliner editor from the panel
    outliner_editor = cmds.outlinerPanel(outliner_panel, query=True, outlinerEditor=True)
    
    if not outliner_editor:
        cmds.warning("Could not find Outliner editor.")
        return
    
    # Use MEL command to expand all items in the outliner
    mel.eval('outlinerEditor -edit -expandAllItems true {};'.format(outliner_editor))
    
    print("All items in the Outliner have been expanded.")

def create_menu():
    """
    Create a menu item in the Outliner panel's context menu using MEL.
    """
    # Since we can't directly access the outliner's popup menu through Python,
    # we'll use MEL to create a script job that adds our menu item when the panel is created
    
    # First, create our callback function that will be executed
    mel_cmd = '''
    global proc expandAllOutlinerItems() {
        python("import expan; expan.expand_all_outliner()");
    }
    '''
    mel.eval(mel_cmd)
    
    # Now create a script that adds our menu item to the Outliner panel's menu
    mel_script = '''
    // Add menu item to the Outliner menu
    global proc addExpandAllMenuItem() {
        string $panels[] = `getPanel -type "outlinerPanel"`;
        if (size($panels) > 0) {
            string $panelMenu = `panel -query -popupMenu $panels[0]`;
            if (size($panelMenu) > 0) {
                menuItem -label "Expand All Items" -parent $panelMenu -command "expandAllOutlinerItems";
            }
        }
    }
    
    // Call the function to add the menu item
    addExpandAllMenuItem();
    '''
    
    # Execute the MEL script
    try:
        mel.eval(mel_script)
        print("Menu item added to Outliner context menu.")
    except Exception as e:
        cmds.warning("Failed to add menu item: {}".format(str(e)))

def create_shelf_button():
    """
    Create a button on the current shelf to expand all outliner items.
    """
    # Get the current shelf
    current_shelf = mel.eval('$gShelfTopLevel = $gShelfTopLevel')
    current_shelf_tab = cmds.tabLayout(current_shelf, query=True, selectTab=True)
    
    # Create the button
    cmds.shelfButton(
        parent=current_shelf_tab,
        image="navButtonExpandAll.png",  # Using Maya's built-in expand icon
        label="Expand All Outliner",
        command="import expan; expan.expand_all_outliner()",
        annotation="Expand all items in the Outliner"
    )
    
    print("Shelf button created for expanding all Outliner items.")

def create_ui_window():
    """
    Create a UI window with buttons to expand all items in the Outliner.
    """
    # Check if the window already exists and delete it
    window_name = "expandOutlinerUI"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    
    # Create the window
    window = cmds.window(window_name, title="Outliner Tools", widthHeight=(300, 150))
    
    # Create the main layout
    main_layout = cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=10, columnWidth=300)
    
    # Add a header
    cmds.text(label="Maya Outliner Tools", font="boldLabelFont", height=30)
    cmds.separator(height=10, style="none")
    
    # Add the expand all button
    cmds.button(label="Expand All Items in Outliner", 
               command=lambda x: expand_all_outliner(), 
               height=50,
               backgroundColor=[0.2, 0.6, 0.2])
    
    # Add a separator
    cmds.separator(height=10)
    
    # Add installation buttons
    cmds.frameLayout(label="Installation Options", collapsable=True, collapse=False)
    cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=5)
    
    cmds.button(label="Add to Outliner Menu", 
               command=lambda x: create_menu(), 
               annotation="Add 'Expand All Items' to the Outliner context menu")
    
    cmds.button(label="Add to Current Shelf", 
               command=lambda x: create_shelf_button(), 
               annotation="Add an 'Expand All Outliner' button to the current shelf")
    
    cmds.setParent("..")
    cmds.setParent("..")
    
    # Add help text
    cmds.separator(height=10)
    cmds.text(label="Click the buttons above to expand all items in the Outliner\nor to install the tool for easier access.", align="center")
    
    # Show the window
    cmds.showWindow(window)
    
    return window

# Function to run when the script is imported
def run():
    create_menu()
    create_shelf_button()
    create_ui_window()
    print("Expand All Outliner tool installed. You can access it from:")
    print("- The UI window that just opened")
    print("- The Outliner context menu")
    print("- The shelf button")

# Auto-run when the script is imported
if __name__ == "__main__":
    run()