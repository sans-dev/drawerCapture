from pathlib import Path


STYLES_DIR = Path("styles")

def load_style_sheet(style_name: str):
    style_path = STYLES_DIR / style_name / f"{style_name}.qss"
    with open(style_path) as f:
        return f.read()
    
load_photoxo_style_sheet = lambda: load_style_sheet("Photoxo")
load_combinear_style_sheet = lambda: load_style_sheet("Combinear")
load_diffnes_style_sheet = lambda: load_style_sheet("Diffnes")
load_synet_style_sheet = lambda: load_style_sheet("SyNet")
