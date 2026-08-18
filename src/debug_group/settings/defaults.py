"""Default debug group settings."""

# ---> Local imports <--- #
from .types import DebugGroupConfigType, FinalDebugSettingsType


DEFAULT_GROUP_CONFIG: DebugGroupConfigType = {
  'is_on': False,
  'fore_color': 'default',
  'back_color': 'default',
  'style': None,
  'indentation_fore_color': 'default',
  'indentation_back_color': 'default',
  'indentation_style': None
}

DEFAULT_DEBUG_SETTINGS: FinalDebugSettingsType[str] = {
  'max_chars_per_line': 100,
  'debugs_on': [],
  'group_configs': {}
}
