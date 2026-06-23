from wt.util import strip_indented_string


def test_strip_indented_string_no_prefix() -> None:
    """Should do nothing when there is no prefix"""

    result = strip_indented_string("code")
    assert result == "code"


def test_strip_indented_string_single_line() -> None:
    """Should strip the prefix from a single-line string"""

    result = strip_indented_string("         prefixed code")
    assert result == "prefixed code"


def test_strip_indented_string_multi_line() -> None:
    """Should strip the prefix from a multi-line string"""

    result = strip_indented_string("    prefixed\n    code")
    assert result == "prefixed\ncode"


def test_strip_indented_string_multiple_indent() -> None:
    """Should keep deeper indentation levels"""

    result = strip_indented_string("  def test():\n    print('hi')")
    assert result == "def test():\n  print('hi')"
