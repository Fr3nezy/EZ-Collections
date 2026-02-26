"""Pie Menu for EZCollections"""

from bpy.types import Menu


class VIEW3D_MT_ez_collections_pie(Menu):
    """EZ Collections pie menu"""
    bl_idname = "VIEW3D_MT_ez_collections_pie"
    bl_label = "EZ Collections V5"

    def draw(self, context):
        """Draw pie menu layout"""
        layout = self.layout
        pie = layout.menu_pie()

        # West
        pie.operator(
            "object.ez_add_to_collection",
            text="Add",
            icon='ADD'
        )
        # East
        pie.operator(
            "object.ez_remove_from_collection",
            text="Remove",
            icon='REMOVE'
        )
        # South
        pie.operator(
            "object.ez_create_collection",
            text="Create",
            icon='OUTLINER_COLLECTION'
        )
        # North
        pie.operator(
            "object.ez_toggle_solo_collection",
            text="Solo",
            icon='RESTRICT_VIEW_ON'
        )
        # North-West
        pie.operator(
            "object.ez_edit_pivot",
            text="Edit Pivot",
            icon='OBJECT_ORIGIN'
        )
        # North-East
        pie.operator(
            "object.ez_set_pivot",
            text="Set Pivot",
            icon='SNAP_MIDPOINT'
        )
