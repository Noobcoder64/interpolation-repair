t0 :- hready.
st0 :- not t0.
:- st0.
{busreq}.
{decide}.
{hburst0}.
{hburst1}.
{hbusreq0}.
{hbusreq1}.
{hgrant0}.
{hgrant1}.
{hlock0}.
{hlock1}.
{hmaster0}.
{hmastlock}.
{hready}.
{locked}.
{start}.
{stateA1}.
{stateG10_1}.
{stateG2}.
{stateG2_0}.
{stateG2_1}.
{stateG3_0}.
{stateG3_1}.
{stateG3_2}.
rule0 :-  not hburst1 .
rule0 :-   not stateA1.
rule1 :- hburst1 .
rule1 :-  stateA1.
rule2 :-  not busreq .
rule2 :-  stateA1.
rule3 :- busreq .
rule3 :-   not stateA1.
rule4 :- hready .
rule4 :-   not start.
rule5 :-  not hburst1 .
rule5 :-   not stateG2.
rule6 :- hburst1 .
rule6 :-  stateG2.
rule7 :-  not busreq .
rule7 :-  stateG2.
rule8 :- busreq .
rule8 :-   not stateG2.
rule9 :- hburst1 .
rule9 :-   not stateG3_0 ,  not stateG3_1 ,  not stateG3_2.
rule10 :- hready .
rule10 :-  stateG3_0 ,  not stateG3_1 ,  not stateG3_2.
rule11 :-  not hready .
rule11 :-   not stateG3_0 , stateG3_1 ,  not stateG3_2.
rule12 :- hready .
rule12 :-  stateG3_0 ,  not stateG3_1 ,  not stateG3_2.
rule13 :-  not hready .
rule13 :-   not stateG3_0 , stateG3_1 ,  not stateG3_2.
rule14 :- hready .
rule14 :-   not stateG3_0 , stateG3_1 ,  not stateG3_2.
rule15 :-  not hready .
rule15 :-  stateG3_0 , stateG3_1 ,  not stateG3_2.
rule16 :- hready .
rule16 :-  stateG3_0 , stateG3_1 ,  not stateG3_2.
rule17 :-  not hready .
rule17 :-   not stateG3_0 ,  not stateG3_1 , stateG3_2.
rule18 :- hready .
rule18 :-   not stateG3_0 ,  not stateG3_1 , stateG3_2.
rule19 :-  not hready .
rule19 :-   not stateG3_0 ,  not stateG3_1 ,  not stateG3_2.
rule20 :-  not hready .
rule20 :-  hgrant0 ,  not hmaster0 .
rule20 :-   not hgrant0 , hmaster0.
rule21 :-  not hready .
rule21 :-  hgrant1 , hmaster0 .
rule21 :-   not hgrant1 ,  not hmaster0.
rule22 :-  not hready .
rule22 :-   not hmastlock ,  not locked .
rule22 :-  hmastlock , locked.
rule23 :-  not hgrant0 .
rule23 :-  locked.
rule24 :-  not hgrant0 .
rule24 :-   not locked.
rule25 :-  not hgrant1 .
rule25 :-  locked.
rule26 :-  not hgrant1 .
rule26 :-   not locked.
rule27 :-  not hbusreq1 .
rule27 :-   not stateG10_1.
rule28 :- hbusreq1 .
rule28 :-  stateG10_1.
rule29 :- hbusreq1 .
rule29 :-  stateG10_1.
rule30 :-  not hbusreq1 .
rule30 :-   not stateG10_1.
rule31 :- hbusreq1 .
rule31 :-  hgrant0.
rule32 :- hmaster0 .
rule32 :-   not busreq ,  not hbusreq0 .
rule32 :-  busreq , hbusreq0.
rule33 :-  not hmaster0 .
rule33 :-   not busreq ,  not hbusreq1 .
rule33 :-  busreq , hbusreq1.
:- rule0,rule1,rule2,rule3,rule4,rule5,rule6,rule7,rule8,rule9,rule10,rule11,rule12,rule13,rule14,rule15,rule16,rule17,rule18,rule19,rule20,rule21,rule22,rule23,rule24,rule25,rule26,rule27,rule28,rule29,rule30,rule31,rule32,rule33.
#show busreq/0.
#show decide/0.
#show hburst0/0.
#show hburst1/0.
#show hbusreq0/0.
#show hbusreq1/0.
#show hgrant0/0.
#show hgrant1/0.
#show hlock0/0.
#show hlock1/0.
#show hmaster0/0.
#show hmastlock/0.
#show hready/0.
#show locked/0.
#show start/0.
#show stateA1/0.
#show stateG10_1/0.
#show stateG2/0.
#show stateG2_0/0.
#show stateG2_1/0.
#show stateG3_0/0.
#show stateG3_1/0.
#show stateG3_2/0.
