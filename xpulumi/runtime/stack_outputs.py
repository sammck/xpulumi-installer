# Copyright (c) 2022 Samuel J. McKelvie
#
# MIT License - See LICENSE file accompanying this package.
#

"""Promise-based fetching of external xpulumi stack outputs"""

from typing import Optional, Any, List, Callable, Mapping, Iterator, Iterable, Tuple

import os

from pulumi import Output, Input, get_stack
from .. import JsonableDict, Jsonable
from .. import XPulumiProject
from .util import get_xpulumi_project


class SyncStackOutputs:
  project: XPulumiProject
  """The xpulumi project"""

  stack_name: str
  """The xpulumi stack name"""

  outputs: JsonableDict
  """The actual outputs of the stack"""

  def __init__(
        self,
        project_name: Optional[str]=None,
        stack_name: Optional[str]=None,
        decrypt_secrets: bool=False
      ) -> None:
    project = get_xpulumi_project(project_name)
    if stack_name is None:
      stack_name = get_stack()
    outputs = project.get_stack_outputs(stack_name, decrypt_secrets=decrypt_secrets)
    self.project = project
    self.stack_name = stack_name
    self.outputs = outputs

  def get_output(self, name: str, default: Jsonable=None) -> Jsonable:
    return self.outputs.get(name, default)
  
  def require_output(self, name: str) -> Jsonable:
    return self.outputs[name]

  def __getitem__(self, key: str) -> Jsonable:
    return self.require_output(key)

  def __len__(self) -> int:
    return len(self.outputs)

  def __contains__(self, key: str) -> bool:
    return key in self.outputs

  def __iter__(self) -> Iterator[str]:
    return iter(self.outputs)

  def keys(self) -> Iterable[str]:
    return self.outputs.keys()
  
  def values(self) -> Iterable[Jsonable]:
    return self.outputs.values()
  
  def items(self) -> Iterable[Tuple[str, Jsonable]]:
    return self.outputs.items()
  
class StackOutputs:
  """An encapsulation of a promise to fetch the outputs of an external deployed xpulunmi stack.

  An instance of this class can provide promises for specific output values, or for a JsonableDict
  containing all output values of the stack.
  """
  _future_outputs: Output[SyncStackOutputs]

  def __init__(
        self,
        project_name: Input[Optional[str]]=None,
        stack_name: Input[Optional[str]]=None,
        decrypt_secrets: Input[bool]=False
      ) -> None:
    """Fetch the outputs of an external deployed xpulumi stack. The returned
       StackOutputs object can provide promises for individual outputs
       as well as all outputs as a JsonableDict.

    Args:
        project_name (Input[Optional[str]], optional):
                      The local xpulumi project name, or None to use the same project
                      as the current stack. Default is None.
        stack_name (Input[Optional[str]], optional): 
                      The stack name within the xpulumi project, or None to use the
                      same stack name as the current project. Defaults to None.
        decrypt_secrets (Input[bool], optional):
                      True if secret outputs should be decrypted. Defaults to False.
    """
    self._future_outputs = Output.all(project_name, stack_name, decrypt_secrets).apply(lambda args: self._resolve(*args))

  def _resolve(self, project_name: Optional[str], stack_name: str, decrypt_secrets: bool) -> SyncStackOutputs:
    result = SyncStackOutputs(project_name=project_name, stack_name=stack_name, decrypt_secrets=decrypt_secrets)
    return result

  def get_outputs(self) -> Output[JsonableDict]:
    return Output.all(self._future_outputs).apply(lambda args: args[0].outputs)
  
  def get_output(self, name: Input[str], default: Input[Jsonable]=None) -> Output[Jsonable]:
    return Output.all(self._future_outputs, name, default).apply(lambda args: args[0].get_output(args[1], default=args[2]))
  
  def require_output(self, name: Input[str]) -> Output[Jsonable]:
    return Output.all(self._future_outputs, name).apply(lambda args: args[0].require_output(args[1]))

  def __getitem__(self, key: Input[str]) -> Output[Jsonable]:
    return self.require_output(key)

  def __len__(self) -> Output[int]:
    return Output.all(self._future_outputs).apply(lambda args: len(args[0]))

  def __contains__(self, key: Input[str]) -> Output[bool]:
    return Output.all(self._future_outputs, key).apply(lambda args: args[1] in args[0])

  def keys(self) -> Output[Iterable[str]]:
    return Output.all(self._future_outputs).apply(lambda args: args[0].keys())
  
  def values(self) -> Output[Iterable[Jsonable]]:
    return Output.all(self._future_outputs).apply(lambda args: args[0].values())
  
  def items(self) -> Output[Iterable[Tuple[str, Jsonable]]]:
    return Output.all(self._future_outputs).apply(lambda args: args[0].items())
