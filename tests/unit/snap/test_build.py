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

import craft_platforms
import pytest
import pytest_check
from craft_platforms.snap import _build
from hypothesis import given, strategies


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
    ("string", "matches"),
    [
        ("core", True),
        ("core14", False),
    ],
)
def test_core_base_regex_match_specials(string, matches):
    assert bool(_build.CORE_BASE_REGEX.match(string)) == matches


@pytest.mark.parametrize(
    ("base", "expected"),
    [
        ("core", craft_platforms.DistroBase("ubuntu", "16.04")),
        ("core16", craft_platforms.DistroBase("ubuntu", "16.04")),
        ("core18", craft_platforms.DistroBase("ubuntu", "18.04")),
        ("core20", craft_platforms.DistroBase("ubuntu", "20.04")),
        ("core22", craft_platforms.DistroBase("ubuntu", "22.04")),
        ("core24", craft_platforms.DistroBase("ubuntu", "24.04")),
        ("core26", craft_platforms.DistroBase("ubuntu", "26.04")),
        ("devel", craft_platforms.DistroBase("ubuntu", "devel")),
    ],
)
def test_get_distro_base_from_core_base_success(base, expected):
    assert _build.get_distro_base_from_core_base(base) == expected
    # Also test this with build_base
    assert _build.get_distro_base_from_core_base("bare", base) == expected


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
        ("devel", None, craft_platforms.DistroBase("ubuntu", "devel")),
        *(
            ("devel", f"core{n}", craft_platforms.DistroBase("ubuntu", f"{n}.04"))
            for n in (16, 18, 20, 22, 24, 26)
        ),
    ],
)
@pytest.mark.parametrize(
    ("platforms", "expected_archs"),
    [
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
    ],
)
def test_get_platforms_snap_build_plan_success(
    base,
    build_base,
    expected_base,
    platforms,
    expected_archs,
):
    build_plan = _build.get_platforms_snap_build_plan(
        base,
        platforms=platforms,
        build_base=build_base,
    )

    for build_item in build_plan:
        with pytest_check.check():
            assert build_item.build_base == expected_base
        with pytest_check.check():
            assert (build_item.build_on, build_item.build_for) in expected_archs[
                build_item.platform
            ]


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
            "devel",
            "core22",
            {"amd64": None},
            [
                craft_platforms.BuildInfo(
                    "amd64",
                    craft_platforms.DebianArchitecture.AMD64,
                    craft_platforms.DebianArchitecture.AMD64,
                    craft_platforms.DistroBase("ubuntu", "22.04"),
                ),
            ],
            id="jammy-for-noble-amd64",
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
