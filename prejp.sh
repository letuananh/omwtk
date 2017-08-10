#!/usr/bin/sh

OMWTK_HOME=~/wk/omwtk
export PYTHONPATH=${OMWTK_HOME}
python3 -m omwtk.prejp "$@"
