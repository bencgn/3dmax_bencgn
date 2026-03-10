import os
import sys
import random
import pymxs

rt = pymxs.runtime

# PySide Compatibility handling across different 3ds Max versions (2021+)
try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *

# Window Management specific to 3ds Max
try:
    import qtmax
    HAS_QTMAX = True
except ImportError:
    try:
        import MaxPlus
        HAS_QTMAX = False
    except ImportError:
        HAS_QTMAX = False


class Spine2HouseTool(QWidget):
    def __init__(self, parent=None):
        super(Spine2HouseTool, self).__init__(parent)
        self.setWindowTitle("Spline to House Generator")
        self.setWindowFlags(Qt.Tool)
        self.resize(380, 500)
        
        self.spline_node_handle = None
        self.house_nodes_handles = []
        self.generated_nodes_handles = []
        self.layer_name = "Spine2House_Generated"
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # --- House Objects ---
        group_houses = QGroupBox("1. Select House / Building Objects")
        group_houses.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout_houses = QVBoxLayout()
        group_houses.setLayout(layout_houses)
        
        self.list_houses = QListWidget()
        self.list_houses.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_houses.setToolTip("Objects to be instanced randomly along the spline.")
        layout_houses.addWidget(self.list_houses)
        
        hlayout_house_btns = QHBoxLayout()
        btn_add_house = QPushButton("Add Selected")
        btn_add_house.clicked.connect(self.cmd_add_houses)
        
        btn_rm_house = QPushButton("Remove Selected")
        btn_rm_house.clicked.connect(self.cmd_remove_houses)
        
        btn_clear_house = QPushButton("Clear All")
        btn_clear_house.clicked.connect(self.cmd_clear_houses)
        
        hlayout_house_btns.addWidget(btn_add_house)
        hlayout_house_btns.addWidget(btn_rm_house)
        hlayout_house_btns.addWidget(btn_clear_house)
        layout_houses.addLayout(hlayout_house_btns)
        layout.addWidget(group_houses)
        
        # --- Spline Path ---
        group_spline = QGroupBox("2. Select Target Spline Path")
        group_spline.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout_spline = QVBoxLayout()
        group_spline.setLayout(layout_spline)
        
        self.lbl_spline = QLabel("Selected Spline: None")
        self.lbl_spline.setWordWrap(True)
        layout_spline.addWidget(self.lbl_spline)
        
        btn_pick_spline = QPushButton("Get Selected Spline (1 Object)")
        btn_pick_spline.clicked.connect(self.cmd_pick_spline)
        layout_spline.addWidget(btn_pick_spline)
        layout.addWidget(group_spline)
        
        # --- Settings ---
        group_settings = QGroupBox("3. Placement Settings")
        group_settings.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout_settings = QFormLayout()
        group_settings.setLayout(layout_settings)
        
        # Min Distance spinbox
        self.spin_min_dist = QDoubleSpinBox()
        self.spin_min_dist.setRange(0.01, 1000000.0)
        self.spin_min_dist.setValue(20.0)
        self.spin_min_dist.setDecimals(3)
        self.spin_min_dist.setSingleStep(1.0)
        
        # Max Distance spinbox
        self.spin_max_dist = QDoubleSpinBox()
        self.spin_max_dist.setRange(0.01, 1000000.0)
        self.spin_max_dist.setValue(50.0)
        self.spin_max_dist.setDecimals(3)
        self.spin_max_dist.setSingleStep(1.0)
        
        # Rotation Combo Box
        self.combo_rot = QComboBox()
        self.combo_rot.addItems(["None", "Random 90° Steps", "Random 45° Steps", "Free Random (0-360°)"])
        
        # Align Checkbox
        self.chk_align = QCheckBox("Align to Spline Tangent")
        self.chk_align.setChecked(True)
        
        layout_settings.addRow("Min Distance:", self.spin_min_dist)
        layout_settings.addRow("Max Distance:", self.spin_max_dist)
        layout_settings.addRow("Random Z Rotation:", self.combo_rot)
        layout_settings.addRow("", self.chk_align)
        layout.addWidget(group_settings)
        
        layout.addStretch()
        
        # --- Actions ---
        btn_generate = QPushButton("Update / Generate Layout")
        btn_generate.setMinimumHeight(40)
        btn_generate.setStyleSheet("font-weight: bold; font-size: 14px; background-color: #4CAF50; color: white; border-radius: 4px;")
        btn_generate.clicked.connect(self.cmd_generate)
        layout.addWidget(btn_generate)
        
        btn_clear_layout = QPushButton("Clear Generated Layout")
        btn_clear_layout.setMinimumHeight(30)
        btn_clear_layout.setStyleSheet("font-weight: bold; font-size: 12px; background-color: #f44336; color: white; border-radius: 4px;")
        btn_clear_layout.clicked.connect(self.clear_generated_nodes)
        layout.addWidget(btn_clear_layout)
        
        btn_combine = QPushButton("Combine Generated to 1 Mesh")
        btn_combine.setMinimumHeight(30)
        btn_combine.setStyleSheet("font-weight: bold; font-size: 12px; background-color: #2196F3; color: white; border-radius: 4px;")
        btn_combine.clicked.connect(self.cmd_combine)
        layout.addWidget(btn_combine)
        
        # --- Progress Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid grey; border-radius: 4px; text-align: center; } QProgressBar::chunk { background-color: #4CAF50; width: 10px; margin: 0.5px; }")
        layout.addWidget(self.progress_bar)
        
    def cmd_add_houses(self):
        sel = rt.selection
        if not sel:
            QMessageBox.warning(self, "Warning", "No objects selected in the scene.\nPlease select objects to add as houses.")
            return
        
        added = 0
        for node in sel:
            # check if it's already in the list
            if node.handle not in self.house_nodes_handles:
                self.house_nodes_handles.append(node.handle)
                self.list_houses.addItem(f"{node.name} (ID: {node.handle})")
                added += 1
                
        if added > 0:
            print(f"Added {added} objects to the house list.")
                
    def cmd_remove_houses(self):
        selected_items = self.list_houses.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            row = self.list_houses.row(item)
            self.list_houses.takeItem(row)
            if row < len(self.house_nodes_handles):
                self.house_nodes_handles.pop(row)
                
    def cmd_clear_houses(self):
        self.list_houses.clear()
        self.house_nodes_handles.clear()
        
    def cmd_pick_spline(self):
        sel = rt.selection
        if not sel or len(sel) > 1:
            QMessageBox.warning(self, "Warning", "Please select exactly ONE Spline/Line object.")
            return
            
        node = sel[0]
        if not rt.isKindOf(node, rt.Shape): # Shape and Line are valid
            QMessageBox.warning(self, "Warning", f"Selected object '{node.name}' is not a valid Shape/Spline.")
            return
            
        self.spline_node_handle = node.handle
        self.lbl_spline.setText(f"Selected Spline: {node.name}")
        self.lbl_spline.setStyleSheet("color: #4CAF50; font-weight: bold;")
        print(f"Target Spline Set: {node.name}")
        
    def clear_generated_nodes(self):
        nodes_to_delete = []
        for handle in self.generated_nodes_handles:
            try:
                node = rt.maxOps.getNodeByHandle(handle)
                if node and rt.isValidNode(node):
                    nodes_to_delete.append(node)
            except Exception as e:
                print(f"Failed to find node to delete: {e}")
                
        if nodes_to_delete:
            for n in nodes_to_delete:
                try:
                    rt.delete(n)
                except:
                    pass
                    
        self.generated_nodes_handles.clear()
        
    def cmd_combine(self):
        if not self.generated_nodes_handles:
            QMessageBox.information(self, "Info", "There are no generated objects to combine.")
            return
            
        nodes_to_combine = []
        for handle in self.generated_nodes_handles:
            try:
                node = rt.maxOps.getNodeByHandle(handle)
                if node and rt.isValidNode(node):
                    nodes_to_combine.append(node)
            except:
                pass
                
        if not nodes_to_combine:
            self.generated_nodes_handles.clear()
            QMessageBox.information(self, "Info", "Valid generated objects no longer exist.")
            return
            
        # Optional: Disable scene redraw during intensive operations
        rt.disableSceneRedraw()
        try:
            with pymxs.undo(True, "Combine Spine2House"):
                # Take the first object and use it as base
                base_mesh = nodes_to_combine[0]
                rt.convertTo(base_mesh, rt.Editable_Poly)
                base_mesh.name = rt.uniqueName("SpineHouse_Combined_")
                
                total_nodes = len(nodes_to_combine) - 1
                if total_nodes > 0:
                    self.progress_bar.setRange(0, total_nodes)
                    self.progress_bar.setValue(0)
                    
                    # Attach the rest
                    for i in range(1, len(nodes_to_combine)):
                        node = nodes_to_combine[i]
                        # We might need to convert it to poly first or just attach
                        rt.polyop.attach(base_mesh, node)
                        
                        self.progress_bar.setValue(i)
                        if i % 10 == 0:
                            QApplication.processEvents()
                            
                    self.progress_bar.setValue(total_nodes)
                            
                self.generated_nodes_handles = [base_mesh.handle] # It becomes the only generated node
                QMessageBox.information(self, "Success", f"Successfully combined into {base_mesh.name}.")
                
                # reset progress
                self.progress_bar.setValue(0)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during combine:\n{str(e)}")
            print(f"Error Spine2House Combine: {e}")
        finally:
            rt.enableSceneRedraw()
            rt.redrawViews()

    def cmd_generate(self):
        if not self.house_nodes_handles:
            QMessageBox.warning(self, "Warning", "Please add at least one House/Building object to the list.")
            return
            
        if self.spline_node_handle is None:
            QMessageBox.warning(self, "Warning", "Please select a target Spline path.")
            return
            
        spline_node = rt.maxOps.getNodeByHandle(self.spline_node_handle)
        if not spline_node or not rt.isValidNode(spline_node):
            QMessageBox.warning(self, "Warning", "The targeted Spline no longer exists. Please pick it again.")
            self.spline_node_handle = None
            self.lbl_spline.setText("Selected Spline: None")
            self.lbl_spline.setStyleSheet("")
            return
            
        valid_houses = []
        for handle in self.house_nodes_handles:
            node = rt.maxOps.getNodeByHandle(handle)
            if node and rt.isValidNode(node):
                valid_houses.append(node)
                
        if not valid_houses:
            QMessageBox.warning(self, "Warning", "The House objects in the list are no longer valid (deleted in scene). Please clear and re-add them.")
            return

        min_dist = self.spin_min_dist.value()
        max_dist = self.spin_max_dist.value()
        rot_type = self.combo_rot.currentIndex()
        align_to_path = self.chk_align.isChecked()
        
        if min_dist > max_dist:
            QMessageBox.warning(self, "Warning", "Min Distance cannot be greater than Max Distance.")
            return
        
        # Create/Get Layer to store instances and keep scene clean
        layer = rt.LayerManager.getLayerFromName(self.layer_name)
        if not layer:
            layer = rt.LayerManager.newLayerFromName(self.layer_name)
            
        # Optional: Disable scene redraw during intensive operations
        rt.disableSceneRedraw()
        try:
            with pymxs.undo(True, "Generate Spine2House Layout"):
                self.clear_generated_nodes()
                
                num_curves = rt.numSplines(spline_node)
                
                # Initial progress setup
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(0)
                
                for curve_idx in range(1, num_curves + 1):
                    try:
                        total_length = rt.curveLength(spline_node, curve_idx)
                    except Exception as e:
                        print(f"Error reading curve {curve_idx} length: {e}")
                        continue
                        
                    current_dist = 0.0
                    while current_dist <= total_length:
                        pct = current_dist / total_length
                        if pct > 1.0:
                            pct = 1.0
                            
                        # Get Pos and Tangent
                        pos = rt.lengthInterp(spline_node, curve_idx, pct)
                        
                        # Selection of house
                        house_source = random.choice(valid_houses)
                        # Create instance via maxscript
                        inst = rt.instance(house_source)
                        # Tag with a name prefix
                        inst.name = rt.uniqueName("SpineHouse_")
                        inst.wirecolor = rt.Color(0, 0, 255) # Blue wirecolor
                        
                        if align_to_path:
                            try:
                                tangent = rt.lengthTangent(spline_node, curve_idx, pct)
                                front = rt.normalize(tangent)
                                up = rt.Point3(0, 0, 1) # World Z Up
                                
                                # Handle Gimbal Lock if path goes straight up/down
                                dot_prod = abs(rt.dot(front, up))
                                if dot_prod > 0.999: 
                                    up = rt.Point3(0, 1, 0)
                                    
                                right = rt.normalize(rt.cross(up, front))
                                up2 = rt.normalize(rt.cross(front, right))
                                
                                # Matrix3(row1=Right, row2=Front(Y), row3=Up(Z), row4=Pos)
                                tm = rt.Matrix3(right, front, up2, pos)
                                
                                # Apply Random Rotation
                                if rot_type > 0:
                                    z_rot = 0
                                    if rot_type == 1:
                                        z_rot = random.choice([0, 90, 180, 270])
                                    elif rot_type == 2:
                                        z_rot = random.choice([0, 45, 90, 135, 180, 225, 270, 315])
                                    elif rot_type == 3:
                                        z_rot = random.uniform(0, 360.0)
                                    if z_rot != 0:
                                        tm = rt.preRotateZ(tm, z_rot)
                                        
                                inst.transform = tm
                            except Exception as e:
                                print(f"Error determining rotation at pos {pos}: {e}")
                                inst.pos = pos
                        else:
                            inst.pos = pos
                            if rot_type > 0:
                                z_rot = 0
                                if rot_type == 1:
                                    z_rot = random.choice([0, 90, 180, 270])
                                elif rot_type == 2:
                                    z_rot = random.choice([0, 45, 90, 135, 180, 225, 270, 315])
                                elif rot_type == 3:
                                    z_rot = random.uniform(0, 360.0)
                                if z_rot != 0:
                                    inst.transform = rt.preRotateZ(inst.transform, z_rot)
                            
                        layer.addNode(inst)
                        self.generated_nodes_handles.append(inst.handle)
                        
                        # Calculate next step distance
                        step = random.uniform(min_dist, max_dist)
                        
                        # Failsafe against infinite loop
                        if step <= 0.01:
                            step = 0.01
                            
                        current_dist += step
                        
                        # Update progress based on distance covered relative to total curves approx
                        base_prog = (curve_idx - 1) / float(num_curves) * 100
                        curve_prog = pct * (100.0 / num_curves)
                        self.progress_bar.setValue(int(base_prog + curve_prog))
                        
                        QApplication.processEvents() # Keeps UI responsive if path is massive

                self.progress_bar.setValue(100)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during generation:\n{str(e)}")
            print(f"Error Spine2House Generate: {e}")
        finally:
            rt.enableSceneRedraw()
            rt.redrawViews()
            
        print(f"Successfully generated {len(self.generated_nodes_handles)} house instances along the spline.")


def show_tool():
    global spine2house_window
    
    # Close existing instance if any
    try:
        if 'spine2house_window' in globals():
            spine2house_window.close()
            spine2house_window.deleteLater()
    except:
        pass

    # Find main window parent for PySide
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
            
    spine2house_window = Spine2HouseTool(main_window)
    spine2house_window.show()

if __name__ == "__main__":
    show_tool()
