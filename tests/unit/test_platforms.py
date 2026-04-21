# This file is part of craft-platforms.
#
# Copyright 2024 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Unit tests for generic platforms build planner."""

import itertools
import re

import craft_platforms
import pytest
import pytest_check
from craft_platforms._errors import InvalidPlatformNameError
from craft_platforms._platforms import RESERVED_PLATFORM_NAMES
from craft_platforms.test import strategies
from hypothesis import given
from hypothesis import strategies as hp_strat

SAMPLE_UBUNTU_VERSIONS = ("16.04", "18.04", "20.04", "22.04", "24.04", "24.10", "devel")


@pytest.mark.parametrize(
    ("base", "build_base", "expected_base"),
    [
        *[
            # No special build base
            (f"ubuntu@{version}", None, craft_platforms.DistroBase("ubuntu", version))
            for version in SAMPLE_UBUNTU_VERSIONS
        ],
        *[
            # Always build on a different Ubuntu version
            (
                "ubuntu@00.04",
                f"ubuntu@{version}",
                craft_platforms.DistroBase("ubuntu", version),
            )
            for version in SAMPLE_UBUNTU_VERSIONS
        ],
    ],
)
@pytest.mark.parametrize(
    ("platforms", "platform_archs"),
    [
        *(
            pytest.param(
                {architecture.value: None},
                {architecture.value: [(architecture.value, architecture.value)]},
                id=f"implicit-{architecture.value}",
            )
            for architecture in craft_platforms.DebianArchitecture
        ),
        *(
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
        ),
        *(
            pytest.param(
                {
                    architecture.value: {
                        "build-on": architecture.value,
                        "build-for": architecture.value,
                    },
                },
                {architecture.value: [(architecture.value, architecture.value)]},
                id=f"explicit-scalar-{architecture.value}",
            )
            for architecture in craft_platforms.DebianArchitecture
        ),
        *(
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
        ),
        *(
            pytest.param(
                {
                    "my-platform": {
                        "build-on": [
                            arch.value for arch in craft_platforms.DebianArchitecture
                        ],
                        "build-for": build_for_arch.value,
                    },
                },
                {
                    "my-platform": [
                        (arch.value, build_for_arch.value)
                        for arch in craft_platforms.DebianArchitecture
                    ],
                },
                id=f"build-on-any-for-scalar-{build_for_arch.value}",
            )
            for build_for_arch in craft_platforms.DebianArchitecture
        ),
        *(
            pytest.param(
                {"my-platform": {"build-on": [arch.value], "build-for": ["all"]}},
                {"my-platform": [(arch, "all")]},
                id=f"on-{arch.value}-for-all",
            )
            for arch in craft_platforms.DebianArchitecture
        ),
    ],
)
def test_build_plans_success(
    base,
    build_base,
    expected_base,
    platforms,
    platform_archs,
    check,
):
    """Shallow test for success on a large number of platform items."""
    build_plan = craft_platforms.get_platforms_build_plan(
        base=base,
        build_base=build_base,
        platforms=platforms,
    )

    for build_item in build_plan:
        with check():
            assert build_item.build_base == expected_base
        with check():
            assert (build_item.build_on, build_item.build_for) in platform_archs[
                build_item.platform
            ]
    expected_length = len(
        list(
            itertools.chain.from_iterable(
                arch_pairs for arch_pairs in platform_archs.values()
            ),
        ),
    )
    pytest_check.equal(expected_length, len(build_plan))


@pytest.mark.parametrize(
    ("base", "build_base", "platforms", "expected"),
    [
        pytest.param(
            "ubuntu@22.04",
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
            None,
            {"amd64": None},
            [
                craft_platforms.BuildInfo(
                    "amd64",
                    craft_platforms.DebianArchitecture.AMD64,
                    craft_platforms.DebianArchitecture.AMD64,
                    craft_platforms.DistroBase("ubuntu", "devel"),
                ),
            ],
            id="devel-amd64",
        ),
        pytest.param(
            "ubuntu@24.04",
            "ubuntu@22.04",
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
            "ubuntu@24.04",
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
        *(
            pytest.param(
                f"ubuntu@{base}.04",
                None,
                {
                    "anywhere": {
                        "build-on": ["amd64", "arm64", "riscv64"],
                        "build-for": ["all"],
                    },
                },
                [
                    craft_platforms.BuildInfo(
                        "anywhere",
                        arch,
                        "all",
                        craft_platforms.DistroBase("ubuntu", f"{base}.04"),
                    )
                    for arch in (
                        craft_platforms.DebianArchitecture.AMD64,
                        craft_platforms.DebianArchitecture.ARM64,
                        craft_platforms.DebianArchitecture.RISCV64,
                    )
                ],
            )
            for base in (20, 22, 24, 26, 28)
        ),
    ],
)
def test_build_plans_in_depth(base, build_base, platforms, expected):
    """Test the exact build plan for a set of items."""
    actual = craft_platforms.get_platforms_build_plan(
        base=base,
        build_base=build_base,
        platforms=platforms,
    )

    assert actual == expected


@pytest.mark.parametrize(
    ("base", "error_msg"),
    [
        (
            "invalid-base",
            "Invalid base string 'invalid-base'. Format should be '<distribution>@<series>'",
        ),
    ],
)
def test_build_plans_bad_base(base, error_msg):
    with pytest.raises(ValueError, match=error_msg):
        craft_platforms.get_platforms_build_plan(base, {"amd64": None})


@pytest.mark.parametrize("platform_name", RESERVED_PLATFORM_NAMES)
@pytest.mark.parametrize(
    "platform_value", [None, {}, {"build-on": ["ppc64el"], "build-for": ["s390x"]}]
)
def test_build_plans_reserved_platform_name(platform_name: str, platform_value):
    with pytest.raises(
        InvalidPlatformNameError, match="Platform name '.*' is reserved."
    ):
        craft_platforms.get_platforms_build_plan(
            base="ubuntu@26.10", platforms={platform_name: platform_value}
        )


def test_build_plans_multiple_reserved_platform_names():
    with pytest.raises(
        InvalidPlatformNameError,
        match=re.escape("Reserved platform names used: '*', 'any'"),
    ):
        craft_platforms.get_platforms_build_plan(
            base="ubuntu@26.10",
            platforms={
                "any": {"build-on": ["riscv64"], "build-for": ["all"]},
                "*": {"build-on": ["s390x"], "build-for": ["all"]},
            },
        )


@pytest.mark.parametrize(
    ("platforms", "error_msg"),
    [
        pytest.param(
            {"my machine": None},
            "platform name 'my machine' is not a valid Debian architecture and needs 'build-on' and 'build-for' specified",
            id="invalid-platform-name-no-details",
        ),
        pytest.param(
            {"my machine": {"build-on": ["my machine"], "build-for": ["amd64"]}},
            "'my machine' is not a valid DebianArchitecture",
            id="invalid-architecture-name",
        ),
        pytest.param(
            {"all": {"build-on": ["amd64"], "build-for": ["all", "amd64"]}},
            "build-for: all must be the only build-for architecture",
            id="all-and-amd64-same-platform",
        ),
        pytest.param(
            {
                "all": {"build-on": ["amd64"], "build-for": ["all"]},
                "amd64": None,
            },
            "build-for: all must be the only build-for architecture",
            id="all-and-amd64-different-platform",
        ),
        pytest.param(
            {
                "this": {"build-on": ["amd64"], "build-for": ["all"]},
                "that": {"build-on": ["amd64"], "build-for": ["all"]},
            },
            r"build-for: all requires exactly one platform definition \(2 provided\)",
            id="build-for-all-twice",
        ),
    ],
)
def test_build_plans_bad_architecture(platforms, error_msg):
    with pytest.raises(ValueError, match=error_msg):
        craft_platforms.get_platforms_build_plan("ubuntu@24.04", platforms)


@pytest.mark.parametrize(
    ("platforms", "error_msg"),
    [
        pytest.param(
            {
                "this": {"build-on": ["amd64"], "build-for": ["all"]},
                "that": {"build-on": ["amd64"], "build-for": ["all"]},
            },
            r"build-for: all can only be in one platform \(2 provided\)",
            id="build-for-all-twice",
        ),
        pytest.param(
            {"all": {"build-on": ["amd64"], "build-for": ["all", "amd64"]}},
            "'all' must be the only build-for architecture in a platform",
            id="all-and-amd64-same-platform",
        ),
    ],
)
def test_build_plans_multiple_all_platforms_error(platforms, error_msg):
    with pytest.raises(ValueError, match=error_msg):
        craft_platforms.get_platforms_build_plan(
            "ubuntu@26.04",
            platforms,
            allow_all_and_architecture_dependent=True,
        )


@pytest.mark.parametrize(
    "platforms",
    [
        pytest.param(
            {
                "all": {"build-on": ["amd64"], "build-for": ["all"]},
                "amd64": None,
            },
            id="all-and-amd64-different-platform",
        ),
    ],
)
def test_build_plans_with_allow_all_and_architecture_dependent(platforms):
    craft_platforms.get_platforms_build_plan(
        "ubuntu@26.04",
        platforms,
        allow_all_and_architecture_dependent=True,
    )


@pytest.mark.slow
@given(
    base=strategies.any_distro_base(),
    # The generic build planner does not currently support multi-arch values.
    platforms=strategies.platform(
        distro_base=hp_strat.nothing(),
        shorthand_keys=strategies.build_on_arch_str(),
        values=strategies.platform_dict(
            build_ons=strategies.build_on_arch_str(),
            build_fors=strategies.build_for_arch_str(),
        ),
    ),
    build_base=hp_strat.one_of(hp_strat.none(), strategies.any_distro_base()),
)
def test_fuzz_get_platforms_build_plan(
    base: craft_platforms.DistroBase,
    platforms: craft_platforms.Platforms,
    build_base: craft_platforms.DistroBase,
):
    build_base_str = str(build_base) if build_base else None
    craft_platforms.get_platforms_build_plan(base, platforms, build_base_str)
    craft_platforms.get_platforms_build_plan(str(base), platforms, build_base_str)


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("my-platform", (None, "my-platform")),
        (
            "ubuntu@24.04:my-platform",
            (craft_platforms.DistroBase("ubuntu", "24.04"), "my-platform"),
        ),
        # Platform names with colons but no base prefix should be treated as names
        ("0:", (None, "0:")),
        ("123:456", (None, "123:456")),
        ("unknown:my-platform", (None, "unknown:my-platform")),
    ],
)
def test_parse_base_and_name(given, expected):
    assert craft_platforms.parse_base_and_name(given) == expected


def test_parse_base_and_name_invalid_base():
    """Test that invalid base strings with multiple @ are caught."""
    expected = "Invalid base string 'invalid@@base'. Format should be '<distribution>@<series>'"

    with pytest.raises(ValueError, match=expected):
        craft_platforms.parse_base_and_name("invalid@@base:my-platform")
