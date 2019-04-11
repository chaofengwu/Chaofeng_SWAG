#!/bin/bash

if [ $# -lt 1 ];
then
    echo "usage: $0 [chromosome number]"
    echo
    echo "Run Strelka2."
    exit
fi

chr=$1
dir=$2
bam="/home/projects/11001079/ms_data/chr${chr}/bam/chr${chr}rg.bam"
ref="/home/projects/11001079/ms_data/chaofeng_runs/data/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna"

mkdir "${dir}/chr${chr}/vcf"
rd="${dir}/chr${chr}/vcf/chr${chr}strelka"

mkdir "${dir}/chr${chr}/timing"
start="${dir}/chr${chr}/timing/strelka-start.txt"
end="${dir}/chr${chr}/timing/strelka-end.txt"
module load anaconda
date >$start
/home/users/industry/uchicago/chaofeng/scratch/strelka-2.9.2.centos6_x86_64/bin/configureStrelkaGermlineWorkflow.py --bam $bam --ref $ref --runDir $rd > /home/projects/11001079/ms_data/chaofeng_runs/outputfiles/strelka.out
${rd}/runWorkflow.py -m local -j 24 -g 96 >> /home/projects/11001079/ms_data/chaofeng_runs/outputfiles/strelka.out
date >$end
