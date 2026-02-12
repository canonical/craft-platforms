# This file is part of craft-platforms.
#
# Copyright 2026 Canonical Ltd.
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
"""Validator functions.

These functions both work locally to validate fields and can be used as Pydantic
validators.
"""

import unicodedata

from craft_platforms._errors import InvalidPlatformNameError
from craft_platforms._platforms import RESERVED_PLATFORM_NAMES

_ALLOWED_UNICODE_CATEGORIES = (
    # See: https://www.unicode.org/reports/tr44/tr44-34.html#General_Category_Values
    "L",  # All letter characters
    "N",  # All numbers
    "So",  # Other symbols
)

_ALLOWED_MIDDLE_CHARACTERS = (
    "-",
    "@",
    ".",
    ":",
)  # Characters only allowed in the middle of a name.

_APPLICATION_RESERVED_CHARACTERS = ("/", "_")  # Only allowed for use by an application.


def validate_strict_platform_name(
    name: str, *, allow_app_characters: bool = True
) -> str:
    """Validate a strictly-defined platform name.

    :param name: the platform name to validate.
    :param allow_app_characters: Whether to allow characters that are reserved for use
        by applications. If False, an app-generated platform name can raise an error.
    :returns: the platform name, if valid.
    :raises: InvalidPlatformName if the platform name is invalid.
    """
    if name in RESERVED_PLATFORM_NAMES:
        raise InvalidPlatformNameError(
            message=f"Platform name {name!r} is reserved.",
            resolution=f"Rename platform {name!r} to follow the naming rules.",
            doc_slug="platform-name-rules",
            reportable=False,
        )
    invalid_characters = []
    if not allow_app_characters:
        invalid_characters.extend(
            character
            for character in _APPLICATION_RESERVED_CHARACTERS
            if character in name
        )

    invalid_characters.extend(
        character
        for character in _ALLOWED_MIDDLE_CHARACTERS
        if name.startswith(character) or name.endswith(character)
    )

    for character in name:
        category = unicodedata.category(character)
        if character in (_ALLOWED_MIDDLE_CHARACTERS + _APPLICATION_RESERVED_CHARACTERS):
            continue
        for allowed_category in _ALLOWED_UNICODE_CATEGORIES:
            if category.startswith(allowed_category):
                break
        else:
            invalid_characters.append(character)

    if invalid_characters:
        raise InvalidPlatformNameError(
            message=f"Invalid platform name: {name!r}",
            details=f"Platform name contains invalid characters: {invalid_characters}",
            resolution=f"Rename platform {name!r} to follow the naming rules.",
            doc_slug="platform-name-rules",
            reportable=False,
        )

    return name
