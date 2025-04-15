# This file is part of craft-platforms.
#
# Copyright 2025 Canonical Ltd.
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
"""Hypothesis strategies for testing platforms."""

from typing import Dict, Optional, Union

try:
    from hypothesis import strategies
except ImportError:
    raise ImportError("Test strategies only work if you have hypothesis installed.")

import craft_platforms

_UBUNTU_VERSIONS = (
    "4.10",
    "5.04",
    "5.10",
    "6.06",
    "6.10",
    *(f"{year}.{month}" for year in range(7, 100) for month in ("04", "10")),
)
_UBUNTU_LTS = (
    "6.06",
    "8.04",
    "10.04",
    "12.04",
    "14.04",
    "16.04",
    "20.04",
    "22.04",
    "24.04",
    "26.04",
)
_DEBIAN_VERSIONS = (
    "1.1",
    "1.2",
    "1.3",
    "2.0",
    "2.1",
    "2.2",
    "3.0",
    "3.1",
    "4.0",
    "5.0",
    "6.0",
    "7.0",
    "8.0",
    *(str(version) for version in range(8, 15)),
    "sid",
    "unstable",
)


@strategies.composite
def ubuntu_series(draw: strategies.DrawFn) -> craft_platforms.DistroBase:
    """Generate Ubuntu series as DistroBase objects.

    This strategy includes both LTS and interim releases, as well as the special
    series "devel" that defines the currently under development Ubuntu release.
    """
    return craft_platforms.DistroBase(
        distribution="ubuntu", series=draw(strategies.sampled_from(_UBUNTU_VERSIONS))
    )


@strategies.composite
def ubuntu_lts(draw: strategies.DrawFn) -> craft_platforms.DistroBase:
    """Generate LTS Ubuntu series as DistroBase objects.

    This includes Ubuntu LTS releases all the way back to Ubuntu 6.06 (Dapper Drake)
    and may include future Ubuntu LTS releases as well.
    """
    return craft_platforms.DistroBase(
        distribution="ubuntu", series=draw(strategies.sampled_from(_UBUNTU_LTS))
    )


@strategies.composite
def debian_series(draw: strategies.DrawFn) -> craft_platforms.DistroBase:
    """Generate Debian releases as DistroBase objects.

    This includes all stable Debian releases by version number (up to Debian 14) as
    well as the special values ``"sid"`` and ``"unstable"``. Because ``"testing"``,
    ``"stable"`` and ``"oldstable"`` refer to different releases given the current
    time, they are not included.
    """
    return craft_platforms.DistroBase(
        distribution="debian", series=draw(strategies.sampled_from(_DEBIAN_VERSIONS))
    )


def real_distro_base() -> strategies.SearchStrategy[craft_platforms.DistroBase]:
    """Generate DistroBase objects of real (possibly future) Linux distributions.

    This is the default strategy when generating ``DistroBase`` objects.
    """
    return strategies.one_of(ubuntu_series(), debian_series())


@strategies.composite
def any_distro_base(draw: strategies.DrawFn) -> craft_platforms.DistroBase:
    """Generate any ``DistroBase`` that vaguely looks as expected."""
    return craft_platforms.DistroBase(
        distribution=draw(
            strategies.text("abcdefghijklmnopqrstuvwxyz-", min_size=1).filter(
                lambda x: not x.startswith("-") and not x.endswith("-")
            )
        ),
        series=str(
            draw(
                strategies.one_of(
                    strategies.sampled_from(
                        ["devel", "dev", "unstable", "testing", "sid", "tumbleweed"]
                    ),
                    strategies.floats(),
                )
            )
        ),
    )


def build_on_arch_str() -> strategies.SearchStrategy[str]:
    """Generate valid ``build-on`` architecture strings.

    This is essentially the string forms of :class:`~craft_platforms.DebianArchitecture`
    """
    return strategies.sampled_from(
        [arch.value for arch in craft_platforms.DebianArchitecture]
    )


def build_for_arch_str() -> strategies.SearchStrategy[str]:
    """Generate valid ``build-for`` architecture strings.

    These are the string forms of any :class:`~craft_platforms.DebianArchitecture`
    plus the special value ``"all"``. This should be used if you want only architecture
    strings without the multi-base format.
    """
    return strategies.sampled_from(
        ["all", *(arch.value for arch in craft_platforms.DebianArchitecture)]
    )


@strategies.composite
def distro_series_arch_str(
    draw: strategies.DrawFn,
    distro_base: strategies.SearchStrategy[craft_platforms.DistroBase],
    arch: Optional[strategies.SearchStrategy[str]] = None,
) -> str:
    """Generate ``distro@series:arch`` strings.

    :param distro_base: A strategy for generating :class:`~craft_platforms.DistroBase`
        objects.
    :param arch: A strategy for generating Debian architecture name strings. Defaults
        to the values of :class:`~craft_platforms.DebianArchitecture`. Use
        :func:`build_for_arch_str` here to include ``all`` as an architecture.
    """
    if arch is None:
        arch = strategies.sampled_from(craft_platforms.DebianArchitecture).map(
            lambda arch: arch.value
        )
    distro_str = str(draw(distro_base))
    arch_str = draw(arch)
    return f"{distro_str}:{arch_str}"


def build_on_str(
    distro_base: strategies.SearchStrategy[craft_platforms.DistroBase],
) -> strategies.SearchStrategy[str]:
    """Generate valid ``build-on`` strings for platforms.

    This strategy includes both architecture values and the values used for multi-base
    platform definitions.

    :param distro_base: A strategy for generating :class:`~craft_platforms.DistroBase`
        objects.
    """
    return strategies.one_of(
        strategies.sampled_from(craft_platforms.DebianArchitecture).map(
            lambda arch: arch.value
        ),
        distro_series_arch_str(distro_base),
    )


def build_for_str(
    distro_base: strategies.SearchStrategy[craft_platforms.DistroBase],
) -> strategies.SearchStrategy[str]:
    """Generate valid ``build-for`` strings for platforms.

    This strategy includes both architecture values (and ``"all"``) as well as valid
    values for multi-base platform definitions. Use :func:`build_for_arch_str` if you
    only want architecture strings or ``"all"``.

    :param distro_base: A strategy for generating :class:`~craft_platforms.DistroBase`
        objects.
    """
    return strategies.one_of(
        strategies.sampled_from(
            ["all", *(arch.value for arch in craft_platforms.DebianArchitecture)]
        ),
        distro_series_arch_str(
            distro_base=distro_base,
            arch=strategies.sampled_from(
                ["all", *(arch.value for arch in craft_platforms.DebianArchitecture)]
            ),
        ),
    )


@strategies.composite
def platform_dict(
    draw: strategies.DrawFn,
    build_ons: Optional[strategies.SearchStrategy[str]] = None,
    build_fors: Optional[strategies.SearchStrategy[str]] = None,
    max_build_ons: Optional[int] = 8,
) -> craft_platforms.PlatformDict:
    """Generate platform dictionaries.

    .. caution::

        The platform dictionaries generated here only limited by the rules of what
        Craft Platforms considers a valid platform dictionary. Most applications have
        far stricter rules for their platform dictionaries, meaning this strategy
        is almost guaranteed to generate invalid dictionaries for an application.
        If you need ``PlatformDict`` objects that are valid for a particular
        application, it is better to build an app-specific strategy.

    :param build_ons: A strategy for creating ``build-on`` strings. Defaults to
        :func:`build_on_str`
    :param build_fors: A strategy for creating ``build-for`` strings. Defaults to
        :func:`build_for_str`
    :param max_build_ons: The maximum length of the ``build-on`` list.
    """
    if build_ons is None:
        build_ons = build_on_str(real_distro_base())
    if build_fors is None:
        build_fors = build_for_str(real_distro_base())
    return {
        "build-on": draw(
            strategies.one_of(
                strategies.lists(
                    build_ons,
                    min_size=1,
                    max_size=max_build_ons,
                    unique_by=lambda x: tuple(sorted(x)),
                ),
                build_ons,
            )
        ),
        "build-for": draw(
            strategies.one_of(
                build_fors,
                strategies.lists(build_fors, min_size=1, max_size=1),  # or list of them
            )
        ),
    }


def platform(
    distro_base: strategies.SearchStrategy[craft_platforms.DistroBase],
    shorthand_keys: Optional[strategies.SearchStrategy[str]] = None,
    values: Union[strategies.SearchStrategy[craft_platforms.PlatformDict], None] = None,
) -> strategies.SearchStrategy[
    Union[Dict[str, None], Dict[str, craft_platforms.PlatformDict]]
]:
    """Generate a single platform in a dictionary.

    The generated platform dictionary could either be of the shorthand form
    (``{"[<distro>@<series>:]<arch>": None}``) or of the longhand form.

    .. caution::

        The default values used here generate platform dictionaries that are not
        valid for most applications.

    :param distro_base: A strategy that generates :class:`~craft_platforms.DistroBase``
        objects.
    :param shorthand_keys: A strategy that generates valid shorthand keys. These could
        be architecture names or ``[<distro>@<base>:]<arch>`` strings (the default).
    :param values: A search strategy that generates ``PlatformDict`` objects. If not
        set, uses :func:`platform_dicts` with default arguments.
    """
    if shorthand_keys is None:
        shorthand_keys = build_on_str(distro_base)
    if values is None:
        values = platform_dict()
    return strategies.one_of(
        strategies.dictionaries(
            keys=shorthand_keys,
            values=strategies.none(),
            min_size=1,
            max_size=1,
        ),
        strategies.dictionaries(
            keys=strategies.text(min_size=1).filter(lambda x: x not in ("@", ":")),
            values=values,
            min_size=1,
            max_size=1,
        ),
    )


@strategies.composite
def platforms(
    draw: strategies.DrawFn,
    distro_base: strategies.SearchStrategy[craft_platforms.DistroBase],
    shorthand_keys: Optional[strategies.SearchStrategy[str]] = None,
    values: Optional[strategies.SearchStrategy[craft_platforms.PlatformDict]] = None,
    min_size: int = 1,
    max_size: Union[int, None] = 8,
) -> Dict[str, Optional[craft_platforms.PlatformDict]]:
    """Generate platforms dictionaries.

    Generates platforms dictionaries with a size in the given range.

    .. warning:: This function can be slow, especially when generating large dictionaries.

    :param distro_base: A strategy that generates :class:`~craft_platforms.DistroBase``
        objects.
    :param shorthand_keys: A strategy that generates valid shorthand keys. These could
        be architecture names or ``[<distro>@<base>:]<arch>`` strings (the default).
    :param values: A search strategy that generates ``PlatformDict`` objects. If not
        set, uses :func:`platform_dicts` with default arguments.
    :param min_size: The minimum size of the dictionary. Must be ``>= 1``.
    :param max_size: The maximum size of the dictionary, or None for unbounded.
    """
    list_of_platforms = draw(
        strategies.lists(
            platform(distro_base, shorthand_keys, values),
            min_size=min_size,
            max_size=max_size,
            unique_by=lambda p_dict: tuple(p_dict.keys()),
        )
    )
    platforms: Dict[str, Optional[craft_platforms.PlatformDict]] = {}
    for p in list_of_platforms:
        platforms.update(p)
    return platforms
