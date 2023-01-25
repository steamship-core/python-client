import importlib
import os
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path

import click
from semver import VersionInfo

from steamship import Package, PackageVersion, Steamship, SteamshipError
from steamship.cli.manifest_init_wizard import validate_handle, validate_version_handle
from steamship.cli.ship_spinner import ship_spinner
from steamship.data.user import User
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
        click.secho("Found the following config parameters; updating steamship.json.", fg="cyan")
        for param_name, param in config_parameters.items():
            click.echo(f"{param_name}:")
            click.echo(f"\tType: {param.type}")
            click.echo(f"\tDefault: {param.default}")
            click.echo(f"\tDescription: {param.description}")
    else:
        click.secho("Found no config parameters; updating steamship.json.", fg="cyan")

    manifest.configTemplate = config_parameters
    manifest.save()


def get_archive_path(manifest: Manifest) -> Path:
    return Path(".") / "build" / "archives" / f"{manifest.handle}_v{manifest.version}.zip"


def bundle_deployable(manifest: Manifest):
    archive_path = get_archive_path(manifest)
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
    def _create_version(self, client: Steamship, manifest: Manifest, thing_id: str):
        pass

    @abstractmethod
    def create_object(self, client: Steamship, manifest: Manifest):
        pass

    @abstractmethod
    def thing_type(self):
        pass

    def create_or_fetch_thing(self, client: Steamship, user: User, manifest: Manifest):
        thing = None
        while thing is None:
            click.echo(
                f"Creating / fetching {self.thing_type()} with handle [{manifest.handle}]... ",
                nl=False,
            )
            try:
                thing = self.create_object(client, manifest)
                print(f"Userid: {thing.user_id}")
                if thing.user_id != user.id:
                    self.ask_for_new_handle(manifest)
                    thing = None
            except SteamshipError as e:
                if e.message == "Something went wrong.":
                    self.ask_for_new_handle(manifest)
                else:
                    click.secho(
                        f"Unable to create / fetch {self.thing_type()}. Server returned message: {e.message}"
                    )
                    click.get_current_context().abort()

        click.echo("Done.")
        return thing

    def ask_for_new_handle(self, manifest: Manifest):
        try_again = click.confirm(
            click.style(
                f"\nIt looks like that handle [{manifest.handle}] is already taken by another user.  Would you like to change the handle and try again?",
                fg="yellow",
            ),
            default=True,
        )
        if try_again:
            new_handle = click.prompt(
                f"What handle would you like to use for your {self.thing_type()}? Valid characters are a-z and -",
                value_proc=validate_handle,
            )
            manifest.handle = new_handle
            manifest.save()
        else:
            click.get_current_context().abort()

    def create_version(self, client: Steamship, manifest: Manifest, thing_id: str):
        version = None
        while version is None:
            try:
                with ship_spinner():
                    version = self._create_version(client, manifest, thing_id)
            except SteamshipError as e:
                if e.message == "The object you are trying to create already exists.":
                    self.ask_for_new_version_handle(manifest)
                else:
                    click.secho(
                        f"Unable to create / fetch {self.thing_type()}. Server returned message: {e.message}"
                    )
                    click.get_current_context().abort()

    def ask_for_new_version_handle(self, manifest: Manifest):
        try_again = click.confirm(
            click.style(
                f"\nIt looks like that version [{manifest.version}] has already been deployed. Would you like to change the version handle and try again?",
                fg="yellow",
            ),
            default=True,
        )
        if try_again:
            default_new = "1.0.0"
            try:
                default_new = str(VersionInfo.parse(manifest.version).bump_prerelease())
            except ValueError:
                pass
            old_archive_path = get_archive_path(manifest)
            new_version_handle = click.prompt(
                "What should the new version be? Valid characters are a-z, 0-9, . and -",
                value_proc=validate_version_handle,
                default=default_new,
            )
            manifest.version = new_version_handle
            manifest.save()
            new_archive_path = get_archive_path(manifest)
            old_archive_path.rename(new_archive_path)
        else:
            click.get_current_context().abort()


class PackageDeployer(DeployableDeployer):
    def _create_version(self, client: Steamship, manifest: Manifest, thing_id: str):
        return PackageVersion.create(
            client=client,
            config_template=manifest.config_template_as_dict(),
            handle=manifest.version,
            filename=f"build/archives/{manifest.handle}_v{manifest.version}.zip",
            package_id=thing_id,
        )

    def create_object(self, client: Steamship, manifest: Manifest):
        return Package.create(client, handle=manifest.handle, fetch_if_exists=True)

    def thing_type(self):
        return "package"
