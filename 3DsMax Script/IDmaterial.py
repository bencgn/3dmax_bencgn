import sys
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    try:
        from PySide6 import QtWidgets, QtCore, QtGui
    except ImportError:
        print("Error: Could not load PySide2 or PySide6.")
        raise

from pymxs import runtime as rt
import os

def get_prop(mat, prop_names, default=None):
    """Safely gets a property value filtering by case-insensitive and underscore-insensitive matching."""
    try:
        props = rt.getPropNames(mat)
        prop_str_list = [str(p).lower().replace("_", "") for p in props]
    except:
        return default
        
    for p in prop_names:
        target = p.lower().replace("_", "")
        if target in prop_str_list:
            idx = prop_str_list.index(target)
            real_p = str(props[idx])
            try:
                # Dùng getattr để PyMxs tự động convert sang MaxScript access thay vì rt.getProperty
                return getattr(mat, real_p)
            except:
                pass
    return default

def set_prop(mat, prop_names, value):
    """Safely sets a property value filtering by case-insensitive and underscore-insensitive matching."""
    try:
        props = rt.getPropNames(mat)
        prop_str_list = [str(p).lower().replace("_", "") for p in props]
    except:
        return False
        
    for p in prop_names:
        target = p.lower().replace("_", "")
        if target in prop_str_list:
            idx = prop_str_list.index(target)
            real_p = str(props[idx])
            try:
                # Dùng setattr thay vì rt.setProperty
                setattr(mat, real_p, value)
                return True
            except:
                pass
    return False

def get_glTF_tex_name(mat):
    """Gets the base color texture name/path"""
    tex = get_prop(mat, ['baseColorTexture', 'baseColorMap', 'base_color_map'])
    if not tex:
        return "None"
    
    # Try to extract the bitmap path
    if hasattr(tex, 'filename') and tex.filename:
        return os.path.basename(tex.filename)
    elif hasattr(tex, 'bitmap') and tex.bitmap:
        return os.path.basename(tex.bitmap.filename)
    elif hasattr(tex, 'name'):
        return tex.name
    return "Assigned (Unknown Map)"

class GLTFMaterialEditorDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(GLTFMaterialEditorDialog, self).__init__(parent)
        self.setWindowTitle("GlTF Editor fast - v001BCN")
        self.resize(500, 450)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        
        self.current_obj = None
        self.materials_data = [] 
        self.selected_sub_mat = None
        
        # Main Layout
        main_layout = QtWidgets.QHBoxLayout(self)
        
        # == LEFT PANEL (List and Sort) ==
        left_panel = QtWidgets.QVBoxLayout()
        
        self.btn_assign_new = QtWidgets.QPushButton("Assign New glTF Material (#BCBCBC)")
        self.btn_assign_new.setMinimumHeight(40)
        self.btn_assign_new.setStyleSheet("background-color: #555; font-weight: bold; color: white;")
        self.btn_assign_new.clicked.connect(self.assign_new_gltf_material)
        left_panel.addWidget(self.btn_assign_new)
        
        # Add a separator line
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        left_panel.addWidget(line)
        
        self.btn_load = QtWidgets.QPushButton("Load from Selected Object")
        self.btn_load.setMinimumHeight(35)
        self.btn_load.clicked.connect(self.load_materials)
        left_panel.addWidget(self.btn_load)
        
        sort_layout = QtWidgets.QHBoxLayout()
        sort_layout.addWidget(QtWidgets.QLabel("Sort by:"))
        self.combo_sort = QtWidgets.QComboBox()
        self.combo_sort.addItems(["ID (Default)", "Name", "Color"])
        self.combo_sort.currentIndexChanged.connect(self.populate_list)
        sort_layout.addWidget(self.combo_sort)
        left_panel.addLayout(sort_layout)
        
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.itemSelectionChanged.connect(self.on_item_selected)
        left_panel.addWidget(self.list_widget)
        
        main_layout.addLayout(left_panel, 1)
        
        # == RIGHT PANEL (Properties) ==
        right_panel = QtWidgets.QVBoxLayout()
        
        self.group_box = QtWidgets.QGroupBox("glTF Material Properties")
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(12)
        
        # Name
        self.txt_name = QtWidgets.QLineEdit()
        self.txt_name.textChanged.connect(self.on_name_changed)
        form_layout.addRow("Name:", self.txt_name)
        
        # Color
        self.btn_color = QtWidgets.QPushButton()
        self.btn_color.setFixedSize(60, 24)
        self.btn_color.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_color.clicked.connect(self.pick_color)
        form_layout.addRow("Base Color:", self.btn_color)
        
        # Texture Label and Buttons
        texture_layout = QtWidgets.QHBoxLayout()
        self.lbl_texture = QtWidgets.QLabel("None")
        self.lbl_texture.setStyleSheet("color: #aaa; font-style: italic;")
        self.lbl_texture.setWordWrap(True)
        texture_layout.addWidget(self.lbl_texture, 1)
        
        self.btn_assign_tex = QtWidgets.QPushButton("Assign")
        self.btn_assign_tex.setFixedWidth(50)
        self.btn_assign_tex.clicked.connect(self.assign_texture)
        texture_layout.addWidget(self.btn_assign_tex)
        
        self.btn_clear_tex = QtWidgets.QPushButton("Clear")
        self.btn_clear_tex.setFixedWidth(50)
        self.btn_clear_tex.clicked.connect(self.clear_texture)
        texture_layout.addWidget(self.btn_clear_tex)
        
        form_layout.addRow("Texture:", texture_layout)
        
        # Alpha Mode
        self.combo_alpha = QtWidgets.QComboBox()
        self.combo_alpha.addItems(["Opaque", "Mask (Cutoff)", "Blend"])
        self.combo_alpha.currentIndexChanged.connect(self.on_alpha_changed)
        form_layout.addRow("Alpha Mode:", self.combo_alpha)
        
        # Metalness
        self.spin_metal = QtWidgets.QDoubleSpinBox()
        self.spin_metal.setRange(0.0, 1.0)
        self.spin_metal.setSingleStep(0.05)
        self.spin_metal.valueChanged.connect(self.on_metal_changed)
        form_layout.addRow("Metalness:", self.spin_metal)
        
        # Roughness
        self.spin_rough = QtWidgets.QDoubleSpinBox()
        self.spin_rough.setRange(0.0, 1.0)
        self.spin_rough.setSingleStep(0.05)
        self.spin_rough.valueChanged.connect(self.on_rough_changed)
        form_layout.addRow("Roughness:", self.spin_rough)
        
        # Normal
        self.spin_normal = QtWidgets.QDoubleSpinBox()
        self.spin_normal.setRange(0.0, 1.0)
        self.spin_normal.setSingleStep(0.05)
        self.spin_normal.valueChanged.connect(self.on_normal_changed)
        form_layout.addRow("Normal:", self.spin_normal)
        
        # Transmission
        self.chk_transmission = QtWidgets.QCheckBox("Enable Transmission")
        self.chk_transmission.stateChanged.connect(self.on_transmission_changed)
        form_layout.addRow("", self.chk_transmission)
        
        self.group_box.setLayout(form_layout)
        right_panel.addWidget(self.group_box)
        right_panel.addStretch()
        
        main_layout.addLayout(right_panel, 1)
        
        self.updating_ui = False
        self.setEnabled_right_panel(False)
        
    def find_prop_name(self, mat, keyword, expected_types):
        """Find property name containing keyword with a matching type."""
        try:
            for p in rt.getPropNames(mat):
                if keyword in str(p).lower().replace("_", ""):
                    try:
                        val = getattr(mat, str(p))
                        if type(val) in expected_types:
                            return str(p)
                    except:
                        pass
        except:
            pass
        return None
        
    def setEnabled_right_panel(self, enabled):
        self.group_box.setEnabled(enabled)
        
    def load_materials(self):
        self.list_widget.clear()
        self.materials_data = []
        self.selected_sub_mat = None
        self.setEnabled_right_panel(False)
        
        if rt.selection.count == 0:
            return
            
        obj = rt.selection[0]
        self.current_obj = obj
        mat = obj.material
        
        if not mat or getattr(mat, 'numsubs', 0) == 0:
            return
            
        for i in range(mat.numsubs):
            sub_mat = mat[i]
            if sub_mat:
                mat_id = mat.materialIDList[i] if hasattr(mat, 'materialIDList') else i + 1
                color = get_prop(sub_mat, ['baseColorFactor', 'baseColor', 'diffuse'])
                
                hex_color = "#FFFFFF"
                if color:
                    try:
                        hex_color = "#{:02X}{:02X}{:02X}".format(int(color.r), int(color.g), int(color.b))
                    except:
                        pass
                        
                self.materials_data.append({
                    'id': mat_id,
                    'name': sub_mat.name,
                    'color_hex': hex_color,
                    'sub_mat': sub_mat
                })
                
        self.populate_list()
        
    def populate_list(self):
        self.list_widget.clear()
        
        sort_by = self.combo_sort.currentText()
        if "Name" in sort_by:
            self.materials_data.sort(key=lambda x: x['name'].lower())
        elif "Color" in sort_by:
            def sort_col(x):
                c = QtGui.QColor(x['color_hex'])
                return (c.hsvHue(), c.hsvSaturation(), c.value())
            self.materials_data.sort(key=sort_col)
        else: # ID
            self.materials_data.sort(key=lambda x: x['id'])
            
        for data in self.materials_data:
            item_text = f"ID: {data['id']} - {data['name']}"
            item = QtWidgets.QListWidgetItem(item_text)
            try:
                pixmap = QtGui.QPixmap(20, 20)
                pixmap.fill(QtGui.QColor(data['color_hex']))
                icon = QtGui.QIcon(pixmap)
                item.setIcon(icon)
            except:
                pass
            item.setData(QtCore.Qt.UserRole, data)
            self.list_widget.addItem(item)
            
    def on_item_selected(self):
        items = self.list_widget.selectedItems()
        if not items:
            self.setEnabled_right_panel(False)
            self.selected_sub_mat = None
            return
            
        data = items[0].data(QtCore.Qt.UserRole)
        self.selected_sub_mat = data['sub_mat']
        self.update_right_panel()
        
    def update_right_panel(self):
        self.updating_ui = True
        self.setEnabled_right_panel(True)
        mat = self.selected_sub_mat
        
        # Name
        self.txt_name.setText(mat.name)
        
        # Color
        color = get_prop(mat, ['baseColorFactor', 'baseColor', 'diffuse'])
        if color:
            try:
                r, g, b = int(color.r), int(color.g), int(color.b)
                self.btn_color.setStyleSheet(f"background-color: rgb({r},{g},{b}); border: 1px solid #aaa;")
            except:
                self.btn_color.setStyleSheet("background-color: #fff; border: 1px solid #aaa;")
                
        # Texture
        self.lbl_texture.setText(get_glTF_tex_name(mat))
            
        # Alpha Mode (Max is usually 1-based: 1=Opaque, 2=Mask/Cutoff, 3=Blend)
        try:
            alpha_val = get_prop(mat, ['alphaMode'])
            if alpha_val is not None:
                if isinstance(alpha_val, (str, rt.Name)):
                    s = str(alpha_val).lower()
                    if "mask" in s or "cutoff" in s:
                        self.combo_alpha.setCurrentIndex(1)
                    elif "blend" in s or "trans" in s:
                        self.combo_alpha.setCurrentIndex(2)
                    else:
                        self.combo_alpha.setCurrentIndex(0)
                else:
                    m_int = int(alpha_val)
                    ui_idx = m_int - 1 if m_int >= 1 else 0
                    self.combo_alpha.setCurrentIndex(ui_idx if 0 <= ui_idx <= 2 else 0)
            else:
                self.combo_alpha.setCurrentIndex(0)
        except:
            self.combo_alpha.setCurrentIndex(0)
            
        # Metalness
        metal = get_prop(mat, ['metalness', 'metallicFactor', 'metallic'], 0.0)
        self.spin_metal.setValue(float(metal))
        
        # Roughness
        rough = get_prop(mat, ['roughness', 'roughnessFactor'], 0.5)
        self.spin_rough.setValue(float(rough))
        
        # Normal
        normal_val = get_prop(mat, ['normalScale', 'normal_scale', 'normalMapScale', 'normal', 'normal_amount'], 1.0)
        self.spin_normal.setValue(float(normal_val))
        
        # Transmission (Smart finding)
        self.prop_trans_bool = self.find_prop_name(mat, "transmission", [bool])
        self.prop_trans_float = self.find_prop_name(mat, "transmission", [float, int])
        
        if self.prop_trans_bool:
            val = getattr(mat, self.prop_trans_bool)
            self.chk_transmission.setChecked(bool(val))
        elif self.prop_trans_float:
            val = getattr(mat, self.prop_trans_float)
            self.chk_transmission.setChecked(float(val) >= 0.99)
        else:
            self.chk_transmission.setChecked(False)

        self.updating_ui = False
        
    def on_name_changed(self, text):
        if self.updating_ui or not self.selected_sub_mat: return
        self.selected_sub_mat.name = text
        # Update list visually
        items = self.list_widget.selectedItems()
        if items:
            data = items[0].data(QtCore.Qt.UserRole)
            data['name'] = text
            items[0].setText(f"ID: {data['id']} - {text}")
            
    def pick_color(self):
        if not self.selected_sub_mat: return
        
        current_color = get_prop(self.selected_sub_mat, ['baseColorFactor', 'baseColor', 'diffuse'])
        initial_qcolor = QtGui.QColor(255, 255, 255)
        if current_color:
            try:
                initial_qcolor = QtGui.QColor(int(current_color.r), int(current_color.g), int(current_color.b))
            except:
                pass
                
        dlg = QtWidgets.QColorDialog(initial_qcolor, self)
        
        def on_currentColorChanged(c):
            # Live update viewport
            set_prop(self.selected_sub_mat, ['baseColorFactor', 'baseColor', 'diffuse'], rt.Color(c.red(), c.green(), c.blue()))
            self.btn_color.setStyleSheet(f"background-color: {c.name()}; border: 1px solid #aaa;")
            rt.redrawViews()
            
        dlg.currentColorChanged.connect(on_currentColorChanged)
        
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            c = dlg.selectedColor()
            set_prop(self.selected_sub_mat, ['baseColorFactor', 'baseColor', 'diffuse'], rt.Color(c.red(), c.green(), c.blue()))
            self.btn_color.setStyleSheet(f"background-color: {c.name()}; border: 1px solid #aaa;")
            
            items = self.list_widget.selectedItems()
            if items:
                data = items[0].data(QtCore.Qt.UserRole)
                data['color_hex'] = c.name().upper()
                pixmap = QtGui.QPixmap(20, 20)
                pixmap.fill(c)
                items[0].setIcon(QtGui.QIcon(pixmap))
                
            rt.redrawViews()
            
    def on_alpha_changed(self, index):
        if self.updating_ui or not self.selected_sub_mat: return
        
        # Determine if we should set string, or 1-based integer, or 0-based integer
        # Most 3ds Max dropdown properties are 1-based (1=Opaque, 2=Mask, 3=Blend)
        current_val = get_prop(self.selected_sub_mat, ['alphaMode'])
        if isinstance(current_val, (str, rt.Name)):
            val_to_set = ["OPAQUE", "MASK", "BLEND"][index]
        elif isinstance(current_val, int) or isinstance(current_val, float):
            val_to_set = index + 1 if current_val >= 1 else index
        else:
            val_to_set = index + 1 # Default to 1-based for 3ds Max UI
            
        set_prop(self.selected_sub_mat, ['alphaMode'], val_to_set)
        
        # If set to Cutoff (Mask), set alphaCutoff to 0.5 to ensure it actually cuts off
        if index == 1:
            set_prop(self.selected_sub_mat, ['alphaCutoff'], 0.5)
            
        rt.redrawViews()
        
    def on_metal_changed(self, value):
        if self.updating_ui or not self.selected_sub_mat: return
        set_prop(self.selected_sub_mat, ['metalness', 'metallicFactor', 'metallic'], float(value))
        rt.redrawViews()
        
    def on_rough_changed(self, value):
        if self.updating_ui or not self.selected_sub_mat: return
        set_prop(self.selected_sub_mat, ['roughness', 'roughnessFactor'], float(value))
        rt.redrawViews()
        
    def on_normal_changed(self, value):
        if self.updating_ui or not self.selected_sub_mat: return
        set_prop(self.selected_sub_mat, ['normalScale', 'normal_scale', 'normalMapScale', 'normal', 'normal_amount'], float(value))
        rt.redrawViews()
        
    def on_transmission_changed(self, state):
        if self.updating_ui or not self.selected_sub_mat: return
        is_checked = (state == QtCore.Qt.Checked)
        
        # Enable it via smart discovered boolean property
        if getattr(self, 'prop_trans_bool', None):
            setattr(self.selected_sub_mat, self.prop_trans_bool, is_checked)
            
        # Enable via smart discovered float property (1.0 or 0.0)
        if getattr(self, 'prop_trans_float', None):
            setattr(self.selected_sub_mat, self.prop_trans_float, 1.0 if is_checked else 0.0)
        
        rt.redrawViews()
        
    def assign_texture(self):
        if not self.selected_sub_mat: return
        # Mở dialog chọn ảnh
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            "Select Texture", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.tga *.tif *.tiff)"
        )
        if filepath:
            filepath = filepath.replace("\\", "/") # MaxScript an toàn với forward slash
            # Tạo Bitmaptexture
            bmp_tex = rt.Bitmaptexture(filename=filepath)
            
            # Gán vào property thích hợp của glTF
            success = set_prop(self.selected_sub_mat, ['baseColorTexture', 'baseColorMap', 'base_color_map'], bmp_tex)
            
            if success:
                self.lbl_texture.setText(os.path.basename(filepath))
                self.lbl_texture.setStyleSheet("color: palette(window-text); font-style: normal;")
                rt.redrawViews()
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Could not assign texture to this material properties. (Property not found)")

    def clear_texture(self):
        if not self.selected_sub_mat: return
        # Xóa (gán undefined) cho texture map
        success = set_prop(self.selected_sub_mat, ['baseColorTexture', 'baseColorMap', 'base_color_map'], rt.undefined)
        if success:
            self.lbl_texture.setText("None")
            self.lbl_texture.setStyleSheet("color: #aaa; font-style: italic;")
            rt.redrawViews()

    def assign_new_gltf_material(self):
        """Create a new glTF Material with color #BCBCBC and assign to selection."""
        if rt.selection.count == 0:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select at least one object in the viewport.")
            return
            
        try:
            mxs_script = """
            (
                local newMat
                if classOf glTFMaterial != UndefinedClass then (
                    newMat = glTFMaterial()
                    if hasProperty newMat "base_color" do newMat.base_color = color 188 188 188
                    if hasProperty newMat "baseColor" do newMat.baseColor = color 188 188 188
                    if hasProperty newMat "baseColorFactor" do newMat.baseColorFactor = color 188 188 188 
                ) else if classOf PhysicalMaterial != UndefinedClass then (
                    newMat = PhysicalMaterial()
                    if hasProperty newMat "base_color" do newMat.base_color = color 188 188 188
                ) else (
                    newMat = StandardMaterial diffuse:(color 188 188 188)
                )
                newMat.name = "MI_glTF_BCBCBC"
                selection.material = newMat
                
                -- Activate viewport texture display if possible
                for m in selection do (
                    try ( showTextureMap m.material true ) catch()
                )
            )
            """
            rt.execute(mxs_script)
            
            # Reload materials in UI for the new object
            self.load_materials()
            rt.redrawViews()
            
            QtWidgets.QMessageBox.information(self, "Success", "Assigned new glTF Material (#BCBCBC) to selection!")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to assign material: {str(e)}")

def main():
    global _gltf_mat_editor_dialog
    try:
        _gltf_mat_editor_dialog.close()
    except:
        pass
    _gltf_mat_editor_dialog = GLTFMaterialEditorDialog()
    _gltf_mat_editor_dialog.show()

if __name__ == "__main__":
    main()
