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
"""Integration tests for platform types."""

import pydantic
import pytest
from craft_platforms.platform_types import StrictAppPlatformName, StrictPlatformName

from tests.unit.test_validators import (
    SAMPLE_INVALID_PLATFORM_NAMES,
    SAMPLE_VALID_APP_ONLY_PLATFORM_NAMES,
    SAMPLE_VALID_PLATFORM_NAMES,
)


@pytest.mark.parametrize("name", SAMPLE_VALID_PLATFORM_NAMES)
def test_strict_platform_name_pydantic_success(name: str):
    pydantic.TypeAdapter(StrictPlatformName).validate_python(name)


@pytest.mark.parametrize(
    "name", SAMPLE_VALID_PLATFORM_NAMES + SAMPLE_VALID_APP_ONLY_PLATFORM_NAMES
)
def test_validate_strict_platform_name_pydantic_success_include_app(name: str):
    pydantic.TypeAdapter(StrictAppPlatformName).validate_python(name)


@pytest.mark.parametrize(
    "name",
    SAMPLE_INVALID_PLATFORM_NAMES + SAMPLE_VALID_APP_ONLY_PLATFORM_NAMES,
)
def test_validate_strict_user_platform_name_pydantic_error(name: str):
    adapter = pydantic.TypeAdapter(StrictPlatformName)
    with pytest.raises(pydantic.ValidationError):
        adapter.validate_python(name)


@pytest.mark.parametrize("name", SAMPLE_INVALID_PLATFORM_NAMES)
def test_validate_strict_app_platform_name_pydantic_error(name: str):
    adapter = pydantic.TypeAdapter(StrictAppPlatformName)
    with pytest.raises(pydantic.ValidationError):
        adapter.validate_python(name)
