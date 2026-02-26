"""Core module for EZCollections"""

from .collection import EZCollection
from .utils import (
    get_active_ez_collection,
    get_ez_collection_from_object,
    set_collection_visibility,
)
from .pivot import (
    has_pivot,
    get_pivot_position,
    set_pivot_position,
    remove_pivot,
    get_pivot_color,
    compute_bounding_box_center,
    compute_bounding_box_bottom,
    compute_bounding_box_top,
)

__all__ = [
    'EZCollection',
    'get_active_ez_collection',
    'get_ez_collection_from_object',
    'set_collection_visibility',
    'has_pivot',
    'get_pivot_position',
    'set_pivot_position',
    'remove_pivot',
    'get_pivot_color',
    'compute_bounding_box_center',
    'compute_bounding_box_bottom',
    'compute_bounding_box_top',
]


def register():
    """Register core components"""
    pass


def unregister():
    """Unregister core components"""
    EZCollection.cleanup_invalid_instances()
