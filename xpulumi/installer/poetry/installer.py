#!/usr/bin/env python3
#
# Copyright (c) 2022 Samuel J. McKelvie
#
# MIT License - See LICENSE file accompanying this package.
#

"""Installer for standard poetry CLI"""

from ast import Module
from typing import TextIO, Tuple, Optional, Dict, Iterator, Sequence
from pathlib import Path

import subprocess
import sys
import os
import argparse
import re
import urllib.request
from urllib.parse import urlparse
import http.client
import platform
import tempfile
import shutil
import shlex
from enum import Enum
from contextlib import contextmanager

from xpulumi.exceptions import XPulumiError

from ..util import (
    command_exists,
    find_command_in_path,
    download_url_text,
    run_once,
    sudo_check_output_stderr_exception,
    check_version_ge,
)

MIN_POETRY_VERSION = "1.1.12"

verbose: bool = False


@run_once
def standard_installer() -> Module:
  import imp
  module_name = "xpulumi.installer.poetry.std_installer"
  std_installer = imp.new_module(module_name)
  code = download_url_text("https://install.python-poetry.org")
  exec(code, std_installer.__dict__)
  sys.modules[module_name] = std_installer
  return std_installer

def std_data_dir(version: Optional[str] = None) -> Path:
  return standard_installer().data_dir(version=version)

def std_bin_dir(version: Optional[str] = None) -> Path:
  return standard_installer().bin_dir(version=version)

class Installer:
  std_installer: object

  def __init__(self, *args, **kwargs) -> None:
    self.std_installer = standard_installer().Installer(*args, **kwargs)

  def run(self) -> int:
    return self.std_installer.run()

def poetry_is_installed() -> bool:
  return command_exists('poetry')

def get_poetry_prog() -> Optional[str]:
  return find_command_in_path('poetry')

def get_poetry_version() -> str:
  result = sudo_check_output_stderr_exception(['poetry', '--version'], use_sudo=False).decode('utf-8').rstrip()
  result = result.split(' ')[-1]
  return result

def install_poetry(
      min_version: Optional[str]=MIN_POETRY_VERSION,
      force: bool=False,
      use_preview: bool=False
    ):
  is_installed = poetry_is_installed()
  if is_installed:
    version = get_poetry_version()
    if force:
      print(f"Forcing reinstall of Poetry over existing version {version}", file=sys.stderr)
    elif min_version is None:
      print(f"Poetry version {version} is already in PATH. No update is necessary.", file=sys.stderr)
      return
    elif check_version_ge(version, min_version):
      print(f"Poetry version {version} is already in PATH and meets the minimum version {min_version}. No update is necessary.", file=sys.stderr)
      return
  else:
    print(f"'poetry' command not found; installing Poetry.", file=sys.stderr)
  installer = Installer(preview=use_preview, force=force)
  exit_code = installer.run()
  if exit_code != 0:
    raise XPulumiError(f"Poetry installer returned nonzero exit code: {exit_code}")

