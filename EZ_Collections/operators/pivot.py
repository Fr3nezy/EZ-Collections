"""EZ Collection Pivot - Operators"""

import bpy
from bpy.types import Operator
from bpy.props import EnumProperty
from mathutils import Vector
from ..core.pivot import (
    has_pivot,
    get_pivot_position,
    set_pivot_position,
    remove_pivot,
    compute_bounding_box_center,
    compute_bounding_box_bottom,
    compute_bounding_box_top,
)

_EMPTY_PREFIX = "EZ_PIVOT_TEMP"


def _get_active_collection(context):
    """Return the active collection from context (viewport active collection)."""
    return context.collection


def _find_collection_for_object(obj):
    """Return the first collection (with EZ pivot) that directly contains obj."""
    for col in bpy.data.collections:
        if obj.name in col.objects and has_pivot(col):
            return col
    return None


# ── Set Pivot (auto center) ───────────────────────────────────────────────────

class OBJECT_OT_ez_set_pivot(Operator):
    """Set EZ Collection pivot at bounding box center"""
    bl_idname = "object.ez_set_pivot"
    bl_label = "Set Collection Pivot"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        col = _get_active_collection(context)
        if col is None or col == context.scene.collection:
            self.report({'WARNING'}, "No active collection selected")
            return {'CANCELLED'}

        pos = compute_bounding_box_center(col)
        set_pivot_position(col, pos)
        self.report({'INFO'}, f"Pivot set at {pos.x:.3f}, {pos.y:.3f}, {pos.z:.3f}")
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}


# ── Reset Pivot ───────────────────────────────────────────────────────────────

class OBJECT_OT_ez_reset_pivot(Operator):
    """Reset EZ Collection pivot to bounding box center"""
    bl_idname = "object.ez_reset_pivot"
    bl_label = "Reset Pivot to Center"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        col = _get_active_collection(context)
        if col is None or col == context.scene.collection:
            self.report({'WARNING'}, "No active collection selected")
            return {'CANCELLED'}

        pos = compute_bounding_box_center(col)
        set_pivot_position(col, pos)
        self.report({'INFO'}, "Pivot reset to bounding box center")
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}


# ── Snap Pivot ────────────────────────────────────────────────────────────────

class OBJECT_OT_ez_snap_pivot(Operator):
    """Snap EZ Collection pivot to a preset position"""
    bl_idname = "object.ez_snap_pivot"
    bl_label = "Snap Pivot"
    bl_options = {'REGISTER', 'UNDO'}

    snap_to: EnumProperty(
        name="Snap To",
        items=[
            ('CENTER', "Center",       "Bounding box center"),
            ('BOTTOM', "Bottom",       "Bounding box bottom (min Z)"),
            ('TOP',    "Top",          "Bounding box top (max Z)"),
            ('ORIGIN', "World Origin", "World origin (0, 0, 0)"),
            ('CURSOR', "3D Cursor",    "Current 3D cursor position"),
        ],
        default='CENTER',
    )

    def execute(self, context):
        col = _get_active_collection(context)
        if col is None or col == context.scene.collection:
            self.report({'WARNING'}, "No active collection selected")
            return {'CANCELLED'}

        if self.snap_to == 'CENTER':
            pos = compute_bounding_box_center(col)
        elif self.snap_to == 'BOTTOM':
            pos = compute_bounding_box_bottom(col)
        elif self.snap_to == 'TOP':
            pos = compute_bounding_box_top(col)
        elif self.snap_to == 'ORIGIN':
            pos = Vector((0.0, 0.0, 0.0))
        elif self.snap_to == 'CURSOR':
            pos = Vector(context.scene.cursor.location)

        set_pivot_position(col, pos)
        self.report({'INFO'}, f"Pivot snapped to {self.snap_to.lower()}")
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}


# ── Edit Pivot (Empty proxy + native Blender transform) ───────────────────────

class OBJECT_OT_ez_edit_pivot(Operator):
    """
    Move the EZ Collection pivot using Blender's native transform system.
    An invisible Empty is placed at the pivot position and made active —
    the user moves it with G (supports snap, axis lock, numeric input).
    Confirm with LMB / Enter, cancel with RMB / Esc.
    """
    bl_idname = "object.ez_edit_pivot"
    bl_label = "Edit Collection Pivot"
    bl_options = {'REGISTER', 'UNDO'}

    _collection_name: str = ""
    _empty_name: str = ""
    _prev_active_name: str = ""
    _prev_selected_names: list = []

    def invoke(self, context, event):
        # Determine which collection to edit:
        # prefer the collection of the active object, fall back to context.collection
        col = None
        if context.active_object:
            col = _find_collection_for_object(context.active_object)
        if col is None:
            col = _get_active_collection(context)
        if col is None or col == context.scene.collection:
            self.report({'WARNING'}, "No collection with pivot found")
            return {'CANCELLED'}

        # Auto-create pivot if missing
        if not has_pivot(col):
            pos = compute_bounding_box_center(col)
            set_pivot_position(col, pos)

        pivot_pos = get_pivot_position(col)

        # Save current selection state
        self._prev_active_name = context.active_object.name if context.active_object else ""
        self._prev_selected_names = [o.name for o in context.selected_objects]
        self._collection_name = col.name

        # Create a small Empty at the pivot position as a proxy
        empty_data = None  # Empty has no mesh data
        empty = bpy.data.objects.new(_EMPTY_PREFIX, empty_data)
        empty.empty_display_type = 'PLAIN_AXES'
        empty.empty_display_size = 0.15
        empty.location = pivot_pos.copy()
        # Link to scene root so it's always visible
        context.scene.collection.objects.link(empty)
        self._empty_name = empty.name

        # Select only the empty
        bpy.ops.object.select_all(action='DESELECT')
        empty.select_set(True)
        context.view_layer.objects.active = empty

        # Set edit mode flag for the draw handler
        context.window_manager['ez_pivot_edit_mode'] = True

        # Launch Blender's native grab — user gets full snap/axis/numeric support
        bpy.ops.transform.translate('INVOKE_DEFAULT')

        # Register our modal to watch for completion
        context.window_manager.modal_handler_add(self)
        self.report({'INFO'}, "Move pivot with G — LMB/Enter confirm, RMB/Esc cancel")
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        empty = bpy.data.objects.get(self._empty_name)

        # The native translate operator consumes LEFTMOUSE/RET to confirm
        # and RIGHTMOUSE/ESC to cancel. After it finishes, the empty will
        # either be at the new position (confirm) or back at the original (cancel).
        # We detect completion by checking if the translate operator is no longer
        # running — i.e. the event passes through to us.

        if event.type in {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER'} and event.value == 'RELEASE':
            # Confirm: read empty position → update pivot
            col = bpy.data.collections.get(self._collection_name)
            if col is not None and empty is not None:
                set_pivot_position(col, Vector(empty.location))
            self._cleanup(context, empty)
            self.report({'INFO'}, "Pivot position confirmed")
            return {'FINISHED'}

        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            # Cancel: discard empty, pivot unchanged
            self._cleanup(context, empty)
            self.report({'INFO'}, "Pivot edit cancelled")
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def _cleanup(self, context, empty):
        """Remove the proxy empty and restore the original selection."""
        context.window_manager['ez_pivot_edit_mode'] = False

        if empty is not None:
            bpy.data.objects.remove(empty, do_unlink=True)

        # Restore previous selection
        bpy.ops.object.select_all(action='DESELECT')
        for name in self._prev_selected_names:
            obj = context.scene.objects.get(name)
            if obj:
                obj.select_set(True)
        if self._prev_active_name:
            prev = context.scene.objects.get(self._prev_active_name)
            if prev:
                context.view_layer.objects.active = prev

        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


# ── Remove Pivot ──────────────────────────────────────────────────────────────

class OBJECT_OT_ez_remove_pivot(Operator):
    """Remove the EZ Collection pivot"""
    bl_idname = "object.ez_remove_pivot"
    bl_label = "Remove Collection Pivot"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        col = _get_active_collection(context)
        if col is None or col == context.scene.collection:
            self.report({'WARNING'}, "No active collection selected")
            return {'CANCELLED'}

        if not has_pivot(col):
            self.report({'WARNING'}, "Collection has no pivot")
            return {'CANCELLED'}

        remove_pivot(col)
        self.report({'INFO'}, "Pivot removed")
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}


# ── Classes ───────────────────────────────────────────────────────────────────

classes = (
    OBJECT_OT_ez_set_pivot,
    OBJECT_OT_ez_reset_pivot,
    OBJECT_OT_ez_snap_pivot,
    OBJECT_OT_ez_edit_pivot,
    OBJECT_OT_ez_remove_pivot,
)
