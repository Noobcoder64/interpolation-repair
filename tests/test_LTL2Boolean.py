import LTL2Boolean as l2b
from path import Path, State

def test_rg1_asm_1():
    # Test case for gr1LTL2Boolean function
    ltlFormula = "G(F(!(req)))"
    path = Path(
        initial_state=State("S0"),
        transient_states=[],
        looping_states=[State("S1"), State("S2")],
    )
    
    # Expected output
    expected_output = "(((!(req__S1))) | ((!(req__S2))))"
    
    # Call the function
    result = l2b.gr1LTL2Boolean(ltlFormula, path)
    
    # Assert the result
    assert result == expected_output, f"Expected {expected_output}, but got {result}"

def test_rg1_gar_1():
    # Test case for gr1LTL2Boolean function
    ltlFormula = "G((cl->!(val)))"
    path = Path(
        initial_state=State("S0"),
        transient_states=[],
        looping_states=[State("S1"), State("S2")],
    )
    
    # Expected output
    expected_output = "(((cl__S0->!(val__S0)))) & (((cl__S1->!(val__S1)))) & (((cl__S2->!(val__S2))))"
    
    # Call the function
    result = l2b.gr1LTL2Boolean(ltlFormula, path)
    
    # Assert the result
    assert result == expected_output, f"Expected {expected_output}, but got {result}"

def test_rg1_gar_2():
    # Test case for gr1LTL2Boolean function
    ltlFormula = "G(F((gr&val)))"
    path = Path(
        initial_state=State("S0"),
        transient_states=[],
        looping_states=[State("S1"), State("S2")],
    )
    
    # Expected output
    expected_output = "((((gr__S1&val__S1))) | (((gr__S2&val__S2))))"
    
    # Call the function
    result = l2b.gr1LTL2Boolean(ltlFormula, path)
    
    # Assert the result
    assert result == expected_output, f"Expected {expected_output}, but got {result}"

def test_lgs_gar_1():
    # Test case for lgsLTL2Boolean function
    ltlFormula = "G((handle_down->(!(X(handle_down))|X(gear_extended))))"

    s0 = State("S0")
    sf = State("Sf")
    s0.set_successor(sf.id_state)
    path = Path(
        initial_state=s0,
        transient_states=[sf],        
    )
    
    # Expected output
    expected_output = "(((handle_down__S0->(!((handle_down__Sf))|(gear_extended__Sf))))) & (TRUE)"
    
    # Call the function
    result = l2b.gr1LTL2Boolean(ltlFormula, path)
    
    # Assert the result
    assert result == expected_output, f"Expected {expected_output}, but got {result}"

def test_lgs_gar_2():
    # Test case for lgsLTL2Boolean function
    ltlFormula = "G((handle_up->(!(X(handle_up))|!(X(gear_extended)))))"

    s0 = State("S0")
    sf = State("Sf")
    s0.set_successor(sf.id_state)
    path = Path(
        initial_state=s0,
        transient_states=[sf],        
    )
    
    # Expected output
    expected_output = "(((handle_up__S0->(!((handle_up__Sf))|!((gear_extended__Sf)))))) & (TRUE)"
    
    # Call the function
    result = l2b.gr1LTL2Boolean(ltlFormula, path)
    
    # Assert the result
    assert result == expected_output, f"Expected {expected_output}, but got {result}"

