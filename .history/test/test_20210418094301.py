
import pandas as pd

def z_score(data_col):
  # https://intellipaat.com/community/20492/pandas-compute-z-score-for-all-columns  
  # from https://www.statisticshowto.com/probability-and-statistics/z-score/: 
  # Simply put, a z-score (also called a standard score) gives you an idea of how far from the mean a data point is. 
  # But more technically it’s a measure of how many standard deviations below or above the population mean a raw score is.
  # https://community.brain-map.org/t/what-is-the-z-score-reference-value-in-rnaseq-gbm-data/513/3
  return (data_col - data_col.mean())/data_col.std()

def apply_z_score(x):
  return z_score(x) # the first column (provided as a row here) is the expression-id

expr = pd.read_csv('test\\DYPIOI1DCI11_0log2\\Expression.csv', header=None)
probes = pd.read_csv('test\\DYPIOI1DCI11_0log2\\Probes.csv', header=0)

z = expr.apply(apply_z_score, axis=1)
print(z)
