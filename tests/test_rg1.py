from spectra_specification import SpectraSpecification
from counterstrategy import Counterstrategy
import specification as sp
import re
import LTL2Boolean as l2b
import mathsat_utils as msu
from path import Path, State
import random
import interpolation

def test_rg1_specification():
    print("\nTesting RG1 Specification\n")

    spec = SpectraSpecification.from_file("tests/specifications/RG1.spectra")
    assert isinstance(spec, SpectraSpecification)
    assert spec.file_path == "tests/specifications/RG1.spectra"
    assert spec.name == "RG1"
    assert spec.inputs == ["r", "c"]
    assert spec.outputs == ["g", "v", "sYS_CONSTRAINT_0_pRespondsToS_responded"]

    assert spec.is_realizable() == False
    assert spec.is_satisfiable() == True
    assert spec.is_y_sat() == True
    assert spec.is_well_separated() == True

    unreal_core = spec.compute_unrealizable_core()
    assert isinstance(unreal_core, list)
    assert len(unreal_core) == 2

    assert unreal_core == [
        "G (((c | g) -> !(next(g))))",
        "GF ((g & v))",
    ]

    core_spec = SpectraSpecification(
        name=spec.name,
        inputs=spec.inputs,
        outputs=spec.outputs,
        assumptions=spec.assumptions,
        guarantees=unreal_core,
    )
    core_spec.to_file("tests/temp/RG1_core.spectra", use_alw=True)

    counterstrategy = core_spec.compute_counterstrategy(min_out_vars=True)
    assert isinstance(counterstrategy, Counterstrategy)
    assert counterstrategy.num_states == 3

    print("Counterstrategy:", counterstrategy)

    path = counterstrategy.extract_random_path()

    print("Path:", path)
    path.unroll()
    print("Unrolled Path:", path)


    assumptions = sp.unspectra(spec.assumptions)
    assumptions = [re.sub(r"\s", "", line) for line in assumptions]

    guarantees = sp.unspectra(unreal_core)
    guarantees = [re.sub(r"\s", "", line) for line in guarantees]

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
    print("Guarantees boolean:", "\n".join(guarantees_boolean))
    print("Guarantees are sat:", msu.is_satisfiable(" & ".join(guarantees_boolean)))

    interpolant = msu.compute_craig_interpolant(assum_val_boolean, " & ".join(guarantees_boolean), cleanup=False)
    print("Interpolant:", interpolant)

    # assert interpolant == ""

    state_components = interpolation.extractStateComponents(interpolant)
    print("State components:", state_components)

    # assert state_components == ""

    refinements, non_io_separable = interpolation.getRefinementsFromStateComponents(state_components, path, spec.inputs)
    print("Refinements:", refinements)
    assert not any("aux" in asm or "CONSTRAINT" in asm for asm in refinements)
    assert not any("G(F(!(!g)))" in asm for asm in refinements)
