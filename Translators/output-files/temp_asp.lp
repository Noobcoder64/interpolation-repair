t0 :- hbusreq0 .
t0 :-   not hlock0.
st0 :- not t0.
:- st0.
{decide}.
{hburst0}.
{hburst1}.
{hbusreq0}.
{hgrant0}.
{hlock0}.
{hlocked}.
{hmaster0}.
{hmastlock}.
{hready}.
{start}.
{stateA1_0}.
{stateG2_0}.
{stateG3_0}.
{stateG3_1}.
{stateG3_2}.
rule0 :-  not hburst1 .
rule0 :-   not stateA1_0.
rule1 :- hburst1 .
rule1 :-  stateA1_0.
rule2 :-  not hbusreq0 .
rule2 :-  stateA1_0.
rule3 :- hbusreq0 .
rule3 :-   not stateA1_0.
rule4 :- hready .
rule4 :-   not start.
rule5 :- hmastlock .
rule5 :-   not stateG2_0.
rule6 :- start .
rule6 :-   not stateG2_0.
rule7 :-  not hburst0 .
rule7 :-   not stateG2_0.
rule8 :-  not hburst1 .
rule8 :-   not stateG2_0.
rule9 :-  not hmaster0 .
rule9 :-   not stateG2_0.
rule10 :- hmaster0 .
rule10 :-  stateG2_0.
rule11 :-  not hbusreq0 .
rule11 :-  stateG2_0.
rule12 :- hbusreq0 .
rule12 :-   not stateG2_0.
rule13 :- hburst1 .
rule13 :-   not stateG3_0.
rule14 :- hready .
rule14 :-  stateG3_0.
rule15 :-  not hready .
rule15 :-   not stateG3_0.
rule16 :- hready .
rule16 :-  stateG3_0.
rule17 :-  not hready .
rule17 :-   not stateG3_0.
rule18 :- hready .
rule18 :-   not stateG3_0.
rule19 :-  not hready .
rule19 :-  stateG3_0.
rule20 :- hready .
rule20 :-  stateG3_0.
rule21 :-  not hready .
rule21 :-   not stateG3_0.
rule22 :- hready .
rule22 :-   not stateG3_0.
rule23 :-  not hready .
rule23 :-   not stateG3_0.
rule24 :-  not hready .
rule24 :-  hgrant0 ,  not hmaster0 .
rule24 :-   not hgrant0 , hmaster0.
rule25 :-  not hready .
rule25 :-   not hlocked ,  not hmastlock .
rule25 :-  hlocked , hmastlock.
rule26 :-  not hgrant0 .
rule26 :-  hlocked.
rule27 :-  not hgrant0 .
rule27 :-   not hlocked.
rule28 :- hbusreq0 .
rule28 :-  hgrant0.
:- rule0,rule1,rule2,rule3,rule4,rule5,rule6,rule7,rule8,rule9,rule10,rule11,rule12,rule13,rule14,rule15,rule16,rule17,rule18,rule19,rule20,rule21,rule22,rule23,rule24,rule25,rule26,rule27,rule28.
#show decide/0.
#show hburst0/0.
#show hburst1/0.
#show hbusreq0/0.
#show hgrant0/0.
#show hlock0/0.
#show hlocked/0.
#show hmaster0/0.
#show hmastlock/0.
#show hready/0.
#show start/0.
#show stateA1_0/0.
#show stateG2_0/0.
#show stateG3_0/0.
#show stateG3_1/0.
#show stateG3_2/0.
