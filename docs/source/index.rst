===============================================
Welcome to the Celeste/Omegagene Documentation!
===============================================

:Author: Kota Kasahara

------------------------------------
Documentation Structure
------------------------------------

The documention consists of the following three components:

.. toctree::
   :maxdepth: 1

   users-manual/index
   build-manual/index
   dev-manual/index

First-time users are advised to consult the :doc:`users-manual/index` first to learn how to get started with omegagene.

------------------------------------
About omegagene
------------------------------------

**"omegagene"** is the name of the molecular dynamics (MD) simulation software.
omegagene has several unique features, such as, the zero-multipole summation method and the virtual-system coupled multi-canonical MD method.

  The current version of omegagene can perform:

1. MD simulations on NVE ensemble
2. MD simulations on NVT ensemble (The velocity rescaling, or Hoover-Evans thermostat)
3. MD simulations on Multi-canonical ensemble, with the Virtual-system coupled McMD method.
4. Applying constraints with SHAKE algorithm
5. Calculations of electrostatic potentials based on the zero-dipole summation method.
6. Calculations of pairwise potentials on GPGPU (powered by CUDA 7.0, Computer Capability 3.5 is required).


------------------------------------
About |Celeste|
------------------------------------

|Celeste| is the code name for the collection of libraries that build omegagene


------------------------------------
Developers
------------------------------------

* KASAHARA Kota, Ritsumeikan Univ., Japan
* MA Benson, Univ. Illinois, US
* GOTO Kota, TITECH, Japan
* BHASKAR Dasgupta, Osaka Univ., Japan
* HIGO Junichi, Osaka Univ., Japan
* FUKUDA Ikuo, Osaka Univ., Japan
* MASHIMO Tadaaki, AIST, Japan
* AKIYAMA Yutaka, TITECH, Japan
* NAKAMURA Haruki, Osaka Univ., Japan



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`