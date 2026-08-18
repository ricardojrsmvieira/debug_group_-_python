"""DebugManager module for managing debug settings."""


# ---> Standard library imports <--- #
import json
from collections.abc import Sequence
from functools import cached_property
from typing import Any, ClassVar, Self, get_args, override

# ---> Third party imports <--- #
from escansi import back_color, fore_color, format_text, reset_formats
from pydantic import BaseModel

# ---> Local imports <--- #
from .constants import (
  AFTER_GROUP_INDENTATION_TEXT,
  INDIVIDUAL_GROUP_INDENTATION_TEXT,
  INIT_PRINT_INDENTATION_TEXT,
  INTERNAL_GROUP_INDENTATION_TEXT,
  PARAGRAPH_INDENTATION_TEXT,
)
from .settings.defaults import DEFAULT_DEBUG_SETTINGS, DEFAULT_GROUP_CONFIG
from .settings.types import (
  DebugGroupConfigType,
  DebugSettingsType,
  FinalDebugGroupConfigType,
  FinalDebugSettingsType,
)
from .utils import deep_parse_json_to_obj


####################################################################################################
#                                                                                                  #
#                                          DEBUG MANAGER                                           #
#                                                                                                  #
####################################################################################################
class DebugManager[DebugGroupNameT: str = str](BaseModel):
  """DebugManager class for managing debug settings."""
  #region Model Config + Class Variables
  _instance: ClassVar['DebugManager[str] | None'] = None
  current_groups: ClassVar['list[DebugManager.DebugGroup[str]]'] = []
  current_level: ClassVar[int] = 0
  #endregion Model Config + Class Variables


  #region Instance Fields + Properties
  #endregion Instance Fields + Properties


  #region Init Subclass + Abstract Methods
  @override
  def __init_subclass__(cls, **kwargs: Any) -> None:
    cls.DEBUG_SETTINGS: FinalDebugSettingsType[DebugGroupNameT] = DEFAULT_DEBUG_SETTINGS.copy() # pyright: ignore[reportAttributeAccessIssue]
    # Indeed we want to pass a str that's not in the DebugGroupNameT, since this is a special case
    cls.NONE_DEBUG_GROUP: DebugManager.NoneDebugGroup[DebugGroupNameT] = (
      DebugManager.NoneDebugGroup[DebugGroupNameT](name = 'None',
                                                   group_name = '__NONE_CATEGORY_DG__', # pyright: ignore[reportArgumentType]
                                                   debug_manager_settings = cls.DEBUG_SETTINGS,
                                                   none_debug_group = None) # pyright: ignore[reportArgumentType]
    )
    cls.MyDebugGroup = cls.DebugGroup[DebugGroupNameT]
    super().__init_subclass__(**kwargs)
  #endregion Init Subclass + Abstract Methods


  #region Class + Static Methods
  #region _Internal Helper Methods
  #endregion _Internal Helper Methods

  #region Normal Methods
  #endregion Normal Methods

  #region Custom Tool Methods
  #endregion Custom Tool Methods
  #endregion Class + Static Methods


  #region New + Init + Post Init + Validators Methods
  @override
  def __new__(cls, configs: DebugSettingsType[DebugGroupNameT]) -> Self:  # noqa: C901, PLR0912
    if cls._instance is not None:
      return cls._instance # pyright: ignore[reportReturnType] # We know here is no longer None

    # This happens when the class if is being initialized without any subclassing, so we need to set
    # the class variables here, since __init_subclass__ is not called in this case.
    if not getattr(cls, 'DEBUG_SETTINGS', None):
      cls.DEBUG_SETTINGS: FinalDebugSettingsType[DebugGroupNameT] = DEFAULT_DEBUG_SETTINGS.copy() # pyright: ignore[reportAttributeAccessIssue]
      cls.NONE_DEBUG_GROUP: DebugManager.NoneDebugGroup[DebugGroupNameT] = (
        DebugManager.NoneDebugGroup[DebugGroupNameT](name = 'None',
                                                     group_name = '__NONE_CATEGORY_DG__', # pyright: ignore[reportArgumentType]
                                                     debug_manager_settings = cls.DEBUG_SETTINGS,
                                                     none_debug_group = None) # pyright: ignore[reportArgumentType]
      )
      cls.MyDebugGroup = cls.DebugGroup[DebugGroupNameT]

    group_configs = configs.get('group_configs', {})

    type_args = cls.__pydantic_generic_metadata__['args']
    if (type_args and type_args[0] is not str):
      for group_name in get_args(type_args[0]):
        if group_name not in group_configs:
          group_configs[group_name] = DEFAULT_GROUP_CONFIG.copy()

      for group_name, group_config in group_configs.items():
        if isinstance(group_config, dict):
          group_configs[group_name] = { **DEFAULT_GROUP_CONFIG, **group_config }

      for group_name, group_config in group_configs.items():
        if isinstance(group_config, str):
          if group_config not in group_configs:
            msg = (f"Debug group '{group_name}' is configured as a copy of '{group_config}', "
                  f"but no configs were found for the latter. "
                  f"Please make sure all copies point to an existing group.")
            raise ValueError(msg)
          if isinstance(group_configs[group_config], str):
            msg = (f"Debug group '{group_name}' configs are configured as a copy of "
                  f"'{group_config}', but the latter is also configured as a copy. "
                  f"Please make sure all copies point to a non-copy group.")
            raise TypeError(msg)
          # We can safely copy the configs, since we know that the group it's copying from is not a
          # copy itself and has all the necessary configs (either default or user-defined)
          group_configs[group_name] = group_configs[group_config].copy() # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]

    group_configs_final: dict[DebugGroupNameT, FinalDebugGroupConfigType] = group_configs # pyright: ignore[reportAssignmentType]
    for group_name in configs.get('debugs_on', DEFAULT_DEBUG_SETTINGS['debugs_on']):
      if group_name not in group_configs_final:
        group_configs_final[group_name] = DEFAULT_GROUP_CONFIG.copy() # pyright: ignore[reportArgumentType]
      group_configs_final[group_name]['is_on'] = True # pyright: ignore[reportArgumentType]

    cls.DEBUG_SETTINGS['max_chars_per_line'] = configs.get('max_chars_per_line',
                                                           DEFAULT_DEBUG_SETTINGS['max_chars_per_line'])
    cls.DEBUG_SETTINGS['debugs_on'] = configs.get('debugs_on', DEFAULT_DEBUG_SETTINGS['debugs_on']) # pyright: ignore[reportGeneralTypeIssues]
    cls.DEBUG_SETTINGS['group_configs'] = group_configs_final

    cls._instance = super().__new__(cls) # pyright: ignore[reportAttributeAccessIssue] # We know we can
    # This way we guarantee that the instance is created only once, even if the class is subclassed
    DebugManager._instance = cls._instance
    return cls._instance # pyright: ignore[reportReturnType] # We know here is no longer None


  @override
  def __init__(self, configs: DebugSettingsType[DebugGroupNameT]) -> None:
    super().__init__(configs = configs)
  #endregion New + Init + Post Init + Validators Methods


  #region Instance Methods
  #region _Internal Helper Methods
  #endregion _Internal Helper Methods

  #region Normal Methods
  def new_group(
    self,
    name: str,
    group_name: DebugGroupNameT,
    config: DebugGroupConfigType | None = None
  ) -> 'DebugManager.DebugGroup[DebugGroupNameT]':
    """Create a new debug group with the provided name and configuration."""
    return DebugManager.DebugGroup[DebugGroupNameT](
      name,
      group_name,
      config,
      debug_manager_settings = self.DEBUG_SETTINGS,
      none_debug_group = self.NONE_DEBUG_GROUP
    )
  #endregion Normal Methods

  #region Custom Tool Methods
  #endregion Custom Tool Methods
  #endregion Instance Methods


  ##################################################################################################
  #                                          DEBUG GROUP                                           #
  ##################################################################################################
  class DebugGroup[T: str](BaseModel):
    """DebugGroup class for managing debug output with indentation and formatting."""
    #region Model Config + Class Variables
    #endregion Model Config + Class Variables


    #region Instance Fields + Properties
    name: str
    indentation: str
    config: FinalDebugGroupConfigType

    _max_chars_per_line: int
    _debugs_on: Sequence[T]
    #endregion Instance Fields + Properties


    #region Init Subclass + Abstract Methods
    #endregion Init Subclass + Abstract Methods


    #region Class + Static Methods
    #region _Internal Helper Methods
    #endregion _Internal Helper Methods

    #region Normal Methods
    #endregion Normal Methods

    #region Custom Tool Methods
    #endregion Custom Tool Methods
    #endregion Class + Static Methods


    #region New + Init + Post Init + Validators Methods
    @override
    def __new__(
      cls,
      name: str,
      group_name: T,
      config: DebugGroupConfigType | None = None,
      *,
      debug_manager_settings: FinalDebugSettingsType[T],
      none_debug_group: 'DebugManager.NoneDebugGroup[T]'
    ) -> 'Self | DebugManager.NoneDebugGroup[T]':
      group = debug_manager_settings['group_configs'].get(group_name)
      if (group_name != '__NONE_CATEGORY_DG__'
          and (group is None or not group['is_on'])):
        return none_debug_group

      return super().__new__(cls)


    @override
    def __init__( # pyright: ignore[reportInconsistentConstructor]
      self,
      name: str,
      group_name: T,
      config: DebugGroupConfigType | None = None,
      *,
      debug_manager_settings: FinalDebugSettingsType[T],
      none_debug_group: 'DebugManager.NoneDebugGroup[T] | None'
    ) -> None:
      final_config: FinalDebugGroupConfigType = {
        **debug_manager_settings['group_configs'][group_name],
        **(config or {})
      }

      if DebugManager.current_groups:
        previous_indentation = DebugManager.current_groups[-1].indentation
      else:
        previous_indentation = ''

      indentation_escape_codes = ''
      indentation_fore = final_config['indentation_fore_color']
      indentation_back = final_config['indentation_back_color']
      indentation_style = final_config['indentation_style']

      if not indentation_style:
        indentation_escape_codes += reset_formats()
      else:
        indentation_escape_codes += format_text(indentation_style)
      indentation_escape_codes += fore_color(indentation_fore)
      indentation_escape_codes += back_color(indentation_back)

      final_indentation = (
        previous_indentation +
        indentation_escape_codes +
        INDIVIDUAL_GROUP_INDENTATION_TEXT
      )
      super().__init__(
        self = self,
        name = name,
        indentation = final_indentation,
        config = final_config
      )
      DebugManager.current_level += 1
      self._max_chars_per_line = (
        debug_manager_settings['max_chars_per_line']
        - DebugManager.current_level * len(INDIVIDUAL_GROUP_INDENTATION_TEXT)
        - len(AFTER_GROUP_INDENTATION_TEXT)
      )
      self._debugs_on = debug_manager_settings['debugs_on']
      self._none_debug_group = none_debug_group


    @override
    def model_post_init(self, _context: Any) -> None:
      print( # noqa: T201 # This package is for debugging purposes, so we want to print to stdout.
        self.indentation[:-1]
        + format_text('bold')
        + f'========> Starting debug group: {self.name} <======='
        + reset_formats()
      )
      # We know the str is only for the NoneDebugGroup, which is never getting here
      DebugManager.current_groups.append(self) # pyright: ignore[reportArgumentType]
    #endregion New + Init + Post Init + Validators Methods


    #region Instance Methods
    #region _Internal Helper Methods
    def _before_text(self, config: FinalDebugGroupConfigType | None = None) -> str:
      if not config:
        config = self.config

      escape_codes = ''
      fore = config['fore_color']
      back = config['back_color']
      style = config['style']

      if not style:
        escape_codes += reset_formats()
      else:
        escape_codes += format_text(style)
      escape_codes += fore_color(fore)
      escape_codes += back_color(back)

      return self.indentation + escape_codes + AFTER_GROUP_INDENTATION_TEXT


    @cached_property
    def _default_before_text(self) -> str:
      return self._before_text()


    def _split_and_group_recursively(  # noqa: C901, PLR0912
      self,
      text: str,
      level: int,
      before_text: str,
      *,
      is_first_call: bool = False
    ) -> str:
      bg_position = text.find('|BG|')
      eg_position = text.find('|EG|')

      # BG comes first
      if bg_position != -1 and (eg_position == -1 or bg_position < eg_position):
        if bg_position == 0:
          return '\n' + self._split_and_group_recursively(text.split('|BG|', 1)[0],
                                                          level + 1,
                                                          before_text,
                                                          is_first_call = is_first_call)

        before, after = text.split('|BG|', 1)
        return (
          self._split_and_group_recursively(before,
                                            level,
                                            before_text,
                                            is_first_call = is_first_call)
          + '\n'
          + self._split_and_group_recursively(after,
                                              level + 1,
                                              before_text)
        )

      # EG comes first
      if eg_position != -1:
        if level == 0:
          msg = 'Mismatched |EG| tag found with no corresponding |BG| tag.'
          raise ValueError(msg)
        if eg_position == (len(text) - len('|EG|') - 1):
          return self._split_and_group_recursively(text.split('|EG|', 1)[0],
                                                  level - 1,
                                                  before_text) + '\n'

        before, after = text.split('|EG|', 1)
        return (
          self._split_and_group_recursively(before, level, before_text)
          + '\n'
          + self._split_and_group_recursively(after, level - 1, before_text)
        )

      # No more BG or EG tags found
      final_text = ''
      max_length = self._max_chars_per_line - (len(INTERNAL_GROUP_INDENTATION_TEXT) * level)
      internal_indentation = INTERNAL_GROUP_INDENTATION_TEXT * level

      # # Fix indentation for JSON values
      while True:
        end = True
        new_text = ''
        for line in text.splitlines():
          if '_VALUE_' in line:
            end = False
            key, value = line.split('_VALUE_')

            if value not in ('{', '{}', '[', '[]'):
              left_spaces = ' ' * len(key)
              if value[-1] == ',':
                value = value[:-1]
                final_comma = ','
              else:
                final_comma = ''
              value = deep_parse_json_to_obj(value)
              value = f'{json.dumps(value, indent = 2)}{final_comma}'
              value = value.replace('\n', f'\n{left_spaces}')
              value = value.replace('\\n', f'\n{left_spaces}')
            new_text += f'{key}{value}\n'

          else:
            new_text += f'{line}\n'
        text = new_text

        if end:
          break

      # # Split lines based on max length
      for i, line in enumerate(text.splitlines()):
        left_spaces_count = len(line) - len(line.lstrip(' '))
        left_spaces = ' ' * left_spaces_count

        if i == 0 and is_first_call:
          final_line = f'{INIT_PRINT_INDENTATION_TEXT}{line}'
        else:
          final_line = f'{PARAGRAPH_INDENTATION_TEXT}{line}'

        while len(final_line) > max_length and ' ' in final_line[max_length:]:
          line_to_add, rest = final_line[:max_length].rsplit(' ', 1)
          final_text += f'{before_text}{internal_indentation}{line_to_add}\n'
          final_line = f'{left_spaces}{rest}{final_line[max_length:]}'

        final_text += f'{before_text}{internal_indentation}{final_line}\n'

      return final_text[:-1] # Remove last newline
    #endregion _Internal Helper Methods

    #region Normal Methods
    def print(
      self,
      *args: Any,  # noqa: ANN401
      config: DebugGroupConfigType | None = None,
      unless: T | list[T] | None = None,
      **kwargs: Any  # noqa: ANN401
    ) -> None:
      """Print debug information with indentation and formatting."""
      if unless:
        if isinstance(unless, str):
          if unless in self._debugs_on:
            return
        else: # List
          for dg_name in unless:
            if dg_name in self._debugs_on:
              return

      final_text = ''
      for arg in args:
        final_text += str(arg)
      for value in kwargs.values():
        final_text += str(value)

      bg_count = final_text.count('|BG|')
      eg_count = final_text.count('|EG|')
      if bg_count != eg_count:
        msg = (f'Mismatched |BG| and |EG| tags in debug print.'
              f' |BG| count: {bg_count}, |EG| count: {eg_count}.')
        raise ValueError(msg)

      if config:
        before_text = self._before_text({ **DebugManager.DEBUG_SETTINGS, **config }) # pyright: ignore[reportGeneralTypeIssues, reportArgumentType]
      else:
        before_text = self._default_before_text

      final_text = self._split_and_group_recursively(final_text, 0, before_text,
                                                     is_first_call = True)

      print(final_text.rstrip('\n') + reset_formats()) # noqa: T201 # This package is for debugging purposes, so we want to print to stdout.


    def end(self) -> None:
      """End the current debug group and print the closing message."""
      print( # noqa: T201 # This package is for debugging purposes, so we want to print to stdout.
        self.indentation[:-1]
        + format_text('bold')
        + f'========> Ending debug group: {self.name} <======='
        + reset_formats()
      )
      if DebugManager.current_groups[-1] is self:
        _ = DebugManager.current_groups.pop()
        DebugManager.current_level -= 1
      else:
        msg = 'DebugGroup end called out of order.'
        raise RuntimeError(msg)
    #endregion Normal Methods

    #region Custom Tool Methods
    #endregion Custom Tool Methods
    #endregion Instance Methods


  ##################################################################################################
  #                                       NONE DEBUG GROUP                                         #
  ##################################################################################################
  class NoneDebugGroup[noneT: str](DebugGroup[noneT]):
    """A DebugGroup that does nothing, used when a category is off."""
    @override
    def __init__( # pyright: ignore[reportMissingSuperCall, reportInconsistentConstructor]
      self,
      name: str,
      group_name: noneT,
      config: DebugGroupConfigType | None = None,
      *,
      debug_manager_settings: FinalDebugSettingsType[noneT],
      none_debug_group: 'DebugManager.NoneDebugGroup[noneT] | None'
    ) -> None:
      pass

    @override
    def model_post_init(self, _context: Any) -> None:
      pass

    @override
    def print(self, *args: Any, **kwargs: Any) -> None:
      pass

    @override
    def end(self) -> None:
      pass


