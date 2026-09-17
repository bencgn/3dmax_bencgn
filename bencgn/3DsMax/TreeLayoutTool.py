# -*- coding: utf-8 -*-
"""
TreeLayoutTool - 3ds Max 2025 (Python 3 / pymxs / PySide6)  -  v1.1
-------------------------------------------------------------------
FIX v1.1:
  - Bam LAYOUT KHONG con tu dong xoa cac cay da rai truoc do.
    (Truoc day no xoa theo handle + quet ten prefix toan scene, nen cuc
     mesh vua Attach - von giu lai handle & ten cua node dau tien - bi
     xoa mat.)
  - Them nut KEEP: chot batch hien tai, tool "quen" chung di hoan toan.
  - Nut CLEAR LAST: chi xoa dung batch vua rai (undo nhanh mot lan rai).
  - Nut DELETE ALL: quet theo prefix, co hop thoai xac nhan.

Cach chay:
  Scripting > Run Script... > chon file TreeLayoutTool.py
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

PREFIX = "TreeLayout_"    # ten cay moi rai ra (chua chot)
KEPT_PREFIX = "Tree_"     # ten sau khi bam KEEP - tool khong dung toi nua


class TreeLayoutTool(QtWidgets.QDialog):
    _instance = None

    def __init__(self, parent=_MAX_PARENT):
        super().__init__(parent)
        self.setWindowTitle("Tree Layout Tool - v1.1")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(340)

        self.tree_handles = []      # anim handle cua cac cay goc
        self.spline_handle = None   # anim handle cua spline
        self.created_handles = []   # handle cua batch VUA rai (chua chot)

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
    QPushButton#btnKeep {
        background-color: #2b4a6b;
        border: 1px solid #4a7fb5;
        color: #cfe6ff;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton#btnKeep:hover  { background-color: #35597f; color:#ffffff; }
    QPushButton#btnKeep:pressed{ background-color: #203a55; }
    QPushButton#btnClear {
        background-color: #4a4430;
        border: 1px solid #8a7a45;
        color: #e8d9a0;
        font-size: 12px;
    }
    QPushButton#btnClear:hover  { background-color: #5a533a; color:#ffffff; }
    QPushButton#btnDelete {
        background-color: #5a3030;
        border: 1px solid #b05050;
        color: #ffb0b0;
        font-size: 12px;
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

        self.chk_auto_seed = QtWidgets.QCheckBox("Tu doi seed moi lan Layout")
        self.chk_auto_seed.setChecked(True)
        form.addRow(self.chk_auto_seed)

        layout.addWidget(grp_opt)

        # --- Nhom 3: nut chinh ---
        v3 = QtWidgets.QVBoxLayout()
        v3.setSpacing(8)

        self.btn_layout = QtWidgets.QPushButton("LAYOUT")
        self.btn_layout.setObjectName("btnLayout")
        self.btn_layout.setMinimumHeight(44)
        self.btn_layout.setCursor(QtCore.Qt.PointingHandCursor)
        v3.addWidget(self.btn_layout)

        self.btn_keep = QtWidgets.QPushButton("KEEP - chot batch nay")
        self.btn_keep.setObjectName("btnKeep")
        self.btn_keep.setMinimumHeight(34)
        self.btn_keep.setCursor(QtCore.Qt.PointingHandCursor)
        v3.addWidget(self.btn_keep)

        h_del = QtWidgets.QHBoxLayout()
        h_del.setSpacing(8)
        self.btn_clear = QtWidgets.QPushButton("CLEAR LAST")
        self.btn_clear.setObjectName("btnClear")
        self.btn_clear.setMinimumHeight(30)
        self.btn_delete = QtWidgets.QPushButton("DELETE ALL")
        self.btn_delete.setObjectName("btnDelete")
        self.btn_delete.setMinimumHeight(30)
        h_del.addWidget(self.btn_clear, 1)
        h_del.addWidget(self.btn_delete, 1)
        v3.addLayout(h_del)

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
        self.btn_keep.clicked.connect(self.keep_layout)
        self.btn_clear.clicked.connect(self.clear_last)
        self.btn_delete.clicked.connect(self.delete_all)

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

    def _set_status(self, text, color="#8fdf8f"):
        self.lbl_status.setText(text)
        self.lbl_status.setStyleSheet("color:%s;" % color)

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
        more = " ... (+%d)" % (len(geo) - 4) if len(geo) > 4 else ""
        self.lbl_trees.setText("%d cay: %s%s" % (len(geo), names, more))
        self.lbl_trees.setStyleSheet("color:#7fbf7f;")
        self._set_status("Da luu danh sach cay.")

    def pick_spline(self):
        self._set_status("Click vao spline trong viewport...", "#f0c060")
        QtWidgets.QApplication.processEvents()

        filter_fn = rt.execute("fn _tl_shapeFilter o = (superClassOf o == shape)")
        picked = rt.pickObject(message="Pick spline layout", filter=filter_fn)

        if picked is None or not rt.isValidNode(picked):
            self._set_status("Huy pick spline.", "#f0c060")
            return

        self.spline_handle = picked.inode.handle
        n_splines = rt.numSplines(picked)
        total_knots = sum(rt.numKnots(picked, s) for s in range(1, n_splines + 1))
        self.lbl_spline.setText("%s  (%d spline, %d knot)"
                                % (picked.name, n_splines, total_knots))
        self.lbl_spline.setStyleSheet("color:#7fbf7f;")
        self._set_status("Da chon spline.")

    # ----------------------------------------------------------- layout
    def do_layout(self):
        trees = self._get_tree_nodes()
        spline = self._node_from_handle(self.spline_handle) if self.spline_handle else None

        if not trees:
            self._set_status("Chua chon cay! (buoc 1)", "#ff8080")
            return
        if spline is None:
            self._set_status("Chua chon spline! (buoc 2)", "#ff8080")
            return

        # >>> KHONG xoa gi ca. Moi lan Layout la mot batch moc them vao scene.
        #     Batch cu (neu chua KEEP) chi bi bo theo doi, khong bi xoa.
        if self.created_handles:
            self.created_handles = []

        if self.chk_auto_seed.isChecked():
            new_seed = random.randint(0, 999999)
            self.spn_seed.blockSignals(True)
            self.spn_seed.setValue(new_seed)
            self.spn_seed.blockSignals(False)

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

        self._set_status("Da rai %d cay. Bam KEEP de chot, hoac CLEAR LAST de rai lai."
                         % created)

    # ------------------------------------------------------------- keep
    def keep_layout(self):
        """Chot batch hien tai: doi ten sang KEPT_PREFIX + bo theo doi."""
        if not self.created_handles:
            self._set_status("Khong co batch nao dang theo doi.", "#f0c060")
            return

        n_ok = 0
        with pymxs.undo(True, "KeepTreeLayout"):
            for h in self.created_handles:
                n = self._node_from_handle(h)
                if n is not None:
                    if n.name.startswith(PREFIX):
                        n.name = rt.uniqueName(KEPT_PREFIX + n.name[len(PREFIX):])
                    n_ok += 1
        self.created_handles = []
        self._set_status("Da chot %d cay - tool khong dung toi chung nua." % n_ok)

    # ------------------------------------------------------------ clear
    def clear_last(self):
        """Chi xoa dung batch vua rai (chua KEEP)."""
        handles = list(self.created_handles)
        self.created_handles = []
        if not handles:
            self._set_status("Khong co batch nao de xoa.", "#f0c060")
            return

        count = 0
        with pymxs.undo(True, "ClearLastTreeLayout"):
            for h in handles:
                n = self._node_from_handle(h)
                # chi xoa neu ten van con prefix -> tranh xoa nham node da
                # bi Attach / doi ten thu cong
                if n is not None and n.name.startswith(PREFIX):
                    rt.delete(n)
                    count += 1
        rt.redrawViews()
        self._set_status("Da xoa %d cay cua batch vua roi." % count)

    # ----------------------------------------------------------- delete
    def delete_all(self):
        """Quet toan scene theo PREFIX - co xac nhan."""
        leftovers = [n for n in rt.objects if n.name.startswith(PREFIX)]
        if not leftovers:
            self.created_handles = []
            self._set_status("Khong tim thay object nao ten '%s...'." % PREFIX, "#f0c060")
            return

        ans = QtWidgets.QMessageBox.question(
            self, "Xac nhan xoa",
            "Se xoa %d object co ten bat dau bang '%s'.\n\n"
            "Luu y: cuc mesh da Attach ma van giu ten cu cung se bi xoa.\n"
            "Tiep tuc?" % (len(leftovers), PREFIX),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        if ans != QtWidgets.QMessageBox.Yes:
            self._set_status("Da huy.", "#f0c060")
            return

        count = 0
        with pymxs.undo(True, "DeleteAllTreeLayout"):
            for n in leftovers:
                if rt.isValidNode(n):
                    rt.delete(n)
                    count += 1
        self.created_handles = []
        rt.redrawViews()
        self._set_status("Da xoa %d cay layout." % count)


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
