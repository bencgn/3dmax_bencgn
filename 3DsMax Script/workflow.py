"""
Workflow Tool - Step 1: Object Renamer
3ds Max Python Script
Rename selected objects with prefix (SM_) and type/suffix options.
"""

try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui

import pymxs
from pymxs import runtime as rt


# ─────────────────────────────────────────────────────────────────────────────
# Main Dialog
# ─────────────────────────────────────────────────────────────────────────────

class ObjectRenamerDialog(QtWidgets.QDialog):
    """Workflow Step 1 – Select Objects → Rename with Prefix/Suffix."""

    TYPE_BUTTONS = [
        ("Glass",         "Glass"),
        ("Floor",         "Floor"),
        ("Wall_1",        "Wall_1"),
        ("Wall_2",        "Wall_2"),
        ("Wall_3",        "Wall_3"),
        ("Ceiling",       "Ceiling"),
        ("Full",          "Full"),
        ("WallInterior",  "WallInterior"),
        ("WallExter",     "WallExter"),
        ("Decor1",        "Decor1"),
        ("WallDecor",     "WallDecor"),
        ("Roof",          "Roof"),
    ]

    def __init__(self, parent=None):
        super(ObjectRenamerDialog, self).__init__(parent)
        self.setWindowTitle("Workflow – Object Renamer")
        self.setWindowFlags(
            self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint
        )
        self.setMinimumWidth(400)
        self._build_ui()
        self._apply_style()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(12, 12, 12, 12)

        # Header
        title = QtWidgets.QLabel("⬡  Object Renamer  —  Step 1")
        title.setObjectName("title")
        root.addWidget(title)
        root.addWidget(self._hr())

        # Selection info
        sel_row = QtWidgets.QHBoxLayout()
        self.lbl_sel = QtWidgets.QLabel("No objects selected")
        self.lbl_sel.setObjectName("selInfo")
        self.btn_refresh = QtWidgets.QPushButton("⟳ Refresh")
        self.btn_refresh.setFixedWidth(80)
        self.btn_refresh.clicked.connect(self._refresh_selection)
        sel_row.addWidget(self.lbl_sel)
        sel_row.addStretch()
        sel_row.addWidget(self.btn_refresh)
        root.addLayout(sel_row)
        root.addWidget(self._hr())

        # ── Prefix ────────────────────────────────────────────────────────────
        pfx_grp = QtWidgets.QGroupBox("Prefix")
        pfx_lay = QtWidgets.QHBoxLayout(pfx_grp)
        self.chk_prefix = QtWidgets.QCheckBox("SM_")
        self.chk_prefix.setChecked(True)
        pfx_lay.addWidget(self.chk_prefix)
        pfx_lay.addStretch()
        root.addWidget(pfx_grp)

        # ── Object Type buttons ───────────────────────────────────────────────
        type_grp = QtWidgets.QGroupBox("Object Type  (choose one)")
        type_grid = QtWidgets.QGridLayout(type_grp)
        type_grid.setSpacing(6)

        self._type_btn_group = QtWidgets.QButtonGroup(self)
        self._type_btn_group.setExclusive(True)

        for idx, (label, keyword) in enumerate(self.TYPE_BUTTONS):
            btn = QtWidgets.QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("typeKeyword", keyword)
            btn.clicked.connect(self._on_type_selected)
            self._type_btn_group.addButton(btn, idx)
            row, col = divmod(idx, 3)
            type_grid.addWidget(btn, row, col)

        # Custom type field
        self.txt_custom_type = QtWidgets.QLineEdit()
        self.txt_custom_type.setPlaceholderText("Custom type …")
        self.txt_custom_type.textChanged.connect(self._on_custom_type_changed)
        num_rows = (len(self.TYPE_BUTTONS) + 2) // 3
        type_grid.addWidget(self.txt_custom_type, num_rows, 0, 1, 3)
        root.addWidget(type_grp)

        # ── Suffix ────────────────────────────────────────────────────────────
        sfx_grp = QtWidgets.QGroupBox("Suffix")
        sfx_lay = QtWidgets.QVBoxLayout(sfx_grp)

        self._sfx_btn_group = QtWidgets.QButtonGroup(self)
        self._sfx_btn_group.setExclusive(True)

        self.rb_inst   = QtWidgets.QRadioButton("inst")
        self.rb_none   = QtWidgets.QRadioButton("(no suffix)")
        self.rb_custom = QtWidgets.QRadioButton("Custom:")
        self.rb_inst.setChecked(True)

        self._sfx_btn_group.addButton(self.rb_inst,   0)
        self._sfx_btn_group.addButton(self.rb_none,   1)
        self._sfx_btn_group.addButton(self.rb_custom, 2)

        self.txt_suffix = QtWidgets.QLineEdit()
        self.txt_suffix.setPlaceholderText("Type suffix …")
        self.txt_suffix.setEnabled(False)
        self.rb_custom.toggled.connect(self.txt_suffix.setEnabled)

        sfx_lay.addWidget(self.rb_inst)
        sfx_lay.addWidget(self.rb_none)
        row_custom = QtWidgets.QHBoxLayout()
        row_custom.addWidget(self.rb_custom)
        row_custom.addWidget(self.txt_suffix)
        sfx_lay.addLayout(row_custom)
        root.addWidget(sfx_grp)

        # ── Preview ───────────────────────────────────────────────────────────
        prev_grp = QtWidgets.QGroupBox("Name Preview")
        prev_lay = QtWidgets.QHBoxLayout(prev_grp)
        self.lbl_preview = QtWidgets.QLabel("SM_…")
        self.lbl_preview.setObjectName("preview")
        prev_lay.addWidget(self.lbl_preview)
        root.addWidget(prev_grp)

        # Connect preview triggers
        self.chk_prefix.toggled.connect(self._update_preview)
        self._type_btn_group.buttonClicked.connect(self._update_preview)
        self._sfx_btn_group.buttonClicked.connect(self._update_preview)
        self.txt_suffix.textChanged.connect(self._update_preview)
        self.txt_custom_type.textChanged.connect(self._update_preview)

        # ── Action buttons ────────────────────────────────────────────────────
        btn_row = QtWidgets.QHBoxLayout()
        self.btn_rename = QtWidgets.QPushButton("✔  Rename Selected")
        self.btn_rename.setObjectName("primaryBtn")
        self.btn_rename.clicked.connect(self._do_rename)
        btn_close = QtWidgets.QPushButton("✖  Close")
        btn_close.clicked.connect(self.close)
        btn_row.addWidget(self.btn_rename)
        btn_row.addWidget(btn_close)
        root.addLayout(btn_row)

        # Status bar
        self.lbl_status = QtWidgets.QLabel("")
        self.lbl_status.setObjectName("status")
        root.addWidget(self.lbl_status)

        self._refresh_selection()
        self._update_preview()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _hr(self):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        return line

    def _apply_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11pt;
            }
            QGroupBox {
                border: 1px solid #45475a;
                border-radius: 6px;
                margin-top: 8px;
                padding: 8px 6px 6px 6px;
                color: #89b4fa;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
            }
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover { background-color: #45475a; }
            QPushButton:checked {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: 1px solid #89b4fa;
                font-weight: bold;
            }
            QPushButton#primaryBtn {
                background-color: #a6e3a1;
                color: #1e1e2e;
                font-weight: bold;
                border: none;
            }
            QPushButton#primaryBtn:hover { background-color: #94e2d5; }
            QLineEdit {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 4px 6px;
            }
            QLineEdit:focus { border: 1px solid #89b4fa; }
            QCheckBox, QRadioButton { color: #cdd6f4; spacing: 6px; }
            QLabel#title {
                font-size: 14pt;
                font-weight: bold;
                color: #cba6f7;
            }
            QLabel#selInfo { color: #f9e2af; }
            QLabel#preview {
                font-size: 12pt;
                font-weight: bold;
                color: #a6e3a1;
                padding: 4px;
            }
            QLabel#status { color: #f38ba8; font-size: 9pt; }
        """)

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _refresh_selection(self):
        count = rt.selection.count
        if count == 0:
            self.lbl_sel.setText("No objects selected")
        elif count == 1:
            self.lbl_sel.setText(f"1 object:  {rt.selection[0].name}")
        else:
            self.lbl_sel.setText(f"{count} objects selected")

    def _on_type_selected(self):
        self.txt_custom_type.blockSignals(True)
        self.txt_custom_type.clear()
        self.txt_custom_type.blockSignals(False)
        self._update_preview()

    def _on_custom_type_changed(self, text):
        if text.strip():
            checked = self._type_btn_group.checkedButton()
            if checked:
                self._type_btn_group.setExclusive(False)
                checked.setChecked(False)
                self._type_btn_group.setExclusive(True)
        self._update_preview()

    def _build_name(self, index=None):
        parts = []
        if self.chk_prefix.isChecked():
            parts.append("SM")

        custom_type = self.txt_custom_type.text().strip()
        if custom_type:
            type_str = custom_type
        else:
            checked = self._type_btn_group.checkedButton()
            type_str = checked.property("typeKeyword") if checked else ""

        if type_str:
            parts.append(type_str)

        if index is not None:
            parts.append(f"{index:02d}")

        if self.rb_inst.isChecked():
            parts.append("inst")
        elif self.rb_custom.isChecked():
            sfx = self.txt_suffix.text().strip()
            if sfx:
                parts.append(sfx)

        return "_".join(parts)

    def _update_preview(self):
        self.lbl_preview.setText(self._build_name())

    def _do_rename(self):
        sel = [rt.selection[i] for i in range(rt.selection.count)]
        if not sel:
            self.lbl_status.setText("⚠ Nothing selected — select objects first!")
            self.lbl_status.setStyleSheet("color:#f38ba8;")
            return

        with pymxs.undo(True, "Workflow Rename"):
            for i, obj in enumerate(sel):
                if len(sel) > 1:
                    new_name = self._build_name(index=i + 1)
                else:
                    new_name = self._build_name()
                obj.name = new_name

        self.lbl_status.setText(f"✔  Renamed {len(sel)} object(s).")
        self.lbl_status.setStyleSheet("color:#a6e3a1;")
        self._refresh_selection()
        self._update_preview()


# ─────────────────────────────────────────────────────────────────────────────
# Launch — keeps a global reference so PySide2 GC won't destroy the dialog
# ─────────────────────────────────────────────────────────────────────────────

_dialog_instance = None

def show_ui():
    global _dialog_instance
    try:
        _dialog_instance.close()
        _dialog_instance.deleteLater()
    except Exception:
        pass
    _dialog_instance = ObjectRenamerDialog()
    _dialog_instance.show()

if __name__ == "__main__":
    show_ui()
