from allensdk.api.queries.rma_api import RmaApi
from allensdk.api.cache import Cache

from types import SimpleNamespace

import numpy as np
import pandas as pd
import glob

import functools
import concurrent

import Utils
import Constants

from StructureMap import StructureMap

class HumanMicroarrayData:
  VALUE_COLUMNS = ['expression_level', 'z-score', Constants.GLOB_Z] 

  currentGets = {}
  
  def __init__(self, geneAcronym):
      self.geneAcronym = geneAcronym
      self.cache_path = Constants.DATAFRAME_CACHE + f'human\\{geneAcronym}\\'
  
  # ok, now we got n probes with m expression-levels & z-scores
  # we also got m samples that describe which donor and which structure each expression-level stems from
  # we have to be aware that the expression-levels are retrieved from a probe, which represents a plane through the brain.
  # so if the plane of the probe is not cutting through a specific brain-region, then there are null-values present for the expression-level.
  # details: http://help.brain-map.org/display/humanbrain/API

  # TODO: this is quite inefficient code. let's review it later
  #@Utils.profile(sort_by='cumulative', lines_to_print=10, strip_dirs=True)
  def transformExpressionData(self, expressionData):
    #print('HumanMicroarrayData.transformExpressionData() start')
    # this class allows us to add attributes to an object
    # https://docs.python.org/3/library/types.html#types.SimpleNamespace
    combined = SimpleNamespace()

    setattr(combined, 'samples', []) 
    setattr(combined, 'expression_levels', [])
    setattr(combined, 'z_scores', [])

    samples = expressionData["samples"] # we hereby prevent a dict-lookup for each probe, because its always the same data used over and over again

    #i = 1
    for probe in expressionData["probes"]:
      # https://stackoverflow.com/questions/30522724/take-multiple-lists-into-dataframe
      # we need to map each probe to the sample-annotations (see MicroarrayData_Readme.txt, provided by the Allen Institue).
      # so, we basically repeat the samples for each probe:
      combined.samples += samples

      # these are provided in the same strucutural manner
      combined.expression_levels += probe["expression_level"]
      combined.z_scores += probe["z-score"] # ! z-scores are NOT comparable with ISH-data for mice. these z-scores are only intended for isolated analysis!
      # see: https://community.brain-map.org/t/z-score-for-human-microarray-and-mouse-ish-data/912/3

      #np.savetxt(f"probe\\z-score_{i}.csv", np.asarray(probe["z-score"], dtype=np.float32), delimiter=",")
      #np.savetxt(f"probe\\expression_level_{i}.csv", np.asarray(probe["expression_level"], dtype=np.float32), delimiter=",")
      #i += 1

      # TODO: find out the right application of z-score to normalize correctly
      # also check: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4243026/#SD12
      combined.z_scores_log2 += Utils.z_score(np.log2(probe["z-score"]))
      print('z-scores', combined.z_scores)
      print('recalc', combined.z_scores_log2)

    # https://stackoverflow.com/questions/29325458/dictionary-column-in-pandas-dataframe
    data = pd.DataFrame({"expression_level": combined.expression_levels, "z-score": combined.z_scores},
                                dtype=np.float32) # setting this type is important for later aggregation. else, pandas throws an error for mean & var

    # the sample's metadata is stored as dictionary-entries. we unpack them using this function, in order to transform them into columns
    def unpack_dict_list(dict_list, attribute, prefix):
      # read it like this: each entry in a list of dictionaries (e.g. combined.samples) is mapped to isolate a specific attribute (e.g. 'structure')
      # then, create a dataframe from this list. lastly, add the provided prefix in order to prevent naming conflicts
      return pd.DataFrame.from_dict(map(lambda x: x[attribute], dict_list)).add_prefix(prefix) 

    # attributes with their respective prefix to prevent ambiguous column-names
    attributes = [("donor", ""), ("sample", "sample_"), ("structure", "structure_")] 

    # note that here, the * is the splat-operator. it is used to unpack the array produced by the list comprehension,
    # in order to provide pd.concat with a plain list of dataframes to concat.
    data = pd.concat([*[unpack_dict_list(combined.samples, attr[0], attr[1]) for attr in attributes], data], axis=1)

    # the z-scores provided here come with some side-notes, according to http://help.brain-map.org/display/humanbrain/API 
    # "Note: z-score is computed independently for each probe over all donors and samples."
    # ! But we don't have probes in ISH data for mice, so we would not be able to compare these numbers.
    # ! To get comparable numbers, we calculate a global z-score.
    # ! As there is only one donor per brain-region, we can simply use the expression_levels:
    data["global-z-score"] = Utils.z_score(data.expression_level)

    # dropna is super slow, so we use this approach instead:
    data = data[data['expression_level'].notnull() & data['z-score'].notnull() & data['global-z-score'].notnull()]

    #print('HumanMicroarrayData.transformExpressionData() done')
    return data 
  
  # @functools.lru_cache(maxsize= 128)
  def get(self, from_cache, aggregations):
  
    if from_cache:
      return self.getAsync(from_cache, aggregations)

    if self.geneAcronym in HumanMicroarrayData.currentGets:
      print(f'Waiting for initial request of human gene {self.geneAcronym} to complete...')
      done, not_done = concurrent.futures.wait([HumanMicroarrayData.currentGets[self.geneAcronym]], 
       return_when=concurrent.futures.FIRST_COMPLETED) # this wants an array... ok
      
      for fut in done:
        print(fut)
        return fut.result() #return HumanMicroarrayData.currentGets[self.geneAcronym].result()

    else: 
      with concurrent.futures.ThreadPoolExecutor() as executor:
        HumanMicroarrayData.currentGets[self.geneAcronym] = executor.submit(self.getAsync, from_cache, aggregations)
        return HumanMicroarrayData.currentGets[self.geneAcronym].result()

  # TODO: only allow one simultaneous call, e.g. with a dictionary per gene and something like a promise
  #@Utils.profile(sort_by='cumulative', lines_to_print=10, strip_dirs=True)
 
  def getAsync(self, from_cache, aggregations): # load data once with use_cache = True, then change it to False to read it from disk instead of fetching it from the api
    #print('HumanMicroarrayData.get() start')
    if not from_cache:
      # we use the RmaApi to query specific information, such as the section data sets of a specific gene
      # for docs, see: https://alleninstitute.github.io/AllenSDK/allensdk.api.queries.rma_api.html
      rma = RmaApi() 

      # the cache_writeer allows us to easily cache the results
      cache_writer = Cache()

      # ok, so we don't need to do multiple requests to forward data from a model to a service, but simply use the pipe-concept:
      # http://help.brain-map.org/display/api/Service+Pipelines
      # e.g. this finds all probes for gabra4 and then queries the microarray-expression data for these probes. note that variables generated by a pipe are referenced by $variableName

      # check out this playground: http://api.brain-map.org/examples/rma_builder/index.html
      query = ("http://api.brain-map.org/api/v2/data/query.json?criteria="
              f"model::Probe,rma::criteria,gene[acronym$il{self.geneAcronym}],rma::options[num_rows$eqall],"
              "pipe::list[probes$eq'id'],"
              "service::human_microarray_expression[probes$eq$probes]")

      data = cache_writer.wrap(
              rma.json_msg_query,
              path=Utils.makedir(f'cache\\human_microarray-expr\\{self.geneAcronym}') + '\\cache.json',
              cache=not from_cache, # the semantics of this function are a bit weird. providing True means: add it to the cache,
              url=query
          )
      
      structure_map, tree, annotation  = StructureMap(reference_space_key = 'annotation/ccf_2017', resolution = 25).get(structure_graph_id=10) # , annotation, meta 
      
      data = self.transformExpressionData(data)

      # https://stackoverflow.com/questions/19125091/pandas-merge-how-to-avoid-duplicating-columns
      # to avoid automatic renaming the duplicate columns by removing any duplicate-column
      # note that our merge-condition is index vs structure_id. because structure_id is the index of structure_map, 
      # it is not identified as a duplicate column.
      data = data[data.columns.difference(structure_map.columns)]

      ret = Utils.merge_with_structure(data, structure_map, HumanMicroarrayData.VALUE_COLUMNS, aggregations)
      
      Utils.save(ret, self.cache_path, 'cache.pkl')
      #print('HumanMicroarrayData.get() done')
      return { 'human': ret, } # , 'raw': data })

    else:
      if not glob.glob(self.cache_path):
        Utils.log.warning(f"No cached dataframe found. Check whether you have access to file '{self.cache_path}' and whether it exists. Obtaining data without caching now...")
        return self.get(False, aggregations)

      #print('HumanMicroarrayData.get() done')
      return { 'human': Utils.load(self.cache_path + 'cache.pkl') }
