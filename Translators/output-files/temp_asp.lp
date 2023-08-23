t0 :-  not parkResult_0 .
t0 :-  spec_policy_2.
st0 :- not t0.
:- st0.
t1 :- throttle_2 .
t1 :-  obstacle_0 , obstacle_0 , sideSense_0 , sideSense_0 , sideSense_1 .
t1 :-  sideSense_2 ,  not sideSense_1 .
t1 :-   not sideSense_2 .
t1 :-   not sideSense_0 .
t1 :-   not sideSense_1 ,  not obstacle_0 .
t1 :-   not sideSense_0 ,  not sideSense_2 .
t1 :-  sideSense_1 , sideSense_2 .
t1 :-   not obstacle_0 ,  not obstacle_0 .
t1 :-   not sideSense_0 , sideSense_0 , sideSense_1 .
t1 :-  sideSense_2 ,  not sideSense_1 .
t1 :-   not sideSense_2 .
t1 :-  obstacle_0 , sideSense_0 ,  not sideSense_0 .
t1 :-   not sideSense_1 ,  not sideSense_2 .
t1 :-  sideSense_1 , sideSense_2.
st1 :- not t1.
:- st1.
t2 :- spec_policy_2 .
t2 :-   not colorSense_0 ,  not colorSense_1.
st2 :- not t2.
:- st2.
t3 :-  not sideSense_0 , sideSense_1 ,  not sideSense_2.
st3 :- not t3.
:- st3.
t4 :-  not sideSense_0 , sideSense_1 , sideSense_2.
st4 :- not t4.
:- st4.
t5 :-  not colorSense_0 , colorSense_1.
st5 :- not t5.
:- st5.
t6 :-  not command_0 ,  not command_1 , command_2 , command_3.
st6 :- not t6.
:- st6.
t7 :-  not command_0 , command_1 ,  not command_2 ,  not command_3.
st7 :- not t7.
:- st7.
t8 :-  not command_0 , command_1 ,  not command_2 , command_3.
st8 :- not t8.
:- st8.
t9 :-  not command_0 , command_1 , command_2 ,  not command_3.
st9 :- not t9.
:- st9.
t10 :-  not command_0 , command_1 , command_2 , command_3.
st10 :- not t10.
:- st10.
t11 :- eNV_CONSTRAINT_0_respondsTo_responded ,  not obstacle_0 .
t11 :-   not eNV_CONSTRAINT_0_respondsTo_responded , obstacle_0.
st11 :- not t11.
:- st11.
t12 :- obstacle_0 , pREV_aux_1 .
t12 :-   not obstacle_0 ,  not pREV_aux_1.
st12 :- not t12.
:- st12.
t13 :-  not obstacle_0 , pREV_aux_2 .
t13 :-  obstacle_0 ,  not pREV_aux_2.
st13 :- not t13.
:- st13.
t14 :- pREV_aux_3 ,  not sideSense_0 .
t14 :-   not pREV_aux_3 , sideSense_0.
st14 :- not t14.
:- st14.
t15 :- pREV_aux_4 ,  not sideSense_0 .
t15 :-   not pREV_aux_4 , sideSense_0.
st15 :- not t15.
:- st15.
t16 :- pREV_aux_5 ,  not sideSense_0 .
t16 :-   not pREV_aux_5 , sideSense_0.
st16 :- not t16.
:- st16.
t17 :- pREV_aux_6 , sideSense_0 .
t17 :-   not pREV_aux_6 ,  not sideSense_0.
st17 :- not t17.
:- st17.
t18 :- pREV_aux_7 ,  not sideSense_0 .
t18 :-   not pREV_aux_7 , sideSense_0.
st18 :- not t18.
:- st18.
t19 :- pREV_aux_8 , sideSense_0 .
t19 :-   not pREV_aux_8 ,  not sideSense_0.
st19 :- not t19.
:- st19.
t20 :- pREV_aux_9 ,  not spec_policy_0 .
t20 :-   not pREV_aux_9 , spec_policy_0.
st20 :- not t20.
:- st20.
{colorSense_0}.
{colorSense_1}.
{command_0}.
{command_1}.
{command_2}.
{command_3}.
{eNV_CONSTRAINT_0_respondsTo_responded}.
{obstacle_0}.
{pREV_aux_1}.
{pREV_aux_2}.
{pREV_aux_3}.
{pREV_aux_4}.
{pREV_aux_5}.
{pREV_aux_6}.
{pREV_aux_7}.
{pREV_aux_8}.
{pREV_aux_9}.
{parkCommand_0}.
{parkCommand_1}.
{parkResult_0}.
{reset_0}.
{sideSense_0}.
{sideSense_1}.
{sideSense_2}.
{spec_policy_0}.
{spec_policy_1}.
{spec_policy_2}.
{steer_0}.
{steer_1}.
{steer_2}.
{throttle_0}.
{throttle_1}.
{throttle_2}.
rule0 :- spec_policy_2 .
rule0 :-   not spec_policy_0 ,  not spec_policy_1 ,  not spec_policy_2 .
rule0 :-   not spec_policy_0 , spec_policy_1 ,  not spec_policy_2.
rule1 :-  not spec_policy_2 .
rule1 :-   not spec_policy_0 ,  not spec_policy_1 , spec_policy_2.
rule2 :- spec_policy_2.
rule3 :-  not spec_policy_2.
rule4 :- spec_policy_2.
rule5 :-  not spec_policy_2 .
rule5 :-  spec_policy_0 ,  not spec_policy_1 , spec_policy_2.
rule6 :- spec_policy_2.
rule7 :-  not spec_policy_2.
rule8 :- command_3 .
rule8 :-   not spec_policy_0 ,  not spec_policy_1 ,  not spec_policy_2.
rule9 :- sideSense_2 .
rule9 :-  spec_policy_0 , spec_policy_0 , spec_policy_1 .
rule9 :-  spec_policy_2 ,  not spec_policy_1 .
rule9 :-   not spec_policy_2 .
rule9 :-   not spec_policy_0 ,  not spec_policy_2 .
rule9 :-  spec_policy_1 , spec_policy_2.
rule10 :- command_3 .
rule10 :-   not spec_policy_0 ,  not spec_policy_1 , spec_policy_2.
rule11 :- parkResult_0 .
rule11 :-   not spec_policy_0 ,  not spec_policy_1 ,  not spec_policy_2.
rule12 :- command_3 .
rule12 :-  spec_policy_0 , spec_policy_0 , spec_policy_1 .
rule12 :-  spec_policy_2 ,  not spec_policy_1 .
rule12 :-   not spec_policy_2 .
rule12 :-   not spec_policy_0 ,  not spec_policy_2 .
rule12 :-  spec_policy_1 , spec_policy_2.
rule13 :- command_3 .
rule13 :-   not spec_policy_0 , spec_policy_1 ,  not spec_policy_2.
rule14 :- command_3 .
rule14 :-   not spec_policy_0 , spec_policy_1 , spec_policy_2.
rule15 :- command_3 .
rule15 :-  spec_policy_0 ,  not spec_policy_1 ,  not spec_policy_2.
rule16 :- command_3 .
rule16 :-  spec_policy_0 ,  not spec_policy_1 , spec_policy_2.
rule17 :- command_3 .
rule17 :-  spec_policy_0 , spec_policy_0 , spec_policy_1 .
rule17 :-  spec_policy_2 ,  not spec_policy_1 .
rule17 :-   not spec_policy_2 .
rule17 :-   not spec_policy_0 ,  not spec_policy_2 .
rule17 :-  spec_policy_1 , spec_policy_2.
rule18 :- command_3 .
rule18 :-  spec_policy_0 , spec_policy_1 ,  not spec_policy_2.
rule19 :- command_3 .
rule19 :-  spec_policy_0 , spec_policy_1 , spec_policy_2.
rule20 :- command_3 .
rule20 :-   not spec_policy_0 ,  not spec_policy_1 ,  not spec_policy_2.
rule21 :-  not throttle_0 , throttle_1 ,  not throttle_2.
rule22 :-  not throttle_0 , throttle_1 , throttle_2.
rule23 :-  not steer_0 ,  not steer_1 , steer_2.
rule24 :-  not steer_0 , steer_1 ,  not steer_2.
rule25 :-  not steer_0 , steer_1 , steer_2.
rule26 :-  not parkCommand_0 , parkCommand_1.
rule27 :- command_0 .
rule27 :-  command_1 .
rule27 :-  command_2 .
rule27 :-   not command_3 .
rule27 :-   not steer_0 , steer_1 ,  not steer_2 ,  not throttle_0 , throttle_1 ,  not throttle_2.
rule28 :- command_0 .
rule28 :-  command_1 .
rule28 :-   not command_2 .
rule28 :-  command_3 .
rule28 :-   not steer_0 , steer_1 ,  not steer_2 ,  not throttle_0 ,  not throttle_1 ,  not throttle_2.
rule29 :- command_0 .
rule29 :-  command_1 .
rule29 :-   not command_2 .
rule29 :-   not command_3 .
rule29 :-   not steer_0 , steer_1 ,  not steer_2 ,  not throttle_0 ,  not throttle_1 , throttle_2.
rule30 :-  not command_0 .
rule30 :-  command_1 .
rule30 :-  command_2 .
rule30 :-  command_3 .
rule30 :-   not steer_0 ,  not steer_1 ,  not steer_2 ,  not throttle_0 , throttle_1 ,  not throttle_2.
rule31 :-  not command_0 .
rule31 :-  command_1 .
rule31 :-  command_2 .
rule31 :-   not command_3 .
rule31 :-   not steer_0 ,  not steer_1 , steer_2 ,  not throttle_0 , throttle_1 ,  not throttle_2.
rule32 :-  not command_0 .
rule32 :-  command_1 .
rule32 :-   not command_2 .
rule32 :-  command_3 .
rule32 :-   not steer_0 , steer_1 ,  not steer_2 ,  not throttle_0 , throttle_1 ,  not throttle_2.
rule33 :- command_0 .
rule33 :-   not command_1 .
rule33 :-  command_2 .
rule33 :-   not command_3 .
rule33 :-   not steer_0 ,  not steer_1 , steer_2 ,  not throttle_0 ,  not throttle_1 ,  not throttle_2.
rule34 :- command_0 .
rule34 :-   not command_1 .
rule34 :-  command_2 .
rule34 :-  command_3 .
rule34 :-   not steer_0 ,  not steer_1 ,  not steer_2 ,  not throttle_0 ,  not throttle_1 ,  not throttle_2.
rule35 :- command_0 .
rule35 :-   not command_1 .
rule35 :-   not command_2 .
rule35 :-  command_3 .
rule35 :-   not steer_0 ,  not steer_1 , steer_2 ,  not throttle_0 ,  not throttle_1 , throttle_2.
rule36 :- command_0 .
rule36 :-   not command_1 .
rule36 :-   not command_2 .
rule36 :-   not command_3 .
rule36 :-   not steer_0 ,  not steer_1 ,  not steer_2 ,  not throttle_0 ,  not throttle_1 , throttle_2.
rule37 :- command_0 .
rule37 :-  command_1 .
rule37 :-  command_2 .
rule37 :-  command_3 .
rule37 :-  spec_policy_0 .
rule37 :-  spec_policy_1 .
rule37 :-  spec_policy_2 .
rule37 :-   not throttle_0 ,  not throttle_1 ,  not throttle_2 .
rule37 :-   not throttle_0 , throttle_1 ,  not throttle_2 .
rule37 :-   not throttle_0 ,  not throttle_1 , throttle_2.
rule38 :- command_0 .
rule38 :-  command_1 .
rule38 :-  command_2 .
rule38 :-  command_3 .
rule38 :-  obstacle_0 .
rule38 :-  spec_policy_0 .
rule38 :-  spec_policy_1 .
rule38 :-  spec_policy_2 .
rule38 :-  steer_0 ,  not steer_1 ,  not steer_2 .
rule38 :-   not steer_0 ,  not steer_1 , steer_2.
rule39 :- command_0 .
rule39 :-  command_1 .
rule39 :-  command_2 .
rule39 :-  command_3 .
rule39 :-  spec_policy_0 .
rule39 :-  spec_policy_1 .
rule39 :-   not spec_policy_2 .
rule39 :-  throttle_0 .
rule39 :-   not throttle_1 .
rule39 :-  parkCommand_0 ,  not throttle_2 .
rule39 :-  parkCommand_1 ,  not steer_0 , steer_1 ,  not steer_2 .
rule39 :-  steer_0 ,  not steer_1 ,  not steer_2 .
rule39 :-   not steer_0 , steer_1 , steer_2.
rule40 :- command_0 .
rule40 :-  command_1 .
rule40 :-  command_2 .
rule40 :-  command_3 .
rule40 :-  obstacle_0 .
rule40 :-  parkResult_0 .
rule40 :-  spec_policy_0 .
rule40 :-  spec_policy_1 .
rule40 :-  spec_policy_2 .
rule40 :-   not throttle_0 ,  not throttle_1 ,  not throttle_2.
rule41 :-  not obstacle_0 .
rule41 :-   not parkCommand_0 , parkCommand_1.
rule42 :- command_0 .
rule42 :-  command_1 .
rule42 :-  command_2 .
rule42 :-  command_3 .
rule42 :-  parkResult_0 .
rule42 :-  spec_policy_0 .
rule42 :-  spec_policy_1 .
rule42 :-  spec_policy_2 .
rule42 :-  throttle_0 .
rule42 :-   not throttle_1 .
rule42 :-  throttle_2.
rule43 :- command_0 .
rule43 :-  command_1 .
rule43 :-  command_2 .
rule43 :-  command_3 .
rule43 :-  obstacle_0 .
rule43 :-   not pREV_aux_1 .
rule43 :-  spec_policy_0 .
rule43 :-  spec_policy_1 .
rule43 :-  spec_policy_2 .
rule43 :-   not steer_0 , steer_1 ,  not steer_2.
rule44 :- command_0 .
rule44 :-  command_1 .
rule44 :-  command_2 .
rule44 :-  command_3 .
rule44 :-  obstacle_0 .
rule44 :-   not pREV_aux_2 .
rule44 :-  sideSense_0 .
rule44 :-  sideSense_1 .
rule44 :-  sideSense_2 .
rule44 :-  spec_policy_0 .
rule44 :-  spec_policy_1 .
rule44 :-  spec_policy_2 .
rule44 :-  steer_0 ,  not steer_1 ,  not steer_2.
rule45 :- command_0 .
rule45 :-  command_1 .
rule45 :-  command_2 .
rule45 :-  command_3 .
rule45 :-  obstacle_0 .
rule45 :-   not pREV_aux_2 .
rule45 :-  sideSense_0 .
rule45 :-   not sideSense_1 .
rule45 :-  sideSense_2 .
rule45 :-  spec_policy_0 .
rule45 :-  spec_policy_1 .
rule45 :-  spec_policy_2 .
rule45 :-   not steer_0 , steer_1 , steer_2.
rule46 :- command_0 .
rule46 :-  command_1 .
rule46 :-  command_2 .
rule46 :-  command_3 .
rule46 :-  obstacle_0 .
rule46 :-   not pREV_aux_2 .
rule46 :-   not pREV_aux_3 .
rule46 :-  sideSense_0 .
rule46 :-  sideSense_1 .
rule46 :-   not sideSense_2 .
rule46 :-  spec_policy_0 .
rule46 :-  spec_policy_1 .
rule46 :-  spec_policy_2 .
rule46 :-   not steer_0 , steer_1 ,  not steer_2.
rule47 :- command_0 .
rule47 :-  command_1 .
rule47 :-  command_2 .
rule47 :-  command_3 .
rule47 :-  obstacle_0 .
rule47 :-   not pREV_aux_2 .
rule47 :-   not pREV_aux_4 .
rule47 :-  sideSense_0 .
rule47 :-  sideSense_1 .
rule47 :-   not sideSense_2 .
rule47 :-  spec_policy_0 .
rule47 :-  spec_policy_1 .
rule47 :-  spec_policy_2 .
rule47 :-  steer_0 ,  not steer_1 ,  not steer_2.
rule48 :- command_0 .
rule48 :-  command_1 .
rule48 :-  command_2 .
rule48 :-  command_3 .
rule48 :-  obstacle_0 .
rule48 :-   not pREV_aux_2 .
rule48 :-   not pREV_aux_5 .
rule48 :-  sideSense_0 .
rule48 :-  sideSense_1 .
rule48 :-   not sideSense_2 .
rule48 :-  spec_policy_0 .
rule48 :-  spec_policy_1 .
rule48 :-  spec_policy_2 .
rule48 :-   not steer_0 , steer_1 , steer_2.
rule49 :- command_0 .
rule49 :-  command_1 .
rule49 :-  command_2 .
rule49 :-  command_3 .
rule49 :-  obstacle_0 .
rule49 :-  sideSense_0 .
rule49 :-   not sideSense_1 .
rule49 :-   not sideSense_2 .
rule49 :-  spec_policy_0 .
rule49 :-  spec_policy_1 .
rule49 :-   not spec_policy_2 .
rule49 :-  steer_0 ,  not steer_1 ,  not steer_2.
rule50 :- command_0 .
rule50 :-  command_1 .
rule50 :-  command_2 .
rule50 :-  command_3 .
rule50 :-  obstacle_0 .
rule50 :-   not sideSense_0 .
rule50 :-  sideSense_1 .
rule50 :-   not sideSense_2 .
rule50 :-  spec_policy_0 .
rule50 :-  spec_policy_1 .
rule50 :-   not spec_policy_2 .
rule50 :-   not steer_0 , steer_1 , steer_2.
rule51 :- command_0 .
rule51 :-  command_1 .
rule51 :-  command_2 .
rule51 :-  command_3 .
rule51 :-  obstacle_0 .
rule51 :-   not pREV_aux_6 .
rule51 :-   not sideSense_0 .
rule51 :-  sideSense_1 .
rule51 :-  sideSense_2 .
rule51 :-  spec_policy_0 .
rule51 :-  spec_policy_1 .
rule51 :-   not spec_policy_2 .
rule51 :-   not steer_0 , steer_1 ,  not steer_2.
rule52 :- command_0 .
rule52 :-  command_1 .
rule52 :-  command_2 .
rule52 :-  command_3 .
rule52 :-  obstacle_0 .
rule52 :-   not pREV_aux_7 .
rule52 :-   not sideSense_0 .
rule52 :-  sideSense_1 .
rule52 :-  sideSense_2 .
rule52 :-  spec_policy_0 .
rule52 :-  spec_policy_1 .
rule52 :-   not spec_policy_2 .
rule52 :-   not steer_0 , steer_1 , steer_2.
rule53 :- command_0 .
rule53 :-  command_1 .
rule53 :-  command_2 .
rule53 :-  command_3 .
rule53 :-  obstacle_0 .
rule53 :-   not pREV_aux_8 .
rule53 :-   not sideSense_0 .
rule53 :-  sideSense_1 .
rule53 :-  sideSense_2 .
rule53 :-  spec_policy_0 .
rule53 :-  spec_policy_1 .
rule53 :-   not spec_policy_2 .
rule53 :-  steer_0 ,  not steer_1 ,  not steer_2.
:- rule0,rule1,rule2,rule3,rule4,rule5,rule6,rule7,rule8,rule9,rule10,rule11,rule12,rule13,rule14,rule15,rule16,rule17,rule18,rule19,rule20,rule21,rule22,rule23,rule24,rule25,rule26,rule27,rule28,rule29,rule30,rule31,rule32,rule33,rule34,rule35,rule36,rule37,rule38,rule39,rule40,rule41,rule42,rule43,rule44,rule45,rule46,rule47,rule48,rule49,rule50,rule51,rule52,rule53.
#show colorSense_0/0.
#show colorSense_1/0.
#show command_0/0.
#show command_1/0.
#show command_2/0.
#show command_3/0.
#show eNV_CONSTRAINT_0_respondsTo_responded/0.
#show obstacle_0/0.
#show pREV_aux_1/0.
#show pREV_aux_2/0.
#show pREV_aux_3/0.
#show pREV_aux_4/0.
#show pREV_aux_5/0.
#show pREV_aux_6/0.
#show pREV_aux_7/0.
#show pREV_aux_8/0.
#show pREV_aux_9/0.
#show parkCommand_0/0.
#show parkCommand_1/0.
#show parkResult_0/0.
#show reset_0/0.
#show sideSense_0/0.
#show sideSense_1/0.
#show sideSense_2/0.
#show spec_policy_0/0.
#show spec_policy_1/0.
#show spec_policy_2/0.
#show steer_0/0.
#show steer_1/0.
#show steer_2/0.
#show throttle_0/0.
#show throttle_1/0.
#show throttle_2/0.
