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
"""Charm-specific module for craft-platforms."""

from ._build import (
    DEFAULT_ARCHITECTURES,
    get_platforms_charm_build_plan,
    get_bases_charm_build_plan,
    get_charm_build_plan,
)


__all__ = [
    "DEFAULT_ARCHITECTURES",
    "get_platforms_charm_build_plan",
    "get_bases_charm_build_plan",
    "get_charm_build_plan",
]
