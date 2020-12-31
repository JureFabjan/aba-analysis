# from https://www.tutorialspoint.com/How-can-I-create-a-directory-if-it-does-not-exist-using-Python

import os
import string
import pandas as pd

GLOB_Z = 'global-z-score'
VALUE_COLUMNS = ['expression_level',GLOB_Z] 

def makedir(path):
  if not os.path.exists(path):
      os.makedirs(path)
  return path


# def getAlphabeticalRange(start, to):
#     base = ord('A')
#     start = start.upper()
#     to = to.upper()

#     # from https://stackoverflow.com/questions/3190122/python-how-to-print-range-a-z
#     return string.ascii_uppercase[base - ord(start):base - ord(to)]
     

# from https://www.statisticshowto.com/probability-and-statistics/z-score/: 
# Simply put, a z-score (also called a standard score) gives you an idea of how far from the mean a data point is. 
# But more technically it’s a measure of how many standard deviations below or above the population mean a raw score is.
def z_score(data_col):
  # https://community.brain-map.org/t/what-is-the-z-score-reference-value-in-rnaseq-gbm-data/513/3
  return (data_col - data_col.mean())/data_col.std()

# https://intellipaat.com/community/20492/pandas-compute-z-score-for-all-columns

def merge_with_structure(data, structure, value_cols, aggregations):
  # merge while keeping each structure, even if there are no expression-levels
  ret = structure.merge(data,  left_index=True, right_on="structure_id", how="left") #.dropna(axis=0, how='all')

  structure_identifier = ['structure_id', 'structure_name', 'acronym']
  level_cols = [col for col in ret.columns if 'level_' in col]
  ret = ret.groupby(level_cols + structure_identifier, dropna=False)[value_cols].agg(aggregations)
  
  return ret
  
  # https://stackoverflow.com/questions/11194610/how-can-i-reorder-multi-indexed-dataframe-columns-at-a-specific-level
  # https://stackoverflow.com/questions/14507794/pandas-how-to-flatten-a-hierarchical-index-in-columns
  # remove multi-index, so that we can select columns in a specific order
  #ret.columns = ret.columns.get_level_values(0)

  #return ret[[left_cols + value_cols + level_cols]]

def negativePart(number):
  return number if (number < 0) else 0


cache_filename = "cache.pkl"

def save(df, path, **kwags):
  makedir(path)
  df.to_pickle(path + cache_filename, **kwags)
  return path + cache_filename

def load(path, **kwags):
  return pd.read_pickle(path + cache_filename, **kwags)