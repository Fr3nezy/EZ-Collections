"""N-Panel for EZCollections"""

from bpy.types import Panel
from ..preferences import get_preferences


class VIEW3D_PT_ez_collections_panel(Panel):
    """EZ Collections N-Panel"""
    bl_label = "EZ Collections"
    bl_idname = "VIEW3D_PT_ez_collections_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'EZ Collections'

    def draw(self, context):
        """Draw panel UI"""
        layout = self.layout
        prefs = get_preferences()
        
        # Collection Naming Section
        box = layout.box()
        box.label(text="Collection Naming", icon='SORTALPHA')
        box.prop(prefs, "collection_prefix", text="Prefix")
        box.prop(prefs, "collection_suffix", text="Suffix")
        
        # Preview
        preview_name = (prefs.collection_prefix + 
                       "NewCollection" + 
                       prefs.collection_suffix)
        box.label(text=f"Preview: {preview_name}", icon='INFO')
        
        # Collection Appearance Section
        box = layout.box()
        box.label(text="Collection Appearance", icon='COLOR')
        box.prop(prefs, "collection_color", text="Color")
        
        # Creation Mode Section
        box = layout.box()
        box.label(text="Creation Mode", icon='OUTLINER_COLLECTION')
        box.prop(prefs, "create_in_active_collection", text="In Active")
        
        # Quick Actions
        layout.separator()
        col = layout.column(align=True)
        col.label(text="Quick Actions:", icon='PLAY')
        col.operator("object.ez_create_collection", icon='ADD')
        col.operator("object.ez_add_to_collection", icon='FORWARD')
        col.operator("object.ez_remove_from_collection", icon='BACK')
        col.operator("object.ez_toggle_solo_collection", icon='HIDE_OFF')
