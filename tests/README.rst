Tests for OpenLP
================

This directory contains unit tests for OpenLP. The ``functional`` directory contains functional unit tests.

Prerequisites
-------------

In order to run the unit tests, you will need the following Python packages/libraries installed:

 - pytest
 - pytestqt
 - flake8

On Ubuntu you can simple install the python3-pytest and flake8 packages.
Most other distributions will also have these packages.
On Windows and Mac OS X you will need to use ``pip`` to install these packages.

Running the Tests
-----------------

To run the tests, navigate to the root directory of the OpenLP project, and then run the following command::

    pytest -v tests

