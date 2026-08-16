"""Shared fixtures for the backend test suite."""

from datetime import datetime

import pytest


@pytest.fixture
def reporter_rows():
    """Two reporter rows, oldest first: the original filer then one linker."""
    return [
        {"name": "Ada Lovelace", "oauth_id": "1001", "reported_at": datetime(2026, 8, 1)},
        {"name": "Alan Turing", "oauth_id": "1002", "reported_at": datetime(2026, 8, 2)},
    ]
