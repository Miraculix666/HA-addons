import pytest
from color import color_temperature_kelvin_to_mired

def test_color_temperature_kelvin_to_mired():
    # Standard values
    assert color_temperature_kelvin_to_mired(2000) == 500
    assert color_temperature_kelvin_to_mired(6500) == 153
    assert color_temperature_kelvin_to_mired(4000) == 250

    # Edge case float rounding
    assert color_temperature_kelvin_to_mired(2700.5) == 370

    # Test error handling
    with pytest.raises(ZeroDivisionError):
        color_temperature_kelvin_to_mired(0)
