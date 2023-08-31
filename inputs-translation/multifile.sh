#!/bin/bash
for filepath in SYNTECH15-UNREAL-RAT/*.rat
do
        python RATSY2Spectra.py ${filepath}
done
