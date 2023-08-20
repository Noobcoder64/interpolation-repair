#!/bin/bash

# These specifications have no enums to translate so use SpecTranslator directly
# for filepath in inputs/AMBA/*.spectra
# do
#         java -jar SpecTranslator.jar -i ${filepath} -o outputs/AMBA
# done

# for filepath in inputs/SYNTECH15-UNREAL/*.spectra
# do
#         python translator.py ${filepath} outputs/SYNTECH-UNREAL/
# done

for filepath in inputs/SYNTECH15-1UNREAL/*.spectra
do
        python translator.py ${filepath} outputs/SYNTECH-1UNREAL/
done