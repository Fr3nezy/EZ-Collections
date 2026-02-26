bl_info = {
    "name": "EZCollections 3.0 - Operative Collections",
    "author": "Lex & Manu",
    "version": (3, 0, 0),
    "blender": (4, 0, 0),
    "location": "Pie Menu (Ctrl+G) & Object Menu",
    "description": "Collection operative con pivot e modifier condivisi + workflow Maya",
    "category": "Object",
}

import bpy
from mathutils import Vector
from bpy.props import EnumProperty, StringProperty, BoolProperty
from bpy.types import Menu, Operator
from bpy.app.handlers import persistent

addon_keymaps = []
_last_selected_objects = set()
_pivot_selection_lock = False  # Flag per permettere selezione pivot

# ----------------------------
# Core Systems
# ----------------------------

class EZPivotSystem:
    def __init__(self, ez_collection):
        self.ez_collection = ez_collection
        self.pivot = None

    def create_pivot(self, method="CENTROID", manual_loc=None):
        # Validazione collection prima di usarla
        if not self.ez_collection.is_valid():
            return
            
        col = self.ez_collection.bl_collection
        all_objects = self.ez_collection.all_objects
        
        if not all_objects:
            return
            
        if method == "CENTROID":
            pts = [obj.matrix_world.translation for obj in all_objects]
            loc = sum(pts, Vector()) / len(pts) if pts else Vector()
        elif method == "BBOX_CENTER":
            coords = []
            for obj in all_objects:
                coords.extend([obj.matrix_world @ Vector(v) for v in obj.bound_box])
            loc = sum(coords, Vector()) / len(coords) if coords else Vector()
        elif method == "MANUAL" and manual_loc:
            loc = Vector(manual_loc)
        else:
            loc = bpy.context.scene.cursor.location.copy()

        # Crea pivot stile Blender - sfera arancione
        self.pivot = bpy.data.objects.new(f"EZPivot_{col.name}", None)
        self.pivot.empty_display_type = 'SPHERE'
        self.pivot.empty_display_size = 0.15
        self.pivot.location = loc
        self.pivot.show_in_front = True
        self.pivot.color = (1.0, 0.647, 0.0, 1.0)  # Arancione Blender
        self.pivot["ez_pivot"] = True
        self.pivot["ez_collection"] = col.name
        
        # Link a collection dedicata per i pivot
        pivot_col = self._get_or_create_pivot_collection()
        pivot_col.objects.link(self.pivot)

        # Constraint system
        for obj in all_objects:
            c = obj.constraints.new('CHILD_OF')
            c.target = self.pivot
            c.use_location_x = c.use_location_y = c.use_location_z = True
            c.use_rotation_x = c.use_rotation_y = c.use_rotation_z = True
            c.use_scale_x = c.use_scale_y = c.use_scale_z = True

    def _get_or_create_pivot_collection(self):
        """Crea/ottiene collection dedicata per i pivot"""
        pivot_col_name = "EZ_Pivots"
        if pivot_col_name not in bpy.data.collections:
            pivot_col = bpy.data.collections.new(pivot_col_name)
            bpy.context.scene.collection.children.link(pivot_col)
        else:
            pivot_col = bpy.data.collections[pivot_col_name]
        return pivot_col

    def validate_pivot(self):
        """Controlla se il pivot esiste ancora"""
        if self.pivot and self.pivot.name not in bpy.data.objects:
            self.pivot = None
            return False
        return self.pivot is not None

    def lock_pivot(self):
        if self.validate_pivot():
            self.pivot.lock_location = [True, True, True]
            self.pivot.lock_rotation = [True, True, True] 
            self.pivot.lock_scale = [True, True, True]

    def unlock_pivot(self):
        if self.validate_pivot():
            self.pivot.lock_location = [False, False, False]
            self.pivot.lock_rotation = [False, False, False]
            self.pivot.lock_scale = [False, False, False]

class SharedModifierSystem:
    def __init__(self, ez_collection):
        self.ez_collection = ez_collection

    def create_shared_modifier(self, mod_type, name=None):
        if not self.ez_collection.is_valid():
            return None
            
        master = self._get_master()
        if not master:
            return None
        
        mod_name = name or f"EZShared_{mod_type}"
        base_mod = master.modifiers.new(mod_name, mod_type)
        
        # Propaga con driver
        for obj in self.ez_collection.all_objects:
            if obj is master:
                continue
            m = obj.modifiers.new(mod_name, mod_type)
            # Driver per proprietà principali
            self._create_drivers(base_mod, m, master)
        
        return base_mod

    def _create_drivers(self, source_mod, target_mod, master):
        """Crea driver per proprietà comuni"""
        common_props = {
            'BEVEL': ['width', 'segments'],
            'SUBSURF': ['levels', 'render_levels'],
            'ARRAY': ['count', 'relative_offset_displace'],
            'SOLIDIFY': ['thickness'],
            'MIRROR': ['use_axis']
        }
        
        mod_type = source_mod.type
        if mod_type in common_props:
            for prop in common_props[mod_type]:
                if hasattr(source_mod, prop) and hasattr(target_mod, prop):
                    try:
                        drv = target_mod.driver_add(prop).driver
                        var = drv.variables.new()
                        var.name = "src"
                        var.targets[0].id = master
                        var.targets[0].data_path = f'modifiers["{source_mod.name}"].{prop}'
                        drv.expression = "src"
                    except:
                        pass

    def _get_master(self):
        objs = self.ez_collection.all_objects
        return objs[0] if objs else None

class EZCollection:
    _instances = {}

    def __new__(cls, bl_collection):
        name = bl_collection.name
        if name in cls._instances:
            inst = cls._instances[name]
            # Verifica se l'istanza è ancora valida
            if inst.is_valid():
                return inst
            else:
                # Rimuovi istanza non valida
                del cls._instances[name]
        
        inst = super().__new__(cls)
        cls._instances[name] = inst
        return inst

    def __init__(self, bl_collection):
        if hasattr(self, "bl_collection"):
            return
        self.bl_collection = bl_collection
        self.pivot_system = EZPivotSystem(self)
        self.mod_sys = SharedModifierSystem(self)
        # Marca come EZ Collection
        bl_collection["ez_collection"] = True

    def is_valid(self):
        """Verifica se la collection esiste ancora"""
        try:
            if self.bl_collection.name not in bpy.data.collections:
                return False
            # Test di accesso per verificare se è valida
            _ = list(self.bl_collection.objects)
            return True
        except ReferenceError:
            return False

    @property
    def all_objects(self):
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
        """Rimuove istanze non valide dalla cache"""
        to_remove = []
        for name, inst in cls._instances.items():
            if not inst.is_valid():
                to_remove.append(name)
        for name in to_remove:
            del cls._instances[name]

# ----------------------------
# Utility Functions
# ----------------------------

def get_active_ez_collection():
    """Trova EZ collection dell'oggetto attivo - versione migliorata"""
    # Cleanup istanze non valide
    EZCollection.cleanup_invalid_instances()
    
    context = bpy.context
    obj = context.active_object
    
    if not obj:
        # Fallback: cerca tra oggetti selezionati
        for sel_obj in context.selected_objects:
            ez_col = get_ez_collection_from_object(sel_obj)
            if ez_col:
                return ez_col
        return None
    
    # Controlla collection dell'oggetto attivo
    return get_ez_collection_from_object(obj)

def get_ez_collection_from_object(obj):
    """Ottiene EZ collection da un oggetto specifico"""
    if not obj:
        return None
    for col in obj.users_collection:
        if col.get("ez_collection"):
            ez_col = EZCollection(col)
            if ez_col.is_valid():
                return ez_col
    return None

def hide_all_pivots():
    """Nasconde tutti i pivot EZ"""
    for obj in bpy.data.objects:
        if obj.get("ez_pivot"):
            obj.hide_viewport = True

def show_collection_pivot(ez_collection):
    """Mostra solo il pivot della collection specifica"""
    if ez_collection and ez_collection.is_valid() and ez_collection.pivot_system.validate_pivot():
        ez_collection.pivot_system.pivot.hide_viewport = False

def is_pivot_selected():
    """Verifica se è selezionato un pivot EZ"""
    for obj in bpy.context.selected_objects:
        if obj.get("ez_pivot"):
            return True
    return False

def update_pivot_visibility():
    """Aggiorna visibilità pivot basata su selezione"""
    global _pivot_selection_lock
    
    # Se un pivot è selezionato, non nascondere i pivot
    if is_pivot_selected():
        _pivot_selection_lock = True
        return
    
    _pivot_selection_lock = False
    hide_all_pivots()
    
    # Trova tutte le EZ collection degli oggetti selezionati
    shown_collections = set()
    for obj in bpy.context.selected_objects:
        ez_col = get_ez_collection_from_object(obj)
        if ez_col and ez_col not in shown_collections:
            show_collection_pivot(ez_col)
            shown_collections.add(ez_col)

def set_collection_visibility(collection, visible):
    """Imposta visibilità collection"""
    collection.hide_viewport = not visible
    collection.hide_render = not visible

# ----------------------------
# Selection Handler
# ----------------------------

@persistent
def selection_changed_handler(scene, depsgraph):
    """Handler per cambiamenti di selezione - aggiorna pivot visibility"""
    global _last_selected_objects
    
    try:
        current_selected = set(obj.name for obj in bpy.context.selected_objects if obj)
        
        if current_selected != _last_selected_objects:
            _last_selected_objects = current_selected.copy()
            update_pivot_visibility()
    except:
        pass

# ----------------------------
# Operators 
# ----------------------------

class OBJECT_OT_ez_create_collection(Operator):
    """Crea nuova collection operativa"""
    bl_idname = "object.ez_create_collection"
    bl_label = "Create EZ Collection"
    bl_options = {'REGISTER', 'UNDO'}

    collection_name: StringProperty(name="Name", default="EZ_Collection")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "collection_name")

    def execute(self, context):
        sel = context.selected_objects
        if not sel:
            self.report({'ERROR'}, "Select objects first")
            return {'CANCELLED'}

        # Crea collection
        col = bpy.data.collections.new(self.collection_name)
        context.scene.collection.children.link(col)
        
        # SPOSTA oggetti (non copia) - RIMUOVI dalle collection precedenti
        for obj in sel:
            # Rimuovi da tutte le collection precedenti
            for old_col in obj.users_collection:
                old_col.objects.unlink(obj)
            # Aggiungi alla nuova collection
            col.objects.link(obj)
        
        # Crea EZ wrapper
        ez_col = EZCollection(col)
        ez_col.pivot_system.create_pivot(method="CENTROID")
        
        # Aggiorna visibilità pivot
        update_pivot_visibility()
        
        self.report({'INFO'}, f"Created '{col.name}' with pivot")
        return {'FINISHED'}

class OBJECT_OT_ez_add_to_collection(Operator):
    """Aggiungi oggetti alla collection attiva"""
    bl_idname = "object.ez_add_to_collection"
    bl_label = "Add to EZ Collection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ez_col = get_active_ez_collection()
        if not ez_col:
            self.report({'ERROR'}, "No active EZ collection")
            return {'CANCELLED'}

        added = 0
        for obj in context.selected_objects:
            # Fix: usa obj.name invece di obj per il confronto
            if obj.name not in [o.name for o in ez_col.all_objects]:
                ez_col.bl_collection.objects.link(obj)
                # Aggiungi constraint se c'è pivot
                if ez_col.pivot_system.validate_pivot():
                    c = obj.constraints.new('CHILD_OF')
                    c.target = ez_col.pivot_system.pivot
                added += 1

        self.report({'INFO'}, f"Added {added} objects")
        return {'FINISHED'}

class OBJECT_OT_ez_remove_from_collection(Operator):
    """Rimuovi oggetti dalla collection"""
    bl_idname = "object.ez_remove_from_collection"
    bl_label = "Remove from EZ Collection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ez_col = get_active_ez_collection()
        if not ez_col:
            self.report({'ERROR'}, "No active EZ collection")
            return {'CANCELLED'}

        removed = 0
        for obj in context.selected_objects:
            # Fix: usa obj.name invece di obj per il confronto
            if obj.name in [o.name for o in ez_col.bl_collection.objects]:
                ez_col.bl_collection.objects.unlink(obj)
                # Rimuovi constraint pivot
                if ez_col.pivot_system.validate_pivot():
                    for c in obj.constraints:
                        if (c.type == 'CHILD_OF' and 
                            c.target == ez_col.pivot_system.pivot):
                            obj.constraints.remove(c)
                removed += 1

        update_pivot_visibility()
        self.report({'INFO'}, f"Removed {removed} objects")
        return {'FINISHED'}

class OBJECT_OT_ez_pivot_lock(Operator):
    """Blocca pivot collection"""
    bl_idname = "object.ez_pivot_lock"
    bl_label = "Lock Pivot"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ez_col = get_active_ez_collection()
        if not ez_col:
            self.report({'ERROR'}, "No active EZ collection")
            return {'CANCELLED'}
        
        if not ez_col.pivot_system.validate_pivot():
            self.report({'ERROR'}, "Collection pivot not found")
            return {'CANCELLED'}
        
        ez_col.pivot_system.lock_pivot()
        self.report({'INFO'}, "Pivot locked")
        return {'FINISHED'}

class OBJECT_OT_ez_pivot_unlock(Operator):
    """Sblocca pivot collection"""
    bl_idname = "object.ez_pivot_unlock"
    bl_label = "Unlock Pivot"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ez_col = get_active_ez_collection()
        if not ez_col:
            self.report({'ERROR'}, "No active EZ collection")
            return {'CANCELLED'}
        
        if not ez_col.pivot_system.validate_pivot():
            self.report({'ERROR'}, "Collection pivot not found")
            return {'CANCELLED'}
        
        ez_col.pivot_system.unlock_pivot()
        self.report({'INFO'}, "Pivot unlocked")
        return {'FINISHED'}

class OBJECT_OT_ez_toggle_solo_collection(Operator):
    """Toggle solo mode per collection"""
    bl_idname = "object.ez_toggle_solo_collection"
    bl_label = "Solo Toggle"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ez_col = get_active_ez_collection()
        if not ez_col:
            self.report({'ERROR'}, "No active EZ collection")
            return {'CANCELLED'}

        col = ez_col.bl_collection
        is_visible = not col.hide_viewport
        
        if is_visible:
            # Nascondi tutte le altre collection (tranne pivot)
            for other_col in bpy.data.collections:
                if other_col != col and other_col.name != "EZ_Pivots":
                    set_collection_visibility(other_col, False)
            self.report({'INFO'}, f"Solo mode: {col.name}")
        else:
            # Mostra tutte (tranne pivot che rimangono gestiti dall'handler)
            for other_col in bpy.data.collections:
                if other_col.name != "EZ_Pivots":
                    set_collection_visibility(other_col, True)
            self.report({'INFO'}, "Solo mode off")
        
        return {'FINISHED'}

class OBJECT_OT_ez_add_shared_modifier(Operator):
    """Aggiungi modifier condiviso"""
    bl_idname = "object.ez_add_shared_modifier"
    bl_label = "Add Shared Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    modifier_type: EnumProperty(
        name="Modifier",
        items=[
            ('BEVEL', 'Bevel', 'Shared bevel modifier'),
            ('SUBSURF', 'Subdivision Surface', 'Shared subdivision'),
            ('ARRAY', 'Array', 'Shared array modifier'),
            ('SOLIDIFY', 'Solidify', 'Shared solidify'),
            ('MIRROR', 'Mirror', 'Shared mirror modifier'),
        ],
        default='BEVEL'
    )

    def execute(self, context):
        # Versione migliorata per trovare collection attiva
        ez_col = get_active_ez_collection()
        
        if not ez_col:
            # Fallback: cerca tra tutti gli oggetti selezionati
            for obj in context.selected_objects:
                ez_col = get_ez_collection_from_object(obj)
                if ez_col:
                    break
        
        if not ez_col:
            self.report({'ERROR'}, "Select an object from an EZ collection")
            return {'CANCELLED'}

        all_objects = ez_col.all_objects
        if not all_objects:
            self.report({'ERROR'}, "EZ collection has no objects")
            return {'CANCELLED'}

        mod = ez_col.mod_sys.create_shared_modifier(self.modifier_type)
        if mod:
            self.report({'INFO'}, f"Added shared {self.modifier_type} to {ez_col.bl_collection.name}")
        else:
            self.report({'ERROR'}, "Failed to create shared modifier")
        return {'FINISHED'}

class OBJECT_OT_ez_merge_collections(Operator):
    """Unisci collection selezionate"""
    bl_idname = "object.ez_merge_collections"
    bl_label = "Merge Collections"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.report({'INFO'}, "Merge collections - Feature coming soon")
        return {'FINISHED'}

# ----------------------------
# Pie Menu
# ----------------------------

class VIEW3D_MT_ez_collections_pie(Menu):
    bl_idname = "VIEW3D_MT_ez_collections_pie"
    bl_label = "EZ Collections 3.0"

    def draw(self, context):
        pie = self.layout.menu_pie()
        
        # Disposizione a 8 settori
        pie.operator("object.ez_add_to_collection", text="Add", icon='ADD')
        pie.operator("object.ez_remove_from_collection", text="Remove", icon='REMOVE')
        pie.operator("object.ez_create_collection", text="Create", icon='OUTLINER_COLLECTION')
        pie.operator("object.ez_toggle_solo_collection", text="Solo", icon='RESTRICT_VIEW_ON')
        pie.operator("object.ez_pivot_lock", text="Lock Pivot", icon='LOCKED')
        pie.operator("object.ez_pivot_unlock", text="Unlock Pivot", icon='UNLOCKED')
        pie.operator("object.ez_add_shared_modifier", text="Shared Modifier", icon='MODIFIER')
        pie.operator("object.ez_merge_collections", text="Merge", icon='OUTLINER_OB_GROUP_INSTANCE')

# ----------------------------
# Registration
# ----------------------------

classes = [
    OBJECT_OT_ez_create_collection,
    OBJECT_OT_ez_add_to_collection,
    OBJECT_OT_ez_remove_from_collection,
    OBJECT_OT_ez_pivot_lock,
    OBJECT_OT_ez_pivot_unlock,
    OBJECT_OT_ez_toggle_solo_collection,
    OBJECT_OT_ez_add_shared_modifier,
    OBJECT_OT_ez_merge_collections,
    VIEW3D_MT_ez_collections_pie,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Keymap Ctrl+G per pie menu
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name="Object Mode", space_type='EMPTY')
    kmi = km.keymap_items.new("wm.call_menu_pie", 'G', 'PRESS', ctrl=True)
    kmi.properties.name = VIEW3D_MT_ez_collections_pie.bl_idname
    addon_keymaps.append((km, kmi))
    
    # Registra handler per selezione
    if selection_changed_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(selection_changed_handler)

def unregister():
    # Rimuovi handler
    if selection_changed_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(selection_changed_handler)
    
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
