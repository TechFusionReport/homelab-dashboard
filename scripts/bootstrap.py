"""Initialize private configuration without replacing existing settings."""
from pathlib import Path
from shutil import copyfile


def bootstrap(root: Path) -> None:
    runtime = root / "local" / "homepage"
    runtime.mkdir(parents=True, exist_ok=True)
    for source in sorted((root / "config").glob("*.yaml")):
        target = runtime / source.name
        if not target.exists():
            copyfile(source, target)
            print(f"Created local/homepage/{source.name}")
    env = root / ".env"
    if not env.exists():
        copyfile(root / ".env.example", env)
        print("Created .env with placeholders")
    print("Edit .env locally before starting Docker Compose.")


if __name__ == "__main__":
    bootstrap(Path(__file__).resolve().parents[1])
