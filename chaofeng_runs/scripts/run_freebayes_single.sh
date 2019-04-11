#!/bin/bash

if [ $# -lt 1 ];
then
    echo "usage: $0 [chromosome number]"
    echo
    echo "Run freebayes with 24 threads."
    exit
fi

chr=$1
dir=$2
bam="/home/projects/11001079/ms_data/chr${chr}/bam/chr${chr}rg.bam"
ref="/home/projects/11001079/ms_data/chaofeng_runs/data/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna"

mkdir "${dir}/chr${chr}/vcf"
reg="/home/projects/11001079/ms_data/chr${chr}/bam/chr${chr}.ref.regions"
vcf="${dir}/chr${chr}/vcf/chr${chr}freebayes.vcf"

mkdir "${dir}/chr${chr}/timing"
start="${dir}/chr${chr}/timing/freebayes-start.txt"
end="${dir}/chr${chr}/timing/freebayes-end.txt"

module load anaconda
date >$start
bamtools coverage -in $bam | coverage_to_regions.py ${ref}.fai 500 >$reg 2> /home/projects/11001079/ms_data/chaofeng_runs/outputfiles/freebayes.out
freebayes-parallel $reg 24 -f $ref $bam >$vcf 2>> /home/projects/11001079/ms_data/chaofeng_runs/outputfiles/freebayes.out
date >$end
