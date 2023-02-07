import click

import steamship


def requirements_init_wizard():
    click.secho(
        "Steamship uses requirements.txt to specify dependencies. You do not currently have a requirements.txt in this directory.",
        fg="yellow",
    )
    if not click.confirm("Would you like to create one automatically?", default=True):
        click.secho("Please manually create a requirements.txt and try again.")
        click.get_current_context().abort()

    with open("requirements.txt", "w") as requirements_file:
        requirements_file.write(f"steamship=={steamship.__version__}\n")

    click.secho(
        "Created a requirements.txt with the steamship dependency. If you need others, they must be added manually."
    )
