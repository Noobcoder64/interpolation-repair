from spectra_specification import SpectraSpecification
from counterstrategy import Counterstrategy

def test_from_file_lgs_unreal():

    spec = SpectraSpecification.from_file("tests/specifications/LGS_unreal.spectra")
    assert spec.name == "LGS"
    assert spec.inputs == ["handle_up", "handle_down"]
    assert spec.outputs == ["gear_extended"]
    assert spec.assumptions == []
    assert spec.guarantees == [
        "G(handle_down -> next(!handle_down | gear_extended))",
        "G(handle_up -> next(!handle_up | !gear_extended))"
    ]

    assert spec.is_realizable() == False
    assert spec.is_satisfiable() == True
    assert spec.is_y_sat() == True
    assert spec.is_well_separated() == True

    counterstrategy = spec.compute_counterstrategy(min_out_vars=False)
    assert isinstance(counterstrategy, Counterstrategy)
    assert counterstrategy.num_states == 3

    sf0 = counterstrategy.states["Sf0"]
    assert sf0.name == "Sf0"
    assert sf0.is_initial == True
    assert sf0.is_dead == True
    assert sf0.inputs == {"handle_up": True, "handle_down": True}
    assert sf0.outputs == {"gear_extended": False}
    assert sf0.successors == ["Sf2"]

    sf1 = counterstrategy.states["Sf1"]
    assert sf1.name == "Sf1"
    assert sf1.is_initial == True
    assert sf1.is_dead == True
    assert sf1.inputs == {"handle_up": True, "handle_down": True}
    assert sf1.outputs == {"gear_extended": True}
    assert sf1.successors == ["Sf2"]

    sf2 = counterstrategy.states["Sf2"]
    assert sf2.name == "Sf2"
    assert sf2.is_initial == False
    assert sf2.is_dead == True
    assert sf2.inputs == {"handle_up": True, "handle_down": True}
    assert sf2.outputs == {}
    assert sf2.successors == []


def test_spectra_specification_rg1():

    spec = SpectraSpecification.from_file("tests/specifications/RG_unreal.spectra")
    assert isinstance(spec, SpectraSpecification)
    assert spec.name == "RG"
    assert spec.inputs == ["req", "cl"]
    assert spec.outputs == ["gr", "val"]
    assert spec.assumptions == ["GF(!req)"]
    assert spec.guarantees == [
        "G(cl -> !val)",
        "GF(gr & val)",
    ]

    assert spec.is_realizable() == False
    
    counterstrategy = spec.compute_counterstrategy(min_out_vars=False)
    assert isinstance(counterstrategy, Counterstrategy)
    assert counterstrategy.num_states == 5

    s0 = counterstrategy.states["S0"]
    assert s0.name == "S0"
    assert s0.is_initial == True
    assert s0.is_dead == False
    assert s0.inputs == {"req": False, "cl": True}
    assert s0.outputs == {"gr": False, "val": False}
    assert s0.successors == ["S0", "Sf1", "S2", "Sf3"]

    sf1 = counterstrategy.states["Sf1"]
    assert sf1.name == "Sf1"
    assert sf1.is_initial == True
    assert sf1.is_dead == True
    assert sf1.inputs == {"req": False, "cl": True}
    assert sf1.outputs == {"gr": False, "val": True}
    assert sf1.successors == ["Sf4"]

    s2 = counterstrategy.states["S2"]
    assert s2.name == "S2"
    assert s2.is_initial == True
    assert s2.is_dead == False
    assert s2.inputs == {"req": False, "cl": True}
    assert s2.outputs == {"gr": True, "val": False}
    assert s2.successors == ["S0", "Sf1", "S2", "Sf3"]

    sf3 = counterstrategy.states["Sf3"]
    assert sf3.name == "Sf3"
    assert sf3.is_initial == True
    assert sf3.is_dead == True
    assert sf3.inputs == {"req": False, "cl": True}
    assert sf3.outputs == {"gr": True, "val": True}
    assert sf3.successors == ["Sf4"]

    sf4 = counterstrategy.states["Sf4"]
    assert sf4.name == "Sf4"
    assert sf4.is_initial == False
    assert sf4.is_dead == True
    assert sf4.inputs == {"req": False, "cl": False}
    assert sf4.outputs == {}
    assert sf4.successors == []

def test_gr1_strictness():
    spec = SpectraSpecification.from_file("tests/specifications/Strict.spectra")
    # Spectra uses strict GR(1) semantics.
    assert spec.is_realizable() == False

def test_lift_copy():

    original_spec = SpectraSpecification.from_file("tests/specifications/Lift_unreal.spectra")

    copied_spec = original_spec.copy()

    assert copied_spec is not original_spec
    assert copied_spec.file_path == None
    assert copied_spec.name == original_spec.name
    assert copied_spec.inputs == original_spec.inputs
    assert copied_spec.outputs == original_spec.outputs
    assert copied_spec.assumptions == original_spec.assumptions
    assert copied_spec.guarantees == original_spec.guarantees

def test_rg_assumptions_core():
    spec = SpectraSpecification.from_file("tests/specifications/RG_repair_core.spectra")
    assert spec.is_y_sat() == True
    assert spec.is_realizable() == True
    assert spec.is_satisfiable() == True
    assert spec.is_well_separated() == True

    assumptions_core = spec.compute_assumptions_core()
    assert isinstance(assumptions_core, list)
    assert len(assumptions_core) == 1
    assert assumptions_core == ["alwEv (!cl)"]
