
from allensdk.core.reference_space_cache import ReferenceSpaceCache
import pandas as pd

class StructureMap:
    def __init__(self, reference_space_key, resolution):
        self.reference_space_key = reference_space_key
        self.resolution = resolution

    
    def get(self, structure_graph_id):
        # from: https://allensdk.readthedocs.io/en/latest/_static/examples/nb/reference_space.html#Constructing-a-structure-tree
        # http://help.brain-map.org/display/api/Atlas+Drawings+and+Ontologies
        #reference_space_key = 'annotation/ccf_2017'
        #resolution = 25

        # ! we need to use different FOLDERS for each structure-graph. else, structures.json gets overwritten by the last retrieved species/graph-id. yikes...
        rspc = ReferenceSpaceCache(self.resolution, self.reference_space_key, manifest=f'cache\\reference_space\\{structure_graph_id}\\cache.json')
        tree = rspc.get_structure_tree(structure_graph_id=structure_graph_id) 
        annotation, meta = rspc.get_annotation_volume()

        # https://allensdk.readthedocs.io/en/latest/_static/examples/nb/reference_space.html
        name_map = tree.get_name_map()
        # from the readthedocs.io-sample:
        acronym_map = tree.value_map(lambda x: x['id'], lambda y: y['acronym'])
        
        # from https://datatofish.com/dictionary-to-dataframe/
        structure_map = pd.DataFrame(list(name_map.items()), columns = ['structure_id','structure_name']).set_index(['structure_id'])

        structure_map['acronym'] = structure_map.index.map(acronym_map)

        # this transforms the ancestor_id_map into a dataframe containing the structure_id and the respective ancestors.
        ancestor_map = pd.DataFrame([{
            "structure_id": k, 
            # ancestors of a structure are obtained as a list, using get_ancestor_id_map()
            # but instead of the ancestor's id, we want the name. hence, we lookup using the name_map
            "ancestors": [name_map[id] for id in reversed(v)] # we reverse the ancestors to always have the root in first position. 
            # from there, we go into finer structures from left to right. this way, we can have null-values for the root-nodes
            } for k, v in tree.get_ancestor_id_map().items()])

        ancestor_map = ancestor_map.set_index(['structure_id'])

        # ancestors are stored as a list in one column. but we want separate columns for each ancestor-level:
        # https://stackoverflow.com/questions/35491274/pandas-split-column-of-lists-into-multiple-columns
        ancestor_map = ancestor_map.ancestors.apply(pd.Series).add_prefix('level_')
        ancestor_map = ancestor_map.where(pd.notnull(ancestor_map), None)

        return (structure_map.merge(ancestor_map, left_index=True, right_index=True, how="left").sort_index(), annotation)