import re

import click
from click import BadParameter

from steamship import Steamship
from steamship.data.user import User


def validate_handle(handle: str) -> str:
    if re.fullmatch(r"[a-z\-]+", handle) is not None:
        return handle
    else:
        raise BadParameter("Handle must only include lowercase letters and -")


def manifest_init_wizard(client: Steamship):
    click.echo(
        click.style(
            "It looks like you don't yet have a steamship.json to deploy. Let's create one.",
            fg="cyan",
        )
    )

    deployable_type = click.prompt(
        "Is this a package or a plugin?",
        default="package",
        type=click.Choice(["package", "plugin"]),
        show_choices=False,
    )

    handle = click.prompt(
        f"What handle would you like to use for your {deployable_type}? Valid characters are a-z and -",
        value_proc=validate_handle,
    )

    # TODO: claim the handle right here!

    version_handle = "0.0.1"

    public = click.confirm(f"Do you want this {deployable_type} to be public?", default=True)

    user = User.current(client)

    author = click.prompt("How should we list your author name?", default=user.handle)

    # TODO: Config variables

    tagline = None
    author_github = None
    if public:
        tagline = click.prompt(f"Want to give the {deployable_type} a tagline?", default="")
        author_github = click.prompt(
            "If you'd like this associated with your github account, please enter it", default=""
        )

    manifest = {
        "type": deployable_type,
        "handle": handle,
        "version": version_handle,
        "description": "",
        "author": author,
        "entrypoint": "api.handler",
        "public": public,
        "build_config": {"ignore": ["tests", "examples"]},
        "configTemplate": {},
        "steamshipRegistry": {
            "tagline": tagline,
            "tagline2": None,
            "usefulFor": None,
            "videoUrl": None,
            "githubUrl": None,
            "demoUrl": None,
            "blogUrl": None,
            "jupyterUrl": None,
            "authorGithub": author_github,
            "authorName": author,
            "authorEmail": None,
            "authorTwitter": None,
            "authorUrl": None,
            "tags": [],
        },
    }
    print(manifest)
