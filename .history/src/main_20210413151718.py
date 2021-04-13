

# load all experiments for mice and humans (=> rows), collect meta-data (sex, age, species, etc. => columns). then: get variance/std by meta-data and brain-region
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
# ! nope, ish data for human is only imaging data. 
#   probe -> annotation -> ontology
#            location ? tree-structure from parent to root

# TODO: check NaN vs 0 and discuss with Jure: is it probable that some regions do not express ANY of gabra4?
# fyi
# ------------------------------ 
# groupby poses an issue: donor-information for specific regions might vary => we cant group by donor-columns

# nice to have:
# ------------------------------
# single-cell rna-seq data.

# if rna-seq not possible => smoothen correlation of subunits using 3d-gaussian per voxel
# nth: check http://help.brain-map.org/display/devmouse/API -> are there any expression-levels without structureid as well? it is a decent fallback.
# nth: detailed microarray or sequencing would also be ok. single-cell is difficult.

# medical case given:
# ------------------------------
# epilepsy-patient has variant of GABRA4 => alpha 4 subunit. question: in which brain regions is this gabra4 mainly expressed??
# differences in expression between humans and mice => heatmap of brain-structures + the numbers, please. differences in age?
# eventually exclude opposing sex? 
# for human-data, only one donor is available for each brain-region (most likely). 
# mice: one mouse per gene => only one animal for gabra4...
# normalization?

import numpy as np
import pandas as pd 
import sys

# our code
from HumanMicroarrayData import HumanMicroarrayData
from MouseISHData import MouseISHData

import FormattedExport
import Comparison
import Visualisation
import Constants
import Utils

#gene = "Gabra4"
#aggregation_function = 'mean'

# human = HumanMicroarrayData(gene).get(from_cache=True, aggregations=Constants.AGGREGATION_FUNCTIONS)
# mouse = MouseISHData(gene).get(from_cache=True, aggregations=Constants.AGGREGATION_FUNCTIONS)
# Comparison.byDonor(
#       human, mouse,      
#       aggregation_function)

# sys.exit()
# TODO: https://medium.com/@vladbezden/new-python-project-configuration-with-vs-code-b41b77f7aed8

webApp = Visualisation.WebInterface(__name__) # 'Meduni Vienna ISH & Microarray data'
#webApp.open_browser()

webApp.run_server(debug=True)
sys.exit()

#Visualisation.grid(comp.reset_index()) # reset_index to allow using acronym in an axis in the grid's grapher-tool

def export(human, mouse, gene):
  FormattedExport.to_excel(getattr(human, gene).data.structure, f'export\\human_agg_{gene}.xlsx') # , columns_and_rows_to_freeze='M2'
  
  mouse_gene = getattr(mouse, gene)
  for i in range(0, len(mouse_gene)):
    FormattedExport.to_excel(mouse_gene[i].data.structure, f'export\\{mouse_gene[i].name}_agg_{gene}.xlsx')

# https://binx.io/blog/2020/03/05/setting-python-source-folders-vscode/