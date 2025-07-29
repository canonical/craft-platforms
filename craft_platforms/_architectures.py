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
from typing import Literal, Tuple, Union

from typing_extensions import Self

from craft_platforms import _distro


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

    def __repr__(self) -> str:
        """Generate the repr of the string value.

        This is different from the Python/StringEnum default because of the very common
        idiom in Craft codebases of using a string's repr to pretty-print to users.
        """
        return f"{self.value!r}"

    @classmethod
    def from_machine(cls, arch: str) -> Self:
        """Get a DebianArchitecture value from the given platform arch.

        :param arch: a string containing an architecture as returned by platform.machine()
        :returns: The DebianArchitecture enum value
        :raises: ValueError if the architecture is not a valid Debian architecture.
        """
        return cls(_ARCH_TRANSLATIONS_PLATFORM_TO_DEB.get(arch.lower(), arch.lower()))

    @classmethod
    def from_efi(cls, arch: str) -> Self:
        """Get a DebianArchitecture value from the given EFI arch.

        :param arch: a string containing an architecture as used in EFI boot stubs, e.g. 'x64', 'aa64'
        :returns: The DebianArchitecture enum value
        :raises: ValueError if the architecture is not a valid Debian architecture.
        """
        return cls(_ARCH_TRANSLATIONS_EFI_TO_DEB.get(arch.lower(), arch.lower()))

    @classmethod
    def from_host(cls) -> Self:
        """Get the DebianArchitecture of the running host."""
        return cls.from_machine(platform.machine())

    def to_platform_arch(self) -> str:
        """Convert this DebianArchitecture to a platform string.

        :returns: A string matching what platform.machine() or uname -m would return.
        """
        return _ARCH_TRANSLATIONS_DEB_TO_PLATFORM.get(self.value, self.value)

    def to_efi_arch(self) -> str:
        """Convert this DebianArchitecture to an EFI string.

        :returns: A string matching what os.uname().machine would return.
        """
        return _ARCH_TRANSLATIONS_DEB_TO_EFI.get(self.value, self.value)


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

# # architecture translations from the EFI syntax to the deb/snap syntax
# The EFI abbreviations were pulled from
# https://github.com/systemd/systemd/blob/main/src/ukify/ukify.py
ARCH_TRANSLATIONS_EFI_TO_DEB = {
    "aa64": "arm64",
    "arm": "armv7l",
    "ia32": "i386",
    "risvc32": "riscv32",
    "riscv64": "riscv64",
    "x64": "amd64",
}

# architecture translations from the deb/snap syntax to the EFI syntax
_ARCH_TRANSLATIONS_DEB_TO_EFI = {
    deb: efi for efi, deb in _ARCH_TRANSLATIONS_EFI_TO_DEB.items()
}


def parse_base_and_architecture(
    arch: str,
) -> Tuple[_distro.DistroBase | None, Union[DebianArchitecture, Literal["all"]]]:
    """Get the debian arch and optional base from an architecture entry.

    The architecture may have an optional base prefixed as '[<base>:]<arch>'.

    :param arch: The architecture entry.

    :returns: A tuple of the DistroBase and the architecture. The architecture is either
     a DebianArchitecture or 'all'.

    :raises ValueError: If the architecture or base is invalid.
    """
    if ":" in arch:
        base_str, _, arch_str = arch.partition(":")
        base = _distro.DistroBase.from_str(base_str)
    else:
        base = None
        arch_str = arch

    try:
        return base, DebianArchitecture(arch_str) if arch_str != "all" else "all"
    except ValueError:
        raise ValueError(f"{arch_str!r} is not a valid Debian architecture.") from None
