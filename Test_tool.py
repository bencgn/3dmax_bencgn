import pymxs

# Get a reference to 3ds Max application
max_app = pymxs.runtime.max

# Get the main toolbar
main_toolbar = max_app.getToolBar("Main UI")

# Get the docking panel
dock_panel = main_toolbar.getDockableWindow("Dockable Window Name")

# Dock the panel to the left side of the viewport
dock_panel.dock(pymxs.runtime.dockLeft)
