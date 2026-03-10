"""
Retarget Animation Tool
3ds Max 2025 Python Script
UI to retarget animation from a source (Dummy/Bone) to a Target object,
and bake the animation.
"""

try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui

import pymxs
from pymxs import runtime as rt

class RetargetAnimationDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(RetargetAnimationDialog, self).__init__(parent)
        self.setWindowTitle("Retarget Animation Tool")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(350)
        
        self.source_node = None
        self.target_node = None
        
        self._build_ui()
        self._apply_style()

    # --- UI and Retargeting Logic with Axis Remapping ---
    
    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(15, 15, 15, 15)

        # Header
        title = QtWidgets.QLabel("⬡ Retarget & Bake Animation")
        title.setObjectName("title")
        title.setAlignment(QtCore.Qt.AlignCenter)
        root.addWidget(title)
        root.addWidget(self._hr())

        # --- Object Selection Group ---
        pick_grp = QtWidgets.QGroupBox("1. Setup Nodes")
        pick_lay = QtWidgets.QGridLayout(pick_grp)
        pick_lay.setSpacing(8)

        axes = ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]

        # Source UI
        lbl_src = QtWidgets.QLabel("Source (Anim):")
        self.btn_pick_source = QtWidgets.QPushButton("Pick Source")
        self.btn_pick_source.setCheckable(True)
        self.btn_pick_source.clicked.connect(self._toggle_pick_source)
        self.lbl_source_name = QtWidgets.QLabel("None")
        self.lbl_source_name.setObjectName("nodeName")
        
        self.cmb_src_up = QtWidgets.QComboBox()
        self.cmb_src_up.addItems(axes)
        self.cmb_src_up.setCurrentText("+Y")

        pick_lay.addWidget(lbl_src, 0, 0)
        pick_lay.addWidget(self.btn_pick_source, 0, 1)
        pick_lay.addWidget(self.lbl_source_name, 0, 2)
        pick_lay.addWidget(QtWidgets.QLabel("Up Axis:"), 0, 3)
        pick_lay.addWidget(self.cmb_src_up, 0, 4)

        # Target UI
        lbl_tgt = QtWidgets.QLabel("Target Object:")
        self.btn_pick_target = QtWidgets.QPushButton("Pick Target")
        self.btn_pick_target.setCheckable(True)
        self.btn_pick_target.clicked.connect(self._toggle_pick_target)
        self.lbl_target_name = QtWidgets.QLabel("None")
        self.lbl_target_name.setObjectName("nodeName")
        
        self.cmb_tgt_up = QtWidgets.QComboBox()
        self.cmb_tgt_up.addItems(axes)
        self.cmb_tgt_up.setCurrentText("+X")

        pick_lay.addWidget(lbl_tgt, 1, 0)
        pick_lay.addWidget(self.btn_pick_target, 1, 1)
        pick_lay.addWidget(self.lbl_target_name, 1, 2)
        pick_lay.addWidget(QtWidgets.QLabel("Up Axis:"), 1, 3)
        pick_lay.addWidget(self.cmb_tgt_up, 1, 4)

        root.addWidget(pick_grp)

        # --- Options Group ---
        opt_grp = QtWidgets.QGroupBox("2. Bake Options")
        opt_lay = QtWidgets.QVBoxLayout(opt_grp)

        # Frame Range
        range_lay = QtWidgets.QHBoxLayout()
        range_lay.addWidget(QtWidgets.QLabel("Start:"))
        self.spn_start = QtWidgets.QSpinBox()
        self.spn_start.setRange(-99999, 99999)
        self.spn_start.setValue(int(rt.animationRange.start))
        range_lay.addWidget(self.spn_start)

        range_lay.addSpacing(15)

        range_lay.addWidget(QtWidgets.QLabel("End:"))
        self.spn_end = QtWidgets.QSpinBox()
        self.spn_end.setRange(-99999, 99999)
        self.spn_end.setValue(int(rt.animationRange.end))
        range_lay.addWidget(self.spn_end)

        opt_lay.addLayout(range_lay)

        # Transform options
        self.chk_pos = QtWidgets.QCheckBox("Retarget Position")
        self.chk_pos.setChecked(True)
        self.chk_rot = QtWidgets.QCheckBox("Retarget Rotation")
        self.chk_rot.setChecked(True)
        self.chk_scale = QtWidgets.QCheckBox("Retarget Scale")
        self.chk_scale.setChecked(False)

        opt_lay.addWidget(self.chk_pos)
        opt_lay.addWidget(self.chk_rot)
        opt_lay.addWidget(self.chk_scale)

        # Maintain Offset
        self.chk_offset = QtWidgets.QCheckBox("Maintain Offset (Relative)")
        self.chk_offset.setChecked(False)
        self.chk_offset.setToolTip("If checked, keeps the initial distance/rotation offset between Source and Target.")
        opt_lay.addWidget(self.chk_offset)

        # Delete source option
        self.chk_del_source = QtWidgets.QCheckBox("Delete Source after Baking")
        self.chk_del_source.setChecked(False)
        opt_lay.addWidget(self.chk_del_source)

        root.addWidget(opt_grp)

        root.addStretch()

        # --- Action Buttons ---
        self.btn_retarget = QtWidgets.QPushButton("🚀 Retarget & Bake")
        self.btn_retarget.setObjectName("primaryBtn")
        self.btn_retarget.setMinimumHeight(35)
        self.btn_retarget.clicked.connect(self._do_retarget)
        root.addWidget(self.btn_retarget)

        # Status
        self.lbl_status = QtWidgets.QLabel("Ready. Pick Source and Target.")
        self.lbl_status.setObjectName("status")
        self.lbl_status.setAlignment(QtCore.Qt.AlignCenter)
        root.addWidget(self.lbl_status)

        # Setup Timers for picking
        self.pick_timer = QtCore.QTimer(self)
        self.pick_timer.timeout.connect(self._check_pick_mode)
        self.pick_mode = None  # 'source' or 'target'

    def _hr(self):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        return line

    def _apply_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }
            QGroupBox {
                border: 1px solid #555;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #c9a55e;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #444;
                border: 1px solid #666;
                padding: 5px 10px;
                border-radius: 3px;
                color: #fff;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QPushButton:checked {
                background-color: #c9a55e;
                color: #2b2b2b;
                font-weight: bold;
            }
            QPushButton#primaryBtn {
                background-color: #588c7e;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton#primaryBtn:hover {
                background-color: #6eb5a2;
            }
            QLabel#title {
                font-size: 14pt;
                font-weight: bold;
                color: #e0e0e0;
            }
            QLabel#nodeName {
                color: #87ceeb;
                font-weight: bold;
            }
            QLabel#status {
                color: #aaa;
                font-style: italic;
            }
            QSpinBox {
                background-color: #3b3b3b;
                color: white;
                border: 1px solid #555;
            }
            QComboBox {
                background-color: #3b3b3b;
                color: white;
                border: 1px solid #555;
                padding: 2px 5px;
            }
            QCheckBox {
                spacing: 8px;
            }
        """)

    # --- Pick Logic ---
    def _toggle_pick_source(self):
        if self.btn_pick_source.isChecked():
            self.btn_pick_target.setChecked(False)
            self.pick_mode = 'source'
            rt.clearSelection()
            self.lbl_status.setText("Select a Source object in the viewport...")
            self.pick_timer.start(100)
        else:
            self.pick_mode = None
            self.pick_timer.stop()
            self.lbl_status.setText("Pick cancelled.")

    def _toggle_pick_target(self):
        if self.btn_pick_target.isChecked():
            self.btn_pick_source.setChecked(False)
            self.pick_mode = 'target'
            rt.clearSelection()
            self.lbl_status.setText("Select a Target object in the viewport...")
            self.pick_timer.start(100)
        else:
            self.pick_mode = None
            self.pick_timer.stop()
            self.lbl_status.setText("Pick cancelled.")

    def _check_pick_mode(self):
        if rt.selection.count == 1:
            sel = rt.selection[0]
            if self.pick_mode == 'source':
                self.source_node = sel
                self.lbl_source_name.setText(sel.name)
                self.btn_pick_source.setChecked(False)
                self.lbl_status.setText(f"Source set to: {sel.name}")
            elif self.pick_mode == 'target':
                self.target_node = sel
                self.lbl_target_name.setText(sel.name)
                self.btn_pick_target.setChecked(False)
                self.lbl_status.setText(f"Target set to: {sel.name}")
            
            self.pick_mode = None
            self.pick_timer.stop()
            rt.clearSelection()

    def _get_axis_vector(self, axis_str):
        """Convert string like '+Y' to a Point3 vector."""
        if axis_str == "+X": return rt.Point3(1, 0, 0)
        if axis_str == "-X": return rt.Point3(-1, 0, 0)
        if axis_str == "+Y": return rt.Point3(0, 1, 0)
        if axis_str == "-Y": return rt.Point3(0, -1, 0)
        if axis_str == "+Z": return rt.Point3(0, 0, 1)
        if axis_str == "-Z": return rt.Point3(0, 0, -1)
        return rt.Point3(0, 0, 1)

    # --- Retarget & Bake Logic ---
    def _do_retarget(self):
        if not self.source_node or not rt.isValidNode(self.source_node):
            self.lbl_status.setText("Error: Source node is missing or invalid.")
            return
        if not self.target_node or not rt.isValidNode(self.target_node):
            self.lbl_status.setText("Error: Target node is missing or invalid.")
            return
        if self.source_node == self.target_node:
            self.lbl_status.setText("Error: Source and Target cannot be the same.")
            return

        start_f = self.spn_start.value()
        end_f = self.spn_end.value()

        do_pos = self.chk_pos.isChecked()
        do_rot = self.chk_rot.isChecked()
        do_scale = self.chk_scale.isChecked()
        maintain_offset = self.chk_offset.isChecked()
        
        if not (do_pos or do_rot or do_scale):
            self.lbl_status.setText("Select at least one transform to retarget.")
            return

        self.lbl_status.setText("Baking animation... Please wait.")
        QtWidgets.QApplication.processEvents()

        try:
            with pymxs.undo(True, "Retarget Animation"):
                with pymxs.animate(True):
                    rt.sliderTime = start_f
                    
                    # 1. Axis Remapping Setup
                    src_up = self._get_axis_vector(self.cmb_src_up.currentText())
                    tgt_up = self._get_axis_vector(self.cmb_tgt_up.currentText())
                    
                    # Create a reliable MaxScript helper to get quaternion between two vectors
                    rt.execute('''
                    fn getQuatBetweenVectors v1 v2 = (
                        local d = dot (normalize v1) (normalize v2)
                        if d >= 0.999999 then return quat 0 0 0 1
                        if d <= -0.999999 then (
                            local ax = cross [1,0,0] v1
                            if length ax < 0.001 do ax = cross [0,1,0] v1
                            return quat 180.0 (normalize ax)
                        )
                        return quat (acos d) (normalize (cross v1 v2))
                    )
                    ''')

                    # Compute quaternions needed to rotate Source Up to Target Up
                    align_quat = rt.getQuatBetweenVectors(src_up, tgt_up)
                    
                    # 2. Maintain Offset Setup
                    pos_offset = rt.Point3(0,0,0)
                    rot_offset = rt.quat(0,0,0,1)
                    
                    if maintain_offset:
                        src_tm = self.source_node.transform
                        tgt_tm = self.target_node.transform
                        
                        # Position offset is pure world space drift
                        pos_offset = tgt_tm.row4 - src_tm.row4
                        
                        # Actual rotated source at frame 0
                        aligned_src_rot = src_tm.rotationPart * align_quat
                        
                        # TargetRot = RotOffset * AlignedSourceRot  =>  RotOffset = TargetRot * Inverse(AlignedSourceRot)
                        rot_offset = tgt_tm.rotationPart * rt.inverse(aligned_src_rot)

                    # Bake frame by frame
                    for f in range(start_f, end_f + 1):
                        rt.sliderTime = f
                        
                        src_pos = self.source_node.transform.row4
                        src_rot = self.source_node.transform.rotationPart
                        
                        if do_pos:
                            if maintain_offset:
                                self.target_node.pos = src_pos + pos_offset
                            else:
                                self.target_node.pos = src_pos
                                
                        if do_rot:
                            # 1. Spin source to match target's axis logic
                            aligned_rot = src_rot * align_quat
                            
                            # 2. Apply relative difference (offset)
                            if maintain_offset:
                                self.target_node.rotation = rot_offset * aligned_rot
                            else:
                                self.target_node.rotation = aligned_rot
                                
                        if do_scale:
                            self.target_node.scale = self.source_node.scale

                # Cleanup
                if self.chk_del_source.isChecked():
                    rt.delete(self.source_node)
                    self.source_node = None
                    self.lbl_source_name.setText("None")

            self.lbl_status.setText("✔ Retargeting Complete!")
            
        except Exception as e:
            self.lbl_status.setText(f"Error: {str(e)}")


# --- Launch ---
_retarget_dialog = None

def show_ui():
    global _retarget_dialog
    try:
        if _retarget_dialog:
            _retarget_dialog.close()
            _retarget_dialog.deleteLater()
    except:
        pass
    _retarget_dialog = RetargetAnimationDialog()
    _retarget_dialog.show()

if __name__ == "__main__":
    show_ui()
