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
"""Architecture related utilities."""

from __future__ import annotations

import enum
import platform

from typing_extensions import Self


class DebianArchitecture(str, enum.Enum):
    """A Debian architecture."""

    AMD64 = "amd64"
    ARM64 = "arm64"
    ARMHF = "armhf"
    I386 = "i386"
    PPC64EL = "ppc64el"
    RISCV64 = "riscv64"
    S390X = "s390x"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_machine(cls, arch: str) -> Self:
        """Get a DebianArchitecture value from the given platform arch.

        :param arch: a string containing an architecture as returned by platform.machine()
        :returns: The DebianArchitecture enum value
        :raises: ValueError if the architecture is not a valid Debian architecture.
        """
        return cls(_ARCH_TRANSLATIONS_PLATFORM_TO_DEB.get(arch.lower(), arch.lower()))

    @classmethod
    def from_host(cls) -> Self:
        """Get the DebianArchitecture of the running host."""
        return cls.from_machine(platform.machine())

    def to_platform_arch(self) -> str:
        """Convert this DebianArchitecture to a platform string.

        :returns: A string matching what platform.machine() or uname -m would return.
        """
        return _ARCH_TRANSLATIONS_DEB_TO_PLATFORM.get(self.value, self.value)


# architecture translations from the platform syntax to the deb/snap syntax
_ARCH_TRANSLATIONS_PLATFORM_TO_DEB = {
    "aarch64": "arm64",
    "armv7l": "armhf",
    "i686": "i386",
    "ppc": "powerpc",
    "ppc64le": "ppc64el",
    "x86_64": "amd64",
}

# architecture translations from the deb/snap syntax to the platform syntax
_ARCH_TRANSLATIONS_DEB_TO_PLATFORM = {
    deb: platform for platform, deb in _ARCH_TRANSLATIONS_PLATFORM_TO_DEB.items()
}
