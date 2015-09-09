#!/usr/bin/sh

echo "VN News Corpus processing"

DATA_DIR=./data
APPD_DIR=./omwtk
INTPUT_FILE=input
CLEANED_INPUT=${INPUT_FILE}.cleaned

# Clean file first
${APPD_DIR}/cleaning_corpus.py ${DATA_DIR}/${INPUT_FILE}.txt

# Use jVNTextPro2 to process data
./jvntextpro2.sh ${DATA_DIR}/${CLEANED_INPUT}.txt

# Provide statistics
${APPD_DIR}/cwc.py ${DATA_DIR}/${CLEANED_INPUT}.txt.wseg.pos -o ${DATA_DIR}/${CLEANED_INPUT}.wseg.pos.final_report.txt
${APPD_DIR}/cwc.py ${DATA_DIR}/${CLEANED_INPUT}.txt -o ${DATA_DIR}/${CLEANED_INPUT}.txt.final_report.txt


