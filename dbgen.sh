#! /bin/sh
cd dbgen
python3 dbgen.py
cd ..
mv dbgen/agt.sqlite ./agt.sqlite