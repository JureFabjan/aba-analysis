import numpy as np

from geneEcomparison import Constants
from geneEcomparison.HumanMicroarrayData import HumanMicroarrayData

def test_human_uncached():
  result = get_human(False)
  
  assert not result is None
  assert not result['human'] is None

def test_human_cached():
  result = get_human(True)
  
  assert not result is None
  assert not result['human'] is None

def get_human(from_cache):
  return HumanMicroarrayData("Gabra4").get(from_cache=from_cache, aggregations=Constants.AGGREGATION_FUNCTIONS.data)
  
  
  