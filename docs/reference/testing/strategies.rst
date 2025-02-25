.. py:module:: craft_platforms.test.strategies

Hypothesis strategies
=====================

Craft Platforms provides several :external+hypothesis:doc:`Hypothesis <index>`
strategies to assist with testing.

Distributions and series
------------------------

The primary strategy here is to generate :py:class:`~craft_platforms.DistroBase`
objects based on real Linux distributions:

.. autofunction:: real_distro_base

However, if you need to check that you can handle any realistic value, you can use:

.. autofunction:: any_distro_base

Specific distributions
~~~~~~~~~~~~~~~~~~~~~~

If you need to test against a specific distribution, the following strategies are
available:

.. autofunction:: debian_series

.. autofunction:: ubuntu_series

.. autofunction:: ubuntu_lts

``[<distro>@<series>:]<arch>`` strings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: distro_series_arch_str

Platforms
---------

There are several way to generate dictionaries of platforms. :py:func:`platforms`
is the most comprehensive, but the complexity of what it creates can cause it to be
quite slow. A faster way to do this is to generate a dictionary containing only a
single platform, which :py:func:`platform` does.

.. autofunction:: platforms

.. autofunction:: platform

If you only need to test the dictionaries created without handling shorthand,
:class:`~craft_platforms.PlatformDict` objects can be created with
:func:`platform_dict`.

.. autofunction:: platform_dict


Architectures
-------------

The strategy for getting :py:class:`~craft_platforms.DebianArchitecture` objects
is the normal strategy for getting any :external+python:class:`~enum.Enum` values:

.. code-block:: python

    from craft_platforms import DebianArchitecture
    from hypothesis import given, strategies

    @given(arch=strategies.sampled_from(DebianArchitecture))
    def test_architecture(arch: DebianArchitecture):
        assert isinstance(arch, DebianArchitecture)


However, this doesn't cover all the valid values that can be placed in ``build-on``
and ``build-for`` fields of a platform. For these, we provide these strategies:

.. autofunction:: build_on_str

.. autofunction:: build_for_str

.. autofunction:: build_for_arch_str
