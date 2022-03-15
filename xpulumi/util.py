# Copyright (c) 2022 Samuel J. McKelvie
#
# MIT License - See LICENSE file accompanying this package.
#

"""Miscellaneous utility functions"""

from typing import Type, Any, Optional
from .internal_types import Jsonable

import json
import hashlib
import os
from urllib.parse import urlparse, ParseResult, urlunparse, unquote as url_unquote
import pathlib

from .exceptions import XPulumiError

def hash_pathname(pathname: str) -> str:
  result = hashlib.sha1(os.path.abspath(os.path.expanduser(pathname)).encode("utf-8")).hexdigest()
  return result


def full_name_of_type(t: Type) -> str:
  """Returns the fully qualified name of a type

  Args:
      t (Type): A type, which may be a builtin type or a class

  Returns:
      str: The fully qualified name of the type
  """
  module: str = t.__module__
  if module == 'builtins':
    result: str = t.__qualname__
  else:
    result = module + '.' + t.__qualname__
  return result

def full_type(o: Any) -> str:
  """Returns the fully qualified name of an object or value's type

  Args:
      o: any object or value

  Returns:
      str: The fully qualified name of the object or value's type
  """
  return full_name_of_type(o.__class__)

def clone_json_data(data: Jsonable) -> Jsonable:
  """Makes a deep copy of a json-serializable value, by serializing and then unserializing.

  Args:
      data (Jsonable): A JSON-serializable value

  Raises:
      TypeError: If data is not serializable to JSON

  Returns:
      Jsonable: A deep copy of the provided value, which can be modified without affecting the original.
  """
  if not data is None and not isinstance(data, (str, int, float, bool)):
    data = json.loads(json.dumps(data))
  return data

def file_url_to_pathname(url: str, cwd: Optional[str]=None, allow_relative: bool=True) -> str:
  if cwd is None:
    cwd = '.'
  url_parts = urlparse(url)
  if url_parts.scheme != 'file':
    raise XPulumiError(f"Not a file:// URL: {url}")
  # Pulumi uses nonstandard (and ambiguous) file:// URIs that allow relative pathnames. They do not support
  # the standard SMB-style "file://<server>/<shared-path>" model. file://myfile is interpreted as relative
  # filename "myfile". file:///myfile is properly interpreted as absolute path "/myfile" on the local machine.
  # file://~/myfile is interpreted as file "myfile" in the caller's home directory.
  # For sanity we treat file://localhost/ and file://127.0.0.1/ as special cases.
  base_dir = url_unquote(url_parts.netloc)
  if base_dir == '' or base_dir == 'localhost' or base_dir == '127.0.0.1':
    base_dir = '/'
  if not allow_relative and base_dir != '/':
    raise XPulumiError(f"Relative and network-based file:// backends are not allowed: {url}")
  url_path = url_unquote(url_parts.path)
  while url_path.startswith('/'):
    url_path = url_path[1:]
  if url_path == '':
    url_path = base_dir
  elif base_dir.endswith('/'):
    url_path = base_dir + url_path
  else:
    url_path = base_dir + '/' + url_path
  pathname = os.path.abspath(os.path.join(os.path.expanduser(cwd), os.path.expanduser(os.path.normpath(url_path))))
  return pathname

def pathname_to_file_url(pathname: str, cwd: Optional[str]=None) -> str:
  if cwd is None:
    cwd = '.'
  pathname = os.path.abspath(os.path.join(os.path.expanduser(cwd), os.path.expanduser(pathname)))
  url = pathlib.Path(pathname).as_uri()
  return url
