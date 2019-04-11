#!/bin/bash
chr_dir=/home/projects/11001079/ms_data/chaofeng_runs/num1run
mkdir $chr_dir

counter=1


while [ $counter -le 1 ]
do
echo $counter
echo $chr_dir
mkdir ${chr_dir}/chr${counter}
#qsub -v 1=$counter -v 2=$chr_dir submit_run_variantes.pbs
qsub -v 1=$counter -v 2=$chr_dir gatk4_submit.pbs
qsub -v 1=$counter -v 2=$chr_dir freebayes_submit.pbs
qsub -v 1=$counter -v 2=$chr_dir strelka_submit.pbs
qsub -v 1=$counter -v 2=$chr_dir platypus_submit.pbs
qsub -v 1=$counter -v 2=$chr_dir gatk3_submit.pbs
((counter++))
done
