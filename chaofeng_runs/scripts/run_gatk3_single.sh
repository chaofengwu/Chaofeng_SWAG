#!/bin/bash

if [ $# -lt 1 ];
then
    echo "usage: $0 [chromosome number]"
    echo
    echo "Run GATK3's HaplotypeCaller."
    exit
fi

module load java
chr=$1
dir=$2
bam="/home/projects/11001079/ms_data/chr${chr}/bam/chr${chr}rg.bam"
ref="/home/projects/11001079/ms_data/chaofeng_runs/data/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna"
module load anaconda
mkdir "${dir}/chr${chr}/vcf"
vcf="${dir}/chr${chr}/vcf/chr${chr}gatk3.vcf"

mkdir "${dir}/chr${chr}/timing"
start="${dir}/chr${chr}/timing/gatk3-start.txt"
end="${dir}/chr${chr}/timing/gatk3-end.txt"

date >$start
java -jar /home/users/industry/uchicago/chaofeng/scratch/GenomeAnalysisTK-3.8-1-0-gf15c1c3ef/GenomeAnalysisTK.jar -R $ref -T HaplotypeCaller -I $bam -nct 24 -o $vcf >  > /home/projects/11001079/ms_data/chaofeng_runs/outputfiles/gatk3.out
date >$end
