# This file is part of starbase.
#
# Copyright 2024 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import os

project = "craft-platforms"
author = "Canonical"

copyright = "2023-%s, %s" % (datetime.date.today().year, author)

# region Configuration for canonical-sphinx
ogp_site_url = "https://canonical-craft-platforms.readthedocs-hosted.com/"
ogp_site_name = project
ogp_image = "https://assets.ubuntu.com/v1/253da317-image-document-ubuntudocs.svg"

html_context = {
    # The following items are required for public-facing products. Replace the
    # placeholder links with those specific to your product.
    "product_page": "github.com/canonical/craft-platforms",
    "github_url": "https://github.com/canonical/craft-platforms",
    "github_issues": "https://github.com/canonical/craft-platforms/issues",
    "matrix": "https://matrix.to/#/#starcraft-development:ubuntu.com",
    "discourse": "",  # Leave this blank to hide it from the dropdown
}

# Target repository for the edit button on pages
html_theme_options = {
    "source_edit_link": "https://github.com/canonical/starbase",
}

html_static_path = ["_static"]
templates_path = ["_templates"]

# Static resources for Google Analytics
html_css_files = [
    'css/cookie-banner.css'
]

html_js_files = [
    'js/bundle.js',
]

extensions = [
    "canonical_sphinx",
]

# endregion

# region General configuration
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions.extend(
    [
        "sphinx_toolbox.more_autodoc",
        "sphinx.ext.napoleon",
        "sphinx_autodoc_typehints",
        "sphinx.ext.intersphinx",
        "sphinx.ext.viewcode",
        "sphinx.ext.coverage",
        "sphinx.ext.doctest",
        "sphinx-pydantic",
        "sphinx_sitemap",
        "sphinx_toolbox",
        "sphinx_toolbox.more_autodoc",
        "sphinxext.rediraffe",
        "sphinx.ext.autodoc",  # Must be loaded after more_autodoc
    ]
)


exclude_patterns = [
    # Exclude the empty quadrants
    "tutorials/index.rst",
    "how-to-guides/index.rst",
    "explanation/index.rst",
    "release-notes/index.rst",
]
# endregion

# region Options for extensions
# Intersphinx extension
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "hypothesis": ("https://hypothesis.readthedocs.io/en/latest", None),
}

# Type annotations config
# add_module_names = True

# Type hints configuration
set_type_checking_flag = True
typehints_fully_qualified = False
always_document_param_types = True
typehints_document_rtype = True

# Autodoc extension configuration
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration
autodoc_member_order = "bysource"
autodoc_default_flags = ["members", "show-inheritance"]
autodoc_typehints_format = "short"

# sphinx-autodoc-typehints configuration
# https://github.com/tox-dev/sphinx-autodoc-typehints?tab=readme-ov-file#options
always_use_bars_union = True
typehints_use_rtype = False
typehints_defaults = "comma"

# More-autodoc configuration
# https://sphinx-toolbox.readthedocs.io/en/stable/extensions/more_autodoc/index.html
overloads_location = "bottom"

# Napoleon configuration
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
napoleon_attr_annotations = True

# Github config
github_username = "canonical"
github_repository = "craft-platforms"

# Client-side page redirects.
rediraffe_redirects = "redirects.txt"

# The full path to the RTD site.
# TODO: Change this to your project's RTD URL. If the RTD site isn't live yet, follow
# the pattern here. If the documentation has moved to documentation.ubuntu.com, enter
# the URL at that domain. It's OK to use this for private projects.
# https://sphinx-sitemap.readthedocs.io
html_baseurl = "https://canonical-craft-platforms.readthedocs-hosted.com/"

# Compose the URL for remote RTD and local builds.
# TODO: If your project doesn't have a `latest` RTD branch set up, change to its default
# branch.
# https://sphinx-sitemap.readthedocs.io
if "READTHEDOCS_VERSION" in os.environ:
    version = os.environ["READTHEDOCS_VERSION"]
    sitemap_url_scheme = "{version}{link}"
else:
    sitemap_url_scheme = "latest/{link}"

# endregion
