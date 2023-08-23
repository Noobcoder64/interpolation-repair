{headMotor_0}.
{headMotor_1}.
{inputMoveMode_0}.
{inputMoveMode_1}.
{leftMotor_0}.
{leftMotor_1}.
{leftMotor_2}.
{obstacle_0}.
{outputMoveMode_0}.
{outputMoveMode_1}.
{rightMotor_0}.
{rightMotor_1}.
{rightMotor_2}.
rule0 :-  not leftMotor_0 , leftMotor_1 , leftMotor_2.
rule1 :-  not rightMotor_0 , rightMotor_1 , rightMotor_2.
rule2 :-  not headMotor_0 , headMotor_1.
rule3 :- inputMoveMode_0 .
rule3 :-  inputMoveMode_1 .
rule3 :-   not obstacle_0 .
rule3 :-  leftMotor_0 ,  not leftMotor_1 , leftMotor_2 , outputMoveMode_0 ,  not outputMoveMode_1 , rightMotor_0 ,  not rightMotor_1 , rightMotor_2.
rule4 :- inputMoveMode_0 .
rule4 :-   not inputMoveMode_1 .
rule4 :-  obstacle_0 .
rule4 :-   not leftMotor_0 ,  not leftMotor_1 ,  not leftMotor_2 ,  not outputMoveMode_0 ,  not outputMoveMode_1 ,  not rightMotor_0 ,  not rightMotor_1 , rightMotor_2.
rule5 :- inputMoveMode_0 .
rule5 :-  inputMoveMode_1 .
rule5 :-  obstacle_0 .
rule5 :-   not leftMotor_0 ,  not leftMotor_1 ,  not leftMotor_2 ,  not rightMotor_0 ,  not rightMotor_1 ,  not rightMotor_2.
rule6 :-  not obstacle_0 .
rule6 :-  outputMoveMode_0 ,  not outputMoveMode_1.
rule7 :- inputMoveMode_0 ,  not inputMoveMode_1 , outputMoveMode_0 , outputMoveMode_1 .
rule7 :-   not outputMoveMode_0 .
rule7 :-   not outputMoveMode_1 ,  not inputMoveMode_0 .
rule7 :-  inputMoveMode_1.
rule8 :-  not inputMoveMode_0 .
rule8 :-  inputMoveMode_1 .
rule8 :-   not leftMotor_0 ,  not leftMotor_1 ,  not leftMotor_2 ,  not rightMotor_0 , rightMotor_1 , rightMotor_2.
rule9 :-  not inputMoveMode_0 .
rule9 :-   not inputMoveMode_1 .
rule9 :-   not leftMotor_0 ,  not leftMotor_1 , leftMotor_2 , rightMotor_0 ,  not rightMotor_1 ,  not rightMotor_2.
rule10 :-  not leftMotor_0 ,  not leftMotor_1 ,  not leftMotor_2 .
rule10 :-  rightMotor_0 ,  not rightMotor_1 ,  not rightMotor_2 .
rule10 :-   not leftMotor_0 , leftMotor_1 , leftMotor_2 ,  not rightMotor_0 , rightMotor_1 , rightMotor_2 .
rule10 :-  inputMoveMode_0 .
rule10 :-  inputMoveMode_1 ,  not inputMoveMode_0 .
rule10 :-   not inputMoveMode_1.
rule11 :- headMotor_0 ,  not headMotor_1 .
rule11 :-   not inputMoveMode_0 .
rule11 :-  inputMoveMode_1 ,  not inputMoveMode_0 .
rule11 :-   not inputMoveMode_1.
rule12 :- leftMotor_0 , leftMotor_1 ,  not leftMotor_2 , rightMotor_0 , rightMotor_1 ,  not rightMotor_2 .
rule12 :-   not outputMoveMode_1 ,  not inputMoveMode_0 .
rule12 :-   not inputMoveMode_1 .
rule12 :-  outputMoveMode_0.
rule13 :-  not inputMoveMode_0 .
rule13 :-   not inputMoveMode_1 .
rule13 :-  obstacle_0 .
rule13 :-   not outputMoveMode_0 ,  not outputMoveMode_1.
:- rule0,rule1,rule2,rule3,rule4,rule5,rule6,rule7,rule8,rule9,rule10,rule11,rule12,rule13.
#show headMotor_0/0.
#show headMotor_1/0.
#show inputMoveMode_0/0.
#show inputMoveMode_1/0.
#show leftMotor_0/0.
#show leftMotor_1/0.
#show leftMotor_2/0.
#show obstacle_0/0.
#show outputMoveMode_0/0.
#show outputMoveMode_1/0.
#show rightMotor_0/0.
#show rightMotor_1/0.
#show rightMotor_2/0.
