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
from HumanMicroarrayData import HumanMicroarrayData
from MouseISHData import MouseISHData

import Constants
import Utils

species_map ={ 'human': HumanMicroarrayData, 'mouse': MouseISHData, 'mouse - coronal': MouseISHData, 'mouse - sagittal': MouseISHData} 

# merge a list of data-frames using a shared column. this column will be used as the new index. 
# uses an inner join. does not mutate the original data-frames.
def merge(dfs, dataset, merge_on, shared_columns):

  copies = []

  for el in dfs:
    for name, el_data in el.items(): # we only have one key-value pair, which is the name & data
      # we need to join using the index. otherwise, the column will be renamed during merge.
      data = getattr(el_data, dataset).reset_index().set_index(merge_on) # assigning this to a new var prevents mutating the original data-frames

      data = data[shared_columns]
      # done discuss with Jure: do we need to know if a species / donor has no samples in a probe?
      # ! drop na is fine, count = 0 is import !!
      data = data.dropna() #data[data[(Constants.GLOB_Z, 'count')] > 0]

      # add_suffix is not suitable, as it would also affect sub-level columns (e.g. mean, var, etc. of expression-levels)
      # https://stackoverflow.com/questions/57740319/how-to-add-prefix-to-multi-index-columns-at-particular-level
      data = data.rename(mapper=lambda x: f'{x}_{name}', axis='columns', level=0)

      copies.append(data)
    
  return reduce(lambda  acc, next: pd.merge(acc, next, left_index=True, right_index=True, how='inner'), copies)


def union(dfs, keys =['human', 'mouse']):
  return pd.concat(dfs, keys=keys)

def by_region(structure_df, agg, value_column, region_column, structure_column):
  
  #aggregations = Utils.get_sub_columns(structure_df, value_column)
  
  region = structure_df.dropna()[[(value_column, agg)]].reset_index().droplevel(1, axis=1) 
  
  agg_fns = { 'min': np.min, 'max': np.max, 'mean': np.mean, 'var': np.mean } # we need to aggregate the columns differently...

  #for k, v in region_agg.items():
  region = region[[region_column, structure_column, value_column]].sort_values([region_column, value_column], ascending=True)
    # https://intellipaat.com/community/31330/pandas-number-rows-within-group
  region['rank'] = region.groupby([region_column]).cumcount() + 1
  region = pd.pivot_table(region, columns=['rank'], index=region_column, aggfunc=agg_fns[agg]).droplevel(0, axis=1)
    
    # pandas sorts case-sensitive, but we don't want this. so:
    # https://stackoverflow.com/questions/30521994/how-to-sort-row-index-case-insensitive-way-in-pandas-dataframe
  region = region.reindex(sorted(region.index, key=lambda x: x.lower()))
  
  return region

def merge_coex(struct1, struct2, genes, index_columns_to_keep = ['structure_name']):
  def simplify_index(s):
    return s.reset_index().set_index(index_columns_to_keep)[s.columns]

  return simplify_index(struct1).merge(simplify_index(struct2), left_index=True, right_index=True, suffixes=[ '_' + g for g in genes])

def findRegionAssignment(x, assignments, species):

  return None

def byDonor(human, mouse, agg, matchBy = 'acronym'):

  # TODO: by region mapping. matchBy "shared_acronym"
  # Constants.RegionAssignments
  # ? comp contain joined data of human and mice. i.e. different species / experiments are provided as columns.
  # raw=True in order to only receive the ndarray instead of a Series. this is much faster, according to:
  # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.apply.html#pandas.DataFrame.apply
  human['human'].structure['regionAssignment'] = human['human'].structure.reset_index().apply(findRegionAssignment, axis=1, raw=True, args=(Constants.RegionAssignments.asList, 'Human', ))

  comp = merge([human] + [mouse], 'acronym', matchBy, Utils.intersect(HumanMicroarrayData.VALUE_COLUMNS, MouseISHData.VALUE_COLUMNS))

  # remove verbose structural details and remove glob-z-prefix to improve readability:
  comp = Utils.drop_columns_if(comp)

  # remove glob_z-prefix ti also improve readability:
  comp = comp.rename({ **column_mappings(mouse)['human'], **column_mappings(mouse)['mouse']},  axis='columns')

  # we isolate the aggregation
  return comp[[(experiment, agg) for experiment in { **column_mappings(mouse)['human'], **column_mappings(mouse)['mouse']}.values()]].droplevel(1, axis=1) 
    

def coexpression(data1, data2, aggregation_function, structure_level, gene1, gene2): # hemisphere, 
  
  data = merge_coex(
    data1.structure,
    data2.structure,
    [gene1, gene2], ['structure_name', structure_level]).reset_index().dropna()

  data[f'shared_{aggregation_function}'] = data[(f'expression_level_{gene1}', aggregation_function)] * data[(f'expression_level_{gene2}', aggregation_function)] 

  return Utils.unstack_columns(data)

def column_mappings(mouse_data):
  
  return { 
      'human': { Constants.GLOB_Z + '_' + 'human': 'human' }, 
      'mouse': { Constants.GLOB_Z + '_' + k:k.replace('_', ' ') for k,v in mouse_data.items() }
    } 