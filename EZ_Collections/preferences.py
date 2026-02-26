"""Addon Preferences for EZCollections"""

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, FloatVectorProperty


class EZCollectionsPreferences(AddonPreferences):
    """EZCollections addon preferences"""
    bl_idname = __package__
    
    collection_prefix: StringProperty(
        name="Prefix",
        description="Prefix added to collection names",
        default="",
    )
    
    collection_suffix: StringProperty(
        name="Suffix", 
        description="Suffix added to collection names",
        default="",
    )
    
    collection_color: FloatVectorProperty(
        name="Collection Color",
        description="Default color for new collections",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 0.647, 0.0),  # Blender orange
    )
    
    create_in_active_collection: BoolProperty(
        name="Create in Active Collection",
        description="Create new collections as children of the active collection",
        default=False,
    )
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        
        box = layout.box()
        box.label(text="Collection Naming", icon='SORTALPHA')
        box.prop(self, "collection_prefix")
        box.prop(self, "collection_suffix")
        
        box = layout.box()
        box.label(text="Collection Appearance", icon='COLOR')
        box.prop(self, "collection_color")
        
        box = layout.box()
        box.label(text="Creation Mode", icon='OUTLINER_COLLECTION')
        box.prop(self, "create_in_active_collection")


def get_preferences():
    """Get addon preferences"""
    return bpy.context.preferences.addons[__package__].preferences


classes = (
    EZCollectionsPreferences,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
