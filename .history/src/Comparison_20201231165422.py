# https://www.pnas.org/content/107/28/12698.full
# https://genomebiology.biomedcentral.com/articles/10.1186/gb-2011-12-1-101
# https://sciencebasedmedicine.org/one-reason-mouse-studies-often-dont-translate-to-humans-very-well/
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3737272/
# https://blogs.sciencemag.org/pipeline/archives/2019/08/22/human-brains-and-mouse-brains-so-similar-so-different
# https://portal.brain-map.org/explore/transcriptome
# https://www.biorxiv.org/content/10.1101/384826v1.full
# https://viewer.cytosplore.org/ (only motor-cortex...)
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5055290/
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5299387/
# https://academic.oup.com/cercor/article/28/11/3829/4508772
# https://www.natureasia.com/en/research/highlight/13065#:~:text=Compared%20to%20the%20cerebral%20cortex,and%20the%20number%20of%20neurons.&text=Using%20mouse%20single%2Dcell%20RNA,corresponding%20cell%20types%20in%20mice.
# https://www.researchgate.net/figure/Anatomical-comparison-between-mouse-and-human-brains-The-comparison-between-rodent-A_fig1_221919008

# TODOs: 
# match using manually created mapping of anatomical structures, e.g. based on Sequeira-paper and/or 
# https://science.sciencemag.org/content/367/6482/eaay5947/tab-figures-data (use link from google...)


# match using correlations of orthologues: https://www.proteinatlas.org/humanproteome/brain/mouse+brain

# compare euclidean distances between receptor-occurences per structure per species correlated against a (chosen) standard => see Sequeira fig 7, page 10 
# order regions in ateroposterior axis and use color-code as in fig 1 (sequeira)
# unsupervised clustering (e.g. ward's) of brain-regions on behalf of expression-levels

from functools import reduce
import pandas as pd
from sklearn import preprocessing
import copy

# https://pythonpedia.com/en/knowledge-base/44327999/python--pandas-merge-multiple-dataframes
# def merge_recursive(dfs, countfiles, column, dataSetNames = ['human', 'mouse'], i=0):
#     if i == (countfiles - 2): # it gets to the second to last and merges it with the last
#         return

#     dfm = dfs[i].reset_index().merge(merge_recursive(dfs[i+1].reset_index(), countfiles, column, dataSetNames, i=i+1), on=column)
#     return dfm

def merge(dfs, column):
  # prevent mutating the original data-frames
  #copied = copy.deepcopy(dfs)

  # https://stackoverflow.com/questions/48236438/merge-multiple-dataframe-with-specified-suffix
  copies = []
  for el in dfs:
    copies.append(el['data'].reset_index().set_index(column).add_suffix('_' + el['name']))
    
  return reduce(lambda  acc, next: pd.merge(acc, next, left_index=True, right_index=True, how='inner'), copies)

def by(df1, df2, column, dataSetNames = ['human', 'mouse']):
    # in order to keep all structural columns, we must flatten both dataframes:
    # https://stackoverflow.com/questions/33004573/after-groupby-how-to-flatten-column-headers
    # but we don't want to mutate the actual variables!
    c = df1.reset_index().merge(df2.reset_index(), on=column, how="inner", suffixes=[ '_' + x for x in dataSetNames]).dropna(axis=1, how='all')
    # we got multiple aggregations for expression_levels, so we need to specify which agg we want to check. in this case, count:
    c = c[(c['expression_level_' + dataSetNames[0]] != 0)['count'] | (c['expression_level_' + dataSetNames[1]] != 0)['count']]
    
    # https://stackoverflow.com/questions/44327999/python-pandas-merge-multiple-dataframes
    #print(c)
    return c

def union(dfs, keys =['human', 'mouse']):
  return pd.concat(dfs, keys=keys)

def prepare(df, value_columns = ['expression_level', 'global-z-score'], reset_i = False):
    d = df # prevents mutating the reference
    if reset_i:
        d = d.reset_index()

    return normalize(d)


# from https://stackoverflow.com/questions/26414913/normalize-columns-of-pandas-data-frame
def normalize(df):
    x = df.values #returns a numpy array
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    df = pd.DataFrame(x_scaled)