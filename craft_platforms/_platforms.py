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
"""Platform related models."""
import itertools
import typing
from collections.abc import Sequence
from typing import Annotated

import annotated_types

from craft_platforms import _architectures, _buildinfo, _distro, _errors

PlatformDict = typing.TypedDict(
    "PlatformDict",
    {
        "build-on": Sequence[str],
        "build-for": Annotated[Sequence[str], annotated_types.Len(1)],
    },
)


Platforms = dict[_architectures.DebianArchitecture | str, PlatformDict | None]


def get_platforms_build_plan(
    base: str,
    platforms: Platforms,
    build_base: str | None = None,
) -> Sequence[_buildinfo.BuildInfo]:
    """Generate the build plan for a platforms-based artefact."""
    distro_base = _distro.DistroBase.from_str(build_base or base)
    build_plan: list[_buildinfo.BuildInfo] = []

    for platform_name, platform in platforms.items():
        if platform is None:
            # This is a workaround for Python 3.10.
            # In python 3.12+ we can just check:
            # `if platform_name not in _architectures.DebianArchitecture`
            try:
                architecture = _architectures.DebianArchitecture(platform_name)
            except ValueError:
                raise _errors.InvalidPlatformNameError(
                    f"Platform name {platform_name!r} is not a valid Debian architecture. "
                    "Specify a build-on and build-for.",
                ) from None
            build_plan.append(
                _buildinfo.BuildInfo(
                    platform=platform_name,
                    build_on=architecture,
                    build_for=architecture,
                    build_base=distro_base,
                ),
            )
        else:
            for build_on, build_for in itertools.product(
                platform["build-on"],
                platform.get("build-for", [platform_name]),
            ):
                build_plan.append(
                    _buildinfo.BuildInfo(
                        platform=platform_name,
                        build_on=_architectures.DebianArchitecture(build_on),
                        build_for=(
                            "all"
                            if build_for == "all"
                            else _architectures.DebianArchitecture(build_for)
                        ),
                        build_base=distro_base,
                    ),
                )

    return build_plan
