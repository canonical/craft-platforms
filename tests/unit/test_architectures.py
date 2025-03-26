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
"""Unit tests for architectures."""

import platform

import pytest
from craft_platforms import DebianArchitecture, DistroBase, parse_base_and_architecture
from craft_platforms.test import strategies
from hypothesis import given


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        pytest.param("AMD64", DebianArchitecture.AMD64, id="amd64-windows"),
        pytest.param("x86_64", DebianArchitecture.AMD64, id="converted"),
        pytest.param("riscv64", DebianArchitecture.RISCV64, id="not-converted"),
    ],
)
def test_debian_architectures_from_machine(given, expected):
    assert DebianArchitecture.from_machine(given) == expected


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        pytest.param(DebianArchitecture.AMD64, "x86_64", id="converted"),
        pytest.param(DebianArchitecture.RISCV64, "riscv64", id="not-converted"),
    ],
)
def test_debian_architecture_to_platform_arch(given, expected):
    assert given.to_platform_arch() == expected


@pytest.mark.parametrize("machine", ["aarch64", "x86_64", "riscv64"])
def test_debian_architecture_from_host(monkeypatch, machine):
    monkeypatch.setattr(platform, "machine", lambda: machine)
    assert DebianArchitecture.from_host().to_platform_arch() == machine


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        (str(DebianArchitecture.AMD64), (None, "amd64")),
        (str(DebianArchitecture.RISCV64), (None, "riscv64")),
        ("all", (None, "all")),
        ("ubuntu@24.04:amd64", (DistroBase("ubuntu", "24.04"), "amd64")),
        ("ubuntu@24.04:riscv64", (DistroBase("ubuntu", "24.04"), "riscv64")),
        ("ubuntu@24.04:all", (DistroBase("ubuntu", "24.04"), "all")),
    ],
)
def test_parse_base_and_architecture(given, expected):
    assert parse_base_and_architecture(given) == expected


def test_parse_base_and_architecture_invalid_arch():
    expected = "'unknown' is not a valid Debian architecture."

    with pytest.raises(ValueError, match=expected):
        parse_base_and_architecture("unknown")


def test_parse_base_and_architecture_invalid_base():
    expected = (
        "Invalid base string 'unknown'. Format should be '<distribution>@<series>'"
    )

    with pytest.raises(ValueError, match=expected):
        parse_base_and_architecture("unknown:riscv64")


@given(
    base=strategies.any_distro_base(),
    arch=strategies.build_for_arch_str(),
)
def test_fuzz_parse_base_and_architecture(base, arch):
    out_base, out_arch = parse_base_and_architecture(f"{base}:{arch}")

    assert out_base == base
    assert out_arch == arch
