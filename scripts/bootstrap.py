"""Initialize private configuration without replacing existing settings."""
import argparse
from pathlib import Path
from shutil import copyfile

TARGETS = {
    "production": {"runtime": "local/homepage", "env": ".env"},
    "preview": {"runtime": "local/preview-homepage", "env": "local/preview.env"},
}
PREVIEW_TITLE_SUFFIX = " · Preview"
PREVIEW_BADGE = "- greeting:\n    text: Preview\n"


def preview_overlay(name: str, text: str) -> str:
    """Label preview runtime config; production templates never carry these labels."""
    if name == "settings.yaml":
        lines = text.split("\n")
        return "\n".join(line + PREVIEW_TITLE_SUFFIX if line.startswith("title: ") else line for line in lines)
    if name == "widgets.yaml":
        logo_end = text.find("\n- ", text.find("- logo:"))
        return text[:logo_end + 1] + PREVIEW_BADGE + text[logo_end + 1:] if logo_end != -1 else text + PREVIEW_BADGE
    return text


def bootstrap(root: Path, target: str = "production", overwrite: bool = False) -> None:
    paths = TARGETS[target]
    runtime = root / paths["runtime"]
    runtime.mkdir(parents=True, exist_ok=True)
    for source in sorted((root / "config").iterdir()):
        if source.suffix not in (".yaml", ".css", ".js"):
            continue
        destination = runtime / source.name
        if destination.exists() and not overwrite:
            continue
        text = source.read_text(encoding="utf-8")
        if target == "preview":
            text = preview_overlay(source.name, text)
        destination.write_text(text, encoding="utf-8", newline="\n")
        print(f"Wrote {paths['runtime']}/{source.name}")
    env = root / paths["env"]
    if not env.exists():
        copyfile(root / ".env.example", env)
        print(f"Created {paths['env']} with placeholders")
    print(f"Edit {paths['env']} locally before starting Docker Compose.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=sorted(TARGETS), default="production")
    parser.add_argument("--overwrite", action="store_true", help="Refresh runtime templates from config/ (local edits are replaced)")
    args = parser.parse_args()
    bootstrap(Path(__file__).resolve().parents[1], args.target, args.overwrite)
