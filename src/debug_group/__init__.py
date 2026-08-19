"""DebugGroup package."""

# ---> Local imports <--- #
from .debug_manager import DebugManager as DebugManager
from .settings import DebugSettingsType as DebugSettingsType


DebugGroup = DebugManager.DebugGroup


__all__ = [
  'DebugGroup',
  'DebugManager',
  'DebugSettingsType'
]
