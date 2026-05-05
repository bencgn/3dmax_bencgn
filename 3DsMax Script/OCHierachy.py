from __future__ import annotations
from typing import List, Optional
import functools

# ── 3ds Max runtime ──────────────────────────────────────────────────────────
try:
    import pymxs
    from pymxs import runtime as rt
    _IN_MAX = True
except ImportError:
    _IN_MAX = False

# ── Qt (PySide6 for 3ds Max 2025) ────────────────────────────────────────────
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
    pass


# ═══════════════════════════════════════════════════════════════════════════════
#  COLOUR PALETTE
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
ACCENT_ERR  = "#ff4444"
HIGHLIGHT   = "rgba(255,255,255,0.07)"
DONE_BG     = "rgba(255,255,255,0.05)"


# ═══════════════════════════════════════════════════════════════════════════════
#  MAX HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_node(name: str):
    if not _IN_MAX: return None
    return rt.getNodeByName(name, exact=True)

def _hierarchy_flat(root_node) -> List:
    result = []
    def _walk(n):
        result.append(n)
        try: kids = list(n.children)
        except Exception: kids = []
        for k in kids: _walk(k)
    _walk(root_node)
    return result

def _scene_roots() -> List:
    if not _IN_MAX: return []
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
        if not _IN_MAX: return

        def _add_children(parent_item, node):
            try: kids = list(node.children)
            except Exception: kids = []
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
        if not items: return None
        return items[0].data(0, QtCore.Qt.ItemDataRole.UserRole)

    def selected_max_node(self):
        name = self.selected_node_name()
        if name is None: return None
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
                if _scan(item.child(i)): return True
            return False
        for i in range(self.topLevelItemCount()):
            _scan(self.topLevelItem(i))

    def clear_highlights(self):
        def _clear(item):
            item.setBackground(0, QtGui.QBrush())
            for i in range(item.childCount()): _clear(item.child(i))
        for i in range(self.topLevelItemCount()): _clear(self.topLevelItem(i))

    def _select_by_name(self, name: str) -> bool:
        def _find(item):
            if item.data(0, QtCore.Qt.ItemDataRole.UserRole) == name: return item
            for i in range(item.childCount()):
                found = _find(item.child(i))
                if found: return found
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
        if name: self.nodeSelected.emit(name)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAIR TABLE
# ═══════════════════════════════════════════════════════════════════════════════

class PairTableWidget(QtWidgets.QTableWidget):
    actionRequested = QtCore.Signal(int)

    _HDR = ["#", "Source", "Action", "Target"]

    def __init__(self, parent=None):
        super().__init__(0, 4, parent)
        self.setHorizontalHeaderLabels(self._HDR)
        self.horizontalHeader().setSectionResizeMode(0, _HV_Content)
        self.horizontalHeader().setSectionResizeMode(1, _HV_Stretch)
        self.horizontalHeader().setSectionResizeMode(2, _HV_Content)
        self.horizontalHeader().setSectionResizeMode(3, _HV_Stretch)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setMinimumHeight(80)

    def load_pairs(self, pairs: List[tuple]):
        self.setRowCount(0)
        for i, (src, tgt) in enumerate(pairs):
            self.insertRow(i)
            idx_item = QtWidgets.QTableWidgetItem(str(i + 1))
            idx_item.setForeground(QtGui.QColor(TEXT_DIM))

            src_item = QtWidgets.QTableWidgetItem(src)
            src_item.setForeground(QtGui.QColor(TEXT_PRI))

            # Make the arrow an actual Action Button so user can test row by row
            btn = QtWidgets.QPushButton("⇛ Apply OC")
            btn.setObjectName("btn_row_action")
            btn.setCursor(Qt.CursorShape.PointingHandCursor if _PYSIDE_VER == 6 else Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton#btn_row_action {{
                    background: transparent; color: {TEXT_PRI};
                    border: 1px solid {BORDER}; border-radius: 4px; padding: 2px 6px;
                }}
                QPushButton#btn_row_action:hover {{ background: {HIGHLIGHT}; }}
            """)
            btn.clicked.connect(functools.partial(self._on_action_click, i))

            tgt_item = QtWidgets.QTableWidgetItem(tgt)
            tgt_item.setForeground(QtGui.QColor(TEXT_MUT))

            self.setItem(i, 0, idx_item)
            self.setItem(i, 1, src_item)
            self.setCellWidget(i, 2, btn)
            self.setItem(i, 3, tgt_item)

    def _on_action_click(self, row_idx: int):
        self.actionRequested.emit(row_idx)

    def mark_done(self, row: int):
        for col in [0, 1, 3]:
            item = self.item(row, col)
            if item:
                item.setForeground(QtGui.QColor(ACCENT))
                item.setBackground(QtGui.QColor(DONE_BG))

    def mark_mismatch(self, row: int):
        for col in [0, 1, 3]:
            item = self.item(row, col)
            if item: item.setForeground(QtGui.QColor(ACCENT_ERR))


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

class OCHierarchyWindow(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("OC Hierarchy Config")
        self.setMinimumSize(560, 600)
        self.resize(600, 650)
        self.setWindowFlags(self.windowFlags() | _WinMin | _WinMax)
        self._pairs: List[tuple] = []
        self._prefix_src_nodes: Optional[List] = None
        self._prefix_tgt_nodes: Optional[List] = None
        self._apply_stylesheet()
        self._build_ui()

    def _apply_stylesheet(self):
        self.setStyleSheet(f"""
            * {{ font-family: "Segoe UI", "Inter", sans-serif; font-size: 12px; }}
            QDialog {{ background: {BG_WIN}; color: {TEXT_PRI}; }}
            QLabel {{ color: {TEXT_PRI}; }}
            QLabel#lbl_title {{ color: {ACCENT}; font-size: 16px; font-weight: 700; letter-spacing: 2px; }}
            QLabel#lbl_sub {{ color: {TEXT_DIM}; font-size: 10px; }}
            QLabel#lbl_section, QLabel#lbl_panel {{ color: {TEXT_MUT}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; }}
            QFrame#sep {{ background: {BORDER}; max-height: 1px; border: none; }}
            QGroupBox {{ border: 1px solid {BORDER}; border-radius: 5px; margin-top: 10px; padding-top: 15px; color: {TEXT_MUT}; font-weight: bold; background: {BG_PANEL}; }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; left: 10px; color: {TEXT_PRI}; }}
            QPushButton {{ background: {BG_CARD}; color: {TEXT_MUT}; border: 1px solid {BORDER}; border-radius: 5px; padding: 5px 12px; font-weight: 500; }}
            QPushButton:hover {{ background: {BG_ITEM}; color: {TEXT_PRI}; border-color: {TEXT_MUT}; }}
            QPushButton:pressed {{ background: {BG_WIN}; }}
            QPushButton#btn_refresh, QPushButton#btn_pick {{ background: transparent; color: {TEXT_DIM}; border: 1px solid {BORDER}; font-size: 10px; }}
            QPushButton#btn_refresh:hover, QPushButton#btn_pick:hover {{ color: {TEXT_PRI}; border-color: {TEXT_MUT}; }}
            QPushButton#btn_match {{ background: {BG_CARD}; color: {TEXT_PRI}; font-weight: 600; }}
            QPushButton#btn_match:hover {{ background: {BG_ITEM}; border-color: {TEXT_MUT}; }}
            QPushButton#btn_apply {{ background: {ACCENT}; color: {BG_WIN}; font-size: 13px; font-weight: 700; border: none; padding: 8px 20px; }}
            QPushButton#btn_apply:hover {{ background: #dddddd; }}
            QTreeWidget, QTableWidget {{ background: {BG_CARD}; color: {TEXT_MUT}; border: 1px solid {BORDER}; border-radius: 5px; outline: none; alternate-background-color: {BG_ITEM}; }}
            QTreeWidget::item:selected {{ background: {HIGHLIGHT}; color: {TEXT_PRI}; }}
            QHeaderView::section {{ background: {BG_PANEL}; color: {TEXT_DIM}; border: none; border-bottom: 1px solid {BORDER}; padding: 4px 6px; font-size: 10px; font-weight: 600; }}
            QRadioButton, QCheckBox {{ color: {TEXT_PRI}; spacing: 8px; }}
            QRadioButton::indicator, QCheckBox::indicator {{ width: 14px; height: 14px; background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 7px; }}
            QCheckBox::indicator {{ border-radius: 3px; }}
            QRadioButton::indicator:checked, QCheckBox::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}
        """)

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 10)
        root.setSpacing(8)

        # Header
        hdr = QtWidgets.QHBoxLayout()
        t = QtWidgets.QLabel("OC HIERARCHY")
        t.setObjectName("lbl_title")
        hdr.addWidget(t)
        sub = QtWidgets.QLabel("Orientation Constraint Config")
        sub.setObjectName("lbl_sub")
        hdr.addWidget(sub)
        hdr.addStretch()
        btn_ref = QtWidgets.QPushButton("⟳ Refresh Trees")
        btn_ref.setObjectName("btn_refresh")
        btn_ref.clicked.connect(self._refresh_scene)
        hdr.addWidget(btn_ref)
        root.addLayout(hdr)
        
        f = QtWidgets.QFrame()
        f.setObjectName("sep"); f.setFrameShape(_Frame_HLine)
        root.addWidget(f)

        # Main Splitter for resizable height
        splitter = QtWidgets.QSplitter(Qt.Orientation.Vertical if _PYSIDE_VER == 6 else Qt.Vertical)
        splitter.setChildrenCollapsible(False)
        splitter.setStyleSheet(f"QSplitter::handle {{ background: {BORDER}; margin: 6px 0; }}")

        top_widget = QtWidgets.QWidget()
        top_lay = QtWidgets.QVBoxLayout(top_widget)
        top_lay.setContentsMargins(0, 0, 0, 0)
        top_lay.setSpacing(8)

        # Trees
        panel = QtWidgets.QHBoxLayout()
        panel.setSpacing(6)

        left = QtWidgets.QVBoxLayout(); left.setSpacing(3)
        l_hdr = QtWidgets.QHBoxLayout()
        l_lbl = QtWidgets.QLabel("SOURCE (Usually Driver)"); l_lbl.setObjectName("lbl_panel")
        l_hdr.addWidget(l_lbl); l_hdr.addStretch()
        l_btn = QtWidgets.QPushButton("⊕ Pick")
        l_btn.setObjectName("btn_pick"); l_btn.clicked.connect(self._pick_source)
        l_hdr.addWidget(l_btn)
        left.addLayout(l_hdr)
        self._tree_src = HierarchyTree("Source")
        self._tree_src.nodeSelected.connect(self._auto_preview)
        left.addWidget(self._tree_src)
        panel.addLayout(left, 1)

        arrow_lbl = QtWidgets.QLabel("⇛")
        arrow_lbl.setStyleSheet(f"color:{TEXT_DIM}; font-size:18px;")
        panel.addWidget(arrow_lbl)

        right = QtWidgets.QVBoxLayout(); right.setSpacing(3)
        r_hdr = QtWidgets.QHBoxLayout()
        r_lbl = QtWidgets.QLabel("TARGET (Usually Driven)"); r_lbl.setObjectName("lbl_panel")
        r_hdr.addWidget(r_lbl); r_hdr.addStretch()
        r_btn = QtWidgets.QPushButton("⊕ Pick")
        r_btn.setObjectName("btn_pick"); r_btn.clicked.connect(self._pick_target)
        r_hdr.addWidget(r_btn)
        right.addLayout(r_hdr)
        self._tree_tgt = HierarchyTree("Target")
        self._tree_tgt.nodeSelected.connect(self._auto_preview)
        right.addWidget(self._tree_tgt)
        panel.addLayout(right, 1)

        top_lay.addLayout(panel, 1)

        # --- CONFIG PANEL ---
        grp_box = QtWidgets.QGroupBox("Constraint Configuration")
        grp_lay = QtWidgets.QVBoxLayout(grp_box)
        grp_lay.setSpacing(8)

        # Direction radio
        dir_lay = QtWidgets.QHBoxLayout()
        self._rad_tgt_gets = QtWidgets.QRadioButton("Target bone GETS constraint (Source Drives)")
        self._rad_src_gets = QtWidgets.QRadioButton("Source bone GETS constraint (Target Drives)")
        self._rad_tgt_gets.setChecked(True) # Default: Target receives constraint
        
        dir_lay.addWidget(QtWidgets.QLabel("Direction: "))
        dir_lay.addWidget(self._rad_tgt_gets)
        dir_lay.addWidget(self._rad_src_gets)
        dir_lay.addStretch()
        grp_lay.addLayout(dir_lay)

        # Relative toggle
        self._chk_relative = QtWidgets.QCheckBox("Keep Initial Offset (relative = on)")
        self._chk_relative.setChecked(True)
        grp_lay.addWidget(self._chk_relative)
        
        top_lay.addWidget(grp_box)
        splitter.addWidget(top_widget)

        bot_widget = QtWidgets.QWidget()
        bot_lay = QtWidgets.QVBoxLayout(bot_widget)
        bot_lay.setContentsMargins(0, 0, 0, 0)
        bot_lay.setSpacing(8)

        # Pairs Table
        plbl = QtWidgets.QLabel("PAIRED BONES (Click ⇛ Apply OC to test single bone)"); plbl.setObjectName("lbl_section")
        bot_lay.addWidget(plbl)
        self._pair_table = PairTableWidget()
        self._pair_table.actionRequested.connect(self._execute_single_row)
        bot_lay.addWidget(self._pair_table, 1)
        
        splitter.addWidget(bot_widget)
        splitter.setSizes([350, 200])

        root.addWidget(splitter, 1)

        # Actions
        act = QtWidgets.QHBoxLayout(); act.setSpacing(8)
        btn_match = QtWidgets.QPushButton("⦿ Match via _prefix")
        btn_match.setObjectName("btn_match")
        btn_match.setToolTip("Auto-pair objects globally using the _ prefix. (e.g., Spine2_159 -> _Spine2_159)")
        btn_match.clicked.connect(self._auto_match_prefix)
        act.addWidget(btn_match)
        act.addStretch()
        self._btn_apply = QtWidgets.QPushButton("▶ Build All Constraints")
        self._btn_apply.setObjectName("btn_apply")
        self._btn_apply.clicked.connect(self._execute_constraints_all)
        act.addWidget(self._btn_apply)
        root.addLayout(act)

        # Status
        self._lbl_status = QtWidgets.QLabel("Ready. Pick roots, select config, and Apply.")
        self._lbl_status.setStyleSheet(f"color:{TEXT_DIM}; font-size:10px;")
        root.addWidget(self._lbl_status)

    def _refresh_scene(self):
        self._tree_src.refresh()
        self._tree_tgt.refresh()
        self._pairs.clear()
        self._prefix_src_nodes = None
        self._prefix_tgt_nodes = None
        self._pair_table.load_pairs([])
        self._set_status("Scene refreshed.")

    def _pick_source(self):
        if not _IN_MAX: return
        sel = list(rt.selection)
        if sel and self._tree_src._select_by_name(str(sel[0].name)):
            self._auto_preview()

    def _pick_target(self):
        if not _IN_MAX: return
        sel = list(rt.selection)
        if sel and self._tree_tgt._select_by_name(str(sel[0].name)):
            self._auto_preview()

    def _build_pairs(self) -> Optional[List[tuple]]:
        s_node = self._tree_src.selected_max_node()
        t_node = self._tree_tgt.selected_max_node()
        if _IN_MAX and (s_node is None or t_node is None):
            return None
        
        s_list = _hierarchy_flat(s_node) if _IN_MAX else []
        t_list = _hierarchy_flat(t_node) if _IN_MAX else []
        
        pairs = []
        for s, t in zip(s_list, t_list):
            pairs.append((str(s.name), str(t.name)))
        return pairs

    def _auto_preview(self, *_):
        pairs = self._build_pairs()
        if pairs is None: return
        self._pairs = pairs
        self._pair_table.load_pairs(pairs)
        self._set_status(f"Direct pair mode: {len(pairs)} pairs ready.")

    def _auto_match_prefix(self):
        if not _IN_MAX: return
        
        name_map = {}
        for node in rt.objects:
            try: name_map[str(node.name)] = node
            except: pass

        ordered_src, ordered_tgt, seen_src = [], [], set()

        for node in _all_scene_nodes_hierarchy():
            try: src_name = str(node.name)
            except Exception: continue
            
            if src_name.startswith("_"): continue
            tgt_name = "_" + src_name
            
            if tgt_name in name_map and src_name not in seen_src:
                seen_src.add(src_name)
                ordered_src.append(node)
                ordered_tgt.append(name_map[tgt_name])

        if not ordered_src:
            self._set_status("No _prefix pairings found.", error=True)
            return

        pairs = [(str(s.name), str(t.name)) for s, t in zip(ordered_src, ordered_tgt)]
        self._pairs = pairs
        self._prefix_src_nodes = ordered_src
        self._prefix_tgt_nodes = ordered_tgt
        self._pair_table.load_pairs(pairs)
        self._set_status(f"Prefix mapping: {len(pairs)} pairs matched.")

    def _execute_single_row(self, row_idx: int):
        # Applies constraint to a single row to test it
        if not _IN_MAX or not self._pairs or row_idx >= len(self._pairs):
            return

        s_name, t_name = self._pairs[row_idx]
        src_node = rt.getNodeByName(s_name, exact=True)
        tgt_node = rt.getNodeByName(t_name, exact=True)

        if not src_node or not tgt_node:
            self._pair_table.mark_mismatch(row_idx)
            self._set_status(f"Cannot find nodes for row {row_idx+1}", error=True)
            return

        success = self._apply_constraint(src_node, tgt_node)
        
        if success:
            self._pair_table.mark_done(row_idx)
            self._set_status(f"✔ Row {row_idx+1}: Constraint Applied.")
        else:
            self._pair_table.mark_mismatch(row_idx)
            self._set_status(f"Row {row_idx+1}: Constraint Failed.", error=True)

    def _execute_constraints_all(self):
        if not _IN_MAX or not self._pairs:
            self._set_status("No pairs loaded.", error=True)
            return

        done, mismatch = 0, 0
        
        for row, (s_name, t_name) in enumerate(self._pairs):
            src_node = rt.getNodeByName(s_name, exact=True)
            tgt_node = rt.getNodeByName(t_name, exact=True)
            if not src_node or not tgt_node:
                self._pair_table.mark_mismatch(row)
                mismatch += 1
                continue

            success = self._apply_constraint(src_node, tgt_node)
            if success:
                self._pair_table.mark_done(row)
                self._tree_src.highlight_row(str(src_node.name), done=True)
                self._tree_tgt.highlight_row(str(tgt_node.name), done=True)
                done += 1
            else:
                self._pair_table.mark_mismatch(row)
                mismatch += 1

        self._prefix_src_nodes = None
        self._prefix_tgt_nodes = None

        status = f"✔ Constraints Built for {done} bones."
        if mismatch: status += f" ({mismatch} errors)"
        self._set_status(status, error=bool(mismatch))

    def _apply_constraint(self, src_node, tgt_node) -> bool:
        try:
            keep_offset = self._chk_relative.isChecked()
            
            if self._rad_tgt_gets.isChecked():
                driver_node, driven_node = src_node, tgt_node
            else:
                driver_node, driven_node = tgt_node, src_node

            # Bypass pymxs MXSWrapperBase bugs by executing the controller assignment in native MaxScript
            rt.tmp_driven = driven_node
            rt.tmp_driver = driver_node
            rt.tmp_keep_offset = keep_offset
            
            ms_code = """
            try (
                local oc = Orientation_Constraint()
                
                -- Wrap existing rotation in a Rotation_List (preserves manual rotation)
                if classOf ::tmp_driven.rotation.controller != Rotation_List do (
                    ::tmp_driven.rotation.controller = Rotation_List()
                )
                
                -- Add to the list (MaxScript smoothly accesses the .Available SubAnim)
                ::tmp_driven.rotation.controller.Available.controller = oc
                
                -- Make it the active controller in the list
                ::tmp_driven.rotation.controller.setActive ::tmp_driven.rotation.controller.count
                
                -- Append target and keep offset
                oc.appendTarget ::tmp_driver 100
                oc.relative = ::tmp_keep_offset
                
                true
            ) catch (
                print (getCurrentException())
                false
            )
            """
            success = rt.execute(ms_code)
            
            # Clean up globals
            rt.tmp_driven = None
            rt.tmp_driver = None
            
            return success
        except Exception as e:
            print("Error applying OC:", e)
            return False

    def _set_status(self, msg: str, error: bool = False):
        c = ACCENT_ERR if error else TEXT_DIM
        self._lbl_status.setStyleSheet(f"color:{c}; font-size:10px;")
        self._lbl_status.setText(msg)


# ═══════════════════════════════════════════════════════════════════════════════
#  LAUNCH
# ═══════════════════════════════════════════════════════════════════════════════

_window_instance = None

def launch():
    global _window_instance
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    if _window_instance is not None:
        try: _window_instance.close()
        except: pass
    _window_instance = OCHierarchyWindow(_max_main_window())
    _window_instance.show()
    return _window_instance

if __name__ == "__main__":
    launch()

