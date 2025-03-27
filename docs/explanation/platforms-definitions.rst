.. py:module:: craft_platforms

Platforms definitions
=====================

In general, the most complex part of the data structures that can form a build
plan is the ``platforms`` definition. However, the general rules for developers
using ``craft-platforms`` are:

0. Each platform entry declares a single artifact (or artifact set), possibly with
   multiple ways to build it.
#. Each platform may only be built once per run.
#. The order of ``BuildInfo`` objects in the build plan is not meaningful for the
   selection process.
#. An error in a build does not necessitate trying a different ``BuildInfo`` for
   the same platform.
#. A consumer of the build plan may filter build plans using any rules not in
   conflict with the rules here.
#. It is an error if, after filtering, the build plan is empty.
#. If after filtering, multiple ``BuildInfo`` objects remain with the same
   ``platform``, any one of those may be used regardless of their order.
#. If a platform can be built under the rules above, it must be built unless further
   specified by the user.

Valid filtering rules
---------------------

While not an exhaustive list, the following rules are examples of valid rules that may
be used to filter the build plan:

- Only build on the current host architecture (use
  :meth:`DebianArchitecture.from_host`).
- Only build on the host's running distro and series.
- Only build for a specified architecture.
- Only build for a specified platform.
- Only build for build bases with the distribution ``"debian"``.
- Only build for build bases with the series ``"12"``.
- Only build on an arbitrary list of architectures.
- Do not cross-compile.

The last of these is not as straightforward as checking
``if info.build_on == info.build_for``, as the string ``"all"`` is a valid ``build_for``
value and should not be considered cross-compiling.

Selecting a ``BuildInfo``
-------------------------

In some cases, an application may be left with multiple ``BuildInfo`` objects that match
a single platform even after filtering above. Any of the following methods (as well as
many others) are valid for further filtering which ``BuildInfo`` to use:

- Randomly select a ``BuildInfo`` item.
- Prefer not to cross-compile (but allow it if no native builds are available).
- Prefer the newest build base.
- Prefer a specific architecture based on availability.
- Reject the build (failing the entire build)

Currently, the only known **invalid** way to proceed at this point is to ignore the
platform with duplicates, but continue the build.
