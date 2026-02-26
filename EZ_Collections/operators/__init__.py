"""Operators module for EZCollections"""

from .create_collection import OBJECT_OT_ez_create_collection
from .add_remove import (
    OBJECT_OT_ez_add_to_collection,
    OBJECT_OT_ez_remove_from_collection,
)
from .visibility import OBJECT_OT_ez_toggle_solo_collection
from .pivot import (
    OBJECT_OT_ez_set_pivot,
    OBJECT_OT_ez_reset_pivot,
    OBJECT_OT_ez_snap_pivot,
    OBJECT_OT_ez_edit_pivot,
    OBJECT_OT_ez_remove_pivot,
)

classes = (
    OBJECT_OT_ez_create_collection,
    OBJECT_OT_ez_add_to_collection,
    OBJECT_OT_ez_remove_from_collection,
    OBJECT_OT_ez_toggle_solo_collection,
    OBJECT_OT_ez_set_pivot,
    OBJECT_OT_ez_reset_pivot,
    OBJECT_OT_ez_snap_pivot,
    OBJECT_OT_ez_edit_pivot,
    OBJECT_OT_ez_remove_pivot,
)


def register():
    """Register all operators"""
    import bpy
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister all operators"""
    import bpy
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
