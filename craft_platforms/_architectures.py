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
    def from_grub(cls, arch: str) -> Self:
        """Get a DebianArchitecture value from the given GRUB arch.

        :param arch: a string containing an architecture as used in the --target argument to grub-install
        :returns: The DebianArchitecture enum value
        :raises: ValueError if the architecture is not a valid Debian architecture.
        """
        return cls(_ARCH_TRANSLATIONS_GRUB_TO_DEB.get(arch.lower(), arch.lower()))

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
        """Convert this DebianArchitecture to an EFI firmware string.

        :returns: A string as matched by UKIFY in systemd
        (see https://github.com/systemd/systemd/blob/main/src/ukify/ukify.py)
        """
        return _ARCH_TRANSLATIONS_DEB_TO_EFI.get(self.value, self.value)

    def to_grub_arch(self) -> str:
        """Convert this DebianArchitecture to a GRUB boot target.

        :returns: A string suitable for the --target argument to grub-install
        """
        return _ARCH_TRANSLATIONS_DEB_TO_GRUB.get(self.value, self.value)


# Architecture translation from the deb/snap syntax to (platform, efi, grub) syntaxes
# platform: values as returned by uname -m
_ARCH_TRANSLATIONS_DEB_TO_PLATFORM = {
    "amd64": "x86_64",
    "arm64": "aarch64",
    "armhf": "armv7l",
    "i386": "i686",
    "ppc64el": "ppc64le",
    "riscv64": "riscv64",
}
# see EFI_ARCH_MAP defined in systemd
# https://github.com/systemd/systemd/blob/2fe2ee9adb18347efc0f6856830b63ba0aa874a2/src/ukify/ukify.py#L65-L75
_ARCH_TRANSLATIONS_DEB_TO_EFI = {
    "amd64": "x64",
    "arm64": "aa64",
    "armhf": "arm",
    "i386": "ia32",
    "riscv64": "riscv64",
}
# values from --target arg for grub-install (see man page)
_ARCH_TRANSLATIONS_DEB_TO_GRUB = {
    "amd64": "x86_64-efi",
    "arm64": "arm64-efi",
    "armhf": "arm-efi",
    "i386": "i386-efi",
    "riscv64": "riscv64-efi",
}

# architecture translations from the other syntaxes to deb/snap syntax
_ARCH_TRANSLATIONS_PLATFORM_TO_DEB = {
    platform: deb for (deb, platform) in _ARCH_TRANSLATIONS_DEB_TO_PLATFORM.items()
}
_ARCH_TRANSLATIONS_EFI_TO_DEB = {
    efi: deb for (deb, efi) in _ARCH_TRANSLATIONS_DEB_TO_EFI.items()
}
_ARCH_TRANSLATIONS_GRUB_TO_DEB = {
    grub: deb for (deb, grub) in _ARCH_TRANSLATIONS_DEB_TO_GRUB.items()
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
