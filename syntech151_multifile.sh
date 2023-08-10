#!/bin/bash
for filepath in Examples/SYNTECH15-UNREAL-1/*.spectra
do
        python refinement_fifo_search_duplicatecheck.py ${filepath}
done
