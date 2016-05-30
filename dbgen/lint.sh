#! /bin/sh

pylint -f colorized --rcfile=pylint.rc dbgen.py fixer.py greektools.py
