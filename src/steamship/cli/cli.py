import json
import logging
import sys
import time
from os import path
from typing import List

import click

import steamship
from steamship import PackageInstance, Steamship, SteamshipError, Workspace
from steamship.base.configuration import Configuration
from steamship.cli.deploy import (
    PackageDeployer,
    PluginDeployer,
    bundle_deployable,
    update_config_template,
)
from steamship.cli.manifest_init_wizard import manifest_init_wizard
from steamship.cli.requirements_init_wizard import requirements_init_wizard
from steamship.cli.ship_spinner import ship_spinner
from steamship.data.manifest import DeployableType, Manifest
from steamship.data.user import User


@click.group()
def cli():
    pass


def initialize(silently=False):
    logging.root.setLevel(logging.FATAL)
    if not silently:
        click.echo(f"Steamship PYTHON cli version {steamship.__version__}")


def abort(message: str):
    click.secho(message, fg="red")
    click.get_current_context().abort()


@click.command()
def login():
    """Log in to Steamship, creating ~/.steamship.json"""
    initialize()
    click.echo("Logging into Steamship.")
    if sys.argv[1] == "login":
        if Configuration.default_config_file_has_api_key():
            overwrite = click.confirm(
                text="You already have an API key in your .steamship.json file.  Do you want to remove it and login?",
                default=False,
            )
            if not overwrite:
                sys.exit(0)
            Configuration.remove_api_key_from_default_config()

        # Carry on with login
        client = Steamship()
        user = User.current(client)
        click.secho(f"🚢🚢🚢 Hooray! You're logged in with user handle: {user.handle} 🚢🚢🚢", fg="green")


@click.command()
def ships():
    """Ship some ships"""
    initialize()
    click.secho("Here are some ships:", fg="cyan")
    with ship_spinner():
        time.sleep(5)
    click.secho()


@click.command()
def deploy():
    """Deploy the package or plugin in this directory"""
    initialize()
    client = None
    try:
        client = Steamship()
    except SteamshipError as e:
        click.secho(e.message, fg="red")
        click.get_current_context().abort()

    user = User.current(client)
    if path.exists("steamship.json"):
        manifest = Manifest.load_manifest()
    else:
        manifest = manifest_init_wizard(client)
        manifest.save()

    if not path.exists("requirements.txt"):
        requirements_init_wizard()

    deployable_type = manifest.type

    update_config_template(manifest)

    deployer = None
    if deployable_type == DeployableType.PACKAGE:
        deployer = PackageDeployer()
    elif deployable_type == DeployableType.PLUGIN:
        deployer = PluginDeployer()
    else:
        click.secho("Deployable must be of type package or plugin.", fg="red")
        click.get_current_context().abort()

    deployable = deployer.create_or_fetch_deployable(client, user, manifest)

    click.echo("Bundling content... ", nl=False)
    bundle_deployable(manifest)
    click.echo("Done. 📦")

    _ = deployer.create_version(client, manifest, deployable.id)

    thing_url = f"{client.config.web_base}{deployable_type}s/{manifest.handle}"
    click.echo(
        f"Deployment was successful. View and share your new {deployable_type} here:\n\n{thing_url}\n"
    )

    # Common error conditions:
    # - Package/plugin handle already taken. [handled; asks user for new]
    # - Version handle already deployed. [handled; asks user for new]
    # - Bad parameter configuration. [mitigated by deriving template from Config object]
    # - Package content fails health check (ex. bad import) [Error caught while checking config object]


@click.command()
@click.option(
    "--delete-data",
    "-d",
    is_flag=True,
    default=False,
    help="Delete all existing data by recreating the workspace.",
)
@click.option("--config", "-c", multiple=True)
def test_instance(delete_data, config: List[str]):  # noqa: C901
    """Create an instance of your package for testing."""
    initialize(silently=True)
    client: Steamship = None
    try:
        client = Steamship()
    except SteamshipError as e:
        abort(e.message)

    manifest: Manifest = None
    if path.exists("steamship.json"):
        manifest = Manifest.load_manifest()
    else:
        abort("You must deploy your package first to create a test instance")

    if not manifest.type == "package":
        abort("This function can only be used on packages.")

    test_workspace_handle = f"test-workspace-for-{manifest.handle}"
    if delete_data:
        try:
            workspace = Workspace.get(client, handle=test_workspace_handle)
            workspace.delete()
        except SteamshipError as e:
            if "Unable to find" not in e.message:
                abort(e.message)

    client.switch_workspace(workspace_handle=test_workspace_handle)

    config_strings = {}
    for config_item in config:
        config_item_parts = config_item.split(":", 1)
        if len(config_item_parts) != 2:
            abort(f"Malformed config item: {config_item}")
        config_strings[config_item_parts[0]] = config_item_parts[1]

    package_config = {}
    if manifest.configTemplate is not None and len(manifest.configTemplate) > 0:
        for param_name, config_parameter in manifest.configTemplate.items():
            param_string_value = config_strings.get(param_name)
            if param_string_value is None:
                if config_parameter.default is not None:
                    package_config[param_name] = config_parameter.default
                else:
                    abort(f"Must provide value for config parameter {param_name}")
            else:
                package_config[param_name] = config_parameter.parameter_value_from_string(
                    param_string_value
                )

    package_instance_handle = manifest.handle
    try:
        existing_instance = PackageInstance.get(client, handle=package_instance_handle)
        existing_instance.delete()
    except SteamshipError as e:
        if "Unable to find" not in e.message:
            abort(e.message)

    package_instance = client.use(manifest.handle, config=package_config)

    output = {
        "invocation_url": package_instance.invocation_url,
        "version_handle": package_instance.package_version_handle,
        "config": package_instance.config,
    }
    click.echo(json.dumps(output, indent="  "))


cli.add_command(login)
cli.add_command(deploy)
cli.add_command(ships)
cli.add_command(test_instance)

if __name__ == "__main__":
    deploy([])
