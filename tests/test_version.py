"""
**File:** ``test_version.py``
**Region:** ``ds-event-stream-py-sdk``

Description
-----------
Smoke tests ensuring the package can be imported for coverage, and that
version and type information markers are exposed as expected.
"""

from __future__ import annotations

import importlib
import importlib.resources


def test_import_package_and_version_is_string() -> None:
    """
    Verify package import works and version is exposed.

    Returns:
        None.
    """

    pkg = importlib.import_module("ds_event_stream_py_sdk")

    assert isinstance(pkg.__version__, str)
    assert pkg.__version__ != ""


def test_py_typed_marker_is_packaged() -> None:
    """
    Verify ``py.typed`` exists to support PEP 561 typing.

    Returns:
        None.
    """

    marker = importlib.resources.files("ds_event_stream_py_sdk").joinpath("py.typed")
    assert marker.is_file()
