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
"""Unit tests for validator functions."""

import pytest
from craft_platforms import InvalidPlatformNameError
from craft_platforms.validators import (
    _ALLOWED_MIDDLE_CHARACTERS,
    _ALLOWED_UNICODE_CATEGORIES,
    _APPLICATION_RESERVED_CHARACTERS,
    validate_strict_platform_name,
)
from hypothesis import given, strategies

SAMPLE_VALID_PLATFORM_NAMES = [
    "a",
    "1",
    "🇧🇷",
    "amd64",
    "raspi-4b-amd64",
    "a-dead-badger",
    "ubuntu@24.04:amd64",
]

SAMPLE_VALID_APP_ONLY_PLATFORM_NAMES = ["mycraft/secret_platform", "x86_64"]

SAMPLE_INVALID_PLATFORM_NAMES = [
    ";",
]


@pytest.mark.parametrize("name", SAMPLE_VALID_PLATFORM_NAMES)
def test_validate_strict_platform_name_success(name: str):
    assert validate_strict_platform_name(name, allow_app_characters=False) == name


@pytest.mark.parametrize(
    "name", SAMPLE_VALID_PLATFORM_NAMES + SAMPLE_VALID_APP_ONLY_PLATFORM_NAMES
)
def test_validate_strict_platform_name_success_include_app(name: str):
    assert validate_strict_platform_name(name) == name


@given(
    name=strategies.text(
        strategies.characters(
            categories=_ALLOWED_UNICODE_CATEGORIES,
            include_characters=_ALLOWED_MIDDLE_CHARACTERS,
        ).filter(
            lambda s: (
                not s.startswith(_ALLOWED_MIDDLE_CHARACTERS)
                and not s.endswith(_ALLOWED_MIDDLE_CHARACTERS)
            )
        )
    ),
)
def test_fuzz_allowed_categories(name: str):
    assert validate_strict_platform_name(name, allow_app_characters=False) == name


@given(
    name=strategies.text(
        strategies.characters(
            categories=_ALLOWED_UNICODE_CATEGORIES,
            include_characters=_ALLOWED_MIDDLE_CHARACTERS,
        ).filter(
            lambda s: (
                not s.startswith(_ALLOWED_MIDDLE_CHARACTERS)
                and not s.endswith(_ALLOWED_MIDDLE_CHARACTERS)
            )
        )
    ),
)
def test_fuzz_allowed_categories_include_app(name: str):
    assert validate_strict_platform_name(name, allow_app_characters=True) == name


@pytest.mark.parametrize(
    "name",
    SAMPLE_INVALID_PLATFORM_NAMES,
)
def test_invalid_platform_names_app_allowed(name: str):
    with pytest.raises(InvalidPlatformNameError):
        validate_strict_platform_name(name)


@pytest.mark.parametrize(
    "name",
    SAMPLE_INVALID_PLATFORM_NAMES + SAMPLE_VALID_APP_ONLY_PLATFORM_NAMES,
)
def test_invalid_platform_names_user_only(name: str):
    with pytest.raises(InvalidPlatformNameError):
        validate_strict_platform_name(name, allow_app_characters=False)


@given(
    name=strategies.text(
        strategies.characters(
            exclude_categories=_ALLOWED_UNICODE_CATEGORIES,
            exclude_characters=_ALLOWED_MIDDLE_CHARACTERS,
        ),
        min_size=1,
    )
)
def test_fuzz_banned_categories_user_name(name: str):
    with pytest.raises(InvalidPlatformNameError):
        validate_strict_platform_name(name, allow_app_characters=False)


@given(
    name=strategies.text(
        strategies.characters(
            exclude_categories=_ALLOWED_UNICODE_CATEGORIES,
            exclude_characters=_ALLOWED_MIDDLE_CHARACTERS
            + _APPLICATION_RESERVED_CHARACTERS,
        ),
        min_size=1,
    )
)
def test_fuzz_banned_categories_app_name(name: str):
    with pytest.raises(InvalidPlatformNameError):
        validate_strict_platform_name(name, allow_app_characters=True)
