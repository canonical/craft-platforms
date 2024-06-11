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
"""Platform related models."""
import typing
from collections.abc import Sequence
from typing import Annotated

import annotated_types

from craft_platforms import _architectures

PlatformDict = typing.TypedDict(
    "PlatformDict",
    {
        "build-on": Sequence[str],
        "build-for": Annotated[Sequence[str], annotated_types.Len(1)],
    },
)


Platforms = dict[_architectures.DebianArchitecture | str, PlatformDict | None]
