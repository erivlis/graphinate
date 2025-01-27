import pytest

from graphinate.color import color_hex

colors = [
    ([0, 0, 0], "#000000"),
    ([0.5, 0.5, 0.5], "#7f7f7f"),
    ([1, 1, 1], "#010101"),
    ([2, 2, 2], "#020202"),
    ([50, 50, 50], "#323232"),
    ([100, 100, 100], "#646464"),
    ([128, 128, 128], "#808080"),
    ([255, 255, 255], "#ffffff"),
    ("Not a Sequence", "Not a Sequence")
]


@pytest.mark.parametrize(('color', 'expected_color_hex'), colors)
def test_color_hex(color, expected_color_hex):
    # act
    actual_color_hex = color_hex(color)

    # assert
    assert actual_color_hex == expected_color_hex


def test_color_hex_error():
    with pytest.raises(ValueError,
                       match="Input values should either be a float between 0 and 1 or an int between 0 and 255"):
        _ = color_hex(["a", "b", "c"])
