t0 :-  not parkResult_0 .
t0 :-  spec_policy_2.
st0 :- not t0.
:- st0.
t1 :- obstacle_0 .
t1 :-  throttle_1 .
t1 :-  sideSense_0 ,  not obstacle_0 .
t1 :-   not sideSense_0.
st1 :- not t1.
:- st1.
t2 :- eNV_CONSTRAINT_0_respondsTo_responded ,  not obstacle_0 .
t2 :-   not eNV_CONSTRAINT_0_respondsTo_responded , obstacle_0.
st2 :- not t2.
:- st2.
t3 :- pREV_aux_1 ,  not spec_policy_0 .
t3 :-   not pREV_aux_1 , spec_policy_0.
st3 :- not t3.
:- st3.
{eNV_CONSTRAINT_0_respondsTo_responded}.
{obstacle_0}.
{pREV_aux_1}.
{parkCommand_0}.
{parkCommand_1}.
{parkResult_0}.
{sideSense_0}.
{spec_policy_0}.
{spec_policy_1}.
{spec_policy_2}.
{steer_0}.
{steer_1}.
{throttle_0}.
{throttle_1}.
rule0 :- spec_policy_2 .
rule0 :-   not spec_policy_0 ,  not spec_policy_1 ,  not spec_policy_2 .
rule0 :-   not spec_policy_0 , spec_policy_1 ,  not spec_policy_2.
rule1 :-  not spec_policy_2 .
rule1 :-   not spec_policy_0 ,  not spec_policy_1 , spec_policy_2.
rule2 :- spec_policy_2.
rule3 :-  not spec_policy_2.
rule4 :- spec_policy_2.
rule5 :- spec_policy_2 .
rule5 :-   not spec_policy_0 ,  not spec_policy_1 ,  not spec_policy_2.
rule6 :- parkResult_0 .
rule6 :-  spec_policy_0 , spec_policy_0 , spec_policy_1 .
rule6 :-  spec_policy_2 ,  not spec_policy_1 .
rule6 :-   not spec_policy_2 .
rule6 :-   not spec_policy_0 ,  not spec_policy_2 .
rule6 :-  spec_policy_1 , spec_policy_2.
rule7 :- parkResult_0 .
rule7 :-   not spec_policy_0 ,  not spec_policy_1 , spec_policy_2.
rule8 :- parkResult_0 .
rule8 :-   not spec_policy_0 ,  not spec_policy_1 ,  not spec_policy_2.
rule9 :- parkResult_0 .
rule9 :-  spec_policy_0 , spec_policy_0 , spec_policy_1 .
rule9 :-  spec_policy_2 ,  not spec_policy_1 .
rule9 :-   not spec_policy_2 .
rule9 :-   not spec_policy_0 ,  not spec_policy_2 .
rule9 :-  spec_policy_1 , spec_policy_2.
rule10 :-  not parkResult_0 .
rule10 :-   not spec_policy_0 , spec_policy_1 ,  not spec_policy_2.
rule11 :- spec_policy_2.
rule12 :-  not spec_policy_2.
rule13 :- spec_policy_2.
rule14 :-  not spec_policy_2 .
rule14 :-  spec_policy_0 , spec_policy_0 , spec_policy_1 .
rule14 :-  spec_policy_2 ,  not spec_policy_1 .
rule14 :-   not spec_policy_2 .
rule14 :-   not spec_policy_0 ,  not spec_policy_2 .
rule14 :-  spec_policy_1 , spec_policy_2.
rule15 :-  not throttle_0 , throttle_1.
rule16 :-  not steer_0 , steer_1.
rule17 :-  not parkCommand_0 , parkCommand_1.
rule18 :-  not spec_policy_0 , spec_policy_1 ,  not spec_policy_2.
rule19 :-  not spec_policy_0 , spec_policy_1 , spec_policy_2.
rule20 :-  not obstacle_0 .
rule20 :-  throttle_0 ,  not throttle_1.
rule21 :-  not sideSense_0 .
rule21 :-  steer_0 ,  not steer_1 ,  not throttle_0 ,  not throttle_1.
rule22 :-  not obstacle_0 .
rule22 :-   not parkCommand_0 , parkCommand_1.
rule23 :- parkResult_0 .
rule23 :-  spec_policy_0 .
rule23 :-  spec_policy_1 .
rule23 :-  spec_policy_2 .
rule23 :-   not throttle_0 .
rule23 :-  throttle_1.
:- rule0,rule1,rule2,rule3,rule4,rule5,rule6,rule7,rule8,rule9,rule10,rule11,rule12,rule13,rule14,rule15,rule16,rule17,rule18,rule19,rule20,rule21,rule22,rule23.
#show eNV_CONSTRAINT_0_respondsTo_responded/0.
#show obstacle_0/0.
#show pREV_aux_1/0.
#show parkCommand_0/0.
#show parkCommand_1/0.
#show parkResult_0/0.
#show sideSense_0/0.
#show spec_policy_0/0.
#show spec_policy_1/0.
#show spec_policy_2/0.
#show steer_0/0.
#show steer_1/0.
#show throttle_0/0.
#show throttle_1/0.
