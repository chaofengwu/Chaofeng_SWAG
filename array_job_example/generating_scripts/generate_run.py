import os
import sys
import json
import subprocess
import numpy as np
import itertools


default_param_value = {
    'gatk4': {'active-probability-threshold': 0.002, 'base-quality-score-threshold': 18, 'max-alternate-alleles': 6, 
            'max-genotype-count': 1024, 'max-reads-per-alignment-start': 50, 'min-assembly-region-size': 50, 
            'min-base-quality-score': 10, 'native-pair-hmm-threads': 4, 'standard-min-confidence-threshold-for-calling': 30},
    'freebayes': {'genotyping-max-banddepth': 6, 'genotyping-max-iterations': 1000, 'min-alternate-count': 2, 
            'min-alternate-fraction': 0.05, 'min-base-quality': 0, 'min-coverage': 0, 'min-mapping-quality': 1, 
           'mismatch-base-quality-threshold': 10},
    'platypus': {'maxVariants': 8, 'minPosterior': 5, 'minReads': 2}
}

def path_leaf(path): # get filename(with extension) from path
    head, tail = os.path.split(path)
    return tail or os.path.basename(head)


def file_in_folder(folder_path, flag=1): # get files in given folder, return list of filepath and filename
    file_list = []
    file_name = []
    for(dirpath, dirnames, filenames) in os.walk(folder_path):
        
        for i in filenames:
            try:
                file_list += [dirpath + os.sep + i]
                file_name += [i]
            except:
                continue
        if flag == 0:
            break
        file_list.sort(key=path_leaf)
        file_name.sort()
    return [file_list, file_name]


def generate_grid(param_dic, defaults):
    # print(param_list)
    key_list = list(param_dic.keys())
    param_list = [val for key, val in param_dic.items()]
    print(param_list)
    res_list = itertools.product(*param_list)
    res = []
    for config in res_list:
        tmp = {}
        for idx, key in enumerate(key_list):
            tmp[key] = config[idx]
        for key, val in defaults.items():
            if key in key_list:
                continue
            else:
                tmp[key] = val
        res.append(tmp)
    return res


caller = sys.argv[1]
chr_num = sys.argv[2]
res_folder_name = '{}_{}_{}_result'.format(caller, chr_num, sys.argv[3])
# random_num = int(sys.argv[4])

dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
print(dir_path)
generated_folder = os.path.join(dir_path, 'scripts_generated_' + caller)
if not os.path.exists(generated_folder):
    os.mkdir(generated_folder)
    print("Directory " , generated_folder ,  " Created ")
else:    
    print("Directory " , generated_folder ,  " already exists")

template_folder = os.path.join(dir_path, caller)
file_list, _ = file_in_folder(template_folder)
# print(file_list)


for file in file_list:
    if '.json' in file:
        with open(file, 'r') as f:
            param_dic = json.load(f)
    if '.pbs' in file:
        pbs_template_file = file
    if '.sh' in file and 'run_' in file:
        bash_template_file = file

print(param_dic)

exist_dic_file = '{}_existing.json'.format(caller)
exist_dic = {}
try:
    with open(exist_dic_file, 'r') as f:
        exist_dic = json.load(f)
except:
    pass

existing_num = len(exist_dic)

param_list = generate_grid(param_dic, default_param_value[caller])
print(list(param_list))


bash_header_file = os.path.join(generated_folder, '{}_{}_submit_bash.sh'.format(caller, chr_num))
with open(bash_header_file, 'w') as f:
    f.write('bash {}'.format(os.path.join(generated_folder, '{}_{}_${{PBS_ARRAY_INDEX}}.sh'.format(caller, chr_num))))
    f.write('\n')

    
with open(pbs_template_file, 'r') as f:
    template_pbs_lines = f.readlines()
    template_pbs_lines = [a.strip() for a in template_pbs_lines]
for idx in range(len(template_pbs_lines)):
    if 'bash NONE' in template_pbs_lines[idx]:
        # template_pbs_lines[idx] = 'bash {}'.format(bash_file_name)
        template_pbs_lines[idx] = 'bash {}'.format(bash_header_file)
    if 'PBS -N' in template_pbs_lines[idx]:
        template_pbs_lines[idx] = '#PBS -N {}_{}'.format(chr_num, caller)
    if 'PBS -J' in template_pbs_lines[idx]:
        template_pbs_lines[idx] = '#PBS -J 1-{}'.format(len(param_list))
    
pbs_file_name = os.path.join(generated_folder, '{}_{}.pbs'.format(caller, chr_num))
with open(pbs_file_name, 'w') as f:
    for line in template_pbs_lines:
        f.write(line)
        f.write('\n')

# for i in range(random_num):
#     config = generate_grid(param_dic, exist_dic)
# print(param_list)
# print(config)
for i, config in enumerate(param_list):
    # cur_num = i + existing_num
    cur_num = i
    with open(bash_template_file, 'r') as f:
        template_bash_lines = f.readlines()
        template_bash_lines = [i.strip() for i in template_bash_lines]
    for idx in range(len(template_bash_lines)):
        if 'chr=-1' in template_bash_lines[idx]:
            template_bash_lines[idx] = 'chr={}'.format(chr_num)
        if 'res_folder_name=NONE' in template_bash_lines[idx]:
            template_bash_lines[idx] = 'res_folder_name={}'.format(res_folder_name)
        if 'run PARAM_SPACE' in template_bash_lines[idx]:
            head = template_bash_lines[idx][:-len('run PARAM_SPACE > $out_vcf')]
            tail = template_bash_lines[idx][-len(' > $out_vcf'):]
            template_bash_lines[idx] = ' --'.join(['{} {}'.format(key, val) for key, val in config.items()])
            template_bash_lines[idx] = head + '--' + template_bash_lines[idx] + tail
        if 'echo PARAM_SPACE' in template_bash_lines[idx]:
            template_bash_lines[idx] = ''
            for key, val in config.items():
                template_bash_lines[idx] += 'echo "{}: {}" >> $out_file\n'.format(key, val)
            # template_bash_lines[idx] = 'echo "' + ';'.join(['{}:{}'.format(key, val) for key, val in config.items()]) + '" >> $out_file'
        if 'index=NONE' in template_bash_lines[idx]:
            template_bash_lines[idx] = 'index={}'.format(i)

    bash_file_name = os.path.join(generated_folder, '{}_{}_{}.sh'.format(caller, chr_num, cur_num))
    with open(bash_file_name, 'w') as f:
        for line in template_bash_lines:
            f.write(line)
            f.write('\n')

    
    # print(pbs_file_name)
    # submit = subprocess.run(['qsub', '{}'.format(pbs_file_name)])

with open(exist_dic_file, 'w') as f:
    json.dump(exist_dic, f)