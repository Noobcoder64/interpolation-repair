from spectra_specification import SpectraSpecification
from counterstrategy import Counterstrategy
import specification as sp
import re
import LTL2Boolean as l2b
import mathsat_utils as msu
from path import Path, State
import random
import interpolation


def test_pcar():
    print("\nTesting PCar Specification\n")

    spec = SpectraSpecification.from_file("tests/specifications/PCarLTL_Unrealizable_V_2_unrealizable0_888_PCar_fixed_unrealizable.spectra")
    assert isinstance(spec, SpectraSpecification)
    assert spec.file_path == "tests/specifications/PCarLTL_Unrealizable_V_2_unrealizable0_888_PCar_fixed_unrealizable.spectra"
    assert spec.name == "PCarLTL_Unrealizable_V_2_unrealizable0_888_PCar_fixed_unrealizable"
    assert spec.inputs == [
        "obstacle_0",
        "sideSense_0",
        "parkResult_0"
    ]
    # Aux variables treated as system variables
    assert spec.outputs == [
        "throttle_0",
        "throttle_1",
        "steer_0",
        "steer_1",
        "parkCommand_0",
        "parkCommand_1",
        "spec_policy_0",
        "spec_policy_1",
        "spec_policy_2",
        "eNV_CONSTRAINT_0_respondsTo_responded",
        "pREV_aux_1",
    ]

    assert spec.is_realizable() == False
    assert spec.is_satisfiable() == True
    assert spec.is_y_sat() == True
    assert spec.is_well_separated() == False

    unreal_core = spec.compute_unrealizable_core()
    assert isinstance(unreal_core, list)
    assert len(unreal_core) == 4

    print("\nUnrealizable Core:\n", "\n".join(unreal_core))
    assert unreal_core == [
        "((!spec_policy_0 & !spec_policy_1 & !spec_policy_2))",
        "GF ((spec_policy_0 & !spec_policy_1 & spec_policy_2))",
        "G (((((!spec_policy_0 & !spec_policy_1 & !spec_policy_2) & (sideSense_0)) & (!parkResult_0)) -> (((spec_policy_0 <-> next(spec_policy_0)) & (spec_policy_1 <-> next(spec_policy_1)) & (spec_policy_2 <-> next(spec_policy_2))) & (!parkCommand_0 & parkCommand_1))))",
        "G ((next(eNV_CONSTRAINT_0_respondsTo_responded) <-> ((!obstacle_0) | (eNV_CONSTRAINT_0_respondsTo_responded & !((!throttle_0 & throttle_1))))))",
    ]

    counterstrategy = spec.compute_counterstrategy(min_out_vars=True)
    assert isinstance(counterstrategy, Counterstrategy)
    print("\nCounterstrategy:\n", counterstrategy)
    assert counterstrategy.num_states == 3

    path = counterstrategy.extract_random_path()
    print("Path:", path)
    assert str(path) == "S0_0 -> S1_1 -> S2_2 -> loop( -> S2_3)"
    path.unroll()
    print("Unrolled Path:", path)
    assert str(path) == "S0_0 -> S1_1 -> S2_2 -> S2_3_1 -> loop( -> S2_3)"


    assumptions = [re.sub(r"\s", "", line) for line in sp.unspectra(spec.assumptions)]
    guarantees = [re.sub(r"\s", "", line) for line in sp.unspectra(unreal_core)]

    assumptions_boolean = list(filter(None,[l2b.gr1LTL2Boolean(asm, path) for asm in assumptions]))
    print("\nAssumptions boolean:\n", "\n".join(assumptions_boolean))

    valuations_boolean = path.get_valuation()

    print("\nValuations:")
    print(valuations_boolean)

    if assumptions_boolean != []:
        assum_val_boolean = " & ".join(assumptions_boolean) + ((" & " + valuations_boolean) if valuations_boolean != "" else "")
    else:
        assum_val_boolean = valuations_boolean

    guarantees_boolean = list(filter(None,[l2b.gr1LTL2Boolean(gar, path) for gar in guarantees]))
    print("\nGuarantees boolean\n:", "\n".join(guarantees_boolean))

    asm_val_gar_boolean = assum_val_boolean + " & " + " & ".join(guarantees_boolean)

    # Assertion failing
    # assert msu.is_satisfiable(asm_val_gar_boolean) == False


def test_pcar_core():
    spec = SpectraSpecification.from_file("tests/specifications/PCarLTL_Unrealizable_V_2_unrealizable0_888_PCar_fixed_unrealizable.spectra")
    assert isinstance(spec, SpectraSpecification)
    assert spec.file_path == "tests/specifications/PCarLTL_Unrealizable_V_2_unrealizable0_888_PCar_fixed_unrealizable.spectra"
    assert spec.name == "PCarLTL_Unrealizable_V_2_unrealizable0_888_PCar_fixed_unrealizable"
    assert spec.inputs == [
        "obstacle_0",
        "sideSense_0",
        "parkResult_0"
    ]
    # Aux variables treated as system variables
    assert spec.outputs == [
        "throttle_0",
        "throttle_1",
        "steer_0",
        "steer_1",
        "parkCommand_0",
        "parkCommand_1",
        "spec_policy_0",
        "spec_policy_1",
        "spec_policy_2",
        "eNV_CONSTRAINT_0_respondsTo_responded",
        "pREV_aux_1",
    ]

    assert spec.is_realizable() == False
    assert spec.is_satisfiable() == True
    assert spec.is_y_sat() == True
    assert spec.is_well_separated() == False

    unreal_core = spec.compute_unrealizable_core()
    assert isinstance(unreal_core, list)
    assert len(unreal_core) == 4

    print("\nUnrealizable Core:\n", "\n".join(unreal_core))
    assert unreal_core == [
        "((!spec_policy_0 & !spec_policy_1 & !spec_policy_2))",
        "GF ((spec_policy_0 & !spec_policy_1 & spec_policy_2))",
        "G (((((!spec_policy_0 & !spec_policy_1 & !spec_policy_2) & (sideSense_0)) & (!parkResult_0)) -> (((spec_policy_0 <-> next(spec_policy_0)) & (spec_policy_1 <-> next(spec_policy_1)) & (spec_policy_2 <-> next(spec_policy_2))) & (!parkCommand_0 & parkCommand_1))))",
        "G ((next(eNV_CONSTRAINT_0_respondsTo_responded) <-> ((!obstacle_0) | (eNV_CONSTRAINT_0_respondsTo_responded & !((!throttle_0 & throttle_1))))))",
    ]

    core_spec = SpectraSpecification(
        name=spec.name + "_core",
        inputs=spec.inputs,
        outputs=spec.outputs,
        assumptions=spec.assumptions,
        guarantees=unreal_core,
    )
    core_spec.to_file("tests/temp/PCarLTL_Unrealizable_V_2_unrealizable0_888_PCar_fixed_unrealizable_core.spectra")

    assert core_spec.is_realizable() == False
    assert core_spec.is_satisfiable() == True
    assert core_spec.is_y_sat() == True
    assert core_spec.is_well_separated() == False

    counterstrategy = core_spec.compute_counterstrategy(min_out_vars=True)
    assert isinstance(counterstrategy, Counterstrategy)
    print("\nCounterstrategy:\n", counterstrategy)
    assert counterstrategy.num_states == 1

    path = counterstrategy.extract_random_path()
    print("Path:", path)
    assert str(path) == "S0_0 -> loop( -> S0_1)"
    path.unroll()
    print("Unrolled Path:", path)
    assert str(path) == "S0_0 -> S0_1_1 -> loop( -> S0_1)"

    assumptions = [re.sub(r"\s", "", line) for line in sp.unspectra(core_spec.assumptions)]
    guarantees = [re.sub(r"\s", "", line) for line in sp.unspectra(unreal_core)]

    assumptions_boolean = list(filter(None,[l2b.gr1LTL2Boolean(asm, path) for asm in assumptions]))
    print("\nAssumptions boolean:\n", "\n".join(assumptions_boolean))

    valuations_boolean = path.get_valuation()

    print("\nValuations:")
    print(valuations_boolean)

    if assumptions_boolean != []:
        assum_val_boolean = " & ".join(assumptions_boolean) + ((" & " + valuations_boolean) if valuations_boolean != "" else "")
    else:
        assum_val_boolean = valuations_boolean

    guarantees_boolean = list(filter(None,[l2b.gr1LTL2Boolean(gar, path) for gar in guarantees]))
    print("\nGuarantees boolean\n:", "\n".join(guarantees_boolean))

    asm_val_gar_boolean = assum_val_boolean + " & " + " & ".join(guarantees_boolean)
    assert msu.is_satisfiable(asm_val_gar_boolean) == False

    interpolant = msu.compute_craig_interpolant(valuations_boolean, " & ".join(guarantees_boolean), cleanup=False)
    print("Interpolant:", interpolant)

    state_components = interpolation.extractStateComponents(interpolant)
    print("State components:", state_components)

    refinements, non_io_separable = interpolation.getRefinementsFromStateComponents(state_components, path, spec.inputs)
    print("Refinements:", refinements)


def test_pcar_ref_1():

    spec = SpectraSpecification.from_file("tests/specifications/PCarLTL_Unrealizable_V_2_unrealizable0_888_PCar_fixed_unrealizable.spectra")

    refined_spec = SpectraSpecification(
        name=spec.name,
        inputs=spec.inputs,
        outputs=spec.outputs,
        assumptions=spec.assumptions + ["!(sideSense_0 & !parkResult_0)"],
        guarantees=spec.guarantees,
    )

    refined_spec.to_file("tests/temp/PCarLTL_Unrealizable_V_2_unrealizable0_888_PCar_fixed_unrealizable_ref_1.spectra")
    assert refined_spec.is_y_sat() == False
    assert refined_spec.is_realizable() == True
    assert refined_spec.is_satisfiable() == False
    assert refined_spec.is_well_separated() == True

def test_pcar_ref_2():

    spec = SpectraSpecification.from_file("tests/specifications/PCarLTL_Unrealizable_V_2_unrealizable0_888_PCar_fixed_unrealizable.spectra")

    refined_spec = SpectraSpecification(
        name=spec.name,
        inputs=spec.inputs,
        outputs=spec.outputs,
        assumptions=spec.assumptions + ["G((sideSense_0 & !parkResult_0) -> next(!(sideSense_0 & !parkResult_0)))"],
        guarantees=spec.guarantees,
    )

    refined_spec.to_file("tests/temp/PCarLTL_Unrealizable_V_2_unrealizable0_888_PCar_fixed_unrealizable_ref_2.spectra")
    assert refined_spec.is_y_sat() == True
    assert refined_spec.is_realizable() == True
    assert refined_spec.is_satisfiable() == True
    assert refined_spec.is_well_separated() == False

def test_pcar_ref_3():

    spec = SpectraSpecification.from_file("tests/specifications/PCarLTL_Unrealizable_V_2_unrealizable0_888_PCar_fixed_unrealizable.spectra")

    refined_spec = SpectraSpecification(
        name=spec.name,
        inputs=spec.inputs,
        outputs=spec.outputs,
        assumptions=spec.assumptions + ["G(!(sideSense_0 & !parkResult_0))"],
        guarantees=spec.guarantees,
    )

    refined_spec.to_file("tests/temp/PCarLTL_Unrealizable_V_2_unrealizable0_888_PCar_fixed_unrealizable_ref_3.spectra")
    assert refined_spec.is_y_sat() == False
    assert refined_spec.is_realizable() == True
    assert refined_spec.is_satisfiable() == False
    assert refined_spec.is_well_separated() == False

def test_pcar_ref_4():

    spec = SpectraSpecification.from_file("tests/specifications/PCarLTL_Unrealizable_V_2_unrealizable0_888_PCar_fixed_unrealizable.spectra")

    refined_spec = SpectraSpecification(
        name=spec.name,
        inputs=spec.inputs,
        outputs=spec.outputs,
        assumptions=spec.assumptions + ["GF (!(sideSense_0 & !parkResult_0))"],
        guarantees=spec.guarantees,
    )

    refined_spec.to_file("tests/temp/PCarLTL_Unrealizable_V_2_unrealizable0_888_PCar_fixed_unrealizable_ref_4.spectra")
    assert refined_spec.is_y_sat() == True
    assert refined_spec.is_realizable() == False
    assert refined_spec.is_satisfiable() == True
    assert refined_spec.is_well_separated() == False