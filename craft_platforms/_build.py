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
"""General build planner for any app."""

from typing import Any, Callable, Dict, Iterable

from craft_platforms import charm, deb, rock, snap
from craft_platforms._buildinfo import BuildInfo
from craft_platforms._platforms import get_platforms_build_plan

_APP_SPECIFIC_PLANNERS: Dict[str, Callable[..., Iterable[BuildInfo]]] = {
    "charmcraft": charm.get_charm_build_plan,
    "debcraft": deb.get_deb_build_plan,
    "rockcraft": rock.get_rock_build_plan,
    "snapcraft": snap.get_platforms_snap_build_plan,
}


def get_build_plan(
    app: str,
    *,
    project_data: Dict[str, Any],
) -> Iterable[BuildInfo]:
    """Get a build plan for a given application.

    :param app: The name of the application (e.g. snapcraft, charmcraft, rockcraft)
    :param project_data: The raw dictionary of the project's YAML file. Normally this
        is what's output from ``yaml.safe_load()``.
    :returns: An iterable containing each possible BuildInfo for this file.

    This function is an abstraction layer over the general build planners, taking
    the application's name and its raw data and returning an exhaustive build plan
    for the given project for that application. This allows craft-platforms to be used
    in a forward-compatible manner as it adds more logic around selecting build
    planners or special behaviour for more apps.
    """
    planner = _APP_SPECIFIC_PLANNERS.get(app, get_platforms_build_plan)
    if app == "charmcraft":
        return planner(project_data)

    args = {
        "base": project_data.get("base"),
        "platforms": project_data.get("platforms"),
        "build_base": project_data.get("build-base"),
    }

    if app == "snapcraft":
        args["snap_type"] = project_data.get("type")

    return planner(**args)
