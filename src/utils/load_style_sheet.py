from pathlib import Path


STYLES_DIR = Path("styles")

def load_style_sheet(style_name: str):
    """
    Load a Qt style sheet from the specified style name.

    Args:
        style_name (str): The name of the style sheet to load.

    Returns:
        str: The contents of the style sheet file.
    """
    style_path = STYLES_DIR / style_name / f"{style_name}.qss"
    with open(style_path) as f:
        return f.read()