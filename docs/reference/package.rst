.. _package_reference:

Package reference
*****************

.. toctree::
   :maxdepth: 1

   charm
   rock
   snap
   errors
   platform_types
   validators


Architectures
-------------

.. autoclass:: craft_platforms.DebianArchitecture
    :members:

Build plans
-----------

.. autoclass:: craft_platforms.BuildInfo
    :members:

.. autofunction:: craft_platforms.get_platforms_build_plan

.. autofunction:: craft_platforms.get_build_plan

Distributions
-------------

.. autoclass:: craft_platforms.BaseName
    :members:

.. autoclass:: craft_platforms.DistroBase
    :members:

.. autofunction:: craft_platforms.is_ubuntu_like
