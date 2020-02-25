import json
import sys

param = sys.argv[1]
pbs_job_num = sys.argv[2]
with open('param_range.json', 'r') as f:
	data = json.load(f)

print(data[param][int(pbs_job_num) - 1])