Filter a build plan
===================

A craft-platforms consumer should attempt to build exactly one artifact for as many
platforms as are feasible. To do this, the build plan must be filtered. In general, a
set of steps for filtering a build plan are:

1. Remove un-buildable ``BuildInfo`` objects.
2. For each remaining platform, select one ``BuildInfo``.

Consider the following ``platforms`` definition for a nonexistent ``fakecraft``:

.. code-block:: yaml

    platforms:
      laptop:
        build-on:
          - ubuntu@24.04:amd64
          - ubuntu@24.04:riscv64
          - debian@12:i386
          - ubuntu@4.10:riscv64
        build-for: [ubuntu@24.04:amd64]
      nostalgia:
        build-on: [windows@5.0:i386]
        build-for: [windows@5.0:i386]
      phone:
        build-on:
          - ubuntu@22.04:s390x
          - ubuntu@24.04:riscv64
        build-for: [ubuntu@24.04:arm64]
      jpeg:
        build-on:
          - debian@12:i386
          - ubuntu@24.04:amd64
          - sunos@4:i386
        build-for: [all@all:all]

Each key under ``platforms`` can be considered a desired artifact with one or more possible
ways to build it. For example, the ``nostalgia`` platform has only a single

Modern build infrastructure such as Launchpad or Open Build Service
is unlikely to have any builders that can build the ``nostalgia`` platform, as Windows 2000
left extended support over a decade ago. Likewise, the ``jpeg`` platform is not likely to
find any takers to build on ``sunos@4:i386``. Other ``BuildItem`` objects may be removed by
availability of hardware or operating systems. If a build system has access to any Ubuntu
version on any hardware (even the rare ``ubuntu@4.10:riscv64``), it could filter the build
plan as follows:

.. literalinclude:: filter_build_plans.py
    :start-at: def filter_build_plan(
    :end-before: # :docs:end_filter

This would result in the following filtered build plan:

.. literalinclude:: filter_build_plans.py
    :start-at: ubuntu_only_build_plan = [
    :end-before: # :docs:end_filtered_build_plan

This still results in three options for the ``laptop`` platform and two for ``phone``.
A build plan should not be considered ordered. The order does not state a user preference
and can change. Rather, at this point the builder may choose one of each at its preference.
For example, a builder with excess RISC-V infrastructure and a preference for the oldest
build base may result in this final build plan:

.. literalinclude:: filter_build_plans.py
    :start-at: oldest_with_riscv_preference = [
    :end-before: # :docs:end_oldest_with_riscv_preference

A builder which does not do cross-compilation may not be able to build for the ``phone``
platform at all:

.. literalinclude:: filter_build_plans.py
    :start-at: native_only_prefer_amd64 = [
    :end-before: # :docs:end_native_only_prefer_amd64

Build plans that result in errors
---------------------------------

craft-platforms will always create an **exhaustive build plan**, but not all build plans
result in something buildable. If, after filtering for builds it is capable of running,
a craft-platforms consumer is left with an empty build plan, it is the consumer's
responsibility to gracefully exit with an error. The following definition could result in a
valid ``fakecraft`` build plan, but would create an error in any known environment:

.. code-block:: yaml

    platforms:
      you-shall-not-build:
        build-on:
          - debian@3.0:riscv64  # Nobody has one of these!
        build-for: [all@all:all]

Whether a build plan where some, but not all, platforms can be built is considered
erroneous is undefined and may be decided by the consumer.
