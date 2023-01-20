import sys
import time
from os import path

import click

from steamship import Steamship
from steamship.base.configuration import Configuration
from steamship.cli.manifest_init_wizard import manifest_init_wizard
from steamship.data.user import User


@click.group()
def cli():
    pass


@click.command()
def login():
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
        click.echo(
            click.style(
                f"🚢🚢🚢 Hooray! You're logged in with user handle: {user.handle} 🚢🚢🚢", fg="green"
            )
        )


@click.command()
def deploy():
    client = Steamship()
    if not path.exists("steamship.json"):
        manifest_init_wizard(client)

    with click.progressbar(
        length=10,
        fill_char="🚢",
        empty_char=" ",
        show_eta=False,
        show_percent=False,
        show_pos=True,
        label="Shipping your package",
    ) as bar:
        for _ in range(10):
            time.sleep(1)
            bar.update(1)


cli.add_command(deploy)
cli.add_command(login)
