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

import craft_platforms
import pytest
import pytest_check
from craft_platforms import charm

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
def test_build_plans_success(
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
        with pytest_check.check():
            assert build_item.build_base == expected_base
        with pytest_check.check():
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
    actual = charm.get_platforms_charm_build_plan(
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
        charm.get_platforms_charm_build_plan(base, None)


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
            "'my machine' is not a valid DebianArchitecture",
            id="invalid-architecture-name",
        ),
    ],
)
def test_build_plans_bad_architecture(platforms, error_msg):
    with pytest.raises(ValueError, match=error_msg):
        charm.get_platforms_charm_build_plan("ubuntu@24.04", platforms)
