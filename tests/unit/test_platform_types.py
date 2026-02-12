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
"""Unit tests for platform types."""

import jsonschema
import pydantic
import pytest
import regex
from craft_platforms.platform_types import (
    STRICT_PLATFORM_NAME_REGEX,
    StrictPlatformName,
)
from typing_extensions import Annotated

from tests.unit.test_validators import (
    SAMPLE_INVALID_PLATFORM_NAMES,
    SAMPLE_VALID_APP_ONLY_PLATFORM_NAMES,
    SAMPLE_VALID_PLATFORM_NAMES,
)

RegexPlatformName = Annotated[str, pydantic.Field(pattern=STRICT_PLATFORM_NAME_REGEX)]


class RootPlatformName(pydantic.RootModel):
    root: StrictPlatformName


@pytest.mark.parametrize("name", SAMPLE_VALID_PLATFORM_NAMES)
def test_strict_platform_name_regex_success(name: str):
    assert regex.match(STRICT_PLATFORM_NAME_REGEX, name)

    RootPlatformName.model_validate(name)


@pytest.mark.parametrize(
    "name", SAMPLE_INVALID_PLATFORM_NAMES + SAMPLE_VALID_APP_ONLY_PLATFORM_NAMES
)
def test_strict_platform_name_regex_error(name: str):
    assert not regex.match(STRICT_PLATFORM_NAME_REGEX, name)

    with pytest.raises(pydantic.ValidationError, match="Invalid platform name"):
        RootPlatformName.model_validate(name)


@pytest.mark.parametrize("name", SAMPLE_VALID_PLATFORM_NAMES)
def test_json_schema_validate_success(name: str):
    jsonschema.validate(name, RootPlatformName.model_json_schema())
