import os
import re
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "driz"
copyright = "2025-present, Sougata Jana"
author = "Sougata Jana"

version = ""
with open("../driz/__init__.py") as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)  # type: ignore

release = version

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "furo"

extensions = ["sphinx.ext.autodoc", "sphinx.ext.viewcode", "sphinx.ext.napoleon"]
