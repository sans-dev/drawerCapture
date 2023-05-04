from pathlib import Path


STYLES_DIR = Path("styles")

def load_style_sheet(style_name: str):
    style_path = STYLES_DIR / style_name / f"{style_name}.qss"
    with open(style_path) as f:
        return f.read()
    
load_photoxo_style_sheet = lambda: load_style_sheet("Photoxo")
load_combiniear_style_sheet = lambda: load_style_sheet("Combinear")
load_diffness_style_sheet = lambda: load_style_sheet("Diffness")
load_sysnet_style_sheet = lambda: load_style_sheet("SysNet")
