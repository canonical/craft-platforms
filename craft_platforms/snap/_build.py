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

import re
import typing
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

CORE_BASE_REGEX = re.compile("^core(?P<major>16|18|[2-9][02468])?(?P<extra>-[a-z]+)?$")


def get_default_architectures(base: str) -> Sequence[_architectures.DebianArchitecture]:
    if base in DEFAULT_ARCHITECTURES_BY_BASE:
        return DEFAULT_ARCHITECTURES_BY_BASE[base]
    return DEFAULT_ARCHITECTURES


def get_distro_base_from_core_base(
    base: str,
    build_base: str | None = None,
) -> _distro.DistroBase:
    if base == "bare":
        if build_base == "devel":
            raise _errors.InvalidBaseError(
                base,
                message="build-base 'devel' is not valid if base is 'bare'",
                resolution="Ensure the build-base is a supported base.",
                docs_url="https://snapcraft.io/docs/base-snaps",
            )
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
    if not (matches := CORE_BASE_REGEX.match(base)):
        raise _errors.InvalidBaseError(
            base,
            resolution="Ensure the base is a supported base.",
            docs_url="https://snapcraft.io/docs/base-snaps",
        )
    major_release = matches.group("major")
    extra = matches.group("extra")
    if extra and not build_base:
        raise _errors.NeedBuildBaseError(base)
    if not extra and build_base not in ("devel", None):
        raise _errors.InvalidBaseError(
            base,
            build_base=True,
            message=f"base {base!r} cannot use a build-base",
            resolution="Remove the 'build-base' key.",
            docs_url="https://snapcraft.io/docs/base-snaps",
        )
    if (
        build_base
        and (build_base_matches := CORE_BASE_REGEX.match(build_base))
        and build_base_matches.group("extra")
    ):
        raise _errors.InvalidBaseError(
            build_base,
            build_base=True,
            resolution="Ensure the build-base is only the core base.",
            docs_url="https://snapcraft.io/docs/base-snaps",
        )
    if build_base == "devel":
        return _distro.DistroBase("ubuntu", "devel")
    if base in ("core", "core16"):
        return _distro.DistroBase("ubuntu", "16.04")
    return _distro.DistroBase("ubuntu", f"{major_release}.04")


@typing.overload
def get_platforms_snap_build_plan(
    base: None,
    *,
    platforms: _platforms.Platforms | None,
    build_base: str | None = None,
    snap_type: typing.Literal["base", "kernel"],
) -> Sequence[_buildinfo.BuildInfo]: ...
@typing.overload
def get_platforms_snap_build_plan(
    base: str,
    *,
    platforms: _platforms.Platforms | None,
    build_base: str | None = None,
    snap_type: str | None = None,
) -> Sequence[_buildinfo.BuildInfo]: ...
def get_platforms_snap_build_plan(
    base: str | None,
    *,
    platforms: _platforms.Platforms | None,
    build_base: str | None = None,
    snap_type: str | None = None,
) -> Sequence[_buildinfo.BuildInfo]:
    """Generate the build plan for a platforms-based charm."""
    distro_base = None
    if base is None:
        if snap_type in ("base", "kernel"):
            if (base, build_base) == (None, "devel"):
                distro_base = _distro.DistroBase("ubuntu", "devel")
            base, build_base = build_base, None
        else:
            raise _errors.RequiresBaseError(
                f"snap type {(snap_type or 'app')!r} requires a 'base' field",
                resolution="Add a 'base' field to the snap definition.",
                docs_url="https://snapcraft.io/docs/base-snaps",
            )
        if base is None:
            raise _errors.RequiresBaseError(
                f"snap type {snap_type!r} requires a 'build-base' field if no 'base' is declared",
                resolution="Add a 'build-base' field to the snap definition.",
                docs_url="https://snapcraft.io/docs/base-snaps#heading--base-snap",
            )
    if not distro_base:
        distro_base = get_distro_base_from_core_base(base, build_base)
    if platforms is None:
        # If no platforms are specified, build for all default architectures without
        # an option of cross-compiling.
        platforms = {
            architecture.value: None
            for architecture in get_default_architectures(build_base or base)
        }
    return _platforms.get_platforms_build_plan(distro_base, platforms)
