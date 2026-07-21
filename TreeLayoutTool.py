# -*- coding: utf-8 -*-
"""
TreeLayoutTool - 3ds Max 2025 (Python 3 / pymxs / PySide6)
----------------------------------------------------------
Chuc nang:
  1. Chon danh sach cay (tree) de random
  2. Chon spline layout
  3. Layout: rai cay random (instance) vao tung knot cua spline
  4. Delete Layout: xoa toan bo cay da rai (return ve ban dau)

Cach chay trong 3ds Max 2025:
  Scripting > Run Script... > chon file TreeLayoutTool.py
  (hoac keo tha file vao viewport)
"""

import random
import pymxs
from pymxs import runtime as rt

from PySide6 import QtWidgets, QtCore

try:
    from qtmax import GetQMaxMainWindow
    _MAX_PARENT = GetQMaxMainWindow()
except Exception:
    _MAX_PARENT = None

PREFIX = "TreeLayout_"   # prefix ten cac cay duoc rai ra, dung de xoa an toan


class TreeLayoutTool(QtWidgets.QDialog):
    _instance = None

    def __init__(self, parent=_MAX_PARENT):
        super().__init__(parent)
        self.setWindowTitle("Tree Layout Tool - v1.0")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(320)

        self.tree_handles = []      # anim handle cua cac cay goc
        self.spline_handle = None   # anim handle cua spline
        self.created_handles = []   # anim handle cua cac instance da tao

        self._build_ui()

    # ---------------------------------------------------------------- UI
    STYLESHEET = """
    QDialog {
        background-color: #3c3c3c;
    }
    QGroupBox {
        color: #e0e0e0;
        font-size: 12px;
        font-weight: bold;
        border: 1px solid #555555;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 8px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 4px;
        color: #f0c060;
    }
    QLabel {
        color: #cccccc;
        font-size: 12px;
    }
    QCheckBox {
        color: #dddddd;
        font-size: 12px;
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
    }
    QSpinBox, QDoubleSpinBox {
        background-color: #2b2b2b;
        color: #ffffff;
        border: 1px solid #666666;
        border-radius: 4px;
        padding: 3px 6px;
        font-size: 12px;
        min-height: 22px;
    }
    QSpinBox:focus, QDoubleSpinBox:focus {
        border: 1px solid #f0c060;
    }
    QPushButton {
        background-color: #545454;
        color: #ffffff;
        border: 1px solid #6a6a6a;
        border-radius: 5px;
        padding: 8px 12px;
        font-size: 12px;
    }
    QPushButton:hover {
        background-color: #656565;
        border: 1px solid #8a8a8a;
    }
    QPushButton:pressed {
        background-color: #454545;
    }
    QPushButton#btnLayout {
        background-color: #2e7d32;
        border: 1px solid #4caf50;
        color: #ffffff;
        font-size: 14px;
        font-weight: bold;
        letter-spacing: 1px;
    }
    QPushButton#btnLayout:hover  { background-color: #388e3c; }
    QPushButton#btnLayout:pressed{ background-color: #1b5e20; }
    QPushButton#btnDelete {
        background-color: #5a3030;
        border: 1px solid #b05050;
        color: #ffb0b0;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton#btnDelete:hover  { background-color: #6e3838; color: #ffffff; }
    QPushButton#btnDelete:pressed{ background-color: #452525; }
    QLabel#status {
        background-color: #2b2b2b;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 6px 8px;
        font-size: 12px;
    }
    """

    def _build_ui(self):
        self.setStyleSheet(self.STYLESHEET)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        # --- Nhom 1: chon cay ---
        grp_tree = QtWidgets.QGroupBox("1. Tree Objects (random)")
        v1 = QtWidgets.QVBoxLayout(grp_tree)
        v1.setSpacing(6)
        self.btn_pick_trees = QtWidgets.QPushButton("  Lay cay tu Selection")
        self.btn_pick_trees.setMinimumHeight(32)
        self.lbl_trees = QtWidgets.QLabel("Chua chon cay nao")
        self.lbl_trees.setStyleSheet("color:#999999; font-style:italic;")
        self.lbl_trees.setWordWrap(True)
        v1.addWidget(self.btn_pick_trees)
        v1.addWidget(self.lbl_trees)
        layout.addWidget(grp_tree)

        # --- Nhom 2: chon spline ---
        grp_spline = QtWidgets.QGroupBox("2. Spline Layout")
        v2 = QtWidgets.QVBoxLayout(grp_spline)
        v2.setSpacing(6)
        self.btn_pick_spline = QtWidgets.QPushButton("  Pick Spline (click vao viewport)")
        self.btn_pick_spline.setMinimumHeight(32)
        self.lbl_spline = QtWidgets.QLabel("Chua chon spline")
        self.lbl_spline.setStyleSheet("color:#999999; font-style:italic;")
        self.lbl_spline.setWordWrap(True)
        v2.addWidget(self.btn_pick_spline)
        v2.addWidget(self.lbl_spline)
        layout.addWidget(grp_spline)

        # --- Tuy chon ---
        grp_opt = QtWidgets.QGroupBox("Options")
        form = QtWidgets.QFormLayout(grp_opt)
        form.setSpacing(8)

        self.chk_rot = QtWidgets.QCheckBox("Random xoay Z (0-360)")
        self.chk_rot.setChecked(True)
        form.addRow(self.chk_rot)

        h_scale = QtWidgets.QHBoxLayout()
        h_scale.setSpacing(6)
        self.spn_scale_min = QtWidgets.QDoubleSpinBox()
        self.spn_scale_min.setRange(0.01, 100.0)
        self.spn_scale_min.setValue(1.0)
        self.spn_scale_min.setSingleStep(0.05)
        self.spn_scale_max = QtWidgets.QDoubleSpinBox()
        self.spn_scale_max.setRange(0.01, 100.0)
        self.spn_scale_max.setValue(1.0)
        self.spn_scale_max.setSingleStep(0.05)
        h_scale.addWidget(QtWidgets.QLabel("Min"))
        h_scale.addWidget(self.spn_scale_min, 1)
        h_scale.addWidget(QtWidgets.QLabel("Max"))
        h_scale.addWidget(self.spn_scale_max, 1)
        form.addRow("Random scale:", h_scale)

        self.spn_seed = QtWidgets.QSpinBox()
        self.spn_seed.setRange(0, 999999)
        self.spn_seed.setValue(12345)
        form.addRow("Seed:", self.spn_seed)

        layout.addWidget(grp_opt)

        # --- Nhom 3: nut chinh ---
        v3 = QtWidgets.QVBoxLayout()
        v3.setSpacing(8)
        self.btn_layout = QtWidgets.QPushButton("LAYOUT")
        self.btn_layout.setObjectName("btnLayout")
        self.btn_layout.setMinimumHeight(44)
        self.btn_layout.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_delete = QtWidgets.QPushButton("DELETE LAYOUT")
        self.btn_delete.setObjectName("btnDelete")
        self.btn_delete.setMinimumHeight(34)
        self.btn_delete.setCursor(QtCore.Qt.PointingHandCursor)
        v3.addWidget(self.btn_layout)
        v3.addWidget(self.btn_delete)
        layout.addLayout(v3)

        self.lbl_status = QtWidgets.QLabel("San sang.")
        self.lbl_status.setObjectName("status")
        self.lbl_status.setStyleSheet("color:#8fdf8f;")
        self.lbl_status.setWordWrap(True)
        layout.addWidget(self.lbl_status)

        # --- Ket noi signal ---
        self.btn_pick_trees.clicked.connect(self.pick_trees)
        self.btn_pick_spline.clicked.connect(self.pick_spline)
        self.btn_layout.clicked.connect(self.do_layout)
        self.btn_delete.clicked.connect(self.delete_layout)

    # ---------------------------------------------------------- helpers
    @staticmethod
    def _node_from_handle(handle):
        node = rt.maxOps.getNodeByHandle(handle)
        if node is None or not rt.isValidNode(node):
            return None
        return node

    def _get_tree_nodes(self):
        nodes = []
        for h in self.tree_handles:
            n = self._node_from_handle(h)
            if n is not None:
                nodes.append(n)
        return nodes

    # ------------------------------------------------------------ picks
    def pick_trees(self):
        sel = list(rt.selection)
        geo = [n for n in sel if rt.superClassOf(n) == rt.GeometryClass]
        if not geo:
            self.lbl_trees.setText("Selection khong co doi tuong geometry nao!")
            self.lbl_trees.setStyleSheet("color:#ff8080;")
            return
        self.tree_handles = [n.inode.handle for n in geo]
        names = ", ".join(n.name for n in geo[:4])
        more = f" ... (+{len(geo)-4})" if len(geo) > 4 else ""
        self.lbl_trees.setText(f"{len(geo)} cay: {names}{more}")
        self.lbl_trees.setStyleSheet("color:#7fbf7f;")
        self.lbl_status.setText("Da luu danh sach cay.")

    def pick_spline(self):
        self.lbl_status.setText("Click vao spline trong viewport...")
        QtWidgets.QApplication.processEvents()

        # filter chi cho pick shape/spline
        filter_fn = rt.execute("fn _tl_shapeFilter o = (superClassOf o == shape)")
        picked = rt.pickObject(message="Pick spline layout", filter=filter_fn)

        if picked is None or not rt.isValidNode(picked):
            self.lbl_status.setText("Huy pick spline.")
            return

        self.spline_handle = picked.inode.handle
        n_splines = rt.numSplines(picked)
        total_knots = sum(rt.numKnots(picked, s) for s in range(1, n_splines + 1))
        self.lbl_spline.setText(f"{picked.name}  ({n_splines} spline, {total_knots} knot)")
        self.lbl_spline.setStyleSheet("color:#7fbf7f;")
        self.lbl_status.setText("Da chon spline.")

    # ----------------------------------------------------------- layout
    def do_layout(self):
        trees = self._get_tree_nodes()
        spline = self._node_from_handle(self.spline_handle) if self.spline_handle else None

        if not trees:
            self.lbl_status.setText("Chua chon cay! (buoc 1)")
            return
        if spline is None:
            self.lbl_status.setText("Chua chon spline! (buoc 2)")
            return

        # xoa layout cu truoc khi rai moi (tranh chong lap)
        self.delete_layout(silent=True)

        rng = random.Random(self.spn_seed.value())
        s_min = min(self.spn_scale_min.value(), self.spn_scale_max.value())
        s_max = max(self.spn_scale_min.value(), self.spn_scale_max.value())

        created = 0
        with pymxs.undo(True, "TreeLayout"):
            rt.disableSceneRedraw()
            try:
                n_splines = rt.numSplines(spline)
                for s in range(1, n_splines + 1):
                    n_knots = rt.numKnots(spline, s)
                    for k in range(1, n_knots + 1):
                        pos = rt.getKnotPoint(spline, s, k)  # world space

                        src = rng.choice(trees)
                        inst = rt.instance(src)
                        inst.name = rt.uniqueName(PREFIX + src.name + "_")
                        inst.position = pos

                        if self.chk_rot.isChecked():
                            rt.rotate(inst, rt.eulerAngles(0, 0, rng.uniform(0.0, 360.0)))

                        if abs(s_max - s_min) > 1e-6 or abs(s_min - 1.0) > 1e-6:
                            sc = rng.uniform(s_min, s_max)
                            inst.scale = rt.Point3(sc, sc, sc)

                        self.created_handles.append(inst.inode.handle)
                        created += 1
            finally:
                rt.enableSceneRedraw()
                rt.redrawViews()

        self.lbl_status.setText(f"Da rai {created} cay vao knot.")

    # ----------------------------------------------------------- delete
    def delete_layout(self, silent=False):
        count = 0
        with pymxs.undo(True, "DeleteTreeLayout"):
            # 1) xoa theo handle da luu
            for h in self.created_handles:
                n = self._node_from_handle(h)
                if n is not None:
                    rt.delete(n)
                    count += 1
            self.created_handles = []

            # 2) don sach theo prefix (phong khi mat handle sau khi mo lai tool)
            leftovers = [n for n in rt.objects if n.name.startswith(PREFIX)]
            for n in leftovers:
                rt.delete(n)
                count += 1

        rt.redrawViews()
        if not silent:
            self.lbl_status.setText(f"Da xoa {count} cay layout." if count else "Khong co gi de xoa.")


# --------------------------------------------------------------- run
def show_tool():
    if TreeLayoutTool._instance is not None:
        try:
            TreeLayoutTool._instance.close()
            TreeLayoutTool._instance.deleteLater()
        except Exception:
            pass
    TreeLayoutTool._instance = TreeLayoutTool()
    TreeLayoutTool._instance.show()


show_tool()