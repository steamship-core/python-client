import re

import click
from click import BadParameter

from steamship import Steamship
from steamship.data.manifest import Manifest, PluginConfig, SteamshipRegistry
from steamship.data.user import User


def validate_handle(handle: str) -> str:
    if re.fullmatch(r"[a-z\-]+", handle) is not None:
        return handle
    else:
        raise BadParameter("Handle must only include lowercase letters and -")


def validate_version_handle(handle: str) -> str:
    if re.fullmatch(r"[a-z0-9\-.]+", handle) is not None:
        return handle
    else:
        raise BadParameter("Handle must only include lowercase letters, numbers, . and -")


def manifest_init_wizard(client: Steamship):
    click.secho(
        "It looks like you don't yet have a steamship.json to deploy. Let's create one.",
        fg="cyan",
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

    plugin_detail = None
    if deployable_type == "plugin":
        plugin_type = click.prompt(
            "What type of plugin is this?",
            default="tagger",
            type=click.Choice(
                ["tagger", "blockifier", "exporter", "fileImporter", "corpusImporter"]
            ),
            show_choices=True,
        )
        if plugin_type == "tagger":
            trainable = click.confirm("Is the plugin trainable?", default=False)
        else:
            trainable = False
        plugin_detail = PluginConfig(isTrainable=trainable, type=plugin_type)

    public = click.confirm(f"Do you want this {deployable_type} to be public?", default=True)

    user = User.current(client)

    author = click.prompt("How should we list your author name?", default=user.handle)

    tagline = None
    author_github = None
    if public:
        tagline = click.prompt(f"Want to give the {deployable_type} a tagline?", default="")
        author_github = click.prompt(
            "If you'd like this associated with your github account, please your github username",
            default="",
        )

    tag_string = click.prompt(
        f"Want to give the {deployable_type} some tags? (comma separated)", default="Prompt API"
    )
    tags = [tag.strip() for tag in tag_string.split(",")]

    return Manifest(
        type=deployable_type,
        handle=handle,
        version=version_handle,
        description="",
        author=author,
        public=public,
        plugin=plugin_detail,
        build_config={"ignore": ["tests", "examples"]},
        configTemplate={},
        steamshipRegistry=SteamshipRegistry(
            tagline=tagline, authorGithub=author_github, authorName=author, tags=tags
        ),
    )
