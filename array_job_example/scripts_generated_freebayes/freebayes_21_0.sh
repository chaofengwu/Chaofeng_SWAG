#!/bin/bash
source activate py2_biotools

variant_caller="freebayes"

chr=21
res_folder_name=freebayes_21_a_result

# param=$1
# chr=$2
# res_folder_name=$3
# index=$PBS_ARRAY_INDEX
index=0

work_dir="/home/projects/11001079/chaofeng/nscc_0205/array_random_select/${variant_caller}"
res_dir="/home/projects/11001079/chaofeng/nscc_0205/res/${res_folder_name}"
# mkdir -p $work_dir
mkdir -p $res_dir
cd $work_dir
# param_val=`python /home/projects/11001079/chaofeng/nscc_0205/random_select/freebayes/get_value.py ${param} ${index}`

bam="/home/projects/11001079/chaofeng/chr${chr}/bam/chr${chr}.bam"
ref="//home/projects/11001079/chaofeng/data/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna"
true_file="/home/projects/11001079/chaofeng/ref/chr${chr}.vcf.gz"
reg="/home/projects/11001079/chaofeng/chr${chr}/bam/chr${chr}.ref.regions"

out_vcf="${res_dir}/${index}.vcf"
out_file="${res_dir}/${index}.txt"
rm $out_file
touch $out_file
echo "min-alternate-count: 0" >> $out_file
echo "min-coverage: 0" >> $out_file
echo "genotyping-max-banddepth: 6" >> $out_file
echo "genotyping-max-iterations: 1000" >> $out_file
echo "min-alternate-fraction: 0.05" >> $out_file
echo "min-base-quality: 0" >> $out_file
echo "min-mapping-quality: 1" >> $out_file
echo "mismatch-base-quality-threshold: 10" >> $out_file


start=`date +%s%N | cut -b1-13`

bamtools coverage -in $bam | coverage_to_regions.py ${ref}.fai 500 >$reg 2>/dev/null
freebayes-parallel $reg 24 -f $ref $bam --min-alternate-count 0 --min-coverage 0 --genotyping-max-banddepth 6 --genotyping-max-iterations 1000 --min-alternate-fraction 0.05 --min-base-quality 0 --min-mapping-quality 1 --mismatch-base-quality-threshold 10 > $out_vcf
# freebayes-parallel $reg 24 -f $ref $bam --${param}=${param_val} > $out_vcf 2>/dev/null

conda activate happy
module load boost/1.59.0/gcc493/serial
module load java
export HAPPY=/home/users/industry/uchicago/chaofeng/scratch/hap.py-build/bin/hap.py

bgzip -c ${out_vcf} > ${out_vcf}.gz
tabix -fp vcf ${out_vcf}.gz
out_vcf=${out_vcf}.gz

end=`date +%s%N | cut -b1-13`
runtime=$(((end-start)))

compare_out_series="${res_dir}/${index}_happy_out"
compare_out_file="${res_dir}/${index}_happy_out.summary.csv"

set -e
HAPPY=/home/users/industry/uchicago/chaofeng/scratch/hap.py-build
HCDIR=/home/users/industry/uchicago/chaofeng/scratch/hap.py-build/bin
HC=${HCDIR}/hap.py

python $HC $true_file $out_vcf -r $ref -o ${compare_out_series} > /dev/null 2>&1

echo "time in 0.001 second: $runtime" >> $out_file
python ${work_dir}/read_csv.py ${compare_out_file} $out_file
