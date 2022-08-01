"""
api_version.py - API Version
"""
from typing import Tuple

class APIVersion:

   def __init__(self, major_version, minor_version):
       self._major_version = major_version
       self._minor_version = minor_version

   def to_tuple(self) -> Tuple[int, int]:
       return self._major_version, self._minor_version

   def to_str(self) -> str:
       return f"v{self._major_version}_{self._minor_version}"