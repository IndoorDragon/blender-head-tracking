import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
    EnumProperty,
    PointerProperty,
)


def _camera_object_poll(self, obj):
    return obj is not None and obj.type == 'CAMERA'


class HTVA_Props(bpy.types.PropertyGroup):
    enabled: BoolProperty(name="Enabled", default=False)

    udp_port: IntProperty(
        name="UDP Port",
        default=5005,
        min=1024,
        max=65535
    )

    target_area_ptr: StringProperty(
        name="Target Viewport",
        default="0",
        description="Internal pointer identifying which 3D View this add-on controls"
    )

    mode: EnumProperty(
        name="Mode",
        items=[
            ('VIEW_ASSIST', "Viewport Control", "Head-tracked viewport orbit/zoom"),
            ('WINDOW', "Depth View (Experimental)", "Head-tracked camera depth view"),
        ],
        default='VIEW_ASSIST'
    )

    # -----------------------------
    # View Assist mode (Viewport Control)
    # -----------------------------
    yaw_strength_deg: FloatProperty(
        name="Yaw Strength (deg)",
        default=25.0,
        min=0.0,
        max=100.0
    )

    pitch_strength_deg: FloatProperty(
        name="Pitch Strength (deg)",
        default=25.0,
        min=0.0,
        max=100.0
    )

    zoom_strength: FloatProperty(
        name="Zoom Strength",
        default=5.0,
        min=0.0,
        max=100.0
    )

    min_distance: FloatProperty(
        name="Min Distance",
        default=0.2,
        min=0.001,
        max=10000.0,
        precision=3
    )

    max_distance: FloatProperty(
        name="Max Distance",
        default=1000.0,
        min=0.01,
        max=10000.0,
        precision=3
    )

    # -----------------------------
    # Depth View (Experimental) mode
    # -----------------------------
    window_camera: PointerProperty(
        name="Window Camera",
        type=bpy.types.Object,
        poll=_camera_object_poll,
        description="Camera used for head-tracked depth view mode"
    )

    window_xy_strength_x: FloatProperty(
        name="Move/Shift X",
        default=1.50,
        min=0.0,
        max=100.0,
        description="Controls both camera X movement and frustum X shift"
    )

    window_xy_strength_y: FloatProperty(
        name="Move/Shift Y",
        default=1.50,
        min=0.0,
        max=100.0,
        description="Controls both camera Y movement and frustum Y shift"
    )

    window_z_strength: FloatProperty(
        name="Move Z / FOV Zoom",
        default=1.50,
        min=0.0,
        max=100.0,
        description="Controls both camera Z movement and FOV zoom"
    )

    window_min_lens: FloatProperty(
        name="Window Min Lens",
        default=1.0,
        min=1.0,
        max=500.0
    )

    window_max_lens: FloatProperty(
        name="Window Max Lens",
        default=300.0,
        min=1.0,
        max=500.0
    )

    smoothing_alpha: FloatProperty(
        name="Smoothing Alpha",
        default=0.2,
        min=0.01,
        max=1.0,
        precision=3
    )

    deadzone: FloatProperty(
        name="Deadzone",
        default=0.03,
        min=0.0,
        max=0.5,
        precision=3
    )