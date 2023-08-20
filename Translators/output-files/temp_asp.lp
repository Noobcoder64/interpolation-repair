t0 :-  not ack_ver_0 .
t0 :-  verMot_0.
st0 :- not t0.
:- st0.
t1 :-  not ack_hor_0 .
t1 :-  horMot_0.
st1 :- not t1.
:- st1.
t2 :-  not color_0 , color_1 ,  not color_2.
st2 :- not t2.
:- st2.
t3 :-  not color_0 , color_1 , color_2.
st3 :- not t3.
:- st3.
t4 :-  not detect_0 , detect_1 ,  not detect_2.
st4 :- not t4.
:- st4.
t5 :-  not detect_0 , detect_1 , detect_2.
st5 :- not t5.
:- st5.
t6 :-  not horMot_0 , sYS_CONSTRAINT_0_respondsTo_responded .
t6 :-  horMot_0 ,  not sYS_CONSTRAINT_0_respondsTo_responded.
st6 :- not t6.
:- st6.
t7 :- ack_ver_0 , eNV_CONSTRAINT_1_respondsTo_responded .
t7 :-   not ack_ver_0 ,  not eNV_CONSTRAINT_1_respondsTo_responded.
st7 :- not t7.
:- st7.
t8 :- ack_hor_0 , eNV_CONSTRAINT_2_respondsTo_responded .
t8 :-   not ack_hor_0 ,  not eNV_CONSTRAINT_2_respondsTo_responded.
st8 :- not t8.
:- st8.
t9 :- ack_bot_0 , eNV_CONSTRAINT_3_respondsTo_responded .
t9 :-   not ack_bot_0 ,  not eNV_CONSTRAINT_3_respondsTo_responded.
st9 :- not t9.
:- st9.
t10 :- botMot_0 , pREV_aux_4 .
t10 :-   not botMot_0 ,  not pREV_aux_4.
st10 :- not t10.
:- st10.
t11 :-  not botMot_0 , pREV_aux_5 .
t11 :-  botMot_0 ,  not pREV_aux_5.
st11 :- not t11.
:- st11.
t12 :-  not ack_ver_0 , pREV_aux_6 .
t12 :-  ack_ver_0 ,  not pREV_aux_6.
st12 :- not t12.
:- st12.
t13 :-  not ack_hor_0 , pREV_aux_7 .
t13 :-  ack_hor_0 ,  not pREV_aux_7.
st13 :- not t13.
:- st13.
t14 :- pREV_aux_8 , speedButton_0 .
t14 :-   not pREV_aux_8 ,  not speedButton_0.
st14 :- not t14.
:- st14.
t15 :-  not motSpeed_0 , pREV_aux_9 .
t15 :-  motSpeed_0 ,  not pREV_aux_9.
st15 :- not t15.
:- st15.
t16 :-  not motSpeed_0 , pREV_aux_10 .
t16 :-  motSpeed_0 ,  not pREV_aux_10.
st16 :- not t16.
:- st16.
t17 :- motSpeed_0 , pREV_aux_11 .
t17 :-   not motSpeed_0 ,  not pREV_aux_11.
st17 :- not t17.
:- st17.
t18 :- ack_ver_0 .
t18 :-  spec_waiting_ack_ver_mot.
st18 :- not t18.
:- st18.
t19 :- ack_hor_0 .
t19 :-  spec_waiting_ack_hor_mot.
st19 :- not t19.
:- st19.
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
{eNV_CONSTRAINT_3_respondsTo_responded}.
{horMot_0}.
{motSpeed_0}.
{motSpeed_1}.
{pREV_aux_10}.
{pREV_aux_11}.
{pREV_aux_4}.
{pREV_aux_5}.
{pREV_aux_6}.
{pREV_aux_7}.
{pREV_aux_8}.
{pREV_aux_9}.
{sYS_CONSTRAINT_0_respondsTo_responded}.
{spec_currentColor_0}.
{spec_currentColor_1}.
{spec_currentColor_2}.
{spec_dropping}.
{spec_prevBotMotReturn}.
{spec_prevBotMotSeek}.
{spec_speedButtonValidPressed}.
{spec_state_return_0}.
{spec_state_return_1}.
{spec_state_seek_0}.
{spec_state_seek_1}.
{spec_waiting_ack_hor_mot}.
{spec_waiting_ack_ver_mot}.
{speedButton_0}.
{verMot_0}.
rule0 :-  not verMot_0 .
rule0 :-  spec_currentColor_0 , spec_currentColor_0 , spec_currentColor_1 .
rule0 :-  spec_currentColor_2 ,  not spec_currentColor_1 .
rule0 :-   not spec_currentColor_2 .
rule0 :-   not spec_currentColor_0 ,  not spec_currentColor_2 .
rule0 :-  spec_currentColor_1 , spec_currentColor_2.
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
rule3 :-  not spec_state_return_0 ,  not spec_state_return_1 .
rule3 :-   not spec_state_return_0 , spec_state_return_1 .
rule3 :-  spec_state_return_0 ,  not spec_state_return_1.
rule4 :-  not spec_waiting_ack_ver_mot .
rule4 :-   not verMot_0.
rule5 :- spec_waiting_ack_ver_mot .
rule5 :-  verMot_0.
rule6 :-  not ack_ver_0 .
rule6 :-   not spec_waiting_ack_ver_mot.
rule7 :- ack_ver_0 .
rule7 :-  spec_waiting_ack_ver_mot.
rule8 :-  not horMot_0 .
rule8 :-   not spec_waiting_ack_hor_mot.
rule9 :- horMot_0 .
rule9 :-  spec_waiting_ack_hor_mot.
rule10 :-  not ack_hor_0 .
rule10 :-   not spec_waiting_ack_hor_mot.
rule11 :- ack_hor_0 .
rule11 :-  spec_waiting_ack_hor_mot.
rule12 :-  not botMot_0 , botMot_1.
rule13 :-  not motSpeed_0 , motSpeed_1.
rule14 :-  not spec_state_return_0 , spec_state_return_1.
rule15 :-  not spec_currentColor_0 , spec_currentColor_1 ,  not spec_currentColor_2.
rule16 :-  not spec_currentColor_0 , spec_currentColor_1 , spec_currentColor_2.
rule17 :- pREV_aux_4 , spec_prevBotMotReturn .
rule17 :-   not pREV_aux_4 ,  not spec_prevBotMotReturn.
rule18 :- pREV_aux_5 , spec_prevBotMotSeek .
rule18 :-   not pREV_aux_5 ,  not spec_prevBotMotSeek.
rule19 :- verMot_0 .
rule19 :-   not botMot_0 , botMot_1 , horMot_0.
rule20 :- horMot_0 .
rule20 :-   not botMot_0 , botMot_1 , verMot_0.
rule21 :- horMot_0 , verMot_0 .
rule21 :-   not botMot_0 , botMot_1.
rule22 :-  not botMot_0 , botMot_1 , horMot_0 , verMot_0 .
rule22 :-  ack_hor_0 , ack_ver_0.
rule23 :- color_0 .
rule23 :-   not color_1 .
rule23 :-   not color_2 .
rule23 :-  spec_dropping .
rule23 :-   not botMot_0 , botMot_1 , horMot_0 , verMot_0.
rule24 :-  not ack_bot_0 .
rule24 :-   not ack_hor_0 .
rule24 :-   not ack_ver_0 .
rule24 :-   not pREV_aux_6 .
rule24 :-   not spec_dropping .
rule24 :-   not botMot_0 ,  not botMot_1.
rule25 :-  not ack_bot_0 , ack_hor_0 , ack_ver_0 , detect_0 , spec_dropping , detect_1 , spec_currentColor_0 , detect_2 , spec_currentColor_1 ,  not horMot_0 , pREV_aux_5 , spec_currentColor_2 .
rule25 :-  horMot_0 ,  not pREV_aux_5 .
rule25 :-   not spec_currentColor_2 .
rule25 :-   not horMot_0 ,  not pREV_aux_5 .
rule25 :-   not spec_currentColor_2 .
rule25 :-  horMot_0 , pREV_aux_5 , spec_currentColor_2 ,  not detect_2 .
rule25 :-   not spec_currentColor_1 .
rule25 :-   not horMot_0 , pREV_aux_5 , spec_currentColor_2 .
rule25 :-  horMot_0 ,  not pREV_aux_5 .
rule25 :-   not spec_currentColor_2 ,  not detect_2 .
rule25 :-   not spec_currentColor_1 .
rule25 :-  detect_2 , spec_currentColor_1 ,  not horMot_0 ,  not pREV_aux_5 .
rule25 :-   not spec_currentColor_2 .
rule25 :-  horMot_0 , pREV_aux_5 , spec_currentColor_2 ,  not detect_1 .
rule25 :-   not spec_currentColor_0 .
rule25 :-  detect_2 , spec_currentColor_1 ,  not horMot_0 , pREV_aux_5 , spec_currentColor_2 .
rule25 :-  horMot_0 ,  not pREV_aux_5 .
rule25 :-   not spec_currentColor_2 .
rule25 :-   not horMot_0 ,  not pREV_aux_5 .
rule25 :-   not spec_currentColor_2 .
rule25 :-  horMot_0 , pREV_aux_5 , spec_currentColor_2 ,  not detect_2 .
rule25 :-   not spec_currentColor_1 ,  not detect_1 .
rule25 :-   not spec_currentColor_0 .
rule25 :-  detect_1 , spec_currentColor_0 ,  not horMot_0 , pREV_aux_5 , spec_currentColor_2 .
rule25 :-  horMot_0 ,  not pREV_aux_5 .
rule25 :-   not spec_currentColor_2 ,  not detect_2 .
rule25 :-   not spec_currentColor_1 .
rule25 :-  detect_2 , spec_currentColor_1 ,  not horMot_0 ,  not pREV_aux_5 .
rule25 :-   not spec_currentColor_2 .
rule25 :-  horMot_0 , pREV_aux_5 , spec_currentColor_2 , ack_bot_0 .
rule25 :-   not ack_hor_0 .
rule25 :-   not ack_ver_0 .
rule25 :-   not detect_0 .
rule25 :-   not spec_dropping.
rule26 :-  not ack_bot_0 .
rule26 :-   not ack_hor_0 .
rule26 :-   not ack_ver_0 .
rule26 :-   not pREV_aux_7 .
rule26 :-   not spec_dropping .
rule26 :-  botMot_0 ,  not botMot_1.
rule27 :-  not ack_bot_0 .
rule27 :-   not spec_prevBotMotReturn .
rule27 :-   not botMot_0 , botMot_1 , horMot_0 , verMot_0.
rule28 :- pREV_aux_8 , spec_speedButtonValidPressed ,  not speedButton_0 .
rule28 :-   not spec_speedButtonValidPressed ,  not pREV_aux_8 .
rule28 :-  speedButton_0.
rule29 :-  not pREV_aux_9 .
rule29 :-   not spec_speedButtonValidPressed .
rule29 :-   not motSpeed_0 , motSpeed_1.
rule30 :-  not pREV_aux_10 .
rule30 :-   not spec_speedButtonValidPressed .
rule30 :-  motSpeed_0 ,  not motSpeed_1.
rule31 :-  not pREV_aux_11 .
rule31 :-   not spec_speedButtonValidPressed .
rule31 :-   not motSpeed_0 ,  not motSpeed_1.
rule32 :-  not pREV_aux_9 .
rule32 :-  spec_speedButtonValidPressed .
rule32 :-   not motSpeed_0 ,  not motSpeed_1.
rule33 :-  not pREV_aux_10 .
rule33 :-  spec_speedButtonValidPressed .
rule33 :-   not motSpeed_0 , motSpeed_1.
rule34 :-  not pREV_aux_11 .
rule34 :-  spec_speedButtonValidPressed .
rule34 :-  motSpeed_0 ,  not motSpeed_1.
:- rule0,rule1,rule2,rule3,rule4,rule5,rule6,rule7,rule8,rule9,rule10,rule11,rule12,rule13,rule14,rule15,rule16,rule17,rule18,rule19,rule20,rule21,rule22,rule23,rule24,rule25,rule26,rule27,rule28,rule29,rule30,rule31,rule32,rule33,rule34.
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
#show eNV_CONSTRAINT_3_respondsTo_responded/0.
#show horMot_0/0.
#show motSpeed_0/0.
#show motSpeed_1/0.
#show pREV_aux_10/0.
#show pREV_aux_11/0.
#show pREV_aux_4/0.
#show pREV_aux_5/0.
#show pREV_aux_6/0.
#show pREV_aux_7/0.
#show pREV_aux_8/0.
#show pREV_aux_9/0.
#show sYS_CONSTRAINT_0_respondsTo_responded/0.
#show spec_currentColor_0/0.
#show spec_currentColor_1/0.
#show spec_currentColor_2/0.
#show spec_dropping/0.
#show spec_prevBotMotReturn/0.
#show spec_prevBotMotSeek/0.
#show spec_speedButtonValidPressed/0.
#show spec_state_return_0/0.
#show spec_state_return_1/0.
#show spec_state_seek_0/0.
#show spec_state_seek_1/0.
#show spec_waiting_ack_hor_mot/0.
#show spec_waiting_ack_ver_mot/0.
#show speedButton_0/0.
#show verMot_0/0.
