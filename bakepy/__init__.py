"""BakePy Markdown package."""
try:
    from .ipython import load_ipython_extension
except:
    pass

from .report import Report

from .recipes import get_recipes, get_recipe_info
from .rendering import get_renderers, get_renderer_info