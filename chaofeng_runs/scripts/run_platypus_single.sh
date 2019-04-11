#!/bin/bash

if [ $# -lt 1 ];
then
    echo "usage: $0 [chromosome number]"
    echo
    echo "Run Platypus."
    exit
fi

chr=$1
dir=$2
bam="/home/projects/11001079/ms_data/chr${chr}/bam/chr${chr}rg.bam"
ref="/home/projects/11001079/ms_data/chaofeng_runs/data/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna"
module load anaconda
mkdir "${dir}/chr${chr}/vcf"
vcf="${dir}/chr${chr}/vcf/chr${chr}platypus.vcf"

mkdir "${dir}/chr${chr}/timing"
start="${dir}/chr${chr}/timing/platypus-start.txt"
end="${dir}/chr${chr}/timing/platypus-end.txt"

date >$start
platypus callVariants --bamFiles=${bam} --refFile=${ref} --output=${vcf} > /home/projects/11001079/ms_data/chaofeng_runs/outputfiles/platypus.out
date >$end
