import pymxs

try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui

rt = pymxs.runtime

class DeleteOverlapFaceUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(DeleteOverlapFaceUI, self).__init__(parent)
        self.setWindowTitle("Delete Overlap Faces Tool")
        self.setWindowFlags(QtCore.Qt.Tool)
        self.resize(320, 150)
        
        # Main layout
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        
        # UI Catalog Label
        catalog_label = QtWidgets.QLabel("1 Delete Overlap")
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        catalog_label.setFont(font)
        catalog_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(catalog_label)
        
        # Instructions
        desc_label = QtWidgets.QLabel("Select mesh/objects and click to delete overlapping faces.")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # Checkbox for 'even flip'
        self.even_flip_cb = QtWidgets.QCheckBox("Delete 2 Face Overlap & Even Flip")
        self.even_flip_cb.setChecked(True)
        self.even_flip_cb.setToolTip("Checkbox: if checked, it will also delete faces that overlap but have flipped/opposite normals.")
        layout.addWidget(self.even_flip_cb)
        
        layout.addSpacing(10)
        
        # Action Button
        self.del_btn = QtWidgets.QPushButton("Click to Delete Face Overlap")
        self.del_btn.setMinimumHeight(40)
        self.del_btn.setStyleSheet("QPushButton { background-color: #d14141; color: white; font-weight: bold; font-size: 14px; border-radius: 5px; } QPushButton:hover { background-color: #e25252; }")
        self.del_btn.clicked.connect(self.run_tool_1)
        layout.addWidget(self.del_btn)
        
        # --- TOOL 2 ---
        
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)
        
        # UI Catalog Label 2
        catalog_label_2 = QtWidgets.QLabel("2 Select Inside Face (Mapping)")
        catalog_label_2.setFont(font)
        catalog_label_2.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(catalog_label_2)
        
        # Instructions 2
        desc_label_2 = QtWidgets.QLabel("Select mesh/objects and tick mapping directions to select inside faces.")
        desc_label_2.setWordWrap(True)
        desc_label_2.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(desc_label_2)
        
        # Checkboxes for Mapping Directions
        mapping_group = QtWidgets.QHBoxLayout()
        
        col1 = QtWidgets.QVBoxLayout()
        self.cb_px = QtWidgets.QCheckBox("+X")
        self.cb_nx = QtWidgets.QCheckBox("-X")
        col1.addWidget(self.cb_px)
        col1.addWidget(self.cb_nx)
        
        col2 = QtWidgets.QVBoxLayout()
        self.cb_py = QtWidgets.QCheckBox("+Y")
        self.cb_ny = QtWidgets.QCheckBox("-Y")
        col2.addWidget(self.cb_py)
        col2.addWidget(self.cb_ny)
        
        col3 = QtWidgets.QVBoxLayout()
        self.cb_pz = QtWidgets.QCheckBox("+Z")
        self.cb_nz = QtWidgets.QCheckBox("-Z")
        self.cb_pz.setChecked(True) # Default check Z
        col3.addWidget(self.cb_pz)
        col3.addWidget(self.cb_nz)
        
        mapping_group.addLayout(col1)
        mapping_group.addLayout(col2)
        mapping_group.addLayout(col3)
        layout.addLayout(mapping_group)
        
        layout.addSpacing(10)
        
        # Action Button 2
        self.sel_btn = QtWidgets.QPushButton("Click to Select Inside Faces")
        self.sel_btn.setMinimumHeight(40)
        self.sel_btn.setStyleSheet("QPushButton { background-color: #4189d1; color: white; font-weight: bold; font-size: 14px; border-radius: 5px; } QPushButton:hover { background-color: #52a2e2; }")
        self.sel_btn.clicked.connect(self.run_tool_2)
        layout.addWidget(self.sel_btn)
        
        # Resize window to fit 2 tools
        self.resize(350, 380)
        
    def run_tool_1(self):
        delete_flipped = self.even_flip_cb.isChecked()
        selection = rt.selection
        
        if not selection:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select at least one object (mesh/editable poly) first.")
            return
            
        with pymxs.undo(True, "Delete Overlap Faces"):
            total_deleted = 0
            processed_count = 0
            
            for obj in selection:
                # Convert to editable poly if needed to use polyop
                is_poly = rt.isKindOf(obj, rt.Editable_Poly)
                if not is_poly:
                    try:
                        rt.convertToPoly(obj)
                    except Exception as e:
                        print("Skipped {}: {}".format(obj.name, str(e)))
                        continue
                
                processed_count += 1
                faces_to_delete = []
                seen_signatures = {}
                
                num_faces = rt.polyOp.getNumFaces(obj)
                
                for i in range(1, num_faces + 1):
                    try:
                        verts = rt.polyOp.getFaceVerts(obj, i)
                        if verts is None:
                            continue
                        
                        # Convert to list to iterate safely
                        verts_list = list(verts)
                    except:
                        continue
                        
                    pos_list = []
                    for v in verts_list:
                        p = rt.polyOp.getVert(obj, v)
                        # Round to 4 decimal places to handle float inaccuracies
                        pos_list.append((round(p.x, 4), round(p.y, 4), round(p.z, 4)))
                    
                    # Create a signature from sorted vertex positions
                    # Sorting makes it ignore the vertex order, so it matches identical shape/position
                    sig = tuple(sorted(pos_list))
                    
                    # Compute normal signature
                    n = rt.polyOp.getFaceNormal(obj, i)
                    # Round normal to 2 decimals for grouping
                    n_sig = (round(n.x, 2), round(n.y, 2), round(n.z, 2))
                    
                    if sig in seen_signatures:
                        # Found overlapping geometry
                        if delete_flipped:
                            # User selected "even flip", delete regardless of normal
                            faces_to_delete.append(i)
                        else:
                            # Verify normal is the same (not flipped inverses)
                            first_n_sig = seen_signatures[sig]
                            if n_sig == first_n_sig:
                                faces_to_delete.append(i)
                    else:
                        seen_signatures[sig] = n_sig
                        
                if faces_to_delete:
                    # Convert python list to maxscript Array
                    mxs_array = rt.Array()
                    for f in faces_to_delete:
                        rt.append(mxs_array, f)
                    
                    # Delete the overlapping faces
                    rt.polyOp.deleteFaces(obj, mxs_array)
                    total_deleted += len(faces_to_delete)
            
            # Redraw viewports to show result
            rt.redrawViews()
            
            # Show result popup
            if total_deleted > 0:
                QtWidgets.QMessageBox.information(self, "Success", "Successfully deleted {} overlapping face(s) across {} object(s).".format(total_deleted, processed_count))
            else:
                QtWidgets.QMessageBox.information(self, "Finished", "No overlapping faces found in the selected object(s).")
                
    def run_tool_2(self):
        selection = rt.selection
        
        if not selection:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select at least one object (mesh/editable poly) first.")
            return
            
        with pymxs.undo(True, "Select Inside Faces"):
            total_selected = 0
            processed_count = 0
            
            for obj in selection:
                # Convert to editable poly if needed
                is_poly = rt.isKindOf(obj, rt.Editable_Poly)
                if not is_poly:
                    try:
                        rt.convertToPoly(obj)
                    except Exception as e:
                        print("Skipped {}: {}".format(obj.name, str(e)))
                        continue
                
                processed_count += 1
                faces_to_select = []
                
                # Get bounding box of the object
                bbox_min = rt.nodeLocalBoundingBox(obj)[0]
                bbox_max = rt.nodeLocalBoundingBox(obj)[1]
                
                # Bounding box dimensions
                # Increase bounding box slightly to start ray from strictly outside
                padding = 10.0
                bbox_min = rt.Point3(bbox_min.x - padding, bbox_min.y - padding, bbox_min.z - padding)
                bbox_max = rt.Point3(bbox_max.x + padding, bbox_max.y + padding, bbox_max.z + padding)
                
                num_faces = rt.polyOp.getNumFaces(obj)
                
                for i in range(1, num_faces + 1):
                    face_center = rt.polyOp.getFaceCenter(obj, i)
                    face_normal = rt.polyOp.getFaceNormal(obj, i)
                    
                    # "Mapping" from an axis means looking from outside the bounding box 
                    # along that axis. If the face is blocked by another face before we 
                    # can see it, it is an "inside" face.
                    
                    is_inside = False
                    
                    # Round normal to avoid float precision issues
                    nx, ny, nz = round(face_normal.x, 2), round(face_normal.y, 2), round(face_normal.z, 2)
                    is_x = abs(nx) > 0.5
                    is_y = abs(ny) > 0.5
                    is_z = abs(nz) > 0.5
                    
                    directions_to_test = []
                    
                    # If mapping +X is checked, look from +X towards the face
                    if self.cb_px.isChecked() and is_x:
                        ray_origin = rt.Point3(bbox_max.x, face_center.y, face_center.z)
                        ray_dir = rt.Point3(-1, 0, 0)
                        directions_to_test.append((ray_origin, ray_dir))
                        
                    if self.cb_nx.isChecked() and is_x:
                        ray_origin = rt.Point3(bbox_min.x, face_center.y, face_center.z)
                        ray_dir = rt.Point3(1, 0, 0)
                        directions_to_test.append((ray_origin, ray_dir))
                        
                    if self.cb_py.isChecked() and is_y:
                        ray_origin = rt.Point3(face_center.x, bbox_max.y, face_center.z)
                        ray_dir = rt.Point3(0, -1, 0)
                        directions_to_test.append((ray_origin, ray_dir))
                        
                    if self.cb_ny.isChecked() and is_y:
                        ray_origin = rt.Point3(face_center.x, bbox_min.y, face_center.z)
                        ray_dir = rt.Point3(0, 1, 0)
                        directions_to_test.append((ray_origin, ray_dir))
                    
                    if self.cb_pz.isChecked() and is_z:
                        ray_origin = rt.Point3(face_center.x, face_center.y, bbox_max.z)
                        ray_dir = rt.Point3(0, 0, -1)
                        directions_to_test.append((ray_origin, ray_dir))
                        
                    if self.cb_nz.isChecked() and is_z:
                        ray_origin = rt.Point3(face_center.x, face_center.y, bbox_min.z)
                        ray_dir = rt.Point3(0, 0, 1)
                        directions_to_test.append((ray_origin, ray_dir))
                        
                    for origin, ray_dir in directions_to_test:
                        # Shoot ray from outside towards the face center
                        test_ray = rt.Ray(origin, ray_dir)
                        hit = rt.intersectRay(obj, test_ray)
                        
                        if hit is not None:
                            # Calculate distance from the mapping origin to the first hit surface
                            dist_to_hit = rt.distance(origin, hit.pos)
                            dist_to_face = rt.distance(origin, face_center)
                            
                            # If the first surface hit is significantly closer than our face's center,
                            # it means our face is blocked / inside another geometry!
                            if dist_to_hit < (dist_to_face - 0.001):
                                is_inside = True
                                break
                            
                    if is_inside:
                        faces_to_select.append(i)
                    
                    if is_inside:
                        faces_to_select.append(i)
                
                if faces_to_select:
                    faces_array = rt.Array()
                    for f in faces_to_select:
                        rt.append(faces_array, f)
                    
                    rt.polyOp.setFaceSelection(obj, faces_array)
                    total_selected += len(faces_to_select)
            
            # Switch to Poly subobject level (Face=4) to see the selection
            if total_selected > 0:
                rt.subobjectLevel = 4
                rt.redrawViews()
                QtWidgets.QMessageBox.information(self, "Success", "Selected {} inside face(s) across {} object(s).".format(total_selected, processed_count))
            else:
                QtWidgets.QMessageBox.information(self, "Finished", "No inside faces found with the checked directions.")

# Global reference to avoid garbage collection
_tool_window = None

def get_main_window():
    try:
        import qtmax
        return qtmax.GetQMaxMainWindow()
    except ImportError:
        try:
            import MaxPlus
            return MaxPlus.GetQMaxMainWindow()
        except:
            return None

def show_ui():
    global _tool_window
    if _tool_window is not None:
        try:
            _tool_window.close()
            _tool_window.deleteLater()
        except:
            pass
            
    _tool_window = DeleteOverlapFaceUI(parent=get_main_window())
    _tool_window.show()

if __name__ == '__main__':
    show_ui()
