Largefile
=========

.. image:: https://api.travis-ci.org/grantjenks/largefile.svg
    :target: http://TODO

Largefile is an Apache2 licensed library for working with large files inspired
by GNU Coreutils and functional programming.

GNU Coreutils are great, until:

* You're stuck with outdated versions.
* You can't remember the switches and syntax for sed/grep/awk.
* You forget the LC_ALL=C trick.
* You want to hack on the tools without diving into C and recompiling.
* You need the functionality of a complete programming language.

Python has great utilities for file i/o but they're a bit hodge-podge. Largefile
combines and surfaces these utilities in an easy way.

::

    >>> import largefile as lf
    >>> f = lf.Largefile('temp.txt')
    >>> f.linecount()
    123456789
    >>> f.shuffle()
    >>> f.sort()
    >>> f.head()
    TODO
    >>> f.sample()
    TODO

Largefile strives to be a fast and feature-full tool for file
processing. It's easy to hack-on and improve yourself.

Features
--------

- Pure-Python
- Fully documented
- 100% test coverage
- Performance matters
- Tested on Python 2.6, 2.7, 3.2, 3.3, and 3.4

Quickstart
----------

Installing Largefile is simple with
`pip <http://www.pip-installer.org/>`_::

    > pip install largefile

You can access documentation in the interpreter with Python's built-in help
function:

::

    >>> import largefile as lf
    >>> help(lf)

Documentation
-------------

Complete documentation including performance comparisons is available at
http://TODO .

Contribute
----------

Collaborators are welcome!

#. Check for open issues or open a fresh issue to start a discussion around a
   bug.  There is a (TODO) Contributor Friendly tag for issues that should be
   used by people who are not very familiar with the codebase yet.
#. Fork `the repository <https://github.com/grantjenks/largefile>`_ on GitHub
   and start making your changes to a new branch.
#. Write a test which shows that the bug was fixed.
#. Send a pull request and bug the maintainer until it gets merged and
   published. :)

Useful Links
------------

- `Largefile Project @ GrantJenks.com`_
- `Largefile Module @ PyPI`_
- `Largefile Source @ Github`_
- `Issue Tracker`_

.. _`Largefile Project @ GrantJenks.com`: http://TODO
.. _`Largefile Module @ PyPI`: https://pypi.python.org/pypi/largefile
.. _`Largefile @ Github`: https://github.com/grantjenks/largefile
.. _`Issue Tracker`: https://github.com/grantjenks/largefile/issues

Largefile License
-----------------

Copyright 2014 Grant Jenks

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
