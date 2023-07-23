t0 :-  not hlock0.
t0 :- hbusreq0.
st0 :- not t0.
:- st0.
{decide }.
{hburst0 }.
{hburst1 }.
{hbusreq0 }.
{hgrant0 }.
{hlock0 }.
{hlocked }.
{hmaster0 }.
{hmastlock }.
{hready}.
{start }.
{stateA1_0 }.
{stateG2_0 }.
{stateG3_0 }.
{stateG3_1 }.
{stateG3_2 }.
rule0 :-  not nextstateA1_0=false.
rule1 :- stateA1_0=false.
rule2 :- stateA1_0.
rule3 :- stateA1_0.
rule4 :- stateA1_0=false.
rule5 :- start=false.
rule6 :- stateG2_0=false.
rule7 :- stateG2_0=false.
rule8 :- stateG2_0=false.
rule9 :- stateG2_0=false.
rule10 :- stateG2_0=false.
rule11 :- stateG2_0.
rule12 :- stateG2_0.
rule13 :- stateG2_0=false.
rule14 :- stateG3_0=false.
rule15 :- stateG3_0.
rule16 :- stateG3_0=false.
rule17 :- stateG3_0.
rule18 :- stateG3_0=false.
rule19 :- stateG3_0=false.
rule20 :- stateG3_0.
rule21 :- stateG3_0.
rule22 :- stateG3_0=false.
rule23 :- stateG3_0=false.
rule24 :- stateG3_0=false.
rule25 :-  not start=false.
rule26 :-  not start=false.
rule27 :-  not hgrant0.
rule27 :- hlocked=false.
rule28 :- hgrant0.
rule29 :-  not hready.
rule29 :- hgrant0<.
rule30 :-  not hready.
rule30 :- hlocked=false<.
rule31 :-  not decide=false.
rule31 :- hgrant0=false<.
rule32 :-  not decide=false.
rule32 :- hlocked=false<.
:- rule0,rule1,rule2,rule3,rule4,rule5,rule6,rule7,rule8,rule9,rule10,rule11,rule12,rule13,rule14,rule15,rule16,rule17,rule18,rule19,rule20,rule21,rule22,rule23,rule24,rule25,rule26,rule27,rule28,rule29,rule30,rule31,rule32.
#show decide /0.
#show hburst0 /0.
#show hburst1 /0.
#show hbusreq0 /0.
#show hgrant0 /0.
#show hlock0 /0.
#show hlocked /0.
#show hmaster0 /0.
#show hmastlock /0.
#show hready/0.
#show start /0.
#show stateA1_0 /0.
#show stateG2_0 /0.
#show stateG3_0 /0.
#show stateG3_1 /0.
#show stateG3_2 /0.
