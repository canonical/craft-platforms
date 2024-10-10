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
"""Build info."""

import dataclasses
from typing import Literal, Union

from craft_platforms import _architectures, _distro


@dataclasses.dataclass
class BuildInfo:
    """Platform build information."""

    platform: str
    """The platform name."""

    build_on: _architectures.DebianArchitecture
    """The architecture to build on."""

    build_for: Union[_architectures.DebianArchitecture, Literal["all"]]
    """The architecture to build for."""

    build_base: _distro.DistroBase
    """The base to build on."""
