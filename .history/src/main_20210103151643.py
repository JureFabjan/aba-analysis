

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

# TODO: check NaN vs 0 and discuss with Jure: is it probable that some regions do not express ANY of gabra4?
# TODO: visualise on brain-map? 

# TODO: co-expression with beta- and gamma-subunits? => these only exist in chicken or zebrafishes (https://www.uniprot.org/uniprot/P34904, https://www.uniprot.org/uniprot/P24045)
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

# parameters
genes = ["Gabra4", "Gabrg3", "Gabrb3"]
aggregations = ['min', 'max', 'mean', 'var']
from_cache = True

human = Utils.simple({ g: HumanMicroarrayData(g).get(from_cache=from_cache, aggregations=aggregations) for g in genes})
mouse = Utils.simple({ g: MouseISHData(g).get(from_cache=from_cache, aggregations=aggregations) for g in genes})
  
# TODO is there any way to get the real z-score for mouse ISH-data??

column_mappings = { 
  'human': { Constants.GLOB_Z + '_' + 'human': 'human' }, 
  'mouse': { Constants.GLOB_Z + '_' + item.name: item.name.replace('_', ' ')  for item in mouse.Gabra4 } 
} 

human_gabra4 = human.Gabra4
mouse_gabra4 = mouse.Gabra4
# parameters for comparison
matchBy = 'acronym'

# ? comp contain joined data of human and mice. i.e. different species / experiments are provided as columns.
comp = Comparison.merge([human_gabra4] + mouse_gabra4, 'acronym', matchBy, Utils.intersect(HumanMicroarrayData.VALUE_COLUMNS, MouseISHData.VALUE_COLUMNS))

# remove verbose structural details and remove glob-z-prefix to improve readability:
comp = Utils.drop_columns_if(comp)

# remove glob_z-prefix ti also improve readability:
comp = comp.rename({ **column_mappings['human'], **column_mappings['mouse']},  axis='columns')

# we isolate aggregations in separate data-frames, stored in a dictionary. they can be accessed using the aggregation-name:
comp_agg = Utils.dict_by_agg(comp, aggregations, column_mappings)

# https://stackoverflow.com/questions/16228248/how-can-i-get-list-of-values-from-dict
Visualisation.heatmap_tiled(list(comp_agg.values()), 'Global z-scores per aggregation & donor', aggregations, 2, 2, 
 { 'left': 0.06, 'bottom': 0.125, 'right': 1, 'top': 0.925, 'wspace': 0.13, 'hspace': 0.365}, yticklabels=True)

# Visualisation.grid(comp.reset_index()) # reset_index to allow using acronym in an axis in the grid's grapher-tool

# coex_b3_a4 = Comparison.coexpression(human.Gabrb3.data.structure, human.Gabra4.data.structure)

# Functional partners according to https://string-db.org/network/9606.ENSP00000264318
# GABRG2, GABRB2
gabr_b3_a4 = Comparison.merge_coex(human.Gabrb3.data.structure, human.Gabra4.data.structure, ['gabrb3', 'gabra4'], ['structure_name', 'level_2']).reset_index()
gabr_b3_a4['shared_var'] = gabr_b3_a4[('expression_level_gabra4', 'var')] * gabr_b3_a4[('expression_level_gabrb3', 'var')]

Visualisation.scatter(Utils.unstack_columns(gabr_b3_a4), 
  x="expression_level_gabra4_mean", 
  y="expression_level_gabrb3_mean", 
  # TODO: would be cool if we could define two different size-columns, so that variances of both gene-expressions could be visualised in one point
  size="shared_var", sizes=(40,400), 
  hue="level_2", # hue is very slow when providing many different values. try to keep it coarsly grained, e.g. on larger scaled brain-structures
  legend = True) 

# TODO: merge using Comparison.merge, but allow additional level (coarser grained structure) to set hue.
#m_h_gabra4 = Comparison.merge_coex(human.Gabra4.data.structure, mouse.Gabra4[0].data.structure, ['human', 'mouse'], ['structure_name', 'level_2']).reset_index()
#m_h_gabra4['shared_var'] = m_h_gabra4[('global-z-score_human', 'var')] * m_h_gabra4[('global-z-score_mouse', 'var')]

# Visualisation.scatter(Utils.unstack_columns(comp.reset_index()), 
#   x="mouse 75551483 sagittal_mean", 
#   y="human_mean", 
#   #size="shared_var", sizes=(40,400), 
#   hue="acronym", # hue is very slow when providing many different values. try to keep it coarsly grained, e.g. on larger scaled brain-structures
#   legend = True) 

# sys.exit()

# expression levels, by fine-structure (structure_name) but grouped by brain region (level_3, e.g. hypothalamus)
h_by_region = Comparison.by_region(human_gabra4.data.structure, 'z-score', 'level_4', 'structure_name')
m_by_region = Comparison.by_region(mouse_gabra4[0].data.structure, 'global-z-score', 'level_4', 'structure_name')

# FormattedExport.to_excel(h_by_region['mean'], f'export\\human_mean_pivot_agg_gabra4.xlsx')

Visualisation.heatmap(h_by_region['mean'], f'Human - gabra4, z-score (mean)', 
  { 'left': 0.175, 'bottom': 0.095, 'right': 1, 'top': 0.967, 'wspace': 0.0, 'hspace': 0.0}, 
  xlabel="fine-structure's rank", ylabel="brain-region", yticklabels=True)

Visualisation.heatmap(m_by_region['mean'], f'Mouse - gabra4, z-score (mean)', 
  { 'left': 0.175, 'bottom': 0.095, 'right': 1, 'top': 0.967, 'wspace': 0.0, 'hspace': 0.0}, 
  xlabel="fine-structure's rank", ylabel="brain-region", yticklabels=True)

def export(human, mouse, gene):
  FormattedExport.to_excel(getattr(human, gene).data.structure, f'export\\human_agg_{gene}.xlsx') # , columns_and_rows_to_freeze='M2'
  
  mouse_gene = getattr(mouse, gene)
  for i in range(0, len(mouse_gene)):
    FormattedExport.to_excel(mouse_gene[i].data.structure, f'export\\{mouse_gene[i].name}_agg_{gene}.xlsx')

# https://binx.io/blog/2020/03/05/setting-python-source-folders-vscode/

# sys.exit()