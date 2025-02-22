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
"""Unit tests for hypothesis strategies."""

from typing import Dict, Union

import craft_platforms
import pytest
from craft_platforms.test import strategies
from hypothesis import given


@pytest.mark.parametrize("version", strategies._UBUNTU_VERSIONS)
def test_ubuntu_version(version: str):
    if version == "6.06":  # Special case for Dapper Drake
        return
    assert version != "6.04"

    year, month = version.split(".")
    assert month in ("04", "10")
    assert int(year) in range(4, 100)
    assert version != "4.04"


@given(strategies.ubuntu_series())
def test_ubuntu_series(base: craft_platforms.DistroBase) -> None:
    assert base.distribution == "ubuntu"

    assert base.series in strategies._UBUNTU_VERSIONS


@given(strategies.debian_series())
def test_debian_series(base: craft_platforms.DistroBase) -> None:
    assert base.distribution == "debian"

    assert base.series in strategies._DEBIAN_VERSIONS


@given(strategies.ubuntu_lts())
def test_ubuntu_lts(base: craft_platforms.DistroBase) -> None:
    assert base.distribution == "ubuntu"
    assert base.series in strategies._UBUNTU_LTS


@given(strategies.real_distro_base())
def test_real_distro_base(base):
    assert isinstance(base, craft_platforms.DistroBase)
    assert base.distribution in ("debian", "ubuntu")


@given(strategies.any_distro_base())
def test_any_distro_base(base):
    assert isinstance(base, craft_platforms.DistroBase)
    assert isinstance(base.distribution, str)
    assert isinstance(base.series, str)


@given(strategies.build_for_arch_str())
def test_build_for_arch_str(build_for: str):
    if build_for == "all":
        return
    craft_platforms.DebianArchitecture(build_for)


@given(strategies.distro_series_arch_str(strategies.any_distro_base()))
def test_distro_series_arch_str(distro_base_arch_str: str):
    distro_base, arch = distro_base_arch_str.split(":")

    craft_platforms.DistroBase.from_str(distro_base)
    craft_platforms.DebianArchitecture(arch)


@given(strategies.build_on_str(strategies.any_distro_base()))
def test_build_on_str(build_on_str: str):
    base, arch = craft_platforms.parse_base_and_architecture(build_on_str)
    assert base is None or isinstance(base, craft_platforms.DistroBase)
    assert isinstance(arch, craft_platforms.DebianArchitecture)


@given(strategies.build_for_str(strategies.any_distro_base()))
def test_build_for_str(build_for_str: str):
    base, arch = craft_platforms.parse_base_and_architecture(build_for_str)
    assert base is None or isinstance(base, craft_platforms.DistroBase)
    assert arch == "all" or isinstance(arch, craft_platforms.DebianArchitecture)


def check_platform_dict(platform_dict: Union[dict, craft_platforms.PlatformDict]):
    assert platform_dict.keys() == {"build-on", "build-for"}

    for build_on in platform_dict["build-on"]:
        _, build_arch = craft_platforms.parse_base_and_architecture(build_on)
        assert isinstance(build_arch, craft_platforms.DebianArchitecture)
    assert len(platform_dict["build-for"]) == 1
    craft_platforms.parse_base_and_architecture(platform_dict["build-for"][0])


@given(strategies.platform_dict(max_build_ons=None))
def test_platform_dicts(platform_dict: dict):
    check_platform_dict(platform_dict)


def check_platforms(platforms: Dict[str, Union[craft_platforms.PlatformDict, None]]):
    for name, value in platforms.items():
        if value is None:
            _, build_arch = craft_platforms.parse_base_and_architecture(name)
            assert isinstance(build_arch, craft_platforms.DebianArchitecture)
        else:
            check_platform_dict(value)


@given(strategies.platform(strategies.any_distro_base()))
def test_platform(platform: Dict[str, Union[craft_platforms.PlatformDict, None]]):
    assert len(platform) == 1
    check_platforms(platform)


@given(strategies.platforms(strategies.any_distro_base()))
def test_platforms(platforms):
    check_platforms(platforms)
