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
"""Unit tests for snap-specific platforms functions."""

from typing import Dict, List, Optional, Union

import craft_platforms
import pytest
import pytest_check
from craft_platforms import _errors
from craft_platforms._distro import DistroBase
from craft_platforms.snap import _build
from hypothesis import given, strategies

PLATFORMS_AND_EXPECTED_ARCHES = [
    *[
        pytest.param(
            {architecture.value: None},
            {architecture.value: [(architecture.value, architecture.value)]},
            id=f"implicit-{architecture.value}",
        )
        for architecture in craft_platforms.DebianArchitecture
    ],
    *[
        pytest.param(
            {
                architecture.value: {
                    "build-on": [architecture.value],
                    "build-for": [architecture.value],
                },
            },
            {architecture.value: [(architecture.value, architecture.value)]},
            id=f"explicit-{architecture.value}",
        )
        for architecture in craft_platforms.DebianArchitecture
    ],
    *[
        pytest.param(
            {
                "my-platform": {
                    "build-on": [
                        arch.value for arch in craft_platforms.DebianArchitecture
                    ],
                    "build-for": [build_for_arch.value],
                },
            },
            {
                "my-platform": [
                    (arch.value, build_for_arch.value)
                    for arch in craft_platforms.DebianArchitecture
                ],
            },
            id=f"build-on-any-for-{build_for_arch.value}",
        )
        for build_for_arch in craft_platforms.DebianArchitecture
    ],
]

SNAP_TYPES_WITH_BASE = ["gadget", "app", None, "some-future-type"]
SNAP_TYPES = [*SNAP_TYPES_WITH_BASE, *_build.SNAP_TYPES_WITHOUT_BASE]


@given(strategies.integers(min_value=16, max_value=98).filter(lambda x: x % 2 == 0))
def test_core_base_regex_match(version):
    assert _build.CORE_BASE_REGEX.match(f"core{version}")


@given(
    strategies.one_of(
        strategies.integers(min_value=99),
        strategies.integers(min_value=16, max_value=98).filter(lambda x: x % 2 != 0),
        strategies.integers(max_value=15),
    ),
)
def test_core_base_regex_version_non_match(version):
    assert not _build.CORE_BASE_REGEX.match(f"core{version}")


@given(strategies.text().filter(lambda s: not s.startswith("core")))
def test_core_base_regex_non_match(string):
    assert not _build.CORE_BASE_REGEX.match(string)


@pytest.mark.parametrize(
    ("base", "expected"),
    [
        ("core", craft_platforms.DistroBase("ubuntu", "16.04")),
        ("devel", craft_platforms.DistroBase("ubuntu", "devel")),
        *(
            (f"core{n}", craft_platforms.DistroBase("ubuntu", f"{n}.04"))
            for n in range(16, 99, 2)
        ),
        *(
            (f"ubuntu@{n}.04", craft_platforms.DistroBase("ubuntu", f"{n}.04"))
            for n in range(16, 99, 2)
        ),
    ],
)
def test_get_distro_base_from_core_base_success(base, expected):
    assert _build.get_distro_base_from_core_base(base) == expected


@pytest.mark.parametrize("base", ["bare", "flared"])
def test_get_distro_base_from_core_base_error(base: str):
    with pytest.raises(ValueError, match="Invalid base string .+. Format should be"):
        _build.get_distro_base_from_core_base(base)


@pytest.mark.parametrize(
    ("base", "build_base", "expected"),
    [
        ("core", None, DistroBase("ubuntu", "16.04")),
        *(
            (f"core{n}", None, DistroBase("ubuntu", f"{n}.04"))
            for n in range(16, 99, 2)
        ),
        ("core", "devel", DistroBase("ubuntu", "devel")),
        *(
            (f"core{n}", "devel", DistroBase("ubuntu", "devel"))
            for n in range(16, 99, 2)
        ),
        *(
            ("bare", f"core{n}", DistroBase("ubuntu", f"{n}.04"))
            for n in range(16, 99, 2)
        ),
        *(
            ("core22-desktop", f"core{n}", DistroBase("ubuntu", f"{n}.04"))
            for n in range(16, 99, 2)
        ),
        *(
            ("some-arbitrary-base-name", f"core{n}", DistroBase("ubuntu", f"{n}.04"))
            for n in range(16, 99, 2)
        ),
        *(
            ("some-arbitrary-base-name", f"debian@{n}", DistroBase("debian", str(n)))
            for n in range(2, 12)
        ),
        ("bare", "ubuntu@23.10", DistroBase("ubuntu", "23.10")),
        ("core24-alex", "core22", DistroBase("ubuntu", "22.04")),
        ("core24-alex", "devel", DistroBase("ubuntu", "devel")),
        ("arbitrary-base-name", "opensuse@15", DistroBase("opensuse", "15")),
    ],
)
@pytest.mark.parametrize("snap_type", SNAP_TYPES)
def test_get_snap_base_general_success(base, build_base, snap_type, expected):
    assert (
        _build.get_snap_base(base=base, build_base=build_base, snap_type=snap_type)
        == expected
    )


@pytest.mark.parametrize(
    ("base", "build_base", "snap_type", "expected"),
    [
        ("core24", "ubuntu@24.04", "kernel", DistroBase("ubuntu", "24.04")),
        ("arbitrary", "debian@11", "kernel", DistroBase("debian", "11")),
    ],
)
def test_get_snap_base_examples_success(base, build_base, snap_type, expected):
    assert (
        _build.get_snap_base(base=base, build_base=build_base, snap_type=snap_type)
        == expected
    )


@pytest.mark.parametrize("snap_type", SNAP_TYPES_WITH_BASE)
@pytest.mark.parametrize(
    ("base", "match"),
    [
        pytest.param(
            "bare",
            "must declare a 'build-base' if 'base' does not match 'coreXY'",
            id="bare",
        ),
        pytest.param(
            "some-arbitrary-base",
            "must declare a 'build-base' if 'base' does not match 'coreXY'",
            id="some-arbitrary-base",
        ),
        pytest.param(
            None,
            "snaps of type [a-zN'-]+ require a 'base'",
            id="no-base",
        ),
    ],
)
def test_get_snap_base_no_build_base_requires_base_error(base, snap_type, match):
    with pytest.raises(_errors.CraftPlatformsError, match=match):
        _build.get_snap_base(base=base, build_base=None, snap_type=snap_type)


@pytest.mark.parametrize("snap_type", _build.SNAP_TYPES_WITHOUT_BASE)
@pytest.mark.parametrize(
    ("base", "match"),
    [
        pytest.param(
            "bare",
            "must declare a 'build-base' if 'base' does not match 'coreXY'",
            id="bare",
        ),
        pytest.param(
            "some-arbitrary-base",
            "must declare a 'build-base' if 'base' does not match 'coreXY'",
            id="some-arbitrary-base",
        ),
        pytest.param(
            None,
            "'[a-z]+' snaps require a 'build-base' if no 'base' is declared",
            id="no-base",
        ),
    ],
)
def test_get_snap_base_no_build_base_ether_or(base, snap_type, match):
    with pytest.raises(_errors.CraftPlatformsError, match=match):
        _build.get_snap_base(base=base, build_base=None, snap_type=snap_type)


@pytest.mark.parametrize(
    ("base", "build_base", "snap_type", "match"),
    [
        (
            None,
            "devel",
            "kernel",
            "non-base snaps require a 'base' if 'build-base' is 'devel",
        ),
        (None, "flared", "base", "build-base 'flared' is unknown or invalid"),
        (
            "core24",
            "ubuntu@24.04",
            "blah",
            "non-kernel snaps cannot use 'base: coreXY' and arbitrary build-bases",
        ),
    ],
)
def test_get_snap_base_specific_errors(base, build_base, snap_type, match):
    with pytest.raises(_errors.CraftPlatformsError, match=match):
        _build.get_snap_base(base=base, build_base=build_base, snap_type=snap_type)


@pytest.mark.parametrize(
    ("base", "build_base", "expected_base"),
    [
        ("core", None, craft_platforms.DistroBase("ubuntu", "16.04")),
        ("bare", "core", craft_platforms.DistroBase("ubuntu", "16.04")),
        *(
            (f"core{n}", None, craft_platforms.DistroBase("ubuntu", f"{n}.04"))
            for n in (16, 18, 20, 22, 24, 26)
        ),
        *(
            ("bare", f"core{n}", craft_platforms.DistroBase("ubuntu", f"{n}.04"))
            for n in (16, 18, 20, 22, 24, 26)
        ),
        *(
            (
                f"core{n}-desktop",
                f"core{n}",
                craft_platforms.DistroBase("ubuntu", f"{n}.04"),
            )
            for n in (16, 18, 20, 22, 24, 26)
        ),
        *(
            pytest.param(
                f"core{n}",
                "devel",
                craft_platforms.DistroBase("ubuntu", "devel"),
                id=f"on-devel-for-core{n}",
            )
            for n in (16, 18, 20, 22, 24, 26)
        ),
    ],
)
@pytest.mark.parametrize(
    ("platforms", "expected_archs"),
    PLATFORMS_AND_EXPECTED_ARCHES,
)
@pytest.mark.parametrize("snap_type", ["app", "core", "gadget", "kernel", None])
def test_get_platforms_snap_build_plan_success(
    base: str,
    build_base: Optional[str],
    expected_base: craft_platforms.DistroBase,
    platforms: Union[craft_platforms.Platforms, None],
    expected_archs: Dict[str, List[str]],
    snap_type: Optional[str],
):
    build_plan = _build.get_platforms_snap_build_plan(
        base,
        platforms=platforms,
        build_base=build_base,
        snap_type=snap_type,
    )

    for build_item in build_plan:
        with pytest_check.check():
            assert build_item.build_base == expected_base
        with pytest_check.check():
            assert (build_item.build_on, build_item.build_for) in expected_archs[
                build_item.platform
            ]


@pytest.mark.parametrize(
    ("build_base", "expected_base"),
    [
        ("core", craft_platforms.DistroBase("ubuntu", "16.04")),
        *(
            (f"core{n}", craft_platforms.DistroBase("ubuntu", f"{n}.04"))
            for n in (16, 18, 20, 22, 24, 26)
        ),
        ("devel", craft_platforms.DistroBase("ubuntu", "devel")),
    ],
)
@pytest.mark.parametrize(
    ("platforms", "expected_archs"),
    PLATFORMS_AND_EXPECTED_ARCHES,
)
def test_get_platforms_snap_build_plan_base_snap_success(
    build_base: str,
    expected_base: craft_platforms.DistroBase,
    platforms: Union[craft_platforms.Platforms, None],
    expected_archs: Dict[str, List[str]],
):
    build_plan = _build.get_platforms_snap_build_plan(
        base=None,
        platforms=platforms,
        build_base=build_base,
        snap_type="base",
    )

    for build_item in build_plan:
        with pytest_check.check():
            assert build_item.build_base == expected_base
        with pytest_check.check():
            assert (build_item.build_on, build_item.build_for) in expected_archs[
                build_item.platform
            ]


@pytest.mark.parametrize(
    ("base", "build_base", "error_cls", "error_match"),
    [
        (
            "core24",
            "ubuntu@24.04",
            craft_platforms.InvalidBaseError,
            "non-kernel snaps cannot use 'base: coreXY' and arbitrary build-bases",
        ),
        (
            None,
            "devel",
            craft_platforms.RequiresBaseError,
            "snaps of type None require a 'base'",
        ),
    ],
)
def test_get_platforms_snap_build_plan_error(
    base,
    build_base,
    error_cls,
    error_match,
):
    with pytest.raises(error_cls, match=error_match):
        _build.get_platforms_snap_build_plan(
            base=base,
            build_base=build_base,
            platforms=None,
        )


@pytest.mark.parametrize(
    ("base", "build_base", "platforms", "expected"),
    [
        pytest.param(
            "core22",
            None,
            {"amd64": None},
            [
                craft_platforms.BuildInfo(
                    "amd64",
                    craft_platforms.DebianArchitecture.AMD64,
                    craft_platforms.DebianArchitecture.AMD64,
                    craft_platforms.DistroBase("ubuntu", "22.04"),
                ),
            ],
            id="jammy-amd64",
        ),
        pytest.param(
            "core24",
            "devel",
            {"amd64": None},
            [
                craft_platforms.BuildInfo(
                    "amd64",
                    craft_platforms.DebianArchitecture.AMD64,
                    craft_platforms.DebianArchitecture.AMD64,
                    craft_platforms.DistroBase("ubuntu", "devel"),
                ),
            ],
            id="devel-for-noble",
        ),
        pytest.param(
            "core24",
            None,
            {
                "my-desktop": {
                    "build-on": ["amd64"],
                    "build-for": ["amd64"],
                },
                "raspi": {"build-on": ["amd64", "arm64"], "build-for": ["arm64"]},
                "some-mainframe-cross-compile": {
                    "build-on": ["amd64", "arm64"],
                    "build-for": ["s390x"],
                },
            },
            [
                craft_platforms.BuildInfo(
                    "my-desktop",
                    craft_platforms.DebianArchitecture.AMD64,
                    craft_platforms.DebianArchitecture.AMD64,
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                ),
                craft_platforms.BuildInfo(
                    "raspi",
                    craft_platforms.DebianArchitecture.AMD64,
                    craft_platforms.DebianArchitecture.ARM64,
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                ),
                craft_platforms.BuildInfo(
                    "raspi",
                    craft_platforms.DebianArchitecture.ARM64,
                    craft_platforms.DebianArchitecture.ARM64,
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                ),
                craft_platforms.BuildInfo(
                    "some-mainframe-cross-compile",
                    craft_platforms.DebianArchitecture.AMD64,
                    craft_platforms.DebianArchitecture.S390X,
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                ),
                craft_platforms.BuildInfo(
                    "some-mainframe-cross-compile",
                    craft_platforms.DebianArchitecture.ARM64,
                    craft_platforms.DebianArchitecture.S390X,
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                ),
            ],
            id="multiple-builds",
        ),
    ],
)
def test_build_plans_in_depth(base, build_base, platforms, expected):
    """Test the exact build plan for a set of items."""
    actual = _build.get_platforms_snap_build_plan(
        base=base,
        build_base=build_base,
        platforms=platforms,
    )

    assert actual == expected


@pytest.mark.parametrize(
    ("base", "build_base", "expected_archs"),
    [
        ("core", None, _build.CORE16_18_DEFAULT_ARCHITECTURES),
        ("core16", None, _build.CORE16_18_DEFAULT_ARCHITECTURES),
        ("core18", None, _build.CORE16_18_DEFAULT_ARCHITECTURES),
        ("core20", None, _build.CORE20_DEFAULT_ARCHITECTURES),
        ("core22", None, _build.DEFAULT_ARCHITECTURES),
        ("core24", None, _build.DEFAULT_ARCHITECTURES),
    ],
)
def test_build_plans_default_architectures(base, build_base, expected_archs):
    actual = _build.get_platforms_snap_build_plan(
        base=base,
        build_base=build_base,
        platforms=None,
    )
    actual_archs = [item.build_for for item in actual]
    pytest_check.equal(actual_archs, list(expected_archs))
    for info in actual:
        pytest_check.equal(info.build_on, info.build_for)
        pytest_check.is_in(info.build_for, expected_archs)
