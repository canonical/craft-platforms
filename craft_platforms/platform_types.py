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
"""Platform types for use with Pydantic.

This module is only usable if pydantic is installed.
"""

import functools

from typing_extensions import Annotated

from craft_platforms.validators import validate_strict_platform_name

try:
    import pydantic
except ImportError:
    raise ImportError(
        "craft_platforms.platform_types requires pydantic to be installed."
    )


STRICT_PLATFORM_NAME_REGEX = r"^[^_/!#$%^&*(){}\[\]+?;'\",<>]*$"
"""A regular expression or use with text editors to warn of invalid platform names.

Because not all JSON schema validators fully implement the regular expression syntax
from ECMA 262, this expression is incomplete. It uses the recommended subset of regular
expressions from
https://json-schema.org/understanding-json-schema/reference/regular_expressions to
weed out many known bad values.
"""


StrictPlatformName = Annotated[
    str,
    pydantic.BeforeValidator(
        functools.partial(validate_strict_platform_name, allow_app_characters=False)
    ),
    pydantic.Field(
        description="The name of a platform.",
        examples=["amd64", "my-favourite-platform", "some-device"],
        pattern=STRICT_PLATFORM_NAME_REGEX,
    ),
]
"""The name of a platform.

``StrictPlatformName`` can be used to specify only user-entered platform names. This
is the strictest type of platform name and only useful if the app doesn't add any
platforms of its own.
"""


StrictAppPlatformName = Annotated[
    str,
    pydantic.Field(
        description="The name of a platform that could be inserted by an application.",
        examples=["amd64", "my-favourite-platform", "some-device"],
    ),
    pydantic.AfterValidator(validate_strict_platform_name),
]
"""The name of a platform, possibly app-provided.

``StrictAppPlatformName`` can be used to specify either user-entered or
application-provided platforms. Application-provided platforms should be prefixed with
the string ``<app_name>/``
"""
