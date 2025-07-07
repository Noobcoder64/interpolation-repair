from spectra_specification import SpectraSpecification
from counterstrategy import Counterstrategy
import specification as sp
import re
import LTL2Boolean as l2b
import mathsat_utils as msu
from path import Path, State
import random
import interpolation

def test_lift_specification():
    print("\nTesting Lift Specification\n")

    spec = SpectraSpecification.from_file("tests/specifications/Lift_unreal.spectra")
    assert isinstance(spec, SpectraSpecification)
    assert spec.file_path == "tests/specifications/Lift_unreal.spectra"
    assert spec.name == "Lift"
    assert spec.inputs == ["b1", "b2", "b3"]
    assert spec.outputs == ["f1", "f2", "f3"]

    assert spec.is_realizable() == False
    assert spec.is_satisfiable() == True
    assert spec.is_y_sat() == True
    assert spec.is_well_separated() == True

    unreal_core = spec.compute_unrealizable_core()
    assert isinstance(unreal_core, list)
    assert len(unreal_core) == 4

    print("Unrealizable Core:", unreal_core)
    assert unreal_core == [
        "(f1 & !f2 & !f3)",
        "G (f1 -> next(f1 | f2))",
        "G (((f1 & next(f2)) | (f2 & next(f3)) | (f2 & next(f1)) | (f3 & next(f2))) -> (b1 | b2 | b3))",
        "GF (f2)",
    ]

    counterstrategy = spec.compute_counterstrategy(min_out_vars=True)
    assert isinstance(counterstrategy, Counterstrategy)
    assert counterstrategy.num_states == 1

    s0 = counterstrategy.states["S0"]
    assert s0.name == "S0"
    assert s0.is_initial == True
    assert s0.is_dead == False
    assert s0.inputs == {"b1": False, "b2": False, "b3": False}
    assert s0.outputs == {"f1": True, "f2": False}
    assert s0.influential_outputs == {}
    assert s0.successors == ["S0"]

    path = counterstrategy.extract_random_path()
    print("Path:", path)
    # assert str(path) == "S0 -> loop( -> Sl0)"
    path.unroll()
    print("Unrolled Path:", path)
    # assert str(path) == "S0 -> Sl0_1 -> loop( -> Sl0)"
    # assert path.initial_state.id_state == "S0"
    # assert path.initial_state.successor == "Sl0_1"
    # assert path.unrolled_states[0].id_state == "Sl0_1"
    # assert path.unrolled_states[0].successor == "Sl0"
    # assert path.looping_states[0].id_state == "Sl0"
    # assert path.looping_states[0].successor == "Sl0"

    {
    # s0 = State("S0")
    # s1 = State("S1")
    # s0.add_to_valuation("!b1")
    # s0.add_to_valuation("!b2")
    # s0.add_to_valuation("!b3")
    # s0.set_successor(s1.id_state)
    # s1.add_to_valuation("!b1")
    # s1.add_to_valuation("!b2")
    # s1.add_to_valuation("!b3")
    # s1.set_successor(s1.id_state)
    # path = Path(
    #     initial_state=s0,
    #     transient_states=[],
    #     looping_states=[s1],
    # )
    # path.unroll()
    # print("Unrolled Path:", path)
    # assert str(path) == "S0 -> S1_1 -> loop( -> S1)"
    # assert len(path.states) == 3
    # assert path.states["S0"].successor == "S1_1"
    # assert path.states["S1_1"].successor == "S1"
    # assert path.states["S1"].successor == "S1"
    }

    assumptions = sp.unspectra(spec.assumptions)
    assert all("next" not in assumption for assumption in assumptions)
    assumptions = [re.sub(r"\s", "", line) for line in assumptions]
    assert all(not re.search(r"\s", line) for line in assumptions)

    guarantees = sp.unspectra(unreal_core)
    assert all("next" not in guarantee for guarantee in guarantees)
    guarantees = [re.sub(r"\s", "", line) for line in guarantees]
    assert all(not re.search(r"\s", line) for line in guarantees)

    assumptions_boolean = list(filter(None,[l2b.gr1LTL2Boolean(asm, path) for asm in assumptions]))
    print("Assumptions boolean:\n", "\n".join(assumptions_boolean))

    valuations_boolean = path.get_valuation()

    print("Valuations:")
    print(valuations_boolean)

    if assumptions_boolean != []:
        assum_val_boolean = " & ".join(assumptions_boolean) + ((" & " + valuations_boolean) if valuations_boolean != "" else "")
    else:
        assum_val_boolean = valuations_boolean
        
    guarantees_boolean = list(filter(None,[l2b.gr1LTL2Boolean(gar, path) for gar in guarantees]))
    print("Guarantees boolean\n:", "\n".join(guarantees_boolean))

    interpolant = msu.compute_craig_interpolant(assum_val_boolean, " & ".join(guarantees_boolean), cleanup=False)
    print("Interpolant:", interpolant)

    # assert interpolant == ""

    state_components = interpolation.extractStateComponents(interpolant)
    print("State components:", state_components)

    # assert state_components == ""

    refinements, non_io_separable = interpolation.getRefinementsFromStateComponents(state_components, path, spec.inputs)
    print("Refinements:", refinements)

    expected_refinements = {
        '!(!b2 & !b3 & !b1)',
        'G((!b2 & !b3 & !b1) -> X(!(!b2 & !b3 & !b1)))',
        'G(!(!b2 & !b3 & !b1))',
        'G(F(!(!b2 & !b3 & !b1)))',
    }

    # assert set(refinements) == expected_refinements


def test_list_ref_1():

    spec = SpectraSpecification.from_file("tests/specifications/Lift_unreal.spectra")

    refined_spec = SpectraSpecification(
        name=spec.name,
        inputs=spec.inputs,
        outputs=spec.outputs,
        assumptions=spec.assumptions + ['!(!b2 & !b3 & !b1)'],
        guarantees=spec.guarantees,
    )

    refined_spec.to_file("tests/temp/Lift_unreal_ref_1.spectra")
    assert refined_spec.is_y_sat() == False
    assert refined_spec.is_realizable() == True
    assert refined_spec.is_satisfiable() == False
    assert refined_spec.is_well_separated() == True

def test_list_ref_2():

    spec = SpectraSpecification.from_file("tests/specifications/Lift_unreal.spectra")

    refined_spec = SpectraSpecification(
        name=spec.name,
        inputs=spec.inputs,
        outputs=spec.outputs,
        assumptions=spec.assumptions + ['G((!b2 & !b3 & !b1) -> next(!(!b2 & !b3 & !b1)))'],
        guarantees=spec.guarantees,
    )

    refined_spec.to_file("tests/temp/Lift_unreal_ref_2.spectra")
    assert refined_spec.is_y_sat() == True
    assert refined_spec.is_realizable() == True
    assert refined_spec.is_satisfiable() == True
    assert refined_spec.is_well_separated() == True

def test_list_ref_3():

    spec = SpectraSpecification.from_file("tests/specifications/Lift_unreal.spectra")

    refined_spec = SpectraSpecification(
        name=spec.name,
        inputs=spec.inputs,
        outputs=spec.outputs,
        assumptions=spec.assumptions + ['G(!(!b2 & !b3 & !b1))'],
        guarantees=spec.guarantees,
    )

    refined_spec.to_file("tests/temp/Lift_unreal_ref_3.spectra")
    assert refined_spec.is_y_sat() == False
    assert refined_spec.is_realizable() == True
    assert refined_spec.is_satisfiable() == False
    assert refined_spec.is_well_separated() == False

def test_list_ref_4():

    spec = SpectraSpecification.from_file("tests/specifications/Lift_unreal.spectra")

    refined_spec = SpectraSpecification(
        name=spec.name,
        inputs=spec.inputs,
        outputs=spec.outputs,
        assumptions=spec.assumptions + ['GF (!(!b2 & !b3 & !b1))'],
        guarantees=spec.guarantees,
    )

    refined_spec.to_file("tests/temp/Lift_unreal_ref_4.spectra")
    assert refined_spec.is_y_sat() == True
    assert refined_spec.is_realizable() == True
    assert refined_spec.is_satisfiable() == True
    assert refined_spec.is_well_separated() == True

