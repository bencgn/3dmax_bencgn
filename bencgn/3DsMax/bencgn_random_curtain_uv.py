# -*- coding: utf-8 -*-
"""
BENCGN - Random Curtain UV
--------------------------
Copy UV cua cac FACE MAU (template) sang cac FACE duoc chon, chon ngau nhien.
Giu dung huong U/V: khong lat, khong xoay, khong lech.

YEU CAU:
  - Object phai la Editable Poly.
  - Neu con modifier Unwrap UVW o tren -> COLLAPSE ve Editable Poly truoc khi chay
    (de UV nam that su o Map Channel cua poly).
  - Cac face nen la QUAD (4 dinh). Face khong phai quad se bi bo qua.

CACH CHAY: 3ds Max > Scripting > Run Python Script... > chon file nay.
"""

import random

try:
    from PySide6 import QtWidgets, QtCore
except ImportError:
    from PySide2 import QtWidgets, QtCore

from pymxs import runtime as rt
import pymxs

try:
    import qtmax
    _MAIN_WIN = qtmax.GetQMaxMainWindow()
except Exception:
    _MAIN_WIN = None


# ----------------------------- vector helpers -----------------------------
def _sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def _dot(a, b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def _scale(a, s): return (a[0]*s, a[1]*s, a[2]*s)
def _len(a): return (a[0]*a[0]+a[1]*a[1]+a[2]*a[2]) ** 0.5
def _norm(a):
    l = _len(a)
    return (a[0]/l, a[1]/l, a[2]/l) if l > 1e-9 else (0.0, 0.0, 0.0)


# --------------------------- max mesh helpers -----------------------------
def _world_vert(obj, vi):
    # Lay toa do dinh trong WORLD space (de world-Z luon la phuong dung)
    p = rt.polyop.getVert(obj, vi, node=obj)
    return (float(p.x), float(p.y), float(p.z))


def _face_frame_coords(positions):
    """Tra ve list (u,v) cua tung goc trong he truc cuc bo cua face.
    up = world Z chieu vao mat phang face  -> truc V
    right = n x up                         -> truc U
    """
    c = (sum(p[0] for p in positions)/len(positions),
         sum(p[1] for p in positions)/len(positions),
         sum(p[2] for p in positions)/len(positions))
    n = _norm(_cross(_sub(positions[1], positions[0]),
                     _sub(positions[2], positions[0])))
    up = _sub((0.0, 0.0, 1.0), _scale(n, _dot((0.0, 0.0, 1.0), n)))
    if _len(up) < 1e-6:  # face nam ngang -> dung world Y lam du phong
        up = _sub((0.0, 1.0, 0.0), _scale(n, _dot((0.0, 1.0, 0.0), n)))
    up = _norm(up)
    right = _norm(_cross(n, up))
    out = []
    for p in positions:
        rel = _sub(p, c)
        out.append((_dot(rel, right), _dot(rel, up)))
    return out


def _classify(coords):
    """Phan 4 goc thanh TL/TR/BL/BR -> dict role=index (0..3). Luon du 4 role."""
    order_v = sorted(range(4), key=lambda i: coords[i][1])
    bottom = order_v[:2]   # v thap nhat
    top = order_v[2:]      # v cao nhat

    def lr(pair):
        a, b = pair
        return (a, b) if coords[a][0] <= coords[b][0] else (b, a)

    bl, br = lr(bottom)
    tl, tr = lr(top)
    return {'TL': tl, 'TR': tr, 'BL': bl, 'BR': br}


def _face_roles(obj, f):
    """Tra ve (geo_vert_indices, role->corner_k) cho 1 face quad."""
    gv = list(rt.polyop.getFaceVerts(obj, f))
    if len(gv) != 4:
        return None, None
    pos = [_world_vert(obj, v) for v in gv]
    roles = _classify(_face_frame_coords(pos))
    return gv, roles


def _read_template(obj, ch, f):
    """Doc UV cua face mau -> dict role->Point3(uv)."""
    gv, roles = _face_roles(obj, f)
    if gv is None:
        return None
    mf = list(rt.polyop.getMapFace(obj, ch, f))
    role_uv = {}
    for role, k in roles.items():
        uv = rt.polyop.getMapVert(obj, ch, mf[k])
        role_uv[role] = (float(uv.x), float(uv.y), float(uv.z))
    return role_uv


def _get_face_selection(obj):
    bits = rt.polyop.getFaceSelection(obj)
    n = rt.polyop.getNumFaces(obj)
    # pymxs BitArray: index 0-based, bits[i] la True/False cho face (i+1)
    return [i + 1 for i in range(n) if bits[i]]


def _face_centroid(obj, f):
    gv = list(rt.polyop.getFaceVerts(obj, f))
    ps = [_world_vert(obj, v) for v in gv]
    n = float(len(ps))
    return (sum(p[0] for p in ps)/n,
            sum(p[1] for p in ps)/n,
            sum(p[2] for p in ps)/n)


def _dist2(a, b):
    dx, dy, dz = a[0]-b[0], a[1]-b[1], a[2]-b[2]
    return dx*dx + dy*dy + dz*dz


def _face_basis(obj, f):
    """Tra ve (centroid, normal, right, up) world cua 1 face.
    up  = world Z chieu len mat phang face (truc DUNG)
    right = normal x up               (truc NGANG)
    """
    gv = list(rt.polyop.getFaceVerts(obj, f))
    ps = [_world_vert(obj, v) for v in gv]
    m = float(len(ps))
    c = (sum(p[0] for p in ps)/m, sum(p[1] for p in ps)/m, sum(p[2] for p in ps)/m)
    n = _norm(_cross(_sub(ps[1], ps[0]), _sub(ps[2], ps[0])))
    up = _sub((0.0, 0.0, 1.0), _scale(n, _dot((0.0, 0.0, 1.0), n)))
    if _len(up) < 1e-6:
        up = _sub((0.0, 1.0, 0.0), _scale(n, _dot((0.0, 1.0, 0.0), n)))
    up = _norm(up)
    right = _norm(_cross(n, up))
    return c, n, right, up


def _build_neighbors(obj, faces, reach_factor=1.6, normal_thresh=0.5):
    """Hang xom theo tung MAT (front/back/left/right...) tu dong:
      - Chi xet 2 face CUNG HUONG (dot phap tuyen > normal_thresh) -> khong lan
        lop truoc/sau cua rem tru.
      - Trong cung tam: chi lay hang xom TREN/DUOI/TRAI/PHAI (canh thang hang
        hoac thang cot), bo qua chieu sau.
    """
    flist = list(faces)
    basis = {f: _face_basis(obj, f) for f in flist}

    # spacing = trung vi khoang cach toi face cung-mat gan nhat
    nearest = []
    for i, f in enumerate(flist):
        cf, nf = basis[f][0], basis[f][1]
        dmin = None
        for g in flist:
            if g == f:
                continue
            if _dot(nf, basis[g][1]) < normal_thresh:
                continue
            d = _dist2(cf, basis[g][0])
            if dmin is None or d < dmin:
                dmin = d
        if dmin:
            nearest.append(dmin ** 0.5)
    nearest.sort()
    spacing = nearest[len(nearest)//2] if nearest else 1.0

    tol = spacing * 0.45          # sai so canh thang hang / thang cot
    reach = spacing * reach_factor  # khoang cach toi da coi la ke nhau

    neigh = {f: [] for f in flist}
    for i, f in enumerate(flist):
        cf, nf, rf, uf = basis[f]
        for g in flist[i+1:]:
            cg, ng = basis[g][0], basis[g][1]
            if _dot(nf, ng) < normal_thresh:      # khac mat -> bo
                continue
            rel = _sub(cg, cf)
            h = _dot(rel, rf)                     # lech ngang
            v = _dot(rel, uf)                     # lech doc
            ah, av = abs(h), abs(v)
            horiz = (av <= tol) and (tol < ah <= reach)   # trai / phai
            vert = (ah <= tol) and (tol < av <= reach)   # tren / duoi
            if horiz or vert:
                neigh[f].append(g)
                neigh[g].append(f)
    return neigh


def _greedy_color(faces, neigh, n_tpl, rng):
    """Gan chi so mau (0..n_tpl-1) sao cho hang xom khac mau, van ngau nhien."""
    order = list(faces)
    rng.shuffle(order)
    assign = {}
    for f in order:
        used = set(assign[g] for g in neigh.get(f, []) if g in assign)
        choices = [t for t in range(n_tpl) if t not in used]
        if not choices:                      # het mau -> danh chap nhan trung
            choices = list(range(n_tpl))
        assign[f] = rng.choice(choices)
    return assign



def _is_editable_poly(obj):
    return obj is not None and rt.isKindOf(obj.baseObject, rt.Editable_Poly)


def _has_unwrap(obj):
    for m in obj.modifiers:
        if rt.classOf(m) == rt.Unwrap_UVW and m.enabled:
            return True
    return False


# --------------------------------- UI -------------------------------------
class RandomCurtainUV(QtWidgets.QDialog):
    def __init__(self, parent=_MAIN_WIN):
        super(RandomCurtainUV, self).__init__(parent)
        self.setWindowTitle("BENCGN - Random Curtain UV")
        self.setMinimumWidth(300)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)

        self.node = None
        self.templates = []   # face indices
        self.targets = []     # face indices
        self.assignment = {}  # face -> template index (ket qua random gan nhat)
        self.neighbors = {}   # face -> [face] (hang xom)

        self._build_ui()
        self._apply_style()

    def _build_ui(self):
        lay = QtWidgets.QVBoxLayout(self)
        lay.setSpacing(8)

        # Map channel
        ch_row = QtWidgets.QHBoxLayout()
        ch_row.addWidget(QtWidgets.QLabel("Map Channel:"))
        self.spin_ch = QtWidgets.QSpinBox()
        self.spin_ch.setRange(1, 99)
        self.spin_ch.setValue(1)
        ch_row.addWidget(self.spin_ch)
        ch_row.addStretch()
        lay.addLayout(ch_row)

        # 1. Templates
        self.btn_tpl = QtWidgets.QPushButton("① Lấy Face Mẫu (từ selection)")
        self.btn_tpl.clicked.connect(self.grab_templates)
        lay.addWidget(self.btn_tpl)
        self.lbl_tpl = QtWidgets.QLabel("Chưa có face mẫu")
        self.lbl_tpl.setObjectName("info")
        lay.addWidget(self.lbl_tpl)

        lay.addWidget(self._sep())

        # 2. Select faces to random
        self.btn_sel = QtWidgets.QPushButton("② Chọn Face để Random")
        self.btn_sel.clicked.connect(self.grab_targets)
        lay.addWidget(self.btn_sel)

        self.btn_invert = QtWidgets.QPushButton("⇄ Invert Selection")
        self.btn_invert.clicked.connect(self.invert_selection)
        lay.addWidget(self.btn_invert)

        self.lbl_sel = QtWidgets.QLabel("Chưa chọn face nào")
        self.lbl_sel.setObjectName("info")
        lay.addWidget(self.lbl_sel)

        lay.addWidget(self._sep())

        # 3. Options tranh trung hang xom
        self.chk_keep = QtWidgets.QCheckBox(
            "Giữ tỉ lệ face B (snap góc trên-trái, không kéo dãn)")
        self.chk_keep.setChecked(True)
        lay.addWidget(self.chk_keep)

        self.chk_avoid = QtWidgets.QCheckBox("Tránh trùng mẫu với hàng xóm")
        self.chk_avoid.setChecked(True)
        lay.addWidget(self.chk_avoid)

        r_row = QtWidgets.QHBoxLayout()
        r_row.addWidget(QtWidgets.QLabel("Khoảng cách kề nhau (×spacing):"))
        self.spin_radius = QtWidgets.QDoubleSpinBox()
        self.spin_radius.setRange(1.0, 5.0)
        self.spin_radius.setSingleStep(0.1)
        self.spin_radius.setValue(1.6)
        r_row.addWidget(self.spin_radius)
        r_row.addStretch()
        lay.addLayout(r_row)

        # 4. Random
        self.btn_run = QtWidgets.QPushButton("③ Random Selected")
        self.btn_run.setObjectName("run")
        self.btn_run.clicked.connect(self.run_random)
        lay.addWidget(self.btn_run)

        # 5. Detect
        self.btn_detect = QtWidgets.QPushButton("④ Detect trùng hàng xóm")
        self.btn_detect.clicked.connect(self.detect_conflicts)
        lay.addWidget(self.btn_detect)

        self.lbl_status = QtWidgets.QLabel("Sẵn sàng.")
        self.lbl_status.setObjectName("status")
        self.lbl_status.setWordWrap(True)
        lay.addWidget(self.lbl_status)

        # ================= RANDOM SELECT (doc lap) =================
        sep2 = self._sep()
        lay.addWidget(sep2)

        lbl_rs = QtWidgets.QLabel("● Random Select (độc lập)")
        lbl_rs.setObjectName("info")
        lay.addWidget(lbl_rs)

        p_row = QtWidgets.QHBoxLayout()
        p_row.addWidget(QtWidgets.QLabel("Tỉ lệ %:"))
        self.spin_pct = QtWidgets.QSpinBox()
        self.spin_pct.setRange(1, 100)
        self.spin_pct.setValue(50)
        p_row.addWidget(self.spin_pct)
        for p in (25, 50, 70):
            b = QtWidgets.QPushButton("%d%%" % p)
            b.setFixedWidth(42)
            b.clicked.connect(lambda _=False, v=p: self.random_select(v))
            p_row.addWidget(b)
        p_row.addStretch()
        lay.addLayout(p_row)

        self.btn_rs = QtWidgets.QPushButton("🎲 Random Select theo %")
        self.btn_rs.clicked.connect(lambda: self.random_select())
        lay.addWidget(self.btn_rs)

        self.lbl_rs = QtWidgets.QLabel("")
        self.lbl_rs.setObjectName("status")
        self.lbl_rs.setWordWrap(True)
        lay.addWidget(self.lbl_rs)

    def _sep(self):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setObjectName("sep")
        return line

    def _apply_style(self):
        self.setStyleSheet("""
            QDialog { background:#2b2b2b; color:#dcdcdc; font-size:12px; }
            QLabel  { color:#dcdcdc; }
            QLabel#info   { color:#8ab4f8; }
            QLabel#status { color:#a0d468; padding-top:4px; }
            QFrame#sep { color:#3c3c3c; }
            QSpinBox { background:#3c3c3c; color:#eee; border:1px solid #555; }
            QPushButton {
                background:#3c3c3c; color:#eee; border:1px solid #555;
                padding:6px; border-radius:3px;
            }
            QPushButton:hover { background:#4a4a4a; }
            QPushButton#run {
                background:#3a5a3a; border:1px solid #4a7a4a; font-weight:bold;
            }
            QPushButton#run:hover { background:#456945; }
        """)

    # ----------------------------- logic ---------------------------------
    def _current_poly(self):
        if rt.selection.count != 1:
            return None
        obj = rt.selection[0]
        return obj if _is_editable_poly(obj) else None

    def grab_templates(self):
        obj = self._current_poly()
        if obj is None:
            self._err("Hãy chọn đúng 1 object Editable Poly.")
            return
        if _has_unwrap(obj):
            self._err("Object còn Unwrap UVW đang bật.\nCollapse về Editable Poly rồi thử lại.")
            return
        faces = _get_face_selection(obj)
        if not faces:
            self._err("Chưa chọn face nào (vào chế độ Face rồi chọn face mẫu).")
            return
        self.node = obj
        self.templates = faces
        if len(faces) > 20:
            self.lbl_tpl.setStyleSheet("color:#e0a030;")
            self.lbl_tpl.setText("Đã lưu %d face mẫu (?) — mẫu thường chỉ ~4.\n"
                                 "Hãy chỉ chọn 4 tấm có UV rồi bấm ① lại." % len(faces))
        else:
            self.lbl_tpl.setStyleSheet("color:#8ab4f8;")
            self.lbl_tpl.setText("Đã lưu %d face mẫu." % len(faces))
        self.lbl_status.setStyleSheet("color:#a0d468; padding-top:4px;")
        self.lbl_status.setText("Sẵn sàng.")

    def grab_targets(self):
        obj = self._current_poly()
        if obj is None:
            self._err("Hãy chọn đúng 1 object Editable Poly.")
            return
        if self.node is not None and obj != self.node:
            self._err("Face mẫu thuộc object khác. Chọn cùng object.")
            return
        faces = _get_face_selection(obj)
        if not faces:
            self._err("Chưa chọn face nào để random.")
            return
        # KHONG tru face mau o day nua -> hien dung so face dang chon.
        # Luc Random se tu dong bo qua face mau.
        self.node = obj
        self.targets = faces
        self.lbl_sel.setStyleSheet("color:#8ab4f8;")
        self.lbl_sel.setText("OK đã chọn %d face to random." % len(faces))
        self.lbl_status.setStyleSheet("color:#a0d468; padding-top:4px;")
        self.lbl_status.setText("Sẵn sàng.")

    def invert_selection(self):
        obj = self._current_poly()
        if obj is None:
            self._err("Hãy chọn đúng 1 object Editable Poly.")
            return
        sel = set(_get_face_selection(obj))
        n = rt.polyop.getNumFaces(obj)
        inv = [i for i in range(1, n + 1) if i not in sel]
        rt.polyop.setFaceSelection(obj, rt.Array(*inv))
        try:
            rt.subObjectLevel = 4  # Face
        except Exception:
            pass
        rt.redrawViews()
        self.lbl_status.setStyleSheet("color:#a0d468; padding-top:4px;")
        self.lbl_status.setText("Đã đảo selection: %d face đang chọn." % len(inv))

    def random_select(self, pct=None):
        """Doc lap: chon ngau nhien pct% face tren TONG so face cua object."""
        obj = self._current_poly()
        if obj is None:
            self.lbl_rs.setStyleSheet("color:#e57373;")
            self.lbl_rs.setText("Hãy chọn đúng 1 object Editable Poly.")
            return
        if pct is None:
            pct = self.spin_pct.value()
        n = rt.polyop.getNumFaces(obj)
        count = int(round(n * pct / 100.0))
        count = max(0, min(n, count))
        faces = random.sample(range(1, n + 1), count) if count else []
        rt.polyop.setFaceSelection(obj, rt.Array(*faces))
        try:
            rt.subObjectLevel = 4  # Face
        except Exception:
            pass
        rt.redrawViews()
        self.lbl_rs.setStyleSheet("color:#a0d468;")
        self.lbl_rs.setText("Đã random chọn %d / %d face (%d%%)." % (count, n, pct))

    def run_random(self):
        if self.node is None or not self.templates:
            self._err("Chưa có face mẫu (bước ①).")
            return
        if not self.targets:
            self._err("Chưa chọn face để random (bước ②).")
            return
        obj = self.node
        if _has_unwrap(obj):
            self._err("Object còn Unwrap UVW đang bật. Collapse trước.")
            return

        ch = self.spin_ch.value()

        # doc UV cac template
        tpl_data = []
        for tf in self.templates:
            d = _read_template(obj, ch, tf)
            if d is not None:
                tpl_data.append(d)
        if not tpl_data:
            self._err("Không đọc được UV từ face mẫu (mẫu phải là quad + đã có UV).")
            return

        targets = self.targets
        tpl_set = set(self.templates)
        skipped = 0
        overwritten_tpl = 0

        # loc target: bo face mau, bo face khong phai quad
        valid = []
        for f in targets:
            if f in tpl_set:
                overwritten_tpl += 1
                continue
            gv, _ = _face_roles(obj, f)
            if gv is None:                    # khong phai quad
                skipped += 1
                continue
            valid.append(f)

        if not valid:
            self._err("Không có face quad hợp lệ để random.")
            return

        # --- chon mau cho tung face ---
        rng = random.Random()
        n_tpl = len(tpl_data)
        self.neighbors = {}
        if self.chk_avoid.isChecked() and n_tpl >= 2:
            self.neighbors = _build_neighbors(
                obj, valid, reach_factor=self.spin_radius.value())
            assign = _greedy_color(valid, self.neighbors, n_tpl, rng)
        else:
            assign = {f: rng.randrange(n_tpl) for f in valid}

        self.assignment = dict(assign)

        keep_ratio = self.chk_keep.isChecked()

        # --- ghi UV ---
        with pymxs.undo(True, "BENCGN Random Curtain UV"):
            if not rt.polyop.getMapSupport(obj, ch):
                rt.polyop.setMapSupport(obj, ch, True)

            n_old = rt.polyop.getNumMapVerts(obj, ch)
            rt.polyop.setNumMapVerts(obj, ch, n_old + 4 * len(valid), keep=True)

            for j, f in enumerate(valid):
                gv, roles = _face_roles(obj, f)
                tpl = tpl_data[assign[f]]
                base = n_old + 4 * j

                if keep_ratio:
                    # GIU ti le B, tinh TRONG UV (khong dinh normal):
                    #  - neo goc tren-trai (minU, maxV) cua B vao TL cua mau
                    #  - scale DEU (uniform) sao cho chieu cao B = chieu cao mau
                    #  - chieu ngang tu co theo ti le -> khong keo lech
                    mf = rt.polyop.getMapFace(obj, ch, f)
                    exist = [rt.polyop.getMapVert(obj, ch, mf[k]) for k in range(4)]
                    bu = [float(e.x) for e in exist]
                    bv = [float(e.y) for e in exist]
                    b_umin, b_vmax = min(bu), max(bv)
                    b_vext = max(bv) - min(bv)

                    tus = [tpl[r][0] for r in ('TL', 'TR', 'BL', 'BR')]
                    tvs = [tpl[r][1] for r in ('TL', 'TR', 'BL', 'BR')]
                    t_umin, t_vmax = min(tus), max(tvs)
                    t_vext = max(tvs) - min(tvs)

                    s = (t_vext / b_vext) if abs(b_vext) > 1e-9 else 1.0

                    idx = []
                    for k in range(4):
                        e = exist[k]
                        nu = t_umin + (float(e.x) - b_umin) * s
                        nv = t_vmax + (float(e.y) - b_vmax) * s
                        mvi = base + 1 + k
                        rt.polyop.setMapVert(obj, ch, mvi,
                                             rt.Point3(nu, nv, float(e.z)))
                        idx.append(mvi)
                else:
                    # KEO DAN theo khung mau (che do cu)
                    idx = []
                    for k in range(4):
                        role = next(r for r, ck in roles.items() if ck == k)
                        u, v, w = tpl[role]
                        mvi = base + 1 + k
                        rt.polyop.setMapVert(obj, ch, mvi, rt.Point3(u, v, w))
                        idx.append(mvi)

                rt.polyop.setMapFace(obj, ch, f,
                                     rt.Array(idx[0], idx[1], idx[2], idx[3]))

        rt.redrawViews()
        msg = "Đã random %d face ✓" % len(valid)
        if self.chk_avoid.isChecked() and n_tpl >= 2:
            bad = self._count_conflicts()
            msg += "  | trùng hàng xóm: %d face" % bad
        if skipped:
            msg += "  (bỏ %d không-quad)" % skipped
        if overwritten_tpl:
            msg += "  (chừa %d mẫu)" % overwritten_tpl
        self.lbl_status.setStyleSheet("color:#a0d468; padding-top:4px;")
        self.lbl_status.setText(msg)

    def _count_conflicts(self):
        bad = set()
        for f, t in self.assignment.items():
            for g in self.neighbors.get(f, []):
                if self.assignment.get(g) == t:
                    bad.add(f)
                    bad.add(g)
        return len(bad)

    def detect_conflicts(self):
        """Chon len viewport cac face co mau trung voi hang xom."""
        if self.node is None or not self.assignment:
            self._err("Chưa random lần nào (bước ③).")
            return
        obj = self.node
        if not self.neighbors:
            self._err("Lần random gần nhất không bật 'tránh trùng' nên không có dữ liệu hàng xóm.")
            return
        bad = set()
        for f, t in self.assignment.items():
            for g in self.neighbors.get(f, []):
                if self.assignment.get(g) == t:
                    bad.add(f)
                    bad.add(g)
        if not bad:
            self.lbl_status.setStyleSheet("color:#a0d468; padding-top:4px;")
            self.lbl_status.setText("Không có face nào trùng mẫu với hàng xóm ✓")
            rt.polyop.setFaceSelection(obj, rt.Array())
            rt.redrawViews()
            return
        rt.polyop.setFaceSelection(obj, rt.Array(*sorted(bad)))
        try:
            rt.subObjectLevel = 4  # Face
        except Exception:
            pass
        rt.redrawViews()
        self.lbl_status.setStyleSheet("color:#e0a030; padding-top:4px;")
        self.lbl_status.setText("Đã chọn %d face còn trùng mẫu với hàng xóm." % len(bad))

    def _err(self, text):
        self.lbl_status.setStyleSheet("color:#e57373; padding-top:4px;")
        self.lbl_status.setText(text)


# --------------------------------- launch ---------------------------------
def show():
    global _bencgn_random_uv_win
    try:
        _bencgn_random_uv_win.close()
    except Exception:
        pass
    _bencgn_random_uv_win = RandomCurtainUV()
    _bencgn_random_uv_win.show()
    return _bencgn_random_uv_win


if __name__ == "__main__":
    show()
