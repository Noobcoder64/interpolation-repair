#!/bin/bash
for filepath in Examples/SYNTECH15-UNREAL/*.spectra
do
        python refinement_fifo_search_duplicatecheck.py ${filepath}
done
