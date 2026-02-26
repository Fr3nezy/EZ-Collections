"""EZCollection class - simplified collection wrapper"""

import bpy


class EZCollection:
    """Simplified wrapper class for Blender collections"""
    
    _instances = {}

    def __new__(cls, bl_collection):
        """Singleton pattern per collection"""
        name = bl_collection.name
        if name in cls._instances:
            inst = cls._instances[name]
            if inst.is_valid():
                return inst
            else:
                del cls._instances[name]
        
        inst = super().__new__(cls)
        cls._instances[name] = inst
        return inst

    def __init__(self, bl_collection):
        """Initialize EZ collection wrapper"""
        if hasattr(self, "bl_collection"):
            return
        self.bl_collection = bl_collection
        bl_collection["ez_collection"] = True

    def is_valid(self):
        """Check if collection still exists"""
        try:
            if self.bl_collection.name not in bpy.data.collections:
                return False
            list(self.bl_collection.objects)
            return True
        except ReferenceError:
            return False

    @property
    def all_objects(self):
        """Get all objects including nested collections"""
        if not self.is_valid():
            return []
        
        objs = list(self.bl_collection.objects)
        for child in self.bl_collection.children:
            child_ez = EZCollection(child)
            if child_ez.is_valid():
                objs += child_ez.all_objects
        return objs

    @classmethod
    def cleanup_invalid_instances(cls):
        """Remove invalid instances from cache"""
        to_remove = []
        for name, inst in cls._instances.items():
            if not inst.is_valid():
                to_remove.append(name)
        for name in to_remove:
            del cls._instances[name]
