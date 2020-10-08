
from allensdk.api.queries.rma_api import RmaApi
from allensdk.api.cache import Cache
from allensdk.api.queries.grid_data_api  import GridDataApi

import numpy as np
import pandas as pd

class MouseISHData:
    def __init__(self, geneAcronym):
        self.geneAcronym = geneAcronym

    def get(self):
        # we use the RmaApi to query specific information, such as the section data sets of a specific gene
        # for docs, see: https://alleninstitute.github.io/AllenSDK/allensdk.api.queries.rma_api.html
        rma = RmaApi() 

        # the cache_writeer allows us to easily cache the results
        cache_writer = Cache()
        use_cache = False # load data once with use_cache = True, then change it to False to read it from disk instead of fetching it from the api

        # http://api.brain-map.org/examples/rma_builder/index.html
        # http://api.brain-map.org/examples/rma_builder/rma_builder.html
        # https://allensdk.readthedocs.io/en/latest/data_api_client.html
        sectionDataSets = pd.DataFrame( # wrap is told to be deprecated, but there is no information on what to use instead :(
            cache_writer.wrap(rma.model_query,
                                path='cache\\section-data-sets.json',
                                cache=use_cache,
                                model='SectionDataSet',
                                filters={'failed':'false'},
                                include=f"genes[acronym$il{self.geneAcronym}],products[id$eq1]", # $il = case-insensitive like | yes, weird notation... id = 1 = mouse brain atlas (not developing!)
                                num_rows='all'))
        # model's documentation: http://api.brain-map.org/doc/SectionDataSet.html



        # there might be a way to retrieve data in higher resolution, as stated here (default is 25, 10 is also available - but resolution is ignored for download_gene_expression_grid_data)
        # https://alleninstitute.github.io/AllenSDK/_modules/allensdk/api/queries/grid_data_api.html
        # See `Downloading 3-D Projection Grid Data <http://help.brain-map.org/display/api/Downloading+3-D+Expression+Grid+Data#name="Downloading3-DExpressionGridData-DOWNLOADING3DPROJECTIONGRIDDATA">`_
        gdApi = GridDataApi()

        experiments = []


        #zipfile.ZipFile(request.urlretrieve(self.url)[0]).read("gridAnnotation.raw")))
        # http://help.brain-map.org/display/mousebrain/Documentation

        annotations = np.fromfile("annotations\\P56_Mouse_gridAnnotation\\gridAnnotation.raw", dtype="uint32")

        structure_map = StructureMap(reference_space_key = 'annotation/ccf_2017', resolution = 25).get()

        for index, row in sectionDataSets.iterrows(): # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
            exp_id = row['id']
            exp_path = f"data\\{exp_id}\\"
            try:
                gdApi.download_gene_expression_grid_data(exp_id, GridDataApi.ENERGY, exp_path)

                # According to the docs here: http://help.brain-map.org/display/api/Downloading+3-D+Expression+Grid+Data
                # we have "A raw uncompressed float (32-bit) little-endian volume representing average expression energy per voxel. A value of "-1" represents no data. This file is returned by default if the volumes parameter is null."
                # https://docs.python.org/3/library/struct.html
                # struct helps us to read binary data by providing the used format. here, it is little-endian (represented by "<") and a 32-bit 
                #energy = numpy.array(list(struct.iter_unpack("<f", open(exp_path + "energy.raw", "rb").read()))).flatten() # way too complicated, but there is a delta in mean and sum. what is the right value??
                #print(exp_id)
                data = pd.DataFrame({"expression_level": np.fromfile(exp_path + "energy.raw",  dtype=np.float32), "structure_id": annotations})

                # TODO: there is something wrong. some expression_levels are assigned to a structure of id 0. same is true for Jure's approach
                data = data[(data.expression_level != -1)] # (data.structure_id != 0) & ]
                #data = pd.DataFrame(np.fromfile(exp_path + "energy.raw",  dtype=np.float32))
                #data = data[]
                # https://stackoverflow.com/questions/31528819/using-merge-on-a-column-and-index-in-pandas
                
                # https://stackoverflow.com/questions/45147100/pandas-drop-columns-with-all-nans
                #experiments.append(data.merge(structure_map,  right_index=True, left_on="structure_id", how="inner").dropna(axis=1, how='all')) # we can use numpy.float32 or "<f"

                data = data.merge(structure_map,  right_index=True, left_on="structure_id", how="inner").dropna(axis=1, how='all')
                experiments.append(data.groupby([col for col in data.columns if 'level_' in col])['expression_level'].agg(['mean','var']))
            except Exception as e:
                print(f"Error retrieving experiment {exp_id}: {str(e)}")
        
        return experiments
