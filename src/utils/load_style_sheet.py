from pathlib import Path


STYLES_DIR = Path("styles")

def load_style_sheet(style_name: str):
    style_path = STYLES_DIR / style_name / f"{style_name}.qss"
    with open(style_path) as f:
        return f.read()