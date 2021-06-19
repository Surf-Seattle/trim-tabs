import os
import click

from utils import utilities

@click.group(
    help="The CLI for the Surf Application."
)
def main():
    pass

@main.command(
    help="Start the surf application."
)
@click.option(
    "--pins/--no_pins",
    required=True,
    default=True,
    help="Whether or not the RPi.GPIO module will be imported and calls to this module will be made. "
         "Use --no_pins when developing on any machine which is not a raspberry pi."
)
@click.option(
    "--fullscreen/--windowed",
    required=True,
    default=True,
    help="Whether or not the UI will load in fullscreen or windowed. "
         "`--fullscreen` is the default and will hide the mouse. "
         "Use `--windowed` when developing on a machine where you want to interact with the UI using a mouse."
)
def run(pins: bool, fullscreen: bool) -> None:

    os.environ['USE_PINS'] = "true" if pins else "false"
    os.environ['FULLSCREEN'] = "true" if fullscreen else "false"

    import main
    main.run()


@main.command(
    help="Write (or overwrite) configs from templates. "
         "Argument flags should be provided without values."
)
@click.option(
    '--all', 'which_config', flag_value='all',
    help="write all configuration files in `~/.surf/config/` from templates."
)
@click.option(
    '--control-surfaces', 'which_config', flag_value='control_surfaces.yml',
    help="write `~/.surf/config/control_surfaces.yml` from template."
)
@click.option(
    '--operating-modes', 'which_config', flag_value='operating_modes.yml',
    help="write `~/.surf/config/operating_modes.yml` from template."
)
def reset_config(which_config: str) -> None:
    utilities.update_config_from_template(which_config)

@main.command(
    help="Update a value in operating_modes.yml, which controls the travel time of contorl surfaces."
)
@click.option(
    '--mode', required=True, help="Which operating mode to update, these are the top level keys in the config file."
)
@click.option(
    '--concurrency', required=True, help="In the chosen mode, which pin-concurrency should be updated."
)
@click.option(
    '--context', required=True, help="Either `deploy` which is when the surfaces are in use, "
                                     "or `withdraw` which is the duration used when fully-retracting."
)
@click.option(
    '--value', required=True, help="A decimal value which is the number of seconds that 100% travel "
                                       "of this control surface should take."
)
def update_operating_mode(mode: str, concurrency: int, context: str, value: str):
    if not concurrency.isdigit():
        raise click.ClickException("The value passed to `--concurrency` must be an integer.")
    error_message = utilities.update_operating_mode_value(mode, int(concurrency), context, value)
    if error_message:
        raise click.ClickException(error_message)

@main.command(
    help="Update value of existing wave-profile."
)
@click.option(
    '--name', required=True, help="The name of the new profile."
)
@click.option(
    '--values', nargs=3, type=int, help="The values for the updated rofile. "
                                        "Each value may be between 0 and 100. "
                                        "Separate each value with a space. "
                                        "Provide the values in the order that the config-surfaces were configured."
)
def update_wave_profile(name: str, values: str) -> None:
    error_message = utilities.update_wave_profile(name, values)
    if error_message:
        raise click.ClickException(error_message)



@main.command(
    help="Create a new wave-profile"
)
@click.option(
    '--name', required=True, help="The name of the new profile."
)
@click.option(
    '--values', nargs=3, type=int, help="The control surface values for the new profile. "
                                        "Each value may be between 0 and 100. "
                                        "Separate each value with a space. "
                                        "Provide the values in the order that the config-surfaces were configured."
)
def new_wave_profile(name, values):
    error_message = utilities.create_new_wave_profile(name, values)
    if error_message:
        raise click.ClickException(error_message)

@main.command(
    help="Delete a new wave-profile"
)
@click.option(
    '--name', required=True, help="The name of the profile to delete."
)
def delete_wave_profile(name):
    error_message = utilities.delete_wave_profile(name)
    if error_message:
        raise click.ClickException(error_message)



@main.command(
    help="Run first time setup. This is done automatically when you run the application "
         "but you can also trigger it here without running the application."
)
def first_time_setup() -> None:
    utilities.first_time_setup_check()
    click.echo("\nEverything is ready to go!\n")


if __name__ == '__main__':
    main()