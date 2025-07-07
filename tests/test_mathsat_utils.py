import mathsat_utils as msu

# def test_writeMathsatFormulaToFile(tmp_path):
#     # Test case for writeMathsatFormulaToFile function
#     filename = "temp/test_formula.msat"
#     # formula = "(!req__S1 | !req__S2) & (req__S1 & cl__S1) & (!req__S2 | cl__S2)"
#     formula = "(((!(req__S1))) | ((!(req__S2)))) & req__S1 & cl__S1 & !req__S2 & cl__S2"
    
#     # Call the function
#     msu.writeMathsatFormulaToFile(filename, formula)
    
#     # Read the file and check its content
#     with open(filename, "r") as f:
#         content = f.read()
    
#     # Check if the content matches the expected format
#     assert "VAR" in content
#     assert "FORMULA" in content
#     assert formula in content

def test_compute_craig_interpolant_rg1():
    # Test case for compute_craig_interpolant function
    formula1 = "(((!(req__S1))) | ((!(req__S2)))) & req__S1 & cl__S1 & !req__S2 & cl__S2"
    formula2 = "(((cl__S0->!(val__S0)))) & (((cl__S1->!(val__S1)))) & (((cl__S2->!(val__S2)))) & ((((gr__S1&val__S1))) | (((gr__S2&val__S2))))"
    
    interpolant = msu.compute_craig_interpolant(formula1, formula2)
    
    assert interpolant == "cl__S1 & cl__S2" or interpolant == "cl__S2 & cl__S1"

def test_compute_craig_interpolant_lgs():
    # Test case for compute_craig_interpolant function
    valuations_boolean = "handle_up__S0 & handle_down__S0 & handle_up__Sf & handle_down__Sf"
    gar_1_boolean = "(((handle_down__S0->(!((handle_down__Sf))|(gear_extended__Sf))))) & (TRUE)"
    gar_2_boolean = "(((handle_up__S0->(!((handle_up__Sf))|!((gear_extended__Sf)))))) & (TRUE)"
    gars_boolean = gar_1_boolean + " & " + gar_2_boolean
    
    interpolant = msu.compute_craig_interpolant(valuations_boolean, gars_boolean)
    
    expected_interpolant = "handle_up__S0 & handle_down__S0 & handle_up__Sf & handle_down__Sf"

    assert set(interpolant.split(" & ")) == set(expected_interpolant.split(" & "))

def test_compute_craig_interpolant_1():
    interpolant = msu.compute_craig_interpolant("a & b", "!b")
    assert interpolant == "b"

def test_compute_craig_interpolant_2():
    interpolant = msu.compute_craig_interpolant("(a | b) & (c | d)", "!a & !b")
    assert interpolant == "(b | a)"