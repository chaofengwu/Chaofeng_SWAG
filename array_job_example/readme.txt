There are three folders:

	1. freebayes, which provides template scripts and parameter ranges

	2. generating_scripts, which includes a python script to generating scripts for pbs job and submit job (I comment the submission line)

		usage of the python script:
			python generate_run.py freebayes 21 array_2D_res
			
			freebayes: indicate which caller to run
			21: indicate the chromosome to use as input data
			array_2D_res: the name of folder to store result

		the script will generate a .pbs file, a "freebayes_21_submit_bash.sh" file, and a set of files with name "freebayes_21_*.sh" in folder "scripts_generated_freebayes"

	3. scripts_generated_freebayes include three files

	freebayes_21.pbs: the pbs file which could submit array job

	freebayes_21_submit_bash.sh: an intermediate file that help me deal with the $PBS_ARRAY_INDEX easier

	freebayes_21_0.sh: an example of the set of files

The main differences between array job and normal job are:

	1. an additional line "-J 1-X" in .pbs file to indicate the size of the array job. Also, this line indicates that it is an array job

	2. an controller PBS_ARRAY_INDEX for indexing