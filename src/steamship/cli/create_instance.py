import json
import logging
from os import path
from typing import Any, Callable, Dict, Optional

import click

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
    "--instance",
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
    workspace: Optional[str] = None, instance: Optional[str] = None, config: Optional[str] = None
):
    """Create an instance of your package/plugin for use.

    Must be run from a directory containing a Steamship manifest.
    """

    with LoggingDisabled():  # keep CLI output as concise as possible
        return _create_instance(workspace, instance, config)


def _create_instance(
    workspace: Optional[str] = None, instance: Optional[str] = None, config: Optional[str] = None
):
    manifest = None
    if path.exists("steamship.json"):
        manifest = Manifest.load_manifest()
    else:
        click.secho("No manifest found for instance creation.", fg="red")
        click.secho("Please try again from a directory with a package or plugin manifest.")
        click.get_current_context().abort()

    if manifest is None:
        click.secho("Steamship manifest failed to load.", fg="red")
        click.get_current_context().abort()

    invocable_config = config_dict(config)

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

    instance_fn = client.use
    if manifest.type == DeployableType.PLUGIN:
        instance_fn = client.use_plugin

    if instance is None:
        instance = create_instance_handle(
            invocable_handle=manifest.handle,
            version_handle=manifest.version,
            invocable_config=invocable_config,
        )

    try:
        _call_fn(client, manifest, instance, invocable_config, instance_fn)

    except SteamshipError as e:
        click.secho(f"\nFailed to create instance: {e.message}", fg="red")
        click.get_current_context().abort()


def _call_fn(
    client: Steamship,
    manifest: Manifest,
    instance: str,
    config: Optional[Dict[str, Any]],
    instance_fn: Callable,
):
    click.echo("Using values:\n- Workspace: ", nl=False)
    click.secho(f"{client.get_workspace().handle}", fg="green")
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
        instance = instance_fn(
            manifest.handle,
            instance_handle=instance,
            version=manifest.version,
            config=config,
            wait_for_init=True,
        )
        if instance:
            click.secho("\nSuccess!", fg="green")
            if manifest.type == DeployableType.PACKAGE:
                click.echo(f"Instance URL: {instance.invocation_url}")
            return
        else:
            raise SteamshipError("instance creation unexpectedly returned empty instance.")


def config_dict(config: Optional[str]) -> Dict[str, Any]:
    return_dict = {}
    if config:
        try:
            json_config = json.loads(config)
            if isinstance(json_config, dict):
                return_dict = json_config
            else:
                click.secho("Could not parse configuration.", fg="red")
                click.get_current_context().abort()
        except Exception:
            try:
                with open(config) as f:
                    file_json = json.load(f)
                    if isinstance(file_json, dict):
                        return_dict = file_json
                    else:
                        click.secho("Could not parse configuration.", fg="red")
                        click.get_current_context().abort()
            except Exception as e:
                click.secho(
                    f"Unknown configuration. Could not parse it as a file or JSON string: {e}",
                    fg="red",
                )
                click.get_current_context().abort()
    return return_dict
