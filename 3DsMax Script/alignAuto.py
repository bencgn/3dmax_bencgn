"""
AlignAuto Tool for 3ds Max 2025
================================
Aligns objects from a "Current" (source) hierarchy to a "Target" hierarchy,
matching:
  • World Position  XYZ  (pivot → pivot)
  • Orientation    (Local) XYZ

The UI shows two mirrored hierarchy trees side-by-side.
Selecting the root of a hierarchy on each side and clicking
"▶  Auto Align All" walks every parent→child pair in order.

Author  : BenCGN
Version : 2.0  (2026)

Usage (3ds Max Python Listener):
    import importlib, sys
    sys.path.insert(0, r"D:\\3dmax_bencgn\\3dmax_bencgn\\3DsMax Script")
    import alignAuto; importlib.reload(alignAuto); alignAuto.launch()
"""

from __future__ import annotations
from typing import List, Optional

# ── 3ds Max runtime ──────────────────────────────────────────────────────────
try:
    import pymxs
    from pymxs import runtime as rt
    _IN_MAX = True
except ImportError:
    _IN_MAX = False

# ── Qt (PySide6 for 3ds Max 2025 / PySide2 fallback) ───────────────────────
_PYSIDE_VER = 0

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import Qt
    _PYSIDE_VER = 6

    _SingleSel   = QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
    _HV_Stretch  = QtWidgets.QHeaderView.ResizeMode.Stretch
    _HV_Content  = QtWidgets.QHeaderView.ResizeMode.ResizeToContents
    _Frame_HLine = QtWidgets.QFrame.Shape.HLine
    _WinMin      = Qt.WindowType.WindowMinimizeButtonHint
    _WinMax      = Qt.WindowType.WindowMaximizeButtonHint

    try:
        import qtmax
        def _max_main_window():
            return qtmax.GetQMaxMainWindow()
    except ImportError:
        def _max_main_window():
            return None

except ImportError:
    try:
        from PySide2 import QtCore, QtGui, QtWidgets
        from PySide2.QtCore import Qt
        _PYSIDE_VER = 2

        _SingleSel   = QtWidgets.QAbstractItemView.SingleSelection
        _HV_Stretch  = QtWidgets.QHeaderView.Stretch
        _HV_Content  = QtWidgets.QHeaderView.ResizeToContents
        _Frame_HLine = QtWidgets.QFrame.HLine
        _WinMin      = Qt.WindowMinimizeButtonHint
        _WinMax      = Qt.WindowMaximizeButtonHint

        try:
            import qtmax
            def _max_main_window():
                return qtmax.GetQMaxMainWindow()
        except ImportError:
            def _max_main_window():
                return None

    except ImportError:
        raise RuntimeError("PySide6 / PySide2 not found. Run inside 3ds Max.")


# ═══════════════════════════════════════════════════════════════════════════════
#  COLOUR PALETTE  — black & white modern / minimal
# ═══════════════════════════════════════════════════════════════════════════════
BG_WIN      = "#111111"
BG_PANEL    = "#1a1a1a"
BG_CARD     = "#222222"
BG_ITEM     = "#2a2a2a"
BORDER      = "#383838"
TEXT_PRI    = "#f0f0f0"
TEXT_MUT    = "#888888"
TEXT_DIM    = "#555555"
ACCENT      = "#ffffff"
ACCENT_OK   = "#cccccc"
ACCENT_ERR  = "#ff4444"
HIGHLIGHT   = "rgba(255,255,255,0.07)"
DONE_BG     = "rgba(255,255,255,0.05)"


# ═══════════════════════════════════════════════════════════════════════════════
#  MAX HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_node(name: str):
    if not _IN_MAX:
        return None
    return rt.getNodeByName(name, exact=True)


def _hierarchy_flat(root_node) -> List:
    result = []
    def _walk(n):
        result.append(n)
        try:
            kids = list(n.children)
        except Exception:
            kids = []
        for k in kids:
            _walk(k)
    _walk(root_node)
    return result


def _scene_roots() -> List:
    if not _IN_MAX:
        return []
    roots = []
    for obj in rt.objects:
        try:
            if obj.parent is None:
                roots.append(obj)
        except Exception:
            pass
    return roots


def _all_scene_nodes_hierarchy() -> List:
    result = []
    for root in _scene_roots():
        result.extend(_hierarchy_flat(root))
    return result


# ═══════════════════════════════════════════════════════════════════════════════
#  HIERARCHY TREE WIDGET
# ═══════════════════════════════════════════════════════════════════════════════

class HierarchyTree(QtWidgets.QTreeWidget):
    nodeSelected = QtCore.Signal(str)

    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self._label = label
        self._node_map: dict = {}
        self.setSelectionMode(_SingleSel)
        self.setRootIsDecorated(True)
        self.setAnimated(True)
        self.setAlternatingRowColors(True)
        self.setHeaderHidden(True)
        self.setMinimumWidth(190)
        self.itemSelectionChanged.connect(self._on_selection)

    def refresh(self):
        self.clear()
        self._node_map.clear()

        if not _IN_MAX:
            for d in ["Root_A", "  Child_A1", "  Child_A2"]:
                it = QtWidgets.QTreeWidgetItem(self)
                it.setText(0, d)
            return

        def _add_children(parent_item, node):
            try:
                kids = list(node.children)
            except Exception:
                kids = []
            for k in kids:
                name = str(k.name)
                child_item = QtWidgets.QTreeWidgetItem(parent_item)
                child_item.setText(0, f"  {name}")
                child_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, name)
                child_item.setForeground(0, QtGui.QColor(TEXT_MUT))
                self._node_map[name] = k
                _add_children(child_item, k)

        for root_node in _scene_roots():
            name = str(root_node.name)
            root_item = QtWidgets.QTreeWidgetItem(self)
            root_item.setText(0, f"◉  {name}")
            root_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, name)
            root_item.setForeground(0, QtGui.QColor(TEXT_PRI))
            fnt = root_item.font(0)
            fnt.setBold(True)
            root_item.setFont(0, fnt)
            self._node_map[name] = root_node
            _add_children(root_item, root_node)

        self.expandAll()

    def selected_node_name(self) -> Optional[str]:
        items = self.selectedItems()
        if not items:
            return None
        return items[0].data(0, QtCore.Qt.ItemDataRole.UserRole)

    def selected_max_node(self):
        name = self.selected_node_name()
        if name is None:
            return None
        return self._node_map.get(name) or _get_node(name)

    def highlight_row(self, name: str, done: bool):
        def _scan(item):
            if item.data(0, QtCore.Qt.ItemDataRole.UserRole) == name:
                if done:
                    item.setForeground(0, QtGui.QColor(ACCENT))
                    item.setBackground(0, QtGui.QColor(DONE_BG))
                else:
                    item.setForeground(0, QtGui.QColor(ACCENT_ERR))
                return True
            for i in range(item.childCount()):
                if _scan(item.child(i)):
                    return True
            return False
        for i in range(self.topLevelItemCount()):
            _scan(self.topLevelItem(i))

    def clear_highlights(self):
        def _clear(item):
            item.setBackground(0, QtGui.QBrush())
            for i in range(item.childCount()):
                _clear(item.child(i))
        for i in range(self.topLevelItemCount()):
            _clear(self.topLevelItem(i))

    def _select_by_name(self, name: str) -> bool:
        def _find(item):
            if item.data(0, QtCore.Qt.ItemDataRole.UserRole) == name:
                return item
            for i in range(item.childCount()):
                found = _find(item.child(i))
                if found:
                    return found
            return None
        for i in range(self.topLevelItemCount()):
            match = _find(self.topLevelItem(i))
            if match:
                self.clearSelection()
                match.setSelected(True)
                self.scrollToItem(match)
                return True
        return False

    def _on_selection(self):
        name = self.selected_node_name()
        if name:
            self.nodeSelected.emit(name)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAIR TABLE
# ═══════════════════════════════════════════════════════════════════════════════

class PairTableWidget(QtWidgets.QTableWidget):
    _HDR = ["#", "Source", "→", "Target"]

    def __init__(self, parent=None):
        super().__init__(0, 4, parent)
        self.setHorizontalHeaderLabels(self._HDR)
        self.horizontalHeader().setSectionResizeMode(0, _HV_Content)
        self.horizontalHeader().setSectionResizeMode(1, _HV_Stretch)
        self.horizontalHeader().setSectionResizeMode(2, _HV_Content)
        self.horizontalHeader().setSectionResizeMode(3, _HV_Stretch)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
            if _PYSIDE_VER == 6
            else QtWidgets.QAbstractItemView.NoEditTriggers
        )
        self.setAlternatingRowColors(True)
        self.setMinimumHeight(110)
        self.setMaximumHeight(160)

    def load_pairs(self, pairs: List[tuple]):
        self.setRowCount(0)
        for i, (src, tgt) in enumerate(pairs):
            self.insertRow(i)
            idx_item = QtWidgets.QTableWidgetItem(str(i + 1))
            idx_item.setForeground(QtGui.QColor(TEXT_DIM))

            src_item = QtWidgets.QTableWidgetItem(src)
            src_item.setForeground(QtGui.QColor(TEXT_PRI))

            arrow = QtWidgets.QTableWidgetItem("→")
            arrow.setForeground(QtGui.QColor(TEXT_MUT))
            arrow.setTextAlignment(
                QtCore.Qt.AlignmentFlag.AlignCenter if _PYSIDE_VER == 6
                else QtCore.Qt.AlignCenter
            )

            tgt_item = QtWidgets.QTableWidgetItem(tgt)
            tgt_item.setForeground(QtGui.QColor(TEXT_MUT))

            self.setItem(i, 0, idx_item)
            self.setItem(i, 1, src_item)
            self.setItem(i, 2, arrow)
            self.setItem(i, 3, tgt_item)

    def mark_done(self, row: int):
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setForeground(QtGui.QColor(ACCENT))
                item.setBackground(QtGui.QColor(DONE_BG))

    def mark_mismatch(self, row: int):
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setForeground(QtGui.QColor(ACCENT_ERR))


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

class AlignAutoWindow(QtWidgets.QDialog):

    VERSION = "2.0"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AlignAuto")
        self.setMinimumSize(560, 500)
        self.resize(620, 560)
        self.setWindowFlags(self.windowFlags() | _WinMin | _WinMax)
        self._pairs: List[tuple] = []
        self._prefix_src_nodes: Optional[List] = None
        self._prefix_tgt_nodes: Optional[List] = None
        self._apply_stylesheet()
        self._build_ui()

    # ── Stylesheet ────────────────────────────────────────────────────────────

    def _apply_stylesheet(self):
        self.setStyleSheet(f"""
            * {{
                font-family: "Segoe UI", "Inter", sans-serif;
                font-size: 12px;
            }}
            QDialog {{
                background: {BG_WIN};
                color: {TEXT_PRI};
            }}

            /* Labels */
            QLabel {{
                color: {TEXT_PRI};
            }}
            QLabel#lbl_title {{
                color: {ACCENT};
                font-size: 16px;
                font-weight: 700;
                letter-spacing: 2px;
            }}
            QLabel#lbl_sub {{
                color: {TEXT_DIM};
                font-size: 10px;
            }}
            QLabel#lbl_section {{
                color: {TEXT_MUT};
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 1px;
                text-transform: uppercase;
            }}
            QLabel#lbl_status {{
                color: {TEXT_DIM};
                font-size: 10px;
                padding: 2px 4px;
            }}
            QLabel#lbl_panel {{
                color: {TEXT_MUT};
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
                padding: 4px 0 2px 0;
            }}

            /* Separator */
            QFrame#sep {{
                background: {BORDER};
                max-height: 1px;
                border: none;
            }}

            /* Buttons — base */
            QPushButton {{
                background: {BG_CARD};
                color: {TEXT_MUT};
                border: 1px solid {BORDER};
                border-radius: 5px;
                padding: 5px 12px;
                font-size: 11px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {BG_ITEM};
                color: {TEXT_PRI};
                border-color: {TEXT_MUT};
            }}
            QPushButton:pressed {{
                background: {BG_WIN};
            }}

            /* Refresh */
            QPushButton#btn_refresh {{
                background: transparent;
                color: {TEXT_DIM};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 3px 8px;
                font-size: 10px;
            }}
            QPushButton#btn_refresh:hover {{
                color: {TEXT_PRI};
                border-color: {TEXT_MUT};
            }}

            /* Pick */
            QPushButton#btn_pick_cur,
            QPushButton#btn_pick_tgt {{
                background: transparent;
                color: {TEXT_DIM};
                border: 1px solid {BORDER};
                border-radius: 4px;
                font-size: 10px;
                padding: 3px 8px;
            }}
            QPushButton#btn_pick_cur:hover,
            QPushButton#btn_pick_tgt:hover {{
                color: {TEXT_PRI};
                border-color: {TEXT_MUT};
            }}

            /* Preview */
            QPushButton#btn_preview {{
                background: transparent;
                color: {TEXT_MUT};
                border: 1px solid {BORDER};
                border-radius: 5px;
                font-size: 11px;
                padding: 5px 12px;
            }}
            QPushButton#btn_preview:hover {{
                color: {TEXT_PRI};
                border-color: {TEXT_MUT};
            }}

            /* Match prefix */
            QPushButton#btn_match {{
                background: {BG_CARD};
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 5px;
                font-size: 11px;
                font-weight: 600;
                padding: 5px 14px;
            }}
            QPushButton#btn_match:hover {{
                background: {BG_ITEM};
                border-color: {TEXT_MUT};
            }}

            /* Auto Align All — primary action */
            QPushButton#btn_align {{
                background: {ACCENT};
                color: {BG_WIN};
                font-size: 13px;
                font-weight: 700;
                border: none;
                border-radius: 6px;
                padding: 8px 28px;
                min-height: 34px;
            }}
            QPushButton#btn_align:hover {{
                background: #dddddd;
            }}
            QPushButton#btn_align:pressed {{
                background: #aaaaaa;
            }}

            /* Orientation Constraint — secondary action */
            QPushButton#btn_orient {{
                background: {BG_CARD};
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 6px;
                font-size: 13px;
                font-weight: 700;
                padding: 8px 20px;
                min-height: 34px;
            }}
            QPushButton#btn_orient:hover {{
                background: {BG_ITEM};
                border-color: {TEXT_MUT};
            }}
            QPushButton#btn_orient:pressed {{
                background: {BG_WIN};
            }}

            /* Tree */
            QTreeWidget {{
                background: {BG_CARD};
                color: {TEXT_MUT};
                border: 1px solid {BORDER};
                border-radius: 5px;
                outline: none;
                font-size: 11px;
                alternate-background-color: {BG_ITEM};
            }}
            QTreeWidget::item {{
                padding: 3px 5px;
            }}
            QTreeWidget::item:selected {{
                background: {HIGHLIGHT};
                color: {TEXT_PRI};
            }}
            QTreeWidget::item:hover:!selected {{
                background: rgba(255,255,255,0.04);
            }}
            QHeaderView::section {{
                background: {BG_PANEL};
                color: {TEXT_DIM};
                border: none;
                border-bottom: 1px solid {BORDER};
                padding: 4px 6px;
                font-size: 10px;
                font-weight: 600;
            }}

            /* Table */
            QTableWidget {{
                background: {BG_CARD};
                color: {TEXT_MUT};
                border: 1px solid {BORDER};
                border-radius: 5px;
                gridline-color: {BG_ITEM};
                alternate-background-color: {BG_ITEM};
                font-size: 11px;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 2px 5px;
            }}
            QTableWidget::item:selected {{
                background: {HIGHLIGHT};
            }}

            /* Scrollbars */
            QScrollBar:vertical {{
                background: {BG_PANEL};
                width: 5px;
                border-radius: 2px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER};
                border-radius: 2px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {TEXT_DIM};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{ height: 0; }}

            QScrollBar:horizontal {{
                background: {BG_PANEL};
                height: 5px;
                border-radius: 2px;
            }}
            QScrollBar::handle:horizontal {{
                background: {BORDER};
                border-radius: 2px;
                min-width: 20px;
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{ width: 0; }}

            /* CheckBox */
            QCheckBox {{
                color: {TEXT_MUT};
                spacing: 5px;
                font-size: 11px;
            }}
            QCheckBox::indicator {{
                width: 13px; height: 13px;
                border: 1px solid {BORDER};
                border-radius: 2px;
                background: {BG_CARD};
            }}
            QCheckBox::indicator:checked {{
                background: {ACCENT};
                border-color: {ACCENT};
            }}
        """)

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setSpacing(8)
        root.setContentsMargins(14, 12, 14, 10)

        # Header
        root.addLayout(self._build_header())
        root.addWidget(self._make_sep())

        # Align axis toggles (compact)
        root.addLayout(self._build_axis_options())
        root.addWidget(self._make_sep())

        # Dual tree panel
        root.addLayout(self._build_dual_panel(), stretch=3)

        # Pair preview label
        pair_lbl = QtWidgets.QLabel("PAIRS")
        pair_lbl.setObjectName("lbl_section")
        root.addWidget(pair_lbl)

        self._pair_table = PairTableWidget()
        root.addWidget(self._pair_table, stretch=1)

        # Action row
        root.addLayout(self._build_action_row())

        # Status
        self._lbl_status = QtWidgets.QLabel("Ready.")
        self._lbl_status.setObjectName("lbl_status")
        root.addWidget(self._lbl_status)

    def _build_header(self) -> QtWidgets.QHBoxLayout:
        lay = QtWidgets.QHBoxLayout()
        lay.setSpacing(8)

        t = QtWidgets.QLabel("ALIGN AUTO")
        t.setObjectName("lbl_title")
        lay.addWidget(t)

        sub = QtWidgets.QLabel("Hierarchy Align  ·  3ds Max 2025")
        sub.setObjectName("lbl_sub")
        lay.addWidget(sub)

        lay.addStretch()

        badge = QtWidgets.QLabel(f"v{self.VERSION}")
        badge.setStyleSheet(
            f"color:{TEXT_DIM}; font-size:10px;"
        )
        lay.addWidget(badge)

        btn_ref = QtWidgets.QPushButton("⟳  Refresh")
        btn_ref.setObjectName("btn_refresh")
        btn_ref.clicked.connect(self._refresh_scene)
        lay.addWidget(btn_ref)

        return lay

    def _build_axis_options(self) -> QtWidgets.QHBoxLayout:
        lay = QtWidgets.QHBoxLayout()
        lay.setSpacing(12)

        lbl = QtWidgets.QLabel("ALIGN AXES")
        lbl.setObjectName("lbl_section")
        lay.addWidget(lbl)

        self._chk_pos_x = QtWidgets.QCheckBox("PX")
        self._chk_pos_y = QtWidgets.QCheckBox("PY")
        self._chk_pos_z = QtWidgets.QCheckBox("PZ")
        self._chk_rot_x = QtWidgets.QCheckBox("RX")
        self._chk_rot_y = QtWidgets.QCheckBox("RY")
        self._chk_rot_z = QtWidgets.QCheckBox("RZ")

        for chk in [self._chk_pos_x, self._chk_pos_y, self._chk_pos_z,
                    self._chk_rot_x, self._chk_rot_y, self._chk_rot_z]:
            chk.setChecked(True)
            lay.addWidget(chk)

        lay.addStretch()
        return lay

    def _build_dual_panel(self) -> QtWidgets.QHBoxLayout:
        lay = QtWidgets.QHBoxLayout()
        lay.setSpacing(6)

        # ── Source (left) ──────────────────────────────────────────────────
        left = QtWidgets.QVBoxLayout()
        left.setSpacing(3)

        hdr_cur = QtWidgets.QHBoxLayout()
        lbl_cur = QtWidgets.QLabel("SOURCE")
        lbl_cur.setObjectName("lbl_panel")
        hdr_cur.addWidget(lbl_cur)
        hdr_cur.addStretch()
        btn_pick_cur = QtWidgets.QPushButton("⊕ Pick")
        btn_pick_cur.setObjectName("btn_pick_cur")
        btn_pick_cur.setToolTip("Use viewport selection as Source root.")
        btn_pick_cur.clicked.connect(self._pick_current)
        hdr_cur.addWidget(btn_pick_cur)
        left.addLayout(hdr_cur)

        self._tree_cur = HierarchyTree("Current")
        self._tree_cur.nodeSelected.connect(self._on_cur_selected)
        left.addWidget(self._tree_cur)

        self._lbl_cur_sel = QtWidgets.QLabel("—")
        self._lbl_cur_sel.setStyleSheet(f"color:{TEXT_DIM}; font-size:10px;")
        left.addWidget(self._lbl_cur_sel)

        lay.addLayout(left, stretch=1)

        # Arrow
        arrow_lbl = QtWidgets.QLabel("→")
        arrow_lbl.setStyleSheet(f"color:{TEXT_DIM}; font-size:18px; padding:0 4px;")
        arrow_lbl.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter if _PYSIDE_VER == 6
            else QtCore.Qt.AlignCenter
        )
        lay.addWidget(arrow_lbl)

        # ── Target (right) ─────────────────────────────────────────────────
        right = QtWidgets.QVBoxLayout()
        right.setSpacing(3)

        hdr_tgt = QtWidgets.QHBoxLayout()
        lbl_tgt = QtWidgets.QLabel("TARGET")
        lbl_tgt.setObjectName("lbl_panel")
        hdr_tgt.addWidget(lbl_tgt)
        hdr_tgt.addStretch()
        btn_pick_tgt = QtWidgets.QPushButton("⊕ Pick")
        btn_pick_tgt.setObjectName("btn_pick_tgt")
        btn_pick_tgt.setToolTip("Use viewport selection as Target root.")
        btn_pick_tgt.clicked.connect(self._pick_target)
        hdr_tgt.addWidget(btn_pick_tgt)
        right.addLayout(hdr_tgt)

        self._tree_tgt = HierarchyTree("Target")
        self._tree_tgt.nodeSelected.connect(self._on_tgt_selected)
        right.addWidget(self._tree_tgt)

        self._lbl_tgt_sel = QtWidgets.QLabel("—")
        self._lbl_tgt_sel.setStyleSheet(f"color:{TEXT_DIM}; font-size:10px;")
        right.addWidget(self._lbl_tgt_sel)

        lay.addLayout(right, stretch=1)

        return lay

    def _build_action_row(self) -> QtWidgets.QHBoxLayout:
        lay = QtWidgets.QHBoxLayout()
        lay.setSpacing(8)

        btn_preview = QtWidgets.QPushButton("Preview Pairs")
        btn_preview.setObjectName("btn_preview")
        btn_preview.setToolTip("Build the pair list without executing alignment.")
        btn_preview.clicked.connect(self._preview_pairs)
        lay.addWidget(btn_preview)

        btn_match = QtWidgets.QPushButton("⦿  Match  _prefix")
        btn_match.setObjectName("btn_match")
        btn_match.setToolTip(
            "Scans scene for nodes named with _ prefix.\n"
            "Example:  _Spine01 → Spine01\n"
            "Ordered parent → child (DFS)."
        )
        btn_match.clicked.connect(self._auto_match_prefix)
        lay.addWidget(btn_match)

        lay.addStretch()

        self._btn_align = QtWidgets.QPushButton("▶  Auto Align All")
        self._btn_align.setObjectName("btn_align")
        self._btn_align.setToolTip(
            "Walks parent → child for both hierarchies and aligns each pair.\n"
            "World Position XYZ + Orientation (Local) XYZ."
        )
        self._btn_align.clicked.connect(self._execute_align)
        lay.addWidget(self._btn_align)

        self._btn_orient = QtWidgets.QPushButton("◎  Orientation Constraint")
        self._btn_orient.setObjectName("btn_orient")
        self._btn_orient.setToolTip(
            "Applies a 3ds Max Orientation Constraint to every source bone.\n"
            "Each source node gets its rotation driven by its matched\n"
            "_prefix target node (retarget bone match).\n"
            "Uses the same _prefix pairs as Auto Align All."
        )
        self._btn_orient.clicked.connect(self._execute_orient_constraint)
        lay.addWidget(self._btn_orient)

        return lay

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _make_sep(self) -> QtWidgets.QFrame:
        f = QtWidgets.QFrame()
        f.setObjectName("sep")
        f.setFrameShape(_Frame_HLine)
        return f

    # ── Scene refresh ─────────────────────────────────────────────────────────

    def _refresh_scene(self):
        self._tree_cur.refresh()
        self._tree_tgt.refresh()
        self._pairs.clear()
        self._prefix_src_nodes = None
        self._prefix_tgt_nodes = None
        self._pair_table.load_pairs([])
        self._set_status("Scene refreshed.")

    # ── Viewport pick ─────────────────────────────────────────────────────────

    def _pick_current(self):
        if not _IN_MAX:
            self._set_status("Not running inside 3ds Max.", error=True)
            return
        sel = list(rt.selection)
        if not sel:
            self._set_status("Nothing selected in viewport.", error=True)
            return
        name = str(sel[0].name)
        if not self._tree_cur._node_map:
            self._set_status("Tree empty — click Refresh first.", error=True)
            return
        if not self._tree_cur._select_by_name(name):
            self._set_status(f"'{name}' not in tree. Refresh and try again.", error=True)
            return
        self._lbl_cur_sel.setText(name)
        self._set_status(f"Source: {name}")
        self._auto_preview()

    def _pick_target(self):
        if not _IN_MAX:
            self._set_status("Not running inside 3ds Max.", error=True)
            return
        sel = list(rt.selection)
        if not sel:
            self._set_status("Nothing selected in viewport.", error=True)
            return
        name = str(sel[0].name)
        if not self._tree_tgt._node_map:
            self._set_status("Tree empty — click Refresh first.", error=True)
            return
        if not self._tree_tgt._select_by_name(name):
            self._set_status(f"'{name}' not in tree. Refresh and try again.", error=True)
            return
        self._lbl_tgt_sel.setText(name)
        self._set_status(f"Target: {name}")
        self._auto_preview()

    # ── Selection callbacks ───────────────────────────────────────────────────

    def _on_cur_selected(self, name: str):
        self._lbl_cur_sel.setText(name)
        self._prefix_src_nodes = None
        self._prefix_tgt_nodes = None
        self._auto_preview()

    def _on_tgt_selected(self, name: str):
        self._lbl_tgt_sel.setText(name)
        self._prefix_src_nodes = None
        self._prefix_tgt_nodes = None
        self._auto_preview()

    # ── Pair building ─────────────────────────────────────────────────────────

    def _build_pairs(self) -> Optional[List[tuple]]:
        src_root = self._tree_cur.selected_max_node()
        tgt_root = self._tree_tgt.selected_max_node()

        if _IN_MAX:
            if src_root is None or tgt_root is None:
                self._set_status("Select a root node in both panels.", error=True)
                return None
            src_list = _hierarchy_flat(src_root)
            tgt_list = _hierarchy_flat(tgt_root)
        else:
            src_list = ["Root_A", "Child_A1", "Child_A2"]
            tgt_list = ["Root_B", "Child_B1", "Child_B2"]

        pairs = []
        for s, t in zip(src_list, tgt_list):
            sn = str(s.name) if _IN_MAX else s
            tn = str(t.name) if _IN_MAX else t
            pairs.append((sn, tn))
        return pairs

    def _auto_preview(self):
        pairs = self._build_pairs()
        if pairs is None:
            return
        self._pairs = pairs
        self._pair_table.load_pairs(pairs)
        self._set_status(f"{len(pairs)} pair(s) ready.")

    def _preview_pairs(self):
        pairs = self._build_pairs()
        if pairs is None:
            return
        self._pairs = pairs
        self._pair_table.load_pairs(pairs)
        self._set_status(f"{len(pairs)} pair(s) queued.")

    # ── Auto Match _prefix ────────────────────────────────────────────────────

    def _auto_match_prefix(self):
        if not _IN_MAX:
            demo = [("Root", "_Root"), ("Spine01", "_Spine01"), ("Spine02", "_Spine02")]
            self._pairs = demo
            self._pair_table.load_pairs(demo)
            self._set_status(f"[Demo] {len(demo)} _prefix pairs.")
            return

        name_map: dict = {}
        for node in rt.objects:
            try:
                name_map[str(node.name)] = node
            except Exception:
                pass

        ordered_src: List = []
        ordered_tgt: List = []
        seen_src: set = set()

        for node in _all_scene_nodes_hierarchy():
            try:
                src_name = str(node.name)
            except Exception:
                continue
            if src_name.startswith("_"):
                continue
            tgt_name = "_" + src_name
            if tgt_name in name_map and src_name not in seen_src:
                seen_src.add(src_name)
                ordered_src.append(node)
                ordered_tgt.append(name_map[tgt_name])

        if not ordered_src:
            self._set_status("No _prefix pairs found in scene.", error=True)
            return

        pairs = [(str(s.name), str(t.name)) for s, t in zip(ordered_src, ordered_tgt)]
        self._pairs = pairs
        self._prefix_src_nodes = ordered_src
        self._prefix_tgt_nodes = ordered_tgt
        self._pair_table.load_pairs(pairs)
        self._set_status(f"{len(pairs)} _prefix pair(s) matched.")

    # ── Alignment execution ───────────────────────────────────────────────────

    def _execute_align(self):
        use_prefix = (
            self._prefix_src_nodes is not None
            and self._prefix_tgt_nodes is not None
            and len(self._prefix_src_nodes) > 0
            and self._pairs
        )

        if use_prefix:
            src_list = self._prefix_src_nodes
            tgt_list = self._prefix_tgt_nodes
            pairs    = self._pairs
        else:
            pairs = self._build_pairs()
            if pairs is None:
                return
            if not pairs:
                self._set_status("No pairs to align.", error=True)
                return
            self._pairs = pairs
            self._pair_table.load_pairs(pairs)
            if _IN_MAX:
                src_root = self._tree_cur.selected_max_node()
                tgt_root = self._tree_tgt.selected_max_node()
                src_list = _hierarchy_flat(src_root)
                tgt_list = _hierarchy_flat(tgt_root)
            else:
                src_list = []
                tgt_list = []

        self._tree_cur.clear_highlights()
        self._tree_tgt.clear_highlights()

        done     = 0
        mismatch = 0

        if _IN_MAX:
            do_pos = (self._chk_pos_x.isChecked(),
                      self._chk_pos_y.isChecked(),
                      self._chk_pos_z.isChecked())
            do_rot = (self._chk_rot_x.isChecked(),
                      self._chk_rot_y.isChecked(),
                      self._chk_rot_z.isChecked())

            for row, (src_node, tgt_node) in enumerate(zip(src_list, tgt_list)):
                try:
                    self._align_node_axes(src_node, tgt_node, do_pos, do_rot)
                    self._pair_table.mark_done(row)
                    self._tree_cur.highlight_row(str(src_node.name), done=True)
                    self._tree_tgt.highlight_row(str(tgt_node.name), done=True)
                    done += 1
                except Exception:
                    self._pair_table.mark_mismatch(row)
                    mismatch += 1
        else:
            for row in range(len(pairs)):
                self._pair_table.mark_done(row)
            done = len(pairs)

        self._prefix_src_nodes = None
        self._prefix_tgt_nodes = None

        status = f"✔  Aligned {done} pair(s)."
        if mismatch:
            status += f"  {mismatch} error(s)."
        self._set_status(status, error=bool(mismatch))

    def _align_node_axes(self, src_node, tgt_node, do_pos: tuple, do_rot: tuple):
        tgt_tm = tgt_node.transform
        src_tm = src_node.transform

        tgt_pos = tgt_tm.pos
        src_pos = src_tm.pos
        new_x = tgt_pos.x if do_pos[0] else src_pos.x
        new_y = tgt_pos.y if do_pos[1] else src_pos.y
        new_z = tgt_pos.z if do_pos[2] else src_pos.z
        new_pos = rt.Point3(new_x, new_y, new_z)

        tgt_euler = rt.quatToEuler(tgt_tm.rotation)
        src_euler = rt.quatToEuler(src_tm.rotation)
        new_ex = tgt_euler.x if do_rot[0] else src_euler.x
        new_ey = tgt_euler.y if do_rot[1] else src_euler.y
        new_ez = tgt_euler.z if do_rot[2] else src_euler.z
        new_rot = rt.eulerToQuat(rt.eulerAngles(new_ex, new_ey, new_ez))

        scl = src_tm.scalepart
        new_tm = rt.matrix3(1)
        new_tm.rotation = new_rot
        new_tm.pos      = new_pos
        scale_tm = rt.scaleMatrix(scl)
        src_node.transform = scale_tm * new_tm

    # ── Orientation Constraint ────────────────────────────────────────────────

    def _execute_orient_constraint(self):
        """
        For every (src, tgt) pair (resolved the same way as Auto Align All):
          • Assigns an Orientation Constraint controller to src_node's rotation.
          • Adds tgt_node as the 100% weight target.

        This makes the source bone's rotation permanently driven by the
        _prefix target bone — the classic retarget-bone-match workflow.

        Existing Orientation Constraints on a node are replaced.
        """
        if not _IN_MAX:
            self._set_status("Orientation Constraint requires 3ds Max runtime.", error=True)
            return

        # ── Resolve pairs (same logic as _execute_align) ─────────────────────
        use_prefix = (
            self._prefix_src_nodes is not None
            and self._prefix_tgt_nodes is not None
            and len(self._prefix_src_nodes) > 0
            and self._pairs
        )

        if use_prefix:
            src_list = self._prefix_src_nodes
            tgt_list = self._prefix_tgt_nodes
            pairs    = self._pairs
        else:
            pairs = self._build_pairs()
            if pairs is None:
                return
            if not pairs:
                self._set_status("No pairs to constrain.", error=True)
                return
            self._pairs = pairs
            self._pair_table.load_pairs(pairs)
            src_root = self._tree_cur.selected_max_node()
            tgt_root = self._tree_tgt.selected_max_node()
            src_list = _hierarchy_flat(src_root)
            tgt_list = _hierarchy_flat(tgt_root)

        self._tree_cur.clear_highlights()
        self._tree_tgt.clear_highlights()

        done     = 0
        mismatch = 0

        for row, (src_node, tgt_node) in enumerate(zip(src_list, tgt_list)):
            try:
                # Create a fresh Orientation Constraint controller
                ctrl = rt.Orientation_Constraint()
                # Assign it to the source node's rotation track
                src_node.rotation.controller = ctrl
                # Add the target node with 100% weight
                ctrl.appendTarget(tgt_node, 100)
                # Keep Initial Offset (relative = on)
                ctrl.relative = True

                self._pair_table.mark_done(row)
                self._tree_cur.highlight_row(str(src_node.name), done=True)
                self._tree_tgt.highlight_row(str(tgt_node.name), done=True)
                done += 1
            except Exception as e:
                self._pair_table.mark_mismatch(row)
                mismatch += 1

        self._prefix_src_nodes = None
        self._prefix_tgt_nodes = None

        status = f"◎  Orientation Constraint applied to {done} bone(s)."
        if mismatch:
            status += f"  {mismatch} error(s)."
        self._set_status(status, error=bool(mismatch))

    # ── Status ────────────────────────────────────────────────────────────────

    def _set_status(self, msg: str, error: bool = False):
        color = ACCENT_ERR if error else TEXT_DIM
        self._lbl_status.setStyleSheet(f"color:{color}; font-size:10px; padding:2px 4px;")
        self._lbl_status.setText(msg)


# ═══════════════════════════════════════════════════════════════════════════════
#  SINGLETON LAUNCHER
# ═══════════════════════════════════════════════════════════════════════════════

_window_instance: Optional[AlignAutoWindow] = None


def launch():
    global _window_instance

    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])

    if _window_instance is not None:
        try:
            _window_instance.close()
        except Exception:
            pass

    parent = _max_main_window()
    _window_instance = AlignAutoWindow(parent=parent)
    _window_instance.show()
    _window_instance.raise_()
    _window_instance.activateWindow()

    return _window_instance


# ── Direct run for offline testing ────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    w = AlignAutoWindow()
    w.show()
    sys.exit(app.exec() if _PYSIDE_VER == 6 else app.exec_())
