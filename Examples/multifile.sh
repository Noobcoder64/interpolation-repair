#!/bin/bash
for filepath in SYNTECH15-UNREAL/*.rat
do
        python RATSY2Spectra.py ${filepath}
done
