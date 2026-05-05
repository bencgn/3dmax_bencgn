"""
ToolName — Object Name Manager for 3ds Max
==========================================
Button 1 · Extract Name to JSON
    Export selected objects (parent→child order) to JSON.
    Each entry: { "name", "type", "type_change" }

Button 2 · Import JSON Name
    Rename selected scene objects using "type_change" values in the JSON.

Usage:
    import importlib, sys
    sys.path.insert(0, r"D:\\3dmax_bencgn\\3dmax_bencgn\\3DsMax Script")
    import ToolName; importlib.reload(ToolName); ToolName.launch()
"""

from __future__ import annotations
import json, os, sys
from collections import deque
from typing import Dict, List, Optional, Set

# ── 3ds Max ──────────────────────────────────────────────────────────────────
try:
    from pymxs import runtime as rt
    _IN_MAX = True
except ImportError:
    _IN_MAX = False

# ── Qt ───────────────────────────────────────────────────────────────────────
try:
    from PySide6 import QtCore, QtWidgets
    from PySide6.QtCore import Qt
    _VER = 6
    try:
        import qtmax
        _parent_win = qtmax.GetQMaxMainWindow
    except ImportError:
        _parent_win = lambda: None
except ImportError:
    from PySide2 import QtCore, QtWidgets
    from PySide2.QtCore import Qt
    _VER = 2
    try:
        import qtmax
        _parent_win = qtmax.GetQMaxMainWindow
    except ImportError:
        _parent_win = lambda: None

# ── Enum shims ───────────────────────────────────────────────────────────────
if _VER == 6:
    _Stretch  = QtWidgets.QHeaderView.ResizeMode.Stretch
    _Contents = QtWidgets.QHeaderView.ResizeMode.ResizeToContents
    _WinFlags = Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowMaximizeButtonHint
else:
    _Stretch  = QtWidgets.QHeaderView.Stretch
    _Contents = QtWidgets.QHeaderView.ResizeToContents
    _WinFlags = Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint


# ═══════════════════════════════════════════════════════════════════════════════
#  CORE LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

def _class_name(node) -> str:
    try:
        return str(rt.classOf(node))
    except Exception:
        return "Unknown"


def _sort_hierarchy(nodes: list) -> list:
    """BFS sort: parents before children, restricted to the supplied list."""
    name_set: Set[str]            = {str(n.name) for n in nodes}
    by_name:  Dict[str, object]   = {str(n.name): n for n in nodes}
    children: Dict[str, List[str]] = {str(n.name): [] for n in nodes}
    parent_of: Dict[str, Optional[str]] = {}

    for node in nodes:
        name = str(node.name)
        try:
            p      = node.parent
            p_name = str(p.name) if p is not None and str(p.name) in name_set else None
        except Exception:
            p_name = None
        parent_of[name] = p_name
        if p_name:
            children[p_name].append(name)

    queue   = deque(n for n in nodes if parent_of[str(n.name)] is None)
    ordered, visited = [], set()
    while queue:
        node = queue.popleft()
        name = str(node.name)
        if name in visited:
            continue
        visited.add(name)
        ordered.append(node)
        for ch in children.get(name, []):
            if ch not in visited:
                queue.append(by_name[ch])

    for node in nodes:           # safety – append anything missed
        if str(node.name) not in visited:
            ordered.append(node)
    return ordered


def _hierarchy_warning(nodes: list) -> str:
    """Return warning string when selected nodes have out-of-selection parents."""
    name_set = {str(n.name) for n in nodes}
    bad = []
    for node in nodes:
        try:
            p = node.parent
            if p is not None and str(p.name) not in name_set:
                bad.append(f'  "{node.name}" → parent "{p.name}" not selected')
        except Exception:
            pass
    if bad:
        return "⚠ Parents missing from selection:\n" + "\n".join(bad[:15])
    return ""


def extract_entries(nodes: list) -> List[dict]:
    return [
        {"name": str(n.name), "type": _class_name(n), "type_change": ""}
        for n in _sort_hierarchy(nodes)
    ]


def save_json(entries: List[dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def load_json(path: str) -> List[dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def get_rename_preview(entries: List[dict], selected_only: bool, is_restore: bool) -> List[dict]:
    if not _IN_MAX:
        return []
    pool = (
        {str(n.name): n for n in rt.selection}
        if selected_only else
        {str(n.name): n for n in rt.objects}
    )
    
    parsed_entries = []
    new_names_counts = {}
    for e in entries:
        orig = e.get("name", "").strip()
        chg = e.get("type_change", "").strip()
        
        if is_restore:
            target = chg
            dest = orig
        else:
            target = orig
            dest = chg
            
        if not target or not dest:
            continue
            
        parsed_entries.append((target, dest))
        if target != dest:
            new_names_counts[dest] = new_names_counts.get(dest, 0) + 1

    all_names_in_scene = {str(n.name) for n in rt.objects}
    names_being_freed = {target for target, dest in parsed_entries 
                         if target != dest and target in pool}
    
    names_occupied = all_names_in_scene - names_being_freed

    result = []
    for target, dest in parsed_entries:
        node = pool.get(target)
        if node is None:
            result.append({"node": None, "old": target, "new": dest, "status": "Not Found"})
        else:
            if target == dest:
                result.append({"node": node, "old": target, "new": dest, "status": "Skip (Same)"})
            else:
                if new_names_counts.get(dest, 0) > 1:
                    result.append({"node": node, "old": target, "new": dest, "status": "Dup in JSON"})
                elif dest in names_occupied:
                    result.append({"node": node, "old": target, "new": dest, "status": "Name Exists"})
                else:
                    names_occupied.add(dest)
                    result.append({"node": node, "old": target, "new": dest, "status": "Ready"})
    return result


# ═══════════════════════════════════════════════════════════════════════════════
#  WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

BG   = "#1c1c28"
CARD = "#252535"
ACC  = "#e94560"
ACH  = "#ff6b6b"
GRN  = "#00d2a0"
TXT  = "#eaeaea"
DIM  = "#6b7280"
BDR  = "#333348"


class RenamePreviewTable(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, 3, parent)
        self.setHorizontalHeaderLabels(["Status", "Old Name", "New Name"])
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers if _VER == 6 else QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection if _VER == 6 else QtWidgets.QAbstractItemView.NoSelection)
        self.setAlternatingRowColors(True)
        h = self.horizontalHeader()
        h.setSectionResizeMode(0, _Contents)
        h.setSectionResizeMode(1, _Stretch)
        h.setSectionResizeMode(2, _Stretch)
        self.setMinimumHeight(120)

    def load_data(self, data: List[dict]):
        self.setRowCount(len(data))
        qg = __import__("PySide6" if _VER == 6 else "PySide2", fromlist=["QtGui"]).QtGui
        c_grn = qg.QColor(GRN)
        c_red = qg.QColor(ACC)
        c_dim = qg.QColor(DIM)
        
        for i, row in enumerate(data):
            st = row["status"]
            i_st = QtWidgets.QTableWidgetItem(st)
            i_old = QtWidgets.QTableWidgetItem(row["old"])
            i_new = QtWidgets.QTableWidgetItem(row["new"])
            
            if st in ("Ready", "Done"):
                i_st.setForeground(c_grn)
            elif st in ("Not Found", "Dup in JSON", "Name Exists", "Error"):
                i_st.setForeground(c_red)
                if st != "Not Found":
                    i_new.setForeground(c_red)
            else:
                i_st.setForeground(c_dim)
                i_new.setForeground(c_dim)
                
            if _VER == 6:
                i_st.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                i_st.setTextAlignment(Qt.AlignCenter)
            
            self.setItem(i, 0, i_st)
            self.setItem(i, 1, i_old)
            self.setItem(i, 2, i_new)


class ToolNameWindow(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._entries: List[dict] = []
        self._pending_renames: List[dict] = []
        self.setWindowTitle("ToolName — Name Manager")
        self.setFixedWidth(540)
        self.setWindowFlags(self.windowFlags() | _WinFlags)
        self._style()
        self._build()

    # ── stylesheet ────────────────────────────────────────────────────────────
    def _style(self):
        self.setStyleSheet(f"""
        QDialog {{
            background:{BG}; color:{TXT};
            font-family:"Segoe UI",sans-serif; font-size:13px;
        }}
        QLabel {{ color:{TXT}; }}
        QLabel#head {{ color:{ACC}; font-size:16px; font-weight:700; }}
        QLabel#sub  {{ color:{DIM}; font-size:11px; }}
        QLabel#log  {{ color:{DIM}; font-size:11px; padding:4px 8px;
                       background:{CARD}; border:1px solid {BDR};
                       border-radius:5px; }}
        QGroupBox {{
            color:{DIM}; border:1px solid {BDR}; border-radius:7px;
            margin-top:10px; padding:6px;
        }}
        QGroupBox::title {{
            subcontrol-origin:margin; subcontrol-position:top left;
            left:8px; padding:0 4px; color:{ACC}; font-size:11px; font-weight:600;
        }}
        QPushButton {{
            background:{CARD}; color:{TXT}; border:1px solid {BDR};
            border-radius:6px; padding:8px 14px; font-size:13px;
        }}
        QPushButton:hover  {{ background:{ACC}; border-color:{ACC}; color:#fff; }}
        QPushButton:pressed {{ background:{ACH}; }}
        QPushButton#extract {{
            background:{ACC}; border-color:{ACC}; color:#fff; font-weight:700;
        }}
        QPushButton#extract:hover  {{ background:{ACH}; }}
        QPushButton#import_ {{
            background:{GRN}; border-color:{GRN}; color:#0a0a0a; font-weight:700;
        }}
        QPushButton#import_:hover  {{ background:#00e8b5; }}
        QPushButton#restore_ {{
            background:#f39c12; border-color:#f39c12; color:#0a0a0a; font-weight:700;
        }}
        QPushButton#restore_:hover  {{ background:#f1c40f; }}
        QLineEdit {{
            background:{CARD}; color:{TXT}; border:1px solid {BDR};
            border-radius:5px; padding:5px 8px;
        }}
        QLineEdit:focus {{ border-color:{ACC}; }}
        QListWidget {{
            background:{CARD}; color:{TXT}; border:1px solid {BDR};
            border-radius:6px; font-size:12px; outline:none;
        }}
        QListWidget::item {{ padding:3px 6px; }}
        QTableWidget {{ background:{CARD}; color:{TXT}; border:1px solid {BDR}; gridline-color:{BDR}; border-radius:6px; font-size:12px; }}
        QHeaderView::section {{ background:{BG}; color:{DIM}; padding:4px; border:none; }}
        QPushButton#apply_ {{ background:{GRN}; color:#0a0a0a; font-weight:700; }}
        QPushButton#apply_:hover {{ background:#00e8b5; }}
        QPushButton#apply_:disabled {{ background:{CARD}; color:{DIM}; border-color:{BDR}; }}
        QRadioButton {{ color:{TXT}; spacing:5px; }}
        QRadioButton::indicator {{
            width:13px; height:13px; border:2px solid {BDR};
            border-radius:7px; background:{CARD};
        }}
        QRadioButton::indicator:checked {{ background:{ACC}; border-color:{ACC}; }}
        QScrollBar:vertical {{
            background:{CARD}; width:6px; border-radius:3px;
        }}
        QScrollBar::handle:vertical {{
            background:{BDR}; border-radius:3px; min-height:20px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
        """)

    # ── build ─────────────────────────────────────────────────────────────────
    def _build(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(14, 14, 14, 12)

        # header
        h = QtWidgets.QHBoxLayout()
        hl = QtWidgets.QLabel("🏷️  ToolName")
        hl.setObjectName("head")
        sl = QtWidgets.QLabel("Object Name Manager · 3ds Max")
        sl.setObjectName("sub")
        hc = QtWidgets.QVBoxLayout()
        hc.setSpacing(1)
        hc.addWidget(hl)
        hc.addWidget(sl)
        h.addLayout(hc)
        h.addStretch()
        root.addLayout(h)

        self._div(root)

        # ── Section 1: Extract ───────────────────────────────────────────────
        g1 = QtWidgets.QGroupBox("1 · Extract Name to JSON")
        v1 = QtWidgets.QVBoxLayout(g1)
        v1.setSpacing(6)

        r1 = QtWidgets.QHBoxLayout()
        self._ex_path = QtWidgets.QLineEdit()
        self._ex_path.setPlaceholderText("Output .json file …")
        r1.addWidget(self._ex_path)
        b_br1 = self._btn("…", small=True)
        b_br1.clicked.connect(self._browse_save)
        r1.addWidget(b_br1)
        v1.addLayout(r1)

        b_ex = QtWidgets.QPushButton("📤  Extract Name to JSON")
        b_ex.setObjectName("extract")
        b_ex.clicked.connect(self._do_extract)
        v1.addWidget(b_ex)
        root.addWidget(g1)

        # ── Section 2: Import ────────────────────────────────────────────────
        g2 = QtWidgets.QGroupBox("2 · Import JSON Name")
        v2 = QtWidgets.QVBoxLayout(g2)
        v2.setSpacing(6)

        r2 = QtWidgets.QHBoxLayout()
        self._im_path = QtWidgets.QLineEdit()
        self._im_path.setPlaceholderText("Input .json file …")
        r2.addWidget(self._im_path)
        b_br2 = self._btn("…", small=True)
        b_br2.clicked.connect(self._browse_load)
        r2.addWidget(b_br2)
        v2.addLayout(r2)

        # scope row
        sr = QtWidgets.QHBoxLayout()
        self._rb_sel   = QtWidgets.QRadioButton("Selected")
        self._rb_scene = QtWidgets.QRadioButton("All scene")
        self._rb_sel.setChecked(True)
        sr.addWidget(self._rb_sel)
        sr.addWidget(self._rb_scene)
        sr.addStretch()
        v2.addLayout(sr)

        btn_lay = QtWidgets.QHBoxLayout()
        b_im = QtWidgets.QPushButton("📥  Preview Import")
        b_im.setObjectName("import_")
        b_im.clicked.connect(lambda: self._do_preview(False))
        
        b_res = QtWidgets.QPushButton("↩️  Preview Restore")
        b_res.setObjectName("restore_")
        b_res.clicked.connect(lambda: self._do_preview(True))
        
        btn_lay.addWidget(b_im)
        btn_lay.addWidget(b_res)
        v2.addLayout(btn_lay)
        root.addWidget(g2)

        # ── Preview Table & Confirm ──────────────────────────────────────────
        plbl = QtWidgets.QLabel("3 · Preview & Confirm Changes")
        plbl.setObjectName("head")
        root.addWidget(plbl)
        
        self._table = RenamePreviewTable()
        root.addWidget(self._table)
        
        self._btn_apply = QtWidgets.QPushButton("✅  Apply Renames")
        self._btn_apply.setObjectName("apply_")
        self._btn_apply.setEnabled(False)
        self._btn_apply.clicked.connect(self._do_apply)
        root.addWidget(self._btn_apply)

        # ── Log ──────────────────────────────────────────────────────────────
        self._log = QtWidgets.QListWidget()
        self._log.setMaximumHeight(80)
        root.addWidget(self._log)

    # ── helpers ───────────────────────────────────────────────────────────────
    def _div(self, layout):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine if _VER == 6 else QtWidgets.QFrame.HLine)
        line.setStyleSheet(f"color:{BDR};")
        layout.addWidget(line)

    def _btn(self, text, small=False) -> QtWidgets.QPushButton:
        b = QtWidgets.QPushButton(text)
        if small:
            b.setFixedWidth(32)
        return b

    def _log_add(self, msg: str, color: str = TXT):
        item = QtWidgets.QListWidgetItem(msg)
        item.setForeground(QtWidgets.QApplication.palette().text()
                           if color == TXT else
                           __import__("PySide6" if _VER == 6 else "PySide2",
                                      fromlist=["QtGui"]).QtGui.QColor(color))
        self._log.addItem(item)
        self._log.scrollToBottom()

    # ── browse ────────────────────────────────────────────────────────────────
    def _browse_save(self):
        p, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save JSON", "", "JSON (*.json)"
        )
        if p:
            self._ex_path.setText(p)

    def _browse_load(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open JSON", "", "JSON (*.json)"
        )
        if p:
            self._im_path.setText(p)

    # ── extract ───────────────────────────────────────────────────────────────
    def _do_extract(self):
        if not _IN_MAX:
            self._log_add("✖  Not inside 3ds Max.", ACC)
            return

        sel = list(rt.selection)
        if not sel:
            self._log_add("⚠  Nothing selected.", ACC)
            return

        path = self._ex_path.text().strip()
        if not path:
            self._log_add("⚠  Set an output file path.", ACC)
            return
        if not path.lower().endswith(".json"):
            path += ".json"
            self._ex_path.setText(path)

        # hierarchy warning
        warn = _hierarchy_warning(sel)
        if warn:
            r = QtWidgets.QMessageBox.warning(
                self, "Incomplete Hierarchy",
                warn + "\n\nExport anyway?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No,
            )
            if r != QtWidgets.QMessageBox.Yes:
                return

        entries = extract_entries(sel)
        try:
            save_json(entries, path)
        except Exception as e:
            self._log_add(f"✖  Save failed: {e}", ACC)
            return

        self._log_add(f"✔  Exported {len(entries)} objects → {os.path.basename(path)}", GRN)

    # ── import ────────────────────────────────────────────────────────────────
    # ── preview & apply ───────────────────────────────────────────────────────
    def _do_preview(self, is_restore: bool):
        self._pending_renames.clear()
        self._table.setRowCount(0)
        self._btn_apply.setEnabled(False)
        
        if not _IN_MAX:
            self._log_add("✖  Not inside 3ds Max.", ACC)
            return

        path = self._im_path.text().strip()
        if not path or not os.path.isfile(path):
            self._log_add("⚠  Valid JSON file required.", ACC)
            return

        entries = load_json(path)
        if not entries:
            self._log_add("⚠  No entries in JSON.", ACC)
            return

        sel_only = self._rb_sel.isChecked()
        if sel_only and not list(rt.selection):
            self._log_add("⚠  Nothing selected — switch scope or select objects.", ACC)
            return

        results = get_rename_preview(entries, sel_only, is_restore)
        self._table.load_data(results)
        self._pending_renames = results
        
        ready = sum(1 for r in results if r["status"] == "Ready")
        
        if ready > 0:
            self._btn_apply.setEnabled(True)
            self._btn_apply.setText(f"✅  Apply {ready} Renames")
            self._log_add(f"✔  Preview loaded: {ready} ready" + (" (Restore)" if is_restore else " (Import)"), GRN)
        else:
            self._btn_apply.setEnabled(False)
            self._btn_apply.setText("✅  Apply Renames")
            not_found = sum(1 for r in results if r["status"] == "Not Found")
            self._log_add(f"⚠  No valid renames found. Missing: {not_found}", ACC)

    def _do_apply(self):
        if not self._pending_renames:
            return
            
        ok, err = 0, 0
        for r in self._pending_renames:
            if r["status"] == "Ready" and r["node"] is not None:
                try:
                    r["node"].name = r["new"]
                    r["status"] = "Done"
                    ok += 1
                except Exception:
                    r["status"] = "Error"
                    err += 1
                    
        self._table.load_data(self._pending_renames)
        self._pending_renames.clear()
        self._btn_apply.setEnabled(False)
        self._btn_apply.setText("✅  Apply Renames")
        
        if err > 0:
            self._log_add(f"⚠  Applied {ok} renames, {err} errors.", ACC)
        else:
            self._log_add(f"✔  Successfully applied {ok} renames!", GRN)


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
_win: Optional[ToolNameWindow] = None

def launch():
    global _win
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    if _win is None or not _win.isVisible():
        _win = ToolNameWindow(parent=_parent_win())
    _win.show(); _win.raise_(); _win.activateWindow()

if __name__ == "__main__":
    launch()
