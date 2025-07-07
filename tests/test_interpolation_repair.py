
from interpolation_repair import counterstrategy_guided_refinement
from spectra_specification import SpectraSpecification
import pytest

def test_lift_interpolation_repair():

    initial_spec = SpectraSpecification.from_file("tests/specifications/Lift_unreal.spectra")
    output_dir = "outputs"
    timeout = 10  # seconds
    repair_limit = 5  # number of repairs
    temp_dir = "temp"

    # Run the counterstrategy guided refinement
    solutions = counterstrategy_guided_refinement(
        initial_spec=initial_spec,
        output_dir=output_dir,
        timeout=timeout,
        repair_limit=repair_limit,
        temp_dir=temp_dir,
    )

    # Check if the solutions are returned correctly
    # assert isinstance(solutions, list)
    # assert len(solutions) <= repair_limit

@pytest.mark.skip(reason="Temporarily disabled")
def test_pcar_interpolation_repair():

    initial_spec = SpectraSpecification.from_file("specifications/SYNTECH15-UNREAL/PCarLTL_Unrealizable_V_2_unrealizable0_888_PCar_fixed_unrealizable.spectra")
    output_dir = "outputs"
    timeout = 10  # seconds
    repair_limit = 5  # number of repairs

    # Run the counterstrategy guided refinement
    solutions = counterstrategy_guided_refinement(
        initial_spec=initial_spec,
        output_dir=output_dir,
        timeout=timeout,
        repair_limit=repair_limit
    )

    # Check if the solutions are returned correctly
    assert isinstance(solutions, list)
    assert len(solutions) <= repair_limit


# test timeout


# test repair limit
