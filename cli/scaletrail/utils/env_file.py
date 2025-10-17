from pathlib import Path
from rich.console import Console
console = Console()
import os


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