"""Core module for EZCollections"""

from .collection import EZCollection
from .utils import (
    get_active_ez_collection,
    get_ez_collection_from_object,
    set_collection_visibility,
)

__all__ = [
    'EZCollection',
    'get_active_ez_collection',
    'get_ez_collection_from_object',
    'set_collection_visibility',
]


def register():
    """Register core components"""
    pass


def unregister():
    """Unregister core components"""
    EZCollection.cleanup_invalid_instances()
