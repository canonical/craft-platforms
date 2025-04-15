*********
Changelog
*********

0.8.0 (2025-04-16)
------------------

Features
========

- Legacy rockcraft base strings ``ubuntu:20.04`` and ``ubuntu:22.04`` are supported.

0.7.1 (2025-04-10)
------------------

Bug Fixes
=========

- The ``bare`` base for Rockcraft was not properly handled. An error will now be raised
  if ``bare`` is specified with no ``build-base``.

0.7.0 (2025-04-02)
------------------

Features
========

- Add a module of :doc:`/reference/testing/strategies` to assist when testing code that
  uses craft-platforms.

Bug Fixes
=========

- Pass the correct type when obtaining a Snapcraft build plan.

0.6.0 (2025-02-11)
------------------

Features
========

- Improve presentation of invalid architecture error messages.
- Add a generic ``get_build_plan`` function that takes the application name and the
  basic project file dictionary and returns a build plan.

0.5.0 (2024-12-18)
------------------

Features
========

- Add multi-base support for charm build plans

0.4.0 (2024-10-17)
------------------

Bug Fixes
=========

- Correctly validate arguments for Snapcraft build plans.

Features
========

- Drop minimum required python version from 3.10 to 3.8.


0.3.1 (2024-Sep-26)
-------------------

Bug Fixes
=========

- Make series comparison less strict.
- Make Platform and PlatformDict public.

Documentation
=============

- Add basic reference documentation.

For a complete list of commits, check out the `0.3.1`_ release on GitHub.


0.3.0 (2024-Sep-09)
-------------------

Features
========

- Add 'build-for: [all]' support to generic build planner.
- Add support for Snapcraft build plans.

For a complete list of commits, check out the `0.3.0`_ release on GitHub.


0.2.0 (2024-Aug-29)
-------------------

Features
========

- Add support for Rockcraft build plans.

For a complete list of commits, check out the `0.2.0`_ release on GitHub.


0.1.1 (2024-Jul-24)
-------------------

Bug Fixes
=========

- Mark the ``craft_platform`` package as typed.

For a complete list of commits, check out the `0.1.1`_ release on GitHub.


0.1.0 (2024-Jul-01)
-------------------

New Features
============

- This initial release has support for Charmcraft build plans.

For a complete list of commits, check out the `0.1.0`_ release on GitHub.


.. _0.3.1: https://github.com/canonical/craft-platforms/releases/tag/0.3.1
.. _0.3.0: https://github.com/canonical/craft-platforms/releases/tag/0.3.0
.. _0.2.0: https://github.com/canonical/craft-platforms/releases/tag/0.2.0
.. _0.1.1: https://github.com/canonical/craft-platforms/releases/tag/0.1.1
.. _0.1.0: https://github.com/canonical/craft-platforms/releases/tag/0.1.0
