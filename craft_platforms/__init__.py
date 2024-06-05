# This file is part of craft-platforms.
#
# Copyright 2024 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License version 3, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Package base for craft_platforms."""

from ._architectures import DebianArchitecture, CRAFT_DEFAULT_ARCHITECTURES
from ._buildinfo import BuildInfo
from ._charmcraft import get_platforms_charm_build_plan
from ._distro import BaseName, DistroBase, is_ubuntu_like

try:
    from ._version import (
        __version__,
    )  # pyright: ignore[reportMissingImports,reportUnknownVariableType]
except ImportError:  # pragma: no cover
    from importlib.metadata import version, PackageNotFoundError

    try:
        __version__ = version("craft-platforms")
    except PackageNotFoundError:
        __version__ = "dev"

__all__ = [
    "__version__",
    "DebianArchitecture",
    "CRAFT_DEFAULT_ARCHITECTURES",
    "BuildInfo",
    "get_platforms_charm_build_plan",
    "BaseName",
    "DistroBase",
    "is_ubuntu_like",
]
