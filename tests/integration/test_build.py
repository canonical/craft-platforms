# Copyright 2025 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License version 3, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Integration tests that test end-to-end build planning."""

import pathlib

import craft_platforms
import pytest
import yaml


@pytest.mark.parametrize(
    ("filename"),
    [
        path.name
        for path in (pathlib.Path(__file__).parent / "valid-projects").iterdir()
    ],
)
def test_valid_projects_succeed(filename: str) -> None:
    app_name = filename.partition("-")[0]
    with (pathlib.Path(__file__).parent / "valid-projects" / filename).open() as f:
        project_data = yaml.safe_load(f)

    build_plan = craft_platforms.get_build_plan(app=app_name, project_data=project_data)

    expected = project_data["_build_plan"]

    assert [repr(item) for item in build_plan] == expected
