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
"""Rockcraft-specific platforms information."""

from typing import Optional, Sequence

from craft_platforms import _buildinfo, _errors, _platforms


def get_rock_build_plan(
    base: str,
    platforms: _platforms.Platforms,
    build_base: Optional[str] = None,
) -> Sequence[_buildinfo.BuildInfo]:
    """Generate the build plan for a rock.

    This function uses the default build planner, but filters it to prevent the use of
    ``build-for: all``

    :param base: the rock base (e.g. ``'ubuntu@24.04'``)
    :param platforms: the platforms structure in ``rockcraft.yaml``
    :param build_base: the build base, if provided in ``rockcraft.yaml``.
    """
    for name, platform in platforms.items():
        if platform and "all" in platform.get("build-for", []):
            raise _errors.InvalidPlatformError(
                name,
                details="Rockcraft cannot build platform-independent images.",
                resolution="Replace 'build-for: [all]' with a valid architecture",
            )
    return _platforms.get_platforms_build_plan(base, platforms, build_base)
