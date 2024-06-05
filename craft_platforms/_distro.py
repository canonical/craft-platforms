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
"""Distribution related utilities."""

import contextlib
import dataclasses
import typing
from types import NotImplementedType

import distro
from typing_extensions import Self


@typing.runtime_checkable
class BaseName(typing.Protocol):
    """A protocol for any class that can be used as an OS base."""

    name: str
    version: str


def _get_version_tuple(version_str: str) -> tuple[int | str, ...]:
    """Convert a version string into a version tuple."""
    parts = typing.cast(list[str | int], version_str.split("."))
    # Try converting each part to an integer, leaving as a string if not doable.
    for idx, part in enumerate(parts):
        with contextlib.suppress(ValueError):
            parts[idx] = int(part)
    return tuple(parts)


def _get_version(base: BaseName | tuple[str, str]) -> str:
    """Get the version of a base."""
    if isinstance(base, BaseName):
        return base.version
    return base[1]


@dataclasses.dataclass(repr=True)
class DistroBase:
    """A linux distribution base."""

    name: str
    version: str

    def _ensure_bases_comparable(self, other: BaseName | tuple[str, str]) -> None:
        """Ensure that these bases are comparable, raising an exception if not.

        :param other: Another distribution base.
        :raises: ValueError if the distribution bases are not comparable.
        """
        other_name = other.name if isinstance(other, BaseName) else other[0]
        if self.name != other_name:
            raise ValueError(
                f"Different distributions ({self.name} and {other_name}) do not have comparable versions.",
            )

    def __eq__(self, other: object, /) -> bool | NotImplementedType:
        if isinstance(other, BaseName):
            return self.name == other.name and self.version == other.version
        if isinstance(other, tuple):
            return bool(self.name == other[0] and self.version == other[1])
        return NotImplemented

    def __lt__(self, other: BaseName | tuple[str, str]) -> bool:
        self._ensure_bases_comparable(other)
        self_version_tuple = _get_version_tuple(self.version)
        other_version_tuple = _get_version_tuple(_get_version(other))
        return self_version_tuple < other_version_tuple

    def __le__(self, other: BaseName | tuple[str, str]) -> bool:
        self._ensure_bases_comparable(other)
        self_version_tuple = _get_version_tuple(self.version)
        other_version_tuple = _get_version_tuple(_get_version(other))
        return self_version_tuple <= other_version_tuple

    def __gt__(self, other: BaseName | tuple[str, str]) -> bool:
        self._ensure_bases_comparable(other)
        self_version_tuple = _get_version_tuple(self.version)
        other_version_tuple = _get_version_tuple(_get_version(other))
        return self_version_tuple > other_version_tuple

    def __ge__(self, other: BaseName | tuple[str, str]) -> bool:
        self._ensure_bases_comparable(other)
        self_version_tuple = _get_version_tuple(self.version)
        other_version_tuple = _get_version_tuple(_get_version(other))
        return self_version_tuple >= other_version_tuple

    @classmethod
    def from_str(cls, base_str: str) -> Self:
        """Parse a distribution string to a DistroBase.

        :param base_str: A distribution string (e.g. "ubuntu@24.04")
        :returns: A DistroBase of this string.
        :raises: ValueError if the string isn't of the appropriate format.
        """
        if base_str.count("@") != 1:
            raise ValueError(
                f"Invalid base string {base_str!r}. Format should be 'distro@version'",
            )
        name, _, version = base_str.partition("@")
        return cls(name, version)

    @classmethod
    def from_linux_distribution(cls, distribution: distro.LinuxDistribution) -> Self:
        """Convert a distro package's LinuxDistribution object to a DistroBase.

        :param distribution: A LinuxDistribution from the distro package.
        :returns: A matching DistroBase object.
        """
        return cls(name=distribution.id(), version=distribution.version())


def is_ubuntu_like(distribution: distro.LinuxDistribution | None = None) -> bool:
    """Determine whether the given distribution is Ubuntu or Ubuntu-like.

    :param distribution: Linux distribution info object, or None to use the host system.
    :returns: A boolean noting whether the given distribution is Ubuntu or Ubuntu-like.
    """
    if distribution is None:
        distribution = distro.LinuxDistribution()
    if distribution.id() == "ubuntu":
        return True
    distros_like = distribution.like().split()
    if "ubuntu" in distros_like:
        return True
    return False
