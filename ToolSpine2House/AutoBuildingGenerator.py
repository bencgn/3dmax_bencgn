import os
import sys
import random
import pymxs

rt = pymxs.runtime

try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *

try:
    import qtmax
    HAS_QTMAX = True
except ImportError:
    try:
        import MaxPlus
        HAS_QTMAX = False
    except ImportError:
        HAS_QTMAX = False

class AutoBuildingTool(QWidget):
    def __init__(self, parent=None):
        super(AutoBuildingTool, self).__init__(parent)
        self.setWindowTitle("Auto Generator - Houses Only")
        self.setWindowFlags(Qt.Tool)
        self.resize(350, 500)
        
        self.layer_name = "AutoBuildings_Generated"
        self.generated_nodes_handles = []
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # --- General Settings ---
        group_general = QGroupBox("1. General Plot Settings")
        group_general.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout_general = QFormLayout()
        group_general.setLayout(layout_general)
        
        self.spin_count = QSpinBox()
        self.spin_count.setRange(1, 10000)
        self.spin_count.setValue(100)
        
        self.spin_area_x = QDoubleSpinBox()
        self.spin_area_x.setRange(1.0, 1000000.0)
        self.spin_area_x.setValue(2000.0)
        self.spin_area_x.setDecimals(1)
        self.spin_area_x.setSingleStep(100.0)
        
        self.spin_area_y = QDoubleSpinBox()
        self.spin_area_y.setRange(1.0, 1000000.0)
        self.spin_area_y.setValue(2000.0)
        self.spin_area_y.setDecimals(1)
        self.spin_area_y.setSingleStep(100.0)
        
        layout_general.addRow("House Count:", self.spin_count)
        layout_general.addRow("Scatter Area X:", self.spin_area_x)
        layout_general.addRow("Scatter Area Y:", self.spin_area_y)
        layout.addWidget(group_general)
        
        # --- House Dimensions ---
        group_dims = QGroupBox("2. House Dimensions")
        group_dims.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout_dims = QFormLayout()
        group_dims.setLayout(layout_dims)
        
        self.spin_min_w = QDoubleSpinBox()
        self.spin_min_w.setRange(1.0, 10000.0)
        self.spin_min_w.setValue(20.0)
        
        self.spin_max_w = QDoubleSpinBox()
        self.spin_max_w.setRange(1.0, 10000.0)
        self.spin_max_w.setValue(45.0)
        
        self.spin_min_h = QDoubleSpinBox()
        self.spin_min_h.setRange(1.0, 100000.0)
        self.spin_min_h.setValue(15.0)
        
        self.spin_max_h = QDoubleSpinBox()
        self.spin_max_h.setRange(1.0, 100000.0)
        self.spin_max_h.setValue(50.0)
        
        layout_dims.addRow("House Width Min:", self.spin_min_w)
        layout_dims.addRow("House Width Max:", self.spin_max_w)
        layout_dims.addRow("House Height Min:", self.spin_min_h)
        layout_dims.addRow("House Height Max:", self.spin_max_h)
        layout.addWidget(group_dims)
        
        # --- Architecture details ---
        group_arch = QGroupBox("3. Architecture & Style")
        group_arch.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout_arch = QFormLayout()
        group_arch.setLayout(layout_arch)
        
        self.chk_roofs = QCheckBox("Add Abstract House Roof")
        self.chk_roofs.setChecked(True)
        self.chk_roofs.setToolTip("Creates an abstract roof cap on top of the house base.")
        
        self.combo_rot = QComboBox()
        self.combo_rot.addItems(["None (0°)", "Random 90°", "Random 45°", "Free Random (0-360°)"])
        self.combo_rot.setCurrentIndex(1)
        
        layout_arch.addRow("", self.chk_roofs)
        layout_arch.addRow("Z Rotation:", self.combo_rot)
        layout.addWidget(group_arch)
        
        layout.addStretch()
        
        # --- Actions ---
        btn_generate = QPushButton("Generate Houses")
        btn_generate.setMinimumHeight(40)
        btn_generate.setStyleSheet("font-weight: bold; font-size: 14px; background-color: #4CAF50; color: white; border-radius: 4px;")
        btn_generate.clicked.connect(self.cmd_generate)
        layout.addWidget(btn_generate)
        
        btn_clear = QPushButton("Clear All Generated")
        btn_clear.setMinimumHeight(30)
        btn_clear.setStyleSheet("font-weight: bold; font-size: 12px; background-color: #f44336; color: white; border-radius: 4px;")
        btn_clear.clicked.connect(self.clear_generated)
        layout.addWidget(btn_clear)
        
    def clear_generated(self):
        nodes_to_delete = []
        for handle in self.generated_nodes_handles:
            try:
                node = rt.maxOps.getNodeByHandle(handle)
                if node and rt.isValidNode(node):
                    nodes_to_delete.append(node)
            except:
                pass
                
        if nodes_to_delete:
            for n in nodes_to_delete:
                try:
                    rt.delete(n)
                except:
                    pass
        self.generated_nodes_handles.clear()

    def cmd_generate(self):
        count = self.spin_count.value()
        area_x = self.spin_area_x.value()
        area_y = self.spin_area_y.value()
        
        min_w = self.spin_min_w.value()
        max_w = self.spin_max_w.value()
        min_h = self.spin_min_h.value()
        max_h = self.spin_max_h.value()
        
        add_roofs = self.chk_roofs.isChecked()
        rot_type = self.combo_rot.currentIndex()
        
        if min_w > max_w:
            QMessageBox.warning(self, "Warning", "Min Width cannot be greater than Max Width.")
            return
            
        if min_h > max_h:
            QMessageBox.warning(self, "Warning", "Min Height cannot be greater than Max Height.")
            return

        layer = rt.LayerManager.getLayerFromName(self.layer_name)
        if not layer:
            layer = rt.LayerManager.newLayerFromName(self.layer_name)
            
        rt.disableSceneRedraw()
        try:
            with pymxs.undo(True, "Generate Auto Houses"):
                for i in range(count):
                    # Random position
                    pos_x = random.uniform(-area_x/2.0, area_x/2.0)
                    pos_y = random.uniform(-area_y/2.0, area_y/2.0)
                    
                    # Random dimensions
                    b_width = random.uniform(min_w, max_w)
                    b_length = random.uniform(min_w, max_w)
                    b_height = random.uniform(min_h, max_h)
                    
                    # Create main body
                    main_box = rt.Box(length=b_length, width=b_width, height=b_height)
                    main_box.pos = rt.Point3(pos_x, pos_y, 0)
                    main_box.name = rt.uniqueName("AutoHouse_Main_")
                    layer.addNode(main_box)
                    self.generated_nodes_handles.append(main_box.handle)
                    
                    # Create abstract roof block
                    if add_roofs:
                        if random.random() > 0.3:
                            t_box = rt.Box(length=b_length*0.9, width=b_width*0.9, height=b_height*0.2)
                            t_box.pos = rt.Point3(pos_x, pos_y, b_height)
                            t_box.name = rt.uniqueName("AutoHouse_Roof_")
                            t_box.parent = main_box
                            layer.addNode(t_box)
                            self.generated_nodes_handles.append(t_box.handle)
                    
                    # Apply rotation to root
                    if rot_type > 0:
                        z_rot = 0
                        if rot_type == 1:
                            z_rot = random.choice([0, 90, 180, 270])
                        elif rot_type == 2:
                            z_rot = random.choice([0, 45, 90, 135, 180, 225, 270, 315])
                        elif rot_type == 3:
                            z_rot = random.uniform(0, 360.0)
                            
                        if z_rot != 0:
                            rt.rotate(main_box, rt.EulerAngles(0, 0, z_rot))

                    if i % 20 == 0:
                        QApplication.processEvents()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate houses:\n{str(e)}")
            print(f"Error AutoBldg: {e}")
        finally:
            rt.enableSceneRedraw()
            rt.redrawViews()

def show_tool():
    global autobuilding_window
    
    try:
        if 'autobuilding_window' in globals():
            autobuilding_window.close()
            autobuilding_window.deleteLater()
    except:
        pass

    main_window = None
    if HAS_QTMAX:
        try:
            main_window = qtmax.GetQMaxMainWindow()
        except:
            pass
    else:
        try:
            main_window = MaxPlus.GetQMaxMainWindow()
        except:
            pass
            
    autobuilding_window = AutoBuildingTool(main_window)
    autobuilding_window.show()

if __name__ == "__main__":
    show_tool()
