# from typing import List
# from dataclasses import dataclass
# from steamship.types.base import Request, Model, str_to_metadata
# from steamship.client.base import ApiBase

# @dataclass
# class Plugin(Model):
#   client: ApiBase = None
#   id: str = None
#   userId: str = None
#   name: str = None
#   handle: str = None
#   isPublic: bool = None
#   externalId: str = None
#   externalType: str = None
#   metadata: str = None

#   @staticmethod
#   def from_dict(d: any, client: ApiBase = None) -> "Plugin":
#     return Plugin(
#       steamship = steamship
#       id = d.get('id', None),
#       userId = d.get('userId', None),
#       appId = d.get('appId', None),
#       name = d.get('name', None),
#       handle = d.get('handle', None),
#       isPublic = d.get('isPublic', None),
#       externalId = d.get('externalId', None),
#       externalType = d.get('externalType', None),
#       metadata = d.get('metadata', None)
#     )

#   @staticmethod
#   def create(
#     client: ApiBase,
#     name: str = None,
#     handle: str = None,
#     filename: str = None,
#     content: str = None,
#     format: str = None,
#     corpusId: str = None,
#     convert: bool = False,
#     spaceId: str = None,
#     spaceHandle: str = None
#     ) -> "Plugin":

#     if filename is None and name is None and content is None:
#       raise Exception("Either filename or name + content must be provided.")
    
#     if filename is not None:
#       with open(filename, 'rb') as f:
#         content = f.read()
#         if name is None:
#           name = filename

#     req = FileUploadRequest(
#       type=FileUploadType.file,
#       corpusId=corpusId,
#       name=name,
#       fileFormat=format,
#       convert=convert
#     )

#     res = client.post(
#       'file/upload',
#       payload=req,
#       file=(name, content, "multipart/form-data"),
#       expect=FileUploadResponse,
#       spaceId=spaceId,
#       spaceHandle=spaceHandle
#     )
#     return File(
#       client=client,
#       name=req.name,
#       id=res.data.fileId,
#       format=res.data.fileFormat,
#       corpusId=res.data.corpusId
#     )

#   def create_version(
#     name: str = None,
#     handle: str = None,
#     filename: str = None,
#     content: str = None,
#     ) -> "PluginVersion":

#     if filename is None and name is None and content is None:
#       raise Exception("Either filename or name + content must be provided.")
    
#     if filename is not None:
#       with open(filename, 'rb') as f:
#         content = f.read()
#         if name is None:
#           name = filename

#     req = PluginVersionUploadRequest(
#       type=FileUploadType.file,
#       appId=self.id,
#       name=name,
#       handle=handle,
#     )

#     res = client.post(
#       'app/version/create',
#       payload=req,
#       file=(name, content, "multipart/form-data"),
#       expect=PluginVersionUploadResponse
#     )
#     return PluginVersion(
#       steamship=self.steamship,
#       name=req.name,
#       id=res.data.id,
#       appId=self.id,
#     )

class PluginVersion:
  pass

class Plugin:
  """A service.
  """
