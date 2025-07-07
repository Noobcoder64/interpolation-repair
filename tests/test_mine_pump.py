import re
from spectra_specification import SpectraSpecification
from counterstrategy import Counterstrategy, CounterstrategyState
import specification as sp
import LTL2Boolean as l2b
import mathsat_utils as msu
import interpolation


def test_mine_pump():

    spec = SpectraSpecification.from_file("tests/specifications/MinePumpTranslated.spectra")
    assert isinstance(spec, SpectraSpecification)
    assert spec.file_path == "tests/specifications/MinePumpTranslated.spectra"
    assert spec.name == "MinePump"
    assert spec.inputs == ["h", "m"]
    assert spec.outputs == ["p", "prev_p"]
    assert spec.assumptions == [
       "G (((prev_p & p) -> !(next(h))))"
    ]
    assert spec.guarantees == [
	    "G ((h -> next(p)))",
	    "G ((m -> !(next(p))))",
	    "(!(prev_p))",
	    "G ((next(prev_p) <-> p))",
    ]

    assert spec.is_y_sat() == True
    assert spec.is_satisfiable() == True
    assert spec.is_realizable() == False
    assert spec.is_well_separated() == True

    unreal_core = spec.compute_unrealizable_core()
    assert unreal_core == [
        "G ((h -> next(p)))",
	    "G ((m -> !(next(p))))",
    ]

    counterstrategy = spec.compute_counterstrategy()
    print("Counterstrategy:", counterstrategy)
    assert isinstance(counterstrategy, Counterstrategy)
    assert counterstrategy.num_states == 2
    sf0: CounterstrategyState = counterstrategy.states["Sf0"]
    assert sf0.name == "Sf0"
    assert sf0.is_initial == True
    assert sf0.is_dead == True
    assert sf0.inputs == {"h": True, "m": True}
    assert sf0.outputs == {"prev_p": False}
    assert sf0.influential_outputs == {}
    assert sf0.successors == ["Sf1"]
    sf1: CounterstrategyState = counterstrategy.states["Sf1"]
    assert sf1.name == "Sf1"
    assert sf1.is_initial == False
    assert sf1.is_dead == True
    assert sf1.inputs == {"h": False, "m": False}
    assert sf1.outputs == {}
    assert sf1.influential_outputs == {}
    assert sf1.successors == []

    path = counterstrategy.extract_random_path()
    print("Path:", path)
    assert str(path) == "Sf0_0 -> Sf1_1"
    path.unroll()
    print("Unrolled Path:", path)
    assert str(path) == "Sf0_0 -> Sf1_1"
    assert path.initial_state.id_state == "Sf0_0"
    assert path.initial_state.successor == "Sf1_1"
    assert path.transient_states[0].id_state == "Sf1_1"
    assert path.transient_states[0].successor == None
    assert path.unrolled_states == []
    assert path.is_loop == False
    assert not hasattr(path, "looping_states")

    assumptions = sp.unspectra(spec.assumptions)
    assert all("next" not in assumption for assumption in assumptions)
    assumptions = [re.sub(r"\s", "", line) for line in assumptions]
    assert all(not re.search(r"\s", line) for line in assumptions)

    guarantees = sp.unspectra(unreal_core)
    assert all("next" not in guarantee for guarantee in guarantees)
    guarantees = [re.sub(r"\s", "", line) for line in guarantees]
    assert all(not re.search(r"\s", line) for line in guarantees)

    assumptions_boolean = list(filter(None,[l2b.gr1LTL2Boolean(asm, path) for asm in assumptions]))
    print("Assumptions boolean:", "\n".join(assumptions_boolean))

    valuations_boolean = path.get_valuation()
    print("Valuations boolean:", valuations_boolean)

    if assumptions_boolean != []:
        assum_val_boolean = " & ".join(assumptions_boolean) + ((" & " + valuations_boolean) if valuations_boolean != "" else "")
    else:
        assum_val_boolean = valuations_boolean
        
    guarantees_boolean = list(filter(None,[l2b.gr1LTL2Boolean(gar, path) for gar in guarantees]))
    print("Guarantees boolean:", "\n".join(guarantees_boolean))

    interpolant = msu.compute_craig_interpolant(assum_val_boolean, " & ".join(guarantees_boolean), cleanup=False)
    print("Interpolant:", interpolant)
    assert interpolant == "m__Sf0_0 & h__Sf0_0" or interpolant == "h__Sf0_0 & m__Sf0_0"

    state_components = interpolation.extractStateComponents(interpolant)
    print("State components:", state_components)
    assert state_components == { "Sf0_0": "h & m" } or state_components == { "Sf0_0": "m & h" }

    refinements, non_io_separable = interpolation.getRefinementsFromStateComponents(state_components, path, ["h", "m"])
    print("Refinements:", refinements)
    print("Non-IO separable:", non_io_separable)

def test_mine_pump_ref_1():

    spec = SpectraSpecification.from_file("tests/specifications/MinePumpTranslated.spectra")

    refined_spec = SpectraSpecification(
        name=spec.name,
        inputs=spec.inputs,
        outputs=spec.outputs,
        assumptions=spec.assumptions + ['!(h & m)'],
        guarantees=spec.guarantees,
    )

    refined_spec.to_file("tests/specifications/MinePumpRef1.spectra")
    assert refined_spec.is_y_sat() == True
    assert refined_spec.is_satisfiable() == True
    assert refined_spec.is_realizable() == False
    assert refined_spec.is_well_separated() == True

def test_mine_pump_ref_2():

    spec = SpectraSpecification.from_file("tests/specifications/MinePumpTranslated.spectra")

    refined_spec = SpectraSpecification(
        name=spec.name,
        inputs=spec.inputs,
        outputs=spec.outputs,
        assumptions=spec.assumptions + ['G(!(h & m))'],
        guarantees=spec.guarantees,
    )

    refined_spec.to_file("tests/specifications/MinePumpRef2.spectra")
    assert refined_spec.is_y_sat() == True
    assert refined_spec.is_satisfiable() == True
    assert refined_spec.is_realizable() == True
    assert refined_spec.is_well_separated() == False