"""EZ Collection Pivot - Core logic"""

import bpy
from mathutils import Vector


# Custom property key stored on the collection
EZ_PIVOT_KEY = "ez_pivot"

# Color tag → RGBA color mapping (matches Blender's built-in collection colors)
COLOR_TAG_COLORS = {
    'NONE':     (0.0,  0.8,  0.8,  1.0),   # Teal/Cyan (default when no tag)
    'COLOR_01': (1.0,  0.25, 0.25, 1.0),   # Red
    'COLOR_02': (1.0,  0.55, 0.1,  1.0),   # Orange
    'COLOR_03': (1.0,  0.9,  0.1,  1.0),   # Yellow
    'COLOR_04': (0.25, 0.85, 0.25, 1.0),   # Green
    'COLOR_05': (0.1,  0.8,  0.7,  1.0),   # Teal
    'COLOR_06': (0.25, 0.5,  1.0,  1.0),   # Blue
    'COLOR_07': (0.7,  0.3,  1.0,  1.0),   # Violet
    'COLOR_08': (1.0,  0.4,  0.7,  1.0),   # Pink
}


def get_pivot_color(collection):
    """Return RGBA color for the pivot based on the collection's color_tag"""
    tag = getattr(collection, 'color_tag', 'NONE')
    return COLOR_TAG_COLORS.get(tag, COLOR_TAG_COLORS['NONE'])


def has_pivot(collection):
    """Check if a collection has a pivot defined"""
    return EZ_PIVOT_KEY in collection


def get_pivot_position(collection):
    """Get pivot position as Vector. Returns None if not set."""
    if not has_pivot(collection):
        return None
    raw = collection[EZ_PIVOT_KEY]
    return Vector((raw[0], raw[1], raw[2]))


def set_pivot_position(collection, position):
    """Set pivot position from a Vector or (x, y, z) tuple"""
    collection[EZ_PIVOT_KEY] = (
        float(position[0]),
        float(position[1]),
        float(position[2]),
    )


def remove_pivot(collection):
    """Remove pivot data from a collection"""
    if EZ_PIVOT_KEY in collection:
        del collection[EZ_PIVOT_KEY]


def compute_bounding_box_center(collection):
    """
    Compute the center of the bounding box of all objects
    in the collection (including nested collections).
    Returns Vector(0,0,0) if no objects found.
    """
    all_objs = _collect_all_objects(collection)
    if not all_objs:
        return Vector((0.0, 0.0, 0.0))

    min_co = Vector((float('inf'),  float('inf'),  float('inf')))
    max_co = Vector((float('-inf'), float('-inf'), float('-inf')))

    for obj in all_objs:
        for corner in _get_world_bbox_corners(obj):
            min_co.x = min(min_co.x, corner.x)
            min_co.y = min(min_co.y, corner.y)
            min_co.z = min(min_co.z, corner.z)
            max_co.x = max(max_co.x, corner.x)
            max_co.y = max(max_co.y, corner.y)
            max_co.z = max(max_co.z, corner.z)

    return (min_co + max_co) / 2.0


def compute_bounding_box_bottom(collection):
    """Return the bottom-center of the bounding box (min Z, center XY)"""
    all_objs = _collect_all_objects(collection)
    if not all_objs:
        return Vector((0.0, 0.0, 0.0))

    min_co = Vector((float('inf'),  float('inf'),  float('inf')))
    max_co = Vector((float('-inf'), float('-inf'), float('-inf')))

    for obj in all_objs:
        for corner in _get_world_bbox_corners(obj):
            min_co.x = min(min_co.x, corner.x)
            min_co.y = min(min_co.y, corner.y)
            min_co.z = min(min_co.z, corner.z)
            max_co.x = max(max_co.x, corner.x)
            max_co.y = max(max_co.y, corner.y)
            max_co.z = max(max_co.z, corner.z)

    center_x = (min_co.x + max_co.x) / 2.0
    center_y = (min_co.y + max_co.y) / 2.0
    return Vector((center_x, center_y, min_co.z))


def compute_bounding_box_top(collection):
    """Return the top-center of the bounding box (max Z, center XY)"""
    all_objs = _collect_all_objects(collection)
    if not all_objs:
        return Vector((0.0, 0.0, 0.0))

    min_co = Vector((float('inf'),  float('inf'),  float('inf')))
    max_co = Vector((float('-inf'), float('-inf'), float('-inf')))

    for obj in all_objs:
        for corner in _get_world_bbox_corners(obj):
            min_co.x = min(min_co.x, corner.x)
            min_co.y = min(min_co.y, corner.y)
            min_co.z = min(min_co.z, corner.z)
            max_co.x = max(max_co.x, corner.x)
            max_co.y = max(max_co.y, corner.y)
            max_co.z = max(max_co.z, corner.z)

    center_x = (min_co.x + max_co.x) / 2.0
    center_y = (min_co.y + max_co.y) / 2.0
    return Vector((center_x, center_y, max_co.z))


# ── Internal helpers ──────────────────────────────────────────────────────────

def _collect_all_objects(collection):
    """Recursively collect all objects from a collection and its children"""
    objs = list(collection.objects)
    for child in collection.children:
        objs += _collect_all_objects(child)
    return objs


def _get_world_bbox_corners(obj):
    """Return the 8 world-space corners of an object's bounding box"""
    mat = obj.matrix_world
    return [mat @ Vector(corner) for corner in obj.bound_box]
