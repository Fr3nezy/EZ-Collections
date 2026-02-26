"""Create Collection operator"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from ..core import EZCollection
from ..preferences import get_preferences


class OBJECT_OT_ez_create_collection(Operator):
    """Create new EZ collection from selected objects"""
    bl_idname = "object.ez_create_collection"
    bl_label = "Create EZ Collection"
    bl_options = {'REGISTER', 'UNDO'}

    collection_name: StringProperty(
        name="Name",
        description="Name for the new collection",
        default="EZ_Collection",
    )

    def invoke(self, context, event):
        """Show dialog for collection name"""
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        """Draw dialog UI"""
        layout = self.layout
        prefs = get_preferences()
        
        layout.prop(self, "collection_name")
        
        # Preview final name
        final_name = (prefs.collection_prefix + 
                     self.collection_name + 
                     prefs.collection_suffix)
        layout.label(text=f"Final: {final_name}", icon='INFO')

    def execute(self, context):
        """Execute collection creation"""
        sel = context.selected_objects
        if not sel:
            self.report({'ERROR'}, "Select objects first")
            return {'CANCELLED'}

        prefs = get_preferences()
        
        # Apply prefix and suffix
        final_name = (prefs.collection_prefix + 
                     self.collection_name + 
                     prefs.collection_suffix)
        
        # Create collection
        col = bpy.data.collections.new(final_name)
        
        # Link to parent collection
        if prefs.create_in_active_collection and context.collection:
            context.collection.children.link(col)
        else:
            context.scene.collection.children.link(col)
        
        # Move objects to new collection (remove from old ones)
        for obj in sel:
            for old_col in list(obj.users_collection):
                old_col.objects.unlink(obj)
            col.objects.link(obj)
        
        # Create EZ wrapper
        ez_col = EZCollection(col)
        
        self.report({'INFO'}, f"Created '{final_name}'")
        return {'FINISHED'}
