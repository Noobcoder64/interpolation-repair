from counterstrategy import Counterstrategy, CounterstrategyState


def test_rg_counterstrategy():
    # Test case for RG1 counterstrategy
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
    assert counterstrategy.num_states == 3
    assert counterstrategy.get_state("S0").is_initial == True
    assert counterstrategy.get_state("S0").is_dead == False
    assert counterstrategy.get_state("S0").inputs == {"req": True, "cl": True}
    assert counterstrategy.get_state("S0").outputs == {}
    assert counterstrategy.get_state("S0").influential_outputs == {}
    assert counterstrategy.get_state("S0").successors == ["S1"]
    # assert counterstrategy.get_state("S0").get_valuation() == ["req", "cl"]

    assert counterstrategy.get_state("S1").is_initial == False
    assert counterstrategy.get_state("S1").is_dead == False
    assert counterstrategy.get_state("S1").inputs == {"req": False, "cl": True}
    assert counterstrategy.get_state("S1").outputs == {}
    assert counterstrategy.get_state("S1").successors == ["S2"]
    # assert counterstrategy.get_state("S1").get_valuation() == ["!req", "cl"]


    assert counterstrategy.get_state("S2").is_initial == False
    assert counterstrategy.get_state("S2").is_dead == False
    assert counterstrategy.get_state("S2").inputs == {"req": True, "cl": True}
    assert counterstrategy.get_state("S2").outputs == {}
    assert counterstrategy.get_state("S2").influential_outputs == {}
    assert counterstrategy.get_state("S2").successors == ["S1"]
    # assert counterstrategy.get_state("S2").get_valuation() == ["req", "cl"]


def test_rg1_counterstrategy():
    s0 = CounterstrategyState(
        name="S0",
        is_initial=True,
        inputs={"r": False, "c": False},
        outputs={"g": False},
        successors=["S0", "S1"],
    )
    s1 = CounterstrategyState(
        name="S1",
        is_initial=True,
        inputs={"r": False, "c": False},
        outputs={"g": True},
        successors=["S2"]
    )
    s2 = CounterstrategyState(
        name="S2",
        inputs={"r": False, "c": True},
        outputs={"g": False},
        successors=["S2"]
    )
    counterstrategy = Counterstrategy(states={"S0": s0, "S1": s1, "S2": s2})
    assert counterstrategy.num_states == 3
    assert counterstrategy.get_state("S0").is_initial == True
    assert counterstrategy.get_state("S0").is_dead == False
    assert counterstrategy.get_state("S0").inputs == {"r": False, "c": False}
    assert counterstrategy.get_state("S0").outputs == {"g": False}
    assert counterstrategy.get_state("S0").influential_outputs == {"g": False}
    assert counterstrategy.get_state("S0").successors == ["S0", "S1"]

    assert counterstrategy.get_state("S1").is_initial == True
    assert counterstrategy.get_state("S1").is_dead == False
    assert counterstrategy.get_state("S1").inputs == {"r": False, "c": False}
    assert counterstrategy.get_state("S1").outputs == {"g": True}
    assert counterstrategy.get_state("S1").influential_outputs == {"g": True}
    assert counterstrategy.get_state("S1").successors == ["S2"]


    assert counterstrategy.get_state("S2").is_initial == False
    assert counterstrategy.get_state("S2").is_dead == False
    assert counterstrategy.get_state("S2").inputs == {"r": False, "c": True}
    assert counterstrategy.get_state("S2").outputs == {"g": False}
    assert counterstrategy.get_state("S2").influential_outputs == {}
    assert counterstrategy.get_state("S2").successors == ["S2"]

    path = counterstrategy.extract_random_path()
    print(path)
    assert path is not None

def test_lift_counterstrategy():
    s0 = CounterstrategyState(
        name="S0",
        is_initial=True,
        inputs={"b1": False, "b2": False, "b3": False},
        outputs={"f1": True, "f2": False},
        successors=["S0"],
    )
    counterstrategy = Counterstrategy(states={"S0": s0})
    assert counterstrategy.num_states == 1
    assert counterstrategy.get_state("S0").is_initial == True
    assert counterstrategy.get_state("S0").is_dead == False
    assert counterstrategy.get_state("S0").inputs == {"b1": False, "b2": False, "b3": False}
    assert counterstrategy.get_state("S0").outputs == {"f1": True, "f2": False}
    assert counterstrategy.get_state("S0").influential_outputs == {}
    assert counterstrategy.get_state("S0").successors == ["S0"]

    path = counterstrategy.extract_random_path()
    print(path)
    assert path is not None