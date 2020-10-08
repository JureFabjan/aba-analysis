
from allensdk.core.reference_space_cache import ReferenceSpaceCache
import pandas as pd

class StructureMap(reference_space_key, resolution):

    # from: https://allensdk.readthedocs.io/en/latest/_static/examples/nb/reference_space.html#Constructing-a-structure-tree
    # http://help.brain-map.org/display/api/Atlas+Drawings+and+Ontologies
    #reference_space_key = 'annotation/ccf_2017'
    #resolution = 25

    rspc = ReferenceSpaceCache(resolution, reference_space_key, manifest='manifest.json')
    # ID 1 is the adult mouse structure graph
    tree = rspc.get_structure_tree(structure_graph_id=1) 

    name_map = tree.get_name_map()
    # from https://datatofish.com/dictionary-to-dataframe/
    structure_map = pd.DataFrame(list(name_map.items()),columns = ['structure_id','structure_name']).set_index(['structure_id'])

    # we reverse the ancestors to always have the root in first position. from there, we descend into finer structures.
    # this way, we can have null-values for the root-nodes
    ancestor_map = pd.DataFrame([{
        "structure_id": k, 
        "ancestors": [name_map[id] for id in reversed(v)]} for k, v in tree.get_ancestor_id_map().items()])

    ancestor_map = ancestor_map.set_index(['structure_id'])

    # https://stackoverflow.com/questions/35491274/pandas-split-column-of-lists-into-multiple-columns
    ancestor_map = ancestor_map.ancestors.apply(pd.Series).add_prefix('level_')
    ancestor_map = ancestor_map.where(pd.notnull(ancestor_map), None)

    return structure_map.merge(ancestor_map, left_index=True, right_index=True, how="inner")