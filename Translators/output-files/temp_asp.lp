t0 :- hbusreq0 .
t0 :-   not hlock0.
st0 :- not t0.
:- st0.
t1 :-  not hburst0 .
t1 :-  hbusreq0.
st1 :- not t1.
:- st1.
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
rule0 :- hburst0 , stateA1_0.
rule1 :-  not hburst1 .
rule1 :-   not stateA1_0.
rule2 :- hburst1 .
rule2 :-  stateA1_0.
rule3 :-  not hbusreq0 .
rule3 :-  stateA1_0.
rule4 :- hbusreq0 .
rule4 :-   not stateA1_0.
rule5 :- hready .
rule5 :-   not start.
rule6 :- hmastlock .
rule6 :-   not stateG2_0.
rule7 :- start .
rule7 :-   not stateG2_0.
rule8 :-  not hburst0 .
rule8 :-   not stateG2_0.
rule9 :-  not hburst1 .
rule9 :-   not stateG2_0.
rule10 :-  not hmaster0 .
rule10 :-   not stateG2_0.
rule11 :- hmaster0 .
rule11 :-  stateG2_0.
rule12 :-  not hbusreq0 .
rule12 :-  stateG2_0.
rule13 :- hbusreq0 .
rule13 :-   not stateG2_0.
rule14 :- hburst1 .
rule14 :-   not stateG3_0 ,  not stateG3_1 ,  not stateG3_2.
rule15 :- hready .
rule15 :-  stateG3_0 ,  not stateG3_1 ,  not stateG3_2.
rule16 :-  not hready .
rule16 :-   not stateG3_0 , stateG3_1 ,  not stateG3_2.
rule17 :- hready .
rule17 :-  stateG3_0 ,  not stateG3_1 ,  not stateG3_2.
rule18 :-  not hready .
rule18 :-   not stateG3_0 , stateG3_1 ,  not stateG3_2.
rule19 :- hready .
rule19 :-   not stateG3_0 , stateG3_1 ,  not stateG3_2.
rule20 :-  not hready .
rule20 :-  stateG3_0 , stateG3_1 ,  not stateG3_2.
rule21 :- hready .
rule21 :-  stateG3_0 , stateG3_1 ,  not stateG3_2.
rule22 :-  not hready .
rule22 :-   not stateG3_0 ,  not stateG3_1 , stateG3_2.
rule23 :- hready .
rule23 :-   not stateG3_0 ,  not stateG3_1 , stateG3_2.
rule24 :-  not hready .
rule24 :-   not stateG3_0 ,  not stateG3_1 ,  not stateG3_2.
rule25 :-  not hready .
rule25 :-  hgrant0 ,  not hmaster0 .
rule25 :-   not hgrant0 , hmaster0.
rule26 :-  not hready .
rule26 :-   not hlocked ,  not hmastlock .
rule26 :-  hlocked , hmastlock.
rule27 :-  not hgrant0 .
rule27 :-  hlocked.
rule28 :-  not hgrant0 .
rule28 :-   not hlocked.
rule29 :- hbusreq0 .
rule29 :-  hgrant0.
:- rule0,rule1,rule2,rule3,rule4,rule5,rule6,rule7,rule8,rule9,rule10,rule11,rule12,rule13,rule14,rule15,rule16,rule17,rule18,rule19,rule20,rule21,rule22,rule23,rule24,rule25,rule26,rule27,rule28,rule29.
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
