import logging
import sys
import time
from os import path

import click

import steamship
from steamship import Steamship, SteamshipError
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


def initialize():
    logging.root.setLevel(logging.FATAL)
    click.echo(f"Steamship PYTHON cli version {steamship.__version__}")


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


cli.add_command(login)
cli.add_command(deploy)
cli.add_command(ships)

if __name__ == "__main__":
    deploy([])
