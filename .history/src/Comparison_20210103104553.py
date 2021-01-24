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

# TODO: 
# match using manually created mapping of anatomical structures, e.g. based on Sequeira-paper and/or 
# https://science.sciencemag.org/content/367/6482/eaay5947/tab-figures-data (use link from google...)


# match using correlations of orthologues: https://www.proteinatlas.org/humanproteome/brain/mouse+brain

# compare euclidean distances between receptor-occurences per structure per species correlated against a (chosen) standard => see Sequeira fig 7, page 10 
# order regions in ateroposterior axis and use color-code as in fig 1 (sequeira)
# unsupervised clustering (e.g. ward's) of brain-regions on behalf of expression-levels

from functools import reduce
import pandas as pd
import numpy as np

import Utils

# merge a list of data-frames using a shared column. this column will be used as the new index. 
# uses an inner join. does not mutate the original data-frames.
def merge(dfs, dataset, merge_on, shared_columns):

  copies = []

  for el in dfs:
    
    # we need to join using the index. otherwise, the column will be renamed during merge.
    data = getattr(el.data, dataset).reset_index().set_index(merge_on) # assigning this to a new var prevents mutating the original data-frames

    data = data[shared_columns]
    # TODO - discuss with Jure: do we need to know if a species / donor has no samples in a probe?
    data = data.dropna() #data[data[(Constants.GLOB_Z, 'count')] > 0]

    # add_suffix is not suitable, as it would also affect sub-level columns (e.g. mean, var, etc. of expression-levels)
    # https://stackoverflow.com/questions/57740319/how-to-add-prefix-to-multi-index-columns-at-particular-level
    data = data.rename(mapper=lambda x: f'{x}_{el["name"]}', axis='columns', level=0)

    copies.append(data)
    
  return reduce(lambda  acc, next: pd.merge(acc, next, left_index=True, right_index=True, how='inner'), copies)

def union(dfs, keys =['human', 'mouse']):
  return pd.concat(dfs, keys=keys)

def by_region(structure_df, value_column, region_column, structure_column):
  
  aggregations = Utils.get_sub_columns(structure_df, value_column)
  
  region = structure_df.dropna()
  region_agg = { agg: region[[(value_column, agg)]].reset_index().droplevel(1, axis=1) for agg in aggregations }

  agg_fns = { 'min': np.min, 'max': np.max, 'mean': np.mean, 'var': np.mean } # we need to aggregate the columns differently...

  for k, v in region_agg.items():
    v = v[[region_column, structure_column, value_column]].sort_values([region_column, value_column], ascending=False)
    # https://intellipaat.com/community/31330/pandas-number-rows-within-group
    v['rank'] = v.groupby([region_column]).cumcount() + 1
    v = pd.pivot_table(v, columns=['rank'], index=region_column, aggfunc=agg_fns[k]).droplevel(0, axis=1)
    
    # pandas sorts case-sensitive, but we don't want this. so:
    # https://stackoverflow.com/questions/30521994/how-to-sort-row-index-case-insensitive-way-in-pandas-dataframe
    region_agg[k] = v.reindex(sorted(v.index, key=lambda x: x.lower()))
  
  return region_agg

def coexpression(struct1, struct2):
  return pd.pivot_table(struct1, columns="structure_name").corrwith(pd.pivot_table(struct2, columns="structure_name"))