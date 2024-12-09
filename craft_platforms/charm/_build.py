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


def _validate_base_definition(
    base: Optional[str],
    build_base: Optional[str],
    platform_name: Optional[str],
    platform: Optional[_platforms.PlatformDict],
) -> None:
    """Validate that a base is defined correctly in the data used to create a build.

    The rules are:
     - a base must be defined in only one place
     - each platform must build on and build for the same base

    :raises ValueError: If the base is not defined correctly in the build data.
    """
    if not (platform_name or base or build_base):
        raise ValueError("No base, build-base, or platforms are specified.")

    if platform_name:
        # validate base defined in the platform name
        platform_base, _ = _platforms.get_base_and_name(platform_name=platform_name)

        if platform_base and (base or build_base):
            raise ValueError(
                f"Platform {platform_name!r} specifies a base and a top-level base "
                "or build-base is specified."
            )

        # validate bases defined in build-on and build-for entries
        if platform:
            # create a set of all bases defined in the build-on and build-for entries
            build_on_for_bases = set()
            for entry in [*platform["build-on"], *platform["build-for"]]:
                build_on_for_distro_base = _architectures.get_base_and_architecture(
                    architecture=entry
                )[0]
                build_on_for_bases.add(
                    str(build_on_for_distro_base) if build_on_for_distro_base else None
                )

            if len(build_on_for_bases) == 0:
                build_on_for_base = None
            elif len(build_on_for_bases) == 1:
                # grab the first element
                build_on_for_base = next(iter(build_on_for_bases))
            else:
                raise ValueError(
                    f"Platform {platform_name!r} has mismatched bases in the 'build-on' "
                    "and 'build-for' entries."
                )

            if platform_base and build_on_for_base:
                raise ValueError(
                    f"Platform {platform_name!r} declares a base in the platform name "
                    "and in 'build-on' and 'build-for' entries. "
                )
        else:
            build_on_for_base = None

        if (platform_base or build_on_for_base) and (base or build_base):
            raise ValueError(
                f"Platform {platform_name!r} specifies a base and a top-level base "
                "or build-base is specified."
            )

        if not (platform_base or build_on_for_base) and not (base or build_base):
            raise ValueError(
                "No base or build-base is specified and no base is specified "
                "in the platforms section."
            )


def _get_base_from_build_data(
    base: Optional[str],
    build_base: Optional[str],
    platform_name: Optional[str],
    platform: Optional[_platforms.PlatformDict],
) -> _distro.DistroBase:
    """Get the base from a data used to create a build.

    :returns: The base to use for a build.

    :raises ValueError: If the base is not defined correctly in the build data.
    """
    _validate_base_definition(
        base=base,
        build_base=build_base,
        platform_name=platform_name,
        platform=platform,
    )

    if build_base:
        return _distro.DistroBase.from_str(build_base)

    if base:
        return _distro.DistroBase.from_str(base)

    if platform_name:
        platform_base, _ = _platforms.get_base_and_name(platform_name=platform_name)
        if platform_base:
            return platform_base

        # build-on and build-for entries all have the same base, so we only
        # need to check one of them
        if platform:
            build_for_base, _ = _architectures.get_base_and_architecture(
                architecture=platform["build-for"][0]
            )
            if build_for_base:
                return build_for_base

    # if this is raised, then the validator is not working correctly
    raise ValueError("Could not determine the base for the build.")


def get_platforms_charm_build_plan(
    base: Optional[str],
    platforms: Optional[_platforms.Platforms],
    build_base: Optional[str] = None,
) -> Sequence[_buildinfo.BuildInfo]:
    """Generate the build plan for a platforms-based charm."""
    if platforms is None:
        distro_base = _get_base_from_build_data(
            base=base,
            build_base=build_base,
            platform_name=None,
            platform=None,
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
        distro_base = _get_base_from_build_data(
            base=base,
            build_base=build_base,
            platform_name=platform_name,
            platform=platform,
        )

        _, platform_name_without_base = _platforms.get_base_and_name(
            platform_name=platform_name
        )

        if platform is None:
            # This is a workaround for Python 3.10.
            # In python 3.12+ we can just check:
            # `if platform_name not in _architectures.DebianArchitecture`
            try:
                architecture = _architectures.DebianArchitecture(
                    platform_name_without_base
                )
            except ValueError:
                raise ValueError(
                    f"Platform name {platform_name!r} is not a valid Debian architecture. "
                    "Specify a build-on and build-for.",
                ) from None

            build_plan.append(
                _buildinfo.BuildInfo(
                    platform=platform_name_without_base,
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
                build_on_base, build_on_arch = _architectures.get_base_and_architecture(
                    architecture=build_on
                )
                if build_on_arch == "all":
                    raise ValueError(
                        f"Platform {platform_name!r} has an invalid 'build-on' entry of 'all'."
                    )

                build_for_base, build_for_arch = (
                    _architectures.get_base_and_architecture(architecture=build_for)
                )

                build_plan.append(
                    _buildinfo.BuildInfo(
                        platform=platform_name_without_base,
                        build_on=build_on_arch,
                        build_for=build_for_arch,
                        build_base=distro_base,
                    ),
                )

    return build_plan
