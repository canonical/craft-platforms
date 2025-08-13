# Craft Platforms

[![QA](https://github.com/canonical/craft-platforms/actions/workflows/qa.yaml/badge.svg)](https://github.com/canonical/craft-platforms/actions/workflows/qa.yaml)
[![ReadTheDocs badge](https://readthedocs.com/projects/canonical-craft-platforms/badge/?version=latest)](https://canonical-craft-platforms.readthedocs-hosted.com)
[![PyPI - Version](https://img.shields.io/pypi/v/craft-platforms)](https://pypi.org/project/craft-platforms)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Security scan](https://github.com/canonical/craft-platforms/actions/workflows/security-scan.yaml/badge.svg)](https://github.com/canonical/craft-platforms/actions/workflows/security-scan.yaml)

**Craft Platforms** is a library that handles platform information for Snapcraft,
Charmcraft, Rockcraft, and other craft apps. A platform in this sense is the combination
of an operating system version and its target architecture.

The library's primary function is to parse information in a craft project file, such as
`snapcraft.yaml`, and creates a build plan from it. The plan is a manifest for
environments, describing those where the artifact can build and run.

This library is most useful for developers who build apps with the [Craft
Application](https://canonical-craft-application.readthedocs-hosted.com) library.

## Basic usage

Craft Platforms creates exhaustive build plans for any craft-like data structure,
taking into account differences between applications.

```terminal
>>> import craft_platforms
>>> craft_platforms.get_build_plan(
...     "mycraft",
...     project_data={"base": "debian@14", "platforms": {"riscv64": None}}
... )
[BuildInfo(platform='riscv64', build_on='riscv64', build_for='riscv64', build_base=DistroBase(distribution='debian', series='14'))]
```

## Installation

Craft Platforms is a pure Python library that runs on Python 3.8 or later. It can be
installed from [PyPI](https://pypi.org/project/craft-platforms)

## Documentation

The [Craft Platforms documentation](https://canonical-craft-platforms.readthedocs-hosted.com) contains reference information for the library.

## Community and support

You can report any issues or bugs on the project's [GitHub
repository](https://github.com/canonical/craft-platforms/issues).

Craft Platforms is covered by the [Ubuntu Code of
Conduct](https://ubuntu.com/community/ethos/code-of-conduct).

## Contribute to Craft Platforms

Craft Platforms is open source and part of the Canonical family. We would love your help.

If you're interested, start with the [contribution guide](HACKING.rst).

We welcome any suggestions and help with the docs. The [Canonical Open Documentation
Academy](https://github.com/canonical/open-documentation-academy) is the hub for doc
development, including Craft Platforms docs. No prior coding experience is required.

## License and copyright

Craft Platforms is released under the [LGPL-3.0 license](LICENSE).

© 2023-2025 Canonical Ltd.
