t0 :-  not color_0 , color_1 ,  not color_2.
st0 :- not t0.
:- st0.
t1 :-  not color_0 , color_1 , color_2.
st1 :- not t1.
:- st1.
t2 :-  not detect_0 , detect_1 ,  not detect_2.
st2 :- not t2.
:- st2.
t3 :-  not detect_0 , detect_1 , detect_2.
st3 :- not t3.
:- st3.
t4 :-  not horMot_0 , sYS_CONSTRAINT_0_respondsTo_responded .
t4 :-  horMot_0 ,  not sYS_CONSTRAINT_0_respondsTo_responded.
st4 :- not t4.
:- st4.
t5 :- ack_ver_0 , eNV_CONSTRAINT_1_respondsTo_responded .
t5 :-   not ack_ver_0 ,  not eNV_CONSTRAINT_1_respondsTo_responded.
st5 :- not t5.
:- st5.
t6 :- ack_hor_0 , eNV_CONSTRAINT_2_respondsTo_responded .
t6 :-   not ack_hor_0 ,  not eNV_CONSTRAINT_2_respondsTo_responded.
st6 :- not t6.
:- st6.
t7 :- pREV_aux_3 , speedButton_0 .
t7 :-   not pREV_aux_3 ,  not speedButton_0.
st7 :- not t7.
:- st7.
t8 :- ack_hor_0 .
t8 :-  verMot_0.
st8 :- not t8.
:- st8.
t9 :- ack_ver_0 .
t9 :-  spec_waiting_ack_ver_mot.
st9 :- not t9.
:- st9.
t10 :- ack_hor_0 .
t10 :-  spec_waiting_ack_hor_mot.
st10 :- not t10.
:- st10.
t11 :- ack_ver_0.
st11 :- not t11.
:- st11.
{ack_bot_0}.
{ack_hor_0}.
{ack_ver_0}.
{botMot_0}.
{botMot_1}.
{color_0}.
{color_1}.
{color_2}.
{detect_0}.
{detect_1}.
{detect_2}.
{eNV_CONSTRAINT_1_respondsTo_responded}.
{eNV_CONSTRAINT_2_respondsTo_responded}.
{horMot_0}.
{motSpeed_0}.
{motSpeed_1}.
{pREV_aux_3}.
{sYS_CONSTRAINT_0_respondsTo_responded}.
{spec_currentColor_0}.
{spec_currentColor_1}.
{spec_currentColor_2}.
{spec_dropping}.
{spec_speedButtonValidPressed}.
{spec_waiting_ack_hor_mot}.
{spec_waiting_ack_ver_mot}.
{speedButton_0}.
{starting_pos_0}.
{verMot_0}.
rule0 :- verMot_0 , spec_currentColor_0 , spec_currentColor_0 , spec_currentColor_1 .
rule0 :-  spec_currentColor_2 ,  not spec_currentColor_1 .
rule0 :-   not spec_currentColor_2 .
rule0 :-   not spec_currentColor_0 ,  not spec_currentColor_2 .
rule0 :-  spec_currentColor_1 , spec_currentColor_2 .
rule0 :-   not verMot_0 , spec_currentColor_0 ,  not spec_currentColor_0 .
rule0 :-   not spec_currentColor_1 ,  not spec_currentColor_2 .
rule0 :-  spec_currentColor_1 , spec_currentColor_2 .
rule0 :-   not spec_currentColor_0 , spec_currentColor_0 , spec_currentColor_1 .
rule0 :-  spec_currentColor_2 ,  not spec_currentColor_1 .
rule0 :-   not spec_currentColor_2.
rule1 :- spec_dropping , spec_dropping , verMot_0 .
rule1 :-   not spec_dropping ,  not verMot_0 .
rule1 :-   not spec_dropping , spec_dropping ,  not verMot_0 .
rule1 :-   not spec_dropping , verMot_0.
rule2 :- color_0 , color_1 , spec_currentColor_0 , color_2 , spec_currentColor_1 , spec_currentColor_2 .
rule2 :-   not spec_currentColor_2 ,  not color_2 .
rule2 :-   not spec_currentColor_1 .
rule2 :-  spec_currentColor_2 ,  not color_2 .
rule2 :-   not spec_currentColor_1 .
rule2 :-  color_2 , spec_currentColor_1 ,  not spec_currentColor_2 ,  not color_1 .
rule2 :-   not spec_currentColor_0 .
rule2 :-   not color_0 , color_2 , spec_currentColor_1 , spec_currentColor_2 .
rule2 :-   not spec_currentColor_2 ,  not color_2 .
rule2 :-   not spec_currentColor_1 ,  not color_1 .
rule2 :-   not spec_currentColor_0 .
rule2 :-  color_1 , spec_currentColor_0 , spec_currentColor_2 ,  not color_2 .
rule2 :-   not spec_currentColor_1 .
rule2 :-  color_2 , spec_currentColor_1 ,  not spec_currentColor_2.
rule3 :- motSpeed_1.
rule4 :-  not motSpeed_1.
rule5 :- motSpeed_1 .
rule5 :-   not motSpeed_0 ,  not motSpeed_1.
rule6 :- motSpeed_0 .
rule6 :-  spec_speedButtonValidPressed .
rule6 :-  motSpeed_1 ,  not motSpeed_0 .
rule6 :-   not motSpeed_1.
rule7 :-  not spec_waiting_ack_ver_mot .
rule7 :-   not verMot_0.
rule8 :- spec_waiting_ack_ver_mot .
rule8 :-  verMot_0.
rule9 :-  not ack_ver_0 .
rule9 :-   not spec_waiting_ack_ver_mot.
rule10 :- ack_ver_0 .
rule10 :-  spec_waiting_ack_ver_mot.
rule11 :-  not horMot_0 .
rule11 :-   not spec_waiting_ack_hor_mot.
rule12 :- horMot_0 .
rule12 :-  spec_waiting_ack_hor_mot.
rule13 :-  not ack_hor_0 .
rule13 :-   not spec_waiting_ack_hor_mot.
rule14 :- ack_hor_0 .
rule14 :-  spec_waiting_ack_hor_mot.
rule15 :-  not botMot_0 , botMot_1.
rule16 :-  not motSpeed_0 , motSpeed_1.
rule17 :-  not spec_currentColor_0 , spec_currentColor_1 ,  not spec_currentColor_2.
rule18 :-  not spec_currentColor_0 , spec_currentColor_1 , spec_currentColor_2.
rule19 :- verMot_0 .
rule19 :-   not botMot_0 , botMot_1 , horMot_0.
rule20 :- horMot_0 .
rule20 :-   not botMot_0 , botMot_1 , verMot_0.
rule21 :- horMot_0 , verMot_0 .
rule21 :-   not botMot_0 , botMot_1.
rule22 :-  not botMot_0 , botMot_1 , horMot_0 , verMot_0 .
rule22 :-  ack_hor_0 , ack_ver_0.
rule23 :- ack_hor_0 , ack_ver_0 , botMot_0 ,  not botMot_1 ,  not spec_dropping , starting_pos_0 .
rule23 :-   not botMot_0 .
rule23 :-  botMot_1 ,  not ack_hor_0 .
rule23 :-   not ack_ver_0 .
rule23 :-  spec_dropping .
rule23 :-   not starting_pos_0.
rule24 :- color_0 .
rule24 :-  color_1 .
rule24 :-   not color_2 .
rule24 :-  spec_dropping .
rule24 :-  starting_pos_0 .
rule24 :-   not botMot_0 , botMot_1 , horMot_0 , verMot_0.
rule25 :- verMot_0 .
rule25 :-   not spec_dropping , color_0 .
rule25 :-  color_1 .
rule25 :-   not color_2.
rule26 :- detect_0 , spec_dropping , detect_1 .
rule26 :-   not spec_currentColor_0 , detect_2 .
rule26 :-   not spec_currentColor_1 , ack_hor_0 , ack_ver_0 ,  not botMot_0 ,  not botMot_1 ,  not spec_currentColor_2 .
rule26 :-  botMot_0 .
rule26 :-  botMot_1 ,  not ack_hor_0 .
rule26 :-   not ack_ver_0 .
rule26 :-  spec_currentColor_2 .
rule26 :-   not detect_2 , spec_currentColor_1 ,  not botMot_0 ,  not botMot_1 ,  not ack_hor_0 .
rule26 :-   not ack_ver_0 .
rule26 :-  spec_currentColor_2 .
rule26 :-  ack_hor_0 , ack_ver_0 ,  not spec_currentColor_2 , botMot_0 .
rule26 :-  botMot_1 .
rule26 :-   not detect_1 , spec_currentColor_0 ,  not detect_2 , spec_currentColor_1 , ack_hor_0 , ack_ver_0 ,  not botMot_0 ,  not botMot_1 ,  not spec_currentColor_2 .
rule26 :-  botMot_0 .
rule26 :-  botMot_1 ,  not ack_hor_0 .
rule26 :-   not ack_ver_0 .
rule26 :-  spec_currentColor_2 .
rule26 :-  detect_2 .
rule26 :-   not spec_currentColor_1 ,  not botMot_0 ,  not botMot_1 ,  not ack_hor_0 .
rule26 :-   not ack_ver_0 .
rule26 :-  spec_currentColor_2 .
rule26 :-  ack_hor_0 , ack_ver_0 ,  not spec_currentColor_2 , botMot_0 .
rule26 :-  botMot_1 .
rule26 :-   not detect_1 , spec_currentColor_0 , detect_2 .
rule26 :-   not spec_currentColor_1 , ack_hor_0 , ack_ver_0 ,  not botMot_0 ,  not botMot_1 ,  not spec_currentColor_2 .
rule26 :-  botMot_0 .
rule26 :-  botMot_1 ,  not ack_hor_0 .
rule26 :-   not ack_ver_0 .
rule26 :-  spec_currentColor_2 .
rule26 :-   not detect_2 , spec_currentColor_1 ,  not botMot_0 ,  not botMot_1 ,  not ack_hor_0 .
rule26 :-   not ack_ver_0 .
rule26 :-  spec_currentColor_2 .
rule26 :-  ack_hor_0 , ack_ver_0 ,  not spec_currentColor_2 , botMot_0 .
rule26 :-  botMot_1 .
rule26 :-  detect_1 .
rule26 :-   not spec_currentColor_0 ,  not detect_2 , spec_currentColor_1 , ack_hor_0 , ack_ver_0 ,  not botMot_0 ,  not botMot_1 ,  not spec_currentColor_2 .
rule26 :-  botMot_0 .
rule26 :-  botMot_1 ,  not ack_hor_0 .
rule26 :-   not ack_ver_0 .
rule26 :-  spec_currentColor_2 .
rule26 :-  detect_2 .
rule26 :-   not spec_currentColor_1 ,  not botMot_0 ,  not botMot_1 ,  not ack_hor_0 .
rule26 :-   not ack_ver_0 .
rule26 :-  spec_currentColor_2 .
rule26 :-  ack_hor_0 , ack_ver_0 ,  not spec_currentColor_2 , botMot_0 .
rule26 :-  botMot_1 ,  not detect_0 .
rule26 :-   not spec_dropping.
rule27 :- detect_0 , spec_dropping , detect_1 , spec_currentColor_0 , detect_2 , spec_currentColor_1 , ack_hor_0 , ack_ver_0 ,  not horMot_0 , spec_currentColor_2 .
rule27 :-  horMot_0 ,  not ack_hor_0 .
rule27 :-   not ack_ver_0 .
rule27 :-   not spec_currentColor_2 .
rule27 :-   not horMot_0 ,  not ack_hor_0 .
rule27 :-   not ack_ver_0 .
rule27 :-   not spec_currentColor_2 .
rule27 :-  ack_hor_0 , ack_ver_0 , horMot_0 , spec_currentColor_2 ,  not detect_2 .
rule27 :-   not spec_currentColor_1 .
rule27 :-  ack_hor_0 , ack_ver_0 ,  not horMot_0 , spec_currentColor_2 .
rule27 :-  horMot_0 ,  not ack_hor_0 .
rule27 :-   not ack_ver_0 .
rule27 :-   not spec_currentColor_2 ,  not detect_2 .
rule27 :-   not spec_currentColor_1 .
rule27 :-  detect_2 , spec_currentColor_1 ,  not horMot_0 ,  not ack_hor_0 .
rule27 :-   not ack_ver_0 .
rule27 :-   not spec_currentColor_2 .
rule27 :-  ack_hor_0 , ack_ver_0 , horMot_0 , spec_currentColor_2 ,  not detect_1 .
rule27 :-   not spec_currentColor_0 .
rule27 :-  detect_2 , spec_currentColor_1 , ack_hor_0 , ack_ver_0 ,  not horMot_0 , spec_currentColor_2 .
rule27 :-  horMot_0 ,  not ack_hor_0 .
rule27 :-   not ack_ver_0 .
rule27 :-   not spec_currentColor_2 .
rule27 :-   not horMot_0 ,  not ack_hor_0 .
rule27 :-   not ack_ver_0 .
rule27 :-   not spec_currentColor_2 .
rule27 :-  ack_hor_0 , ack_ver_0 , horMot_0 , spec_currentColor_2 ,  not detect_2 .
rule27 :-   not spec_currentColor_1 ,  not detect_1 .
rule27 :-   not spec_currentColor_0 .
rule27 :-  detect_1 , spec_currentColor_0 , ack_hor_0 , ack_ver_0 ,  not horMot_0 , spec_currentColor_2 .
rule27 :-  horMot_0 ,  not ack_hor_0 .
rule27 :-   not ack_ver_0 .
rule27 :-   not spec_currentColor_2 ,  not detect_2 .
rule27 :-   not spec_currentColor_1 .
rule27 :-  detect_2 , spec_currentColor_1 ,  not horMot_0 ,  not ack_hor_0 .
rule27 :-   not ack_ver_0 .
rule27 :-   not spec_currentColor_2 .
rule27 :-  ack_hor_0 , ack_ver_0 , horMot_0 , spec_currentColor_2 ,  not detect_0 .
rule27 :-   not spec_dropping.
rule28 :- pREV_aux_3 , spec_speedButtonValidPressed ,  not speedButton_0 .
rule28 :-   not spec_speedButtonValidPressed ,  not pREV_aux_3 .
rule28 :-  speedButton_0.
:- rule0,rule1,rule2,rule3,rule4,rule5,rule6,rule7,rule8,rule9,rule10,rule11,rule12,rule13,rule14,rule15,rule16,rule17,rule18,rule19,rule20,rule21,rule22,rule23,rule24,rule25,rule26,rule27,rule28.
#show ack_bot_0/0.
#show ack_hor_0/0.
#show ack_ver_0/0.
#show botMot_0/0.
#show botMot_1/0.
#show color_0/0.
#show color_1/0.
#show color_2/0.
#show detect_0/0.
#show detect_1/0.
#show detect_2/0.
#show eNV_CONSTRAINT_1_respondsTo_responded/0.
#show eNV_CONSTRAINT_2_respondsTo_responded/0.
#show horMot_0/0.
#show motSpeed_0/0.
#show motSpeed_1/0.
#show pREV_aux_3/0.
#show sYS_CONSTRAINT_0_respondsTo_responded/0.
#show spec_currentColor_0/0.
#show spec_currentColor_1/0.
#show spec_currentColor_2/0.
#show spec_dropping/0.
#show spec_speedButtonValidPressed/0.
#show spec_waiting_ack_hor_mot/0.
#show spec_waiting_ack_ver_mot/0.
#show speedButton_0/0.
#show starting_pos_0/0.
#show verMot_0/0.
