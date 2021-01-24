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

species_map ={ 'human': HumanMicroarrayData, 'mouse': MouseISHData} 

# merge a list of data-frames using a shared column. this column will be used as the new index. 
# uses an inner join. does not mutate the original data-frames.
def merge(dfs, dataset, merge_on, shared_columns):

  copies = []

  for el in dfs:
    
    # we need to join using the index. otherwise, the column will be renamed during merge.
    data = getattr(el.data, dataset).reset_index().set_index(merge_on) # assigning this to a new var prevents mutating the original data-frames

    data = data[shared_columns]
    # done discuss with Jure: do we need to know if a species / donor has no samples in a probe?
    # ! drop na is fine, count = 0 is import !!
    data = data.dropna() #data[data[(Constants.GLOB_Z, 'count')] > 0]

    # add_suffix is not suitable, as it would also affect sub-level columns (e.g. mean, var, etc. of expression-levels)
    # https://stackoverflow.com/questions/57740319/how-to-add-prefix-to-multi-index-columns-at-particular-level
    data = data.rename(mapper=lambda x: f'{x}_{el.name}', axis='columns', level=0)

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

def merge_coex(struct1, struct2, genes, index_columns_to_keep = ['structure_name']):
  def simplify_index(s):
    return s.reset_index().set_index(index_columns_to_keep)[s.columns]

  return simplify_index(struct1).merge(simplify_index(struct2), left_index=True, right_index=True, suffixes=[ '_' + g for g in genes])


def byDonor(human, mouse, agg, matchBy = 'acronym'):

  # ? comp contain joined data of human and mice. i.e. different species / experiments are provided as columns.
  comp = merge([human] + mouse, 'acronym', matchBy, Utils.intersect(HumanMicroarrayData.VALUE_COLUMNS, MouseISHData.VALUE_COLUMNS))

  # remove verbose structural details and remove glob-z-prefix to improve readability:
  comp = Utils.drop_columns_if(comp)

  # remove glob_z-prefix ti also improve readability:
  comp = comp.rename({ **column_mappings(mouse)['human'], **column_mappings(mouse)['mouse']},  axis='columns')

  # we isolate the aggregation
  return comp[[(experiment, agg) for experiment in { **column_mappings(mouse)['human'], **column_mappings(mouse)['mouse']}.values()]].droplevel(1, axis=1) 
    

def coexpression(aggregation_function, structure_level, species, hemisphere, gene1, gene2):
  # human.Gabra4.data.structure

  if(gene1 == gene2):
    raise Exception("Co-expressions for the same gene of the same species make no sense and would lead to errors.")

  result1 = species_map[species](gene1).get(from_cache=True, aggregations=Constants.AGGREGATION_FUNCTIONS)
  result2 = species_map[species](gene2).get(from_cache=True, aggregations=Constants.AGGREGATION_FUNCTIONS)

  # TODO: maybe provide an option to select which plane of section should be used for mice, because got 2.
  # TODO: there we could allow comparison of the same gene and same species.
  if(species == 'mouse'):
    result1 = result1[0]
    result2 = result2[0]

  data = merge_coex(
    result1.data.structure,
    result2.data.structure,
    [gene1, gene2], ['structure_name', structure_level]).reset_index().dropna()

  data[f'shared_{aggregation_function}'] = data[(f'expression_level_{gene1.toLowerCase()}', aggregation_function)] * data[(f'expression_level_{gene2.toLowerCase()}', aggregation_function)] 

  return Utils.unstack_columns(data)

#  return pd.pivot_table(struct1, columns="structure_name").corrwith(pd.pivot_table(struct2, columns="structure_name"))

def column_mappings(mouse_data):
  return { 
      'human': { Constants.GLOB_Z + '_' + 'human': 'human' }, 
      'mouse': { Constants.GLOB_Z + '_' + item.name: item.name.replace('_', ' ')  for item in mouse_data } 
    } 