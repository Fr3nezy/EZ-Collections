bl_info = {
    "name": "EZCollections Manager",
    "author": "Lex & Manu",
    "version": (2, 4),
    "blender": (4, 0, 0),
    "location": "Pie Menu (Ctrl+G) & Outliner (Shift+Ctrl+Click)",
    "description": "Advanced collection management with smart pivots and full workflow",
    "category": "Object",
}

import bpy
import bmesh
from bpy.types import Operator, Menu
from bpy.props import StringProperty
from mathutils import Vector
import random

addon_keymaps = []

# Variabili globali per il timer di selezione
_last_selected = set()


def set_visibility(collection, visible):
    """Imposta visibilità di una collection nel viewport e render"""
    collection.hide_viewport = not visible
    collection.hide_render = not visible


def hide_all_pivots():
    """Nasconde tutti i pivot EZ nel viewport"""
    for col in bpy.data.collections:
        if "ez_pivot" in col:
            pivot = bpy.data.objects.get(col["ez_pivot"])
            if pivot:
                pivot.hide_viewport = True


def get_collection_pivot(collection):
    """Restituisce il pivot di una EZ Collection se esiste"""
    if "ez_pivot" not in collection:
        return None
    return bpy.data.objects.get(collection["ez_pivot"])


def is_ez_collection(collection):
    """Verifica se una collection è una EZ Collection"""
    return "ez_pivot" in collection


def create_smart_pivot(collection_name, location, is_parent=False):
    """Crea un pivot icosphere con proprietà avanzate"""
    mesh = bpy.data.meshes.new(f"PivotMesh_{collection_name}")
    bm = bmesh.new()
    
    radius = 0.08 if is_parent else 0.05
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=radius)
    bm.to_mesh(mesh)
    bm.free()
    
    pivot = bpy.data.objects.new(f"Pivot_{collection_name}", mesh)
    pivot.location = location
    
    # Proprietà visualizzazione
    pivot.display_type = 'SOLID'
    pivot.show_in_front = True
    pivot.hide_render = True
    
    if is_parent:
        pivot.show_name = True
        pivot.color = (1, 0.5, 0, 1)
    
    # Material con colore
    mat = bpy.data.materials.new(name=f"PivotMat_{collection_name}")
    mat.use_nodes = True
    
    if is_parent:
        random_color = (1.0, 0.5, 0.1, 1.0)
    else:
        random_color = (
            random.uniform(0.3, 1.0),
            random.uniform(0.3, 1.0), 
            random.uniform(0.3, 1.0),
            1.0
        )
    
    principled = mat.node_tree.nodes["Principled BSDF"]
    principled.inputs["Base Color"].default_value = random_color
    principled.inputs["Roughness"].default_value = 0.2
    principled.inputs["Emission Color"].default_value = random_color
    principled.inputs["Emission Strength"].default_value = 0.5 if is_parent else 0.3
    
    pivot.data.materials.append(mat)
    return pivot


def preserve_parent_hierarchy(objects, new_parent):
    """Sistema di parenting che preserva le gerarchie esistenti"""
    root_objects = []
    for obj in objects:
        if obj.parent is None or obj.parent not in objects:
            root_objects.append(obj)
    
    bpy.ops.object.select_all(action='DESELECT')
    new_parent.select_set(True)
    
    for obj in root_objects:
        obj.select_set(True)
    
    if root_objects:
        bpy.context.view_layer.objects.active = new_parent
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    
    return root_objects


def generate_unique_name(base_name, existing_names):
    """Genera un nome univoco basato su un nome base"""
    name = base_name
    counter = 1
    while name in existing_names:
        name = f"{base_name}_{counter}"
        counter += 1
    return name


def get_collection_hierarchy(obj):
    """Restituisce tutta la gerarchia di EZCollections per un oggetto"""
    hierarchy = []
    
    for col in obj.users_collection:
        if is_ez_collection(col):
            hierarchy.append(col)
            
            # Trova collection padre ricorsivamente
            def find_parent_collections(child_col):
                for parent_col in bpy.data.collections:
                    if child_col in parent_col.children and is_ez_collection(parent_col):
                        hierarchy.append(parent_col)
                        find_parent_collections(parent_col)  # Continua ricorsivamente
            
            find_parent_collections(col)
    
    return hierarchy


# -----------------------------------
# Timer per Selection Handler - SOLUZIONE AFFIDABILE
# -----------------------------------
def selection_timer():
    """Timer che controlla i cambiamenti di selezione ogni 100ms"""
    global _last_selected
    
    try:
        current_selected = set(obj.name for obj in bpy.context.selected_objects if obj)
        
        if current_selected != _last_selected:
            _last_selected = current_selected.copy()
            
            if not current_selected:
                hide_all_pivots()
                return 0.1
            
            # Nascondi tutti i pivot
            hide_all_pivots()
            
            # Mostra pivot della gerarchia per ogni oggetto selezionato
            shown_collections = set()
            for obj_name in current_selected:
                obj = bpy.data.objects.get(obj_name)
                if obj:
                    hierarchy = get_collection_hierarchy(obj)
                    for col in hierarchy:
                        if col not in shown_collections:
                            pivot = get_collection_pivot(col)
                            if pivot:
                                pivot.hide_viewport = False
                                shown_collections.add(col)
        
        return 0.1  # Ripeti ogni 100ms
    except:
        return 0.1


# -----------------------------------
# Outliner: Shift+Ctrl+Click
# -----------------------------------
class OUTLINER_OT_ez_select_collection(Operator):
    bl_idname = "outliner.ez_select_collection"
    bl_label = "EZ Select Collection Contents"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        alc = context.view_layer.active_layer_collection
        if not alc:
            self.report({'WARNING'}, "No active collection in Outliner.")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        for obj in alc.collection.objects:
            if obj.type != 'EMPTY' or not obj.name.startswith("Pivot_"):
                obj.select_set(True)

        if alc.collection.objects:
            non_pivot_objects = [obj for obj in alc.collection.objects 
                                if obj.type != 'EMPTY' or not obj.name.startswith("Pivot_")]
            if non_pivot_objects:
                context.view_layer.objects.active = non_pivot_objects[0]

        return {'FINISHED'}


# -----------------------------------
# Create EZ Collection
# -----------------------------------
class OBJECT_OT_ez_create_collection(Operator):
    bl_idname = "object.ez_create_collection"
    bl_label = "Create EZ Collection"
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

        suffix = self.collection_suffix.strip()
        if not suffix:
            self.report({'ERROR'}, "Collection name cannot be empty.")
            return {'CANCELLED'}

        base_name = f"COL_{suffix}"
        existing_names = [c.name for c in bpy.data.collections]
        collection_name = generate_unique_name(base_name, existing_names)

        col = bpy.data.collections.new(collection_name)
        col.color_tag = 'COLOR_02'
        context.scene.collection.children.link(col)

        for obj in objs:
            for parent_col in obj.users_collection:
                parent_col.objects.unlink(obj)
            col.objects.link(obj)

        center = sum((obj.matrix_world.translation for obj in objs), 
                     Vector()) / len(objs)

        pivot = create_smart_pivot(collection_name, center, is_parent=False)
        col.objects.link(pivot)

        preserve_parent_hierarchy(objs, pivot)
        col["ez_pivot"] = pivot.name

        hide_all_pivots()
        pivot.hide_viewport = False

        bpy.ops.object.select_all(action='DESELECT')
        pivot.select_set(True)
        context.view_layer.objects.active = pivot

        self.report({'INFO'}, f"Collection '{collection_name}' created with smart pivot.")
        return {'FINISHED'}


# -----------------------------------
# Add to EZ Collection
# -----------------------------------
class OBJECT_OT_ez_add_to_collection(Operator):
    bl_idname = "object.ez_add_to_collection"
    bl_label = "Add to EZ Collection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        alc = context.view_layer.active_layer_collection
        if not alc or not is_ez_collection(alc.collection):
            self.report({'ERROR'}, "Active collection is not an EZCollection.")
            return {'CANCELLED'}

        col = alc.collection
        pivot = get_collection_pivot(col)
        if not pivot:
            self.report({'ERROR'}, "Pivot not found.")
            return {'CANCELLED'}

        selected_objects = [obj for obj in context.selected_objects if obj != pivot]
        if not selected_objects:
            self.report({'WARNING'}, "No valid objects selected.")
            return {'CANCELLED'}

        for obj in selected_objects:
            if obj.name not in col.objects:
                for parent_col in obj.users_collection:
                    if parent_col != col:
                        parent_col.objects.unlink(obj)
                col.objects.link(obj)

        preserve_parent_hierarchy(selected_objects, pivot)

        self.report({'INFO'}, f"{len(selected_objects)} object(s) added to '{col.name}'.")
        return {'FINISHED'}


# -----------------------------------
# Remove from EZ Collection
# -----------------------------------
class OBJECT_OT_ez_remove_from_collection(Operator):
    bl_idname = "object.ez_remove_from_collection"
    bl_label = "Remove from EZ Collection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        alc = context.view_layer.active_layer_collection
        if not alc or not is_ez_collection(alc.collection):
            self.report({'ERROR'}, "Active collection is not an EZCollection.")
            return {'CANCELLED'}

        col = alc.collection
        pivot = get_collection_pivot(col)
        selected_objects = [obj for obj in context.selected_objects if obj != pivot]
        
        if not selected_objects:
            self.report({'WARNING'}, "No valid objects selected.")
            return {'CANCELLED'}

        for obj in selected_objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

            if obj.name in col.objects:
                col.objects.unlink(obj)

            if obj.name not in context.scene.collection.objects:
                context.scene.collection.objects.link(obj)

        self.report({'INFO'}, f"{len(selected_objects)} object(s) removed from '{col.name}'.")
        return {'FINISHED'}


# -----------------------------------
# Pivot Lock/Unlock
# -----------------------------------
class OBJECT_OT_ez_pivot_unlock(Operator):
    bl_idname = "object.ez_pivot_unlock"
    bl_label = "Unlock Pivot"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        alc = context.view_layer.active_layer_collection
        if not alc or not is_ez_collection(alc.collection):
            self.report({'ERROR'}, "Active collection is not an EZCollection.")
            return {'CANCELLED'}

        pivot = get_collection_pivot(alc.collection)
        if not pivot:
            self.report({'ERROR'}, "Pivot not found.")
            return {'CANCELLED'}

        children = [obj for obj in alc.collection.objects if obj.parent == pivot]

        bpy.ops.object.select_all(action='DESELECT')
        for obj in children:
            obj.select_set(True)

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
    bl_label = "Lock Pivot"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        alc = context.view_layer.active_layer_collection
        if not alc or not is_ez_collection(alc.collection):
            self.report({'ERROR'}, "Active collection is not an EZCollection.")
            return {'CANCELLED'}

        pivot = get_collection_pivot(alc.collection)
        if not pivot:
            self.report({'ERROR'}, "Pivot not found.")
            return {'CANCELLED'}

        collection_objects = [obj for obj in alc.collection.objects if obj != pivot]

        preserve_parent_hierarchy(collection_objects, pivot)

        self.report({'INFO'}, f"Pivot '{pivot.name}' locked.")
        return {'FINISHED'}


# -----------------------------------
# Solo Toggle
# -----------------------------------
class OBJECT_OT_ez_toggle_solo_collection(Operator):
    bl_idname = "object.ez_toggle_solo_collection"
    bl_label = "Toggle Solo View"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        alc = context.view_layer.active_layer_collection
        if not alc or not is_ez_collection(alc.collection):
            self.report({'ERROR'}, "Active collection is not an EZCollection.")
            return {'CANCELLED'}

        col = alc.collection
        backup_key = "ez_solo_backup"

        if backup_key not in context.scene:
            backup = {c.name: c.hide_viewport for c in bpy.data.collections}
            context.scene[backup_key] = backup

            for collection in bpy.data.collections:
                set_visibility(collection, collection == col)

            self.report({'INFO'}, f"Solo view ON for '{col.name}'.")
        else:
            backup = context.scene[backup_key]
            for name, was_hidden in backup.items():
                collection = bpy.data.collections.get(name)
                if collection:
                    collection.hide_viewport = was_hidden

            del context.scene[backup_key]
            self.report({'INFO'}, "Solo view OFF. Restored previous state.")

        return {'FINISHED'}


# -----------------------------------
# Merge EZ Collections
# -----------------------------------
class OBJECT_OT_ez_merge_collections(Operator):
    bl_idname = "object.ez_merge_collections"
    bl_label = "Merge EZ Collections"
    bl_options = {'REGISTER', 'UNDO'}

    parent_collection_name: StringProperty(
        name="Parent Collection Name",
        description="Enter name for the parent collection (prefixed with 'COL_')",
        default=""
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "parent_collection_name")

    def execute(self, context):
        selected_collections = []
        
        for obj in context.selected_objects:
            for col in obj.users_collection:
                if is_ez_collection(col) and col not in selected_collections:
                    selected_collections.append(col)
        
        if not selected_collections:
            alc = context.view_layer.active_layer_collection
            if alc and is_ez_collection(alc.collection):
                selected_collections.append(alc.collection)

        if len(selected_collections) < 2:
            self.report({'ERROR'}, "Select objects from at least 2 EZCollections to merge them.")
            return {'CANCELLED'}

        parent_name = self.parent_collection_name.strip()
        if not parent_name:
            self.report({'ERROR'}, "Parent collection name cannot be empty.")
            return {'CANCELLED'}

        base_name = f"COL_{parent_name}"
        existing_names = [c.name for c in bpy.data.collections]
        parent_collection_name = generate_unique_name(base_name, existing_names)

        parent_col = bpy.data.collections.new(parent_collection_name)
        parent_col.color_tag = 'COLOR_01'
        context.scene.collection.children.link(parent_col)

        pivot_locations = []
        for col in selected_collections:
            pivot = get_collection_pivot(col)
            if pivot:
                pivot_locations.append(pivot.matrix_world.translation)

        if not pivot_locations:
            self.report({'ERROR'}, "No valid pivots found in selected EZCollections.")
            return {'CANCELLED'}

        parent_center = sum(pivot_locations, Vector()) / len(pivot_locations)

        parent_pivot = create_smart_pivot(parent_collection_name, parent_center, is_parent=True)
        parent_col.objects.link(parent_pivot)

        for col in selected_collections:
            if col.name in context.scene.collection.children:
                context.scene.collection.children.unlink(col)
            
            parent_col.children.link(col)

            child_pivot = get_collection_pivot(col)
            if child_pivot:
                bpy.ops.object.select_all(action='DESELECT')
                parent_pivot.select_set(True)
                child_pivot.select_set(True)
                context.view_layer.objects.active = parent_pivot
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        parent_col["ez_pivot"] = parent_pivot.name

        hide_all_pivots()
        parent_pivot.hide_viewport = False

        bpy.ops.object.select_all(action='DESELECT')
        parent_pivot.select_set(True)
        context.view_layer.objects.active = parent_pivot

        self.report({'INFO'}, f"Merged {len(selected_collections)} EZCollections into '{parent_collection_name}'.")
        return {'FINISHED'}


# -----------------------------------
# Unmerge EZ Collections
# -----------------------------------
class OBJECT_OT_ez_unmerge_collections(Operator):
    bl_idname = "object.ez_unmerge_collections"
    bl_label = "Unmerge EZ Collections"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        alc = context.view_layer.active_layer_collection
        if not alc or not is_ez_collection(alc.collection):
            self.report({'ERROR'}, "Active collection is not an EZCollection.")
            return {'CANCELLED'}

        parent_col = alc.collection
        child_collections = [col for col in parent_col.children if is_ez_collection(col)]
        
        if not child_collections:
            self.report({'WARNING'}, "No child EZCollections found to unmerge.")
            return {'CANCELLED'}

        for col in child_collections:
            child_pivot = get_collection_pivot(col)
            if child_pivot and child_pivot.parent:
                bpy.ops.object.select_all(action='DESELECT')
                child_pivot.select_set(True)
                context.view_layer.objects.active = child_pivot
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

            parent_col.children.unlink(col)
            context.scene.collection.children.link(col)

        self.report({'INFO'}, f"Unmerged {len(child_collections)} EZCollections from '{parent_col.name}'.")
        return {'FINISHED'}


# -----------------------------------
# Pie Menu COMPLETO
# -----------------------------------
class VIEW3D_MT_ez_collections_pie(Menu):
    bl_idname = "VIEW3D_MT_ez_collections_pie"
    bl_label = "EZ Collections"

    def draw(self, context):
        pie = self.layout.menu_pie()

        pie.operator("object.ez_add_to_collection", text="Add", icon='PLUS')
        pie.operator("object.ez_remove_from_collection", text="Remove", icon='REMOVE')
        pie.operator("object.ez_create_collection", text="Create", icon='GROUP')
        pie.operator("object.ez_toggle_solo_collection", text="Solo", icon='RESTRICT_VIEW_ON')
        pie.operator("object.ez_pivot_lock", text="Lock Pivot", icon='LOCKED')
        pie.operator("object.ez_pivot_unlock", text="Unlock Pivot", icon='UNLOCKED')
        pie.operator("object.ez_merge_collections", text="Merge Collections", icon='OUTLINER_COLLECTION')
        pie.operator("object.ez_unmerge_collections", text="Unmerge Collections", icon='OUTLINER_OB_GROUP_INSTANCE')


classes = [
    OUTLINER_OT_ez_select_collection,
    OBJECT_OT_ez_create_collection,
    OBJECT_OT_ez_add_to_collection,
    OBJECT_OT_ez_remove_from_collection,
    OBJECT_OT_ez_pivot_unlock,
    OBJECT_OT_ez_pivot_lock,
    OBJECT_OT_ez_toggle_solo_collection,
    OBJECT_OT_ez_merge_collections,
    OBJECT_OT_ez_unmerge_collections,
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
    kmi2 = km2.keymap_items.new(OUTLINER_OT_ez_select_collection.bl_idname, 
                                'LEFTMOUSE', 'PRESS', ctrl=True, shift=True)
    addon_keymaps.append((km2, kmi2))
    
    # REGISTRA IL TIMER per la gestione selezione
    bpy.app.timers.register(selection_timer)


def unregister():
    # RIMUOVI IL TIMER
    if bpy.app.timers.is_registered(selection_timer):
        bpy.app.timers.unregister(selection_timer)
        
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
