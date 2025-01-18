# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'PiArgus'
copyright = '2025, Laurent Verweijen'
author = 'Laurent Verweijen'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.githubpages',
    'sphinx.ext.viewcode',
    'myst_parser',
    'sphinxcontrib.mermaid',
]

templates_path = ['_templates']
exclude_patterns = []

# Make sure __init__ is always documented.
autodoc_default_options = {
    # 'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    # 'undoc-members': True,
    # 'exclude-members': '__weakref__'
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

myst_enable_extensions = ["colon_fence", "dollarmath"]

# Code is in src. Make sure sphinx can find it
import sys
from pathlib import Path
src_folder = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_folder.resolve(strict=True)))
