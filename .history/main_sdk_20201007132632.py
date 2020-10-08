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

aggregations = ['min', 'max', 'count', 'mean','var']
human = HumanMicroarrayData(geneAcronym).get(from_cache=True, aggregations=aggregations)
#mouse = MouseISHData(geneAcronym).get(from_cache=True, aggregations=aggregations) 

# TODO: clarify - we got sagittal and coronal planes for mice. do we need both? for humans, no planes are specified (i guess microarray works differently).
#print(mouse)
#print(human)

#show(human, settings={'block': True})

human.to_excel(f'export\\human_{geneAcronym}.xlsx')
#show(mouse[0], settings={'block': True})

# https://allensdk.readthedocs.io/en/latest/_static/examples/nb/reference_space.html#Constructing-a-structure-tree
# http://help.brain-map.org/display/api/Atlas+Drawings+and+Ontologies#AtlasDrawingsandOntologies-StructuresAndOntologies
# http://help.brain-map.org/display/mousebrain/API#API-Expression3DGridsExpressionGridding
# http://help.brain-map.org/display/mousebrain/Documentation
# https://developingmouse.brain-map.org/static/atlas
# http://help.brain-map.org/pages/viewpage.action?pageId=2424836

#print(human.groupby('struct_name')[['expression_level', 'z-score']].agg(['min','max','mean','var']))

#print(human)

# this is a good usecase of using model_query
# https://download.alleninstitute.org/informatics-archive/september-2017/mouse_projection/download_projection_structure_unionize_as_csv.html