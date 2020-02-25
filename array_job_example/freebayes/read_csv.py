import pandas as pd
import sys
#csv_file = 'Strelka2-ve.summary.csv'
csv_file = sys.argv[1]
out_file = sys.argv[2]
with open(csv_file, 'rb') as f:
	data = pd.read_csv(f)
	prec = data.iloc[2]['METRIC.Precision']
	recall = data.iloc[2]['METRIC.Recall']

with open(out_file, 'a') as f:
	f.write('Precision: {0}\n'.format(prec))
	f.write('Recall: {0}\n'.format(recall))