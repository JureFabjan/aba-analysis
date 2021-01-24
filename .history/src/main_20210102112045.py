

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

column_mappings = { 'human': { Constants.GLOB_Z + '_' + 'human': 'human' }, 'mouse': { item['name']: item['name'].replace('_', ' ')  for item in mouse } } 

# parameters for comparison
matchBy = 'acronym'

# ? comp contain joined data of human and mice. i.e. different species / experiments are provided as columns.
comp = Comparison.merge([human] + mouse, 'acronym', matchBy, Utils.intersect(HumanMicroarrayData.VALUE_COLUMNS, MouseISHData.VALUE_COLUMNS))

# remove verbose structural details and remove glob-z-prefix to improve readability:
comp = Utils.drop_columns_if(comp)

# remove glob_z-prefix ti also improve readability:
comp = comp.rename(column_mapping,  axis='columns')

# we isolate aggregations in separate data-frames, stored in a dictionary. they can be accessed using the aggregation-name:
comp_agg = { agg: comp[[(d, agg) for d in column_mapping.values()]].droplevel(1, axis=1) for agg in aggregations }

# https://stackoverflow.com/questions/16228248/how-can-i-get-list-of-values-from-dict
Visualisation.heatmap_tiled(list(comp_agg.values()), 'global z-scores', aggregations, 2, 2, 
 { 'left': 0.06, 'bottom': 0.125, 'right': 1, 'top': 0.95, 'wspace': 0.13, 'hspace': 0.365})

Visualisation.grid(comp.reset_index()) # reset_index to allow using acronym in an axis in the grid's grapher-tool

# TODO: expression levels by brain region

# TODO: check NaN vs 0 and discuss with Jure: is it probable that some regions do not express ANY of gabra4?
# TODO: visualise on brain-map? 




def export():
  FormattedExport.to_excel(human['data']['structure'], f'export\\human_agg_{geneAcronym}.xlsx') # , columns_and_rows_to_freeze='M2'
  # FormattedExport.to_excel(comp, f'export\\human_mouse_{geneAcronym}.xlsx')
  # FormattedExport.to_excel(comp_pivot, f'export\\human_mouse_pivot_{geneAcronym}.xlsx')

  for i in range(0, len(mouse)):
    FormattedExport.to_excel(mouse[i]['data']['structure'], f'export\\{mouse[i]["name"]}_agg_{geneAcronym}.xlsx')

# https://binx.io/blog/2020/03/05/setting-python-source-folders-vscode/