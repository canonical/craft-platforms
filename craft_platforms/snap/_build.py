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
"""Snapcraft-specific platforms information."""

import itertools
import re
from collections.abc import Sequence

from craft_platforms import _architectures, _buildinfo, _distro, _errors, _platforms

CORE16_18_DEFAULT_ARCHITECTURES = (
    _architectures.DebianArchitecture.AMD64,
    _architectures.DebianArchitecture.ARM64,
    _architectures.DebianArchitecture.ARMHF,
    _architectures.DebianArchitecture.I386,
    _architectures.DebianArchitecture.PPC64EL,
    _architectures.DebianArchitecture.S390X,
)

CORE20_DEFAULT_ARCHITECTURES = (
    _architectures.DebianArchitecture.AMD64,
    _architectures.DebianArchitecture.ARM64,
    _architectures.DebianArchitecture.ARMHF,
    _architectures.DebianArchitecture.PPC64EL,
    _architectures.DebianArchitecture.S390X,
)

DEFAULT_ARCHITECTURES_BY_BASE = {
    "core": CORE16_18_DEFAULT_ARCHITECTURES,
    "core16": CORE16_18_DEFAULT_ARCHITECTURES,
    "core18": CORE16_18_DEFAULT_ARCHITECTURES,
    "core20": CORE20_DEFAULT_ARCHITECTURES,
}

# The default architectures for the current and future releases.
DEFAULT_ARCHITECTURES = (
    _architectures.DebianArchitecture.AMD64,
    _architectures.DebianArchitecture.ARM64,
    _architectures.DebianArchitecture.ARMHF,
    _architectures.DebianArchitecture.PPC64EL,
    _architectures.DebianArchitecture.RISCV64,
    _architectures.DebianArchitecture.S390X,
)

CORE_BASE_REGEX = re.compile("^core(16|18|[2-9][02468])?$")


def get_default_architectures(base: str) -> Sequence[_architectures.DebianArchitecture]:
    if base in DEFAULT_ARCHITECTURES_BY_BASE:
        return DEFAULT_ARCHITECTURES_BY_BASE[base]
    return DEFAULT_ARCHITECTURES


def get_distro_base_from_core_base(
    base: str,
    build_base: str | None = None,
) -> _distro.DistroBase:
    if base == "bare":
        if build_base is None:
            raise _errors.NeedBuildBaseError(base)
        try:
            return get_distro_base_from_core_base(build_base)
        except _errors.InvalidBaseError:
            raise _errors.InvalidBaseError(
                build_base,
                resolution="Ensure the build-base is a supported base.",
                docs_url="https://snapcraft.io/docs/base-snaps",
                build_base=True,
            ) from None
    if base == "devel":
        if build_base:
            try:
                return get_distro_base_from_core_base(build_base)
            except _errors.InvalidBaseError:
                raise _errors.InvalidBaseError(
                    build_base,
                    resolution="Ensure the build-base is a supported base.",
                    docs_url="https://snapcraft.io/docs/base-snaps",
                    build_base=True,
                ) from None
        return _distro.DistroBase("ubuntu", "devel")

    if not CORE_BASE_REGEX.match(base):
        raise _errors.InvalidBaseError(
            base,
            resolution="Ensure the base is a supported base.",
            docs_url="https://snapcraft.io/docs/base-snaps",
        )
    if base in ("core", "core16"):
        return _distro.DistroBase("ubuntu", "16.04")
    major_release = base[4:]
    return _distro.DistroBase("ubuntu", f"{major_release}.04")


def get_platforms_snap_build_plan(
    base: str,
    *,
    platforms: _platforms.Platforms | None,
    build_base: str | None = None,
) -> Sequence[_buildinfo.BuildInfo]:
    """Generate the build plan for a platforms-based charm."""
    distro_base = get_distro_base_from_core_base(base, build_base)
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
            for arch in get_default_architectures(build_base or base)
        ]
    build_plan: list[_buildinfo.BuildInfo] = []
    for platform_name, platform in platforms.items():
        if platform is None:
            # This is a workaround for Python 3.10.
            # In python 3.12+ we can just check:
            # `if platform_name not in _architectures.DebianArchitecture`
            try:
                architecture = _architectures.DebianArchitecture(platform_name)
            except ValueError:
                raise _errors.InvalidPlatformNameError(platform_name) from None
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
