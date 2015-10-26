#!/bin/bash

# Generate patch
python3 -m omwtk.nmc_patch_cfromcto

# Patch database
sqlite3 data/eng.db < data/eng-update.sql

# Extract gold annotations
python3 -m omwtk.corpus2txt && python3 -m omwtk.nmctag2txt
