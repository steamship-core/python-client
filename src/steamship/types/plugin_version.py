# from typing import List
# from dataclasses import dataclass
# from steamship.types.base import Request, Model, str_to_metadata

# @dataclass
# class PluginVersion(Model):
#   id: str = None
#   userId: str = None
#   appId: str = None
#   name: str = None
#   handle: str = None
#   isDefault: bool = None
#   externalId: str = None
#   externalType: str = None
#   metadata: str = None

#   @staticmethod
#   def from_dict(d: any, client: ApiBase = None) -> "PluginVersion":
#     return PluginVersion(
#       id = d.get('id', None),
#       userId = d.get('userId', None),
#       appId = d.get('appId', None),
#       name = d.get('name', None),
#       handle = d.get('handle', None),
#       isDefault = d.get('isDefault', None),
#       externalId = d.get('externalId', None),
#       externalType = d.get('externalType', None),
#       metadata = d.get('metadata', None)
#     )
