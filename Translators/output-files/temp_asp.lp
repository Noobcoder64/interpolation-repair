t0 :- speedButton_0 , yBoolExpr_0 .
t0 :-   not speedButton_0 ,  not yBoolExpr_0.
st0 :- not t0.
:- st0.
t1 :- haltButton_0 , yBoolExpr_1 .
t1 :-   not haltButton_0 ,  not yBoolExpr_1.
st1 :- not t1.
:- st1.
t2 :- responded_0 , spec_pausing_0 .
t2 :-   not responded_0 ,  not spec_pausing_0.
st2 :- not t2.
:- st2.
t3 :- ack_hor_0 , responded_1 .
t3 :-   not ack_hor_0 ,  not responded_1.
st3 :- not t3.
:- st3.
{ack_bot_0}.
{ack_hor_0}.
{ack_ver_0}.
{allsleep}.
{botMot_0}.
{botMot_1}.
{color_0}.
{color_1}.
{color_2}.
{detect_0}.
{detect_1}.
{detect_2}.
{direction_0}.
{edge_0}.
{haltButton_0}.
{horMot_0}.
{motSpeed_0}.
{motSpeed_1}.
{nonemove}.
{onlybotmoves}.
{responded_0}.
{responded_1}.
{responded_2}.
{spec_currentColor_0}.
{spec_currentColor_1}.
{spec_currentColor_2}.
{spec_dropping}.
{spec_pauseButtonValidPressed}.
{spec_pausing_0}.
{spec_speedButtonValidPressed}.
{spec_waiting_ack_hor_mot}.
{spec_waiting_ack_ver_mot}.
{speedButton_0}.
{starting_pos_0}.
{verMot_0}.
{verhor_dontmove}.
{yBoolExpr_0}.
{yBoolExpr_1}.
rule0 :-  not verMot_0 .
rule0 :-  spec_currentColor_0 , spec_currentColor_0 , spec_currentColor_1 .
rule0 :-  spec_currentColor_2 ,  not spec_currentColor_1 .
rule0 :-   not spec_currentColor_2 .
rule0 :-   not spec_currentColor_0 ,  not spec_currentColor_2 .
rule0 :-  spec_currentColor_1 , spec_currentColor_2.
rule1 :- verMot_0 .
rule1 :-  color_0 , color_1 , spec_currentColor_0 , color_2 , spec_currentColor_1 , spec_currentColor_2 .
rule1 :-   not spec_currentColor_2 ,  not color_2 .
rule1 :-   not spec_currentColor_1 .
rule1 :-  spec_currentColor_2 ,  not color_2 .
rule1 :-   not spec_currentColor_1 .
rule1 :-  color_2 , spec_currentColor_1 ,  not spec_currentColor_2 ,  not color_1 .
rule1 :-   not spec_currentColor_0 .
rule1 :-   not color_0 , color_2 , spec_currentColor_1 , spec_currentColor_2 .
rule1 :-   not spec_currentColor_2 ,  not color_2 .
rule1 :-   not spec_currentColor_1 ,  not color_1 .
rule1 :-   not spec_currentColor_0 .
rule1 :-  color_1 , spec_currentColor_0 , spec_currentColor_2 ,  not color_2 .
rule1 :-   not spec_currentColor_1 .
rule1 :-  color_2 , spec_currentColor_1 ,  not spec_currentColor_2.
rule2 :- spec_dropping , spec_dropping , verMot_0 .
rule2 :-   not spec_dropping ,  not verMot_0 .
rule2 :-   not spec_dropping , spec_dropping ,  not verMot_0 .
rule2 :-   not spec_dropping , verMot_0.
rule3 :- edge_0.
rule4 :- motSpeed_1.
rule5 :-  not motSpeed_1.
rule6 :- motSpeed_1 .
rule6 :-   not motSpeed_0 ,  not motSpeed_1.
rule7 :- motSpeed_0 .
rule7 :-  spec_speedButtonValidPressed .
rule7 :-  motSpeed_1 ,  not motSpeed_0 .
rule7 :-   not motSpeed_1.
rule8 :- spec_pausing_0.
rule9 :-  not spec_waiting_ack_ver_mot .
rule9 :-   not verMot_0.
rule10 :- spec_waiting_ack_ver_mot .
rule10 :-  verMot_0.
rule11 :-  not ack_ver_0 .
rule11 :-   not spec_waiting_ack_ver_mot.
rule12 :- ack_ver_0 .
rule12 :-  spec_waiting_ack_ver_mot.
rule13 :-  not horMot_0 .
rule13 :-   not spec_waiting_ack_hor_mot.
rule14 :- horMot_0 .
rule14 :-  spec_waiting_ack_hor_mot.
rule15 :-  not ack_hor_0 .
rule15 :-   not spec_waiting_ack_hor_mot.
rule16 :- ack_hor_0 .
rule16 :-  spec_waiting_ack_hor_mot.
rule17 :-  not horMot_0 , responded_2 .
rule17 :-  horMot_0 ,  not responded_2.
rule18 :- ack_hor_0 .
rule18 :-  spec_waiting_ack_hor_mot.
rule19 :- verMot_0 .
rule19 :-   not botMot_0 , botMot_1 , horMot_0.
rule20 :- horMot_0 .
rule20 :-   not botMot_0 , botMot_1 , verMot_0.
rule21 :- horMot_0 , verMot_0 .
rule21 :-   not botMot_0 , botMot_1.
rule22 :- allsleep .
rule22 :-  ack_hor_0 , ack_ver_0.
rule23 :- botMot_0 ,  not botMot_1 ,  not spec_dropping , spec_pausing_0 , starting_pos_0 , verhor_dontmove .
rule23 :-   not botMot_0 .
rule23 :-  botMot_1 , spec_dropping .
rule23 :-   not spec_pausing_0 .
rule23 :-   not starting_pos_0 .
rule23 :-   not verhor_dontmove.
rule24 :- allsleep .
rule24 :-  color_0 .
rule24 :-  color_1 .
rule24 :-   not color_2 .
rule24 :-  spec_dropping .
rule24 :-  starting_pos_0.
rule25 :- verMot_0 .
rule25 :-   not spec_dropping , color_0 .
rule25 :-  color_1 .
rule25 :-   not color_2.
rule26 :- nonemove ,  not spec_dropping , spec_pausing_0 ,  not starting_pos_0 ,  not verMot_0 , color_0 .
rule26 :-  color_1 .
rule26 :-   not color_2 .
rule26 :-  verMot_0 ,  not nonemove .
rule26 :-  spec_dropping .
rule26 :-   not spec_pausing_0 .
rule26 :-  starting_pos_0 .
rule26 :-   not color_0 ,  not color_1 , color_2.
rule27 :-  not botMot_0 ,  not botMot_1 , spec_dropping , spec_pausing_0 , verhor_dontmove , detect_0 ,  not spec_currentColor_0 .
rule27 :-   not detect_0 , spec_currentColor_0 .
rule27 :-  detect_1 ,  not spec_currentColor_1 .
rule27 :-   not detect_1 , spec_currentColor_1 .
rule27 :-  detect_2 ,  not spec_currentColor_2 .
rule27 :-   not detect_2 , spec_currentColor_2 .
rule27 :-  botMot_0 .
rule27 :-  botMot_1 ,  not spec_dropping .
rule27 :-   not spec_pausing_0 .
rule27 :-   not verhor_dontmove .
rule27 :-  detect_0 , spec_currentColor_0 .
rule27 :-   not detect_0 ,  not spec_currentColor_0 , detect_1 , spec_currentColor_1 .
rule27 :-   not detect_1 ,  not spec_currentColor_1 , detect_2 , spec_currentColor_2 .
rule27 :-   not detect_2 ,  not spec_currentColor_2.
rule28 :-  not horMot_0 , spec_dropping , spec_pausing_0 , verhor_dontmove , detect_0 , spec_currentColor_0 .
rule28 :-   not detect_0 ,  not spec_currentColor_0 , detect_1 , spec_currentColor_1 .
rule28 :-   not detect_1 ,  not spec_currentColor_1 , detect_2 , spec_currentColor_2 .
rule28 :-   not detect_2 ,  not spec_currentColor_2 .
rule28 :-  horMot_0 ,  not spec_dropping .
rule28 :-   not spec_pausing_0 .
rule28 :-   not verhor_dontmove .
rule28 :-  detect_0 ,  not spec_currentColor_0 .
rule28 :-   not detect_0 , spec_currentColor_0 .
rule28 :-  detect_1 ,  not spec_currentColor_1 .
rule28 :-   not detect_1 , spec_currentColor_1 .
rule28 :-  detect_2 ,  not spec_currentColor_2 .
rule28 :-   not detect_2 , spec_currentColor_2.
rule29 :- spec_speedButtonValidPressed ,  not speedButton_0 , yBoolExpr_0 .
rule29 :-   not spec_speedButtonValidPressed , speedButton_0 .
rule29 :-   not yBoolExpr_0.
rule30 :-  not haltButton_0 , spec_pauseButtonValidPressed , yBoolExpr_1 .
rule30 :-   not spec_pauseButtonValidPressed , haltButton_0 .
rule30 :-   not yBoolExpr_1.
rule31 :- allsleep .
rule31 :-  spec_pausing_0.
:- rule0,rule1,rule2,rule3,rule4,rule5,rule6,rule7,rule8,rule9,rule10,rule11,rule12,rule13,rule14,rule15,rule16,rule17,rule18,rule19,rule20,rule21,rule22,rule23,rule24,rule25,rule26,rule27,rule28,rule29,rule30,rule31.
#show ack_bot_0/0.
#show ack_hor_0/0.
#show ack_ver_0/0.
#show allsleep/0.
#show botMot_0/0.
#show botMot_1/0.
#show color_0/0.
#show color_1/0.
#show color_2/0.
#show detect_0/0.
#show detect_1/0.
#show detect_2/0.
#show direction_0/0.
#show edge_0/0.
#show haltButton_0/0.
#show horMot_0/0.
#show motSpeed_0/0.
#show motSpeed_1/0.
#show nonemove/0.
#show onlybotmoves/0.
#show responded_0/0.
#show responded_1/0.
#show responded_2/0.
#show spec_currentColor_0/0.
#show spec_currentColor_1/0.
#show spec_currentColor_2/0.
#show spec_dropping/0.
#show spec_pauseButtonValidPressed/0.
#show spec_pausing_0/0.
#show spec_speedButtonValidPressed/0.
#show spec_waiting_ack_hor_mot/0.
#show spec_waiting_ack_ver_mot/0.
#show speedButton_0/0.
#show starting_pos_0/0.
#show verMot_0/0.
#show verhor_dontmove/0.
#show yBoolExpr_0/0.
#show yBoolExpr_1/0.
