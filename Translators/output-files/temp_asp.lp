{a}.
{b}.
rule0 :-  not a .
rule0 :-  b.
rule1 :-  not a .
rule1 :-   not b.
:- rule0,rule1.
#show a/0.
#show b/0.
