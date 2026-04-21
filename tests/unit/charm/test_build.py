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
"""Tests for charmcraft builds."""

import itertools
from typing import Optional

import craft_platforms
import pytest
import pytest_check
from craft_platforms import charm
from craft_platforms.test import strategies
from hypothesis import assume, given
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
        pytest.param(
            None,
            {
                architecture.value: [(architecture, architecture)]
                for architecture in charm.DEFAULT_ARCHITECTURES
            },
            id="default-platforms",
        ),
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
                    architecture.value: {
                        "build-on": architecture.value,
                        "build-for": architecture.value,
                    },
                },
                {architecture.value: [(architecture.value, architecture.value)]},
                id=f"explicit-scalar-{architecture.value}",
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
        *[
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
        ],
    ],
)
def test_build_plans_success(
    check,
    base,
    build_base,
    expected_base,
    platforms,
    platform_archs,
):
    """Shallow test for success on a large number of platform items."""
    build_plan = charm.get_platforms_charm_build_plan(
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
                "0:": {
                    "build-on": ["amd64"],
                    "build-for": ["amd64"],
                },
            },
            [
                craft_platforms.BuildInfo(
                    "0:",
                    craft_platforms.DebianArchitecture.AMD64,
                    craft_platforms.DebianArchitecture.AMD64,
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                ),
            ],
            id="weird-platform-name-with-colon",
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
        pytest.param(
            None,
            None,
            {
                "noble": {
                    "build-on": ["ubuntu@24.04:amd64"],
                    "build-for": ["ubuntu@24.04:amd64"],
                },
            },
            [
                craft_platforms.BuildInfo(
                    "noble",
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                )
            ],
            id="multi-base-simple",
        ),
        pytest.param(
            None,
            None,
            {
                "noble": {
                    "build-on": "ubuntu@24.04:amd64",
                    "build-for": "ubuntu@24.04:amd64",
                },
            },
            [
                craft_platforms.BuildInfo(
                    "noble",
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                )
            ],
            id="multi-base-scalar",
        ),
        pytest.param(
            None,
            None,
            {"ubuntu@24.04:amd64": None},
            [
                craft_platforms.BuildInfo(
                    "ubuntu@24.04:amd64",
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                )
            ],
            id="multi-base-shorthand",
        ),
        pytest.param(
            None,
            None,
            {
                # base and arch in platform name
                "ubuntu@20.04:amd64": None,
                # base and arch in build entries
                "noble": {
                    "build-on": ["ubuntu@24.04:amd64"],
                    "build-for": ["ubuntu@24.04:amd64"],
                },
            },
            [
                craft_platforms.BuildInfo(
                    "ubuntu@20.04:amd64",
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DistroBase("ubuntu", "20.04"),
                ),
                craft_platforms.BuildInfo(
                    "noble",
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                ),
            ],
            id="multi-base-mixed-notation",
        ),
        pytest.param(
            None,
            None,
            {
                "jammy": {
                    "build-on": ["ubuntu@22.04:amd64"],
                    "build-for": ["ubuntu@22.04:all"],
                },
                "noble": {
                    "build-on": ["ubuntu@24.04:amd64"],
                    "build-for": ["ubuntu@24.04:all"],
                },
            },
            [
                craft_platforms.BuildInfo(
                    "jammy",
                    craft_platforms.DebianArchitecture("amd64"),
                    "all",
                    craft_platforms.DistroBase("ubuntu", "22.04"),
                ),
                craft_platforms.BuildInfo(
                    "noble",
                    craft_platforms.DebianArchitecture("amd64"),
                    "all",
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                ),
            ],
            id="multi-base-all",
        ),
        pytest.param(
            None,
            None,
            {
                "jammy": {
                    "build-on": "ubuntu@22.04:amd64",
                    "build-for": "ubuntu@22.04:all",
                },
                "noble": {
                    "build-on": "ubuntu@24.04:amd64",
                    "build-for": "ubuntu@24.04:all",
                },
            },
            [
                craft_platforms.BuildInfo(
                    "jammy",
                    craft_platforms.DebianArchitecture("amd64"),
                    "all",
                    craft_platforms.DistroBase("ubuntu", "22.04"),
                ),
                craft_platforms.BuildInfo(
                    "noble",
                    craft_platforms.DebianArchitecture("amd64"),
                    "all",
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                ),
            ],
            id="multi-base-all-scalar",
        ),
        pytest.param(
            None,
            None,
            {
                "ubuntu@20.04:amd64": None,
                "jammy-list": {
                    "build-on": ["ubuntu@22.04:amd64"],
                    "build-for": ["ubuntu@22.04:amd64"],
                },
                "jammy-scalar": {
                    "build-on": "ubuntu@22.04:amd64",
                    "build-for": "ubuntu@22.04:amd64",
                },
                "noble": {
                    "build-on": ["ubuntu@22.04:amd64"],
                    "build-for": ["ubuntu@22.04:amd64"],
                },
                "noble-cross": {
                    "build-on": ["ubuntu@24.04:amd64", "ubuntu@24.04:riscv64"],
                    "build-for": ["ubuntu@24.04:riscv64"],
                },
            },
            [
                craft_platforms.BuildInfo(
                    "ubuntu@20.04:amd64",
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DistroBase("ubuntu", "20.04"),
                ),
                craft_platforms.BuildInfo(
                    "jammy-list",
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DistroBase("ubuntu", "22.04"),
                ),
                craft_platforms.BuildInfo(
                    "jammy-scalar",
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DistroBase("ubuntu", "22.04"),
                ),
                craft_platforms.BuildInfo(
                    "noble",
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DistroBase("ubuntu", "22.04"),
                ),
                craft_platforms.BuildInfo(
                    "noble-cross",
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DebianArchitecture("riscv64"),
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                ),
                craft_platforms.BuildInfo(
                    "noble-cross",
                    craft_platforms.DebianArchitecture("riscv64"),
                    craft_platforms.DebianArchitecture("riscv64"),
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                ),
            ],
            id="multi-base-complex",
        ),
        pytest.param(
            None,
            None,
            {
                "ubuntu@24.04:amd64": {
                    "build-on": ["s390x"],
                    "build-for": ["amd64"],
                },
            },
            [
                craft_platforms.BuildInfo(
                    "ubuntu@24.04:amd64",
                    craft_platforms.DebianArchitecture("s390x"),
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                ),
            ],
            id="multi-base-set-arch",
        ),
        pytest.param(  # This is how craft-application expands the shorthand.
            None,
            None,
            {
                "ubuntu@24.04:amd64": {
                    "build-on": ["ubuntu@24.04:amd64"],
                    "build-for": ["ubuntu@24.04:amd64"],
                },
            },
            [
                craft_platforms.BuildInfo(
                    "ubuntu@24.04:amd64",
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                ),
            ],
            id="multi-base-redundant",
        ),
        pytest.param(
            None,
            None,
            {
                "ubuntu@24.04:amd64": {
                    "build-on": ["ubuntu@24.04:amd64", "ubuntu@24.04:riscv64"],
                    "build-for": ["ubuntu@24.04:amd64"],
                },
            },
            [
                craft_platforms.BuildInfo(
                    "ubuntu@24.04:amd64",
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                ),
                craft_platforms.BuildInfo(
                    "ubuntu@24.04:amd64",
                    craft_platforms.DebianArchitecture("riscv64"),
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DistroBase("ubuntu", "24.04"),
                ),
            ],
            id="multi-base-long-multi-build-on",
        ),
        pytest.param(
            None,
            None,
            {
                "noble": {
                    "build-on": ["devel:amd64"],
                    "build-for": ["ubuntu@24.04:amd64"],
                },
            },
            [
                craft_platforms.BuildInfo(
                    "noble",
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DistroBase("ubuntu", "devel"),
                ),
            ],
            id="multi-base-devel-build-on",
        ),
        pytest.param(
            None,
            None,
            {
                "noble": {
                    "build-on": ["ubuntu@devel:amd64"],
                    "build-for": ["ubuntu@24.04:amd64"],
                },
            },
            [
                craft_platforms.BuildInfo(
                    "noble",
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DebianArchitecture("amd64"),
                    craft_platforms.DistroBase("ubuntu", "devel"),
                ),
            ],
            id="multi-base-ubuntu-at-devel-build-on",
        ),
        pytest.param(
            None,
            None,
            {
                "noble": {
                    "build-on": ["devel:amd64"],
                    "build-for": ["ubuntu@24.04:all"],
                },
            },
            [
                craft_platforms.BuildInfo(
                    "noble",
                    craft_platforms.DebianArchitecture("amd64"),
                    "all",
                    craft_platforms.DistroBase("ubuntu", "devel"),
                ),
            ],
            id="multi-base-devel-build-on-all",
        ),
    ],
)
def test_build_plans_in_depth(base, build_base, platforms, expected):
    """Test the exact build plan for a set of items."""
    actual = charm.get_platforms_charm_build_plan(
        base=base,
        build_base=build_base,
        platforms=platforms,
    )

    assert actual == expected


@pytest.mark.parametrize(
    ("base", "build_base", "platforms", "error_msg", "error_res"),
    [
        pytest.param(
            "invalid-base",
            None,
            None,
            "Invalid base string 'invalid-base'. Format should be '<distribution>@<series>'",
            None,
            id="invalid-base",
        ),
        pytest.param(
            None,
            None,
            None,
            "No base, build-base, or platforms are declared.",
            "Declare a base or build-base.",
            id="no-base-no-platform",
        ),
        pytest.param(
            None,
            None,
            {
                "my-platform": {
                    "build-on": ["amd64"],
                    "build-for": ["amd64"],
                },
            },
            "No base or build-base is declared and no base is declared in the platforms section.",
            "Declare a base or build-base.",
            id="no-base-with-platform",
        ),
        pytest.param(
            None,
            None,
            {"amd64": None},
            "No base or build-base is declared and no base is declared in the platforms section.",
            "Declare a base or build-base.",
            id="no-base-with-shorthand-platform",
        ),
        pytest.param(
            "ubuntu@24.04",
            None,
            {"ubuntu@24.04:amd64": None},
            "Platform 'ubuntu@24.04:amd64' declares a base and a top-level base or build-base is declared.",
            "Remove the base from the platform's name or remove the top-level base or build-base.",
            id="base-and-platform-base",
        ),
        pytest.param(
            None,
            "ubuntu@24.04",
            {"ubuntu@24.04:amd64": None},
            "Platform 'ubuntu@24.04:amd64' declares a base and a top-level base or build-base is declared.",
            "Remove the base from the platform's name or remove the top-level base or build-base.",
            id="build-base-and-platform-base",
        ),
        pytest.param(
            "ubuntu@24.04",
            None,
            {
                "my-platform": {
                    "build-on": ["ubuntu@24.04:amd64"],
                    "build-for": ["ubuntu@24.04:amd64"],
                },
            },
            "Platform 'my-platform' declares a base and a top-level base or build-base is declared.",
            "Remove the base from the platform's name or remove the top-level base or build-base.",
            id="base-and-build-on-for-base",
        ),
        pytest.param(
            None,
            "ubuntu@24.04",
            {
                "my-platform": {
                    "build-on": ["ubuntu@24.04:amd64"],
                    "build-for": ["ubuntu@24.04:amd64"],
                },
            },
            "Platform 'my-platform' declares a base and a top-level base or build-base is declared.",
            "Remove the base from the platform's name or remove the top-level base or build-base.",
            id="build-base-and-build-on-for-base",
        ),
        pytest.param(
            None,
            None,
            {
                "my-platform": {
                    "build-on": ["ubuntu@22.04:amd64"],
                    "build-for": ["ubuntu@24.04:amd64"],
                },
            },
            "Platform 'my-platform' has mismatched bases in the 'build-on' and 'build-for' entries.",
            "Use the same base for all 'build-on' and 'build-for' entries for the platform.",
            id="build-on-for-base-mismatch",
        ),
        pytest.param(
            None,
            None,
            {
                "my-platform": {
                    "build-on": ["ubuntu@22.04:amd64"],
                    "build-for": ["amd64"],
                },
            },
            "Platform 'my-platform' has mismatched bases in the 'build-on' and 'build-for' entries.",
            "Use the same base for all 'build-on' and 'build-for' entries for the platform.",
            id="build-on-base-wrong",
        ),
        pytest.param(
            None,
            None,
            {
                "ubuntu@24.04:amd64": {
                    "build-on": ["ubuntu@22.04:amd64"],
                    "build-for": ["amd64"],
                },
            },
            "Platform 'ubuntu@24.04:amd64' has mismatched bases in the 'build-on' and 'build-for' entries.",
            "Use the same base for all 'build-on' and 'build-for' entries for the platform.",
            id="platform-base-with-entries",
        ),
        pytest.param(
            None,
            None,
            {
                "ubuntu@24.04:amd64": {
                    "build-on": ["ubuntu@22.04:amd64"],
                    "build-for": ["ubuntu@22.04:amd64"],
                },
            },
            r"Platform 'ubuntu@24.04:amd64' declares a base in the platform's name and declares an incompatible 'build-for' entry \(ubuntu@22.04\)",
            "Either remove the base from the platform's name or remove the incompatible 'build-for' entry for the platform.",
            id="build-on-base-wrong",
        ),
        pytest.param(
            None,
            None,
            {
                "ubuntu@24.04:amd64": {
                    "build-on": ["ubuntu@22.04:amd64"],
                },
            },
            r"Platform 'ubuntu@24.04:amd64' has mismatched bases in the 'build-on' and 'build-for' entries.",
            "Use the same base for all 'build-on' and 'build-for' entries for the platform.",
            id="platform-base-with-incompatible-build-on",
        ),
        pytest.param(
            None,
            None,
            {
                "noble": {
                    "build-on": ["devel:amd64", "ubuntu@24.04:arm64"],
                    "build-for": ["ubuntu@24.04:amd64"],
                },
            },
            r"Platform 'noble' has mismatched bases in the 'build-on' and 'build-for' entries.",
            "Use the same base for all 'build-on' and 'build-for' entries for the platform.",
            id="devel-and-stable-mixed-build-on",
        ),
    ],
)
def test_build_plans_bad_base(base, build_base, platforms, error_msg, error_res):
    with pytest.raises(
        (ValueError, craft_platforms.CraftPlatformsError), match=error_msg
    ) as err:
        charm.get_platforms_charm_build_plan(
            base=base,
            build_base=build_base,
            platforms=platforms,
        )

    if error_res and isinstance(err.value, craft_platforms.CraftPlatformsError):
        assert err.value.resolution == error_res


@pytest.mark.parametrize(
    ("platforms", "error_msg"),
    [
        pytest.param(
            {"my machine": None},
            "Platform name 'my machine' is not a valid Debian architecture. Specify a build-on and build-for.",
            id="invalid-platform-name-no-details",
        ),
        pytest.param(
            {"my machine": {"build-on": ["my machine"], "build-for": ["amd64"]}},
            "'my machine' is not a valid Debian architecture",
            id="invalid-architecture-name",
        ),
        pytest.param(
            {"my machine": {"build-on": ["all"], "build-for": ["amd64"]}},
            "Platform 'my machine' has an invalid 'build-on' entry of 'all'.",
            id="build-on-all",
        ),
    ],
)
def test_build_plans_bad_architecture(platforms, error_msg):
    with pytest.raises(ValueError, match=error_msg):
        charm.get_platforms_charm_build_plan("ubuntu@24.04", platforms)


def _is_valid_platform(platforms):
    """Allow test suite to pass until #116 is fixed."""
    for platform in platforms:
        if ":" in platform:
            platform_name, _, platform_base = platform.partition(":")
            if not platform_base or not platform_name or "@" not in platform_name:
                print(f"Skipping unhandled platform name {platform} (#116)")
                return False

    return True


def _is_valid_multi_base_platform_dict(p):
    """Return True if the platform dict is consistent for multi-base builds.

    A valid multi-base platform dict must satisfy:
    - All ``build-on`` entries either share the same base as ``build-for``,
      or are devel-series entries (exactly ``"devel"`` or ``"*@devel"``).
    - ``build-on`` must not mix devel-series entries with entries that carry
      an explicit non-devel base, for the same reason that two different
      stable bases in ``build-on`` are rejected.
    """
    build_ons = p["build-on"] if isinstance(p["build-on"], list) else [p["build-on"]]
    build_fors = p["build-for"] if isinstance(p["build-for"], list) else [p["build-for"]]
    build_for_base = build_fors[0].partition(":")[0]

    devel_build_ons = [
        on
        for on in build_ons
        if on.partition(":")[0] == "devel" or on.partition(":")[0].endswith("@devel")
    ]
    # build-on entries that carry an explicit distro@series that is not devel
    non_devel_with_base_build_ons = [
        on
        for on in build_ons
        if "@" in on.partition(":")[0]
        and not on.partition(":")[0].endswith("@devel")
    ]

    # Mixing devel and explicit non-devel bases in build-on is not allowed.
    if devel_build_ons and non_devel_with_base_build_ons:
        return False

    # All non-devel entries that carry an explicit base must match build-for.
    return all(
        on.partition(":")[0] == build_for_base for on in non_devel_with_base_build_ons
    )


@given(
    base=strategies.real_distro_base(),
    platforms=strategies.platform(
        distro_base=strategies.any_distro_base(),
        shorthand_keys=strategies.build_on_arch_str(),
        values=strategies.platform_dict(
            build_ons=strategies.build_on_arch_str(),
            build_fors=strategies.build_for_arch_str(),
        ),
    ),
    build_base=hp_strat.one_of(hp_strat.none(), strategies.any_distro_base()),
)
def test_fuzz_get_platforms_build_plan_single_base(
    base: craft_platforms.DistroBase,
    platforms: craft_platforms.Platforms,
    build_base: Optional[craft_platforms.DistroBase],
):
    assume(_is_valid_platform(platforms))
    craft_platforms.charm.get_platforms_charm_build_plan(
        base=str(base),
        platforms=platforms,
        build_base=str(build_base) if build_base else None,
    )


@pytest.mark.slow
@given(
    platforms=strategies.platform(
        distro_base=strategies.real_distro_base(),
        shorthand_keys=strategies.distro_series_arch_str(strategies.any_distro_base()),
        values=strategies.platform_dict(
            build_ons=strategies.distro_series_arch_str(strategies.any_distro_base()),
            build_fors=strategies.distro_series_arch_str(strategies.any_distro_base()),
        ).filter(_is_valid_multi_base_platform_dict),
    ),
)
def test_fuzz_get_platforms_build_plan_multi_base(
    platforms: craft_platforms.Platforms,
):
    assume(_is_valid_platform(platforms))
    craft_platforms.charm.get_platforms_charm_build_plan(None, platforms)


@pytest.mark.parametrize(
    ("bases", "expected"),
    [
        pytest.param(
            [{"name": "ubuntu", "channel": "20.04"}],
            [
                craft_platforms.BuildInfo(
                    "ubuntu-20.04-amd64",
                    craft_platforms.DebianArchitecture.AMD64,
                    craft_platforms.DebianArchitecture.AMD64,
                    craft_platforms.DistroBase("ubuntu", "20.04"),
                ),
                craft_platforms.BuildInfo(
                    "ubuntu-20.04-arm64",
                    craft_platforms.DebianArchitecture.ARM64,
                    craft_platforms.DebianArchitecture.ARM64,
                    craft_platforms.DistroBase("ubuntu", "20.04"),
                ),
                craft_platforms.BuildInfo(
                    "ubuntu-20.04-ppc64el",
                    craft_platforms.DebianArchitecture.PPC64EL,
                    craft_platforms.DebianArchitecture.PPC64EL,
                    craft_platforms.DistroBase("ubuntu", "20.04"),
                ),
                craft_platforms.BuildInfo(
                    "ubuntu-20.04-riscv64",
                    craft_platforms.DebianArchitecture.RISCV64,
                    craft_platforms.DebianArchitecture.RISCV64,
                    craft_platforms.DistroBase("ubuntu", "20.04"),
                ),
                craft_platforms.BuildInfo(
                    "ubuntu-20.04-s390x",
                    craft_platforms.DebianArchitecture.S390X,
                    craft_platforms.DebianArchitecture.S390X,
                    craft_platforms.DistroBase("ubuntu", "20.04"),
                ),
            ],
        ),
        pytest.param(
            [{"name": "ubuntu", "channel": "22.04", "architectures": ["arm64"]}],
            [
                craft_platforms.BuildInfo(
                    "ubuntu-22.04-arm64",
                    craft_platforms.DebianArchitecture.ARM64,
                    craft_platforms.DebianArchitecture.ARM64,
                    craft_platforms.DistroBase("ubuntu", "22.04"),
                ),
            ],
        ),
        pytest.param(
            [
                {
                    "build-on": [
                        {
                            "name": "ubuntu",
                            "channel": "22.04",
                            "architectures": ["amd64", "s390x"],
                        }
                    ],
                    "run-on": [
                        {
                            "name": "ubuntu",
                            "channel": "22.04",
                            "architectures": ["s390x"],
                        }
                    ],
                },
            ],
            [
                craft_platforms.BuildInfo(
                    "ubuntu-22.04-s390x",
                    craft_platforms.DebianArchitecture.AMD64,
                    craft_platforms.DebianArchitecture.S390X,
                    craft_platforms.DistroBase("ubuntu", "22.04"),
                ),
                craft_platforms.BuildInfo(
                    "ubuntu-22.04-s390x",
                    craft_platforms.DebianArchitecture.S390X,
                    craft_platforms.DebianArchitecture.S390X,
                    craft_platforms.DistroBase("ubuntu", "22.04"),
                ),
            ],
        ),
        pytest.param(
            [
                {
                    "build-on": [
                        {
                            "name": "ubuntu",
                            "channel": "22.04",
                            "architectures": ["amd64", "riscv64"],
                        },
                        {
                            "name": "ubuntu",
                            "channel": "20.04",
                            "architectures": ["amd64", "arm64"],
                        },
                    ],
                    "run-on": [
                        {
                            "name": "ubuntu",
                            "channel": "22.04",
                            "architectures": ["amd64"],
                        },
                        {
                            "name": "ubuntu",
                            "channel": "22.04",
                            "architectures": ["riscv64"],
                        },
                        {
                            "name": "ubuntu",
                            "channel": "22.04",
                            "architectures": ["arm64"],
                        },
                    ],
                },
                {
                    "build-on": [{"name": "ubuntu", "channel": "20.04"}],
                    "run-on": [
                        {
                            "name": "ubuntu",
                            "channel": "20.04",
                            "architectures": [
                                "amd64",
                                "arm64",
                                "riscv64",
                                "s390x",
                                "ppc64el",
                                "armhf",
                            ],
                        }
                    ],
                },
            ],
            [
                craft_platforms.BuildInfo(
                    platform="ubuntu-22.04-amd64",
                    build_on=craft_platforms.DebianArchitecture.AMD64,
                    build_for=craft_platforms.DebianArchitecture.AMD64,
                    build_base=craft_platforms.DistroBase(
                        distribution="ubuntu",
                        series="22.04",
                    ),
                ),
                craft_platforms.BuildInfo(
                    platform="ubuntu-22.04-amd64",
                    build_on=craft_platforms.DebianArchitecture.RISCV64,
                    build_for=craft_platforms.DebianArchitecture.AMD64,
                    build_base=craft_platforms.DistroBase(
                        distribution="ubuntu",
                        series="22.04",
                    ),
                ),
                craft_platforms.BuildInfo(
                    platform="ubuntu-22.04-riscv64",
                    build_on=craft_platforms.DebianArchitecture.AMD64,
                    build_for=craft_platforms.DebianArchitecture.RISCV64,
                    build_base=craft_platforms.DistroBase(
                        distribution="ubuntu",
                        series="22.04",
                    ),
                ),
                craft_platforms.BuildInfo(
                    platform="ubuntu-22.04-riscv64",
                    build_on=craft_platforms.DebianArchitecture.RISCV64,
                    build_for=craft_platforms.DebianArchitecture.RISCV64,
                    build_base=craft_platforms.DistroBase(
                        distribution="ubuntu",
                        series="22.04",
                    ),
                ),
                craft_platforms.BuildInfo(
                    platform="ubuntu-22.04-arm64",
                    build_on=craft_platforms.DebianArchitecture.AMD64,
                    build_for=craft_platforms.DebianArchitecture.ARM64,
                    build_base=craft_platforms.DistroBase(
                        distribution="ubuntu",
                        series="22.04",
                    ),
                ),
                craft_platforms.BuildInfo(
                    platform="ubuntu-22.04-arm64",
                    build_on=craft_platforms.DebianArchitecture.RISCV64,
                    build_for=craft_platforms.DebianArchitecture.ARM64,
                    build_base=craft_platforms.DistroBase(
                        distribution="ubuntu",
                        series="22.04",
                    ),
                ),
                craft_platforms.BuildInfo(
                    platform="ubuntu-20.04-amd64",
                    build_on=craft_platforms.DebianArchitecture.AMD64,
                    build_for=craft_platforms.DebianArchitecture.AMD64,
                    build_base=craft_platforms.DistroBase(
                        distribution="ubuntu",
                        series="20.04",
                    ),
                ),
                craft_platforms.BuildInfo(
                    platform="ubuntu-20.04-amd64",
                    build_on=craft_platforms.DebianArchitecture.ARM64,
                    build_for=craft_platforms.DebianArchitecture.AMD64,
                    build_base=craft_platforms.DistroBase(
                        distribution="ubuntu",
                        series="20.04",
                    ),
                ),
                craft_platforms.BuildInfo(
                    platform="ubuntu-20.04-riscv64",
                    build_on=craft_platforms.DebianArchitecture.AMD64,
                    build_for=craft_platforms.DebianArchitecture.RISCV64,
                    build_base=craft_platforms.DistroBase(
                        distribution="ubuntu",
                        series="20.04",
                    ),
                ),
                craft_platforms.BuildInfo(
                    platform="ubuntu-20.04-riscv64",
                    build_on=craft_platforms.DebianArchitecture.ARM64,
                    build_for=craft_platforms.DebianArchitecture.RISCV64,
                    build_base=craft_platforms.DistroBase(
                        distribution="ubuntu",
                        series="20.04",
                    ),
                ),
                craft_platforms.BuildInfo(
                    platform="ubuntu-20.04-arm64",
                    build_on=craft_platforms.DebianArchitecture.AMD64,
                    build_for=craft_platforms.DebianArchitecture.ARM64,
                    build_base=craft_platforms.DistroBase(
                        distribution="ubuntu",
                        series="20.04",
                    ),
                ),
                craft_platforms.BuildInfo(
                    platform="ubuntu-20.04-arm64",
                    build_on=craft_platforms.DebianArchitecture.ARM64,
                    build_for=craft_platforms.DebianArchitecture.ARM64,
                    build_base=craft_platforms.DistroBase(
                        distribution="ubuntu",
                        series="20.04",
                    ),
                ),
                craft_platforms.BuildInfo(
                    platform="ubuntu-20.04-amd64-arm64-riscv64-s390x-ppc64el-armhf",
                    build_on=craft_platforms.DebianArchitecture.AMD64,
                    build_for=craft_platforms.DebianArchitecture.AMD64,
                    build_base=craft_platforms.DistroBase(
                        distribution="ubuntu",
                        series="20.04",
                    ),
                ),
                craft_platforms.BuildInfo(
                    platform="ubuntu-20.04-amd64-arm64-riscv64-s390x-ppc64el-armhf",
                    build_on=craft_platforms.DebianArchitecture.ARM64,
                    build_for=craft_platforms.DebianArchitecture.AMD64,
                    build_base=craft_platforms.DistroBase(
                        distribution="ubuntu",
                        series="20.04",
                    ),
                ),
                craft_platforms.BuildInfo(
                    platform="ubuntu-20.04-amd64-arm64-riscv64-s390x-ppc64el-armhf",
                    build_on=craft_platforms.DebianArchitecture.PPC64EL,
                    build_for=craft_platforms.DebianArchitecture.AMD64,
                    build_base=craft_platforms.DistroBase(
                        distribution="ubuntu",
                        series="20.04",
                    ),
                ),
                craft_platforms.BuildInfo(
                    platform="ubuntu-20.04-amd64-arm64-riscv64-s390x-ppc64el-armhf",
                    build_on=craft_platforms.DebianArchitecture.RISCV64,
                    build_for=craft_platforms.DebianArchitecture.AMD64,
                    build_base=craft_platforms.DistroBase(
                        distribution="ubuntu",
                        series="20.04",
                    ),
                ),
                craft_platforms.BuildInfo(
                    platform="ubuntu-20.04-amd64-arm64-riscv64-s390x-ppc64el-armhf",
                    build_on=craft_platforms.DebianArchitecture.S390X,
                    build_for=craft_platforms.DebianArchitecture.AMD64,
                    build_base=craft_platforms.DistroBase(
                        distribution="ubuntu",
                        series="20.04",
                    ),
                ),
            ],
        ),
    ],
)
def test_bases_build_plan_success(bases, expected):
    assert charm.get_bases_charm_build_plan(bases) == expected
