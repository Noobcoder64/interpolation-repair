#!/bin/bash
for filepath in AMBAss/*.rat
do
        python RATSY2Spectra.py ${filepath}
done
