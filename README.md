# Craft Platforms

[![QA](https://github.com/canonical/craft-platforms/actions/workflows/qa.yaml/badge.svg)](https://github.com/canonical/craft-platforms/actions/workflows/qa.yaml)
[![Security scan](https://github.com/canonical/craft-platforms/actions/workflows/security-scan.yaml/badge.svg)](https://github.com/canonical/craft-platforms/actions/workflows/security-scan.yaml)
[![Documentation](https://github.com/canonical/craft-platforms/actions/workflows/docs.yaml/badge.svg)](https://github.com/canonical/craft-platforms/actions/workflows/docs.yaml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPI - Version](https://img.shields.io/pypi/v/craft-platforms)](https://pypi.org/project/craft-platforms)
[![ReadTheDocs badge](https://readthedocs.com/projects/canonical-craft-platforms/badge/?version=latest)](https://canonical-craft-platforms.readthedocs-hosted.com)

Utilities for handling platform information for Snapcraft, Charmcraft, Rockcraft, and
other craft tools based on [Craft Application](https://canonical-craft-application.readthedocs-hosted.com).

Craft Platforms parses information defined in a craft recipe file such as a
`snapcraft.yaml` file and creates a build plan. A build plan describes the
environments where the application can build artifacts and the environments
where the artifacts can run.

## Basic usage

Craft Platforms creates exhaustive build plans for any craft-like data structure,
taking into account differences per application.

```terminal
>>> import craft_platforms
>>> craft_platforms.get_build_plan(
...     "mycraft",
...     project_data={"base": "debian@14", "platforms": {"riscv64": None}}
... )
[BuildInfo(platform='riscv64', build_on='riscv64', build_for='riscv64', build_base=DistroBase(distribution='debian', series='14'))]
```

## Installation

Craft Platforms is a pure-python library that runs on Python 3.8 or later. It can be
installed from [PyPI](https://pypi.org/project/craft-platforms)

## Documentation

The documentation is available [on ReadTheDocs](https://canonical-craft-platforms.readthedocs-hosted.com)

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
