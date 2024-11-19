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
from typing import Collection, List, Optional, Sequence, Set

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
    base: Optional[str],
    platforms: Optional[_platforms.Platforms],
    build_base: Optional[str] = None,
) -> Sequence[_buildinfo.BuildInfo]:
    """Generate the build plan for a platforms-based charm."""
    if base or build_base:
        distro_base = _distro.DistroBase.from_str(build_base or base)
    else:
        distro_base = None
    if platforms is None:
        if not base or build_base:
            raise ValueError(
                "No platforms are specified and no base or build-base is specified."
            )

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
        platform_base, platform_name = _platforms.get_base_and_name(
            platform_name=platform_name
        )

        if platform_base and (base or build_base):
            raise ValueError(
                f"Platform {platform_name!r} specifies a base and a top-level base "
                "or build-base is specified."
            )

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
                    build_base=platform_base or distro_base,
                ),
            )
        else:
            arch_bases: Set[str] = set()
            """Bases defined across the 'build-on/for' entries of a platform."""

            for build_on, build_for in itertools.product(
                platform["build-on"],
                platform["build-for"],
            ):
                build_on_base, build_on_arch = _platforms.get_base_and_architecture(
                    architecture=build_on
                )
                build_for_base, build_for_arch = _platforms.get_base_and_architecture(
                    architecture=build_for
                )

                if build_on_base != build_for_base:
                    raise ValueError(
                        f"Platform {platform_name!r} has mismatched bases in the 'build-on' "
                        "and 'build-for' entries."
                    )

                arch_bases.update(
                    {str(base) for base in (build_on_base, build_for_base) if base is not None}
                )

                build_plan.append(
                    _buildinfo.BuildInfo(
                        platform=platform_name,
                        build_on=build_on_arch,
                        build_for=build_for_arch,
                        build_base=build_on_base or platform_base or distro_base,
                    ),
                )


            if len(arch_bases) > 1:
                raise ValueError(
                    f"Platform {platform_name!r} has multiple bases {arch_bases}. "
                    "All bases must be the same for a platform."
                )

            if platform_base and arch_bases:
                raise ValueError(
                    f"Platform {platform_name!r} declares a base in the platform name "
                    "and in 'build-on' and 'build-for' entries. "
                    "For each platform, the base must be declared in only the platform "
                    "name or in all 'build-on' and 'build-for' entries."
                )

            # XXX: the next 2 checks could be combined as an XOR
            if (platform_base or arch_bases) and (base or build_base):
                raise ValueError(
                    f"Platform {platform_name!r} specifies a base and a top-level base "
                    "or build-base is specified."
                )

            if not (platform_base or arch_bases) and not (base or build_base):
                raise ValueError(
                    f"No top-level and build-base is specified and no base is specified "
                    "in the platforms section."
                )


    return build_plan
