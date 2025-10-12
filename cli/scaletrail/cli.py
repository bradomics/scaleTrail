import typer
import inquirer
from pathlib import Path

from rich.console import Console
from rich_pyfiglet import RichFiglet

console = Console()
app = typer.Typer()

CONTINENT_CHOICES = [
    "North America",
    "Europe",
    "Asia",
    "South America",
    "Oceania",
    "Show all regions"
]

NORTH_AMERICA_LINODE_REGIONS = [
    "ca-central",
    "us-central",
    "us-east",
    "us-iad",
    "us-lax",
    "us-mia",
    "us-ord",
    "us-sea",
    "us-southeast",
    "us-west"
]

EUROPE_LINODE_REGIONS = [
    "de-fra-2",
    "es-mad",
    "eu-central",
    "eu-west",
    "fr-par",
    "gb-lon",
    "it-mil",
    "nl-ams",
    "se-sto"
]

ASIA_LINODE_REGIONS = [
    "ap-northeast",
    "ap-south",
    "ap-west",
    "id-cgk",
    "in-bom-2",
    "in-maa",
    "jp-osa",
    "jp-tyo-3",
    "sg-sin-2"
]

SOUTH_AMERICA_LINODE_REGIONS = [
    "br-gru"
]

OCEANIA_LINODE_REGIONS = [
    "au-mel",
    "ap-southeast"
]

CONTINENT_TO_REGIONS = {
    "North America": NORTH_AMERICA_LINODE_REGIONS,
    "Europe": EUROPE_LINODE_REGIONS,
    "Asia": ASIA_LINODE_REGIONS,
    "South America": SOUTH_AMERICA_LINODE_REGIONS,
    "Oceania": OCEANIA_LINODE_REGIONS,
}

def show_banner():
    """Helper function to print the CLI banner."""
    rich_fig = RichFiglet(
        "ScaleTrail",
        font="slant",
        colors=["#fd0083 ", "#0abac7"],
        horizontal=True,
    )
    console.print(rich_fig)
    console.print("")  # Add a blank line for spacing
    console.print("[dim]ScaleTrail CLI v0.1.0[/dim]")
    console.print("")  # Add a blank line for spacing
    console.print("[cyan]Welcome to ScaleTrail![/cyan]")
    console.print("")
    console.print("[bold]Helpful links:[/bold]")
    console.print("* [link=https://github.com/bradomics/scaleTrail?tab=readme-ov-file#scaletrail]README[/link]")
    console.print("")

@app.command()
def init(
    project_name: str = typer.Option(
        "",
        help="The name of the project to initialize.",
    ),
    continent: str = typer.Option(
        "",
        help="Continent for infrastructure (North America, Europe, Asia, South America, Oceania).",
    ),
    linode_region: str = typer.Option(
        "",
        help="The Linode region slug for your desired infrastructure's region.",
    ),
    instance_type: str = typer.Option(
        "",
        help="The Linode instance type for your desired infrastructure.",
    ),
    image: str = typer.Option(
        "",
        help="The Linode image slug for your desired infrastructure's base image.",
    ),
    backups_enabled: bool = typer.Option(
        False,
        help="Whether to enable backups for the Linode instance.",
    ),
    tags: str = typer.Option(
        "",
        help="Comma-separated tags to apply to the Linode instance.",
    ),
    stripe_api_key: str = typer.Option(
        "",
        help="Your Stripe API key for payment processing.",
    ),
    sendgrid_api_key: str = typer.Option(
        "",
        help="Your SendGrid API key for payment processing.",
    )
):
    """Initializes the project configuration."""
    # The banner and links are now part of the init command's execution flow.
    show_banner()

    if not project_name:
        project_name = typer.prompt("Project name")

    # Allow CLI overrides: if both continent and region were provided, skip prompts
    if not linode_region:
        if not continent:
            ans = inquirer.prompt([
                inquirer.List("continent",
                    message="Select a continent (or show all regions)",
                    choices=CONTINENT_CHOICES,
                    carousel=True)
            ]) or {}
            continent = ans.get("continent", "")
            if not continent:
                raise typer.Exit(1)

        if continent == "Show all regions":
            region_choices = sum(CONTINENT_TO_REGIONS.values(), [])  # flatten
        else:
            # normalize if user passed --continent europe
            norm = continent.strip().lower()
            alias = {c.lower(): c for c in CONTINENT_CHOICES if c != "Show all regions"}
            continent = alias.get(norm, continent)
            region_choices = CONTINENT_TO_REGIONS.get(continent, [])

        ans = inquirer.prompt([
            inquirer.List("linode_region",
                message=f"Select a Linode region{f' in {continent}' if continent!='Show all regions' else ''}",
                choices=region_choices,
                carousel=True)
        ]) or {}
        linode_region = ans.get("linode_region", "")
    if not linode_region:
        raise typer.Exit(1)

    if not instance_type:
        instance_type = typer.prompt("Instance type")

    if not image:
        image = typer.prompt("Image")

    if not backups_enabled:
        backups_enabled = typer.prompt("Image")

    if not tags:
        tags = typer.prompt("Tags (comma-separated)")

    if not stripe_api_key:
        stripe_api_key = typer.prompt("Stripe API key")

    if not sendgrid_api_key:
        sendgrid_api_key = typer.prompt("SendGrid API key")

    config_dir = Path.home() / f".{project_name}"
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "config.ini"
    config_file.write_text("[settings]\ninitialized=True\n")
    typer.echo("")
    typer.echo(f"Initialized project '{project_name}' in {config_dir}")

# Other commands will not show the banner
@app.command()
def run():
    """Runs the application."""
    typer.echo("Running the application...")

if __name__ == "__main__":
    app()
