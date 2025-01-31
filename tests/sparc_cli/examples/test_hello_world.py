import pytest
from sparc_cli.examples.hello_world import hello

def test_hello():
    """Test that hello() returns the expected greeting string."""
    assert hello() == "Hello, World!"
