try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    try:
        from PySide6 import QtWidgets, QtCore, QtGui
    except ImportError:
        print("Error: Could not load PySide2 or PySide6. Please ensure you are running this in a 3ds Max environment with Python support.")
        raise
from pymxs import runtime as rt

class MaterialCheckerDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MaterialCheckerDialog, self).__init__(parent)
        self.setWindowTitle("Material Checker")
        self.resize(300, 400)
        
        # Data storage
        self.name_to_ids = {}
        self.current_obj = None
        
        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        
        # Prefix Check Section
        prefix_layout = QtWidgets.QHBoxLayout()
        self.edit_prefix = QtWidgets.QLineEdit()
        self.edit_prefix.setPlaceholderText("Enter material name prefix...")
        prefix_layout.addWidget(self.edit_prefix)

        self.btn_check_prefix = QtWidgets.QPushButton("Check Prefix")
        self.btn_check_prefix.clicked.connect(self.check_prefix_materials)
        prefix_layout.addWidget(self.btn_check_prefix)

        self.btn_add_prefix = QtWidgets.QPushButton("Add Prefix")
        self.btn_add_prefix.clicked.connect(self.add_prefix_to_materials)
        prefix_layout.addWidget(self.btn_add_prefix)
        
        layout.addLayout(prefix_layout)

        # Check Button
        self.btn_check = QtWidgets.QPushButton("Check Duplicates")
        self.btn_check.clicked.connect(self.check_materials)
        layout.addWidget(self.btn_check)
        
        # List Widget
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)
        
        # Info Label
        self.lbl_info = QtWidgets.QLabel("Select an object and choose an action.")
        layout.addWidget(self.lbl_info)

    def get_target_object(self):
        selection = rt.selection
        if selection.count == 0:
            self.lbl_info.setText("No object selected.")
            return None

        obj = selection[0]
        
        # Check if editable poly
        if not rt.isKindOf(obj, rt.Editable_Poly):
            self.lbl_info.setText("Selected object is not an Editable Poly.")
            return None
            
        mat = obj.material
        if not mat or not rt.isKindOf(mat, rt.Multimaterial):
            self.lbl_info.setText("No Multi/Sub-Object material found.")
            return None
            
        return obj

    def add_prefix_to_materials(self):
        self.current_obj = self.get_target_object()
        if not self.current_obj:
            return

        prefix = self.edit_prefix.text()
        if not prefix:
            self.lbl_info.setText("Please enter a prefix to add.")
            return
            
        mat = self.current_obj.material
        count = 0
        
        # Start Undo
        # rt.process_undo is not always straightforward in Python, but we can try simple execution or just direct change
        # A simple way for undo in pymxs often involves contexts, but for now we iterate directly.
        # rt.theHold.Begin() ... could simulate undo.
        
        try:
            for i in range(mat.numsubs):
                sub_mat = mat[i]
                if sub_mat:
                    sub_mat.name = prefix + sub_mat.name
                    count += 1
            
            self.lbl_info.setText(f"Added prefix '{prefix}' to {count} materials.")
            # Optional: Refresh list if we were viewing it
            self.list_widget.clear()
            
        except Exception as e:
            self.lbl_info.setText(f"Error renaming: {str(e)}")

    def check_prefix_materials(self):
        self.list_widget.clear()
        self.current_obj = self.get_target_object()
        if not self.current_obj:
            return

        prefix = self.edit_prefix.text()
        if not prefix:
            self.lbl_info.setText("Please enter a prefix.")
            return
            
        self.lbl_info.setText(f"Checking for materials starting with: '{prefix}'")
        
        mat = self.current_obj.material
        found_any = False
        
        for i in range(mat.numsubs):
            sub_mat = mat[i]
            if sub_mat:
                mat_name = sub_mat.name
                if mat_name.startswith(prefix):
                    # Found match
                    current_id = mat.materialIDList[i]
                    
                    # Add to list
                    item_text = f"{mat_name} (ID: {current_id})"
                    item = QtWidgets.QListWidgetItem(item_text)
                    item.setData(QtCore.Qt.UserRole, [current_id]) # Store as list for compatibility
                    self.list_widget.addItem(item)
                    found_any = True
        
        if found_any:
            self.lbl_info.setText(f"Found materials matching prefix '{prefix}'.")
        else:
            self.lbl_info.setText(f"No materials found with prefix '{prefix}'.")

    def check_materials(self):
        self.list_widget.clear()
        self.current_obj = self.get_target_object()
        if not self.current_obj:
            return

        mat = self.current_obj.material
        self.lbl_info.setText(f"Checking duplicates in: {mat.name}")
        
        # Analyze material
        # Map name -> list of IDs
        name_to_ids = {}
        
        for i in range(mat.numsubs):
            sub_mat = mat[i]
            if sub_mat:
                mat_name = sub_mat.name
                current_id = mat.materialIDList[i]
                
                if mat_name not in name_to_ids:
                    name_to_ids[mat_name] = []
                name_to_ids[mat_name].append(current_id)
        
        # Filter duplicates
        found_duplicates = False
        for name, ids in name_to_ids.items():
            if len(ids) > 1:
                item_text = f"{name} (IDs: {ids})"
                item = QtWidgets.QListWidgetItem(item_text)
                # Store data in item
                item.setData(QtCore.Qt.UserRole, ids)
                self.list_widget.addItem(item)
                found_duplicates = True
                
        if found_duplicates:
            self.lbl_info.setText("Found duplicates. Click item to select faces.")
        else:
            self.lbl_info.setText("No duplicate sub-material names found.")

    def on_item_clicked(self, item):
        if not self.current_obj:
            return
            
        ids = item.data(QtCore.Qt.UserRole)
        if not ids:
            return
            
        # Select faces
        try:
            # Switch to Modify panel and Poly mode
            rt.execute("max modify mode")
            rt.subObjectLevel = 4 # Polygon level
            
            target_ids = set(ids)
            num_faces = rt.polyop.getNumFaces(self.current_obj)
            faces_to_select = []
            
            for f in range(1, num_faces + 1):
                mat_id = rt.polyop.getFaceMatID(self.current_obj, f)
                if mat_id in target_ids:
                    faces_to_select.append(f)
            
            if faces_to_select:
                rt.polyop.setFaceSelection(self.current_obj, faces_to_select)
                rt.redrawViews()
                self.lbl_info.setText(f"Selected {len(faces_to_select)} faces for {item.text()}")
            else:
                self.lbl_info.setText("No faces found for these IDs.")
                
        except Exception as e:
            self.lbl_info.setText(f"Error: {str(e)}")
            print(e)

def main():
    # Make sure we don't garbage collect the window immediately 
    # Use a global variable or attach to main window
    global _material_checker_dialog
    try:
        _material_checker_dialog.close()
    except:
        pass
        
    # Get Max Window as parent (optional but good practice)
    # Using simple approach for now, just show()
    _material_checker_dialog = MaterialCheckerDialog()
    _material_checker_dialog.show()

if __name__ == "__main__":
    main()
