#!/usr/bin/env bash

if [ "$(uname)" == "Darwin" ]; then
    # Get script dir on Mac
    NMB1_DIR=$(dirname "$(stat -f "$0")")
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # Get script dir on Linux
    NMB1_DIR=$(dirname "$(readlink -f "$0")")
fi
OLD_DIR=$PWD
cd $NMB1_DIR
git reset --hard HEAD
git pull
pkill -9 -f NewMusicBot1/app.py
python3 -u $NMB1_DIR/app.py $NMB1_DIR/config.json $NMB1_DIR/blacklist.json $NMB1_DIR/results.csv | tee -a $NMB1_DIR/stdout.log &
disown
cd $OLD_DIR

