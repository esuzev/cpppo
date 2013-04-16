from __future__ import absolute_import
from __future__ import print_function

import logging
import os
import sys

from .dotdict import *

def test_dotdict():
    # Like dict, construct from mapping, iterable and/or keywords
    assert "a" in dotdict({"a":1})
    assert dotdict({"a":1})["a"] == 1

    assert "b" in dotdict({"a":1}, b=2)
    assert dotdict({"a":1}, b=2)["b"] == 2

    assert "c" in dotdict([("c",3)], d=4)
    assert dotdict([("c",3)], d=4)["c"] == 3

    assert "e" in dotdict(e=5)
    assert dotdict(e=5)["e"] == 5

    # Create hierarchies by assignment
    d = dotdict()
    d["a.b"] = 1
    assert d["a.b"] == 1
    assert d.a.b == 1		# attribute access =~= indexing
    d.a.b = 2
    assert d["a.b"] == 2
    assert d.a.b == 2

    # but only one layer at a time by attribute access
    try:
        d.x.y = 99
        assert False, "Shouldn't be able to create y in non-existent x!"
    except KeyError as e:
        assert "'x'" in str( e )

    # dicts already containing dotted keys are converted when assigned
    d2 = {"c.d": 2}
    d.a.b = d2
    assert d.a.b.c.d == 2

    assert "b.c.d" in d.a
    assert "b.c.x" not in d.a
    assert "e.f" not in d.a
    assert "a.b" in d     # Not a value, but is another layer of dotdict
    assert "a.b.x...b.c.d" in d
    assert "a.b.x....a.b.c.d" in d
    assert "a.b.x" not in d
    assert "a.b.c" in d

    assert isinstance( d.a.b.setdefault( 'c', "boo" ), dotdict )

    # Now, test paths containing back-tracking "a.b..c" ==> "a.c".  Of course,
    # this only works with indexing, not attribute access.  Leading '.' are OK
    # in indexes, consistent with 
    d.a.x = 3
    assert d["a.x"] == 3
    assert d[".a.x"] == 3
    assert d["a.b..x"] == 3
    assert d["a.b.c.d....x"] == 3
    # and back-tracking past root is OK (just like in filesystems)
    d["a...a.x"]
    d["a.b.c...x"]
    assert "a.....a.x" in d
    try:
        d["a.b.c...y"]
        assert False, "Should have failed trying to find y in root"
    except KeyError as e:
        assert "'y'" in str( e ) 

    # back-tracking doesn't confirm the validity of the ignored key elements:
    assert d["a.b.c.d.e.f....d"] == 2

    # key iteration
    assert list( sorted( k for k in d )) == ['a.b.c.d', 'a.x']

    # Make sure keys/items returns a list/iterator appropriate to Python version
    import types
    assert isinstance( d.keys(), list if sys.version_info.major < 3 else types.GeneratorType )
    assert isinstance( d.items(), list if sys.version_info.major < 3 else types.GeneratorType )


    # Test deletion, including refusing partial keys (unless empty)
    try:
        del d["a.b.c"]
    except KeyError as e:
        assert "(partial key)" in str( e ) 
    del d["a.b.c.d"]
    # key iteration (ignores empty key layers)
    assert list( sorted( k for k in d )) == ['a.x']
    del d["a.b.c"]
    assert list( sorted( k for k in d )) == ['a.x']
    # We can dig down using attribute access
    assert d.a.x == 3
    try:
        del d.a.x
    except AttributeError as e:
        assert "x" in str( e )
    del d.a["x"]
    assert list( sorted( k for k in d )) == []
    assert "a" in d
    assert "b" in d.a
    assert "c" not in d.a.b
    del d["a.b"]
    del d["a"]