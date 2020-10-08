from allensdk.api.queries.ontologies_api import OntologiesApi
from allensdk.api.queries.grid_data_api  import GridDataApi
from allensdk.core.structure_tree import StructureTree
from allensdk.api.queries.mouse_atlas_api import MouseAtlasApi
from allensdk.core.reference_space_cache import ReferenceSpaceCache

import numpy as np
import pandas as pd

from urllib import request

from pandasgui import show

from StructureMap import StructureMap
from HumanMicroarrayData import HumanMicroarrayData

# https://python-reference.readthedocs.io/en/latest/docs/operators/index.html
# https://github.com/benfulcher/AllenSDK
# http://help.brain-map.org/display/api/Atlas+Drawings+and+Ontologies


# TODO: load all experiments for mice and humans (=> rows), collect meta-data (sex, age, species, etc. => columns). then: get variance/std by meta-data and brain-region
# meta-data model definition: http://api.brain-map.org/doc/Donor.html
# how do i get a list of all experiments? => http://help.brain-map.org/display/api/Example+Queries+for+Experiment+Metadata
# http://help.brain-map.org/display/api/Allen%2BBrain%2BAtlas%2BAPI
# https://portal.brain-map.org/explore/transcriptome
# how do i get the 20 microm data? => 3-D PROJECTION GRID DATA is available in: 10, 25, 50, and 100 (in microns).
# https://wiki.mouseimaging.ca/ => https://wiki.mouseimaging.ca/display/MICePub/Mouse+Brain+Atlases

# https://allensdk.readthedocs.io/en/latest/allensdk.api.queries.grid_data_api.html
# https://allensdk.readthedocs.io/en/latest/data_api_client.html
# correlation of gabra4 expression in % for humans vs mice
# expression levels by brain region (also by species)
# comparison triangle: in situ human - microarray human - in situ mice
#   probe -> annotation -> ontology
#            location ? tree-structure from parent to root

# nice to have:
# ------------------------------
# single-cell rna-seq data.
# co-expression with beta- and gamma-subunits?
# if rna-seq not possible => smoothen correlation of subunits using 3d-gaussian per voxel

# medical case given:
# ------------------------------
# epilepsy-patient has variant of GABRA4 => alpha 4 subunit. question: in which brain regions is this gabra4 mainly expressed??
# differences in expression between humans and mice => heatmap of brain-structures + the numbers, please. differences in age?
# eventually exclude opposing sex? 
# for human-data, only one donor is available for each brain-region (most likely). 
# mice: one mouse per gene => only one animal for gabra4...
# normalization?

geneAcronym = "Gabra4"


human = HumanMicroarrayData(geneAcronym).get()


#print(human.groupby('struct_name')[['expression_level', 'z-score']].agg(['min','max','mean','var']))

#print(human)

# this is a good usecase of using model_query
# https://download.alleninstitute.org/informatics-archive/september-2017/mouse_projection/download_projection_structure_unionize_as_csv.html

#oapi = OntologiesApi()
#structure_graph = oapi.get_structures_with_sets([1])  # 1 is the id of the adult mouse structure graph

# This removes some unused fields returned by the query
#structure_graph = StructureTree.clean_structures(structure_graph)  

#tree = StructureTree(structure_graph)
#print(tree.parents([1011]))

# some list of experiments with gene-search
# http://www.brainspan.org/ish/search/show?page_num=0&page_size=35&no_paging=false&search_term=H376.IV.03.R&search_type=advanced&facet_specimen_hemisphere=right


# http://api.brain-map.org/examples/rma_builder/index.html
# http://api.brain-map.org/examples/rma_builder/rma_builder.html
# https://allensdk.readthedocs.io/en/latest/data_api_client.html
sectionDataSets = pd.DataFrame( # wrap is told to be deprecated, but there is no information on what to use instead :(
    cache_writer.wrap(rma.model_query,
                        path='cache\\section-data-sets.json',
                        cache=use_cache,
                        model='SectionDataSet',
                        filters={'failed':'false'},
                        include=f"genes[acronym$il{geneAcronym}],products[id$eq1]", # $il = case-insensitive like | yes, weird notation... id = 1 = mouse brain atlas (not developing!)
                        num_rows='all'))
# model's documentation: http://api.brain-map.org/doc/SectionDataSet.html
print(sectionDataSets)


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

print(experiments)

show(experiments[0], settings={'block': True})


# https://github.com/quantopian/qgrid

# https://pypi.org/project/pandasgui/


# https://allensdk.readthedocs.io/en/latest/_static/examples/nb/reference_space.html#Constructing-a-structure-tree
# http://help.brain-map.org/display/api/Atlas+Drawings+and+Ontologies#AtlasDrawingsandOntologies-StructuresAndOntologies
# http://help.brain-map.org/display/mousebrain/API#API-Expression3DGridsExpressionGridding
# http://help.brain-map.org/display/mousebrain/Documentation
# https://developingmouse.brain-map.org/static/atlas
# http://help.brain-map.org/pages/viewpage.action?pageId=2424836

# we only have 2 experiments for gabra4, right?
# https://mouse.brain-map.org/search/show?page_num=0&page_size=34&no_paging=false&exact_match=false&search_term=gaba%20alpha%204&search_type=gene
# mice: 75551483, 71924402

# mouseAtlasApi = MouseAtlasApi()
