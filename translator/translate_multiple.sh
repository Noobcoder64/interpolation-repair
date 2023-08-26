#!/bin/bash

# for filepath in inputs/SIMPLE/*.spectra
# do
#         java -jar SpecTranslator.jar -i ${filepath} -o outputs/SIMPLE
# done

# for filepath in inputs/AMBA/*.spectra
# do
#         java -jar SpecTranslator.jar -i ${filepath} -o outputs/AMBA
# done

# for filepath in inputs/SYNTECH15-UNREAL/*.spectra
# do
#         python translator.py ${filepath} outputs/SYNTECH-UNREAL/
# done

# for filepath in inputs/SYNTECH15-1UNREAL/*.spectra
# do
#         python translator.py ${filepath} outputs/SYNTECH15-1UNREAL/
# done

for filepath in inputs/SYNTECH15-UNREAL-ORIGINAL/*.spectra
do
        python translator.py ${filepath} outputs/BOOL-TRANSLATED-G
done