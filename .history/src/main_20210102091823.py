

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

import glob
import numpy as np
import pandas as pd
import os
from pandasgui import show


# our code
from HumanMicroarrayData import HumanMicroarrayData
from MouseISHData import MouseISHData
import FormattedExport
import Comparison
import Visualisation
import Constants
import Utils

geneAcronym = "Gabra4"

cache_path_human = Constants.DATAFRAME_CACHE + f'human\\{geneAcronym}\\'
cache_path_mouse = Constants.DATAFRAME_CACHE + f'mouse\\{geneAcronym}\\'

# TODO: try nrrd http://help.brain-map.org/display/mouseconnectivity/API#API-DownloadAtlas
aggregations = ['min', 'max', 'mean', 'var']
from_cache = True

human = HumanMicroarrayData(geneAcronym).get(from_cache=from_cache, aggregations=aggregations)
mouse = MouseISHData(geneAcronym).get(from_cache=from_cache, aggregations=aggregations) 
      
# TODO: expression levels by brain region (also by species)
matchBy = 'acronym'


# human['data'].reset_index().set_index(matchBy)[['z-score']]

#flat_h = human['data'].reset_index().set_index(matchBy)[[(Constants.GLOB_Z,'mean')]]
#flat_m = [m['data'].reset_index().set_index(matchBy)[[(Constants.GLOB_Z,'mean')]] for m in mouse]
#u = Comparison.union([flat_h, flat_m]).droplevel(1, axis=1) # remove sub-leveled label 'mean'
#FormattedExport.to_excel(u, f'export\\human_mouse_union_{geneAcronym}.xlsx')
#u_corr = u.dropna().reset_index().groupby(['level_0', matchBy])[[('global-z-score','mean')]].corr()
#Visualisation.heatmap(u_corr)

# ? comp contain joined data of human and mice. i.e. different species / experiments are provided as columns.
comp = Comparison.merge([human] + mouse, matchBy, Utils.intersection(HumanMicroarrayData.VALUE_COLUMNS, MouseISHData.VALUE_COLUMNS))
# remove verbose structural details and remove glob-z-prefix to improve readability:
comp = Utils.drop_columns_if(comp).rename({ Constants.GLOB_Z + '_' + item['name']: item['name'] for item in ([human] + mouse) })

# pivot data to get brain-regions as columns and species / experiments as rows. 
#comp_pivot = pd.pivot_table(comp, columns=[matchBy], aggfunc=np.mean)
#comp_pivot_agg = { agg: comp_pivot.iloc[comp_pivot.index.get_level_values(1) == agg].droplevel(1, axis=0) for agg in aggregations }
comp_pivot_agg = { agg: comp.droplevel(1, axis=1) for agg in aggregations }

# comp_pivot_agg_ratios = { agg: comp_pivot_agg[agg] for agg in aggregations}
#for agg in aggregations:
#  Visualisation.heatmap(comp_pivot_agg[agg], agg)

# https://stackoverflow.com/questions/16228248/how-can-i-get-list-of-values-from-dict
Visualisation.heatmap_tiled(list(comp_pivot_agg.values()), 'global z-scores', aggregations, 2, 2)

# TODO: check NaN vs 0 and discuss with Jure: is it probable that some regions do not express ANY of gabra4?
# TODO: visualise on brain-map? 

#df = comp[[(Constants.GLOB_Z + '_human', 'mean'), (Constants.GLOB_Z + '_mouse', 'mean'), ('acronym', '')]]

# we flatten the data to make it more accesible:
# https://stackoverflow.com/questions/14507794/pandas-how-to-flatten-a-hierarchical-index-in-columns
#df.columns = df.columns.get_level_values(0)

# TODO: clarify - groupby poses an issue: donor-information for specific regions might vary => we cant group by donor-columns
# TODO: clarify - we got sagittal and coronal planes for mice. do we need both? for humans, no planes are specified (i guess microarray works differently).

#show(human, settings={'block': True})
#show(mouse[0], settings={'block': True})

def export():
  FormattedExport.to_excel(human['data'], f'export\\human_agg_{geneAcronym}.xlsx') # , columns_and_rows_to_freeze='M2'
  # FormattedExport.to_excel(comp, f'export\\human_mouse_{geneAcronym}.xlsx')
  # FormattedExport.to_excel(comp_pivot, f'export\\human_mouse_pivot_{geneAcronym}.xlsx')

  for i in range(0, len(mouse)):
    FormattedExport.to_excel(mouse[i]['data'], f'export\\{mouse[i]["name"]}_agg_{geneAcronym}.xlsx')

  

# https://binx.io/blog/2020/03/05/setting-python-source-folders-vscode/

