# Configuration file for the Sphinx documentation builder.
# For the full list of built-in configuration values, see:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Project information -----------------------------------------------------
project = 'Maritime Operations Dashboard'
copyright = '2025, Ryan Acuna, Seth Johnson, Yolvin Aguirre-Duran, Sean Schoolfield, Oliver Jimenez-Gonzalez'
author = 'Ryan Acuna, Seth Johnson, Yolvin Aguirre-Duran, Sean Schoolfield, Oliver Jimenez-Gonzalez'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',          # Generates documentation from docstrings
    'sphinx.ext.viewcode',         # Links to source code
    'sphinx.ext.napoleon',         # Supports Google & NumPy style docstrings
    'sphinx_autodoc_typehints',    # Type hints support
    'sphinxcontrib.httpdomain',    # For FastAPI/HTTP documentation
]

# Include project paths for autodoc
sys.path.insert(0, os.path.abspath('../../backend'))  # Include FastAPI backend
sys.path.insert(0, os.path.abspath('../frontend')) # Optionally include React frontend

# Specify templates and exclude patterns
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'  # Clean and modern look
html_static_path = ['_static']

# Options for Sphinx RTD Theme
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
}

# -- Autodoc settings --------------------------------------------------------
autodoc_member_order = 'bysource'  # Keep the order of functions/members
autodoc_typehints = "description"  # Show type hints in description
