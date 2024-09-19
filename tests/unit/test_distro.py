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
"""Unit tests for distro utilities."""

import itertools

import craft_platforms
import distro
import pytest
import pytest_check

CENTOS_7 = """\
NAME="CentOS Linux"
VERSION="7 (Core)"
ID="centos"
ID_LIKE="rhel fedora"
VERSION_ID="7"
PRETTY_NAME="CentOS Linux 7 (Core)"
ANSI_COLOR="0;31"
CPE_NAME="cpe:/o:centos:centos:7"
HOME_URL="https://www.centos.org/"
BUG_REPORT_URL="https://bugs.centos.org/"

CENTOS_MANTISBT_PROJECT="CentOS-7"
CENTOS_MANTISBT_PROJECT_VERSION="7"
REDHAT_SUPPORT_PRODUCT="centos"
REDHAT_SUPPORT_PRODUCT_VERSION="7"
"""
DEBIAN_10 = """\
PRETTY_NAME="Debian GNU/Linux 10 (buster)"
NAME="Debian GNU/Linux"
VERSION_ID="10"
VERSION="10 (buster)"
VERSION_CODENAME=buster
ID=debian
HOME_URL="https://www.debian.org/"
SUPPORT_URL="https://www.debian.org/support"
BUG_REPORT_URL="https://bugs.debian.org/"
"""

# Sample linux distributions used for tests. These don't need to be supported.
DAPPER = craft_platforms.DistroBase("ubuntu", "6.06")
BIONIC = craft_platforms.DistroBase("ubuntu", "18.04")
FOCAL = craft_platforms.DistroBase("ubuntu", "20.04")
JAMMY = craft_platforms.DistroBase("ubuntu", "22.04")
NOBLE = craft_platforms.DistroBase("ubuntu", "24.04")
ORACULAR = craft_platforms.DistroBase("ubuntu", "24.10")
DEVEL = craft_platforms.DistroBase("ubuntu", "devel")
BUSTER = craft_platforms.DistroBase("debian", "10")
BOOKWORM = craft_platforms.DistroBase("debian", "12")
ALMA_EIGHT = craft_platforms.DistroBase("almalinux", "8.10")
ALMA_NINE = craft_platforms.DistroBase("almalinux", "9")
ALMA_NINE_FOUR = craft_platforms.DistroBase("almalinux", "9.4")

ALL_UBUNTU = [DAPPER, BIONIC, FOCAL, JAMMY, NOBLE, ORACULAR, DEVEL]
ALL_DEBIAN = [BUSTER, BOOKWORM]
ALL_ALMA = [ALMA_EIGHT, ALMA_NINE]
ALL_DISTROS = [*ALL_UBUNTU, *ALL_DEBIAN, *ALL_ALMA]


@pytest.mark.parametrize(
    ("base", "other", "expected"),
    [
        *[(distro, distro, True) for distro in ALL_DISTROS],
        *[
            (first, second, False)
            for first, second in itertools.permutations(ALL_DISTROS, r=2)
        ],
        *[(distro, ("bsd", "4.2.2"), False) for distro in ALL_DISTROS],
        *[
            pytest.param(
                distro,
                (distro.distribution, distro.series),
                True,
                id=f"{distro.series}_tuple",
            )
            for distro in ALL_DISTROS
        ],
        (ALMA_NINE, ALMA_NINE_FOUR, True),
    ],
)
def test_distro_base_equality(base, other, expected):
    assert (base == other) == expected
    assert (other == base) == expected  # Ensure equality works both ways


@pytest.mark.parametrize(
    ("smaller", "bigger"),
    [
        *[
            pytest.param(
                craft_platforms.DistroBase("ubuntu", "4.10"),
                version,
                id=f"ubuntu_warty_vs_{version.series}",
            )
            for version in ALL_UBUNTU
        ],
        *[
            pytest.param(
                version,
                craft_platforms.DistroBase("ubuntu", "999999.10"),
                id=f"ubuntu_infinity_vs_{version.series}",
            )
            # ubuntu 999999.10 is greater than all ubuntu releases except ubuntu@devel
            for version in ALL_UBUNTU
            if version != DEVEL
        ],
        *[
            pytest.param(
                version,
                craft_platforms.DistroBase("ubuntu", "devel"),
                id=f"ubuntu_devel_vs_{version.series}",
            )
            # ubuntu@devel is greater than all ubuntu releases
            for version in ALL_UBUNTU
            if version != DEVEL
        ],
        *[
            pytest.param(
                craft_platforms.DistroBase("debian", "1.1"),
                version,
                id=f"debian_buzz_vs_{version.series}",
            )
            for version in ALL_DEBIAN
        ],
        *[
            pytest.param(
                version,
                craft_platforms.DistroBase("debian", "99999"),
                id=f"debian_future_vs_{version.series}",
            )
            for version in ALL_DEBIAN
        ],
        *[
            pytest.param(
                craft_platforms.DistroBase("almalinux", "0"),
                version,
                id=f"alma_zero_vs_{version.series}",
            )
            for version in ALL_ALMA
        ],
        *[
            pytest.param(
                version,
                craft_platforms.DistroBase("almalinux", "99999"),
                id=f"alma_future_vs_{version.series}",
            )
            for version in ALL_ALMA
        ],
    ],
)
def test_distro_base_difference_success(smaller, bigger):
    with pytest_check.check():
        assert bigger > smaller
    with pytest_check.check():
        assert bigger >= smaller
    with pytest_check.check():
        assert smaller <= bigger
    with pytest_check.check():
        assert smaller < bigger
    with pytest_check.check():
        assert bigger != smaller


@pytest.mark.parametrize(
    ("first", "second"),
    [
        *list(itertools.product(ALL_UBUNTU, ALL_DEBIAN)),
        *list(itertools.product(ALL_UBUNTU, ALL_ALMA)),
        *list(itertools.product(ALL_DEBIAN, ALL_ALMA)),
    ],
)
def test_compare_incompatible_distros(first, second):
    pytest_check.is_false(first == second)
    pytest_check.is_false(second == first)
    pytest_check.is_true(first != second)
    pytest_check.is_true(second != first)
    with pytest_check.raises(
        ValueError,
    ):  # pyright: ignore[reportOptionalContextManager]
        assert first > second
    with pytest_check.raises(
        ValueError,
    ):  # pyright: ignore[reportOptionalContextManager]
        assert first >= second
    with pytest_check.raises(
        ValueError,
    ):  # pyright: ignore[reportOptionalContextManager]
        assert first <= second
    with pytest_check.raises(
        ValueError,
    ):  # pyright: ignore[reportOptionalContextManager]
        assert first < second
    with pytest_check.raises(
        ValueError,
    ):  # pyright: ignore[reportOptionalContextManager]
        assert second > first
    with pytest_check.raises(
        ValueError,
    ):  # pyright: ignore[reportOptionalContextManager]
        assert second >= first
    with pytest_check.raises(
        ValueError,
    ):  # pyright: ignore[reportOptionalContextManager]
        assert second <= first
    with pytest_check.raises(
        ValueError,
    ):  # pyright: ignore[reportOptionalContextManager]
        assert second < first


@pytest.mark.parametrize(
    ("os_release", "expected"),
    [
        (CENTOS_7, False),
        (DEBIAN_10, False),
    ],
)
def test_is_ubuntu_like(os_release: str, expected):
    distribution = distro.LinuxDistribution(
        include_lsb=False,
        os_release_file=os_release,
    )
    assert craft_platforms.is_ubuntu_like(distribution) is expected


@pytest.mark.parametrize(
    ("distro_string", "expected"),
    [
        ("ubuntu@6.06", DAPPER),
        ("ubuntu@18.04", BIONIC),
        ("ubuntu@20.04", FOCAL),
        ("ubuntu@22.04", JAMMY),
        ("ubuntu@24.04", NOBLE),
        ("ubuntu@24.10", ORACULAR),
        ("devel", DEVEL),
        ("ubuntu@devel", DEVEL),
        ("debian@10", BUSTER),
        ("debian@12", BOOKWORM),
        ("almalinux@8.10", ALMA_EIGHT),
        ("almalinux@9.4", ALMA_NINE),
    ],
)
def test_from_str(distro_string, expected):
    actual = craft_platforms.DistroBase.from_str(distro_string)

    assert actual == expected


def test_from_str_error():
    with pytest.raises(ValueError, match="Invalid base string 'invalid-base'.*"):
        craft_platforms.DistroBase.from_str("invalid-base")
