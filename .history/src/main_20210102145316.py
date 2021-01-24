

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
# ! nope, ish data for human is only imaging data. 
#   probe -> annotation -> ontology
#            location ? tree-structure from parent to root

# fyi
# ------------------------------ 
# groupby poses an issue: donor-information for specific regions might vary => we cant group by donor-columns

# nice to have:
# ------------------------------
# single-cell rna-seq data.
# co-expression with beta- and gamma-subunits?
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

# our code
from HumanMicroarrayData import HumanMicroarrayData
from MouseISHData import MouseISHData
import FormattedExport
import Comparison
import Visualisation
import Constants
import Utils

# parameters
geneAcronym = "Gabra4"
aggregations = ['min', 'max', 'mean', 'var']
from_cache = True

human = HumanMicroarrayData(geneAcronym).get(from_cache=from_cache, aggregations=aggregations)
mouse = MouseISHData(geneAcronym).get(from_cache=from_cache, aggregations=aggregations) 

column_mappings = { 
  'human': { Constants.GLOB_Z + '_' + 'human': 'human' }, 
  'mouse': { Constants.GLOB_Z + '_' + item['name']: item['name'].replace('_', ' ')  for item in mouse } 
} 


# parameters for comparison
matchBy = 'acronym'

# ? comp contain joined data of human and mice. i.e. different species / experiments are provided as columns.
comp = Comparison.merge([human] + mouse, 'acronym', matchBy, Utils.intersect(HumanMicroarrayData.VALUE_COLUMNS, MouseISHData.VALUE_COLUMNS))

# remove verbose structural details and remove glob-z-prefix to improve readability:
comp = Utils.drop_columns_if(comp)

# remove glob_z-prefix ti also improve readability:
comp = comp.rename({ **column_mappings['human'], **column_mappings['mouse']},  axis='columns')

# we isolate aggregations in separate data-frames, stored in a dictionary. they can be accessed using the aggregation-name:
comp_agg = { agg: comp[[(experiment, agg) for experiment 
  in { **column_mappings['human'], **column_mappings['mouse']}.values()]].droplevel(1, axis=1) 
    for agg 
      in aggregations }

# https://stackoverflow.com/questions/16228248/how-can-i-get-list-of-values-from-dict
Visualisation.heatmap_tiled(list(comp_agg.values()), 'Global z-scores per aggregation & donor', aggregations, 2, 2, 
 { 'left': 0.06, 'bottom': 0.125, 'right': 1, 'top': 0.925, 'wspace': 0.13, 'hspace': 0.365}, yticklabels=True)

# Visualisation.grid(comp.reset_index()) # reset_index to allow using acronym in an axis in the grid's grapher-tool

# expression levels, by fine-structure (structure_name) but grouped by brain region (level_3, e.g. hypothalamus)
h_by_region = Comparison.by_region(human['data']['structure'], 'z-score', 'level_3', 'structure_name')
# mean_pivot['level_3'] = mean_pivot['level_3'].to_string()

FormattedExport.to_excel(h_by_region['mean'], f'export\\human_mean_pivot_agg_{geneAcronym}.xlsx')

Visualisation.heatmap(h_by_region['var'], f'Human - {geneAcronym}, z-score (var)', 
{ 'left': 0.175, 'bottom': 0.095, 'right': 1, 'top': 0.967, 'wspace': 0.0, 'hspace': 0.0}, 
xlabel="fine-structure's rank", ylabel="brain-region", yticklabels=True)
# Visualisation.grid(mean_pivot)
# TODO: check NaN vs 0 and discuss with Jure: is it probable that some regions do not express ANY of gabra4?
# TODO: visualise on brain-map? 

def export():
  FormattedExport.to_excel(human['data']['structure'], f'export\\human_agg_{geneAcronym}.xlsx') # , columns_and_rows_to_freeze='M2'
  # FormattedExport.to_excel(comp, f'export\\human_mouse_{geneAcronym}.xlsx')
  # FormattedExport.to_excel(comp_pivot, f'export\\human_mouse_pivot_{geneAcronym}.xlsx')

  for i in range(0, len(mouse)):
    FormattedExport.to_excel(mouse[i]['data']['structure'], f'export\\{mouse[i]["name"]}_agg_{geneAcronym}.xlsx')

# https://binx.io/blog/2020/03/05/setting-python-source-folders-vscode/