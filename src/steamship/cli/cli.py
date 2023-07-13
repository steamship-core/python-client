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
from steamship.invocable.dev_logging_handler import DevelopmentLoggingHandler
from steamship.invocable.lambda_handler import get_class_from_module
from steamship.utils.repl import HttpREPL


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


def _run_ngrok(local_port: int) -> str:
    """Create an NGROK URL directed at `local_port`."""
    try:
        from pyngrok import ngrok
    except BaseException:
        click.secho("⚠️ Public API: Unable to start ngrok. Please either:")
        click.secho("   - Install pyngrok via `pip install pyngrok`")
        click.secho("   - Use the --no_ngrok flag")
        click.secho("   NGROK is only necessary if you wish to debug Telegram or Slack locally.")
        exit(1)
    try:
        http_tunnel = ngrok.connect(local_port, bind_tls=True)
    except BaseException:
        click.secho(f"⚠️ Public API: Unable to bind ngrok to port {local_port}")
        click.secho("   - Try running with a different port via the  --port flag.")
        exit(1)

    ngrok_api_url = http_tunnel.public_url
    return ngrok_api_url


def _run_local_server(
    local_port: int,
    instance_handle: Optional[str] = None,
    config: Optional[str] = None,
    workspace: Optional[str] = None,
    base_url: Optional[
        str
    ] = None,  # If provided, will override the default calculation, eg for ngrok
) -> str:
    """Start the local API Server."""
    logging.info(
        f"Starting local server. port={local_port}, instance_handle={instance_handle}, workspace={workspace}"
    )

    path = find_api_py()
    api_module = get_api_module(path)
    invocable_class = get_class_from_module(api_module)

    # Use the provided base url (e.g. from NGROK) or default to localhost
    _base_url = base_url or "http://localhost"

    logging.info(f"Local server base URL (for PackageService configuration) is {_base_url}")

    if not invocable_class:
        logging.error("Local server startup unable to find Steamship service.")
        click.secho("⚠️ Local API: Unable to find Steamship service. Please:")
        click.secho(
            "   - Check to see that you have an api.py file containing an AgentService or PackageService "
        )
        exit(1)

    manifest = load_manifest()

    if not manifest:
        logging.error("Local server startup unable to find Steamship manifest.")
        click.secho("⚠️ Local API: Unable to find your steamship.json file")
        exit(1)

    invocable_config, is_file = config_str_to_dict(config)
    set_unset_params(config, invocable_config, is_file, manifest)

    server = SteamshipHTTPServer(
        invocable_class,
        base_url=_base_url,
        port=local_port,
        invocable_handle=manifest.handle,
        invocable_version_handle=manifest.version,
        invocable_instance_handle=instance_handle,
        config=invocable_config,
        workspace=workspace,
    )
    try:
        server.start()
    except SteamshipError as e:
        click.secho(f"⚠️ Local API: {e.message}")
        if "validation error" in e.message:
            click.secho(
                "💡 Suggestion: Create a configuration file called config.json containing the required "
            )
            click.secho(
                "               configuration fields in your agent's configuration. Then run again with"
            )
            click.secho("               ship run local -c config.json")
            exit(-1)
    except BaseException as e:
        click.secho(f"⚠️ Local API: {e}")
        exit(-1)

    logging.info("Local server running.")

    def on_exit(signum, frame):
        logging.info("Local server shutting down.")
        click.secho("Shutting down server.")
        server.stop()
        click.secho("Shut down.")
        logging.info("Local server shut down complete.")
        exit(1)

    signal.signal(signal.SIGINT, on_exit)

    local_api_url = f"http://localhost:{server.port}"

    logging.info(f"Local server address: {local_api_url}")

    return local_api_url


def _run_web_interface(base_url: str) -> str:
    web_base = DEFAULT_WEB_BASE
    logging.info(f"Starting web interface. web_base={web_base} and base_url={base_url}")

    try:
        config = Configuration()
        web_base = config.web_base
    except BaseException:
        click.secho("⚠️ Web UI:  Unable to find Steamship Configuration. Please:")
        click.secho(
            "   - Run `ship login` to make sure you have Steamship credentials in your environment."
        )

    # Guarantee one and only one trailing /
    if not web_base.endswith("/"):
        web_base = f"{web_base}/"

    web_url = f"{web_base}debug?endpoint={base_url}/prompt"
    logging.info(f"Web interface url is: {web_url}")

    return web_url


def serve_local(
    port: int = 8443,
    instance_handle: Optional[str] = None,
    no_ngrok: Optional[bool] = False,
    no_repl: Optional[bool] = False,
    no_ui: Optional[bool] = False,
    config: Optional[str] = None,
    workspace: Optional[str] = None,
):
    """Serve the invocable on localhost. Useful for debugging locally."""
    dev_logging_handler = DevelopmentLoggingHandler.init_and_take_root()

    initialize()
    click.secho("Running your project...\n")

    # Report the logs
    click.secho(f"📝 Log file:   {dev_logging_handler.log_filename}")

    # Start the NGROK connection
    ngrok_api_url = None
    if not no_ngrok:
        ngrok_api_url = _run_ngrok(port)
        click.secho(f"🌎 Public API: {ngrok_api_url}")

    # Start the local API Server. This has to happen after NGROK because the port & url need to be plummed.
    try:
        local_api_url = _run_local_server(
            local_port=port,
            instance_handle=instance_handle,
            config=config,
            workspace=workspace,
            base_url=ngrok_api_url,
        )
    except BaseException as e:
        click.secho("⚠️ Local API:  Unable to start local server.")
        click.secho(e)
        exit(-1)

    if local_api_url:
        click.secho(f"🌎 Local API:  {local_api_url}")
    else:
        click.secho("⚠️ Local API:  Unable to start local server.")
        exit(-1)

    # Start the web UI
    if not no_ui:
        web_url = _run_web_interface(ngrok_api_url or local_api_url)
        if web_url:
            click.secho(f"🌎 Web UI:     {web_url}")

    if no_repl:
        while True:
            # We need to make sure the thread doesn't exit.
            time.sleep(1)
    else:
        click.secho("\n💬 Interactive REPL below. Type to interact.\n")
        prompt_url = f"{local_api_url or ngrok_api_url}/prompt"
        repl = HttpREPL(prompt_url=prompt_url, dev_logging_handler=dev_logging_handler)
        repl.run()


@click.command()
@click.option(
    "--port",
    "-p",
    type=int,
    default=8443,
    help="Port to host the server on.",
)
@click.option(
    "--instance_handle",
    "-h",
    type=str,
    default=None,
    help="Handle of the package or plugin instance being hosted.",
)
@click.option(
    "--no-ngrok",
    is_flag=True,
    default=False,
    help="Don't attempt to attach to ngrok.",
)
@click.option(
    "--no-ui",
    is_flag=True,
    default=False,
    help="Don't attempt to attach to a web UI.",
)
@click.option(
    "--no-repl",
    is_flag=True,
    default=False,
    help="Don't start a console REPL.",
)
@click.option(
    "--config",
    "-c",
    type=str,
    required=False,
    help="Instance configuration. May be inline JSON or a path to a file. If not specified, "
    "an empty configuration dictionary will be passed to the instance.",
)
@click.option(
    "--workspace",
    "-w",
    required=False,
    type=str,
    help="Workspace handle. The new instance will be created in this workspace. If not specified, "
    "the default workspace will be used.",
)
@click.argument(
    "environment", required=True, type=click.Choice(["local", "remote"], case_sensitive=False)
)
@click.pass_context
def run(
    ctx,
    environment: str,
    port: int = 8080,
    instance_handle: Optional[str] = None,
    no_ngrok: Optional[bool] = False,
    no_ui: Optional[bool] = False,
    no_repl: Optional[bool] = False,
    config: Optional[str] = None,
    workspace: Optional[str] = None,
):
    """Serve your invocable locally or on prod"""
    if environment == "local":
        serve_local(
            port=port,
            instance_handle=instance_handle,
            no_ngrok=no_ngrok,
            no_repl=no_repl,
            no_ui=no_ui,
            config=config,
            workspace=workspace,
        )
    else:
        if click.confirm("Do you want to deploy a new version first?", default=False):
            ctx.invoke(deploy)
        ctx.invoke(
            create_instance, workspace=workspace, instance_handle=instance_handle, config=config
        )


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
cli.add_command(run)
cli.add_command(create_instance, name="use")
