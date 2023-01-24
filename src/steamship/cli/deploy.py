import importlib
import os
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path

import click

from steamship import Package, PackageVersion, Steamship, SteamshipError
from steamship.invocable.lambda_handler import get_class_from_module
from steamship.invocable.manifest import Manifest

DEFAULT_BUILD_IGNORE = [
    "build",
    ".git",
    ".venv",
    ".ipynb_checkpoints",
    ".DS_Store",
    "venv",
    "tests",
    "examples",
    ".idea",
    "__pycache__",
]


def update_config_template(manifest: Manifest):

    path = Path("src/api.py")
    if not path.exists():
        path = Path("api.py")
        if not path.exists():
            raise SteamshipError("Could not find api.py either in root directory or in src.")

    module = importlib.machinery.SourceFileLoader("api", str(path)).load_module()
    invocable_type = get_class_from_module(module)

    # DK: why do I have to pass invocable_type here into config_cls class method?
    config_parameters = invocable_type.config_cls(invocable_type).get_config_parameters()

    if len(config_parameters) > 0:
        click.echo(
            click.style(
                "Found the following config parameters; updating steamship.json.", fg="cyan"
            )
        )
        for param_name, param in config_parameters.items():
            click.echo(f"{param_name}:")
            click.echo(f"\tType: {param.type}")
            click.echo(f"\tDefault: {param.default}")
            click.echo(f"\tDescription: {param.description}")
    else:
        click.echo(click.style("Found no config parameters; updating steamship.json.", fg="cyan"))

    manifest.configTemplate = config_parameters
    manifest.save()


def bundle_deployable(manifest: Manifest):
    archive_path = Path(".") / "build" / "archives" / f"{manifest.handle}_v{manifest.version}.zip"
    excludes = DEFAULT_BUILD_IGNORE + manifest.build_config.get("ignore", [])

    archive_path.unlink(missing_ok=True)
    with zipfile.ZipFile(
        file=archive_path, mode="a", compression=zipfile.ZIP_DEFLATED, allowZip64=False
    ) as zip_file:

        root = Path(".")
        for file_path in root.iterdir():
            if file_path.name not in excludes:
                if file_path.is_dir():
                    for directory, _, files in os.walk(file_path):
                        subdirectory_path = Path(directory)
                        if Path(directory).name not in excludes:
                            for file in files:
                                pypi_file = subdirectory_path / file
                                relative_to = pypi_file.relative_to(file_path)
                                zip_file.write(pypi_file, relative_to)

                else:
                    zip_file.write(file_path)


class DeployableDeployer(ABC):
    @abstractmethod
    def create_version(self, client: Steamship, manifest: Manifest, thing_id: str):
        pass

    @abstractmethod
    def create_object(self, client: Steamship, manifest: Manifest):
        pass


class PackageDeployer(DeployableDeployer):
    def create_version(self, client: Steamship, manifest: Manifest, thing_id: str):
        return PackageVersion.create(
            client=client,
            config_template=manifest.config_template_as_dict(),
            handle=manifest.version,
            filename=f"build/archives/{manifest.handle}_v{manifest.version}.zip",
            package_id=thing_id,
        )

    def create_object(self, client: Steamship, manifest: Manifest):
        return Package.create(client, handle=manifest.handle, fetch_if_exists=True)
