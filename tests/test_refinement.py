import re
import pytest
from spectra_specification import SpectraSpecification
from refinement import RefinementNode


def test_lift_minimise_spec():
    
    initial_spec = SpectraSpecification.from_file("tests/specifications/Lift_unreal.spectra")

    spec = initial_spec.copy()
    spec.to_file("tests/temp/Lift_unreal_copy.spectra")

    assert spec.is_realizable() is False

    node = RefinementNode()

    node.set_spec(spec)

    assert node.spec is not None
    assert node.spec is spec

    node.minimiseSpec()
    node.spec.to_file("tests/temp/Lift_unreal_core.spectra")

    assert node.unreal_core is not None
    assert node.spec.name == spec.name
    assert node.spec.inputs == spec.inputs
    assert node.spec.outputs == spec.outputs
    assert node.spec.assumptions == spec.assumptions
    assert node.spec.guarantees == [
        "(f1 & !f2 & !f3)",
        "G (f1 -> next(f1 | f2))",
        "G (((f1 & next(f2)) | (f2 & next(f3)) | (f2 & next(f1)) | (f3 & next(f2))) -> (b1 | b2 | b3))",
        "GF (f2)",
    ]
    assert node.spec.is_realizable() is False
    assert node.isRealizable() is False
    
def test_refinement_when_spec_not_set():

    node = RefinementNode()

    assert node.id is not None
    assert node.parent_id is None
    
    # assert node.spec is None
    assert node.gr1_units == []

    assert node.is_y_sat is None
    assert node.is_realizable is None
    assert node.is_satisfiable is None
    assert node.is_well_separated is None

    assert node.unreal_core is None
    assert node.counterstrategy is None
    assert node.path_length is None
    assert node.is_looping_path is None

    assert node.interpolant is None
    assert node.is_interpolant_state_separable is None
    assert node.num_state_components is None
    assert node.num_non_io_separable_state_components is None
    assert node.is_interpolant_fully_separable is None
    assert node.num_refs_generated is None

    assert node.time_y_sat_check is None
    assert node.time_realizability_check is None
    assert node.time_satisfiability_check is None
    assert node.time_well_separation_check is None

    assert node.time_refine is None
    assert node.time_unreal_core is None
    assert node.time_counterstrategy is None
    assert node.time_generation is None
    assert node.time_interpolation is None

    with pytest.raises(AttributeError):
        node.minimiseSpec()

    with pytest.raises(AttributeError):
        node.isYSat()

    with pytest.raises(AttributeError):
        node.isSatisfiable()

    with pytest.raises(AttributeError):
        node.isRealizable()

    with pytest.raises(AttributeError):
        node.isWellSeparated()

    with pytest.raises(AttributeError):
        node.getUnrealizableCore()

    with pytest.raises(AttributeError):
        node.getCounterstrategy()

    with pytest.raises(AttributeError):
        node.generateRefinements()

    with pytest.raises(AttributeError):
        node.generateRefinedNodes()
    
def test_refinement_when_spec_set_but_not_saved():

    initial_spec = SpectraSpecification.from_file("tests/specifications/Lift_unreal.spectra")

    spec = initial_spec.copy()

    node = RefinementNode()
    node.set_spec(spec)

    assert node.spec is not None

    with pytest.raises(ValueError):
        node.minimiseSpec()

    with pytest.raises(ValueError):
        node.isYSat()

    with pytest.raises(ValueError):
        node.isSatisfiable()

    with pytest.raises(ValueError):
        node.isRealizable()

    with pytest.raises(ValueError):
        node.isWellSeparated()

    with pytest.raises(ValueError):
        node.getUnrealizableCore()

    with pytest.raises(ValueError):
        node.getCounterstrategy()

    with pytest.raises(ValueError):
        node.generateRefinements()

    with pytest.raises(ValueError):
        node.generateRefinedNodes()

def test_refinement_when_spec_set_and_saved():

    initial_spec = SpectraSpecification.from_file("tests/specifications/Lift_unreal.spectra")

    spec = initial_spec.copy()
    spec.to_file("tests/temp/Lift_unreal_copy.spectra")

    node = RefinementNode()
    node.set_spec(spec)

    assert node.spec is not None
    assert node.spec.file_path == "tests/temp/Lift_unreal_copy.spectra"

    node.minimiseSpec()
    node.spec.to_file("tests/temp/Lift_unreal_core.spectra")

    assert node.spec.name == spec.name
    assert node.spec.inputs == spec.inputs
    assert node.spec.outputs == spec.outputs
    assert node.spec.assumptions == spec.assumptions
    assert node.spec.guarantees == [
        "(f1 & !f2 & !f3)",
        "G (f1 -> next(f1 | f2))",
        "G (((f1 & next(f2)) | (f2 & next(f3)) | (f2 & next(f1)) | (f3 & next(f2))) -> (b1 | b2 | b3))",
        "GF (f2)",
    ]

    assert node.isYSat() is True
    assert node.time_y_sat_check is not None

    assert node.isSatisfiable() is True
    assert node.time_satisfiability_check is not None

    assert node.isRealizable() is False
    assert node.time_realizability_check is not None

    assert node.isWellSeparated() is True
    assert node.time_well_separation_check is not None

    assert node.getUnrealizableCore() == [
        "(f1 & !f2 & !f3)",
        "G (f1 -> next(f1 | f2))",
        "G (((f1 & next(f2)) | (f2 & next(f3)) | (f2 & next(f1)) | (f3 & next(f2))) -> (b1 | b2 | b3))",
        "GF (f2)",
    ]
    assert node.time_unreal_core is not None

    assert node.getCounterstrategy().num_states == 1
    assert node.getCounterstrategy().states["S0"] is not None
    assert node.getCounterstrategy().states["S0"].is_initial is True
    assert node.getCounterstrategy().states["S0"].is_dead is False
    assert node.getCounterstrategy().states["S0"].inputs == { "b1": False, "b2": False, "b3": False }
    assert node.getCounterstrategy().states["S0"].outputs == { "f1": True, "f2": False }
    assert node.getCounterstrategy().states["S0"].influential_outputs == {}
    assert node.getCounterstrategy().states["S0"].successors == ["S0"]
    assert node.time_counterstrategy is not None

    refinements = node.generateRefinements()

    assert re.fullmatch(r"!\(!b\d & !b\d & !b\d\)", refinements[0])
    assert re.fullmatch(r"G\(!\(!b\d & !b\d & !b\d\)\)", refinements[1])
    assert re.fullmatch(r"G\(\(!b\d & !b\d & !b\d\) -> X\(!\(!b\d & !b\d & !b\d\)\)\)", refinements[2])
    assert re.fullmatch(r"G\(F\(!\(!b\d & !b\d & !b\d\)\)\)", refinements[3])
    
    assert node.time_generation is not None
    assert node.num_refs_generated == 4
    assert node.interpolant is not None
    assert node.time_interpolation is not None
    assert node.is_interpolant_state_separable is True
    assert node.num_state_components == 2
    assert node.num_non_io_separable_state_components == 0
    assert node.is_interpolant_fully_separable is True
    assert node.num_refs_generated == 4

    refined_nodes = node.generateRefinedNodes()

    assert len(refined_nodes) == 4

    assert refined_nodes[0].id is not None
    assert refined_nodes[0].parent_id == node.id
    assert refined_nodes[0].spec is None
    assert re.fullmatch(r"!\(!b\d & !b\d & !b\d\)", refined_nodes[0].gr1_units[0])

def test_rg_repair_core():
    spec = SpectraSpecification.from_file("tests/specifications/RG_repair_core.spectra")

    node = RefinementNode(gr1_units=["(!cl)", "alwEv (!cl)"])
    node.set_spec(spec)

    repair_core = node.getRepairCore()

    assert node.time_repair_core is not None
    assert repair_core == ["alwEv (!cl)"]
    assert node.gr1_units == ["alwEv (!cl)"]