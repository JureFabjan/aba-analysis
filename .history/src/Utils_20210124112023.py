
import os
import pandas as pd
import logging as log
import pickle
from types import SimpleNamespace

GLOB_Z = 'global-z-score'

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

def get_sub_columns(df, column):
  return [c[1] for c in df.columns if c[0]==column]

def drop_columns_if(df, keywords = ['structure_', 'level_']):
  # https://stackoverflow.com/questions/13411544/delete-column-from-pandas-dataframe
  ret = df.copy()

  for name in df.columns:
    if any(keyword in name[0] for keyword in keywords):
      ret = ret.drop(name, 1)
  
  return ret

def intersect(lst1, lst2): 
  # from https://www.geeksforgeeks.org/python-intersection-two-lists/
  return list(set(lst1) & set(lst2))
  
def merge_with_structure(data, structure, value_cols, aggregations):
  # merge while keeping each structure, even if there are no expression-levels.
  # https://stackoverflow.com/questions/31528819/using-merge-on-a-column-and-index-in-pandas
  ret = structure.merge(data,  left_index=True, right_on="structure_id", how="left")

  structure_identifier = ['structure_id', 'structure_name', 'acronym']
  level_cols = [col for col in ret.columns if 'level_' in col]
  byStructure = ret.groupby(level_cols + structure_identifier, dropna=False)[value_cols].agg(aggregations)
  byAcronym = ret.groupby('acronym', dropna=False)[value_cols].agg(aggregations)
  
  return simple({ 'structure': byStructure, 'acronym': byAcronym })

def splitByThreshold(data, column, separation_threshold):
  return (
    data[(data[column] < separation_threshold) & (data[column] > (-1 * separation_threshold))], 
    data[(data[column] > separation_threshold) | (data[column] < (-1 * separation_threshold))]);

def negativePart(number):
  return number if (number < 0) else 0

def save(obj, path, filename):
  # https://www.techcoil.com/blog/how-to-save-and-load-objects-to-and-from-file-in-python-via-facilities-from-the-pickle-module/
  makedir(path)
  with open(path + filename, 'wb') as file:
    # https://stackoverflow.com/questions/29127593/trying-to-write-a-cpickle-object-but-get-a-write-attribute-type-error
    pickle.dump(obj, file)

  return path + filename

def load(path):
  with open(path, 'rb') as file:
    return pickle.load(file)

def simple(dict):
  ret = SimpleNamespace()
  for k,v in dict.items():
    setattr(ret, k, v) 

  return ret
    
def dict_by_agg(data, aggregations, column_mappings):
  return { agg: data[[(experiment, agg) for experiment 
  in { **column_mappings['human'], **column_mappings['mouse']}.values()]].droplevel(1, axis=1) 
    for agg 
      in aggregations }    

def unstack_columns(df, separator = '_'):
  # inverse of: https://stackoverflow.com/questions/46247302/pandas-split-columns-into-multilevel
  return pd.DataFrame(df.values, columns=[separator.join([val for val in c if val != "" ]) for c in df.columns])  


def unpack(*arg):
    return list(arg)

# ? this helps profiling performance-bottlenecks
# from: https://towardsdatascience.com/how-to-profile-your-code-in-python-e70c834fad89
import cProfile
import pstats
from functools import wraps

def profile(output_file=None, sort_by='cumulative', lines_to_print=None, strip_dirs=False):
    """A time profiler decorator.
    Inspired by and modified the profile decorator of Giampaolo Rodola:
    http://code.activestate.com/recipes/577817-profile-decorator/
    Args:
        output_file: str or None. Default is None
            Path of the output file. If only name of the file is given, it's
            saved in the current directory.
            If it's None, the name of the decorated function is used.
        sort_by: str or SortKey enum or tuple/list of str/SortKey enum
            Sorting criteria for the Stats object.
            For a list of valid string and SortKey refer to:
            https://docs.python.org/3/library/profile.html#pstats.Stats.sort_stats
        lines_to_print: int or None
            Number of lines to print. Default (None) is for all the lines.
            This is useful in reducing the size of the printout, especially
            that sorting by 'cumulative', the time consuming operations
            are printed toward the top of the file.
        strip_dirs: bool
            Whether to remove the leading path info from file names.
            This is also useful in reducing the size of the printout
    Returns:
        Profile of the decorated function
    """

    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _output_file = output_file or func.__name__ + '.prof'
            pr = cProfile.Profile()
            pr.enable()
            retval = func(*args, **kwargs)
            pr.disable()
            pr.dump_stats(_output_file)

            with open(_output_file, 'w') as f:
                ps = pstats.Stats(pr, stream=f)
                if strip_dirs:
                    ps.strip_dirs()
                if isinstance(sort_by, (tuple, list)):
                    ps.sort_stats(*sort_by)
                else:
                    ps.sort_stats(sort_by)
                ps.print_stats(lines_to_print)
            return retval

        return wrapper

    return inner