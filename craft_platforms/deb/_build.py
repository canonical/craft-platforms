# This file is part of craft-platforms.
#
# Copyright 2025 Canonical Ltd.
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
"""Rockcraft-specific platforms information."""

from typing import Optional, Sequence

import distro

from craft_platforms import _buildinfo, _platforms
from craft_platforms._architectures import DebianArchitecture
from craft_platforms._distro import DistroBase


def get_deb_build_plan(
    base: Optional[str],
    platforms: Optional[_platforms.Platforms],
    build_base: Optional[str] = None,
) -> Sequence[_buildinfo.BuildInfo]:
    """Generate the build plan for a rock.

    This function uses the default build planner, but filters it to prevent the use of
    ``build-for: all``

    :param base: the rock base (e.g. ``'ubuntu@24.04'``)
    :param platforms: the platforms structure in ``rockcraft.yaml``
    :param build_base: the build base, if provided in ``rockcraft.yaml``.
    :raises NeedsBuildBaseError: If base is bare and no build base is specified
    """
    if not base:
        base = str(DistroBase.from_linux_distribution(distro.LinuxDistribution()))
    if not platforms:
        platforms = {
            "all": {
                "build-on": [arch.value for arch in DebianArchitecture],
                "build-for": ["all"],
            },
            **{arch.value: None for arch in DebianArchitecture},
        }

    for name, value in platforms.items():
        if name == "all" and value is None:
            platforms["all"] = {
                "build-on": [arch.value for arch in DebianArchitecture],
                "build-for": ["all"],
            }

    return _platforms.get_platforms_build_plan(
        base,
        platforms,
        build_base,
        allow_all_and_architecture_dependent=True,
    )
