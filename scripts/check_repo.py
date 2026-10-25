"""Fail on mis-encoded text and on preview-only labels in production templates."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
# Lead-in characters left when UTF-8 text is decoded as cp1252 and re-encoded.
MOJIBAKE = (chr(0xC3), chr(0xE2) + chr(0x20AC))
PRODUCTION_TEMPLATES = ('config/settings.yaml', 'config/widgets.yaml')


def main():
    problems = []
    tracked = subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split('\n')
    for name in filter(None, tracked):
        data = (ROOT / name).read_bytes()
        if b'\0' in data:
            continue
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            problems.append(f'{name}: not valid UTF-8')
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if any(marker in line for marker in MOJIBAKE):
                problems.append(f'{name}:{number}: mis-encoded text')
    for name in PRODUCTION_TEMPLATES:
        if 'preview' in (ROOT / name).read_text(encoding='utf-8').lower():
            problems.append(f'{name}: preview labels belong in scripts/bootstrap.py --target preview')
    print('\n'.join(problems) or 'Repository text checks passed.')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
