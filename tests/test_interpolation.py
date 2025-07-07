import pytest
import interpolation as ip
from path import Path, State
from counterstrategy import Counterstrategy, CounterstrategyState

def test_extractStateComponents():

    interpolant = "(a__S0 | b__S0) & c__S0 & !b__S1"

    state_components = ip.extractStateComponents(interpolant)

    assert state_components["S0"] == "(a | b) & c" or state_components["S0"] == "c & (a | b)"
    assert state_components["S1"] == "!b"

def test_non_state_separable():

    interpolant = "a__S0 | a__S1"

    with pytest.raises(ip.NonStateSeparableException):
        state_components = ip.extractStateComponents(interpolant)

def test_rg_extractStateComponents():

    interpolant = "cl__S1 & cl__S2"

    state_components = ip.extractStateComponents(interpolant)

    expected_state_components = {'S1': 'cl', 'S2': 'cl'}

    assert state_components == expected_state_components

def test_lgs_extractStateComponents():

    interpolant = "handle_up__S0 & handle_down__S0 & handle_up__Sf & handle_down__Sf"

    state_components = ip.extractStateComponents(interpolant)

    expected_state_components = {'S0': 'handle_down & handle_up', 'Sf': 'handle_up & handle_down'}

    assert state_components["S0"] == "handle_up & handle_down" or state_components["S0"] == "handle_down & handle_up"
    assert state_components["Sf"] == "handle_up & handle_down" or state_components["Sf"] == "handle_down & handle_up"

def test_projectOntoVars():
    projection = ip.projectOntoVars("a & c", ["a"])
    expetected_projection = "a"
    assert projection == expetected_projection

def test_rg1_getRefinementsFromStateComponents():

    state_components = {'S1': 'cl', 'S2': 'cl'}

    s0 = State("S0")
    s1 = State("S1")
    s2 = State("S2")
    s0.set_successor(s1.id_state)
    s1.add_to_valuation("req")
    s1.add_to_valuation("cl")
    s1.set_successor(s2.id_state)
    s2.add_to_valuation("!req")
    s2.add_to_valuation("cl")
    s2.set_successor(s1.id_state)
    path = Path(
        initial_state=s0,
        transient_states=[],
        looping_states=[s1, s2],
    )

    input_vars = ["req", "cl"]

    refinements, non_io_separable = ip.getRefinementsFromStateComponents(state_components, path, input_vars)

    print(refinements)

    assert set(refinements) == set(['G((cl) -> X(!(cl)))', 'G(F(!(cl)))'])

def test_lgs_getRefinementsFromStateComponents():

    state_components = {'S0': 'handle_down & handle_up', 'Sf': 'handle_up & handle_down'}

    s0 = State("S0")
    sf = State("Sf")
    s0.add_to_valuation("handle_up")
    s0.add_to_valuation("handle_down")
    s0.set_successor(sf.id_state)
    sf.add_to_valuation("handle_up")
    sf.add_to_valuation("handle_down")
    path = Path(
        initial_state=s0,
        transient_states=[sf],
    )

    input_vars = ["handle_up", "handle_down"]

    refinements, non_io_separable = ip.getRefinementsFromStateComponents(state_components, path, input_vars)

    expected_refinements = ['G((handle_down & handle_up) -> X(!(handle_up & handle_down)))', 'G(!(handle_up & handle_down))', '!(handle_down & handle_up)']

    assert set(refinements) == set(expected_refinements)


def test_rg_generateRefinements():
    s0 = CounterstrategyState(
        name="S0",
        is_initial=True,
        inputs={"req": True, "cl": True},
        outputs={},
        successors=["S1"],
    )
    s1 = CounterstrategyState(
        name="S1",
        inputs={"req": False, "cl": True},
        outputs={},
        successors=["S2"]
    )
    s2 = CounterstrategyState(
        name="S2",
        inputs={"req": True, "cl": True},
        outputs={},
        successors=["S1"]
    )
    counterstrategy = Counterstrategy(states={"S0": s0, "S1": s1, "S2": s2})

    refinements, metrics = ip.generateRefinements(
        counterstrategy,
        assumptions=["GF (!(req))"],
        guarantees=["G ((cl -> !(val)))", "GF ((gr & val))"],
        input_vars=["req", "cl"],
    )

    print("Refinements:", refinements)
    print("Metrics:", metrics)

    assert set(refinements) == { "G(!(cl))", "G((cl) -> X(!(cl)))", "G(F(!(cl)))" }

    assert metrics["path_length"] == 6
    assert metrics["path_is_looping"] == True
    assert metrics["interpolant"] == "cl__S1_3 & cl__S2_2" or metrics["interpolant"] == "cl__S2_2 & cl__S1_3"
    assert metrics["time_interpolation"] is not None
    assert metrics["is_interpolant_state_separable"] == True
    assert metrics["num_state_components"] == 2
    assert metrics["num_non_io_separable_state_components"] == 0
    assert metrics["is_interpolant_fully_separable"] == True
