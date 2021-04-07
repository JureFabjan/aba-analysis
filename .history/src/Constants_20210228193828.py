
from allensdk.api.queries.rma_api import RmaApi
from allensdk.api.cache import Cache

import pandas as pd
import numpy as np

import Utils
import copy 

GLOB_Z = 'global-z-score'
EXPR_LVL = 'expression_level'
VALUE_COLUMNS = [EXPR_LVL,GLOB_Z] 

DATAFRAME_CACHE = "cache\\data-frames\\"

# ! here, some magic happens. these lists define - amongst the available options in dropdowns, their labels, and defaults - also some interactions with the charts.
# ! the type defines the named parameter that is provided to the chart-functions. 
GENE_LIST = Utils.simple({ 'label': 'Gene', 'type': 'gene', 'default' : 'Gabra4', 'defaultLeft':'Gabra4', 'defaultRight':'Gabrb3', 'data': ["Gabra1", "Gabra2", "Gabra4", "Gabra5", "Gabrb1", "Gabrb2", "Gabrb3", "Gabrd", "Gabrg2", "Gabrg3"] })
# for co-expressions, we need additional gene-selection. this ensure that the type is correctly bound to the expected parameters
GENE1_LIST = copy.copy(GENE_LIST)
GENE1_LIST.type =  'gene1'
GENE1_LIST.defaultLeft =  'Gabra4'
GENE1_LIST.defaultRight =  'Gabra5'

GENE2_LIST = copy.copy(GENE_LIST)
GENE2_LIST.type =  'gene2'
GENE2_LIST.defaultLeft = 'Gabrb2'
GENE2_LIST.defaultRight = 'Gabrb3'
GENE2_LIST.label = 'vs'


AGGREGATION_FUNCTIONS = Utils.simple({ 'label': 'Aggregation function', 'type': 'aggregation_function', 'default': 'mean', 'defaultLeft': 'mean', 'defaultRight': 'var', 'data': ['min', 'max', 'mean', 'var'] })
HEMISPHERES = Utils.simple({ 'label': 'Hemisphere', 'type': 'hemisphere', 'default': 'both', 'defaultLeft': 'both', 'defaultRight': 'both', 'data': ['left', 'right', 'both'] })
SPECIES = Utils.simple({ 'label': None, 'type': 'species', 'default': 'human', 'defaultLeft': 'human', 'defaultRight': 'mouse - sagittal', 'data': ['human', 'mouse - sagittal', 'mouse - coronal']})
STRUCTURE_LEVELS = Utils.simple({ 'label': 'Level', 'type': 'structure_level', 'default': 2, 'defaultLeft': 2, 'defaultRight': 2, 'data': [l for l in range(0,10)] })

AGGREGATION_AGGREGATES = { 'min': np.min, 'max': np.max, 'mean': np.mean, 'var': np.mean }

class AllenSdkHelper:
  def __init__(self):
    self.rma = RmaApi() 

        # the cache_writeer allows us to easily cache the results
    self.cache_writer = Cache()

    self.PlaneOfSections = self.cache_writer.wrap(
            self.rma.json_msg_query,
            path=Utils.makedir(f'cache\\models') + '\\PlaneOfSection.json',
            cache=False, # the semantics of this function are a bit weird. providing True means: add it to the cache,
            url="http://api.brain-map.org/api/v2/data/query.json?criteria=model::PlaneOfSection,rma::options[num_rows$eqall]"
        )

  def getPlaneOfSections(self):
    return self.PlaneOfSections

allenSdkHelper = AllenSdkHelper()

PlaneOfSections = {x['id']: x['name'] for x in allenSdkHelper.getPlaneOfSections()} 

RegionAssignments = pd.DataFrame.from_dict(
  pd.read_excel('annotations\\region assignment.xlsx') # TODO use csv instead
  .apply(lambda x: 
    { f"{species}_{x[species].split(';')[0]}": x[species].split(';')[1] 
    for species in ['Human', 'Mouse'] } ,axis=1)
    )[0].apply(pd.Series)

