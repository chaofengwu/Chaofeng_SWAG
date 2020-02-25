#!/bin/bash

param="min-mapping-quality"
val=0
for val in 1 2 3 4 5 6 7 8 9 10
do
	qsub -v param=$param,val=$val freebayes.pbs
done

param="min-base-quality"
val=0
for val in 0 2 4 6 8 10 12 14 16 18 20
do
	qsub -v param=$param,val=$val freebayes.pbs
done

param="mismatch-base-quality-threshold"
val=0
for val in 1 4 7 10 13 16 19 22 25 28
do
	qsub -v param=$param,val=$val freebayes.pbs
done

param="min-alternate-fraction"
val=0
for val in 0.005 0.01 0.02 0.05 0.04 0.05 0.06 0.07 0.08 0.09 0.1
do
	qsub -v param=$param,val=$val freebayes.pbs
done

param="min-alternate-count"
val=0
for val in 1 2 3 4 5 6 7 8 9 10
do
	qsub -v param=$param,val=$val freebayes.pbs
done

param="min-coverage"
val=0
for val in 0 4 8 12 16 20 24 28 32 36 40
do
	qsub -v param=$param,val=$val freebayes.pbs
done

param="genotyping-max-iterations"
val=0
for val in 100 400 700 1000 1300 1600 1900 2200 2500
do
	qsub -v param=$param,val=$val freebayes.pbs
done

param="genotyping-max-banddepth"
val=0
for val in 1 2 3 4 5 6 7 8 9 10
do
	qsub -v param=$param,val=$val freebayes.pbs
done
