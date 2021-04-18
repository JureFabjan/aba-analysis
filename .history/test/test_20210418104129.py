
import pandas as pd
import numpy as np
def z_score(data_col):
  # https://intellipaat.com/community/20492/pandas-compute-z-score-for-all-columns  
  # from https://www.statisticshowto.com/probability-and-statistics/z-score/: 
  # Simply put, a z-score (also called a standard score) gives you an idea of how far from the mean a data point is. 
  # But more technically it’s a measure of how many standard deviations below or above the population mean a raw score is.
  # https://community.brain-map.org/t/what-is-the-z-score-reference-value-in-rnaseq-gbm-data/513/3
  return (data_col - data_col.mean())/data_col.std()

def apply_z_score(x):
  return z_score(x[1:]) # the first column (provided as a row here) is the expression-id

folder = "structures_log2intensities" # structures_log2intensities / samples_log2intensities
# test using http://human.brain-map.org/microarray/search/show?exact_match=false&search_term=gabra4&search_type=gene&page_num=0
expr = pd.read_csv(f'test\\{folder}\\Expression.csv', header=None)
#probes = pd.read_csv('test\\DYPIOI1DCI11_0log2\\Probes.csv', header=0)

z = expr.apply(apply_z_score, axis=1)

all_values = z.values.flatten()
all_values.sort()

#print(all_values)
np.savetxt(f"dl_z-score_{folder}.csv", all_values, delimiter=",")