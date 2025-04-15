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

"""Utilities for craft-platforms."""

from typing import Sequence, Union


def vectorize(item: Union[str, Sequence[str]]) -> Sequence[str]:
    """Convert a string into a sequence of strings.

    If the item is already a sequence, it is returned as-is.

    :param item: The item to vectorize.

    :returns: A sequence of strings.
    """
    if isinstance(item, str):
        return [item]
    return item
