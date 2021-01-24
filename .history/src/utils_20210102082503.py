
import os
import pandas as pd
import logging 

GLOB_Z = 'global-z-score'
VALUE_COLUMNS = ['expression_level',GLOB_Z] 

def z_score(data_col):
  # https://intellipaat.com/community/20492/pandas-compute-z-score-for-all-columns  
  # from https://www.statisticshowto.com/probability-and-statistics/z-score/: 
  # Simply put, a z-score (also called a standard score) gives you an idea of how far from the mean a data point is. 
  # But more technically it’s a measure of how many standard deviations below or above the population mean a raw score is.
  # https://community.brain-map.org/t/what-is-the-z-score-reference-value-in-rnaseq-gbm-data/513/3
  return (data_col - data_col.mean())/data_col.std()

def makedir(path):
  # from https://www.tutorialspoint.com/How-can-I-create-a-directory-if-it-does-not-exist-using-Python
  if not os.path.exists(path):
      os.makedirs(path)
  return path

def getFilename(filepath): 
  # https://stackoverflow.com/questions/4444923/get-filename-without-extension-in-python/4444952
  return os.path.splitext(os.path.basename(filepath))[0]

def drop_columns_if(df, keywords = ['structure_', 'level_']):
  # https://stackoverflow.com/questions/13411544/delete-column-from-pandas-dataframe
  ret = df.copy()

  for name in df.columns:
    if any(keyword in name[0] for keyword in keywords):
      ret = ret.drop(name, 1)
  
  return ret
  
def merge_with_structure(data, structure, value_cols, aggregations):
  # merge while keeping each structure, even if there are no expression-levels.
  # https://stackoverflow.com/questions/31528819/using-merge-on-a-column-and-index-in-pandas
  ret = structure.merge(data,  left_index=True, right_on="structure_id", how="left")

  structure_identifier = ['structure_id', 'structure_name', 'acronym']
  level_cols = [col for col in ret.columns if 'level_' in col]
  ret = ret.groupby(level_cols + structure_identifier, dropna=False)[value_cols].agg(aggregations)
  
  return ret

def splitByThreshold(data, column, separation_threshold):
  return (
    data[(data[column] < separation_threshold) & (data[column] > (-1 * separation_threshold))], 
    data[(data[column] > separation_threshold) | (data[column] < (-1 * separation_threshold))]);

def negativePart(number):
  return number if (number < 0) else 0

def save(df, path, filename, **kwags):
  makedir(path)
  df.to_pickle(path + filename, **kwags)
  return path + filename

def load(path, **kwags):
  return pd.read_pickle(path, **kwags)

#def log(fn, text):
  #return logging