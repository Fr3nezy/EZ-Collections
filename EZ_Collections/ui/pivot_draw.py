"""EZ Collection Pivot - GPU Draw Handler (Blender 4.x compatible)"""

import bpy
import gpu
import math
from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import location_3d_to_region_2d
from ..core.pivot import has_pivot, get_pivot_position, get_pivot_color

_draw_handle = None

PIVOT_DOT_RADIUS  = 5.0
PIVOT_CROSS_SIZE  = 10.0
PIVOT_SEGMENTS    = 24
PIVOT_LINE_WIDTH  = 2.0
PIVOT_EDIT_RADIUS = 8.0
PIVOT_EDIT_LINE_W = 3.0


def _circle_tris(cx, cy, radius, segments=PIVOT_SEGMENTS):
    """Filled circle as TRIS (fan from center)."""
    verts = []
    for i in range(segments):
        a0 = 2.0 * math.pi * i / segments
        a1 = 2.0 * math.pi * (i + 1) / segments
        verts.append((cx, cy))
        verts.append((cx + math.cos(a0) * radius, cy + math.sin(a0) * radius))
        verts.append((cx + math.cos(a1) * radius, cy + math.sin(a1) * radius))
    return verts


def _circle_outline(cx, cy, radius, segments=PIVOT_SEGMENTS):
    """Circle outline as LINE_STRIP (closed)."""
    verts = []
    for i in range(segments + 1):
        a = 2.0 * math.pi * i / segments
        verts.append((cx + math.cos(a) * radius, cy + math.sin(a) * radius))
    return verts


def _find_collection_for_object(obj):
    """Return the first collection (with EZ pivot) that directly contains obj."""
    for col in bpy.data.collections:
        if obj.name in col.objects and has_pivot(col):
            return col
    return None


def draw_pivot_callback():
    """
    GPU POST_PIXEL callback — draws the EZ pivot dot in the 3D viewport.
    Called for every region redraw; we must guard against non-WINDOW regions.
    """
    context = bpy.context

    # Only draw in the main WINDOW region of the 3D viewport
    region = context.region
    if region is None or region.type != 'WINDOW':
        return

    rv3d = context.region_data
    if rv3d is None:
        return

    if context.mode != 'OBJECT':
        return

    active_obj = context.active_object
    if active_obj is None:
        return

    # Skip the temporary empty used during pivot editing
    if active_obj.name.startswith("EZ_PIVOT_TEMP"):
        return

    col = _find_collection_for_object(active_obj)
    if col is None:
        return

    pivot_pos = get_pivot_position(col)
    if pivot_pos is None:
        return

    pivot_2d = location_3d_to_region_2d(region, rv3d, pivot_pos)
    if pivot_2d is None:
        return

    cx, cy = pivot_2d.x, pivot_2d.y
    is_edit = context.window_manager.get('ez_pivot_edit_mode', False)
    r, g, b, _ = get_pivot_color(col)
    a      = 1.0 if is_edit else 0.9
    radius = PIVOT_EDIT_RADIUS if is_edit else PIVOT_DOT_RADIUS
    cross  = PIVOT_CROSS_SIZE * (1.4 if is_edit else 1.0)
    lw     = PIVOT_EDIT_LINE_W if is_edit else PIVOT_LINE_WIDTH

    gpu.state.blend_set('ALPHA')

    # ── Filled dot (TRIS fan) ─────────────────────────────────────────────
    shader_uni = gpu.shader.from_builtin('UNIFORM_COLOR')
    dot_verts  = _circle_tris(cx, cy, radius * 0.45, 16)
    dot_batch  = batch_for_shader(shader_uni, 'TRIS', {"pos": dot_verts})
    shader_uni.bind()
    shader_uni.uniform_float("color", (r, g, b, a))
    dot_batch.draw(shader_uni)

    # ── Circle outline + cross (POLYLINE for real thickness) ──────────────
    shader_pl = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    vp = gpu.state.viewport_get()
    shader_pl.bind()
    shader_pl.uniform_float("viewportSize", (vp[2], vp[3]))
    shader_pl.uniform_float("lineWidth", lw)
    shader_pl.uniform_float("color", (r, g, b, a))

    circ_batch = batch_for_shader(shader_pl, 'LINE_STRIP',
                                  {"pos": _circle_outline(cx, cy, radius)})
    circ_batch.draw(shader_pl)

    h_batch = batch_for_shader(shader_pl, 'LINE_STRIP',
                               {"pos": [(cx - cross, cy), (cx + cross, cy)]})
    h_batch.draw(shader_pl)

    v_batch = batch_for_shader(shader_pl, 'LINE_STRIP',
                               {"pos": [(cx, cy - cross), (cx, cy + cross)]})
    v_batch.draw(shader_pl)

    # ── Glow ring in edit mode ────────────────────────────────────────────
    if is_edit:
        shader_pl.uniform_float("lineWidth", 1.0)
        shader_pl.uniform_float("color", (r, g, b, 0.3))
        glow_batch = batch_for_shader(shader_pl, 'LINE_STRIP',
                                      {"pos": _circle_outline(cx, cy, radius * 2.2)})
        glow_batch.draw(shader_pl)

    gpu.state.blend_set('NONE')


# ── Register / Unregister ─────────────────────────────────────────────────────

def register():
    global _draw_handle
    _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        draw_pivot_callback, (), 'WINDOW', 'POST_PIXEL'
    )


def unregister():
    global _draw_handle
    if _draw_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        _draw_handle = None
