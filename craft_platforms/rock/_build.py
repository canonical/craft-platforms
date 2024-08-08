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

from collections.abc import Sequence

from craft_platforms import _buildinfo, _platforms


def get_rock_build_plan(
    base: str,
    platforms: _platforms.Platforms,
    build_base: str | None = None,
) -> Sequence[_buildinfo.BuildInfo]:
    """Generate the build plan for a rock.

    This may diverge from the parent BuildInfo class when the parent gains
    support for 'build-for: ["all"]' (#23).
    """
    # rockcraft uses the default build planner
    return _platforms.get_platforms_build_plan(base, platforms, build_base)
