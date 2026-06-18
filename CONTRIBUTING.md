# Contributing

Craft Platforms welcomes contributions from around the world.

Before contributing, review the [Ubuntu Code of Conduct](https://ubuntu.com/community/ethos/code-of-conduct) and the [Canonical contributor licence agreement](http://www.ubuntu.com/legal/contributors).

## Report issues

Search the [issue tracker](https://github.com/canonical/craft-platforms/issues) before opening a new issue. If you do not find an existing report, open one with enough context to describe the problem or request clearly.

## Set up development

Use a fork-and-branch workflow for local development:

```bash
git clone https://github.com/<your-user>/craft-platforms --recurse-submodules
cd craft-platforms
git remote add upstream https://github.com/canonical/craft-platforms
git fetch upstream
make setup
```

Use the SSH remote form if you already use SSH with GitHub.

## Make changes

Keep changes small and focused. For code changes, run:

```bash
make format
make lint
make test-fast
```

Run `make docs` for documentation changes.

Commit messages should follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

## Open a pull request

Use the PR template and include a summary of the change, the tests you ran, and any documentation updates. See [HACKING.rst](HACKING.rst) for more detailed project guidance.
