import json
import logging
import os
from json import JSONDecodeError
from os import path
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import click
from pydantic import ValidationError

from steamship import Steamship, SteamshipError
from steamship.cli.ship_spinner import ship_spinner
from steamship.data.manifest import DeployableType, Manifest
from steamship.utils.metadata import hash_dict
from steamship.utils.utils import create_instance_handle


class LoggingDisabled:
    """Context manager that turns off logging within context."""

    def __enter__(self):
        logging.disable(logging.CRITICAL)

    def __exit__(self, exit_type, exit_value, exit_traceback):
        logging.disable(logging.NOTSET)


@click.command(name="use")
@click.option(
    "--workspace",
    "-w",
    required=False,
    type=str,
    help="Workspace handle. The new instance will be created in this workspace. If not specified, "
    "the default workspace will be used.",
)
@click.option(
    "--instance_handle",
    "-i",
    type=str,
    required=False,
    help="Instance handle. Used to name the instance (if it needs to be created). If not specified, "
    "a generated instance name will be used.",
)
@click.option(
    "--config",
    "-c",
    type=str,
    required=False,
    help="Instance configuration. May be inline JSON or a path to a file. If not specified, "
    "an empty configuration dictionary will be passed to the instance.",
)
def create_instance(
    workspace: Optional[str] = None,
    instance_handle: Optional[str] = None,
    config: Optional[str] = None,
):
    """Create an instance of your package/plugin for use.

    Must be run from a directory containing a Steamship manifest.
    """

    with LoggingDisabled():  # keep CLI output as concise as possible
        return _create_instance(workspace=workspace, instance_handle=instance_handle, config=config)


def _create_instance(  # noqa: C901
    workspace: Optional[str] = None,
    instance_handle: Optional[str] = None,
    config: Optional[str] = None,
):
    manifest = load_manifest()
    invocable_config, is_file = config_str_to_dict(config)
    set_unset_params(config, invocable_config, is_file, manifest)

    if workspace is None or len(workspace) == 0:
        ws_hash = hash_dict(
            {
                **invocable_config,
                "version": manifest.version,
                "invocable": manifest.handle,
            }
        )
        workspace = f"space-{ws_hash}"

    client = None
    try:
        client = Steamship(workspace=workspace)
    except SteamshipError as e:
        click.secho(e.message, fg="red")
        click.get_current_context().abort()

    create_instance_fn = client.use
    if manifest.type == DeployableType.PLUGIN:
        create_instance_fn = client.use_plugin

    if instance_handle is None:
        instance_handle = create_instance_handle(
            invocable_handle=manifest.handle,
            version_handle=manifest.version,
            invocable_config=invocable_config,
        )

    try:
        _call_create_instance_fn(
            client, manifest, instance_handle, invocable_config, create_instance_fn
        )
    except SteamshipError as e:
        if "Configuration for this PackageInstance is invalid." in e.message:
            click.secho(
                "\nThe configuration for this Package instance was invalid. "
                "This usually means it contains some required configuration fields.",
                fg="red",
            )
            click.secho("Create one interactively on the web at:\n", fg="red")
            click.secho(f"   https://steamship.com/packages/{manifest.handle}/_create\n")
        else:
            click.secho(f"\nFailed to create instance: {e.message}", fg="red")
        click.get_current_context().abort()


def load_manifest():
    manifest = None
    if path.exists("steamship.json"):
        try:
            manifest = Manifest.load_manifest()
        except ValidationError as e:
            click.secho("")
            click.secho("This package had an invalid steamship.json file.", fg="red")
            click.secho("")
            click.secho(f"{e}", fg="red")
            click.secho("")
            click.get_current_context().abort()
    else:
        click.secho("No manifest found for instance creation.", fg="red")
        click.secho("Please try again from a directory with a package or plugin manifest.")
        click.get_current_context().abort()
    if manifest is None:
        click.secho("Steamship manifest failed to load.", fg="red")
        click.get_current_context().abort()
    return manifest


def set_unset_params(config, invocable_config, is_file, manifest):
    new_param_values = False
    for param, param_config in manifest.configTemplate.items():
        if param not in invocable_config and (
            param_config.default is None or param_config.default == ""
        ):
            if param.upper() in os.environ:
                invocable_config[param] = os.environ[param.upper()]
            else:
                invocable_config[param] = click.prompt(
                    f"Value for {param} ({param_config.description})"
                    + ("\nPress Enter for DEFAULT" if param_config.default == "" else ""),
                    default="",
                )
            new_param_values = True
    if is_file and new_param_values:
        if click.confirm(
            f"Do you want to store this config in your config file ({config})?", default=True
        ):
            json.dump(invocable_config, Path(config).open("w"))
            click.secho(
                f"Successfully wrote configuration {json.dumps(config)} to {config}.", fg="green"
            )


def _call_create_instance_fn(
    client: Steamship,
    manifest: Manifest,
    instance: str,
    config: Optional[Dict[str, Any]],
    create_instance_fn: Callable,
):
    """"""
    workspace_handle = client.get_workspace().handle

    click.echo("Using values:\n- Workspace: ", nl=False)
    click.secho(f"{workspace_handle}", fg="green")
    click.echo(f"- {manifest.type.title()}: ", nl=False)
    click.secho(f"{manifest.handle}", fg="green")
    click.echo("- Version: ", nl=False)
    click.secho(f"{manifest.version}", fg="green")
    click.echo("- Instance Handle: ", nl=False)
    click.secho(f"{instance}", fg="green")
    click.echo("- Configuration: ", nl=False)
    click.secho(f"{json.dumps(config)}", fg="green")

    click.echo("Creating new (or fetching existing) instance: ", nl=False)
    with ship_spinner():
        instance = create_instance_fn(
            manifest.handle,
            instance_handle=instance,
            version=manifest.version,
            config=config,
            wait_for_init=True,
        )
        if instance:
            click.secho("\nSuccess!", fg="green")
            click.secho("")
            if manifest.type == DeployableType.PACKAGE:
                click.echo(
                    f"Web URL: https://steamship.com/workspaces/{workspace_handle}/packages/{instance.handle}"
                )
                click.echo(f"API URL: {instance.invocation_url}")
                click.secho("")
            return
        else:
            raise SteamshipError("instance creation unexpectedly returned empty instance.")


def cannot_parse_config(config: str, exception: Optional[Exception] = None):
    exception_str = f": {exception}" if exception else ""
    click.secho(
        f"Could not parse configuration {config} as a file or JSON string{exception_str}",
        fg="red",
    )
    click.get_current_context().abort()


def config_str_to_dict(config: Optional[str] = None) -> (Dict[str, Any], bool):
    """Convert config string into dict.

    The input string can be a JSON-string or the name of a file."""

    if not config:
        return {}, False
    try:
        json_config = json.loads(config)
        if not isinstance(json_config, dict):
            cannot_parse_config(config)
        return json_config, False
    except JSONDecodeError:
        try:
            config_path = Path(config)
            if not config_path.exists():
                if click.confirm(
                    f"Configuration file {config_path} does not exist. Do you want to create it",
                    default=True,
                ):
                    config_path.parent.mkdir(parents=True, exist_ok=True)
                    json.dump({}, config_path.open("w"))
            file_json = json.load(config_path.open())
            if not isinstance(file_json, dict):
                cannot_parse_config(config)
            return file_json, True

        except Exception as e:
            cannot_parse_config(config, e)
