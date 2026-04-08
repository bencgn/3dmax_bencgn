"""
LinkBack Tool for 3ds Max 2025
================================
Saves parent-child link relationships to JSON.
Loads and visualises them so users can selectively unlink objects.

Author : ghinho
Version: 1.0  (2026)

Usage (in 3ds Max Python Listener or startup script):
    import importlib, sys
    sys.path.append(r"D:\3dmax_bencgn\3dmax_bencgn\3DsMax Script\ghinho")
    import linkback; importlib.reload(linkback); linkback.launch()
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# ── 3ds Max runtime ──────────────────────────────────────────────────────────
try:
    import pymxs
    from pymxs import runtime as rt

    _IN_MAX = True
except ImportError:
    _IN_MAX = False  # allow offline syntax-check

# ── Qt  (3ds Max 2025 = PySide6 / Python 3.11 ; older Max = PySide2) ─────────
_PYSIDE_VER = 0  # will be set to 6 or 2 below

try:
    # ── PySide6 (3ds Max 2025+) ────────────────────────────────────────────────
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import Qt
    _PYSIDE_VER = 6

    # In PySide6, enum values live under their class, e.g. Qt.CheckState.Checked.
    # Build a small shim so the rest of the code can use Qt.Checked etc. unchanged.
    class _QtCompat:
        """Forwards PySide6 enum members using PySide2-style attribute names."""
        # CheckState
        Checked           = Qt.CheckState.Checked
        Unchecked         = Qt.CheckState.Unchecked
        PartiallyChecked  = Qt.CheckState.PartiallyChecked
        # ItemFlag
        ItemIsUserCheckable = Qt.ItemFlag.ItemIsUserCheckable
        ItemIsEnabled       = Qt.ItemFlag.ItemIsEnabled
        ItemIsSelectable    = Qt.ItemFlag.ItemIsSelectable
        # Orientation
        Horizontal = Qt.Orientation.Horizontal
        Vertical   = Qt.Orientation.Vertical
        # WindowType
        WindowMinimizeButtonHint = Qt.WindowType.WindowMinimizeButtonHint
        WindowMaximizeButtonHint = Qt.WindowType.WindowMaximizeButtonHint
        # SelectionMode
        ExtendedSelection = QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
        # pass everything else straight to Qt
        def __getattr__(self, name):
            return getattr(Qt, name)
    Qt = _QtCompat()

    try:
        import qtmax
        def _max_main_window():
            return qtmax.GetQMaxMainWindow()
    except ImportError:
        def _max_main_window():
            return None

except ImportError:
    try:
        # ── PySide2 (3ds Max 2022-2024) ────────────────────────────────────────
        from PySide2 import QtCore, QtGui, QtWidgets
        from PySide2.QtCore import Qt
        _PYSIDE_VER = 2

        try:
            import qtmax
            def _max_main_window():
                return qtmax.GetQMaxMainWindow()
        except ImportError:
            def _max_main_window():
                return None

    except ImportError:
        raise RuntimeError(
            "Neither PySide6 nor PySide2 found.\n"
            "Please run this script from inside 3ds Max 2025 Python."
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  COLOUR PALETTE
# ═══════════════════════════════════════════════════════════════════════════════
DARK_BG      = "#1a1a2e"
PANEL_BG     = "#16213e"
CARD_BG      = "#0f3460"
ACCENT       = "#e94560"
ACCENT_HOVER = "#ff6b6b"
TEXT_PRIMARY = "#eaeaea"
TEXT_MUTED   = "#8892b0"
SUCCESS      = "#00d2a0"
WARNING      = "#f4a261"
LINK_COLOR   = "#a8dadc"
BORDER       = "#2a2a4a"


# ═══════════════════════════════════════════════════════════════════════════════
#  PySide6 / PySide2 ENUM COMPATIBILITY HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

if _PYSIDE_VER == 6:
    _HV_Stretch        = QtWidgets.QHeaderView.ResizeMode.Stretch
    _HV_ResizeContents = QtWidgets.QHeaderView.ResizeMode.ResizeToContents
    _AV_ExtendedSel    = QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
    _Frame_HLine       = QtWidgets.QFrame.Shape.HLine
    _WinMin            = Qt.WindowMinimizeButtonHint
    _WinMax            = Qt.WindowMaximizeButtonHint
else:
    _HV_Stretch        = QtWidgets.QHeaderView.Stretch
    _HV_ResizeContents = QtWidgets.QHeaderView.ResizeToContents
    _AV_ExtendedSel    = QtWidgets.QAbstractItemView.ExtendedSelection
    _Frame_HLine       = QtWidgets.QFrame.HLine
    _WinMin            = Qt.WindowMinimizeButtonHint
    _WinMax            = Qt.WindowMaximizeButtonHint


# ═══════════════════════════════════════════════════════════════════════════════
#  CORE DATA LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

class LinkData:
    """Represents one child→parent relationship."""

    def __init__(self, child: str, parent: str, child_handle: int = -1, parent_handle: int = -1):
        self.child         = child
        self.parent        = parent
        self.child_handle  = child_handle
        self.parent_handle = parent_handle

    def to_dict(self) -> dict:
        return {
            "child":         self.child,
            "parent":        self.parent,
            "child_handle":  self.child_handle,
            "parent_handle": self.parent_handle,
        }

    @staticmethod
    def from_dict(d: dict) -> "LinkData":
        return LinkData(
            child         = d.get("child",  ""),
            parent        = d.get("parent", ""),
            child_handle  = d.get("child_handle",  -1),
            parent_handle = d.get("parent_handle", -1),
        )


class LinkSession:
    """A named snapshot of link relationships."""

    def __init__(self, name: str = "", links: Optional[List[LinkData]] = None):
        self.name      = name or datetime.now().strftime("Session_%Y%m%d_%H%M%S")
        self.timestamp = datetime.now().isoformat(timespec="seconds")
        self.links: List[LinkData] = links or []

    def to_dict(self) -> dict:
        return {
            "session_name": self.name,
            "timestamp":    self.timestamp,
            "links":        [l.to_dict() for l in self.links],
        }

    @staticmethod
    def from_dict(d: dict) -> "LinkSession":
        s = LinkSession(name=d.get("session_name", "Unnamed"))
        s.timestamp = d.get("timestamp", "")
        s.links = [LinkData.from_dict(x) for x in d.get("links", [])]
        return s


# ═══════════════════════════════════════════════════════════════════════════════
#  3DS MAX HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_handle(node) -> int:
    """Return the Max handle of a node (0 if unavailable)."""
    try:
        return int(rt.getHandleByAnim(node))
    except Exception:
        return -1


def collect_links_from_scene(scope: str = "all") -> List[LinkData]:
    """
    Walk scene objects and return every child→parent relationship.
    scope: 'all'      → every object in the scene
           'selected' → only currently selected objects
    """
    if not _IN_MAX:
        return []

    results: List[LinkData] = []

    if scope == "selected":
        candidates = list(rt.selection)
    else:
        candidates = list(rt.objects)

    for node in candidates:
        try:
            parent = node.parent
            if parent is not None:
                results.append(
                    LinkData(
                        child         = str(node.name),
                        parent        = str(parent.name),
                        child_handle  = _get_handle(node),
                        parent_handle = _get_handle(parent),
                    )
                )
        except Exception:
            continue

    return results


def save_links_to_json(session: LinkSession, filepath: str) -> None:
    """Serialise session to JSON file (appends to existing sessions list)."""
    data: List[dict] = []
    if os.path.isfile(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if not isinstance(data, list):
                    data = []
        except Exception:
            data = []

    data.append(session.to_dict())

    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def load_sessions_from_json(filepath: str) -> List[LinkSession]:
    """Load all sessions from a JSON file."""
    if not os.path.isfile(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            return []
        return [LinkSession.from_dict(d) for d in data]
    except Exception:
        return []


def relink_objects(links: List[LinkData]) -> dict:
    """
    Re-apply saved parent-child links.
    Finds each child and its saved parent, then sets node.parent = parent_node.
    Returns a dict with counts: {'ok': n, 'not_found': n, 'errors': n}
    """
    result = {"ok": 0, "not_found": 0, "errors": 0}
    if not _IN_MAX:
        return result

    for link in links:
        try:
            # ── Find child node ───────────────────────────────────────────────
            child_node = None
            if link.child_handle > 0:
                try:
                    child_node = rt.getAnimByHandle(link.child_handle)
                except Exception:
                    pass
            if child_node is None:
                child_node = rt.getNodeByName(link.child, exact=True)

            if child_node is None:
                result["not_found"] += 1
                continue

            # ── Find parent node ──────────────────────────────────────────────
            parent_node = None
            if link.parent_handle > 0:
                try:
                    parent_node = rt.getAnimByHandle(link.parent_handle)
                except Exception:
                    pass
            if parent_node is None:
                parent_node = rt.getNodeByName(link.parent, exact=True)

            if parent_node is None:
                result["not_found"] += 1
                continue

            # ── Restore the link ──────────────────────────────────────────────
            child_node.parent = parent_node
            result["ok"] += 1
        except Exception:
            result["errors"] += 1

    return result


def select_objects_in_max(names: List[str]) -> None:
    """Select objects in 3ds Max by name list."""
    if not _IN_MAX:
        return
    nodes = [rt.getNodeByName(n, exact=True) for n in names]
    nodes = [n for n in nodes if n is not None]
    if nodes:
        rt.select(nodes)


# ═══════════════════════════════════════════════════════════════════════════════
#  CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════════════════════════════

class LinkTreeItem(QtWidgets.QTreeWidgetItem):
    """One row in the link tree — stores the LinkData payload."""

    def __init__(self, link: LinkData, parent_item=None):
        super().__init__(parent_item)
        self.link_data = link

        self.setText(0, link.child)
        self.setText(1, link.parent)
        self.setText(2, f"#{link.child_handle}" if link.child_handle > 0 else "–")

        self.setCheckState(0, Qt.Unchecked)
        self.setForeground(0, QtGui.QColor(LINK_COLOR))
        self.setForeground(1, QtGui.QColor(TEXT_MUTED))
        self.setForeground(2, QtGui.QColor(TEXT_MUTED))


class SessionComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QComboBox {{
                background: {CARD_BG};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                min-height: 32px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 28px;
            }}
            QComboBox QAbstractItemView {{
                background: {PANEL_BG};
                color: {TEXT_PRIMARY};
                selection-background-color: {CARD_BG};
            }}
        """)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

class LinkBackWindow(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sessions: List[LinkSession] = []
        self._json_path: str = ""

        self.setWindowTitle("LinkBack  –  Link Relationship Manager")
        self.setMinimumSize(820, 620)
        self.setWindowFlags(self.windowFlags() | _WinMin | _WinMax)
        self._apply_stylesheet()
        self._build_ui()

    # ── STYLESHEET ────────────────────────────────────────────────────────────
    def _apply_stylesheet(self):
        self.setStyleSheet(f"""
            QDialog {{
                background: {DARK_BG};
                color: {TEXT_PRIMARY};
                font-family: "Segoe UI", "Inter", sans-serif;
                font-size: 13px;
            }}
            QLabel {{
                color: {TEXT_PRIMARY};
            }}
            QLabel#title_label {{
                color: {ACCENT};
                font-size: 20px;
                font-weight: 700;
                letter-spacing: 1px;
            }}
            QLabel#subtitle_label {{
                color: {TEXT_MUTED};
                font-size: 11px;
            }}
            QLabel#section_label {{
                color: {ACCENT};
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.5px;
            }}
            QFrame#card {{
                background: {PANEL_BG};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
            QFrame#separator {{
                background: {BORDER};
                max-height: 1px;
            }}
            QPushButton {{
                background: {CARD_BG};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 7px;
                padding: 8px 18px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {ACCENT};
                border-color: {ACCENT};
                color: #ffffff;
            }}
            QPushButton:pressed {{
                background: {ACCENT_HOVER};
            }}
            QPushButton#btn_primary {{
                background: {ACCENT};
                border-color: {ACCENT};
                color: #ffffff;
                font-weight: 600;
            }}
            QPushButton#btn_primary:hover {{
                background: {ACCENT_HOVER};
            }}
            QPushButton#btn_success {{
                background: {SUCCESS};
                border-color: {SUCCESS};
                color: #0a0a0a;
                font-weight: 600;
            }}
            QPushButton#btn_success:hover {{
                background: #00e8b5;
            }}
            QPushButton#btn_warning {{
                background: {WARNING};
                border-color: {WARNING};
                color: #0a0a0a;
                font-weight: 600;
            }}
            QPushButton#btn_warning:hover {{
                background: #f6b87a;
            }}
            QLineEdit {{
                background: {CARD_BG};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {ACCENT};
            }}
            QTreeWidget {{
                background: {CARD_BG};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 8px;
                outline: none;
                font-size: 13px;
                alternate-background-color: {PANEL_BG};
            }}
            QTreeWidget::item {{
                padding: 5px 4px;
                border-radius: 4px;
            }}
            QTreeWidget::item:selected {{
                background: {ACCENT};
                color: #ffffff;
            }}
            QTreeWidget::item:hover {{
                background: rgba(233,69,96,0.15);
            }}
            QHeaderView::section {{
                background: {PANEL_BG};
                color: {ACCENT};
                border: none;
                border-bottom: 1px solid {BORDER};
                padding: 6px 8px;
                font-weight: 600;
                font-size: 12px;
            }}
            QScrollBar:vertical {{
                background: {PANEL_BG};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {CARD_BG};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QCheckBox {{
                color: {TEXT_PRIMARY};
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {BORDER};
                border-radius: 4px;
                background: {CARD_BG};
            }}
            QCheckBox::indicator:checked {{
                background: {ACCENT};
                border-color: {ACCENT};
            }}
            QRadioButton {{
                color: {TEXT_PRIMARY};
                spacing: 6px;
            }}
            QRadioButton::indicator {{
                width: 14px;
                height: 14px;
                border: 2px solid {BORDER};
                border-radius: 7px;
                background: {CARD_BG};
            }}
            QRadioButton::indicator:checked {{
                background: {ACCENT};
                border-color: {ACCENT};
            }}
            QStatusBar, QLabel#status_label {{
                color: {TEXT_MUTED};
                font-size: 11px;
            }}
            QTabWidget::pane {{
                border: 1px solid {BORDER};
                border-radius: 8px;
                background: {PANEL_BG};
            }}
            QTabBar::tab {{
                background: {CARD_BG};
                color: {TEXT_MUTED};
                border: 1px solid {BORDER};
                border-bottom: none;
                padding: 8px 20px;
                border-top-left-radius: 7px;
                border-top-right-radius: 7px;
                font-size: 13px;
            }}
            QTabBar::tab:selected {{
                background: {ACCENT};
                color: #ffffff;
                font-weight: 600;
            }}
            QTabBar::tab:hover:!selected {{
                background: rgba(233,69,96,0.2);
                color: {TEXT_PRIMARY};
            }}
            QGroupBox {{
                color: {TEXT_MUTED};
                border: 1px solid {BORDER};
                border-radius: 8px;
                margin-top: 12px;
                padding: 8px;
                font-size: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 6px;
                color: {ACCENT};
                font-weight: 600;
            }}
        """)

    # ── BUILD UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setSpacing(14)
        root.setContentsMargins(18, 18, 18, 14)

        # ── Header ────────────────────────────────────────────────────────────
        header = QtWidgets.QHBoxLayout()
        icon_lbl = QtWidgets.QLabel("🔗")
        icon_lbl.setStyleSheet("font-size: 28px;")
        header.addWidget(icon_lbl)

        title_col = QtWidgets.QVBoxLayout()
        title_col.setSpacing(2)
        t = QtWidgets.QLabel("LinkBack")
        t.setObjectName("title_label")
        sub = QtWidgets.QLabel("Parent-Child Link Relationship Manager  ·  3ds Max 2025")
        sub.setObjectName("subtitle_label")
        title_col.addWidget(t)
        title_col.addWidget(sub)
        header.addLayout(title_col)
        header.addStretch()

        # version badge
        badge = QtWidgets.QLabel("v1.0")
        badge.setStyleSheet(
            f"background:{CARD_BG}; color:{TEXT_MUTED}; border:1px solid {BORDER};"
            "border-radius:10px; padding:2px 10px; font-size:11px;"
        )
        header.addWidget(badge)
        root.addLayout(header)

        # separator
        sep = QtWidgets.QFrame(); sep.setObjectName("separator"); sep.setFrameShape(_Frame_HLine)
        sep.setStyleSheet(f"background:{BORDER}; border:none; max-height:1px;")
        root.addWidget(sep)

        # ── Tab widget ────────────────────────────────────────────────────────
        tabs = QtWidgets.QTabWidget()
        root.addWidget(tabs)

        tabs.addTab(self._build_save_tab(),   "  💾  Save Links  ")
        tabs.addTab(self._build_load_tab(),   "  🔗  Load & LinkBack  ")
        tabs.addTab(self._build_help_tab(),   "  ℹ️  Help  ")

        # ── Status bar ────────────────────────────────────────────────────────
        self._status = QtWidgets.QLabel("Ready.")
        self._status.setObjectName("status_label")
        root.addWidget(self._status)

    # ── SAVE TAB ──────────────────────────────────────────────────────────────
    def _build_save_tab(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)
        lay.setSpacing(12)
        lay.setContentsMargins(14, 14, 14, 14)

        # ── Scope ─────────────────────────────────────────────────────────────
        scope_box = QtWidgets.QGroupBox("Scope — Which objects to scan")
        scope_lay = QtWidgets.QHBoxLayout(scope_box)
        self._rb_all = QtWidgets.QRadioButton("All objects in scene")
        self._rb_sel = QtWidgets.QRadioButton("Selected objects only")
        self._rb_all.setChecked(True)
        scope_lay.addWidget(self._rb_all)
        scope_lay.addWidget(self._rb_sel)
        scope_lay.addStretch()
        lay.addWidget(scope_box)

        # ── Session name ──────────────────────────────────────────────────────
        name_row = QtWidgets.QHBoxLayout()
        name_row.addWidget(QtWidgets.QLabel("Session name:"))
        self._session_name_edit = QtWidgets.QLineEdit()
        self._session_name_edit.setPlaceholderText("Leave blank for auto timestamp name …")
        name_row.addWidget(self._session_name_edit)
        lay.addLayout(name_row)

        # ── File path ─────────────────────────────────────────────────────────
        path_row = QtWidgets.QHBoxLayout()
        path_row.addWidget(QtWidgets.QLabel("Save to JSON:"))
        self._save_path_edit = QtWidgets.QLineEdit()
        self._save_path_edit.setPlaceholderText("Click Browse …  or  type path")
        path_row.addWidget(self._save_path_edit)
        btn_browse_save = QtWidgets.QPushButton("Browse …")
        btn_browse_save.clicked.connect(self._browse_save)
        path_row.addWidget(btn_browse_save)
        lay.addLayout(path_row)

        # ── Preview area ──────────────────────────────────────────────────────
        preview_lbl = QtWidgets.QLabel("PREVIEW  —  Links that will be saved")
        preview_lbl.setObjectName("section_label")
        lay.addWidget(preview_lbl)

        self._preview_tree = QtWidgets.QTreeWidget()
        self._preview_tree.setHeaderLabels(["Child Object", "Parent Object", "Handle"])
        self._preview_tree.setAlternatingRowColors(True)
        self._preview_tree.header().setStretchLastSection(False)
        self._preview_tree.header().setSectionResizeMode(0, _HV_Stretch)
        self._preview_tree.header().setSectionResizeMode(1, _HV_Stretch)
        self._preview_tree.header().setSectionResizeMode(2, _HV_ResizeContents)
        lay.addWidget(self._preview_tree, 1)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = QtWidgets.QHBoxLayout()

        btn_scan = QtWidgets.QPushButton("🔍  Scan Links")
        btn_scan.clicked.connect(self._scan_links)
        btn_row.addWidget(btn_scan)

        btn_row.addStretch()

        self._save_count_lbl = QtWidgets.QLabel("No links scanned yet.")
        self._save_count_lbl.setStyleSheet(f"color:{TEXT_MUTED}; font-size:12px;")
        btn_row.addWidget(self._save_count_lbl)

        btn_row.addStretch()

        btn_save = QtWidgets.QPushButton("💾  Save to JSON")
        btn_save.setObjectName("btn_primary")
        btn_save.clicked.connect(self._save_links)
        btn_row.addWidget(btn_save)

        lay.addLayout(btn_row)
        return w

    # ── LOAD/UNLINK TAB ───────────────────────────────────────────────────────
    def _build_load_tab(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)
        lay.setSpacing(12)
        lay.setContentsMargins(14, 14, 14, 14)

        # ── File path ─────────────────────────────────────────────────────────
        path_row = QtWidgets.QHBoxLayout()
        path_row.addWidget(QtWidgets.QLabel("JSON file:"))
        self._load_path_edit = QtWidgets.QLineEdit()
        self._load_path_edit.setPlaceholderText("Browse to a saved LinkBack JSON …")
        path_row.addWidget(self._load_path_edit)
        btn_browse_load = QtWidgets.QPushButton("Browse …")
        btn_browse_load.clicked.connect(self._browse_load)
        path_row.addWidget(btn_browse_load)
        btn_load_file = QtWidgets.QPushButton("📂  Load")
        btn_load_file.setObjectName("btn_primary")
        btn_load_file.clicked.connect(self._load_file)
        path_row.addWidget(btn_load_file)
        lay.addLayout(path_row)

        # ── Session selector ──────────────────────────────────────────────────
        sess_row = QtWidgets.QHBoxLayout()
        sess_row.addWidget(QtWidgets.QLabel("Session:"))
        self._session_combo = SessionComboBox()
        self._session_combo.currentIndexChanged.connect(self._on_session_changed)
        sess_row.addWidget(self._session_combo, 1)
        sess_row.addStretch()
        self._sess_info_lbl = QtWidgets.QLabel("")
        self._sess_info_lbl.setStyleSheet(f"color:{TEXT_MUTED}; font-size:11px;")
        sess_row.addWidget(self._sess_info_lbl)
        lay.addLayout(sess_row)

        # ── Link tree ─────────────────────────────────────────────────────────
        tree_lbl = QtWidgets.QLabel("LINK RELATIONSHIPS  —  ✓ tick rows to re-apply / LinkBack")
        tree_lbl.setObjectName("section_label")
        lay.addWidget(tree_lbl)

        self._link_tree = QtWidgets.QTreeWidget()
        self._link_tree.setHeaderLabels(["Child Object", "Parent Object", "Handle"])
        self._link_tree.setAlternatingRowColors(True)
        self._link_tree.setSelectionMode(_AV_ExtendedSel)
        self._link_tree.header().setStretchLastSection(False)
        self._link_tree.header().setSectionResizeMode(0, _HV_Stretch)
        self._link_tree.header().setSectionResizeMode(1, _HV_Stretch)
        self._link_tree.header().setSectionResizeMode(2, _HV_ResizeContents)
        self._link_tree.itemChanged.connect(self._on_item_checked_changed)
        lay.addWidget(self._link_tree, 1)

        # ── Select-all / clear ────────────────────────────────────────────────
        check_row = QtWidgets.QHBoxLayout()
        btn_check_all = QtWidgets.QPushButton("☑  Check All")
        btn_check_none = QtWidgets.QPushButton("☐  Uncheck All")
        btn_check_all.clicked.connect(lambda: self._set_all_checked(True))
        btn_check_none.clicked.connect(lambda: self._set_all_checked(False))
        check_row.addWidget(btn_check_all)
        check_row.addWidget(btn_check_none)
        check_row.addStretch()
        self._checked_count_lbl = QtWidgets.QLabel("0 items checked")
        self._checked_count_lbl.setStyleSheet(f"color:{TEXT_MUTED}; font-size:12px;")
        check_row.addWidget(self._checked_count_lbl)
        lay.addLayout(check_row)

        sep = QtWidgets.QFrame()
        sep.setFrameShape(_Frame_HLine)
        sep.setStyleSheet(f"background:{BORDER}; border:none; max-height:1px;")
        lay.addWidget(sep)

        # ── Action buttons ────────────────────────────────────────────────────
        action_row = QtWidgets.QHBoxLayout()
        action_row.setSpacing(10)

        btn_select_max = QtWidgets.QPushButton("📌  Select in 3ds Max")
        btn_select_max.setObjectName("btn_warning")
        btn_select_max.setToolTip(
            "Selects the checked CHILD objects in the 3ds Max viewport so you can "
            "visually confirm which objects will be re-linked before applying."
        )
        btn_select_max.clicked.connect(self._select_in_max)

        btn_relink = QtWidgets.QPushButton("🔗  LinkBack Selected")
        btn_relink.setObjectName("btn_success")
        btn_relink.setToolTip(
            "Re-link checked child objects back to their saved parents "
            "(restores the relationship as it was when you clicked Save Links)."
        )
        btn_relink.clicked.connect(self._relink_selected)

        action_row.addStretch()
        action_row.addWidget(btn_select_max)
        action_row.addWidget(btn_relink)
        lay.addLayout(action_row)

        return w

    # ── HELP TAB ──────────────────────────────────────────────────────────────
    def _build_help_tab(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)
        lay.setContentsMargins(20, 20, 20, 20)

        txt = QtWidgets.QTextBrowser()
        txt.setOpenExternalLinks(True)
        txt.setStyleSheet(
            f"background:{CARD_BG}; color:{TEXT_PRIMARY}; border:1px solid {BORDER};"
            "border-radius:8px; padding:12px; font-size:13px; line-height:1.6;"
        )
        txt.setHtml(f"""
<h2 style="color:{ACCENT};">📖 How to use LinkBack</h2>

<h3 style="color:{WARNING};">Problem</h3>
<p>In 3ds Max, objects can be <b>linked</b> (parent → child hierarchy). Sometimes
you export or hand off a scene and some objects are still linked — causing unexpected
transforms or pivot issues. LinkBack helps you <i>remember</i> what was linked and
<i>undo</i> those links later.</p>

<h3 style="color:{SUCCESS};">Step 1 — Save Links (before exporting / sending scene)</h3>
<ol>
  <li>Switch to the <b>💾 Save Links</b> tab.</li>
  <li>Choose <b>All objects</b> or select specific objects and pick <b>Selected only</b>.</li>
  <li>Give the session a name (optional).</li>
  <li>Click <b>Browse…</b> to choose where to save the JSON file.</li>
  <li>Click <b>🔍 Scan Links</b> — review the preview table.</li>
  <li>Click <b>💾 Save to JSON</b>.</li>
</ol>

<h3 style="color:{ACCENT_HOVER};">Step 2 — Restore links (when you open the scene again)</h3>
<ol>
  <li>Switch to the <b>🔗 Load &amp; LinkBack</b> tab.</li>
  <li>Browse to your saved JSON and click <b>📂 Load</b>.</li>
  <li>Pick the session from the drop-down.</li>
  <li>Review the table — each row shows a child object and its saved parent.</li>
  <li>Tick the rows you want to re-link (or <i>Check All</i>).</li>
  <li>Optionally click <b>📌 Select in 3ds Max</b> to highlight the child objects first.</li>
  <li>Click <b>🔗 LinkBack Selected</b> — objects are re-attached to their saved parents.</li>
</ol>

<h3 style="color:{TEXT_MUTED};">Tips</h3>
<ul>
  <li>You can save <b>multiple sessions</b> to the same JSON file and switch between them.</li>
  <li>Objects are found by <b>handle first</b>, then by name — rename-safe as long as the
      scene file is the same.</li>
  <li>Undo is available in 3ds Max (Ctrl+Z) after unlinking.</li>
</ul>
""")
        lay.addWidget(txt)
        return w

    # ═══════════════════════════════════════════════════════════════════════════
    #  SAVE TAB LOGIC
    # ═══════════════════════════════════════════════════════════════════════════

    def _browse_save(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save LinkBack JSON", "", "JSON Files (*.json);;All Files (*)"
        )
        if path:
            self._save_path_edit.setText(path)

    def _scan_links(self):
        scope = "selected" if self._rb_sel.isChecked() else "all"
        links = collect_links_from_scene(scope)

        self._preview_tree.clear()
        for lnk in links:
            item = LinkTreeItem(lnk)
            item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)  # no checkbox in preview
            self._preview_tree.addTopLevelItem(item)

        count = len(links)
        if count == 0:
            self._save_count_lbl.setText("⚠  No links found.")
            self._status.setText("Scan complete — no linked objects found.")
        else:
            self._save_count_lbl.setText(f"✓  {count} link(s) found.")
            self._status.setText(f"Scan complete — {count} link(s) found. Ready to save.")

        # store for saving
        self._scanned_links = links

    def _save_links(self):
        path = self._save_path_edit.text().strip()
        if not path:
            QtWidgets.QMessageBox.warning(self, "No Path", "Please choose a JSON file path first.")
            return

        links = getattr(self, "_scanned_links", None)
        if links is None:
            QtWidgets.QMessageBox.warning(self, "Not Scanned", "Click Scan Links first.")
            return
        if len(links) == 0:
            QtWidgets.QMessageBox.information(self, "Nothing to Save", "No links were found during scan.")
            return

        name = self._session_name_edit.text().strip() or None
        session = LinkSession(name=name, links=links)
        try:
            save_links_to_json(session, path)
        except Exception as ex:
            QtWidgets.QMessageBox.critical(self, "Save Error", str(ex))
            return

        self._status.setText(
            f"✓  Saved {len(links)} link(s) to  {os.path.basename(path)}  "
            f"(session: {session.name})"
        )
        QtWidgets.QMessageBox.information(
            self, "Saved",
            f"✓  {len(links)} link relationship(s) saved.\n\n"
            f"Session : {session.name}\n"
            f"File    : {path}"
        )

    # ═══════════════════════════════════════════════════════════════════════════
    #  LOAD/UNLINK TAB LOGIC
    # ═══════════════════════════════════════════════════════════════════════════

    def _browse_load(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open LinkBack JSON", "", "JSON Files (*.json);;All Files (*)"
        )
        if path:
            self._load_path_edit.setText(path)

    def _load_file(self):
        path = self._load_path_edit.text().strip()
        if not path:
            QtWidgets.QMessageBox.warning(self, "No Path", "Please choose a JSON file first.")
            return
        if not os.path.isfile(path):
            QtWidgets.QMessageBox.warning(self, "Not Found", f"File not found:\n{path}")
            return

        self._sessions = load_sessions_from_json(path)
        self._json_path = path

        self._session_combo.blockSignals(True)
        self._session_combo.clear()
        for s in self._sessions:
            self._session_combo.addItem(f"{s.name}  [{s.timestamp}]  ({len(s.links)} links)")
        self._session_combo.blockSignals(False)

        if self._sessions:
            self._session_combo.setCurrentIndex(len(self._sessions) - 1)
            self._on_session_changed(len(self._sessions) - 1)
            self._status.setText(
                f"✓  Loaded {len(self._sessions)} session(s) from {os.path.basename(path)}"
            )
        else:
            self._link_tree.clear()
            self._status.setText("⚠  No sessions found in file.")

    def _on_session_changed(self, idx: int):
        if idx < 0 or idx >= len(self._sessions):
            return
        session = self._sessions[idx]
        self._sess_info_lbl.setText(
            f"Saved: {session.timestamp}  ·  {len(session.links)} link(s)"
        )
        self._populate_link_tree(session.links)

    def _populate_link_tree(self, links: List[LinkData]):
        self._link_tree.blockSignals(True)
        self._link_tree.clear()

        # Group by parent for readability
        parent_groups: Dict[str, List[LinkData]] = {}
        for lnk in links:
            parent_groups.setdefault(lnk.parent, []).append(lnk)

        for parent_name, children in sorted(parent_groups.items()):
            if len(parent_groups) > 1:
                # Create a group header
                grp = QtWidgets.QTreeWidgetItem(self._link_tree)
                grp.setText(0, f"▸  Parent: {parent_name}")
                grp.setText(1, f"({len(children)} children)")
                grp.setForeground(0, QtGui.QColor(WARNING))
                grp.setForeground(1, QtGui.QColor(TEXT_MUTED))
                grp.setFlags(grp.flags() & ~Qt.ItemIsUserCheckable)
                grp.setExpanded(True)
                for lnk in children:
                    child_item = LinkTreeItem(lnk, grp)
                    self._link_tree.addTopLevelItem  # child added via parent
            else:
                for lnk in children:
                    item = LinkTreeItem(lnk)
                    self._link_tree.addTopLevelItem(item)

        self._link_tree.expandAll()
        self._link_tree.blockSignals(False)
        self._update_checked_count()

    def _on_item_checked_changed(self, item, column):
        if column == 0:
            self._update_checked_count()

    def _update_checked_count(self):
        count = self._count_checked()
        self._checked_count_lbl.setText(f"{count} item(s) checked")

    def _count_checked(self) -> int:
        count = 0
        def _walk(item):
            nonlocal count
            if hasattr(item, "link_data") and item.checkState(0) == Qt.Checked:
                count += 1
            for i in range(item.childCount()):
                _walk(item.child(i))
        for i in range(self._link_tree.topLevelItemCount()):
            _walk(self._link_tree.topLevelItem(i))
        return count

    def _collect_checked(self) -> List[LinkData]:
        result = []
        def _walk(item):
            if hasattr(item, "link_data") and item.checkState(0) == Qt.Checked:
                result.append(item.link_data)
            for i in range(item.childCount()):
                _walk(item.child(i))
        for i in range(self._link_tree.topLevelItemCount()):
            _walk(self._link_tree.topLevelItem(i))
        return result

    def _set_all_checked(self, state: bool):
        check = Qt.Checked if state else Qt.Unchecked
        self._link_tree.blockSignals(True)
        def _walk(item):
            if hasattr(item, "link_data"):
                item.setCheckState(0, check)
            for i in range(item.childCount()):
                _walk(item.child(i))
        for i in range(self._link_tree.topLevelItemCount()):
            _walk(self._link_tree.topLevelItem(i))
        self._link_tree.blockSignals(False)
        self._update_checked_count()

    def _select_in_max(self):
        links = self._collect_checked()
        if not links:
            QtWidgets.QMessageBox.information(
                self, "Nothing Checked", "Tick at least one row before selecting."
            )
            return
        names = [l.child for l in links]
        select_objects_in_max(names)
        self._status.setText(
            f"📌  Selected {len(names)} object(s) in 3ds Max: {', '.join(names[:5])}"
            + ("…" if len(names) > 5 else "")
        )

    def _relink_selected(self):
        links = self._collect_checked()
        if not links:
            QtWidgets.QMessageBox.information(
                self, "Nothing Checked", "Tick at least one row before linking back."
            )
            return

        names_preview = "\n".join(
            f"  • {l.child}  →  parent: {l.parent}" for l in links[:10]
        )
        if len(links) > 10:
            names_preview += f"\n  … and {len(links) - 10} more"

        confirm = QtWidgets.QMessageBox.question(
            self,
            "Confirm LinkBack",
            f"Re-link {len(links)} object(s) back to their saved parents:\n\n"
            f"{names_preview}\n\n"
            "3ds Max Undo (Ctrl+Z) is available.\n\nProceed?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No,
        )

        if confirm != QtWidgets.QMessageBox.Yes:
            return

        result = relink_objects(links)

        msg = (
            f"✅  LinkBack complete.\n\n"
            f"  Re-linked : {result['ok']}\n"
            f"  Not found : {result['not_found']}\n"
            f"  Errors    : {result['errors']}"
        )
        self._status.setText(
            f"🔗  LinkBack — OK:{result['ok']}  "
            f"NotFound:{result['not_found']}  Err:{result['errors']}"
        )
        QtWidgets.QMessageBox.information(self, "UnlinkBack Result", msg)


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

_window_instance: Optional[LinkBackWindow] = None


def launch():
    """Open (or raise) the LinkBack window inside 3ds Max 2025."""
    global _window_instance

    # Ensure a QApplication exists (Max provides one)
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    if _window_instance is not None:
        try:
            _window_instance.raise_()
            _window_instance.activateWindow()
            return _window_instance
        except RuntimeError:
            _window_instance = None

    parent = _max_main_window()
    _window_instance = LinkBackWindow(parent=parent)
    _window_instance.show()
    return _window_instance


# Allow direct execution for testing outside Max
if __name__ == "__main__":
    _app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    win = launch()
    if not _IN_MAX:
        _app.exec_()
