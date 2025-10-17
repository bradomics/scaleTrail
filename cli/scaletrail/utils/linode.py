from typing import Any, Dict, List, Optional
import inquirer
from scaletrail.utils import formatting

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
    choices = [(formatting._row(inst), inst["id"]) for inst in instances_sorted]

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