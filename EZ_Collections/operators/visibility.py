"""Collection Visibility operators"""

import bpy
from bpy.types import Operator
from ..core import get_active_ez_collection, set_collection_visibility


class OBJECT_OT_ez_toggle_solo_collection(Operator):
    """Toggle solo mode for active collection"""
    bl_idname = "object.ez_toggle_solo_collection"
    bl_label = "Solo Toggle"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Execute solo toggle"""
        ez_col = get_active_ez_collection()
        if not ez_col:
            self.report({'ERROR'}, "No active EZ collection")
            return {'CANCELLED'}

        col = ez_col.bl_collection
        is_visible = not col.hide_viewport
        
        if is_visible:
            # Hide all other collections
            for other_col in bpy.data.collections:
                if other_col != col:
                    set_collection_visibility(other_col, False)
            self.report({'INFO'}, f"Solo mode: {col.name}")
        else:
            # Show all collections
            for other_col in bpy.data.collections:
                set_collection_visibility(other_col, True)
            self.report({'INFO'}, "Solo mode off")
        
        return {'FINISHED'}
