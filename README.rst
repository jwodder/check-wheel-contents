.. image:: http://www.repostatus.org/badges/latest/wip.svg
    :target: http://www.repostatus.org/#wip
    :alt: Project Status: WIP — Initial development is in progress, but there
          has not yet been a stable, usable release suitable for the public.

.. image:: https://travis-ci.com/jwodder/check-wheel-contents.svg?branch=master
    :target: https://travis-ci.com/jwodder/check-wheel-contents

.. image:: https://codecov.io/gh/jwodder/check-wheel-contents/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jwodder/check-wheel-contents

.. image:: https://img.shields.io/github/license/jwodder/check-wheel-contents.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

.. image:: https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg
    :target: https://saythanks.io/to/jwodder

`GitHub <https://github.com/jwodder/check-wheel-contents>`_
| `Issues <https://github.com/jwodder/check-wheel-contents/issues>`_

.. contents::
    :backlinks: top

Getting the right files into your wheel is tricky, and sometimes we mess up and
publish a wheel containing ``__pycache__`` directories or ``tests/``.  Do we
have to manually check the contents of every wheel we build before uploading it
to PyPI?  How about letting this program check for you?  Just run
``check-wheel-contents`` on your wheel, and it'll fail and notify you if any of
several common errors & mistakes are detected.  The errors are described below,
along with common causes and corresponding fixes.

Installation
============
``check-wheel-contents`` requires Python 3.6 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install
``check-wheel-contents`` and its dependencies::

    python3 -m pip install git+https://github.com/jwodder/check-wheel-contents.git


Checks
======

**Note**: Unless otherwise stated, the common causes and their fixes listed
here are specific to projects developed using setuptools.  Users of other tools
like flit and poetry will have to consult those projects' documentation in
order to resolve failed checks.

**Note**: When rebuilding a wheel with setuptools, it is a good idea to delete
the ``build/`` directory first.  (This can be done in a single command with
``python setup.py clean --all bdist_wheel``.)  Not doing this can cause various
checks to continue to fail or new ones to start failing.


W001 — Wheel contains .pyc/.pyo files
-------------------------------------
This check fails if there are any files in the wheel with a ``.pyc`` or
``.pyo`` extension.  Such files are compiled Python bytecode files, and they do
not belong in wheels, because (a) they are platform-specific and thus useless
to many of your users, and (b) pip generates ``.pyc`` files for the ``.py``
files in your wheel automatically.

Common causes:

- You have ``include_package_data`` set to ``True``, your ``MANIFEST.in``
  contains ``graft packagename`` or ``recursive-include packagename *``, and
  the line ``global-exclude *.py[co]`` or similar is either missing from the
  ``MANIFEST.in`` or else in the wrong location.

  **Solution**: Ensure that ``global-exclude *.py[co]`` appears in your
  ``MANIFEST.in`` file *after* all ``include``, ``recursive-include``,
  ``global-include``, and ``graft`` commands.

- You have ``[install]optimize = 1`` set in ``setup.cfg`` (or, equivalently,
  ``options={"install": {"optimize": "1"}}`` set in ``setup.py``).

  **Solution**: Remove this setting.  It's only useful when using ``setup.py
  install`` anyway, which is deprecated.


W002 — Wheel contains duplicate files
-------------------------------------
This check fails if any two files in the wheel have the same contents.  Common
file contents, such files that are empty or just contain the line ``# -*-
coding: utf-8 -*-``, are excluded from this check.

Common causes:

- *(Build tool agnostic)* You copied a file or directory when you actually
  meant to rename it.

  **Solution**: Delete the original copy of the file or directory.

- You built a wheel, renamed a file or directory, and then built a wheel again
  without first deleting the ``build/`` directory.

  **Solution**: Delete the ``build/`` directory and build the wheel again.


W003 — Wheel contains non-module at library toplevel
----------------------------------------------------
This check fails if there are any files at the root of the purelib or platlib
section of the wheel that are not Python modules or ``.pth`` files.
Non-modules belong elsewhere in a wheel:

- Licenses and similar notices should be stored in the wheel's ``*.dist-info``
  directory using ``wheel``'s ``license_files`` option.

- Package data/resource files belong inside a package directory so that they
  can be located with ``pkg_resources`` or ``importlib-resources``.

- A project's ``README`` should already be used as the project's
  ``long_description``, in which case the text of the ``README`` is already
  included in the wheel inside the ``*.dist-info/METADATA`` file.


W004 — Module is not located at importable path
-----------------------------------------------
This check fails if there are any Python modules in the purelib or platlib
section of the wheel that cannot be imported due to one or more of their path
components being invalid Python identifiers.

Common causes:

- *(Build tool agnostic)* You gave a package directory or module a name
  containing a hyphen or other character not allowed in Python identifiers.

  **Solution**: Rename the offending directory or module to remove the
  offending character, most likely by changing it to an underscore.

- *(Build tool agnostic)* You gave a package directory or module the name of a
  Python keyword.

  **Solution**: Rename the offending directory or module.


W005 — Wheel contains common toplevel name in library
-----------------------------------------------------
This check fails if there are any files or directories named ``build``,
``data``, ``dist``, ``doc``,  ``docs``, ``example``, ``examples``, ``src``,
``test``, or ``tests`` located at the root of the purelib or platlib section of
the wheel.  These names are conventionally used for directories that don't
belong in wheels (aside from ``src``, whose contents belong in wheels but
itself does not belong in a wheel).  Projects should only use toplevel names
that resemble the project name; using common names will cause different
projects' files to overwrite each other on installation.

Common causes:

- For ``src``: You failed to set up your ``src/`` layout correctly.  ``src``
  should not contain an ``__init__.py`` file, ``where='src'`` needs to be
  passed to ``setuptools.find_packages()`` in ``setup.py``, and
  ``package_dir={"": "src"}`` needs to be passed to ``setup()`` in
  ``setup.py``.

- For directories other than ``src``: The directory contains an ``__init__.py``
  file, and the directory is not listed in the ``exclude`` argument to
  ``setuptools.find_packages()`` in ``setup.py``.

  **Solution**: Include ``'DIRNAME'`` and ``'DIRNAME.*'`` in the list passed to
  the ``exclude`` argument of ``find_packages()``.

- For directories other than ``src``: The directory is listed in the
  ``exclude`` argument to ``find_packages()``, but ``'DIRNAME.*'`` is not, and
  a subdirectory of the directory contains an ``__init__.py`` file.

  **Solution**: Include ``'DIRNAME.*'`` in the list passed to the ``exclude``
  argument of ``find_packages()``.

- You actually want to include your tests or examples in your wheel.

  **Solution**: Move the tests or whatever to inside your main package
  directory (e.g., move ``tests/`` to ``somepackage/tests/``) so that they
  won't collide with other projects' files on installation.


W006 — ``__init__.py`` at top level of library
----------------------------------------------
This check fails if there is a file named ``__init__.py`` at the root of the
purelib or platlib section of the wheel.  ``__init__.py`` files only belong
inside package directories, not at the root of an installation.

Common causes:

- You failed to set up your ``src/`` layout correctly.  ``src`` should not
  contain an ``__init__.py`` file, ``where='src'`` needs to be passed to
  ``setuptools.find_packages()`` in ``setup.py``, and ``package_dir={"":
  "src"}`` needs to be passed to ``setup()`` in ``setup.py``.

- You created an ``__init__.py`` file at the root of your project and set
  ``packages='.'`` in ``setup.py``.

  **Solution**: Configure your project's packages correctly.  For single-file
  modules, pass a list of their names (without the ``.py`` extension) to the
  ``py_modules`` argument to ``setup()``.  For package modules (directories),
  pass a list of their names and the dotted names of their descendant
  subpackages (possibly obtained by calling ``setuptools.find_packages()``) to
  ``packages``.


W007 — Wheel library is empty
-----------------------------
This check fails if the wheel contains no files in either its purelib or
platlib section.

Common causes:

- Your project consists of a single-file ``.py`` module, but you declared it to
  ``setup()`` in ``setup.py`` using the ``packages`` keyword.

  **Solution**: Single-file modules must be declared to ``setup()`` using the
  ``py_modules`` keyword.  Pass it a list of the names of your single-file
  modules without the ``.py`` extension.

- You are using ``setuptools.find_packages()`` to list your packages for
  ``setup()``, but your package does not contain an ``__init__.py`` file.

  **Solution**: Create an ``__init__.py`` file in your package.  If this is not
  an option because you are building a namespace package, use
  ``setuptools.find_namespace_packages()`` instead of ``find_packages()``.  Be
  sure to set the arguments appropriately so that the function only finds your
  main package; `see the documentation for further information
  <https://setuptools.readthedocs.io/en/latest/setuptools.html#find-namespace-packages>`_.

- You're deliberately creating a wheel that only contains scripts, headers, or
  other data files.

  **Solution**: Ignore this check.


W008 — Wheel is empty
---------------------
This check fails if the wheel contains no files other than the ``*.dist-info``
metadata directory.  It is a stronger check than W007, intended for users who
are creating wheels that only contain scripts, headers, and other data files
and thus need to ignore W007.

Common causes:

- Same causes as for W007

- You're deliberately creating an empty wheel whose only function is to cause a
  set of dependencies to be installed.

  **Solution**: Ignore this check.


W009 — Wheel contains multiple toplevel library entries
-------------------------------------------------------
This check fails if the wheel's purelib and platlib sections contain more than
one toplevel entry between them, excluding ``.pth`` files and files &
directories that begin with an underscore.  This is generally a sign that
something has gone wrong in packaging your project, as very few projects want
to distribute code with multiple top-level modules or packages.

Common causes:

- You built a wheel, renamed a toplevel file or directory, and then built a
  wheel again without first deleting the ``build/`` directory.

  **Solution**: Delete the ``build/`` directory and build the wheel again.

- You are using ``setuptools.find_packages()`` in your ``setup.py``, your
  project contains multiple directories with ``__init__.py`` files, and one or
  more of these directories (other than your main package) is not listed in the
  ``exclude`` argument to ``find_packages()``.

  **Solution**: Pass a list of all ``__init__.py``-having directories in your
  project other than your main package to the ``exclude`` argument of
  ``find_packages()``.  For proper exclusion, each directory ``DIRNAME`` should
  correspond to two elements of this list, ``'DIRNAME'`` and ``'DIRNAME.*'``,
  in order to ensure that the directory and all of its subdirectories are
  excluded.

- You are deliberately creating a wheel with multiple top-level Python modules
  or packages.

  **Solution**: [Not yet implemented]


W010 — Toplevel library directory contains no Python modules
------------------------------------------------------------
This check fails if a directory tree rooted at the root of the purelib or
platlib section of the wheel contains no Python modules.


..
    W101 — Wheel library contains files not in source tree
    W102 — Wheel library is missing files in source tree
    W201 — Wheel library is missing specified toplevel entry
    W202 — Wheel library has undeclared toplevel entry
