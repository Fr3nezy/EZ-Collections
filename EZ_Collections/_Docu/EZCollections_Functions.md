# EZCollections Addon - Complete Function Reference

## Overview
EZCollections is a Blender addon (version 4.0) that provides simplified collection management with customizable naming and creation options, implementing a Maya-style workflow for basic collection operations.

**Author**: Lex & Manu
**Blender Version**: 4.0.0+
**Activation**: Pie Menu (Ctrl+G) & N-Panel (View3D > EZ Collections)

## Core Architecture

### EZCollection Class
Simplified wrapper class for Blender collections with basic management functionality.

**Key Methods:**
- `__init__(bl_collection)`: Initializes EZ collection wrapper
- `is_valid()`: Validates if collection still exists
- `all_objects`: Property returning all objects in collection (including nested collections)
- `cleanup_invalid_instances()`: Class method to remove invalid cached instances

## Addon Preferences

### EZCollectionsPreferences Class
Global addon preferences accessible via Edit → Preferences → Add-ons → EZCollections.

**Properties:**
- `collection_prefix`: String prefix added to collection names (default: "")
- `collection_suffix`: String suffix added to collection names (default: "")
- `collection_color_tag`: Enum selector for default collection color tag (default: `NONE`). Uses Blender's built-in color tags: `NONE`, `COLOR_01` (Red), `COLOR_02` (Orange), `COLOR_03` (Yellow), `COLOR_04` (Green), `COLOR_05` (Teal), `COLOR_06` (Blue), `COLOR_07` (Violet), `COLOR_08` (Pink)
- `create_in_active_collection`: Boolean toggle for creation mode (default: False)

## Operators

### Collection Management

#### OBJECT_OT_ez_create_collection
**ID**: `object.ez_create_collection`
**Label**: Create EZ Collection
**Function**: Creates new EZ collection from selected objects with advanced naming and placement
- Applies prefix/suffix from addon preferences
- Sets collection color from preferences
- Places collection based on creation mode setting:
  - **Root Mode**: Creates at scene root level
  - **Active Collection Mode**: Creates as child of currently active collection
- Moves objects from current collections to new one
- Supports nested collection creation

#### OBJECT_OT_ez_add_to_collection
**ID**: `object.ez_add_to_collection`
**Label**: Add to EZ Collection
**Function**: Adds selected objects to active EZ collection
- Checks for duplicates to prevent double-linking
- Works with nested collection hierarchies

#### OBJECT_OT_ez_remove_from_collection
**ID**: `object.ez_remove_from_collection`
**Label**: Remove from EZ Collection
**Function**: Removes selected objects from their EZ collection
- Safely unlinks objects from collection
- Preserves object existence and other collection memberships

#### OBJECT_OT_ez_toggle_solo_collection
**ID**: `object.ez_toggle_solo_collection`
**Label**: Solo Toggle
**Function**: Toggles solo mode for active collection
- Hides/shows other collections for focused workflow
- Preserves scene organization

## Utility Functions

### Collection Detection
- `get_active_ez_collection()`: Finds EZ collection from active/selected objects
- `get_ez_collection_from_object(obj)`: Gets EZ collection containing specific object

### General Utilities
- `set_collection_visibility(collection, visible)`: Sets viewport/render visibility

## UI Components

### N-Panel (VIEW3D_PT_ez_collections_panel)
**Location**: View3D → Sidebar (N) → EZ Collections
**Sections**:
- **Collection Naming**: Prefix/suffix controls with live preview
- **Collection Appearance**: Color tag selector (9 options: None + 8 Blender built-in color tags)
- **Creation Mode**: Toggle between root and active collection placement

### Pie Menu (VIEW3D_MT_ez_collections_pie)
**Shortcut**: Ctrl+G
**Layout**: 4-sector pie menu
- Add to Collection
- Remove from Collection
- Create Collection
- Solo Toggle

## Key Features

### Advanced Collection Naming
- Customizable prefixes and suffixes via addon preferences
- Live preview of final collection names in N-panel
- Persistent settings saved with Blender preferences

### Flexible Collection Creation
- **Root Creation**: Collections created at scene hierarchy root
- **Active Collection Creation**: Collections created as children of active collection
- Automatic color application from preferences

### Smart Collection Detection
- Automatic detection of EZ collections from selected objects
- Fallback to active object when no selection exists
- Support for nested collection hierarchies

### Performance Optimizations
- Instance caching for collections
- Automatic cleanup of invalid references
- Efficient object iteration with nested collection support

### Maya-Style Workflow
- Collection-based operations instead of individual objects
- Quick access via pie menu and N-panel
- Non-destructive object management
- Streamlined workflow for collection organization

## Data Structure

### Custom Properties
- Collections: `"ez_collection": True`

### Global Variables
- `addon_keymaps`: List of registered keymaps

## Dependencies
- `bpy`: Blender Python API
- `bpy.props`: For operator properties and addon preferences
- `bpy.types`: For Blender type definitions and UI components
