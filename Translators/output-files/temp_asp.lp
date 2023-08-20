t0 :- sYS_CONSTRAINT_0_respondsTo_responded , heading_0 , heading_1 , spec_nextHead_0 , spec_nextHead_1 .
t0 :-   not spec_nextHead_1 ,  not heading_1 .
t0 :-   not spec_nextHead_0 .
t0 :-   not heading_0 , spec_nextHead_1 ,  not heading_1 .
t0 :-   not spec_nextHead_0 .
t0 :-  heading_1 , spec_nextHead_0 ,  not spec_nextHead_1 .
t0 :-   not sYS_CONSTRAINT_0_respondsTo_responded , heading_0 , spec_nextHead_1 ,  not heading_1 .
t0 :-   not spec_nextHead_0 .
t0 :-  heading_1 , spec_nextHead_0 ,  not spec_nextHead_1 .
t0 :-   not heading_0 , heading_1 , spec_nextHead_0 , spec_nextHead_1 .
t0 :-   not spec_nextHead_1 ,  not heading_1 .
t0 :-   not spec_nextHead_0.
st0 :- not t0.
:- st0.
t1 :- eNV_CONSTRAINT_1_respondsTo_responded , heading_0 , heading_1 , spec_nextHead_0 , spec_nextHead_1 .
t1 :-  spec_nextMoveMode_1 .
t1 :-   not spec_nextMoveMode_0 ,  not spec_nextMoveMode_1 .
t1 :-   not spec_nextHead_1 ,  not spec_nextMoveMode_1 , spec_nextMoveMode_0 .
t1 :-  spec_nextMoveMode_1 ,  not heading_1 .
t1 :-   not spec_nextHead_0 .
t1 :-   not heading_0 ,  not heading_1 .
t1 :-   not spec_nextHead_0 , spec_nextHead_1 .
t1 :-  spec_nextMoveMode_1 .
t1 :-   not spec_nextMoveMode_0 ,  not spec_nextMoveMode_1 .
t1 :-  heading_1 , spec_nextHead_0 ,  not spec_nextHead_1 ,  not spec_nextMoveMode_1 , spec_nextMoveMode_0 .
t1 :-  spec_nextMoveMode_1 .
t1 :-   not eNV_CONSTRAINT_1_respondsTo_responded , heading_0 ,  not heading_1 .
t1 :-   not spec_nextHead_0 , spec_nextHead_1 .
t1 :-  spec_nextMoveMode_1 .
t1 :-   not spec_nextMoveMode_0 ,  not spec_nextMoveMode_1 .
t1 :-  heading_1 , spec_nextHead_0 ,  not spec_nextHead_1 ,  not spec_nextMoveMode_1 , spec_nextMoveMode_0 .
t1 :-  spec_nextMoveMode_1 .
t1 :-   not heading_0 , heading_1 , spec_nextHead_0 , spec_nextHead_1 .
t1 :-  spec_nextMoveMode_1 .
t1 :-   not spec_nextMoveMode_0 ,  not spec_nextMoveMode_1 .
t1 :-   not spec_nextHead_1 ,  not spec_nextMoveMode_1 , spec_nextMoveMode_0 .
t1 :-  spec_nextMoveMode_1 ,  not heading_1 .
t1 :-   not spec_nextHead_0.
st1 :- not t1.
:- st1.
t2 :- eNV_CONSTRAINT_2_respondsTo_responded , heading_0 , heading_1 , spec_nextHead_0 , spec_nextHead_1 .
t2 :-   not spec_nextMoveMode_1 .
t2 :-   not spec_nextMoveMode_0 , spec_nextMoveMode_1 .
t2 :-   not spec_nextHead_1 , spec_nextMoveMode_1 , spec_nextMoveMode_0 .
t2 :-   not spec_nextMoveMode_1 ,  not heading_1 .
t2 :-   not spec_nextHead_0 .
t2 :-   not heading_0 ,  not heading_1 .
t2 :-   not spec_nextHead_0 , spec_nextHead_1 .
t2 :-   not spec_nextMoveMode_1 .
t2 :-   not spec_nextMoveMode_0 , spec_nextMoveMode_1 .
t2 :-  heading_1 , spec_nextHead_0 ,  not spec_nextHead_1 , spec_nextMoveMode_1 , spec_nextMoveMode_0 .
t2 :-   not spec_nextMoveMode_1 .
t2 :-   not eNV_CONSTRAINT_2_respondsTo_responded , heading_0 ,  not heading_1 .
t2 :-   not spec_nextHead_0 , spec_nextHead_1 .
t2 :-   not spec_nextMoveMode_1 .
t2 :-   not spec_nextMoveMode_0 , spec_nextMoveMode_1 .
t2 :-  heading_1 , spec_nextHead_0 ,  not spec_nextHead_1 , spec_nextMoveMode_1 , spec_nextMoveMode_0 .
t2 :-   not spec_nextMoveMode_1 .
t2 :-   not heading_0 , heading_1 , spec_nextHead_0 , spec_nextHead_1 .
t2 :-   not spec_nextMoveMode_1 .
t2 :-   not spec_nextMoveMode_0 , spec_nextMoveMode_1 .
t2 :-   not spec_nextHead_1 , spec_nextMoveMode_1 , spec_nextMoveMode_0 .
t2 :-   not spec_nextMoveMode_1 ,  not heading_1 .
t2 :-   not spec_nextHead_0.
st2 :- not t2.
:- st2.
t3 :- pREV_aux_3 ,  not spec_nextMoveMode_0 ,  not spec_nextMoveMode_1 .
t3 :-   not pREV_aux_3 , spec_nextMoveMode_0 .
t3 :-  spec_nextMoveMode_1.
st3 :- not t3.
:- st3.
t4 :- pREV_aux_4 , spec_nextMoveMode_0 ,  not spec_nextMoveMode_1 .
t4 :-   not pREV_aux_4 ,  not spec_nextMoveMode_0 .
t4 :-  spec_nextMoveMode_1.
st4 :- not t4.
:- st4.
t5 :- pREV_aux_4 , pREV_aux_5 .
t5 :-   not pREV_aux_4 ,  not pREV_aux_5.
st5 :- not t5.
:- st5.
t6 :- pREV_aux_6 , spec_nextMoveMode_0 , spec_nextMoveMode_1 .
t6 :-   not pREV_aux_6 ,  not spec_nextMoveMode_0 .
t6 :-   not spec_nextMoveMode_1.
st6 :- not t6.
:- st6.
t7 :- pREV_aux_6 , pREV_aux_7 .
t7 :-   not pREV_aux_6 ,  not pREV_aux_7.
st7 :- not t7.
:- st7.
t8 :- pREV_aux_8 ,  not spec_nextMoveMode_0 , spec_nextMoveMode_1 .
t8 :-   not pREV_aux_8 , spec_nextMoveMode_0 .
t8 :-   not spec_nextMoveMode_1.
st8 :- not t8.
:- st8.
{button_0}.
{eNV_CONSTRAINT_1_respondsTo_responded}.
{eNV_CONSTRAINT_2_respondsTo_responded}.
{headMotor_0}.
{headMotor_1}.
{heading_0}.
{heading_1}.
{leftMotor_0}.
{leftMotor_1}.
{leftMotor_2}.
{leftMotor_3}.
{noise_0}.
{obstacle_0}.
{pREV_aux_3}.
{pREV_aux_4}.
{pREV_aux_5}.
{pREV_aux_6}.
{pREV_aux_7}.
{pREV_aux_8}.
{rightMotor_0}.
{rightMotor_1}.
{rightMotor_2}.
{rightMotor_3}.
{sYS_CONSTRAINT_0_respondsTo_responded}.
{spec_nextHead_0}.
{spec_nextHead_1}.
{spec_nextMoveMode_0}.
{spec_nextMoveMode_1}.
{spec_specState_0}.
{spec_specState_1}.
{spec_turnState_0}.
{spec_turnState_1}.
rule0 :- leftMotor_0 .
rule0 :-  leftMotor_1 .
rule0 :-  leftMotor_2 .
rule0 :-  leftMotor_3 .
rule0 :-  rightMotor_0 .
rule0 :-  rightMotor_1 .
rule0 :-  rightMotor_2 .
rule0 :-   not rightMotor_3.
rule1 :- leftMotor_0 .
rule1 :-  leftMotor_1 .
rule1 :-  leftMotor_2 .
rule1 :-   not leftMotor_3 .
rule1 :-  rightMotor_0 .
rule1 :-  rightMotor_1 .
rule1 :-  rightMotor_2 .
rule1 :-  rightMotor_3.
rule2 :- spec_nextMoveMode_0 .
rule2 :-   not spec_nextMoveMode_1 .
rule2 :-   not spec_specState_0 , spec_specState_1.
rule3 :- spec_nextMoveMode_0 .
rule3 :-  spec_nextMoveMode_1 .
rule3 :-  spec_specState_0 ,  not spec_specState_1.
rule4 :-  not spec_specState_0 ,  not spec_specState_1 .
rule4 :-   not spec_nextMoveMode_0 .
rule4 :-  spec_nextMoveMode_1 ,  not spec_nextMoveMode_0 .
rule4 :-   not spec_nextMoveMode_1.
rule5 :-  not button_0 .
rule5 :-  spec_nextHead_0 , heading_0 , heading_1 , spec_nextHead_1 .
rule5 :-   not heading_1 ,  not heading_0 .
rule5 :-   not spec_nextHead_1 .
rule5 :-   not spec_nextHead_0 , heading_1 ,  not heading_0 .
rule5 :-   not spec_nextHead_1 .
rule5 :-  heading_0 ,  not heading_1 , spec_nextHead_1.
rule6 :- button_0 .
rule6 :-  spec_nextHead_0 .
rule6 :-  spec_nextHead_1 ,  not spec_nextHead_0 .
rule6 :-   not spec_nextHead_1.
rule7 :-  not spec_turnState_0 ,  not spec_turnState_1 .
rule7 :-  spec_nextMoveMode_0 .
rule7 :-  spec_nextMoveMode_1 ,  not spec_nextMoveMode_0 .
rule7 :-   not spec_nextMoveMode_1.
rule8 :-  not spec_turnState_0 , spec_turnState_1 .
rule8 :-   not spec_nextMoveMode_0 .
rule8 :-  spec_nextMoveMode_1 ,  not spec_nextMoveMode_0 .
rule8 :-   not spec_nextMoveMode_1 .
rule8 :-  spec_turnState_1.
rule9 :-  not spec_turnState_1 .
rule9 :-  spec_nextMoveMode_0 , spec_nextMoveMode_1.
rule10 :-  not spec_turnState_0 , spec_turnState_1 .
rule10 :-   not spec_nextMoveMode_0 .
rule10 :-  spec_nextMoveMode_1 ,  not spec_nextMoveMode_0 .
rule10 :-   not spec_nextMoveMode_1.
rule11 :- spec_nextMoveMode_0 .
rule11 :-  spec_nextMoveMode_1 .
rule11 :-  spec_turnState_0 , spec_turnState_1.
rule12 :-  not spec_turnState_1.
rule13 :-  not leftMotor_0 , spec_nextMoveMode_0 ,  not spec_nextMoveMode_1 ,  not spec_turnState_0 , spec_turnState_1 .
rule13 :-  leftMotor_0 ,  not spec_nextMoveMode_0 .
rule13 :-  spec_nextMoveMode_1 .
rule13 :-  spec_turnState_0 .
rule13 :-   not spec_turnState_1.
rule14 :-  not leftMotor_0 , spec_nextMoveMode_0 , spec_nextMoveMode_1 ,  not spec_turnState_0 , spec_turnState_1 .
rule14 :-  leftMotor_0 ,  not spec_nextMoveMode_0 .
rule14 :-   not spec_nextMoveMode_1 .
rule14 :-  spec_turnState_0 .
rule14 :-   not spec_turnState_1.
rule15 :-  not leftMotor_0 , spec_turnState_0 ,  not spec_turnState_1 .
rule15 :-  leftMotor_0 ,  not spec_turnState_0 .
rule15 :-  spec_turnState_1.
rule16 :-  not spec_turnState_0 ,  not spec_turnState_1.
rule17 :-  not spec_turnState_0 ,  not spec_turnState_1.
rule18 :-  not leftMotor_0 ,  not leftMotor_1 ,  not leftMotor_2 , leftMotor_3.
rule19 :-  not leftMotor_0 ,  not leftMotor_1 , leftMotor_2 ,  not leftMotor_3.
rule20 :-  not leftMotor_0 ,  not leftMotor_1 , leftMotor_2 , leftMotor_3.
rule21 :-  not leftMotor_0 , leftMotor_1 ,  not leftMotor_2 ,  not leftMotor_3.
rule22 :-  not leftMotor_0 , leftMotor_1 ,  not leftMotor_2 , leftMotor_3.
rule23 :-  not leftMotor_0 , leftMotor_1 , leftMotor_2 ,  not leftMotor_3.
rule24 :-  not leftMotor_0 , leftMotor_1 , leftMotor_2 , leftMotor_3.
rule25 :-  not rightMotor_0 ,  not rightMotor_1 ,  not rightMotor_2 , rightMotor_3.
rule26 :-  not rightMotor_0 ,  not rightMotor_1 , rightMotor_2 ,  not rightMotor_3.
rule27 :-  not rightMotor_0 ,  not rightMotor_1 , rightMotor_2 , rightMotor_3.
rule28 :-  not rightMotor_0 , rightMotor_1 ,  not rightMotor_2 ,  not rightMotor_3.
rule29 :-  not rightMotor_0 , rightMotor_1 ,  not rightMotor_2 , rightMotor_3.
rule30 :-  not rightMotor_0 , rightMotor_1 , rightMotor_2 ,  not rightMotor_3.
rule31 :-  not rightMotor_0 , rightMotor_1 , rightMotor_2 , rightMotor_3.
rule32 :-  not headMotor_0 , headMotor_1.
rule33 :-  not obstacle_0 .
rule33 :-  spec_nextMoveMode_0 ,  not spec_nextMoveMode_1.
rule34 :-  not spec_nextMoveMode_0 .
rule34 :-  spec_nextMoveMode_1 .
rule34 :-  heading_0 .
rule34 :-   not heading_1 .
rule34 :-  spec_nextHead_0 .
rule34 :-  spec_nextHead_1 ,  not heading_0 .
rule34 :-  heading_1 .
rule34 :-  spec_nextHead_0 .
rule34 :-   not spec_nextHead_1 ,  not heading_0 .
rule34 :-   not heading_1 .
rule34 :-   not spec_nextHead_0 .
rule34 :-  spec_nextHead_1 , heading_0 .
rule34 :-  heading_1 .
rule34 :-   not spec_nextHead_0 .
rule34 :-   not spec_nextHead_1 .
rule34 :-  spec_turnState_0 .
rule34 :-  spec_turnState_1.
rule35 :-  not spec_nextMoveMode_0 .
rule35 :-   not spec_nextMoveMode_1 .
rule35 :-  heading_0 .
rule35 :-  heading_1 .
rule35 :-  spec_nextHead_0 .
rule35 :-   not spec_nextHead_1 , heading_0 .
rule35 :-   not heading_1 .
rule35 :-   not spec_nextHead_0 .
rule35 :-  spec_nextHead_1 ,  not heading_0 .
rule35 :-  heading_1 .
rule35 :-   not spec_nextHead_0 .
rule35 :-   not spec_nextHead_1 ,  not heading_0 .
rule35 :-   not heading_1 .
rule35 :-  spec_nextHead_0 .
rule35 :-  spec_nextHead_1 .
rule35 :-  spec_turnState_0 .
rule35 :-  spec_turnState_1.
rule36 :-  not leftMotor_0 ,  not leftMotor_1 ,  not leftMotor_2 , leftMotor_3 ,  not rightMotor_0 , rightMotor_1 ,  not rightMotor_2 ,  not rightMotor_3 , spec_turnState_0 ,  not spec_turnState_1 .
rule36 :-  leftMotor_0 .
rule36 :-  leftMotor_1 .
rule36 :-  leftMotor_2 .
rule36 :-   not leftMotor_3 .
rule36 :-  rightMotor_0 .
rule36 :-   not rightMotor_1 .
rule36 :-  rightMotor_2 .
rule36 :-  rightMotor_3 ,  not spec_turnState_0 .
rule36 :-  spec_turnState_1.
:- rule0,rule1,rule2,rule3,rule4,rule5,rule6,rule7,rule8,rule9,rule10,rule11,rule12,rule13,rule14,rule15,rule16,rule17,rule18,rule19,rule20,rule21,rule22,rule23,rule24,rule25,rule26,rule27,rule28,rule29,rule30,rule31,rule32,rule33,rule34,rule35,rule36.
#show button_0/0.
#show eNV_CONSTRAINT_1_respondsTo_responded/0.
#show eNV_CONSTRAINT_2_respondsTo_responded/0.
#show headMotor_0/0.
#show headMotor_1/0.
#show heading_0/0.
#show heading_1/0.
#show leftMotor_0/0.
#show leftMotor_1/0.
#show leftMotor_2/0.
#show leftMotor_3/0.
#show noise_0/0.
#show obstacle_0/0.
#show pREV_aux_3/0.
#show pREV_aux_4/0.
#show pREV_aux_5/0.
#show pREV_aux_6/0.
#show pREV_aux_7/0.
#show pREV_aux_8/0.
#show rightMotor_0/0.
#show rightMotor_1/0.
#show rightMotor_2/0.
#show rightMotor_3/0.
#show sYS_CONSTRAINT_0_respondsTo_responded/0.
#show spec_nextHead_0/0.
#show spec_nextHead_1/0.
#show spec_nextMoveMode_0/0.
#show spec_nextMoveMode_1/0.
#show spec_specState_0/0.
#show spec_specState_1/0.
#show spec_turnState_0/0.
#show spec_turnState_1/0.
