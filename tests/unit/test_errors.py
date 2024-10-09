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
"""Unit tests for error classes."""

from typing import Optional

import pytest
from craft_platforms._errors import CraftPlatformsError

FULL_PLATFORMS_ERROR = CraftPlatformsError(
    message="message",
    details="details",
    resolution="resolution",
    docs_url="https://docs.canonical.com",
    doc_slug="sluggy-mc-slugface",
    logpath_report=False,
    reportable=False,
    retcode=-1,
)


class OtherCraftError(Exception):
    """An exception class that matches the CraftError protocol."""

    def __init__(
        self,
        message: str,
        details: Optional[str] = None,
        resolution: Optional[str] = None,
    ) -> None:
        self.details = details
        self.resolution = resolution
        super().__init__(message)


NON_MATCHING_ERROR = OtherCraftError("message", "details", "resolution")
NON_MATCHING_ERROR.docs_url = "no match"  # pyright: ignore[reportAttributeAccessIssue]


class NonError:
    """A non-exception class that matches the CraftError protocol."""

    def __init__(
        self,
        message: str,
        details: Optional[str] = None,
        resolution: Optional[str] = None,
    ) -> None:
        self.args = (message,)
        self.details = details
        self.resolution = resolution


@pytest.mark.parametrize(
    ("this", "that", "expected"),
    [
        (CraftPlatformsError("msg"), CraftPlatformsError("msg"), True),
        (CraftPlatformsError("msg"), OtherCraftError("msg"), True),
        (CraftPlatformsError("msg"), NonError("msg"), False),
        (CraftPlatformsError("msg"), Exception("msg"), False),
        (
            FULL_PLATFORMS_ERROR,
            CraftPlatformsError(
                message="other-message",
                details="details",
                resolution="resolution",
                docs_url="https://docs.canonical.com",
                doc_slug="sluggy-mc-slugface",
                logpath_report=False,
                reportable=False,
                retcode=-1,
            ),
            False,
        ),
        (
            FULL_PLATFORMS_ERROR,
            CraftPlatformsError(
                message="message",
                details="other-details",
                resolution="resolution",
                docs_url="https://docs.canonical.com",
                doc_slug="sluggy-mc-slugface",
                logpath_report=False,
                reportable=False,
                retcode=-1,
            ),
            False,
        ),
        (
            FULL_PLATFORMS_ERROR,
            CraftPlatformsError(
                message="message",
                details="details",
                resolution="other-resolution",
                docs_url="https://docs.canonical.com",
                doc_slug="sluggy-mc-slugface",
                logpath_report=False,
                reportable=False,
                retcode=-1,
            ),
            False,
        ),
        (
            FULL_PLATFORMS_ERROR,
            CraftPlatformsError(
                message="message",
                details="details",
                resolution="resolution",
                docs_url="https://other-docs.canonical.com",
                doc_slug="sluggy-mc-slugface",
                logpath_report=False,
                reportable=False,
                retcode=-1,
            ),
            False,
        ),
        (
            FULL_PLATFORMS_ERROR,
            CraftPlatformsError(
                message="message",
                details="details",
                resolution="resolution",
                docs_url="https://docs.canonical.com",
                doc_slug="other-slug",
                logpath_report=False,
                reportable=False,
                retcode=-1,
            ),
            False,
        ),
        (
            FULL_PLATFORMS_ERROR,
            CraftPlatformsError(
                message="message",
                details="details",
                resolution="resolution",
                docs_url="https://docs.canonical.com",
                doc_slug="sluggy-mc-slugface",
                logpath_report=True,  # Different
                reportable=False,
                retcode=-1,
            ),
            False,
        ),
        (
            FULL_PLATFORMS_ERROR,
            CraftPlatformsError(
                message="message",
                details="details",
                resolution="resolution",
                docs_url="https://docs.canonical.com",
                doc_slug="sluggy-mc-slugface",
                logpath_report=False,
                reportable=True,  # Different
                retcode=-1,
            ),
            False,
        ),
        (
            FULL_PLATFORMS_ERROR,
            CraftPlatformsError(
                message="message",
                details="details",
                resolution="resolution",
                docs_url="https://docs.canonical.com",
                doc_slug="sluggy-mc-slugface",
                logpath_report=False,
                reportable=False,
                retcode=-2,  # Different
            ),
            False,
        ),
        (
            FULL_PLATFORMS_ERROR,
            OtherCraftError("message", "details", "resolution"),
            True,
        ),
        (FULL_PLATFORMS_ERROR, OtherCraftError("nope", "details", "resolution"), False),
        (FULL_PLATFORMS_ERROR, OtherCraftError("message", "nope", "resolution"), False),
        (FULL_PLATFORMS_ERROR, OtherCraftError("message", "details", "nope"), False),
        (FULL_PLATFORMS_ERROR, NON_MATCHING_ERROR, False),
    ],
)
def test_platforms_error_equality(this, that, expected):
    assert (this == that) == expected
