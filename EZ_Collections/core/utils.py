"""Utility functions for EZCollections"""

import bpy
from .collection import EZCollection


def get_active_ez_collection():
    """Find EZ collection from active or selected objects"""
    EZCollection.cleanup_invalid_instances()
    
    context = bpy.context
    obj = context.active_object
    
    if not obj:
        # Fallback: search through selected objects
        for sel_obj in context.selected_objects:
            ez_col = get_ez_collection_from_object(sel_obj)
            if ez_col:
                return ez_col
        return None
    
    return get_ez_collection_from_object(obj)


def get_ez_collection_from_object(obj):
    """Get EZ collection from a specific object"""
    if not obj:
        return None
    
    for col in obj.users_collection:
        if col.get("ez_collection"):
            ez_col = EZCollection(col)
            if ez_col.is_valid():
                return ez_col
    return None


def set_collection_visibility(collection, visible):
    """Set collection viewport and render visibility"""
    collection.hide_viewport = not visible
    collection.hide_render = not visible
