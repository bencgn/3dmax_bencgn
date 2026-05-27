"""
3ds Max Python tool: randomly layout selected objects on spline knots.

Run this file from 3ds Max with:
    Scripting > Run Script...

Workflow:
    1. Select 2 or more source objects, then click "Select Objects To Layout".
    2. Select one spline/shape, then click "Select Spline".
    3. Click "Layout Random In Knots".
    4. Use "Random Scale" and "Random Rotate" on the generated layout.
"""

from __future__ import annotations

import random

import pymxs
from pymxs import runtime as rt

try:
    from PySide6 import QtCore, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtWidgets

try:
    import qtmax
except ImportError:
    qtmax = None


TOOL_TITLE = "Spline Knots Random Layout"


def _max_main_window():
    if qtmax is None:
        return None
    try:
        return qtmax.GetQMaxMainWindow()
    except Exception:
        return None


def _install_maxscript_helpers():
    rt.execute(
        r"""
        global sk2o_getSplineKnotsWorld
        global sk2o_resetAndRotate
        global sk2o_combineNodesToPoly
        global sk2o_deleteValidNodes
        global sk2o_layoutCloneOnKnots
        global sk2o_layoutMoveOnKnots
        global sk2o_randomScaleNodes
        global sk2o_randomRotateNodes

        fn sk2o_getSplineKnotsWorld shp =
        (
            local pts = #()
            if isValidNode shp do
            (
                try
                (
                    try(updateShape shp)catch()
                    try(update shp)catch()
                    for splIndex = 1 to (numSplines shp) do
                    (
                        for knotIndex = 1 to (numKnots shp splIndex) do
                        (
                            append pts (in coordsys world getKnotPoint shp splIndex knotIndex)
                        )
                    )
                )
                catch
                (
                    pts = #()
                )
            )
            pts
        )

        fn sk2o_resetAndRotate node baseRot rotX rotY rotZ useX useY useZ =
        (
            if isValidNode node do
            (
                try
                (
                    node.rotation = baseRot
                    if useX do rotate node (angleaxis rotX [1, 0, 0])
                    if useY do rotate node (angleaxis rotY [0, 1, 0])
                    if useZ do rotate node (angleaxis rotZ [0, 0, 1])
                )
                catch()
            )
        )

        fn sk2o_deleteValidNodes nodes =
        (
            local deleteNodes = #()
            for node in nodes where isValidNode node do append deleteNodes node
            local deleteCount = deleteNodes.count
            if deleteCount > 0 do delete deleteNodes
            deleteCount
        )

        fn sk2o_layoutCloneOnKnots sourceNodes knots useInstance =
        (
            local validSources = #()
            local resultNodes = #()
            for node in sourceNodes where isValidNode node do append validSources node

            if validSources.count > 0 and knots.count > 0 do
            (
                disableSceneRedraw()
                try
                (
                    for point in knots do
                    (
                        local sourceNode = validSources[random 1 validSources.count]
                        local newNode = if useInstance then instance sourceNode else copy sourceNode
                        if isValidNode newNode do
                        (
                            try(newNode.name = uniqueName ((sourceNode.name as string) + "_knot_"))catch()
                            newNode.position = point
                            append resultNodes newNode
                        )
                    )
                )
                catch()
                enableSceneRedraw()
            )
            resultNodes
        )

        fn sk2o_layoutMoveOnKnots sourceNodes knots =
        (
            local shuffledNodes = #()
            local resultNodes = #()
            for node in sourceNodes where isValidNode node do append shuffledNodes node

            for i = shuffledNodes.count to 2 by -1 do
            (
                local swapIndex = random 1 i
                local oldNode = shuffledNodes[i]
                shuffledNodes[i] = shuffledNodes[swapIndex]
                shuffledNodes[swapIndex] = oldNode
            )

            local total = if shuffledNodes.count < knots.count then shuffledNodes.count else knots.count
            if total > 0 do
            (
                disableSceneRedraw()
                try
                (
                    for i = 1 to total do
                    (
                        if isValidNode shuffledNodes[i] do
                        (
                            shuffledNodes[i].position = knots[i]
                            append resultNodes shuffledNodes[i]
                        )
                    )
                )
                catch()
                enableSceneRedraw()
            )
            resultNodes
        )

        fn sk2o_randomScaleNodes nodes baseScales minScale maxScale =
        (
            local changedCount = 0
            local total = if nodes.count < baseScales.count then nodes.count else baseScales.count
            if total > 0 do
            (
                disableSceneRedraw()
                try
                (
                    for i = 1 to total do
                    (
                        if isValidNode nodes[i] do
                        (
                            local baseScale = baseScales[i]
                            local factor = random minScale maxScale
                            nodes[i].scale = [baseScale.x * factor, baseScale.y * factor, baseScale.z * factor]
                            changedCount += 1
                        )
                    )
                )
                catch()
                enableSceneRedraw()
            )
            changedCount
        )

        fn sk2o_randomRotateNodes nodes baseRotations minRotate maxRotate useX useY useZ =
        (
            local changedCount = 0
            local total = if nodes.count < baseRotations.count then nodes.count else baseRotations.count
            if total > 0 do
            (
                disableSceneRedraw()
                try
                (
                    for i = 1 to total do
                    (
                        if isValidNode nodes[i] do
                        (
                            nodes[i].rotation = baseRotations[i]
                            if useX do rotate nodes[i] (angleaxis (random minRotate maxRotate) [1, 0, 0])
                            if useY do rotate nodes[i] (angleaxis (random minRotate maxRotate) [0, 1, 0])
                            if useZ do rotate nodes[i] (angleaxis (random minRotate maxRotate) [0, 0, 1])
                            changedCount += 1
                        )
                    )
                )
                catch()
                enableSceneRedraw()
            )
            changedCount
        )

        fn sk2o_combineNodesToPoly nodes combinedName =
        (
            local sourceNodes = #()
            for node in nodes where isValidNode node do append sourceNodes node
            if sourceNodes.count < 1 then
            (
                undefined
            )
            else
            (
                local baseNode = undefined
                local resultNode = undefined
                disableSceneRedraw()
                try
                (
                    baseNode = sourceNodes[1]
                    baseNode.name = uniqueName combinedName
                    convertToPoly baseNode

                    for nodeIndex = 2 to sourceNodes.count do
                    (
                        local sourceNode = sourceNodes[nodeIndex]
                        try
                        (
                            if isValidNode sourceNode do
                            (
                                convertToPoly sourceNode
                                polyop.attach baseNode sourceNode
                            )
                        )
                        catch
                        (
                            format "Spline Knots combine skipped node: %\n" sourceNode
                        )
                    )

                    baseNode.pivot = [0, 0, 0]
                    resultNode = baseNode
                )
                catch
                (
                    resultNode = undefined
                )
                enableSceneRedraw()
                resultNode
            )
        )
        """
    )


def _valid_node(node):
    try:
        return bool(rt.isValidNode(node))
    except Exception:
        return False


def _node_name(node):
    try:
        return str(node.name)
    except Exception:
        return "<deleted>"


def _selection_nodes():
    return [node for node in rt.selection if _valid_node(node)]


def _copy_point3(value):
    return rt.Point3(value.x, value.y, value.z)


def _node_handle(node):
    try:
        return int(rt.getHandleByAnim(node))
    except Exception:
        return id(node)


def _select_nodes(nodes):
    valid_nodes = [node for node in nodes if _valid_node(node)]
    try:
        rt.select(valid_nodes)
        return
    except Exception:
        rt.clearSelection()
        for node in valid_nodes:
            rt.selectMore(node)


class SplineKnotsRandomLayout(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SplineKnotsRandomLayout, self).__init__(parent)
        self.setWindowTitle(TOOL_TITLE)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)
        self.resize(420, 520)

        self.source_nodes = []
        self.spline_node = None
        self.generated_nodes = []
        self.generated_are_clones = False
        self.base_scales = {}
        self.base_rotations = {}
        self.source_start_transforms = {}
        self.is_busy = False

        self._build_ui()
        self._connect_signals()
        self._set_state("Pending", 0)
        self._refresh_ui()

    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        source_group = QtWidgets.QGroupBox("1. Source Objects")
        source_layout = QtWidgets.QVBoxLayout(source_group)
        self.pick_sources_btn = QtWidgets.QPushButton("Select Objects To Layout")
        self.source_label = QtWidgets.QLabel("No source objects stored")
        self.source_label.setWordWrap(True)
        source_layout.addWidget(self.pick_sources_btn)
        source_layout.addWidget(self.source_label)

        spline_group = QtWidgets.QGroupBox("2. Target Spline")
        spline_layout = QtWidgets.QVBoxLayout(spline_group)
        self.pick_spline_btn = QtWidgets.QPushButton("Select Spline")
        self.spline_label = QtWidgets.QLabel("No spline stored")
        self.spline_label.setWordWrap(True)
        spline_layout.addWidget(self.pick_spline_btn)
        spline_layout.addWidget(self.spline_label)

        layout_group = QtWidgets.QGroupBox("3. Layout")
        layout_form = QtWidgets.QFormLayout(layout_group)
        self.layout_mode_combo = QtWidgets.QComboBox()
        self.layout_mode_combo.addItems(
            [
                "Clone random source on every knot",
                "Move selected objects to random knots",
            ]
        )
        self.clone_type_combo = QtWidgets.QComboBox()
        self.clone_type_combo.addItems(["Copy", "Instance"])
        self.replace_previous_check = QtWidgets.QCheckBox("Replace previous generated clones")
        self.replace_previous_check.setChecked(True)
        self.refresh_spline_check = QtWidgets.QCheckBox("Refresh spline knots before layout")
        self.refresh_spline_check.setChecked(True)
        self.use_selected_spline_check = QtWidgets.QCheckBox("Use selected spline if changed")
        self.use_selected_spline_check.setChecked(True)
        self.layout_btn = QtWidgets.QPushButton("Layout Random In Knots")
        self.reset_layout_btn = QtWidgets.QPushButton("Reset Layout")
        layout_form.addRow("Mode", self.layout_mode_combo)
        layout_form.addRow("Clone type", self.clone_type_combo)
        layout_form.addRow("", self.replace_previous_check)
        layout_form.addRow("", self.refresh_spline_check)
        layout_form.addRow("", self.use_selected_spline_check)
        layout_form.addRow("", self.layout_btn)
        layout_form.addRow("", self.reset_layout_btn)

        self.random_group = QtWidgets.QGroupBox("4. Randomize Layout Result")
        random_layout = QtWidgets.QVBoxLayout(self.random_group)

        scale_row = QtWidgets.QHBoxLayout()
        self.scale_min_spin = QtWidgets.QDoubleSpinBox()
        self.scale_min_spin.setRange(1.0, 10000.0)
        self.scale_min_spin.setValue(80.0)
        self.scale_min_spin.setSuffix("%")
        self.scale_max_spin = QtWidgets.QDoubleSpinBox()
        self.scale_max_spin.setRange(1.0, 10000.0)
        self.scale_max_spin.setValue(120.0)
        self.scale_max_spin.setSuffix("%")
        self.random_scale_btn = QtWidgets.QPushButton("Random Scale")
        scale_row.addWidget(QtWidgets.QLabel("Scale"))
        scale_row.addWidget(self.scale_min_spin)
        scale_row.addWidget(self.scale_max_spin)
        scale_row.addWidget(self.random_scale_btn)

        rotate_range_row = QtWidgets.QHBoxLayout()
        self.rotate_min_spin = QtWidgets.QDoubleSpinBox()
        self.rotate_min_spin.setRange(-3600.0, 3600.0)
        self.rotate_min_spin.setValue(0.0)
        self.rotate_min_spin.setSuffix(" deg")
        self.rotate_max_spin = QtWidgets.QDoubleSpinBox()
        self.rotate_max_spin.setRange(-3600.0, 3600.0)
        self.rotate_max_spin.setValue(360.0)
        self.rotate_max_spin.setSuffix(" deg")
        rotate_range_row.addWidget(QtWidgets.QLabel("Rotate"))
        rotate_range_row.addWidget(self.rotate_min_spin)
        rotate_range_row.addWidget(self.rotate_max_spin)

        rotate_axis_row = QtWidgets.QHBoxLayout()
        self.rotate_x_check = QtWidgets.QCheckBox("X")
        self.rotate_y_check = QtWidgets.QCheckBox("Y")
        self.rotate_z_check = QtWidgets.QCheckBox("Z")
        self.rotate_z_check.setChecked(True)
        self.random_rotate_btn = QtWidgets.QPushButton("Random Rotate")
        rotate_axis_row.addWidget(QtWidgets.QLabel("Axis"))
        rotate_axis_row.addWidget(self.rotate_x_check)
        rotate_axis_row.addWidget(self.rotate_y_check)
        rotate_axis_row.addWidget(self.rotate_z_check)
        rotate_axis_row.addStretch()
        rotate_axis_row.addWidget(self.random_rotate_btn)

        result_row = QtWidgets.QHBoxLayout()
        self.select_result_btn = QtWidgets.QPushButton("Select Result")
        self.combine_pivot_btn = QtWidgets.QPushButton("Combine Result + Pivot XYZ 0,0,0")
        self.result_label = QtWidgets.QLabel("No layout result yet")
        self.result_label.setWordWrap(True)
        result_row.addWidget(self.select_result_btn)
        result_row.addWidget(self.combine_pivot_btn)
        result_row.addWidget(self.result_label, 1)

        random_layout.addLayout(scale_row)
        random_layout.addLayout(rotate_range_row)
        random_layout.addLayout(rotate_axis_row)
        random_layout.addLayout(result_row)

        status_group = QtWidgets.QGroupBox("Status")
        status_layout = QtWidgets.QVBoxLayout(status_group)
        self.state_label = QtWidgets.QLabel("State: Pending")
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.state_label)
        status_layout.addWidget(self.progress_bar)
        status_layout.addWidget(self.status_label)

        main_layout.addWidget(source_group)
        main_layout.addWidget(spline_group)
        main_layout.addWidget(layout_group)
        main_layout.addWidget(self.random_group)
        main_layout.addWidget(status_group)
        main_layout.addStretch()

    def _connect_signals(self):
        self.pick_sources_btn.clicked.connect(self.pick_sources)
        self.pick_spline_btn.clicked.connect(self.pick_spline)
        self.layout_btn.clicked.connect(self.layout_random_in_knots)
        self.reset_layout_btn.clicked.connect(self.reset_layout)
        self.random_scale_btn.clicked.connect(self.random_scale)
        self.random_rotate_btn.clicked.connect(self.random_rotate)
        self.select_result_btn.clicked.connect(self.select_result)
        self.combine_pivot_btn.clicked.connect(self.combine_result_pivot_zero)
        self.layout_mode_combo.currentIndexChanged.connect(self._refresh_ui)

    def _set_state(self, state, progress=None, detail=None):
        self.state_label.setText("State: {0}".format(state))
        if progress is not None:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(max(0, min(100, int(progress))))
        if detail is not None:
            self.status_label.setText(detail)
        QtWidgets.QApplication.processEvents()

    def _set_progress_count(self, current, total, state=None):
        if total <= 0:
            self._set_state(state or "Working", 0)
            return
        update_every = max(1, int(total / 40))
        if current < total and current % update_every != 0:
            return
        progress = int((float(current) / float(total)) * 100.0)
        self._set_state(state or "Working", progress)

    def _set_busy(self, busy):
        self.is_busy = busy
        for widget in (
            self.pick_sources_btn,
            self.pick_spline_btn,
            self.layout_btn,
            self.reset_layout_btn,
            self.random_scale_btn,
            self.random_rotate_btn,
            self.select_result_btn,
            self.combine_pivot_btn,
            self.layout_mode_combo,
            self.clone_type_combo,
            self.replace_previous_check,
            self.refresh_spline_check,
            self.use_selected_spline_check,
        ):
            widget.setEnabled(not busy)
        QtWidgets.QApplication.processEvents()

    def _refresh_ui(self):
        self.source_nodes = [node for node in self.source_nodes if _valid_node(node)]
        self.generated_nodes = [node for node in self.generated_nodes if _valid_node(node)]

        if self.source_nodes:
            names = ", ".join(_node_name(node) for node in self.source_nodes[:5])
            if len(self.source_nodes) > 5:
                names += ", ..."
            self.source_label.setText(
                "{0} source object(s): {1}".format(len(self.source_nodes), names)
            )
        else:
            self.source_label.setText("No source objects stored")

        if _valid_node(self.spline_node):
            knot_count = len(self._spline_knots_world(self.spline_node))
            self.spline_label.setText(
                "{0} ({1} knot(s))".format(_node_name(self.spline_node), knot_count)
            )
        else:
            self.spline_node = None
            self.spline_label.setText("No spline stored")

        clone_mode = self.layout_mode_combo.currentIndex() == 0
        self.clone_type_combo.setEnabled(clone_mode and not self.is_busy)
        self.replace_previous_check.setEnabled(clone_mode and not self.is_busy)

        has_result = len(self.generated_nodes) > 0
        self.random_group.setEnabled(has_result and not self.is_busy)
        self.result_label.setText(
            "{0} object(s) in result".format(len(self.generated_nodes))
            if has_result
            else "No layout result yet"
        )

    def _message(self, text, title=TOOL_TITLE):
        QtWidgets.QMessageBox.information(self, title, text)
        self.status_label.setText(text)

    def _spline_knots_world(self, spline_node):
        if not _valid_node(spline_node):
            return []
        try:
            if self.refresh_spline_check.isChecked():
                try:
                    rt.completeRedraw()
                except Exception:
                    pass
            return list(rt.sk2o_getSplineKnotsWorld(spline_node))
        except Exception:
            return []

    def _snapshot_node_transform(self, node):
        try:
            return (_copy_point3(node.position), node.rotation, _copy_point3(node.scale))
        except Exception:
            return None

    def _restore_node_transform(self, node, transform_data):
        if not _valid_node(node) or transform_data is None:
            return False
        position, rotation, scale = transform_data
        try:
            node.position = position
            node.rotation = rotation
            node.scale = scale
            return True
        except Exception:
            return False

    def _store_source_start_transforms(self):
        self.source_start_transforms = {}
        for node in self.source_nodes:
            if not _valid_node(node):
                continue
            transform_data = self._snapshot_node_transform(node)
            if transform_data is not None:
                self.source_start_transforms[_node_handle(node)] = transform_data

    def _maybe_use_selected_spline(self):
        if not self.use_selected_spline_check.isChecked():
            return
        nodes = _selection_nodes()
        if len(nodes) != 1:
            return
        selected_node = nodes[0]
        if selected_node == self.spline_node:
            return
        if selected_node in self.source_nodes or selected_node in self.generated_nodes:
            return
        knots = self._spline_knots_world(selected_node)
        if knots:
            self.spline_node = selected_node
            self.status_label.setText(
                "Using selected spline {0} with {1} knot(s).".format(
                    _node_name(selected_node), len(knots)
                )
            )

    def pick_sources(self):
        nodes = _selection_nodes()
        if len(nodes) < 2:
            self._message("Select 2 or more source objects first.")
            return
        self.source_nodes = nodes
        self._store_source_start_transforms()
        self.status_label.setText("Stored {0} source object(s).".format(len(nodes)))
        self._set_state("Pending", 0)
        self._refresh_ui()

    def pick_spline(self):
        nodes = _selection_nodes()
        if len(nodes) != 1:
            self._message("Select exactly one spline or shape first.")
            return

        knots = self._spline_knots_world(nodes[0])
        if not knots:
            self._message("The selected object has no readable spline knots.")
            return

        self.spline_node = nodes[0]
        self.status_label.setText(
            "Stored spline {0} with {1} knot(s).".format(_node_name(nodes[0]), len(knots))
        )
        self._set_state("Pending", 0)
        self._refresh_ui()

    def _delete_previous_clones_if_needed(self):
        if not (
            self.generated_are_clones
            and self.generated_nodes
            and self.replace_previous_check.isChecked()
        ):
            return

        for node in list(self.generated_nodes):
            if _valid_node(node):
                try:
                    rt.delete(node)
                except Exception:
                    pass
        self.generated_nodes = []
        self.generated_are_clones = False

    def _clear_layout_result(self, delete_generated=True, restore_moved=True):
        deleted_count = 0
        restored_count = 0

        if self.generated_are_clones and delete_generated:
            try:
                deleted_count = int(rt.sk2o_deleteValidNodes(self.generated_nodes))
            except Exception:
                for node in list(self.generated_nodes):
                    if _valid_node(node):
                        try:
                            rt.delete(node)
                            deleted_count += 1
                        except Exception:
                            pass
        elif restore_moved:
            for node in list(self.generated_nodes):
                transform_data = self.source_start_transforms.get(_node_handle(node))
                if self._restore_node_transform(node, transform_data):
                    restored_count += 1

        self.generated_nodes = []
        self.generated_are_clones = False
        self.base_scales = {}
        self.base_rotations = {}
        return deleted_count, restored_count

    def reset_layout(self):
        self._set_busy(True)
        self._set_state("Resetting", 0, "Resetting previous layout result...")
        try:
            with pymxs.undo(True, "Reset Spline Knots Layout"):
                deleted_count, restored_count = self._clear_layout_result(
                    delete_generated=True, restore_moved=True
                )
                rt.redrawViews()
            self._set_state(
                "Pending",
                0,
                "Reset done. Deleted {0} generated object(s), restored {1} moved object(s).".format(
                    deleted_count, restored_count
                ),
            )
        finally:
            self._set_busy(False)
            self._refresh_ui()

    def _clone_node(self, source_node):
        clone_type = self.clone_type_combo.currentText()
        try:
            if clone_type == "Instance":
                return rt.instance(source_node)
            return rt.copy(source_node)
        except Exception:
            try:
                return rt.copy(source_node)
            except Exception:
                return None

    def _store_base_transforms(self):
        self.base_scales = {}
        self.base_rotations = {}
        for node in self.generated_nodes:
            if not _valid_node(node):
                continue
            handle = _node_handle(node)
            try:
                self.base_scales[handle] = _copy_point3(node.scale)
                self.base_rotations[handle] = node.rotation
            except Exception:
                pass

    def layout_random_in_knots(self):
        self._set_busy(True)
        self._set_state("Pending", 0, "Preparing layout...")
        self.source_nodes = [node for node in self.source_nodes if _valid_node(node)]
        if not self.source_start_transforms:
            self._store_source_start_transforms()

        try:
            if len(self.source_nodes) < 2:
                self._message("Store 2 or more source objects first.")
                return

            self._maybe_use_selected_spline()
            self._set_state("Reading Spline", 5, "Refreshing spline knots from scene...")
            knots = self._spline_knots_world(self.spline_node)
            if not knots:
                self._message("Store a spline with at least one knot first.")
                return

            clone_mode = self.layout_mode_combo.currentIndex() == 0
            random.shuffle(knots)

            with pymxs.undo(True, TOOL_TITLE):
                if self.generated_nodes:
                    self._set_state("Resetting", 10, "Resetting previous layout before next layout...")
                    if self.generated_are_clones and self.replace_previous_check.isChecked():
                        self._clear_layout_result(delete_generated=True, restore_moved=False)
                    elif not self.generated_are_clones:
                        self._clear_layout_result(delete_generated=False, restore_moved=True)

                result_nodes = []

                if clone_mode:
                    use_instance = self.clone_type_combo.currentText() == "Instance"
                    self._set_state(
                        "Layouting",
                        25,
                        "Fast layout: cloning inside 3ds Max with redraw off...",
                    )
                    result_nodes = list(
                        rt.sk2o_layoutCloneOnKnots(self.source_nodes, knots, use_instance)
                    )
                    self._set_state("Layouting", 90, "Clone layout finished.")
                    self.generated_are_clones = True
                else:
                    self._set_state(
                        "Layouting",
                        25,
                        "Fast layout: moving source objects inside 3ds Max with redraw off...",
                    )
                    result_nodes = list(rt.sk2o_layoutMoveOnKnots(self.source_nodes, knots))
                    self._set_state("Layouting", 90, "Move layout finished.")
                    self.generated_are_clones = False

                self._set_state("Finishing", 95, "Saving result transforms...")
                self.generated_nodes = result_nodes
                self._store_base_transforms()
                _select_nodes(self.generated_nodes)
                rt.redrawViews()

            self._set_state(
                "Done",
                100,
                "Layout complete: {0} object(s) placed on {1} spline knot(s).".format(
                    len(self.generated_nodes), len(knots)
                ),
            )
        finally:
            self._set_busy(False)
            self._refresh_ui()

    def random_scale(self):
        self._set_state("Scaling", 0, "Applying random scale...")
        self.generated_nodes = [node for node in self.generated_nodes if _valid_node(node)]
        if not self.generated_nodes:
            self._message("Create a layout result first.")
            return

        min_scale = self.scale_min_spin.value() / 100.0
        max_scale = self.scale_max_spin.value() / 100.0
        if min_scale > max_scale:
            min_scale, max_scale = max_scale, min_scale

        target_nodes = []
        base_scales = []
        for node in self.generated_nodes:
            handle = _node_handle(node)
            base_scale = self.base_scales.get(handle)
            if base_scale is None:
                try:
                    base_scale = _copy_point3(node.scale)
                except Exception:
                    continue
                self.base_scales[handle] = base_scale
            target_nodes.append(node)
            base_scales.append(base_scale)

        with pymxs.undo(True, "Random Scale Layout Result"):
            changed_count = int(
                rt.sk2o_randomScaleNodes(
                    target_nodes, base_scales, min_scale, max_scale
                )
            )
            rt.redrawViews()

        self._set_state(
            "Done",
            100,
            "Random scale applied to {0} object(s).".format(changed_count),
        )

    def random_rotate(self):
        self._set_state("Rotating", 0, "Applying random rotation...")
        self.generated_nodes = [node for node in self.generated_nodes if _valid_node(node)]
        if not self.generated_nodes:
            self._message("Create a layout result first.")
            return
        if not (
            self.rotate_x_check.isChecked()
            or self.rotate_y_check.isChecked()
            or self.rotate_z_check.isChecked()
        ):
            self._message("Choose at least one rotation axis.")
            return

        min_rotate = self.rotate_min_spin.value()
        max_rotate = self.rotate_max_spin.value()
        if min_rotate > max_rotate:
            min_rotate, max_rotate = max_rotate, min_rotate

        use_x = self.rotate_x_check.isChecked()
        use_y = self.rotate_y_check.isChecked()
        use_z = self.rotate_z_check.isChecked()

        target_nodes = []
        base_rotations = []
        for node in self.generated_nodes:
            handle = _node_handle(node)
            base_rotation = self.base_rotations.get(handle)
            if base_rotation is None:
                try:
                    base_rotation = node.rotation
                except Exception:
                    continue
                self.base_rotations[handle] = base_rotation
            target_nodes.append(node)
            base_rotations.append(base_rotation)

        with pymxs.undo(True, "Random Rotate Layout Result"):
            changed_count = int(
                rt.sk2o_randomRotateNodes(
                    target_nodes,
                    base_rotations,
                    min_rotate,
                    max_rotate,
                    use_x,
                    use_y,
                    use_z,
                )
            )
            rt.redrawViews()

        self._set_state(
            "Done",
            100,
            "Random rotation applied to {0} object(s).".format(changed_count),
        )

    def select_result(self):
        self.generated_nodes = [node for node in self.generated_nodes if _valid_node(node)]
        if not self.generated_nodes:
            self._message("No layout result to select.")
            return
        _select_nodes(self.generated_nodes)
        self.status_label.setText(
            "Selected {0} result object(s).".format(len(self.generated_nodes))
        )
        self._refresh_ui()

    def combine_result_pivot_zero(self):
        self._set_busy(True)
        self._set_state("Combining", 0, "Combining layout result...")
        self.generated_nodes = [node for node in self.generated_nodes if _valid_node(node)]

        try:
            if not self.generated_nodes:
                self._message("Create a layout result first.")
                return

            with pymxs.undo(True, "Combine Layout Result Pivot Zero"):
                if len(self.generated_nodes) == 1:
                    combined_node = self.generated_nodes[0]
                    try:
                        combined_node.pivot = rt.Point3(0, 0, 0)
                    except Exception:
                        pass
                else:
                    self._set_state(
                        "Combining",
                        50,
                        "Combining {0} object(s) into one Editable Poly...".format(
                            len(self.generated_nodes)
                        ),
                    )
                    combined_node = rt.sk2o_combineNodesToPoly(
                        self.generated_nodes, "SplineKnots_Combined_"
                    )

                if not _valid_node(combined_node):
                    self._message("Could not combine these objects. Try mesh/poly objects.")
                    return

                self.generated_nodes = [combined_node]
                self.generated_are_clones = True
                self._store_base_transforms()
                _select_nodes(self.generated_nodes)
                rt.redrawViews()

            self._set_state(
                "Done",
                100,
                "Combined result is one object. Pivot is at world XYZ 0,0,0.",
            )
        finally:
            self._set_busy(False)
            self._refresh_ui()


def show_dialog():
    _install_maxscript_helpers()

    global _spline_knots_random_layout_dialog
    try:
        _spline_knots_random_layout_dialog.close()
        _spline_knots_random_layout_dialog.deleteLater()
    except Exception:
        pass

    _spline_knots_random_layout_dialog = SplineKnotsRandomLayout(_max_main_window())
    _spline_knots_random_layout_dialog.show()
    return _spline_knots_random_layout_dialog


if __name__ == "__main__":
    show_dialog()
