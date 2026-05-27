"""
convertAutodeskGeneric_to_glTFMaterial.py
-----------------------------------------
Standalone 3ds Max tool to convert Autodesk Generic sub-materials
inside a Multi/Sub-Object material to glTF materials, keeping colors
and texture maps intact.

Usage:
    Run this script from the 3ds Max Script Editor or via a macroscript.
    Select an object with a Multi/Sub-Object material, then click Convert.
"""

try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    try:
        from PySide6 import QtWidgets, QtCore, QtGui
    except ImportError:
        raise RuntimeError("PySide2 / PySide6 not available. Run inside 3ds Max.")

from pymxs import runtime as rt


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------

def get_mat_class_name(mat):
    """Return the real MaxScript class name as a plain Python string."""
    try:
        return str(rt.classOf(mat))
    except Exception:
        return ""


def is_autodesk_generic(mat):
    """
    True when mat is an Autodesk Material (Generic, Concrete, etc.).
    """
    cls = get_mat_class_name(mat).lower()
    if "autodesk" in cls:
        return True
    # Heuristic fallback (catches exotic plugin builds)
    if hasattr(mat, "base_color") and hasattr(mat, "base_color_map"):
        return True
    return False


def find_gltf_class():
    """
    Return the MaxScript class for the glTF material plugin,
    or None if no glTF plugin is installed.
    Tries every known class name across different plugin versions.
    """
    candidates = [
        "glTFMaterial", "glTF_Material", "glTF2Material",
        "GLTF_Material", "BabylonMaterial",
    ]
    for name in candidates:
        cls = getattr(rt, name, None)
        if cls is not None:
            return cls
    # Last resort — rt.execute
    for mxs_name in ("glTFMaterial", "glTF_Material"):
        try:
            cls = rt.execute(mxs_name)
            if cls is not None:
                return cls
        except Exception:
            pass
    return None


def copy_color_to_gltf(new_mat, src_color):
    """
    Copy src_color to the glTF material using whatever attribute name the
    installed plugin exposes.  Returns hex string '#RRGGBB' on success.
    """
    if src_color is None:
        return None
    try:
        r, g, b = int(src_color.r), int(src_color.g), int(src_color.b)
    except Exception:
        return None
    hex_str = "#{:02X}{:02X}{:02X}".format(r, g, b)

    for attr in ("baseColorFactor", "baseColor", "base_color",
                 "diffuse", "albedo", "albedoColor"):
        if hasattr(new_mat, attr):
            try:
                setattr(new_mat, attr, src_color)
                return hex_str
            except Exception:
                pass
    return hex_str   # color was read; assignment may have failed


def copy_map_to_gltf(new_mat, src_map):
    """Copy texture map to the glTF material."""
    if src_map is None:
        return
    for attr in ("baseColorTexture", "baseColor_map", "base_color_map",
                 "diffuseMap", "albedoTexture"):
        if hasattr(new_mat, attr):
            try:
                setattr(new_mat, attr, src_map)
                return
            except Exception:
                pass


# ---------------------------------------------------------------------------
#  UI
# ---------------------------------------------------------------------------

class ConvertGenericToGLTFDialog(QtWidgets.QDialog):

    # --- Style constants ---
    _STYLE = """
        QDialog {
            background-color: #2b2b2b;
            color: #e0e0e0;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }
        QLabel {
            color: #cccccc;
        }
        QListWidget {
            background-color: #1e1e1e;
            color: #d4d4d4;
            border: 1px solid #444;
            border-radius: 4px;
            font-size: 12px;
        }
        QListWidget::item:selected {
            background-color: #094771;
        }
        QPushButton {
            border-radius: 4px;
            padding: 4px 10px;
        }
        QGroupBox {
            color: #aaaaaa;
            border: 1px solid #444;
            border-radius: 5px;
            margin-top: 6px;
            font-size: 12px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px;
        }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Convert Autodesk Generic → glTF Material")
        self.resize(620, 560)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.setStyleSheet(self._STYLE)
        self._build_ui()

    # -----------------------------------------------------------------------
    #  UI construction
    # -----------------------------------------------------------------------

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setSpacing(8)
        root.setContentsMargins(10, 10, 10, 10)

        # --- Title label ---
        title = QtWidgets.QLabel("Autodesk Generic  →  glTF Material Converter")
        title.setStyleSheet(
            "font-size:15px; font-weight:bold; color:#4ec9b0; padding:4px 0;"
        )
        root.addWidget(title)

        # --- Action buttons ---
        grp_actions = QtWidgets.QGroupBox("Actions")
        act_layout  = QtWidgets.QVBoxLayout(grp_actions)
        act_layout.setSpacing(6)

        self.btn_debug = self._make_btn(
            "[Debug] List Material Class Names",
            "#3a3a3a", "#505050",
            self.run_debug,
            tooltip="Inspect the real MaxScript class of every sub-material.\n"
                    "Green rows will be converted; grey rows will be skipped.",
            font_size=11,
        )
        act_layout.addWidget(self.btn_debug)

        self.btn_convert = self._make_btn(
            "▶  Convert Autodesk Generic → glTF Material  (Keep Color)",
            "#0e6b3a", "#168a4c",
            self.run_convert,
            tooltip="Convert every Autodesk Generic sub-material to a glTF\n"
                    "material, preserving base color and texture maps.",
            bold=True,
            height=44,
        )
        act_layout.addWidget(self.btn_convert)

        root.addWidget(grp_actions)

        # --- Results list ---
        grp_results = QtWidgets.QGroupBox("Results")
        res_layout  = QtWidgets.QVBoxLayout(grp_results)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setStyleSheet(
            "QListWidget { alternate-background-color: #252525; }"
        )
        res_layout.addWidget(self.list_widget)
        root.addWidget(grp_results, stretch=1)

        # --- Status bar ---
        self.lbl_status = QtWidgets.QLabel("Select an Editable Poly with a Multi/Sub-Object material.")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet(
            "color:#9cdcfe; font-size:12px; padding:3px 2px;"
        )
        root.addWidget(self.lbl_status)

        # --- Close button ---
        btn_close = self._make_btn("Close", "#555", "#666", self.close)
        root.addWidget(btn_close)

    @staticmethod
    def _make_btn(label, bg, bg_hover, slot,
                  tooltip="", bold=False, height=34, font_size=13):
        btn = QtWidgets.QPushButton(label)
        btn.setMinimumHeight(height)
        weight = "bold" if bold else "normal"
        btn.setStyleSheet(
            f"QPushButton {{ background-color:{bg}; color:white; border-radius:4px;"
            f"  font-size:{font_size}px; font-weight:{weight}; }}"
            f"QPushButton:hover {{ background-color:{bg_hover}; }}"
            f"QPushButton:pressed {{ background-color:{bg}; }}"
        )
        if tooltip:
            btn.setToolTip(tooltip)
        btn.clicked.connect(slot)
        return btn

    # -----------------------------------------------------------------------
    #  Helpers
    # -----------------------------------------------------------------------

    def _post(self, text, bg=None, fg=None, hex_color=None):
        """Append a row to the results list."""
        item = QtWidgets.QListWidgetItem(text)
        if bg:
            item.setBackground(QtGui.QColor(bg))
        if fg:
            item.setForeground(QtGui.QColor(fg))
        if hex_color:
            try:
                px = QtGui.QPixmap(18, 18)
                px.fill(QtGui.QColor(hex_color))
                item.setIcon(QtGui.QIcon(px))
            except Exception:
                pass
        self.list_widget.addItem(item)
        self.list_widget.scrollToBottom()

    def _set_status(self, text, color="#9cdcfe"):
        self.lbl_status.setStyleSheet(
            f"color:{color}; font-size:12px; padding:3px 2px;"
        )
        self.lbl_status.setText(text)

    def _get_multi_mat(self):
        """
        Validates selection and returns (obj, multi_mat) or (None, None).
        Shows errors via _set_status.
        """
        sel = rt.selection
        if sel.count == 0:
            self._set_status("No object selected.", "#f48771")
            return None, None
        obj = sel[0]
        if not rt.isKindOf(obj, rt.Editable_Poly):
            self._set_status("Selected object is not an Editable Poly.", "#f48771")
            return None, None
        mat = obj.material
        if not mat or not rt.isKindOf(mat, rt.Multimaterial):
            self._set_status("No Multi/Sub-Object material on selected object.", "#f48771")
            return None, None
        return obj, mat

    # -----------------------------------------------------------------------
    #  Debug
    # -----------------------------------------------------------------------

    def run_debug(self):
        self.list_widget.clear()
        obj, multi_mat = self._get_multi_mat()
        if obj is None:
            return

        gltf_cls      = find_gltf_class()
        gltf_cls_name = str(gltf_cls) if gltf_cls else "NOT FOUND — install glTF plugin"

        # Header row
        self._post(
            f"  glTF plugin class detected:  {gltf_cls_name}",
            bg="#3a3000" if gltf_cls is None else "#003a1e",
            fg="#ffd700" if gltf_cls is None else "#4ec9b0",
        )
        self._post(
            f"  Multi/Sub-Object: '{multi_mat.name}'  ({multi_mat.numsubs} slots)"
            f"  |  Object: '{obj.name}'",
            bg="#202020",
        )

        will_convert = 0
        will_skip    = 0

        for i in range(1, multi_mat.numsubs + 1):
            try:
                sub = multi_mat[i]
            except Exception:
                sub = None
                
            if sub is None:
                self._post(f"  slot {i}  |  (empty)", fg="#555555")
                continue

            try:
                mat_id = multi_mat.materialIDList[i]
            except Exception:
                mat_id = i
                
            cls_name = get_mat_class_name(sub)
            generic  = is_autodesk_generic(sub)

            if generic:
                will_convert += 1
                flag = "✓  WILL CONVERT"
                bg   = "#1a3a1a"
                fg   = "#6fbf73"
            else:
                will_skip += 1
                flag = "✗  skip"
                bg   = None
                fg   = "#666666"

            # Show known color attrs for extra info
            color_val = (
                getattr(sub, "base_color",  None) or
                getattr(sub, "baseColor",   None) or
                getattr(sub, "diffuse",     None)
            )
            color_info = ""
            if color_val:
                try:
                    color_info = (
                        f"  color=#{int(color_val.r):02X}"
                        f"{int(color_val.g):02X}"
                        f"{int(color_val.b):02X}"
                    )
                except Exception:
                    pass

            self._post(
                f"  ID {mat_id:>3}  |  class='{cls_name}'  |  {flag}"
                f"{color_info}  |  name: {sub.name}",
                bg=bg, fg=fg,
            )

        self._set_status(
            f"[Debug]  Will convert: {will_convert}  |  Skip: {will_skip}.  "
            f"{'Run Convert when ready.' if will_convert else 'Nothing to convert — check class names above.'}",
            color="#4ec9b0" if will_convert else "#f48771",
        )

    # -----------------------------------------------------------------------
    #  Convert
    # -----------------------------------------------------------------------

    def run_convert(self):
        self.list_widget.clear()
        obj, multi_mat = self._get_multi_mat()
        if obj is None:
            return

        gltf_cls = find_gltf_class()
        if gltf_cls is None:
            self._set_status(
                "ERROR: glTF Material plugin not found.  "
                "Install Babylon.js Exporter (Max2Babylon) or Autodesk glTF plugin, "
                "then restart 3ds Max.",
                color="#f48771",
            )
            self.run_debug()   # still show class names for troubleshooting
            return

        gltf_cls_name = str(gltf_cls)
        self._post(
            f"  glTF class: {gltf_cls_name}  |  Multi: '{multi_mat.name}'  |  Object: '{obj.name}'",
            bg="#003a1e", fg="#4ec9b0",
        )

        converted = 0
        skipped   = 0
        errors    = 0

        for i in range(1, multi_mat.numsubs + 1):
            try:
                sub = multi_mat[i]
            except Exception:
                sub = None
                
            if sub is None:
                continue

            try:
                mat_id = multi_mat.materialIDList[i]
            except Exception:
                mat_id = i
                
            cls_name = get_mat_class_name(sub)

            # ---- Skip non-Autodesk-Generic ----
            if not is_autodesk_generic(sub):
                skipped += 1
                self._post(
                    f"  [SKIP]   ID {mat_id:>3}  class='{cls_name}'  name={sub.name}",
                    fg="#666666",
                )
                continue

            # ---- Read source color & map ----
            src_color      = None
            color_attr     = "(none)"
            src_map        = None

            common_colors = ["Generic_Color", "base_color", "baseColor", "diffuse", "color"]
            for cattr in common_colors:
                if hasattr(sub, cattr):
                    v = getattr(sub, cattr, None)
                    if v is not None:
                        src_color  = v
                        color_attr = cattr
                        break

            if src_color is None:
                try:
                    for prop in rt.getPropNames(sub):
                        pname = str(prop)
                        if pname.lower().endswith("_color"):
                            v = getattr(sub, pname, None)
                            if v is not None:
                                src_color = v
                                color_attr = pname
                                break
                except Exception:
                    pass

            common_maps = ["Generic_Image", "base_color_map", "baseColorTexture", "baseColor_map", "diffuseMap", "map"]
            for mattr in common_maps:
                if hasattr(sub, mattr):
                    v = getattr(sub, mattr, None)
                    if v is not None:
                        src_map = v
                        break
            
            if src_map is None:
                try:
                    for prop in rt.getPropNames(sub):
                        pname = str(prop)
                        if pname.lower().endswith("_image"):
                            v = getattr(sub, pname, None)
                            if v is not None:
                                src_map = v
                                break
                except Exception:
                    pass

            # ---- Create glTF material ----
            try:
                new_mat = gltf_cls()
            except Exception as exc:
                errors += 1
                self._post(
                    f"  [ERROR]  ID {mat_id:>3}  name={sub.name}  —  could not create glTF: {exc}",
                    fg="#f48771",
                )
                continue

            original_name = sub.name
            new_mat.name  = original_name + "_glTF"

            # ---- Copy color & map ----
            hex_color = copy_color_to_gltf(new_mat, src_color)
            copy_map_to_gltf(new_mat, src_map)

            # ---- Replace slot ----
            multi_mat[i] = new_mat
            converted += 1

            map_label = src_map.name if src_map else "none"
            color_str = hex_color   if hex_color else "(read failed)"

            self._post(
                f"  [OK]     ID {mat_id:>3}  {original_name}  →  {new_mat.name}"
                f"  |  color({color_attr}): {color_str}  |  map: {map_label}",
                bg="#1a3a1a",
                fg="#6fbf73",
                hex_color=hex_color,
            )

        # ---- Summary ----
        summary = (
            f"Done  —  Converted: {converted}  |  "
            f"Skipped (other type): {skipped}  |  Errors: {errors}"
        )
        if skipped and converted == 0:
            summary += "  ← Run [Debug] to inspect class names."
        self._set_status(
            summary,
            color="#4ec9b0" if errors == 0 else "#f48771",
        )
        self._post(f"\n  {summary}", bg="#1e1e1e", fg="#9cdcfe")


# ---------------------------------------------------------------------------
#  Entry point
# ---------------------------------------------------------------------------

def main():
    global _convert_gltf_dialog
    try:
        _convert_gltf_dialog.close()
        _convert_gltf_dialog.deleteLater()
    except Exception:
        pass
    _convert_gltf_dialog = ConvertGenericToGLTFDialog()
    _convert_gltf_dialog.show()


if __name__ == "__main__":
    main()
