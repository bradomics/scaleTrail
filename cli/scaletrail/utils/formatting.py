from rich.console import Console
from rich_pyfiglet import RichFiglet

console = Console()

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
# Provides color mapping for different environments when displayed in the CLI
ENV_COLORS= {
    "dev": "blue",
    "staging": "purple",
    "prod": "green"
}