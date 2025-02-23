from scripts.visual_cryptography import vc_grayscale_halftone, vc_color_cmyk
from scripts.random_grid import rg_grayscale_halftone, rg_grayscale_bitplane, rg_grayscale_additive_SS

# Using get_config() to retrieve the dictionaries with function mappings
ALGORITHM_MODULES = {
    "vc_grayscale_halftone": vc_grayscale_halftone.get_config(),
    "vc_color_cmyk": vc_color_cmyk.get_config(),

    "rg_grayscale_additive_SS": rg_grayscale_additive_SS.get_config(),
    "rg_grayscale_halftone": rg_grayscale_halftone.get_config(),
    "rg_grayscale_bitplane": rg_grayscale_bitplane.get_config(),
}
