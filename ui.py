import bpy

from .operators import _is_tracker_running


class HTVA_PT_panel(bpy.types.Panel):
    bl_label = "Head Tracking"
    bl_idname = "HTVA_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Head Tracking"

    def draw(self, context):
        layout = self.layout
        props = context.scene.htva_props

        # ===============================
        # TRACKER CONTROLS
        # ===============================
        box = layout.box()
        box.label(text="Tracker", icon="CAMERA_DATA")

        running = _is_tracker_running()

        col = box.column(align=True)

        row = col.row(align=True)
        row.enabled = not running
        row.operator("htva.launch_tracker", text="Launch (Preview)", icon="PLAY")
        row.operator("htva.launch_tracker_bg", text="Launch (Background)", icon="PLAY")

        row = col.row(align=True)
        row.enabled = running
        row.operator("htva.stop_tracker", text="Stop Tracker", icon="CANCEL")

        status_text = "RUNNING" if running else "STOPPED"
        status_icon = "CHECKMARK" if running else "CANCEL"
        box.label(text=f"Tracker Status: {status_text}", icon=status_icon)

        # ===============================
        # MODE
        # ===============================
        box = layout.box()
        box.label(text="Mode", icon="TOOL_SETTINGS")
        box.prop(props, "mode", text="")

        # ===============================
        # STATUS / PRIMARY CONTROLS
        # ===============================
        box = layout.box()
        box.label(text="Control", icon="CAMERA_DATA")

        row = box.row(align=True)
        icon = "PLAY" if not props.enabled else "PAUSE"
        text = "Start" if not props.enabled else "Stop"
        row.operator("htva.toggle", text=text, icon=icon)

        status = "ON" if props.enabled else "OFF"
        status_icon = "CHECKMARK" if props.enabled else "CANCEL"
        box.label(text=f"Status: {status}", icon=status_icon)

        # ===============================
        # VIEW ASSIST MODE UI
        # ===============================
        if props.mode == 'VIEW_ASSIST':
            box = layout.box()
            box.label(text="Viewport", icon="VIEW3D")
            box.operator("htva.use_this_viewport", icon="RESTRICT_VIEW_OFF")

            box = layout.box()
            box.label(text="Sensitivity", icon="ORIENTATION_VIEW")
            col = box.column(align=True)
            col.prop(props, "yaw_strength_deg", text="Yaw")
            col.prop(props, "pitch_strength_deg", text="Pitch")
            col.prop(props, "zoom_strength", text="Zoom")

            box = layout.box()
            box.label(text="Distance Limits", icon="EMPTY_ARROWS")
            col = box.column(align=True)
            col.prop(props, "max_distance", text="Max")
            col.prop(props, "min_distance", text="Min")

        # ===============================
        # DEPTH VIEW MODE UI
        # ===============================
        elif props.mode == 'WINDOW':
            box = layout.box()
            box.label(text="Depth View Camera", icon="CAMERA_DATA")
            box.prop(props, "window_camera", text="Camera")

            box = layout.box()
            box.label(text="Depth View Controls", icon="VIEW_CAMERA")
            col = box.column(align=True)
            col.prop(props, "window_xy_strength_x", text="Move/Shift X")
            col.prop(props, "window_xy_strength_y", text="Move/Shift Y")
            col.prop(props, "window_z_strength", text="Move Z / FOV Zoom")

            box = layout.box()
            box.label(text="Lens Limits", icon="VIEW_PERSPECTIVE")
            col = box.column(align=True)
            col.prop(props, "window_min_lens", text="Min Lens")
            col.prop(props, "window_max_lens", text="Max Lens")

            box = layout.box()
            box.label(text="Tip", icon="INFO")
            box.label(text="Use camera scale 1, 1, 1.")
            box.label(text="Enter Camera View with NumPad 0.")

        # ===============================
        # SMOOTHING
        # ===============================
        box = layout.box()
        box.label(text="Smoothing", icon="MOD_SMOOTH")

        col = box.column(align=True)
        col.prop(props, "smoothing_alpha", text="Smooth Alpha")
        col.prop(props, "deadzone", text="Deadzone")