#from allensdk.api.queries.ontologies_api import OntologiesApi
#from allensdk.core.structure_tree import StructureTree
#from allensdk.api.queries.mouse_atlas_api import MouseAtlasApi
#from allensdk.core.reference_space_cache import ReferenceSpaceCache

import numpy as np
import pandas as pd

from pandasgui import show


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


from HumanMicroarrayData import HumanMicroarrayData
from MouseISHData import MouseISHData

geneAcronym = "Gabra4"

human = HumanMicroarrayData(geneAcronym).get(from_cache=True)
mouse = MouseISHData(geneAcronym).get(from_cache=True)

print(mouse)

print(human)

show(mouse[0], settings={'block': True})


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
