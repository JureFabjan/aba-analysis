
from allensdk.api.queries.rma_api import RmaApi
from allensdk.api.cache import Cache
from allensdk.api.queries.grid_data_api  import GridDataApi

from allensdk.api.queries.reference_space_api import ReferenceSpaceApi

import numpy as np
import pandas as pd

from pandasgui import show # for debbuging

import Utils
import Constants
from StructureMap import StructureMap

class MouseISHData:
    def __init__(self, geneAcronym):
        self.geneAcronym = geneAcronym

    def get(self, from_cache =, aggregations): # load data once with from_cache = False, then change it to True to read it from disk instead of fetching it from the api
        
        # we use the RmaApi to query specific information, such as the section data sets of a specific gene
        # for docs, see: https://alleninstitute.github.io/AllenSDK/allensdk.api.queries.rma_api.html
        rma = RmaApi() 
        
        # there might be a way to retrieve data in higher resolution, as stated here (default is 25, 10 is also available - but resolution is ignored for download_gene_expression_grid_data)
        # https://alleninstitute.github.io/AllenSDK/_modules/allensdk/api/queries/grid_data_api.html
        # See `Downloading 3-D Projection Grid Data <http://help.brain-map.org/display/api/Downloading+3-D+Expression+Grid+Data#name="Downloading3-DExpressionGridData-DOWNLOADING3DPROJECTIONGRIDDATA">`_
        gdApi = GridDataApi()

        # the cache_writeer allows us to easily cache the results
        cache_writer = Cache()        

        # http://api.brain-map.org/examples/rma_builder/index.html
        # http://api.brain-map.org/examples/rma_builder/rma_builder.html
        # https://allensdk.readthedocs.io/en/latest/data_api_client.html
        sectionDataSets = pd.DataFrame( # wrap is told to be deprecated, but there is no information on what to use instead :(
            cache_writer.wrap(rma.model_query,
                                path=Utils.makedir(f'cache\\mouse_section-datasets\\{self.geneAcronym}') + '\\cache.json',
                                cache=not from_cache, # the semantics of this function are a bit weird. providing True means: add it to the cache
                                model='SectionDataSet',
                                filters={'failed':'false'},
                                include=f"genes[acronym$il{self.geneAcronym}],products[id$eq1]", # $il = case-insensitive like | yes, weird notation... id = 1 = mouse brain atlas (not developing!)
                                num_rows='all'))
        # model's documentation: http://api.brain-map.org/doc/SectionDataSet.html
        # https://community.brain-map.org/t/attempting-to-download-substructures-for-coronal-p56-mouse-atlas/174/2

        experiments = []
        
        # http://help.brain-map.org/display/mousebrain/Documentation
        annotations = np.fromfile("annotations\\P56_Mouse_gridAnnotation\\gridAnnotation.raw", dtype="uint32")

        # https://community.brain-map.org/t/how-to-acquire-the-structure-label-for-the-expression-grid-data/150/4
        # for Mouse P56, structure_graph_id = 1 according to http://help.brain-map.org/display/api/Atlas+Drawings+and+Ontologies
        structure_map = StructureMap(reference_space_key = 'annotation/ccf_2017', resolution=25).get(structure_graph_id=1) # , annotation, meta 
        #show(structure_map, settings={'block': True})

        for index, row in sectionDataSets.iterrows(): # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
            exp_id = row['id']
            exp_path = f"data\\{exp_id}\\"

            # https://allensdk.readthedocs.io/en/latest/_static/examples/nb/reference_space.html#Constructing-a-structure-tree
            # TODO: this should allow us to circumvent having pre-packaged grid-annotations.
            # annotation, meta = rspc.get_annotation_volume()

            #refSp = ReferenceSpaceApi()
            #anns = refSp.download_mouse_atlas_volume(age=15, volume_type=GridDataApi.ENERGY, file_name=f'cache\\mouse_atlas_volume.zip')
            # http://help.brain-map.org/display/mousebrain/API
            
            try:
                gdApi.download_gene_expression_grid_data(exp_id, GridDataApi.ENERGY, exp_path)

                expression_levels = np.fromfile(exp_path + "energy.raw",  dtype=np.float32)
                
                # According to the doc @ http://help.brain-map.org/display/api/Downloading+3-D+Expression+Grid+Data
                # we have "A raw uncompressed float (32-bit) little-endian volume representing average expression energy per voxel. 
                # A value of "-1" represents no data. This file is returned by default if the volumes parameter is null."
                data = pd.DataFrame({"expression_level": expression_levels, "structure_id": annotations})

                # some expression_levels are assigned to a structure of id 0. same is true for Jure's approach.
                # according to the Allen institue, this is just due to background-noise: 
                # https://community.brain-map.org/t/how-to-acquire-the-structure-label-for-the-expression-grid-data/150/4
                # values of -1 mean "no value"
                data = data[(data.expression_level != -1) & (data.structure_id != 0)]

                data["global-z-score"] = Utils.z_score(data.expression_level)

                # https://stackoverflow.com/questions/31528819/using-merge-on-a-column-and-index-in-pandas
                # https://stackoverflow.com/questions/45147100/pandas-drop-columns-with-all-nans                

                data = Utils.merge_with_structure(data, structure_map, Utils.VALUE_COLUMNS, aggregations)

                experiments.append({ 'data': data, 'name': f'mouse_{exp_id}_{Constants.PlaneOfSections[row["plane_of_section_id"]]}'})
            except Exception as e:
                print(f"Error retrieving mouse-ish experiment {exp_id}: {str(e)}")
        
        return experiments
