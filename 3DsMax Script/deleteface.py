"""
Delete Face by Normal Direction
This script deletes faces based on their normal direction along specified axes (X, Y, Z)
"""

try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    try:
        from PySide6 import QtWidgets, QtCore, QtGui
    except ImportError:
        print("Error: Could not load PySide2 or PySide6. Please ensure you are running this in a 3ds Max environment with Python support.")
        raise

from pymxs import runtime as rt

class DeleteFaceByNormalUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(DeleteFaceByNormalUI, self).__init__(parent)
        self.setWindowTitle("Delete Face by Normal Direction")
        self.setMinimumWidth(350)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        
        # Title
        title_label = QtWidgets.QLabel("Delete Faces by Normal Direction")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Description
        desc_label = QtWidgets.QLabel("Select axes to delete faces aligned with those directions:")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("padding: 5px; color: #666;")
        main_layout.addWidget(desc_label)
        
        # Separator
        line1 = QtWidgets.QFrame()
        line1.setFrameShape(QtWidgets.QFrame.HLine)
        line1.setFrameShadow(QtWidgets.QFrame.Sunken)
        main_layout.addWidget(line1)
        
        # Axis Selection Group
        axis_group = QtWidgets.QGroupBox("Axis Direction")
        axis_layout = QtWidgets.QVBoxLayout()
        
        # Checkboxes for each axis
        self.check_x = QtWidgets.QCheckBox("Delete faces with normal aligned to X axis")
        self.check_y = QtWidgets.QCheckBox("Delete faces with normal aligned to Y axis")
        self.check_z = QtWidgets.QCheckBox("Delete faces with normal aligned to Z axis")
        
        self.check_x.setChecked(False)
        self.check_y.setChecked(True)  # Y is default
        self.check_z.setChecked(False)
        
        axis_layout.addWidget(self.check_x)
        axis_layout.addWidget(self.check_y)
        axis_layout.addWidget(self.check_z)
        
        axis_group.setLayout(axis_layout)
        main_layout.addWidget(axis_group)
        
        # Tolerance Settings
        tolerance_group = QtWidgets.QGroupBox("Tolerance Settings")
        tolerance_layout = QtWidgets.QFormLayout()
        
        self.tolerance_spinbox = QtWidgets.QDoubleSpinBox()
        self.tolerance_spinbox.setRange(0.0, 90.0)
        self.tolerance_spinbox.setValue(10.0)
        self.tolerance_spinbox.setSuffix(" degrees")
        self.tolerance_spinbox.setToolTip("Angle tolerance for face normal alignment (0-90 degrees)")
        
        tolerance_layout.addRow("Angle Tolerance:", self.tolerance_spinbox)
        tolerance_group.setLayout(tolerance_layout)
        main_layout.addWidget(tolerance_group)
        
        # Direction Options
        direction_group = QtWidgets.QGroupBox("Direction Options")
        direction_layout = QtWidgets.QVBoxLayout()
        
        self.radio_positive = QtWidgets.QRadioButton("Positive direction (+X, +Y, +Z)")
        self.radio_negative = QtWidgets.QRadioButton("Negative direction (-X, -Y, -Z)")
        self.radio_both = QtWidgets.QRadioButton("Both directions")
        
        self.radio_both.setChecked(True)
        
        direction_layout.addWidget(self.radio_positive)
        direction_layout.addWidget(self.radio_negative)
        direction_layout.addWidget(self.radio_both)
        
        direction_group.setLayout(direction_layout)
        main_layout.addWidget(direction_group)
        
        # Separator
        line2 = QtWidgets.QFrame()
        line2.setFrameShape(QtWidgets.QFrame.HLine)
        line2.setFrameShadow(QtWidgets.QFrame.Sunken)
        main_layout.addWidget(line2)
        
        # Info Label
        self.info_label = QtWidgets.QLabel("")
        self.info_label.setStyleSheet("padding: 5px; color: #0066cc;")
        self.info_label.setWordWrap(True)
        main_layout.addWidget(self.info_label)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.preview_btn = QtWidgets.QPushButton("Preview Selection")
        self.preview_btn.setToolTip("Select faces that will be deleted")
        self.preview_btn.clicked.connect(self.preview_faces)
        
        self.delete_btn = QtWidgets.QPushButton("Delete Faces")
        self.delete_btn.setStyleSheet("background-color: #d9534f; color: white; font-weight: bold;")
        self.delete_btn.setToolTip("Delete selected faces permanently")
        self.delete_btn.clicked.connect(self.delete_faces)
        
        self.close_btn = QtWidgets.QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.preview_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def get_selected_axes(self):
        """Return list of selected axes"""
        axes = []
        if self.check_x.isChecked():
            axes.append('x')
        if self.check_y.isChecked():
            axes.append('y')
        if self.check_z.isChecked():
            axes.append('z')
        return axes
    
    def get_direction_mode(self):
        """Return direction mode: 'positive', 'negative', or 'both'"""
        if self.radio_positive.isChecked():
            return 'positive'
        elif self.radio_negative.isChecked():
            return 'negative'
        else:
            return 'both'
    
    def check_selection(self):
        """Check if valid object is selected"""
        selection = rt.selection
        
        if len(selection) == 0:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select an object first.")
            return None
        
        obj = selection[0]
        
        # Check if object is editable mesh/poly
        if not rt.classOf(obj) == rt.Editable_Poly and not rt.classOf(obj) == rt.Editable_mesh:
            # Try to convert to editable poly
            try:
                rt.convertTo(obj, rt.Editable_Poly)
            except:
                QtWidgets.QMessageBox.warning(self, "Invalid Object", 
                    "Please select an Editable Poly or Editable Mesh object.")
                return None
        
        return obj
    
    def get_faces_to_delete(self, obj):
        """Get list of face indices that match the criteria"""
        axes = self.get_selected_axes()
        
        if not axes:
            QtWidgets.QMessageBox.warning(self, "No Axis Selected", 
                "Please select at least one axis (X, Y, or Z).")
            return []
        
        tolerance = self.tolerance_spinbox.value()
        direction_mode = self.get_direction_mode()
        
        # Convert tolerance to radians for dot product comparison
        import math
        tolerance_rad = math.radians(tolerance)
        min_dot = math.cos(tolerance_rad)
        
        # Use a list to collect face indices, then convert to BitArray
        faces_list = []
        num_faces = rt.polyOp.getNumFaces(obj)
        
        for face_idx in range(1, num_faces + 1):
            # Get face normal
            face_normal = rt.polyOp.getFaceNormal(obj, face_idx)
            
            # Normalize the normal vector
            normal_length = rt.length(face_normal)
            if normal_length > 0:
                face_normal = face_normal / normal_length
            else:
                continue
            
            # Check against each selected axis
            for axis in axes:
                should_delete = False
                
                if axis == 'x':
                    dot_product = abs(face_normal.x)
                    if dot_product >= min_dot:
                        if direction_mode == 'both':
                            should_delete = True
                        elif direction_mode == 'positive' and face_normal.x > 0:
                            should_delete = True
                        elif direction_mode == 'negative' and face_normal.x < 0:
                            should_delete = True
                
                elif axis == 'y':
                    dot_product = abs(face_normal.y)
                    if dot_product >= min_dot:
                        if direction_mode == 'both':
                            should_delete = True
                        elif direction_mode == 'positive' and face_normal.y > 0:
                            should_delete = True
                        elif direction_mode == 'negative' and face_normal.y < 0:
                            should_delete = True
                
                elif axis == 'z':
                    dot_product = abs(face_normal.z)
                    if dot_product >= min_dot:
                        if direction_mode == 'both':
                            should_delete = True
                        elif direction_mode == 'positive' and face_normal.z > 0:
                            should_delete = True
                        elif direction_mode == 'negative' and face_normal.z < 0:
                            should_delete = True
                
                if should_delete:
                    faces_list.append(face_idx)
                    break  # No need to check other axes for this face
        
        return faces_list
    
    def preview_faces(self):
        """Preview which faces will be deleted by selecting them"""
        obj = self.check_selection()
        if not obj:
            return
        
        faces_to_delete = self.get_faces_to_delete(obj)
        
        if not faces_to_delete:
            self.info_label.setText("No faces found matching the criteria.")
            QtWidgets.QMessageBox.information(self, "Preview", "No faces match the selected criteria.")
            return
        
        # Set face selection
        rt.polyOp.setFaceSelection(obj, faces_to_delete)
        
        # Switch to face sub-object mode
        rt.subObjectLevel = 4  # Face level
        
        num_selected = len(faces_to_delete)
        self.info_label.setText(f"Preview: {num_selected} face(s) selected and will be deleted.")
        
        QtWidgets.QMessageBox.information(self, "Preview", 
            f"{num_selected} face(s) have been selected.\nThese faces will be deleted when you click 'Delete Faces'.")
    
    def delete_faces(self):
        """Delete faces based on selected criteria"""
        obj = self.check_selection()
        if not obj:
            return
        
        faces_to_delete = self.get_faces_to_delete(obj)
        
        if not faces_to_delete:
            self.info_label.setText("No faces found matching the criteria.")
            QtWidgets.QMessageBox.information(self, "Delete Faces", "No faces match the selected criteria.")
            return
        
        num_faces = len(faces_to_delete)
        
        # Confirm deletion
        reply = QtWidgets.QMessageBox.question(self, "Confirm Deletion",
            f"Are you sure you want to delete {num_faces} face(s)?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.Yes:
            # Delete the faces
            rt.polyOp.deleteFaces(obj, faces_to_delete)
            
            self.info_label.setText(f"Success! Deleted {num_faces} face(s).")
            
            QtWidgets.QMessageBox.information(self, "Success", 
                f"Successfully deleted {num_faces} face(s).")
            
            # Exit sub-object mode
            rt.subObjectLevel = 0

def show_ui():
    """Show the UI"""
    global delete_face_ui
    
    try:
        delete_face_ui.close()
        delete_face_ui.deleteLater()
    except:
        pass
    
    delete_face_ui = DeleteFaceByNormalUI()
    delete_face_ui.show()

# Run the script
if __name__ == "__main__":
    show_ui()
