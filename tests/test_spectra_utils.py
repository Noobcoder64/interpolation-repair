import pytest
import jpype
import spectra_utils as spectra
import time

def test_check_realizability():
    is_realizable = spectra.check_realizability("tests/specifications/Lift_unreal.spectra", timeout=10)
    assert is_realizable is False

@pytest.mark.skip(reason="Temporarily disabled")
def test_compute_counterstrategy_timeout_10s():
    try:
        spectra.compute_counterstrategy("tests/specifications/amba08_no_safety_0.spectra", min_sys_vars=True, timeout=10)
    except Exception as e:
        assert f"{type(e).__name__} - {e}" == "CounterstrategyTimeoutException - Counterstrategy computation timed out"

def test_assumptions_core():
    asm_core = spectra.compute_assumptions_core("tests/specifications/721295fd-bbe7-4805-be32-486a85932dcd.spectra")
    assert asm_core == [19, 21, 23, 27]
