"""Add and Remove from Collection operators"""

import bpy
from bpy.types import Operator
from ..core import get_active_ez_collection


class OBJECT_OT_ez_add_to_collection(Operator):
    """Add selected objects to active EZ collection"""
    bl_idname = "object.ez_add_to_collection"
    bl_label = "Add to EZ Collection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Execute add operation"""
        ez_col = get_active_ez_collection()
        if not ez_col:
            self.report({'ERROR'}, "No active EZ collection")
            return {'CANCELLED'}

        added = 0
        existing_names = [o.name for o in ez_col.all_objects]
        
        for obj in context.selected_objects:
            if obj.name not in existing_names:
                ez_col.bl_collection.objects.link(obj)
                added += 1

        self.report({'INFO'}, f"Added {added} objects")
        return {'FINISHED'}


class OBJECT_OT_ez_remove_from_collection(Operator):
    """Remove selected objects from their EZ collection"""
    bl_idname = "object.ez_remove_from_collection"
    bl_label = "Remove from EZ Collection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Execute remove operation"""
        ez_col = get_active_ez_collection()
        if not ez_col:
            self.report({'ERROR'}, "No active EZ collection")
            return {'CANCELLED'}

        removed = 0
        collection_obj_names = [o.name for o in ez_col.bl_collection.objects]
        
        for obj in context.selected_objects:
            if obj.name in collection_obj_names:
                ez_col.bl_collection.objects.unlink(obj)
                removed += 1

        self.report({'INFO'}, f"Removed {removed} objects")
        return {'FINISHED'}
