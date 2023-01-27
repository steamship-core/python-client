import json
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel

from steamship.invocable.config import ConfigParameter


class DeployableType(str, Enum):
    PLUGIN = "plugin"
    PACKAGE = "package"


class SteamshipRegistry(BaseModel):
    tagline: Optional[str]  # noqa: N815
    tagline2: Optional[str]  # noqa: N815
    usefulFor: Optional[str]  # noqa: N815
    videoURL: Optional[str]  # noqa: N815
    githubURL: Optional[str]  # noqa: N815
    demoURL: Optional[str]  # noqa: N815
    jupyterURL: Optional[str]  # noqa: N815
    authorGithub: Optional[str]  # noqa: N815
    authorName: Optional[str]  # noqa: N815
    authorEmail: Optional[str]  # noqa: N815
    authorTwitter: Optional[str]  # noqa: N815
    authorURL: Optional[str]  # noqa: N815
    tags: List[str]


class Manifest(BaseModel):
    type: DeployableType
    handle: str
    version: str
    description: Optional[str]
    author: Optional[str]
    entrypoint: str = "Unused"
    public: bool
    build_config: Dict[str, List[str]] = {"ignore": []}
    configTemplate: Dict[str, ConfigParameter]  # noqa: N815
    steamshipRegistry: SteamshipRegistry  # noqa: N815

    @staticmethod
    def load_manifest() -> "Manifest":
        return Manifest.parse_file("steamship.json", content_type="application/json")

    def save(self):
        with open("steamship.json", "w") as file:
            json.dump(self.dict(), file, indent="\t")

    def config_template_as_dict(self):
        result = {}
        for param, spec in self.configTemplate.items():
            result[param] = {k: v for k, v in spec.dict().items() if v is not None}

        return result
