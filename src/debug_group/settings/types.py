"""Debug group settings types."""

# ---> Standard library imports <--- #
from typing import TypedDict

# ---> Third party imports <--- #
from escansi import FormatNameType


# IMPORTANT: Whatever you add to one, add to the other ->
class DebugGroupConfigType(TypedDict, total = False):
  """Debug group configuration type."""
  is_on: bool
  fore_color: str | tuple[int, int, int] | int
  back_color: str | tuple[int, int, int] | int
  style: None | FormatNameType | tuple[FormatNameType, ...]
  indentation_fore_color: str | tuple[int, int, int] | int
  indentation_back_color: str | tuple[int, int, int] | int
  indentation_style: None | FormatNameType | tuple[FormatNameType, ...]

class FinalDebugGroupConfigType(TypedDict):
  """Final debug group configuration type."""
  is_on: bool
  fore_color: str | tuple[int, int, int] | int
  back_color: str | tuple[int, int, int] | int
  style: None | FormatNameType | tuple[FormatNameType, ...]
  indentation_fore_color: str | tuple[int, int, int] | int
  indentation_back_color: str | tuple[int, int, int] | int
  indentation_style: None | FormatNameType | tuple[FormatNameType, ...]
# <- IMPORTANT: Whatever you add to one, add to the other


# IMPORTANT: Whatever you add to one, add to the other ->
class DebugSettingsType[DebugGroupNameT: str](TypedDict, total = False):
  """Debug settings type."""
  max_chars_per_line: int
  debugs_on: list[DebugGroupNameT]
  group_configs: dict[DebugGroupNameT, DebugGroupConfigType | DebugGroupNameT]

class FinalDebugSettingsType[DebugGroupNameT: str](TypedDict):
  """Final debug settings type."""
  max_chars_per_line: int
  debugs_on: list[DebugGroupNameT]
  group_configs: dict[DebugGroupNameT, FinalDebugGroupConfigType]
# <- IMPORTANT: Whatever you add to one, add to the other
