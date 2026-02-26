bl_info = {
    "name": "EZCollections V5 - Modern Collection Manager",
    "author": "Lex & Manu",
    "version": (5, 0, 0),
    "blender": (4, 5, 0),
    "location": "Pie Menu (Ctrl+G) & N-Panel (View3D > EZ Collections)",
    "description": "Modern collection management with customizable naming and Maya-style workflow",
    "category": "Object",
}

import bpy
from . import preferences
from . import operators
from . import ui
from . import core

# Global keymaps
addon_keymaps = []

def register():
    """Register all addon components"""
    preferences.register()
    core.register()
    operators.register()
    ui.register()
    
    # Register keymap for pie menu
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name="Object Mode", space_type='EMPTY')
    kmi = km.keymap_items.new("wm.call_menu_pie", 'G', 'PRESS', ctrl=True)
    kmi.properties.name = "VIEW3D_MT_ez_collections_pie"
    addon_keymaps.append((km, kmi))

def unregister():
    """Unregister all addon components"""
    # Remove keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    ui.unregister()
    operators.unregister()
    core.unregister()
    preferences.unregister()

if __name__ == "__main__":
    register()
