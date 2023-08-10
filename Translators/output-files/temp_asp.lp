t0 :-  not parkResult_0.
st0 :- not t0.
:- st0.
t1 :-  not  not obstacle_0.
st1 :- not t1.
:- st1.
{obstacle_0}.
{parkCommand_0}.
{parkCommand_1}.
{parkResult_0}.
{responded_0}.
{sideSense_0}.
{spec_policy_0}.
{spec_policy_1}.
{spec_policy_2}.
{steer_0}.
{steer_1}.
{throttle_0}.
{throttle_1}.
{yBoolExpr_0}.
rule0 :- responded_0.
rule0 :-  not responded_0.
rule1 :-  not spec_policy_0, not spec_policy_1, not spec_policy_2.
rule1 :-  not spec_policy_0, not spec_policy_1,spec_policy_2.
rule1 :-  not spec_policy_0,spec_policy_1, not spec_policy_2.
rule2 :-  not spec_policy_0, not spec_policy_1, not spec_policy_2.
rule3 :- yBoolExpr_0.
rule3 :-  not yBoolExpr_0.
rule4 :-  not obstacle_0.
rule4 :- throttle_0, not throttle_1.
rule5 :-  not sideSense_0.
rule5 :-  not  not steer_0, not steer_1, not throttle_0, not throttle_1.
rule6 :-  not obstacle_0.
rule6 :-  not parkCommand_0,parkCommand_1.
rule7 :- spec_policy_0.
rule7 :- spec_policy_1.
rule7 :- spec_policy_2.
rule7 :- parkResult_0.
rule7 :-  not throttle_0.
rule7 :- throttle_1.
:- rule0,rule1,rule2,rule3,rule4,rule5,rule6,rule7.
#show obstacle_0/0.
#show parkCommand_0/0.
#show parkCommand_1/0.
#show parkResult_0/0.
#show responded_0/0.
#show sideSense_0/0.
#show spec_policy_0/0.
#show spec_policy_1/0.
#show spec_policy_2/0.
#show steer_0/0.
#show steer_1/0.
#show throttle_0/0.
#show throttle_1/0.
#show yBoolExpr_0/0.
