"""UI module for EZCollections"""

from .pie_menu import VIEW3D_MT_ez_collections_pie
from .panel import VIEW3D_PT_ez_collections_panel
from . import pivot_draw

classes = (
    VIEW3D_MT_ez_collections_pie,
    VIEW3D_PT_ez_collections_panel,
)


def register():
    """Register all UI components"""
    import bpy
    for cls in classes:
        bpy.utils.register_class(cls)
    pivot_draw.register()


def unregister():
    """Unregister all UI components"""
    import bpy
    pivot_draw.unregister()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
