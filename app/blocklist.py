import yaml
from pathlib import Path
import click

BLOCKLIST_FILE = Path("blocked_employers.yaml")


def load_blocklist(filepath=BLOCKLIST_FILE):
    if not filepath.exists():
        return []
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
        return data.get("blocked_employers", [])


def save_blocklist(employers, filepath=BLOCKLIST_FILE):
    with open(filepath, "w") as f:
        yaml.dump({"blocked_employers": sorted(set(employers))}, f)


def add_to_blocklist(new_name, filepath=BLOCKLIST_FILE):
    employers = load_blocklist(filepath)
    if new_name not in employers:
        employers.append(new_name)
        save_blocklist(employers, filepath)
        print(f"'{new_name}' added to blocklist.")
    else:
        print(f"'{new_name}' is already in the blocklist.")


def remove_from_blocklist(name_to_remove, filepath=BLOCKLIST_FILE):
    employers = load_blocklist(filepath)
    if name_to_remove in employers:
        employers.remove(name_to_remove)
        save_blocklist(employers, filepath)
        print(f"'{name_to_remove}' removed from blocklist.")
    else:
        print(f"'{name_to_remove}' is not in the blocklist.")


@click.group()
def cli():
    """Manage the blocked employers list (for hiring/consulting filters)."""
    pass


@cli.command()
@click.argument("employer_name")
def add(employer_name):
    """Add an employer to the blocklist."""
    add_to_blocklist(employer_name)


@cli.command()
@click.argument("employer_name")
def remove(employer_name):
    """Remove an employer from the blocklist."""
    remove_from_blocklist(employer_name)


@cli.command(name="list")
def list_employers():
    """Show all blocked employers."""
    blocked = load_blocklist()
    if blocked:
        click.echo("Blocked Employers:")
        for name in blocked:
            click.echo(f" - {name}")
    else:
        click.echo("No blocked employers yet.")


if __name__ == "__main__":
    cli()
