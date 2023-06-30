import json
import logging
import signal
import sys
import time
from os import getenv, path
from typing import Optional

import click

import steamship
from steamship import Steamship, SteamshipError
from steamship.base.configuration import DEFAULT_WEB_BASE, Configuration
from steamship.cli.create_instance import (
    config_str_to_dict,
    create_instance,
    load_manifest,
    set_unset_params,
)
from steamship.cli.deploy import (
    PackageDeployer,
    PluginDeployer,
    bundle_deployable,
    update_config_template,
)
from steamship.cli.local_server.server import SteamshipHTTPServer
from steamship.cli.manifest_init_wizard import manifest_init_wizard
from steamship.cli.requirements_init_wizard import requirements_init_wizard
from steamship.cli.ship_spinner import ship_spinner
from steamship.cli.utils import find_api_py, get_api_module
from steamship.data.manifest import DeployableType, Manifest
from steamship.data.user import User
from steamship.invocable.lambda_handler import get_class_from_module


@click.group()
def cli():
    pass


def initialize(suppress_message: bool = False):
    logging.root.setLevel(logging.FATAL)
    if not suppress_message:
        click.echo(f"Steamship Python CLI version {steamship.__version__}")


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
@click.option(
    "--port",
    "-p",
    type=int,
    default=8080,
    help="Port to host the server on.",
)
@click.option(
    "--invocable_handle",
    "-i",
    type=str,
    default=None,
    help="Handle of the package or plugin being hosted.",
)
@click.option(
    "--invocable_version_handle",
    "-v",
    type=str,
    default=None,
    help="Handle of the package or plugin version being hosted.",
)
@click.option(
    "--invocable_instance_handle",
    "-h",
    type=str,
    default=None,
    help="Handle of the package or plugin instance being hosted.",
)
@click.option(
    "--api_key",
    "-k",
    type=str,
    default=None,
    help="API Key to hard-code for hosting.",
)
@click.option(
    "--ngrok",
    "-n",
    is_flag=True,
    help="Whether to create a public ngrok URL.",
)
@click.option(
    "--ui",
    "-u",
    is_flag=True,
    help="Whether to connect to graphical interface.",
)
@click.option(
    "--config",
    "-c",
    type=str,
    required=False,
    help="Instance configuration. May be inline JSON or a path to a file. If not specified, "
    "an empty configuration dictionary will be passed to the instance.",
)
def serve(
    port: int = 8080,
    invocable_handle: Optional[str] = None,
    invocable_version_handle: Optional[str] = None,
    invocable_instance_handle: Optional[str] = None,
    api_key: Optional[str] = None,
    ngrok: Optional[bool] = False,
    ui: Optional[bool] = True,
    config: Optional[str] = None,
):
    """Serve the local invocable"""
    initialize()
    path = find_api_py()
    api_module = get_api_module(path)
    invocable_class = get_class_from_module(api_module)
    base_url = "http://localhost"
    click.secho(f"Found Invocable: {invocable_class.__name__}")
    manifest = load_manifest()
    invocable_config, is_file = config_str_to_dict(config)
    set_unset_params(config, invocable_config, is_file, manifest)
    add_port_to_invocable_url = True

    if ngrok or ui:
        try:
            from pyngrok import ngrok
        except BaseException:
            click.secho("Shut down.")
            click.secho("⚠️ Unable to create public URL with ngrok. Please either:")
            click.secho("   1) Install pyngrok (`pip install pyngrok`) and re-run, or")
            click.secho("   2) Run without the --ngrok flag")
            exit(1)

        http_tunnel = ngrok.connect(port, bind_tls=True)
        public_url = http_tunnel.public_url
        click.secho(f" 🌎 Public URL: {public_url}")
        base_url = public_url
        add_port_to_invocable_url = False  # NGROK's URL will redirect to the local port already

    server = SteamshipHTTPServer(
        invocable_class,
        base_url=base_url,
        port=port,
        invocable_handle=invocable_handle,
        invocable_version_handle=invocable_version_handle,
        invocable_instance_handle=invocable_instance_handle,
        default_api_key=api_key,
        config=invocable_config,
        add_port_to_invocable_url=add_port_to_invocable_url,
    )
    if ui:
        web_base = DEFAULT_WEB_BASE
        try:
            config = Configuration()
            web_base = config.web_base
        except BaseException:
            click.secho(
                "Warning: unable to read Steamship configuration from disk. Have you logged in with `ship login`?"
            )

        click.secho("")
        click.secho("To view the graphical UI, visit: ")
        click.secho(f"    {web_base}/debug?endpoint={public_url}/answer")

    def on_exit(signum, frame):
        click.secho("Shutting down server.")
        server.stop()
        click.secho("Shut down.")
        exit(1)

    signal.signal(signal.SIGINT, on_exit)

    click.secho(f"Starting development server on port {server.port}")
    server.start()
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

    thing_url = f"{client.config.web_base}{deployable_type.value}s/{manifest.handle}"
    click.echo(
        f"Deployment was successful. View and share your new {deployable_type.value} here:\n\n{thing_url}\n"
    )

    # Common error conditions:
    # - Package/plugin handle already taken. [handled; asks user for new]
    # - Version handle already deployed. [handled; asks user for new]
    # - Bad parameter configuration. [mitigated by deriving template from Config object]
    # - Package content fails health check (ex. bad import) [Error caught while checking config object]


@click.command()
def info():
    """Displays information about the current Steamship user.

    This is useful to help users (in a support or hackathon context) test whether they have configured their
    Steamship environment correctly.
    """
    initialize()
    click.echo("\nSteamship Client Info\n=====================\n")

    if Configuration.default_config_file_has_api_key() or getenv("STEAMSHIP_API_KEY", None):
        # User is logged in!
        client = None
        try:
            client = Steamship()
        except BaseException:
            click.secho("Incorrect API key or network error.\n", fg="red")
            click.secho(
                "Your Steamship API Key is set, but we were unable to use it to fetch your account information.\n"
            )
            click.secho("- If you are on your own computer, run `ship login` to login.")
            click.secho(
                "- If you are in Replit, add the STEAMSHIP_API_KEY secret, then close and re-open this shell.\n"
            )
            return

        try:
            user = User.current(client)
            click.echo(f"User handle: {user.handle}")
            click.echo(f"User ID:     {user.id}")
            click.echo(f"Profile:     {client.config.profile}")
            click.echo("\nReady to ship! 🚢🚢🚢\n")

        except BaseException:
            click.secho("Incorrect API key or network error.\n", fg="red")
            click.secho(
                "Your Steamship API Key is set, but we were unable to use it to fetch your account information.\n"
            )
            click.secho("- If you are on your own computer, run `ship login` to login.")
            click.secho(
                "- If you are in Replit, add the STEAMSHIP_API_KEY secret, then close and re-open this shell.\n"
            )
    else:
        click.secho("You are not logged in.\n")
        click.secho("- If you are on your own computer, run `ship login` to login.")
        click.secho(
            "- If you are in Replit, add the STEAMSHIP_API_KEY secret, then close and re-open this shell.\n"
        )


@click.command()
@click.option(
    "--workspace",
    "-w",
    required=True,
    type=str,
    help="Workspace handle used for scoping logs request. All requests MUST be scoped by workspace.",
)
@click.option(
    "--offset",
    "-o",
    default=0,
    type=int,
    help="Starting index from sorted logs to return a chunk. Used for paging. Defaults to 0.",
)
@click.option(
    "--number",
    "-n",
    default=50,
    type=int,
    help="Number of logs to return in a single batch. Defaults to 50.",
)
@click.option(
    "--package",
    "-p",
    type=str,
    help="Package handle. Used to filter logs returend to a specific package (across all instances).",
)
@click.option(
    "--instance",
    "-i",
    type=str,
    help="Instance handle. Used to filter logs returned to a specific instance of a package.",
)
@click.option(
    "--version",
    "-v",
    type=str,
    help="Version handle. Used to filter logs returned to a specific version of a package.",
)
@click.option(
    "--path",
    "request_path",
    type=str,
    help="Path invoked by a client operation. Used to filter logs returned to a specific invocation path.",
)
@click.option(
    "--with-fields",
    "-f",
    "field_values",
    type=str,
    help="Dictionary of log field values (format: key1=value1,key2=value2,...). Used to filter logs returned.",
)
def logs(
    workspace: str,
    offset: int,
    number: int,
    package: Optional[str] = None,
    instance: Optional[str] = None,
    version: Optional[str] = None,
    request_path: Optional[str] = None,
    field_values: Optional[str] = None,
):
    """Retrieve logs within a workspace."""

    initialize(suppress_message=True)
    client = None
    try:
        client = Steamship(workspace=workspace)
    except SteamshipError as e:
        raise click.UsageError(message=e.message)

    value_dict = {}
    if field_values:
        try:
            for item in field_values.split(","):
                key, value = item.split("=")
                value_dict[key] = value
        except ValueError:
            raise click.UsageError(
                message="Invalid dictionary format for fields. Please provide a dictionary in the "
                "format: key1=value1,key2=value2,..."
            )

    click.echo(
        json.dumps(
            client.logs(offset, number, package, instance, version, request_path, value_dict)
        )
    )


cli.add_command(login)
cli.add_command(deploy)
cli.add_command(info)
cli.add_command(deploy, name="it")
cli.add_command(ships)
cli.add_command(logs)
cli.add_command(serve)
cli.add_command(create_instance, name="use")


if __name__ == "__main__":
    serve([])
