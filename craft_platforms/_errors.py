# This file is part of craft-platforms.
#
# Copyright 2024 Canonical Ltd.
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
"""Error classes for craft-platforms."""

import dataclasses
import os
import typing

# Workaround for Windows...
EX_DATAERR = getattr(os, "EX_DATAERR", 65)


@typing.runtime_checkable
class CraftError(typing.Protocol):
    """A protocol for determining whether an object is a craft error."""

    args: typing.Collection[str]
    details: str | None
    resolution: str | None


@dataclasses.dataclass(kw_only=True)
class CraftPlatformsError(Exception):
    """Signal a program error with a lot of information to report."""

    message: str = dataclasses.field(kw_only=False)
    """The main message to the user about this error."""

    details: str | None = None
    """The full error details which originated the error situation."""

    resolution: str | None = None
    """An extra line indicating to the user how the error may be fixed or avoided (to be
      shown together with ``message``)."""

    docs_url: str | None = None
    """An URL to point the user to documentation (to be shown together with ``message``)."""

    doc_slug: str | None = None
    """The slug to the user documentation. Needs a base url to form a full address.
      Note that ``docs_url`` has preference if it is set."""

    logpath_report: bool = True
    """Whether the location of the log filepath should be presented in the screen as the
     final message."""

    reportable: bool = True
    """If an error report should be sent to some error-handling backend (like Sentry)."""

    retcode: int = 1
    """The code to return when the application finishes."""

    def __post_init__(self) -> None:
        super().__init__(self.message)
        if self.doc_slug and not self.doc_slug.startswith("/"):
            self.doc_slug = f"/{self.doc_slug}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CraftPlatformsError):
            return (
                self.message == other.message
                and self.details == other.details
                and self.resolution == other.resolution
                and self.docs_url == other.docs_url
                and self.logpath_report == other.logpath_report
                and self.reportable == other.reportable
                and self.retcode == other.retcode
                and self.doc_slug == other.doc_slug
            )
        if isinstance(other, CraftError) and isinstance(other, Exception):
            if (
                self.args != other.args
                or self.details != other.details
                or self.resolution != other.resolution
            ):
                return False
            for attr in (
                "message",
                "docs_url",
                "docs_slug",
                "logpath_report",
                "reportable",
                "retcode",
            ):
                if hasattr(other, attr) and getattr(other, attr) != getattr(self, attr):
                    return False
            return True
        return NotImplemented


class NeedBuildBaseError(CraftPlatformsError, ValueError):
    """Error when ``base`` requires a ``build_base``, but none is unspecified."""

    def __init__(self, base: str) -> None:
        super().__init__(
            message=f"base '{base}' requires a 'build-base', but none is specified",
            resolution="Specify a build-base.",
            retcode=EX_DATAERR,
        )


class InvalidPlatformNameError(CraftPlatformsError, ValueError):
    """Error when a specified platform name is not a Debian architecture."""

    def __init__(self, platform_name: str) -> None:
        self.platform_name = platform_name
        super().__init__(
            message=f"platform name {platform_name!r} is not a valid Debian architecture and needs 'build-on' and 'build-for' specified",
            resolution=f"Specify 'build-on' and 'build-for' values under the {platform_name!r} entry.",
        )


class InvalidPlatformError(CraftPlatformsError, ValueError):
    """Error when a specified platform is invalid."""

    def __init__(
        self,
        platform_name: str,
        *,
        details: str | None = None,
        resolution: str,
        docs_url: str | None = None,
        doc_slug: str | None = None,
    ) -> None:
        self.platform_name = platform_name
        super().__init__(
            message=f"platform {platform_name!r} is invalid",
            details=details,
            resolution=resolution,
            docs_url=docs_url,
            doc_slug=doc_slug,
        )


class InvalidBaseError(CraftPlatformsError, ValueError):
    """Error when a specified base name is invalid."""

    def __init__(
        self,
        base: str,
        *,
        message: str | None = None,
        resolution: str | None = None,
        docs_url: str | None = None,
        build_base: bool = False,
    ) -> None:
        self.base = base
        if resolution is None:
            resolution = "Ensure the base matches the <distro>@<series> pattern and is a supported series."
        if not message:
            message = (
                f"build-base '{base}' is unknown or invalid"
                if build_base
                else f"base '{base}' is unknown or invalid"
            )

        super().__init__(message=message, resolution=resolution, docs_url=docs_url)


class RequiresBaseError(CraftPlatformsError, ValueError):
    """Error when a base is required in this configuration."""
