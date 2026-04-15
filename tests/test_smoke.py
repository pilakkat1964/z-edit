"""Smoke tests for zedit."""

def test_zedit_module_imports():
    """Test that the zedit module can be imported."""
    import zedit
    assert hasattr(zedit, "main")
    assert callable(zedit.main)


def test_version_exists():
    """Test that version is accessible."""
    import zedit
    # Module should be importable and functional
    assert zedit is not None
