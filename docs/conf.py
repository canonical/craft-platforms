# This file is part of craft-platforms.
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
import textwrap

project = "craft-platforms"
author = "Canonical"

copyright = f"2023-{datetime.date.today().year}, {author}"

# region Configuration for canonical-sphinx
ogp_site_url = "https://canonical-craft-platforms.readthedocs-hosted.com/"
ogp_site_name = project
ogp_image = "https://assets.ubuntu.com/v1/253da317-image-document-ubuntudocs.svg"

html_context = {
    "product_page": "github.com/canonical/craft-platforms",
    "github_url": "https://github.com/canonical/craft-platforms",
}

extensions = [
    "canonical_sphinx",
]
# endregion

# region General configuration
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions.extend(
    [
        # "sphinx_toolbox.more_autodoc",
        "sphinx_toolbox.more_autodoc.variables",
        "sphinx.ext.autodoc",  # Must be loaded after more_autodoc
        "sphinx.ext.napoleon",
        "sphinx_autodoc_typehints",
        "sphinx.ext.intersphinx",
        "sphinx.ext.viewcode",
        "sphinx.ext.coverage",
        "sphinx.ext.doctest",
        "sphinx_pydantic",
        "sphinx_toolbox",
    ]
)

exclude_patterns = [
    # Exclude the empty quadrants
    "tutorials/index.rst",
    "how-to/index.rst",
    "explanation/index.rst",
    "README.md",
    "reuse",
]

# endregion

# region Options for extensions
# Intersphinx extension
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "hypothesis": ("https://hypothesis.readthedocs.io/en/latest", None),
    "starflow": ("https://documentation.ubuntu.com/starflow/latest", None),
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

# endregion

# region Project-specific configuration

html_title = project + " documentation"

# Sidebar documentation title
# To disable the title, set it to an empty string.

# Documentation website URL
ogp_site_name = project

# Preview image URL
# TODO: To customise the preview image, update the next line.

# Product favicon; shown in bookmarks, browser tabs, etc.
# TODO: To customise the favicon, uncomment and update the next line.
# html_favicon = ".sphinx/_static/favicon.png"

# Dictionary of values to pass into the Sphinx context for all pages:
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_context
html_context.update(
    {
        # Product page URL; can be different from product docs URL
        "product_page": "github.com/canonical/craft-platforms",
        # Product tag image; the orange part of your logo, shown in the page header
        # "product_tag": "_static/tag.png",
        # Your Discourse instance URL
        "discourse": "",
        # Your Mattermost channel URL
        "mattermost": "https://chat.canonical.com/canonical/channels/documentation",
        # Your Matrix channel URL
        "matrix": "https://matrix.to/#/#starcraft-development:ubuntu.com",
        # Your documentation GitHub repository URL. If set, links for viewing the
        # documentation source files and creating GitHub issues are added at the
        # bottom of each page.
        "github_url": "https://github.com/canonical/craft-platforms",
        # Docs branch in the repo; used in links for viewing the source files
        "repo_default_branch": "main",
        # Docs location in the repo; used in links for viewing the source files
        "repo_folder": "/docs/",
        # List contributors on individual pages
        "display_contributors": False,
        # Required for feedback button
        "github_issues": "enabled",
        # Passes the top-level 'author' value to the theme
        "author": author,
        # Documentation license information
        "license": {
            "name": "LGPL-3.0",
            "url": "https://github.com/canonical/craft-platforms/blob/main/LICENSE",
        },
    }
)

html_theme_options = {
    "source_edit_link": "https://github.com/canonical/craft-platforms",
}

# TODO: If your documentation is hosted on https://documentation.ubuntu.com/,
#       uncomment and set to the RTD slug.
# slug = ""


#########################
# Sitemap configuration #
#########################

# Use RTD canonical URL to ensure duplicate pages have a specific canonical URL
html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "/")

# sphinx-sitemap uses html_baseurl to generate the full URL for each page:
sitemap_url_scheme = "{link}"

# Include `lastmod` dates in the sitemap:
# sitemap_show_lastmod = True

# TODO: Exclude pages that aren't user-facing from the sitemap (e.g., module pages
# generated by autodoc).
# Pages excluded from the sitemap:
sitemap_excludes = [
    "404/",
    "genindex/",
    "search/",
]


################################
# Template and asset locations #
################################

# html_static_path = ["_static"]
# templates_path = ["_templates"]


#############
# Redirects #
#############

# Add redirects to the 'redirects.txt' file
# https://sphinxext-rediraffe.readthedocs.io/en/latest/

# To set up redirects in the Read the Docs project dashboard:
# https://docs.readthedocs.io/en/stable/guides/redirects.html

rediraffe_redirects = "redirects.txt"

# Strips '/index.html' from destination URLs when building with 'dirhtml'
rediraffe_dir_only = True

############################
# sphinx-llm configuration #
############################

# This description is included in llms.txt to provide some initial context for your
# product docs.
llms_txt_description = textwrap.dedent(
    """\
    This is the documentation for Craft Platforms, a library that handles
    platform information for craft apps.
    """
)

# The base URL for references built by sphinx-markdown-builder.
if os.environ.get("READTHEDOCS"):
    markdown_http_base = html_baseurl

# Link checker exceptions
linkcheck_ignore = [
    r"^https://github.com",
    r"^https://www.gnu.org/",
    r"^https://crates.io/",
    r"^https://([\w-]*\.)?npmjs.org",
    r"^https://rsync.samba.org",
    r"^https://ubuntu.com",
    r"^https://matrix.to/#",
    r"^https://gitlab.gnome.org",
]

linkcheck_retries = 20
linkcheck_report_timeouts_as_broken = False
