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
        box.prop(prefs, "collection_color_tag", text="Color Tag")
        
        # Creation Mode Section
        box = layout.box()
        box.label(text="Creation Mode", icon='OUTLINER_COLLECTION')
        box.prop(prefs, "create_in_active_collection", text="In Active")
        
        # Collection Pivot Section
        box = layout.box()
        box.label(text="Collection Pivot", icon='OBJECT_ORIGIN')

        active_col = context.collection
        scene_col = context.scene.collection
        has_valid_col = (active_col is not None and active_col != scene_col)

        if has_valid_col:
            from ..core.pivot import has_pivot, get_pivot_position
            if has_pivot(active_col):
                pos = get_pivot_position(active_col)
                if pos:
                    row = box.row()
                    row.label(text=f"X: {pos.x:.3f}  Y: {pos.y:.3f}  Z: {pos.z:.3f}",
                              icon='EMPTY_AXIS')

                row = box.row(align=True)
                row.operator("object.ez_edit_pivot",  text="Edit",  icon='GREASEPENCIL')
                row.operator("object.ez_reset_pivot", text="Reset", icon='LOOP_BACK')
                row.operator("object.ez_remove_pivot", text="", icon='X')

                # Snap presets
                snap_col = box.column(align=True)
                snap_col.label(text="Snap to:", icon='SNAP_ON')
                row2 = snap_col.row(align=True)
                op = row2.operator("object.ez_snap_pivot", text="Center")
                op.snap_to = 'CENTER'
                op = row2.operator("object.ez_snap_pivot", text="Bottom")
                op.snap_to = 'BOTTOM'
                op = row2.operator("object.ez_snap_pivot", text="Top")
                op.snap_to = 'TOP'
                row3 = snap_col.row(align=True)
                op = row3.operator("object.ez_snap_pivot", text="Origin")
                op.snap_to = 'ORIGIN'
                op = row3.operator("object.ez_snap_pivot", text="Cursor")
                op.snap_to = 'CURSOR'
            else:
                box.operator("object.ez_set_pivot", text="Set Pivot", icon='OBJECT_ORIGIN')
        else:
            box.label(text="Select a collection in the Outliner", icon='INFO')

        # Quick Actions
        layout.separator()
        col = layout.column(align=True)
        col.label(text="Quick Actions:", icon='PLAY')
        col.operator("object.ez_create_collection", icon='ADD')
        col.operator("object.ez_add_to_collection", icon='FORWARD')
        col.operator("object.ez_remove_from_collection", icon='BACK')
        col.operator("object.ez_toggle_solo_collection", icon='HIDE_OFF')
