import typer
from pathlib import Path

from rich.console import Console
from rich_pyfiglet import RichFiglet

console = Console()
app = typer.Typer()

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
    linode_region: str = typer.Option(
        "",
        help="The Linode region slug for your desired infrastructure's region.",
    ),
):
    """Initializes the project configuration."""
    # The banner and links are now part of the init command's execution flow.
    show_banner()

    if not project_name:
        project_name = typer.prompt("Project name")

    if not linode_region:
        linode_region = typer.prompt("Linode region")

    if not instance_type:
        instance_type = typer.prompt("Instance type")

    if not image:
        image = typer.prompt("Image")

    if not backups_enabled:
        backups_enabled = typer.prompt("Image")

    if not tags:
        tags = typer.prompt("Tags (comma-separated)")

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
