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
"""Charmcraft-specific platforms information."""

import itertools
from typing import Collection, List, Optional, Sequence

from craft_platforms import _architectures, _buildinfo, _distro, _platforms

DEFAULT_ARCHITECTURES: Collection[_architectures.DebianArchitecture] = (
    _architectures.DebianArchitecture.AMD64,
    _architectures.DebianArchitecture.ARM64,
    _architectures.DebianArchitecture.PPC64EL,
    _architectures.DebianArchitecture.RISCV64,
    _architectures.DebianArchitecture.S390X,
)
"""Default architectures for building a charm

If no platforms are defined, the charm will be built on and for these architectures.
"""


def get_platforms_charm_build_plan(
    base: str,
    platforms: Optional[_platforms.Platforms],
    build_base: Optional[str] = None,
) -> Sequence[_buildinfo.BuildInfo]:
    """Generate the build plan for a platforms-based charm."""
    distro_base = _distro.DistroBase.from_str(build_base or base)
    if platforms is None:
        # If no platforms are specified, build for all default architectures without
        # an option of cross-compiling.
        return [
            _buildinfo.BuildInfo(
                platform=arch.value,
                build_on=arch,
                build_for=arch,
                build_base=distro_base,
            )
            for arch in DEFAULT_ARCHITECTURES
        ]
    build_plan: List[_buildinfo.BuildInfo] = []
    for platform_name, platform in platforms.items():
        if platform is None:
            # This is a workaround for Python 3.10.
            # In python 3.12+ we can just check:
            # `if platform_name not in _architectures.DebianArchitecture`
            try:
                architecture = _architectures.DebianArchitecture(platform_name)
            except ValueError:
                raise ValueError(
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
                platform["build-for"],
            ):
                build_plan.append(
                    _buildinfo.BuildInfo(
                        platform=platform_name,
                        build_on=_architectures.DebianArchitecture(build_on),
                        build_for=_architectures.DebianArchitecture(build_for),
                        build_base=distro_base,
                    ),
                )
    return build_plan
