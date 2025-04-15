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

from craft_platforms import (
    _architectures,
    _buildinfo,
    _distro,
    _errors,
    _platforms,
    _utils,
)

DEFAULT_ARCHITECTURES: Collection[_architectures.DebianArchitecture] = (
    _architectures.DebianArchitecture.AMD64,
    _architectures.DebianArchitecture.ARM64,
    _architectures.DebianArchitecture.PPC64EL,
    _architectures.DebianArchitecture.RISCV64,
    _architectures.DebianArchitecture.S390X,
)
"""Default architectures for building a charm.

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
        raise _errors.RequiresBaseError(
            message="No base, build-base, or platforms are declared.",
            resolution="Declare a base or build-base.",
        )

    if not platform_name:
        return

    # validate base defined in the platform name
    platform_base, _ = _platforms.parse_base_and_name(platform_name=platform_name)

    if platform:
        if platform_base:
            raise _errors.InvalidMultiBaseError(
                message=(
                    f"Platform {platform_name!r} declares a base in the platform's "
                    "name and declares 'build-on' and 'build-for' entries."
                ),
                resolution=(
                    "Either remove the base from the platform's name or remove the "
                    "'build-on' and 'build-for' entries for the platform."
                ),
            )
        # create a set of the bases defined in the build-on and build-for entries
        bases = set()
        for entry in [
            *_utils.vectorize(platform["build-on"]),
            *_utils.vectorize(platform["build-for"]),
        ]:
            distro_base, _ = _architectures.parse_base_and_architecture(arch=entry)
            bases.add(str(distro_base) if distro_base else None)

        if len(bases) == 0:
            # an empty set means no bases are defined
            build_on_for_base = None
        elif len(bases) == 1:
            # a set with one element means the same base was defined for all entries
            build_on_for_base = next(iter(bases))
        else:
            # otherwise there are multiple bases defined or some entries missing bases
            raise _errors.InvalidMultiBaseError(
                message=(
                    f"Platform {platform_name!r} has mismatched bases in the 'build-on' "
                    "and 'build-for' entries."
                ),
                resolution=(
                    "Use the same base for all 'build-on' and 'build-for' entries for "
                    "the platform."
                ),
            )
    else:
        build_on_for_base = None

    if (platform_base or build_on_for_base) and (base or build_base):
        raise _errors.InvalidMultiBaseError(
            message=f"Platform {platform_name!r} declares a base and a top-level base "
            "or build-base is declared.",
            resolution=(
                "Remove the base from the platform's name or remove the top-level base "
                "or build-base."
            ),
        )

    if not (platform_base or build_on_for_base) and not (base or build_base):
        raise _errors.RequiresBaseError(
            message=(
                "No base or build-base is declared and no base is declared "
                "in the platforms section."
            ),
            resolution="Declare a base or build-base.",
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
        platform_base, _ = _platforms.parse_base_and_name(platform_name=platform_name)
        if platform_base:
            return platform_base

        # build-on and build-for entries all have the same base, so we only
        # need to check one of them
        if platform:
            build_for_base, _ = _architectures.parse_base_and_architecture(
                arch=_utils.vectorize(platform["build-for"])[0]
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
    """Generate the build plan for a platforms-based charm.

    Platforms-based charms are charms that don't use the deprecated ``bases``
    field in their ``charmcraft.yaml``.

    Multi-base recipes are supported. A multi-base recipe defines the base
    within the ``platform`` field instead of defining ``base`` and
    ``build-base``. For each platform, the base is either prefixed to the
    platform name or prefixed to every ``build-on`` and ``build-for` entry.
    In both cases, the prefixed base is delimited with a colon (``<base>:``).

    :param base: The run-time environment for the charm, formatted  as
      ``distribution@series``. If the ``build-base`` is unset, then the ``base``
      determines the build environment.
    :param build_base: The build environment to using when building the charm,
      formatted as ``distribution@series``.
    :param platforms: The mapping of platform names to ``PlatformDicts``. If
      the ``base`` and ``build-base`` are unset, then the base must be defined
      in the platforms.

    :raises ValueError: If the build plan can't be created due to invalid base
      and platform definitions.

    :returns: A build plan describing the environments where the charm can build
      and where the charm can run.
    """
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

        if platform is None:
            _, arch_str = _platforms.parse_base_and_name(platform_name)

            # This is a workaround for Python 3.10.
            # In python 3.12+ we can just check:
            # `if platform_name not in _architectures.DebianArchitecture`
            try:
                arch = _architectures.DebianArchitecture(arch_str)
            except ValueError:
                raise ValueError(
                    f"Platform name {platform_name!r} is not a valid Debian architecture. "
                    "Specify a build-on and build-for.",
                ) from None

            build_plan.append(
                _buildinfo.BuildInfo(
                    platform=platform_name,
                    build_on=arch,
                    build_for=arch,
                    build_base=distro_base,
                ),
            )
        else:
            for build_on, build_for in itertools.product(
                _utils.vectorize(platform["build-on"]),
                _utils.vectorize(platform["build-for"]),
            ):
                _, build_on_arch = _architectures.parse_base_and_architecture(
                    arch=build_on
                )
                if build_on_arch == "all":
                    raise ValueError(
                        f"Platform {platform_name!r} has an invalid 'build-on' entry of 'all'."
                    )

                _, build_for_arch = _architectures.parse_base_and_architecture(
                    arch=build_for
                )

                build_plan.append(
                    _buildinfo.BuildInfo(
                        platform=platform_name,
                        build_on=build_on_arch,
                        build_for=build_for_arch,
                        build_base=distro_base,
                    ),
                )

    return build_plan
