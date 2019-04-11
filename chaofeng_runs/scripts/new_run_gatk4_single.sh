#!/bin/bash

if [ $# -lt 1 ];
then
    echo "usage: $0 [chromosome number]"
    echo
    echo "Run all tools with 24 threads (if possible)."
    exit
fi

chr=$1
dir=$2

echo "Running GATK4..."
/home/projects/11001079/ms_data/chaofeng_runs/scripts/run_gatk4_single.sh $chr $dir
echo "GATK4 complete."
