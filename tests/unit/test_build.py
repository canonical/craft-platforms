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
"""Unit tests for build functions."""

from unittest.mock import Mock, call

import exceptiongroup
import pytest
from craft_platforms import InvalidPlatformNameError, _build


def test_get_snapcraft_build_plan(monkeypatch):
    fake_build_plan = Mock()
    monkeypatch.setitem(_build._APP_SPECIFIC_PLANNERS, "snapcraft", fake_build_plan)

    project_data = {
        "base": "core22",
        "build-base": "core24",
        "platforms": {},
        "type": "base",
    }
    _build.get_build_plan(
        "snapcraft", project_data=project_data, strict_platform_names=True
    )

    assert fake_build_plan.mock_calls == [
        call(base="core22", build_base="core24", platforms={}, snap_type="base")
    ]


@pytest.mark.parametrize(
    ("platforms", "error"),
    [
        pytest.param(
            {";": None},
            InvalidPlatformNameError(
                message="Invalid platform name: ';'",
                details="Platform name contains invalid characters: [';']",
                resolution="Rename platform ';' to follow the naming rules.",
                doc_slug="platform-name-rules",
                reportable=False,
            ),
            id="single",
        ),
        pytest.param(
            {";": None, "_": None},
            exceptiongroup.ExceptionGroup(
                "Multiple errors while validating platform names",
                [
                    InvalidPlatformNameError(
                        message="Invalid platform name: ';'",
                        details="Platform name contains invalid characters: [';']",
                        resolution="Rename platform ';' to follow the naming rules.",
                        doc_slug="platform-name-rules",
                        reportable=False,
                    ),
                    InvalidPlatformNameError(
                        message="Invalid platform name: '_'",
                        details="Platform name contains invalid characters: ['_']",
                        resolution="Rename platform '_' to follow the naming rules.",
                        doc_slug="platform-name-rules",
                        reportable=False,
                    ),
                ],
            ),
            id="multiple",
        ),
    ],
)
def test_strict_platform_name_errors(platforms, error):
    project_data = {
        "base": "ubuntu@26.04",
        "build-base": "devel",
        "platforms": platforms,
    }
    with pytest.raises(type(error)) as exc_info:
        _build.get_build_plan(
            "mycraft",
            project_data=project_data,
            strict_platform_names=True,
        )

    if isinstance(exc_info.value, exceptiongroup.ExceptionGroup):
        assert exc_info.value.message == error.message
        assert exc_info.value.exceptions == error.exceptions
    else:
        assert exc_info.value == error
