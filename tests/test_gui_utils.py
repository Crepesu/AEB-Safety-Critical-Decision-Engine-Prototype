import pytest
from aeb.aeb_gui import choose_color, COLOR_OK, COLOR_WARN, COLOR_ERR, COLOR_NEUTRAL

@pytest.mark.parametrize(
    "value,expected",
    [
        (None, COLOR_NEUTRAL),
        (True, COLOR_OK),
        (False, COLOR_ERR),
        ("operational", COLOR_OK),
        ("monitor", COLOR_OK),
        ("warning", COLOR_WARN),
        ("emergency_braking", COLOR_ERR),
        ("sensor_failure", COLOR_ERR),
        ("unknown_state", COLOR_WARN),  # cautious default
    ]
)
def test_choose_color(value, expected):
    assert choose_color(value, COLOR_OK, COLOR_WARN, COLOR_ERR) == expected
