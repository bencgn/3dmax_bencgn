try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    try:
        from PySide6 import QtWidgets, QtCore, QtGui
    except ImportError:
        print("Error: Could not load PySide2 or PySide6. Please ensure you are running this in a 3ds Max environment with Python support.")
        raise
from pymxs import runtime as rt

class ColorCheckerDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ColorCheckerDialog, self).__init__(parent)
        self.setWindowTitle("Material Color Checker")
        self.resize(400, 550)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        
        # Data storage
        self.current_obj = None
        
        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        
        # Buttons
        btn_layout = QtWidgets.QVBoxLayout()
        
        self.btn_check_same = QtWidgets.QPushButton("Check Same BaseColor")
        self.btn_check_same.setMinimumHeight(40)
        self.btn_check_same.clicked.connect(self.check_same_colors)
        btn_layout.addWidget(self.btn_check_same)
        
        self.btn_list_no_tex = QtWidgets.QPushButton("List Color (No Texture)")
        self.btn_list_no_tex.setMinimumHeight(40)
        self.btn_list_no_tex.clicked.connect(self.list_no_texture_colors)
        btn_layout.addWidget(self.btn_list_no_tex)

        self.btn_prefix_mit = QtWidgets.QPushButton("Add 'MIT_' Prefix (Textured)")
        self.btn_prefix_mit.setMinimumHeight(40)
        self.btn_prefix_mit.clicked.connect(self.add_mit_prefix)
        btn_layout.addWidget(self.btn_prefix_mit)
        
        self.btn_list_all_mtl = QtWidgets.QPushButton("List All Mtl IDs")
        self.btn_list_all_mtl.setMinimumHeight(40)
        self.btn_list_all_mtl.clicked.connect(self.list_all_materials)
        btn_layout.addWidget(self.btn_list_all_mtl)
        
        # Sort Layout
        sort_layout = QtWidgets.QHBoxLayout()
        self.lbl_sort = QtWidgets.QLabel("Sort 'List All' By:")
        self.combo_sort = QtWidgets.QComboBox()
        self.combo_sort.addItems(["ID (Default)", "Name", "Color"])
        self.combo_sort.currentIndexChanged.connect(self.list_all_materials)
        sort_layout.addWidget(self.lbl_sort)
        sort_layout.addWidget(self.combo_sort)
        btn_layout.addLayout(sort_layout)
        
        layout.addLayout(btn_layout)
        
        # List Widget
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self.show_set_id_dialog)
        layout.addWidget(self.list_widget)
        
        # Rename Section
        rename_layout = QtWidgets.QHBoxLayout()
        self.txt_rename = QtWidgets.QLineEdit()
        self.txt_rename.setPlaceholderText("New Material Name...")
        self.btn_rename = QtWidgets.QPushButton("Rename")
        self.btn_rename.clicked.connect(self.rename_material)
        rename_layout.addWidget(self.txt_rename)
        rename_layout.addWidget(self.btn_rename)
        layout.addLayout(rename_layout)
        
        # Info Label
        self.lbl_info = QtWidgets.QLabel("Select an object and choose an action.")
        self.lbl_info.setWordWrap(True)
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

    def get_material_color_hex(self, mat):
        """
        Attempts to get the diffuse/base color and returns it as a HEX string.
        Returns None if color cannot be determined.
        """
        if not mat:
            return None
            
        color = None
        
        # Check for Physical Material
        if rt.isKindOf(mat, rt.PhysicalMaterial):
            color = mat.base_color
        # Check for Standard Material
        elif rt.isKindOf(mat, rt.Standard):
            color = mat.diffuse
        # Check for glTF Material (3ds Max glTF Exporter material)
        # Class names: glTFMaterial or glTF_Material depending on plugin version
        elif hasattr(rt, 'glTFMaterial') and rt.isKindOf(mat, rt.glTFMaterial):
            # baseColorFactor is the Base Color in glTF Material
            if hasattr(mat, 'baseColorFactor'):
                color = mat.baseColorFactor
            elif hasattr(mat, 'baseColor'):
                color = mat.baseColor
        elif hasattr(rt, 'glTF_Material') and rt.isKindOf(mat, rt.glTF_Material):
            if hasattr(mat, 'baseColorFactor'):
                color = mat.baseColorFactor
            elif hasattr(mat, 'baseColor'):
                color = mat.baseColor
        # Generic fallback: check common base color attribute names
        elif hasattr(mat, 'baseColorFactor'):
            color = mat.baseColorFactor
        elif hasattr(mat, 'baseColor'):
            color = mat.baseColor
        # VRay Mtl fallback
        elif hasattr(mat, 'diffuse'): 
             color = mat.diffuse
        
        if color:
            try:
                # 3ds Max color is usually 0-255 RGB
                r = int(color.r)
                g = int(color.g)
                b = int(color.b)
                return "#{:02x}{:02x}{:02x}".format(r, g, b).upper()
            except:
                return None
        return None

    def has_texture(self, mat):
        """
        Checks if the material has a texture map assigned to base color / diffuse.
        """
        if not mat:
            return False
            
        # Physical Material
        if rt.isKindOf(mat, rt.PhysicalMaterial):
            if mat.base_color_map:
                return True
                
        # Standard Material
        elif rt.isKindOf(mat, rt.Standard):
            if mat.diffuseMap:
                return True

        # glTF Material - check baseColorTexture slot
        elif (hasattr(rt, 'glTFMaterial') and rt.isKindOf(mat, rt.glTFMaterial)) or \
             (hasattr(rt, 'glTF_Material') and rt.isKindOf(mat, rt.glTF_Material)):
            if hasattr(mat, 'baseColorTexture') and mat.baseColorTexture:
                return True
            if hasattr(mat, 'baseColor_map') and mat.baseColor_map:
                return True

        # Generic glTF fallback (any plugin exposing these attributes)
        elif hasattr(mat, 'baseColorTexture') and mat.baseColorTexture:
            return True
        elif hasattr(mat, 'baseColor_map') and mat.baseColor_map:
            return True

        # VRay or generic fallback (checking common map slots if attributes exist)
        elif hasattr(mat, 'texmap_diffuse'): # VRayMtl often uses texmap_diffuse
             if mat.texmap_diffuse:
                 return True
                 
        return False

    def check_same_colors(self):
        self.list_widget.clear()
        self.current_obj = self.get_target_object()
        if not self.current_obj:
            return

        mat = self.current_obj.material
        self.lbl_info.setText(f"Checking same BaseColors in: {mat.name} (Object: {self.current_obj.name})")
        
        # Dictionary: HEX -> List of IDs
        hex_map = {}
        
        for i in range(mat.numsubs):
            sub_mat = mat[i]
            # Use materialIDList to get the actual ID (1-based usually, but index is 0-based)
            # Safe way: mat.materialIDList[i]
            if sub_mat:
                hex_color = self.get_material_color_hex(sub_mat)
                current_id = mat.materialIDList[i]
                
                if hex_color:
                    if hex_color not in hex_map:
                        hex_map[hex_color] = []
                    hex_map[hex_color].append(current_id)

        # Populate List
        found_any = False
        for hex_code, ids in hex_map.items():
            if len(ids) > 1: # Only list duplicates? Or group all? User said "list ra mã HEX color", usually implies grouping.
                # Let's list all groups that have valid HEX found, usually intent is to find sharing colors.
                # If "same" implies duplicates only:
                count = len(ids)
                item_text = f"Color: {hex_code} - IDs: {ids} (Count: {count})"
                item = QtWidgets.QListWidgetItem(item_text)
                
                # Set background color icon/hint
                pixmap = QtGui.QPixmap(20, 20)
                pixmap.fill(QtGui.QColor(hex_code))
                icon = QtGui.QIcon(pixmap)
                item.setIcon(icon)
                
                item.setData(QtCore.Qt.UserRole, ids)
                self.list_widget.addItem(item)
                found_any = True
        
        if found_any:
            self.lbl_info.setText("Found materials grouped by BaseColor (showing duplicates/groups).")
        else:
            self.lbl_info.setText("No grouped colors found or materials use textures/unknown types.")

    def list_no_texture_colors(self):
        self.list_widget.clear()
        self.current_obj = self.get_target_object()
        if not self.current_obj:
            return
            
        mat = self.current_obj.material
        self.lbl_info.setText(f"Listing non-textured colors in: {mat.name} (Object: {self.current_obj.name})")
        
        found_any = False
        
        for i in range(mat.numsubs):
            sub_mat = mat[i]
            if sub_mat:
                if not self.has_texture(sub_mat):
                    hex_color = self.get_material_color_hex(sub_mat)
                    if hex_color:
                        current_id = mat.materialIDList[i]
                        
                        item_text = f"ID: {current_id} - Color: {hex_color} - Name: {sub_mat.name}"
                        item = QtWidgets.QListWidgetItem(item_text)
                        
                        # Icon
                        try:
                            pixmap = QtGui.QPixmap(20, 20)
                            pixmap.fill(QtGui.QColor(hex_color))
                            icon = QtGui.QIcon(pixmap)
                            item.setIcon(icon)
                        except:
                            pass
                            
                        item.setData(QtCore.Qt.UserRole, [current_id])
                        self.list_widget.addItem(item)
                        found_any = True
                        
        if found_any:
            self.lbl_info.setText("Listed materials with NO BaseColor Map.")
        else:
            self.lbl_info.setText("All materials have textures or colors could not be determined.")

    def rename_material(self):
        if not self.current_obj:
            return
            
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            self.lbl_info.setText("Please select an item from the list to rename.")
            return
            
        new_name = self.txt_rename.text().strip()
        if not new_name:
            self.lbl_info.setText("Please enter a new name first.")
            return
            
        item = selected_items[0]
        ids = item.data(QtCore.Qt.UserRole)
        if not ids:
            return
            
        target_id = ids[0]
        mat = self.current_obj.material
        if not mat or getattr(mat, 'numsubs', 0) == 0:
            return
            
        for i in range(mat.numsubs):
            if hasattr(mat, 'materialIDList') and i < len(mat.materialIDList):
                mat_id = mat.materialIDList[i]
            else:
                mat_id = i + 1

            if mat_id == target_id:
                sub_mat = mat[i]
                if sub_mat:
                    old_name = sub_mat.name
                    sub_mat.name = new_name
                    self.lbl_info.setText(f"Renamed ID {target_id}: '{old_name}' -> '{new_name}'")
                    
                    # Update item text visually
                    text_parts = item.text().split(" - Name: ")
                    if len(text_parts) == 2:
                        item.setText(f"{text_parts[0]} - Name: {new_name}")
                        
                    # Also update if it was from MIT prefix list
                    elif " -> " in item.text():
                        try:
                            base_text = item.text().split(" -> ")[0]
                            base_first = base_text.split(" - ")[0]
                            item.setText(f"{base_first} - {old_name} -> {new_name}")
                        except:
                            pass
                break

    def get_used_mat_ids(self, obj):
        """
        Returns a set of Material IDs actually used by faces on the given object.
        """
        used_ids = set()
        try:
            num_faces = rt.polyop.getNumFaces(obj)
            for f in range(1, num_faces + 1):
                used_ids.add(rt.polyop.getFaceMatID(obj, f))
        except:
            pass
        return used_ids

    def list_all_materials(self):
        self.list_widget.clear()
        self.current_obj = self.get_target_object()
        if not self.current_obj:
            return
            
        mat = self.current_obj.material
        self.lbl_info.setText(f"Listing all materials in: {mat.name} (Object: {self.current_obj.name})")
        
        # Collect IDs actually used by faces on the object
        used_ids = self.get_used_mat_ids(self.current_obj)
        
        found_any = False
        mat_data_list = []
        
        for i in range(mat.numsubs):
            sub_mat = mat[i]
            if sub_mat:
                current_id = mat.materialIDList[i]
                has_tex = self.has_texture(sub_mat)
                hex_color = self.get_material_color_hex(sub_mat)
                is_used = current_id in used_ids
                
                mat_data_list.append({
                    'id': current_id,
                    'name': sub_mat.name,
                    'has_tex': has_tex,
                    'hex_color': hex_color,
                    'sub_mat': sub_mat,
                    'is_used': is_used
                })
                
        # Get sort criteria
        sort_by = self.combo_sort.currentText()
        if sort_by == "Name":
            mat_data_list.sort(key=lambda x: x['name'].lower())
        elif sort_by == "Color":
            def color_sort_key(x):
                c = x['hex_color']
                if not c:
                    return (1, 0, 0, 0)
                qcolor = QtGui.QColor(c)
                return (0, qcolor.hsvHue(), qcolor.hsvSaturation(), qcolor.value())
            mat_data_list.sort(key=color_sort_key)
        else:
            # Default ID sort
            mat_data_list.sort(key=lambda x: x['id'])

        for data in mat_data_list:
            tex_marker = "T" if data['has_tex'] else " "
            none_marker = "" if data['is_used'] else " [None]"
            color_info = f" - Color: {data['hex_color']}" if data['hex_color'] else ""
            
            item_text = f"[{tex_marker}] ID: {data['id']}{none_marker}{color_info} - Name: {data['name']}"
            item = QtWidgets.QListWidgetItem(item_text)
            
            # Dim color for unused IDs
            if not data['is_used']:
                item.setForeground(QtGui.QColor(160, 160, 160))

            if data['hex_color']:
                try:
                    pixmap = QtGui.QPixmap(20, 20)
                    pixmap.fill(QtGui.QColor(data['hex_color']))
                    icon = QtGui.QIcon(pixmap)
                    item.setIcon(icon)
                except:
                    pass
                    
            item.setData(QtCore.Qt.UserRole, [data['id']])
            self.list_widget.addItem(item)
            found_any = True
                
        if found_any:
            used_count = sum(1 for d in mat_data_list if d['is_used'])
            none_count = len(mat_data_list) - used_count
            self.lbl_info.setText(
                f"Listed all Sub-Materials (Sorted by {sort_by}). "
                f"Used: {used_count} | Unused [None]: {none_count} | "
                f"Double-click to Set ID."
            )
        else:
            self.lbl_info.setText("No Sub-Materials found.")

    def get_selected_faces_mxs(self, obj):
        """
        Read the current face selection directly via pymxs.
        rt.polyop.getFaceSelection returns a MaxScript bitarray;
        iterating it in Python yields the 1-based indices of selected faces.
        """
        try:
            ba = rt.polyop.getFaceSelection(obj)
            # pymxs bitarray: iterating gives 1-based indices of set bits
            faces = [int(f) for f in ba]
            return faces
        except:
            return []


    def show_set_id_dialog(self, item):
        """
        Opens a dialog to set the Material ID using the native
        $.EditablePoly.selectByMaterial / setFacesMaterial MaxScript API.
        This avoids all face-reading issues. The object is put in face
        sub-object mode, faces of target_id are selected, then their
        ID is set to new_id, and the material is assigned as instance.
        """
        if not self.current_obj:
            return
        ids = item.data(QtCore.Qt.UserRole)
        if not ids:
            return
        target_id = ids[0]

        # Build dialog
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Set Material ID")
        dlg.setWindowFlags(dlg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        dlg.resize(360, 180)
        v = QtWidgets.QVBoxLayout(dlg)

        # Info
        mat_name_text = item.text().split(" - Name: ")[-1] if " - Name: " in item.text() else ""
        lbl = QtWidgets.QLabel(
            f"<b>Material:</b> {mat_name_text}<br>"
            f"<b>Source ID:</b> {target_id}<br>"
            f"Will auto-select all faces of ID {target_id} and set to new ID."
        )
        lbl.setWordWrap(True)
        v.addWidget(lbl)

        # Spin box for new ID
        spin_layout = QtWidgets.QHBoxLayout()
        spin_layout.addWidget(QtWidgets.QLabel("Set to ID:"))
        spin_id = QtWidgets.QSpinBox()
        spin_id.setMinimum(1)
        spin_id.setMaximum(9999)
        spin_id.setValue(target_id)
        spin_layout.addWidget(spin_id)
        v.addLayout(spin_layout)

        # Checkbox: assign material as instance to new slot
        chk_instance = QtWidgets.QCheckBox("Also assign material as Instance to new ID slot")
        chk_instance.setChecked(True)
        v.addWidget(chk_instance)

        info_lbl = QtWidgets.QLabel("")
        info_lbl.setWordWrap(True)
        v.addWidget(info_lbl)

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        btn_apply = QtWidgets.QPushButton(f"Apply: Select ID {target_id} Faces → Set New ID")
        btn_cancel = QtWidgets.QPushButton("Cancel")
        btn_layout.addWidget(btn_apply)
        btn_layout.addWidget(btn_cancel)
        v.addLayout(btn_layout)

        def assign_material_instance(new_id):
            """
            Assigns the source sub-material (at target_id slot) as an instance
            into the new_id slot of the Multi/Sub-Object material.
            """
            try:
                multi_mat = self.current_obj.material
                # Find source sub-material
                source_sub = None
                for i in range(multi_mat.numsubs):
                    if multi_mat.materialIDList[i] == target_id:
                        source_sub = multi_mat[i]
                        break

                if source_sub is None:
                    return False, "Source material not found."
                if new_id == target_id:
                    return True, "Same ID, no slot change needed."

                # Find or create new_id slot
                existing_slot_index = None
                for i in range(multi_mat.numsubs):
                    if multi_mat.materialIDList[i] == new_id:
                        existing_slot_index = i
                        break

                if existing_slot_index is not None:
                    multi_mat[existing_slot_index] = source_sub
                else:
                    mxs_cmd = (
                        f"local m = selection[1].material\n"
                        f"local newCount = m.numsubs + 1\n"
                        f"setNumSubMtls m newCount\n"
                        f"m.materialIDList[newCount] = {new_id}\n"
                    )
                    rt.execute(mxs_cmd)
                    new_index = multi_mat.numsubs - 1
                    multi_mat[new_index] = source_sub

                return True, f"Material assigned as instance to slot ID {new_id}."
            except Exception as e:
                return False, str(e)

        def apply_by_material_id():
            new_id = spin_id.value()
            try:
                # 1. Enter modify mode + face sub-object level
                rt.execute("max modify mode")
                rt.subObjectLevel = 4

                # 2. selectByMaterial to select faces, then use polyOp to set ID
                # Wrap in () block so 'local' declarations are valid in MaxScript
                mxs_script = (
                    f"(\n"
                    f"  max modify mode\n"
                    f"  subObjectLevel = 4\n"
                    f"  $.EditablePoly.selectByMaterial {target_id}\n"
                    f"  local ba = polyOp.getFaceSelection $\n"
                    f"  local n = polyOp.getNumFaces $\n"
                    f"  for i = 1 to n do ( if ba[i] do polyOp.setFaceMatID $ i {new_id} )\n"
                    f"  redrawViews()\n"
                    f")\n"
                )
                rt.execute(mxs_script)

                msg = f"Selected faces of ID {target_id} and set to ID {new_id}."

                # 3. Assign material as instance if checked
                if chk_instance.isChecked():
                    ok, inst_msg = assign_material_instance(new_id)
                    msg += f"\nInstance: {inst_msg}"

                info_lbl.setText(msg)
                self.list_all_materials()  # Refresh list
            except Exception as e:
                info_lbl.setText(f"Error: {str(e)}")

        btn_apply.clicked.connect(apply_by_material_id)
        btn_cancel.clicked.connect(dlg.reject)

        dlg.exec()


    def add_mit_prefix(self):
        self.list_widget.clear()
        self.current_obj = self.get_target_object()
        if not self.current_obj:
            return

        mat = self.current_obj.material
        self.lbl_info.setText(f"Checking for textured materials in: {mat.name} (Object: {self.current_obj.name})")
        
        count_renamed = 0
        count_existing = 0
        report_list = []
        
        for i in range(mat.numsubs):
            sub_mat = mat[i]
            if sub_mat:
                # Check if it has texture
                if self.has_texture(sub_mat):
                    current_id = mat.materialIDList[i] # Get ID
                    
                    # Check prefix
                    if not sub_mat.name.startswith("MIT_"):
                        original_name = sub_mat.name
                        sub_mat.name = "MIT_" + original_name
                        count_renamed += 1
                        report_list.append(f"[RENAMED] ID: {current_id} - {original_name} -> {sub_mat.name}")
                    else:
                        count_existing += 1
                        report_list.append(f"[OK] ID: {current_id} - {sub_mat.name}")
                        
        if report_list:
            self.lbl_info.setText(f"Checked textured materials. Renamed: {count_renamed}, Already OK: {count_existing}")
            for item_text in report_list:
                item = QtWidgets.QListWidgetItem(item_text)
                # Visual feedback
                if "[OK]" in item_text:
                     # Greenish for OK
                     item.setBackground(QtGui.QColor(220, 255, 220)) 
                else:
                     # Blueish for modified
                     item.setBackground(QtGui.QColor(220, 240, 255))
                
                # Still add ID data for selection
                # Parse ID from string or just pass it? 
                # Better to store it cleanly. logic above captured current_id
                # But wait, report_list strings have ID.
                # We need to map item back to ID for click selection.
                
                # Let's extract ID from the text or store tuples in report_list
                # Re-parsing: "ID: {current_id} -"
                
                # Better: store data in list
                pass # Just creating item
                
                self.list_widget.addItem(item)
                
                # Add data for selection
                # We need to parse back the ID from the text or better, structure report_list to hold (text, id)
                
                # Let's simple parse:
                try:
                    # simplistic extraction used in loop:
                    # report_list.append(f"[OK] ID: {current_id} - {sub_mat.name}")
                    # regex or split
                    id_part = item_text.split("ID: ")[1].split(" -")[0]
                    item.setData(QtCore.Qt.UserRole, [int(id_part)])
                except:
                    pass
        else:
            self.lbl_info.setText("No textured materials found.")

    def on_item_clicked(self, item):
        if not self.current_obj:
            return
            
        ids = item.data(QtCore.Qt.UserRole)
        if not ids:
            return

        # Auto-fill the rename text box if name is in the item text
        text_parts = item.text().split(" - Name: ")
        if len(text_parts) == 2:
            self.txt_rename.setText(text_parts[1])
        elif " -> " in item.text(): # For the MIT rename list
            name_part = item.text().split(" -> ")[-1]
            self.txt_rename.setText(name_part)
            
        # Select faces
        try:
            # Switch to Modify panel and Poly mode
            rt.execute("max modify mode")
            rt.subObjectLevel = 4 # Polygon level
            
            target_ids = set(ids)
            num_faces = rt.polyop.getNumFaces(self.current_obj)
            faces_to_select = []
            
            # Using bitarray is faster in MaxScript but for simple list logic loop is okay for moderate meshes
            # Optimizing: Getting all face MAT IDs at once if possible
            # rt.polyop.getFaceSelection often returns bitarray
            
            # Iterating 1 to num_poly is slow for huge meshes.
            # But getFaceMatID one by one is what we have unless we write maxscript wrapper.
            # Let's use a slightly faster approach if possible, but loop is safest for Python integration.
            
            for f in range(1, num_faces + 1):
                mat_id = rt.polyop.getFaceMatID(self.current_obj, f)
                if mat_id in target_ids:
                    faces_to_select.append(f)
            
            if faces_to_select:
                rt.polyop.setFaceSelection(self.current_obj, faces_to_select)
                rt.redrawViews()
                self.lbl_info.setText(f"Selected {len(faces_to_select)} faces for IDs {ids}")
            else:
                self.lbl_info.setText("No faces found for these IDs on this object.")
                
        except Exception as e:
            self.lbl_info.setText(f"Error selecting faces: {str(e)}")
            print(e)

def main():
    global _color_checker_dialog
    try:
        _color_checker_dialog.close()
    except:
        pass
        
    _color_checker_dialog = ColorCheckerDialog()
    _color_checker_dialog.show()

if __name__ == "__main__":
    main()
