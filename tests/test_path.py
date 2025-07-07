from path import State, Path

# Tests for the State class
def test_state_init():
    state = State("S1")
    assert state.id_state == "S1"
    assert state.valuation == set()
    assert state.successor is None

def test_state_set_successor():
    state = State("S1")
    state.set_successor("S2")
    assert state.successor == "S2"

def test_state_add_to_valuation():
    state = State("S1")
    state.add_to_valuation("x")
    state.add_to_valuation("y")
    assert state.valuation == {"x", "y"}

def test_state_get_valuation():
    state = State("S1")
    state.add_to_valuation("x")
    state.add_to_valuation("y")
    expected_options = {"x__S1 & y__S1", "y__S1 & x__S1"}
    assert state.get_valuation() in expected_options

# Tests for the Path class
def test_path_init():
    initial = State("S1")
    transient = [State("S2"), State("S3")]
    looping = [State("S4")]
    path = Path(initial, transient, looping)
    assert path.initial_state == initial
    assert path.transient_states == transient
    assert path.looping_states == looping
    assert path.is_loop is True
    assert path.states["S1"] == initial
    assert path.states["S2"] == transient[0]
    assert path.states["S3"] == transient[1]
    assert path.states["S4"] == looping[0]

def test_path_get_valuation():
    initial = State("S1")
    initial.add_to_valuation("x")
    transient = [State("S2")]
    transient[0].add_to_valuation("y")
    path = Path(initial, transient)
    assert path.get_valuation() == "x__S1 & y__S2"

def test_path_unroll():
    initial = State("S1")
    transient = [State("S2")]
    looping = [State("S3"), State("S4")]
    path = Path(initial, transient, looping)
    path.unroll()
    assert path.unrolling_degree == 1
    assert len(path.unrolled_states) == 2
    assert path.unrolled_states[0].id_state == "S3_1"
    assert path.unrolled_states[1].id_state == "S4_1"

def test_path_str():
    initial = State("S1")
    transient = [State("S2")]
    looping = [State("S3")]
    path = Path(initial, transient, looping)
    assert str(path) == "S1 -> S2 -> loop( -> S3)"

def test_rg_path():
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
    assert str(path) == "S0 -> loop( -> S1 -> S2)"
    expected_literals = {"req__S1", "cl__S1", "!req__S2", "cl__S2"}
    assert set(path.get_valuation().split(" & ")) == expected_literals

def test_lgs_path():
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
    assert str(path) == "S0 -> Sf"
    expected_literals = {"handle_up__S0", "handle_down__S0", "handle_up__Sf", "handle_down__Sf"}
    assert set(path.get_valuation().split(" & ")) == expected_literals