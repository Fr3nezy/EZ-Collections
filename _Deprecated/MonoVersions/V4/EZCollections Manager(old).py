bl_info = {
    "name": "EZCollections Manager",
    "author": "Lex & Manu",
    "version": (1, 2),
    "blender": (4, 0, 0),
    "location": "Pie Menu (Ctrl+G) & Outliner (Ctrl+Click)",
    "description": "Advanced collection management with smart pivots and full workflow",
    "category": "Object",
}

import bpy
from bpy.types import Operator, Menu
from bpy.props import StringProperty
from mathutils import Vector

addon_keymaps = []

def set_visibility(collection, visible):
    collection.hide_viewport = not visible
    collection.hide_render   = not visible

def hide_all_pivots():
    for col in bpy.data.collections:
        if "ez_pivot" in col:
            p = bpy.data.objects.get(col["ez_pivot"])
            if p:
                p.hide_viewport = True

# -----------------------------------
# Outliner: Ctrl+Click on collection
# -----------------------------------
class OUTLINER_OT_ez_select_collection(Operator):
    bl_idname = "outliner.ez_select_collection"
    bl_label  = "EZ Select Collection Contents"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        alc = context.view_layer.active_layer_collection
        if not alc:
            self.report({'WARNING'}, "No active collection in Outliner.")
            return {'CANCELLED'}

        # Select all objects in that collection
        bpy.ops.object.select_all(action='DESELECT')
        for o in alc.collection.objects:
            o.select_set(True)
        if alc.collection.objects:
            context.view_layer.objects.active = alc.collection.objects[0]

        # Show only the active pivot
        hide_all_pivots()
        pivot = bpy.data.objects.get(alc.collection.get("ez_pivot", ""))
        if pivot:
            pivot.hide_viewport = False

        return {'FINISHED'}

# -----------------------------------
# Create EZ Collection (Ctrl+G)
# -----------------------------------
class OBJECT_OT_ez_create_collection(Operator):
    bl_idname = "object.ez_create_collection"
    bl_label  = "Create EZ Collection"
    bl_options = {'REGISTER', 'UNDO'}

    collection_suffix: StringProperty(
        name="Collection Name",
        description="Enter name suffix (prefixed with 'COL_')",
        default=""
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "collection_suffix")

    def execute(self, context):
        objs = context.selected_objects
        if not objs:
            self.report({'ERROR'}, "Select at least one object first.")
            return {'CANCELLED'}

        # Clear parent but keep transform
        for o in objs:
            bpy.ops.object.select_all(action='DESELECT')
            o.select_set(True)
            context.view_layer.objects.active = o
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        suffix = self.collection_suffix.strip()
        if not suffix:
            self.report({'ERROR'}, "Collection name cannot be empty.")
            return {'CANCELLED'}

        # Unique name
        base = f"COL_{suffix}"
        existing = [c.name for c in bpy.data.collections if c.name.startswith(base)]
        name = base; i = 1
        while name in existing:
            name = f"{base}_{i}"
            i += 1

        # Create collection
        col = bpy.data.collections.new(name)
        col.color_tag = 'COLOR_02'
        context.scene.collection.children.link(col)

        # Link objects
        for o in objs:
            for pc in o.users_collection:
                pc.objects.unlink(o)
            col.objects.link(o)

        # Compute centroid
        center = sum((o.matrix_world.translation for o in objs), Vector()) / len(objs)

        # Create pivot at centroid
        pivot = bpy.data.objects.new(f"Pivot_{name}", None)
        pivot.empty_display_type = 'PLAIN_AXES'
        pivot.empty_display_size = 0.2
        pivot.location = center
        col.objects.link(pivot)

        # Parent to pivot keep transform
        bpy.ops.object.select_all(action='DESELECT')
        pivot.select_set(True)
        for o in objs:
            o.select_set(True)
        context.view_layer.objects.active = pivot
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        # Store pivot
        col["ez_pivot"] = pivot.name

        # Hide all pivots, show this one
        hide_all_pivots()
        pivot.hide_viewport = False

        # Activate pivot
        bpy.ops.object.select_all(action='DESELECT')
        pivot.select_set(True)
        context.view_layer.objects.active = pivot

        self.report({'INFO'}, f"Collection '{name}' created with pivot at centroid.")
        return {'FINISHED'}

# -----------------------------------
# Add to EZ Collection
# -----------------------------------
class OBJECT_OT_ez_add_to_collection(Operator):
    bl_idname = "object.ez_add_to_collection"
    bl_label  = "Add to EZ Collection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        alc = context.view_layer.active_layer_collection
        if not alc or "ez_pivot" not in alc.collection:
            self.report({'ERROR'}, "Active collection is not an EZCollection.")
            return {'CANCELLED'}

        col   = alc.collection
        pivot = bpy.data.objects.get(col["ez_pivot"])
        sel   = [o for o in context.selected_objects if o != pivot]
        if not sel:
            self.report({'WARNING'}, "No valid objects selected.")
            return {'CANCELLED'}

        for o in sel:
            if o.name not in col.objects:
                for pc in o.users_collection:
                    if pc != col:
                        pc.objects.unlink(o)
                col.objects.link(o)

        # Parent to pivot keep transform
        bpy.ops.object.select_all(action='DESELECT')
        pivot.select_set(True)
        for o in sel:
            o.select_set(True)
        context.view_layer.objects.active = pivot
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        self.report({'INFO'}, f"{len(sel)} object(s) added to '{col.name}'.")
        return {'FINISHED'}

# -----------------------------------
# Remove from EZ Collection
# -----------------------------------
class OBJECT_OT_ez_remove_from_collection(Operator):
    bl_idname = "object.ez_remove_from_collection"
    bl_label  = "Remove from EZ Collection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        alc = context.view_layer.active_layer_collection
        if not alc or "ez_pivot" not in alc.collection:
            self.report({'ERROR'}, "Active collection is not an EZCollection.")
            return {'CANCELLED'}

        col   = alc.collection
        pivot = bpy.data.objects.get(col["ez_pivot"])
        sel   = [o for o in context.selected_objects if o != pivot]
        if not sel:
            self.report({'WARNING'}, "No valid objects selected.")
            return {'CANCELLED'}

        for o in sel:
            bpy.ops.object.select_all(action='DESELECT')
            o.select_set(True)
            context.view_layer.objects.active = o
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            if o.name in col.objects:
                col.objects.unlink(o)
            if o.name not in context.scene.collection.objects:
                context.scene.collection.objects.link(o)

        self.report({'INFO'}, f"{len(sel)} object(s) removed from '{col.name}'.")
        return {'FINISHED'}

# -----------------------------------
# Origin Utilities
# -----------------------------------
class OBJECT_OT_ez_origin_to_center(Operator):
    bl_idname = "object.ez_origin_to_center"
    bl_label  = "Origin to Center of Mass"
    def execute(self, context):
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
        return {'FINISHED'}

class OBJECT_OT_ez_origin_to_cursor(Operator):
    bl_idname = "object.ez_origin_to_cursor"
    bl_label  = "Origin to 3D Cursor"
    def execute(self, context):
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        return {'FINISHED'}

# -----------------------------------
# Pivot Lock/Unlock
# -----------------------------------
class OBJECT_OT_ez_pivot_unlock(Operator):
    bl_idname = "object.ez_pivot_unlock"
    bl_label  = "Unlock Pivot"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        alc   = context.view_layer.active_layer_collection
        pivot = bpy.data.objects.get(alc.collection.get("ez_pivot", ""))
        if not pivot:
            self.report({'ERROR'}, "Pivot not found.")
            return {'CANCELLED'}
        children = [o for o in alc.collection.objects if o.parent == pivot]
        bpy.ops.object.select_all(action='DESELECT')
        for o in children:
            o.select_set(True)
        if children:
            context.view_layer.objects.active = children[0]
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        bpy.ops.object.select_all(action='DESELECT')
        pivot.select_set(True)
        context.view_layer.objects.active = pivot
        self.report({'INFO'}, f"Pivot '{pivot.name}' unlocked.")
        return {'FINISHED'}

class OBJECT_OT_ez_pivot_lock(Operator):
    bl_idname = "object.ez_pivot_lock"
    bl_label  = "Lock Pivot"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        alc   = context.view_layer.active_layer_collection
        pivot = bpy.data.objects.get(alc.collection.get("ez_pivot", ""))
        if not pivot:
            self.report({'ERROR'}, "Pivot not found.")
            return {'CANCELLED'}
        bpy.ops.object.select_all(action='DESELECT')
        pivot.select_set(True)
        for o in alc.collection.objects:
            if o != pivot:
                o.select_set(True)
        context.view_layer.objects.active = pivot
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        self.report({'INFO'}, f"Pivot '{pivot.name}' locked.")
        return {'FINISHED'}

# -----------------------------------
# Solo Toggle
# -----------------------------------
class OBJECT_OT_ez_toggle_solo_collection(Operator):
    bl_idname = "object.ez_toggle_solo_collection"
    bl_label  = "Toggle Solo View"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        alc = context.view_layer.active_layer_collection
        if not alc or "ez_pivot" not in alc.collection:
            self.report({'ERROR'}, "Active collection is not an EZCollection.")
            return {'CANCELLED'}
        col = alc.collection; key = "ez_solo_backup"
        if key not in context.scene:
            backup = {c.name: c.hide_viewport for c in bpy.data.collections}
            context.scene[key] = backup
            for c in bpy.data.collections:
                set_visibility(c, c==col)
            self.report({'INFO'}, f"Solo view ON for '{col.name}'.")
        else:
            backup = context.scene[key]
            for name, was in backup.items():
                c = bpy.data.collections.get(name)
                if c: c.hide_viewport = was
            del context.scene[key]
            self.report({'INFO'}, "Solo view OFF. Restored previous state.")
        return {'FINISHED'}

# -----------------------------------
# Pie Menu
# -----------------------------------  
class VIEW3D_MT_ez_collections_pie(Menu):
    bl_idname = "VIEW3D_MT_ez_collections_pie"
    bl_label  = "EZ Collections"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("object.ez_add_to_collection",    text="Add",    icon='PLUS')
        pie.operator("object.ez_remove_from_collection", text="Remove", icon='REMOVE')
        pie.operator("object.ez_create_collection",    text="Create", icon='GROUP')
        pie.operator("object.ez_toggle_solo_collection", text="Solo", icon='RESTRICT_VIEW_ON')
        pie.operator("object.ez_origin_to_center",     text="Origin Center", icon='PIVOT_BOUNDBOX')
        pie.operator("object.ez_origin_to_cursor",     text="Origin Cursor", icon='PIVOT_CURSOR')
        pie.operator("object.ez_pivot_lock",           text="Lock Pivot", icon='LOCKED')
        pie.operator("object.ez_pivot_unlock",         text="Unlock Pivot", icon='UNLOCKED')

classes = [
    OUTLINER_OT_ez_select_collection,
    OBJECT_OT_ez_create_collection,
    OBJECT_OT_ez_add_to_collection,
    OBJECT_OT_ez_remove_from_collection,
    OBJECT_OT_ez_origin_to_center,
    OBJECT_OT_ez_origin_to_cursor,
    OBJECT_OT_ez_pivot_unlock,
    OBJECT_OT_ez_pivot_lock,
    OBJECT_OT_ez_toggle_solo_collection,
    VIEW3D_MT_ez_collections_pie,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name="Object Mode", space_type='EMPTY')
    kmi = km.keymap_items.new("wm.call_menu_pie", 'G', 'PRESS', ctrl=True)
    kmi.properties.name = VIEW3D_MT_ez_collections_pie.bl_idname
    addon_keymaps.append((km, kmi))
    km2 = wm.keyconfigs.addon.keymaps.new(name="Outliner", space_type='OUTLINER')
    kmi2 = km2.keymap_items.new(OUTLINER_OT_ez_select_collection.bl_idname, 'LEFTMOUSE', 'PRESS', ctrl=True)
    addon_keymaps.append((km2, kmi2))

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__=="__main__":
    register()
