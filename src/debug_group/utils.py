"""Utility functions module."""

# ---> Standard library imports <--- #
import ast
import json
import re
from typing import Any


type JsonParseableType = Any # README/TODO: Replace with a more specific type hint
def deep_parse_json_to_obj(value: JsonParseableType) -> JsonParseableType:
  """Recursively parse a JSON-like structure (dict, list, or string) into Python objects."""
  if isinstance(value, str):
    # Convert datetime.date(YYYY, MM, DD) to 'YYYY-MM-DD' format before parsing
    value = re.sub(
      r'datetime\.date\((\d+), (\d+), (\d+)\)',
      lambda m: f"'{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}'",
      value
    )
    value = re.sub(
      r"Decimal\('(\d+\.\d+)'\)",
      lambda m: f'{m.group(1)}',
      value
    )
    for parser in (json.loads, ast.literal_eval):
      try:
        return deep_parse_json_to_obj(parser(value))
      except Exception as _e:  # noqa: BLE001, S110
        pass
    return value

  if isinstance(value, list):
    return [deep_parse_json_to_obj(v) for v in value] # pyright: ignore[reportUnknownVariableType]

  if isinstance(value, dict):
    return {k: deep_parse_json_to_obj(v) for k, v in value.items()} # pyright: ignore[reportUnknownVariableType]

  return value
