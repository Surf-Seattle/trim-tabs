import click
import time
from utils import pins


@click.group()
def main():
    """The CLI of Trim-Tab Utilities."""
    pass


@main.command(short_help="Command a specific pin high or low")
@click.argument(
    "pin_number",
    type=click.Choice([str(x) for x in pins.configuration()]),
    required=True,
)
@click.option("--high", "action", flag_value="high")
@click.option("--low", "action", flag_value="low")
@click.option("--cycle", "action", flag_value="cycle", default=True)
@click.option("--duration", required=False, default=2)
def pin(pin_number: int, action: int, duration) -> None:
    """Set a pin high, low, or cycle it high then low."""
    pin_number = int(pin_number)
    pins.set_as_output([pin_number])
    if action == "high":
        pins.high(pin_number)
    elif action == "low":
        pins.low(pin_number)
    elif action == "cycle":
        pins.high(pin_number, duration)


@main.command(short_help="Cycle configured pins")
@click.option("--duration", required=False, default=2)
@click.option("--cooldown", required=False, default=1)
def configured(duration: int, cooldown: int) -> None:
    pins.set_as_output(list(pins.configuration()))
    for pin_number, pin_name in pins.configuration().items():
        click.echo(f"({pin_number}) {pin_name.ljust(40)}\t HIGH", nl=False)
        pins.high(pin_number, int(duration))
        click.echo("\tLOW")
        time.sleep(int(cooldown))


if __name__ == "__main__":
    main()
