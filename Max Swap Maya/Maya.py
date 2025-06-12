"""
Maya Python Script: Send to Max and Get from Max Tool
Save this as a .py file and run in Maya Script Editor or add to shelf
"""

import maya.cmds as cmds
import maya.mel as mel
import os
import datetime
import glob
import subprocess
import platform

class MaxMayaTransfer:
    def __init__(self):
        self.transfer_folder = "C:/temp/"
        self.window_name = "maxMayaTransferWindow"
        
    def ensure_transfer_folder(self):
        """Create transfer folder if it doesn't exist"""
        if not os.path.exists(self.transfer_folder):
            os.makedirs(self.transfer_folder)
    
    def send_to_max(self):
        """Export selected objects as FBX to transfer folder"""
        self.ensure_transfer_folder()
        
        # Check if objects are selected
        selected = cmds.ls(selection=True)
        if not selected:
            cmds.confirmDialog(title="Send to Max", message="Please select objects to send to Max", button=['OK'])
            return
        
        # Generate timestamp for unique filename
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"Maya_to_Max_{timestamp}.fbx"
        filepath = os.path.join(self.transfer_folder, filename).replace("\\", "/")
        
        try:
            # Load FBX plugin if not already loaded
            if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
                cmds.loadPlugin('fbxmaya')
            
            # Set FBX export options
            mel.eval('FBXExportSmoothingGroups -v true')
            mel.eval('FBXExportHardEdges -v false') 
            mel.eval('FBXExportTangents -v false')
            mel.eval('FBXExportSmoothMesh -v true')
            mel.eval('FBXExportInstances -v false')
            mel.eval('FBXExportReferencedAssetsContent -v true')
            
            # Export selected objects
            mel.eval(f'FBXExport -f "{filepath}" -s')
            
            cmds.confirmDialog(
                title="Send to Max", 
                message=f"Objects exported to Max!\nFile: {filename}", 
                button=['OK']
            )
            
        except Exception as e:
            cmds.confirmDialog(
                title="Export Error", 
                message=f"Error exporting FBX file:\n{str(e)}", 
                button=['OK']
            )
    
    def get_from_max(self):
        """Import FBX files from transfer folder"""
        self.ensure_transfer_folder()
        
        # Get all FBX files from transfer folder
        fbx_pattern = os.path.join(self.transfer_folder, "*.fbx").replace("\\", "/")
        fbx_files = glob.glob(fbx_pattern)
        
        if not fbx_files:
            cmds.confirmDialog(
                title="Get from Max", 
                message="No FBX files found in transfer folder", 
                button=['OK']
            )
            return
        
        # Sort by modification time (newest first)
        fbx_files.sort(key=os.path.getmtime, reverse=True)
        
        # If multiple files, show selection dialog
        selected_file = fbx_files[0]  # Default to newest
        
        if len(fbx_files) > 1:
            file_names = [os.path.basename(f) for f in fbx_files]
            result = cmds.layoutDialog(ui=lambda: self.file_selection_ui(file_names))
            if result and result != "Cancel":
                selected_index = int(result) 
                selected_file = fbx_files[selected_index]
            elif result == "Cancel":
                return
        
        try:
            # Load FBX plugin if not already loaded
            if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
                cmds.loadPlugin('fbxmaya')
            
            # Import the selected FBX file
            mel.eval(f'FBXImport -f "{selected_file.replace(chr(92), "/")}"')
            
            filename = os.path.basename(selected_file)
            cmds.confirmDialog(
                title="Get from Max", 
                message=f"FBX file imported successfully!\nFile: {filename}", 
                button=['OK']
            )
            
        except Exception as e:
            cmds.confirmDialog(
                title="Import Error", 
                message=f"Error importing FBX file:\n{str(e)}", 
                button=['OK']
            )
    
    def file_selection_ui(self, file_names):
        """UI for selecting which file to import"""
        form = cmds.setParent(q=True)
        cmds.formLayout(form, edit=True, width=400)
        
        # Title
        title = cmds.text(label="Select FBX file to import:", align="center", height=30)
        
        # File list
        file_list = cmds.textScrollList(
            numberOfRows=8,
            allowMultiSelection=False,
            append=file_names,
            selectIndexedItem=1
        )
        
        # Buttons
        import_btn = cmds.button(label="Import", command=lambda x: self.return_selection(file_list))
        cancel_btn = cmds.button(label="Cancel", command=lambda x: cmds.layoutDialog(dismiss="Cancel"))
        
        # Layout
        cmds.formLayout(form, edit=True,
            attachForm=[(title, 'top', 10), (title, 'left', 10), (title, 'right', 10),
                       (file_list, 'left', 10), (file_list, 'right', 10),
                       (import_btn, 'left', 10), (import_btn, 'bottom', 10),
                       (cancel_btn, 'right', 10), (cancel_btn, 'bottom', 10)],
            attachControl=[(file_list, 'top', 5, title),
                          (file_list, 'bottom', 10, import_btn),
                          (cancel_btn, 'left', 10, import_btn)],
            attachPosition=[(import_btn, 'right', 5, 50)]
        )
    
    def return_selection(self, file_list):
        """Return selected file index"""
        selection = cmds.textScrollList(file_list, query=True, selectIndexedItem=True)
        if selection:
            cmds.layoutDialog(dismiss=str(selection[0] - 1))
        else:
            cmds.layoutDialog(dismiss="0")
    
    def open_transfer_folder(self):
        """Open the transfer folder in file explorer"""
        self.ensure_transfer_folder()
        
        if platform.system() == "Windows":
            os.startfile(self.transfer_folder)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", self.transfer_folder])
        else:  # Linux
            subprocess.call(["xdg-open", self.transfer_folder])
    
    def create_ui(self):
        """Create the main UI window"""
        # Delete existing window if it exists
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
        
        # Create window
        window = cmds.window(
            self.window_name,
            title="Maya ↔ Max Transfer",
            widthHeight=(320, 200),
            resizeToFitChildren=True
        )
        
        # Main layout
        main_layout = cmds.columnLayout(adjustableColumn=True, columnAttach=('both', 15), rowSpacing=10)
        
        # Title
        cmds.text(label="Transfer FBX between Maya and Max", align="center", font="boldLabelFont")
        cmds.text(label=f"Folder: {self.transfer_folder}", align="center")
        
        cmds.separator(height=10, style='in')
        
        # Main buttons
        cmds.button(
            label="Send to Max", 
            height=40, 
            backgroundColor=[0.4, 0.6, 0.4],
            command=lambda x: self.send_to_max()
        )
        
        cmds.button(
            label="Get from Max", 
            height=40, 
            backgroundColor=[0.4, 0.4, 0.6],
            command=lambda x: self.get_from_max()
        )
        
        cmds.separator(height=10, style='in')
        
        # Utility buttons
        button_layout = cmds.rowLayout(numberOfColumns=2, columnWidth2=[150, 150])
        cmds.button(
            label="Open Transfer Folder", 
            command=lambda x: self.open_transfer_folder()
        )
        cmds.button(
            label="Refresh", 
            command=lambda x: self.refresh_ui()
        )
        
        cmds.showWindow(window)
        return window
    
    def refresh_ui(self):
        """Refresh the UI"""
        print("Transfer tool refreshed")

# Quick functions that can be called directly or added to shelf
def quick_send_to_max():
    """Quick send function for shelf button"""
    transfer = MaxMayaTransfer()
    transfer.send_to_max()

def quick_get_from_max():
    """Quick get function for shelf button"""
    transfer = MaxMayaTransfer()
    transfer.get_from_max()

def show_transfer_ui():
    """Show the transfer UI"""
    transfer = MaxMayaTransfer()
    transfer.create_ui()

# Run the UI when script is executed
if __name__ == "__main__":
    show_transfer_ui()

# For adding to Maya shelf, use these commands:
"""
# Send to Max shelf button:
import maya.cmds as cmds
cmds.shelfButton(
    command='quick_send_to_max()',
    annotation='Send selected objects to 3ds Max',
    image='out_polyUnite.png',
    label='→Max'
)

# Get from Max shelf button:  
cmds.shelfButton(
    command='quick_get_from_max()',
    annotation='Get objects from 3ds Max',
    image='in_polyUnite.png', 
    label='Max→'
)
"""