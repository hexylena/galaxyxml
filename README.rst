Galaxy XML Generation Libraries |Build Status| |PyPI|
=====================================================

These libraries will support building of Tool XML and Tool Dependencies
XML. We'd be happy to support any other XML that Galaxy supports, just
make an issue or PR if you're feeling motivated.

Known Bugs
----------

-  no validation of unique names
-  repeats aren't named properly
-  conditional/whens aren't named properly
-  conditionals not handled in CLI

License
-------

-  Apache License, v2

Changelog
---------

-  0.4.12

   - Correct the ordering of elements for planemo (thanks @fubar2)
   - Properly read stdio on loading tools (thanks @fubar2)

-  0.4.11

   - Update to command line override (thanks @fubar2)

-  0.4.10

   - Allow overriding of command line in support of positional args (thanks @fubar2)

-  0.4.9

   - Fix quoting of text params (thanks @fubar2!)

-  0.4.8

   - Fix travis deploy process
   - Fix testing
   - py36 only

-  0.4.6

   -  Deprecate py2
   -  Wrap version command in CDATA

-  0.4.5

   -  Bug fixes:

      -  Write catched error to logger instead of STDOUT
      -  Fix Travis: install ``xmllint``
      -  Fix Travis: Deal with new ``flake8`` restrictions for
         exceptions

-  0.4.3

   -  Bug fixes:

      -  Allow ``<discover_dataset>`` within ``<data>`` in ``<outputs>``
      -  Allow import of existing XML with no description

-  0.4.2

   -  Add methods to check presence of EDAM and citations (thanks @khillion)

-  0.4.0

   -  Add feature to import existing Galaxy xml

-  0.3.3

   -  @khillion implemented the
      following:

      -  ``<options>`` with ``<filter>`` and ``<column>``
      -  ``<container>`` for ``<requirements>``
      -  Started to add ``<tests>`` section
      -  ``<section>`` in ``<inputs>``
      -  ``<collection>`` with ``<discover_datasets>`` in ``<outputs>``

   -  Please note that ``tool.parameters.OutputParam()`` has been
      changed to ``tool.parameters.OutputData()``

-  0.3.2

   -  configfiles
      (`#8 <https://github.com/hexylena/galaxyxml/pull/8>`__)

-  0.3.0

   -  Travis auto-deploys on new tags
   -  Testing
   -  p3k

-  0.2.3

   -  First widely used/stable version

.. |Build Status| image:: https://travis-ci.org/hexylena/galaxyxml.svg?branch=master
   :target: https://travis-ci.org/hexylena/galaxyxml
.. |PyPI| image:: https://img.shields.io/pypi/v/galaxyxml.svg
   :target: https://pypi.python.org/pypi/galaxyxml/
