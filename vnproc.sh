#!/usr/bin/sh

echo "VN News Corpus processing"

DATA_DIR=./data

./cleaning_corpus.py ${DATA_DIR}/input.txt

./jvntextpro2.sh ${DATA_DIR}/input.cleaned.txt

./cwc.py ${DATA_DIR}/input.cleaned.txt.wseg.pos -o ${DATA_DIR}/input.cleaned.wseg.pos.final_report.txt
./cwc.py ${DATA_DIR}/input.cleaned.txt -o ${DATA_DIR}/input.cleaned.final_report.txt


