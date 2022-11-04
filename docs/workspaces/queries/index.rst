.. _Queries:

Queries
-------

Steamship contains a query language, **ShipQL**, designed to help you fetch Files, Blocks, and Tags.
ShipQL enables you to query the results of multiple AI models applied to the same text, to find files or sections identified by language AI features.

ShipQL Version 1 supports only the criteria on which objects are matched (like a SQL WHERE clause).
It does not yet support projection and selection (like the SQL SELECT clause).

Usage
~~~~~

File, Block, and Tag objects are all queryable via ShipQL.
Their objects in the Python Client have a static ``query`` method which accepts a ShipQL string.

The object type returned from that query method depends upon the object you used to call it.
However the ShipQL predicates always refer to ``Tags``.

For example: executing the query ``name "Dave"`` on the ``Block.query`` endpoint will return ``Blocks`` which have ``Tags`` which have ``name="Dave"``.

Language Description
~~~~~~~~~~~~~~~~~~~~

Unary Predicates
^^^^^^^^^^^^^^^^

These predicates filter unary properties of tags.

- ``blocktag`` - The tag is on a block
- ``filetag`` - The tag is on a file

Binary Predicates
^^^^^^^^^^^^^^^^^

These predicates filter valued properties of tags.

- ``kind "string"`` - The kind of the tag. Only equality is supported. Ex: ``kind "ner"``
- ``name "string"`` - The name of the tag. Only equality is supported. Ex: ``name "Dave"``
- ``file_id "uuid string"`` - The UUID of the file to which the tag belongs.
- ``block_id "uuid string"`` - The UUID of the block to which the tag belongs.
- ``value("pathString") <op> <comparisonValue>`` - Comparison on the value (JSON content) of the tag.  Path string is a dot-separated key path in the json content.
  Comparison value is a string, numeric, or boolean literal (lowercase).  Op can be:

  - ``=`` - Equals. Ex: ``value("approved") = true``
  - ``>=`` - Greater than or equal to. Ex: ``value("confidence") >= 0.5``
  - ``>`` - Greater than.  Ex: ``value("confidence") > 0.5``
  - ``<=`` - Less than or equal to.  Ex: ``value("confidence") <= 0.5``
  - ``<`` - Less than.  Ex: ``value("confidence") < 0.5``
  - ``exists`` - Exists (no comparison value required).  Ex: ``value("active") exists``

Binary Relations
^^^^^^^^^^^^^^^^

Binary relations allow filtering on the relationship of a tag to another tag.
All relations require the 2nd matching tag to be distinct from the first.

Using them in the query language creates the context for a second tag, which may have additional predicates and relations.
Ex: ``kind "foo2" and overlaps { kind "bar2"}`` means there exists a tag of kind "foo2" which overlaps a second tag of kind "bar2".

- ``overlaps`` - The spans of the two tags overlap, and they are in the same block.
- ``samespan`` - The spans of the two tags match exactly, and they are in the same block.
- ``sameblock`` - The two tags appear in the same block.
- ``samefile`` - The two tags appear in the same file.

Conjunctions
^^^^^^^^^^^^

Conjunctions allow combinations of predicates and relations.
There is no order of operations between conjunctions;
groups of unlike conjunctions must be separated with parentheses,
ex: ``blocktag and (kind "foo3" or name "Tag6")``

- ``and``- Multiple predicates or relations can be intersected with and.
- ``or`` - Multiple predicates or relations may be disjoined with or.

Special Predicates
^^^^^^^^^^^^^^^^^^

- ``all`` - All may appear only at the top level of the query and must be the entire query.
  It means to return all ``Files``, ``Blocks``, or ``Tags``.

