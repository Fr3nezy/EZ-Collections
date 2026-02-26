"""Addon Preferences for EZCollections"""

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, EnumProperty


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
    
    collection_color_tag: EnumProperty(
        name="Collection Color Tag",
        description="Color tag for new collections (matches Blender's built-in color tags)",
        items=[
            ('NONE',     "None",   "No color tag",         'X',                    0),
            ('COLOR_01', "Red",    "Red color tag",         'COLLECTION_COLOR_01',  1),
            ('COLOR_02', "Orange", "Orange color tag",      'COLLECTION_COLOR_02',  2),
            ('COLOR_03', "Yellow", "Yellow color tag",      'COLLECTION_COLOR_03',  3),
            ('COLOR_04', "Green",  "Green color tag",       'COLLECTION_COLOR_04',  4),
            ('COLOR_05', "Teal",   "Teal color tag",        'COLLECTION_COLOR_05',  5),
            ('COLOR_06', "Blue",   "Blue color tag",        'COLLECTION_COLOR_06',  6),
            ('COLOR_07', "Violet", "Violet color tag",      'COLLECTION_COLOR_07',  7),
            ('COLOR_08', "Pink",   "Pink color tag",        'COLLECTION_COLOR_08',  8),
        ],
        default='NONE',
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
        box.prop(self, "collection_color_tag")
        
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
