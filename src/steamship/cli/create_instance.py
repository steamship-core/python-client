import json
from os import path
from typing import Any, Dict, Optional

import click

from steamship import Steamship, SteamshipError
from steamship.cli.ship_spinner import ship_spinner
from steamship.data.manifest import DeployableType, Manifest


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

    Must be run from a directory containing a Steamship manifest."""
    global client
    global manifest

    try:
        client = Steamship(workspace=workspace)
    except SteamshipError as e:
        click.secho(e.message, fg="red")
        click.get_current_context().abort()

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

    instance_fn = client.use
    if manifest.type == DeployableType.PLUGIN:
        instance_fn = client.use_plugin

    try:
        click.echo("Creating a new instance for usage: ", nl=False)
        with ship_spinner():
            instance = instance_fn(
                manifest.handle,
                instance_handle=instance,
                version=manifest.version,
                config=invocable_config,
                wait_for_init=True,
            )
            if instance:
                click.secho(
                    f"\nSuccess! New instance '{instance.handle}' for plugin '{manifest.handle}' created "
                    f"in workspace '{client.get_workspace().handle}'.",
                    fg="green",
                )
                if manifest.type == DeployableType.PACKAGE:
                    click.echo(f"Instance URL: {instance.invocation_url}")
                return

    except SteamshipError as e:
        click.secho(f"Failed to create instance: {e.message}", fg="red")
        click.get_current_context().exit()


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
