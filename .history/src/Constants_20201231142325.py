GLOB_Z = 'global-z-score'
EXPR_LVL = 'expression_level'
VALUE_COLUMNS = [EXPR_LVL,GLOB_Z] 

DATAFRAME_CACHE = "cache\\data-frames\\"

from allensdk.api.queries.rma_api import RmaApi
from allensdk.api.cache import Cache
import Utils

class allensdk:
  def __init__(self):
    rma = RmaApi() 

        # the cache_writeer allows us to easily cache the results
    cache_writer = Cache()
    query = ("http://api.brain-map.org/api/v2/data/query.xml?criteria=model::PlaneOfSection")

    data = cache_writer.wrap(
            rma.json_msg_query,
            path=Utils.makedir(f'cache\\models\\PlaneOfSection.json'),
            cache=True, # the semantics of this function are a bit weird. providing True means: add it to the cache,
            url=query
        )
    return data
