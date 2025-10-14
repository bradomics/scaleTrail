import typer
import inquirer

from pathlib import Path
import os
import requests
from typing import Any, Dict, List, Optional

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

def api_key_present(env_key):
    current_dir = Path.cwd()
    env_path = current_dir / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.startswith(f"{env_key}="):
                    key = line.split("=", 1)[1].strip()
                    if key:
                        console.print(f"{env_key} found.")
                        return True
    return False

def add_api_key(env_key, env_value):
    """Adds or updates an API key in the .env file."""
    env_path = Path.cwd() / ".env"

    # Ensure the file exists
    if not env_path.exists():
        env_path.touch()

    # Read all existing lines
    with open(env_path, "r") as f:
        lines = f.readlines()

    key_exists = False
    new_lines = []

    for line in lines:
        if line.startswith(f"{env_key}="):
            new_lines.append(f"{env_key}={env_value}\n")
            key_exists = True
        else:
            new_lines.append(line)

    # If the key was not found, append it
    if not key_exists:
        new_lines.append(f"{env_key}={env_value}\n")

    # Write updated lines back to .env
    with open(env_path, "w") as f:
        f.writelines(new_lines)

    print(f"Set {env_key} in {env_path}")

def find_or_create_env_file():
    """Creates a .env file in the current directory if it doesn't exist."""
    current_dir = Path.cwd()
    env_path = current_dir / ".env"

    if env_path.exists():
        console.print(f".env found at: {env_path}")
    else:
        console.print(f"No .env found at {env_path}, creating one...")
        file_path = os.path.join(".", ".env") 

        with open(file_path, "w") as f:
            f.write("# Environment variables for ScaleTrail\n")



def _pick_price(item: Dict[str, Any], region_id: str) -> Dict[str, float]:
    """
    Return {"hourly": x, "monthly": y} using region override if present,
    otherwise the base price.
    """
    base = item.get("price", {}) or {}
    hourly = base.get("hourly")
    monthly = base.get("monthly")

    for rp in item.get("region_prices", []) or []:
        if rp.get("id") == region_id:
            hourly = rp.get("hourly", hourly)
            monthly = rp.get("monthly", monthly)
            break
    return {"hourly": float(hourly), "monthly": float(monthly)}

def _pick_backup_price(item: Dict[str, Any], region_id: str) -> Optional[Dict[str, float]]:
    """
    Same as _pick_price but for the backups addon. Returns None if no backups addon.
    """
    backups = (item.get("addons") or {}).get("backups")
    if not backups:
        return None

    base = (backups.get("price") or {})
    hourly = base.get("hourly")
    monthly = base.get("monthly")

    for rp in backups.get("region_prices", []) or []:
        if rp.get("id") == region_id:
            hourly = rp.get("hourly", hourly)
            monthly = rp.get("monthly", monthly)
            break

    return {"hourly": float(hourly), "monthly": float(monthly)}

def _gb_from_mb(mb: int) -> float:
    return mb / 1024.0

def _fmt_money(v: float) -> str:
    return f"${v:,.2f}"

def _row(inst: dict) -> str:
    label = inst.get("label", "")
    cls = inst.get("class", "")
    mem_gb = _gb_from_mb(inst.get("memory_mb", 0))
    disk_gb = _gb_from_mb(inst.get("disk_mb", 0))
    xfer_gb = inst.get("transfer_gb", 0)
    monthly = inst.get("price_monthly", 0.0)
    backups = inst.get("backups_monthly", 0.0)

    # Tweak widths to taste; these work well in a standard terminal
    return (
        f"{label:<18} | "
        f"{cls:<9} | "
        f"{mem_gb:>6.0f} | "
        f"{disk_gb:>7.0f} | "
        f"{xfer_gb:>11} | "
        f"{_fmt_money(monthly):>10} | "
        f"{_fmt_money(backups):>14}"
    )

def choose_instance(instances: list, message: str = "Select a Linode plan"):
    instances_sorted = sorted(instances, key=lambda x: x.get("price_monthly", 0))

    header = (
        f"{'Label':<18} | "
        f"{'Class':<9} | "
        f"{'Mem GB':>6} | "
        f"{'Disk GB':>7} | "
        f"{'Transfer GB':>11} | "
        f"{'Monthly':>10} | "
        f"{'Backups Monthly':>14}"
    )

    # Show header above the prompt
    print(header)
    print("-" * len(header))

    # python-inquirer expects choices as strings OR (name, value) tuples
    choices = [(_row(inst), inst["id"]) for inst in instances_sorted]

    questions = [
        inquirer.List(
            "selected",
            message=message,
            choices=choices,
            carousel=True,  # supported in python-inquirer
        )
    ]
    answers = inquirer.prompt(questions)
    if not answers:
        return None

    selected_id = answers["selected"]
    # return full instance (not just id)
    return next((i for i in instances if i["id"] == selected_id), None)

def get_instances_for_region(resp: Dict[str, Any], region_id: str, 
                             include_classes: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Flatten the Linode types payload into a list of dicts with the right
    price for `region_id`. Optionally filter by class (e.g., ["standard","dedicated"]).
    """
    out: List[Dict[str, Any]] = []
    for itm in resp.get("data", []) or []:
        if include_classes and itm.get("class") not in include_classes:
            continue

        price = _pick_price(itm, region_id)
        backup_price = _pick_backup_price(itm, region_id)

        out.append({
            "id": itm.get("id"),
            "label": itm.get("label"),
            "class": itm.get("class"),
            "vcpus": itm.get("vcpus"),
            "memory_mb": itm.get("memory"),
            "disk_mb": itm.get("disk"),
            "transfer_gb": itm.get("transfer"),
            "gpus": itm.get("gpus"),
            "network_out_mbps": itm.get("network_out"),
            "price_hourly": price["hourly"],
            "price_monthly": price["monthly"],
            "backups_hourly": backup_price["hourly"] if backup_price else None,
            "backups_monthly": backup_price["monthly"] if backup_price else None,
        })
    return out



@app.command()
def init(
    project_name: str = typer.Option(
        "",
        help="The name of the project to initialize.",
    ),
    linode_api_key: str = typer.Option(
        "",
        help="Your Linode API key for managing infrastructure.",
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

    # We'll first need to ensure the .env file exists along with API keys necessary to trigger
    # infrastructure changes.
    find_or_create_env_file()
    if not api_key_present("LINODE_API_KEY"):
        linode_api_key = typer.prompt("Linode API key", hide_input=True)
        add_api_key("LINODE_API_KEY", linode_api_key)

    if not api_key_present("CLOUDFLARE_ACCOUNT_ID"):
        cloudflare_account_id = typer.prompt("Cloudflare account ID", hide_input=True)
        add_api_key("CLOUDFLARE_ACCOUNT_ID", cloudflare_account_id)

    if not api_key_present("CLOUDFLARE_API_KEY"):
        cloudflare_api_key = typer.prompt("Cloudflare API key", hide_input=True)
        add_api_key("CLOUDFLARE_API_KEY", cloudflare_api_key)
        
    if not api_key_present("STRIPE_API_KEY"):
        stripe_api_key = typer.prompt("Stripe API key", hide_input=True)
        add_api_key("STRIPE_API_KEY", stripe_api_key)

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
        console.print(f"Selected region: {linode_region}")
                # Use continent to filter for available Linode types
        url = "https://api.linode.com/v4/linode/types"

        payload = {}
        headers = {
            'Accept': 'application/json',
            'Authorization': linode_api_key
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        console.print('Available Linode instance types:')
        # region_id could be "us-east", "us-ord", "br-gru", "id-cgk", etc.
        instances = get_instances_for_region(response.json(), region_id="br-gru",
                                            include_classes=["nanode","standard","dedicated","premium"])
        # Assuming `instances` is your processed list (region-adjusted pricing)
        selected = choose_instance(instances, message="Pick a size for your Linode instance")
        if selected:
            # selected is the whole instance dict (change value=inst["id"] above if you only want the id)
            print("You chose:", selected["id"], "-", selected["label"])
                
            # `instances` is now a list of rows with region-adjusted hourly/monthly (and backups) pricing.
            console.print(instances)

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
