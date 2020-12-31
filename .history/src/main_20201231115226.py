

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

import glob
import numpy as np
import pandas as pd
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
aggregations = ['min', 'max', 'mean', 'var', 'count']
from_cache = True

if not from_cache or not glob.glob(cache_path_human):
  human = HumanMicroarrayData(geneAcronym).get(from_cache=from_cache, aggregations=aggregations)
  FormattedExport.to_excel(human, f'export\\human_agg_{geneAcronym}.xlsx') # , columns_and_rows_to_freeze='M2'

  Utils.save(human, cache_path_human)

  mouse = MouseISHData(geneAcronym).get(from_cache=from_cache, aggregations=aggregations) 
  for i in range(0, len(mouse)):
      FormattedExport.to_excel(mouse[i], f'export\\mouse_{i}_agg_{geneAcronym}.xlsx')
      Utils.save(mouse[i], cache_path_mouse + str(i))
 
else:
  human = Utils.load(cache_path_human)
  mouse = [Utils.load(file) for file in glob.glob(f'{cache_path_mouse}/*/')]

comp = Comparison.by(human, mouse[0], 'acronym')
FormattedExport.to_excel(comp, f'export\\human_mouse_{geneAcronym}.xlsx')

  #z_corr = comp[[(Constants.GLOB_Z + '_human', 'mean'), (Constants.GLOB_Z + '_mouse', 'mean'), ('acronym', '')]].corr()
agg ='mean'
groupBy = 'acronym'

  

flat_h = human.reset_index().set_index('acronym')[[(Constants.GLOB_Z,'mean')]]
flat_m = mouse[0].reset_index().set_index('acronym')[[(Constants.GLOB_Z,'mean')]]



# TODO: cache the results.
u = Comparison.union([flat_h, flat_m]).droplevel(1, axis=1) # remove sub-leveled label 'mean'

FormattedExport.to_excel(u, f'export\\human_mouse_union_{geneAcronym}.xlsx')

u_corr = u.dropna().reset_index().groupby(['level_0', 'acronym'])[[('global-z-score','mean')]].corr()

Visualisation.heatmap(u_corr)

c = comp[[(Constants.GLOB_Z + '_human', 'mean'), (Constants.GLOB_Z + '_mouse', 'mean'), ('acronym', '')]].droplevel(1, axis=1)
c = c.rename(columns={'global-z-score_human': 'human',  'global-z-score_mouse': 'mouse'})

c_piv = pd.pivot_table(c, columns=['acronym'], aggfunc=np.mean)
c_piv = c_piv.dropna(axis=1, how='any') # prevent division by zero
# TODO: check NaN vs 0 and discuss with Jure: is it probable that some regions do not express ANY of gabra4?

h_m_ratios =c_piv.loc['human', :] / c_piv.loc['mouse', :]

# TODO: visualise on brain-map? 
#c_piv.corr()

c.groupby('acronym')[['human','mouse']].corr()

#df = comp[[(Constants.GLOB_Z + '_human', 'mean'), (Constants.GLOB_Z + '_mouse', 'mean'), ('acronym', '')]]

# we flatten the data to make it more accesible:
# https://stackoverflow.com/questions/14507794/pandas-how-to-flatten-a-hierarchical-index-in-columns
#df.columns = df.columns.get_level_values(0)

# get correlations by structure:
# https://stackoverflow.com/questions/28988627/pandas-correlation-groupby
#z_corr = df.groupby(groupBy)[[Constants.GLOB_Z + '_human',Constants.GLOB_Z + '_mouse']].corr()
# we should compare the mean by region.
#print(z_corr)
#Visualisation.heatmap(z_corr)

# TODO: clarify - groupby poses an issue: donor-information for specific regions might vary => we cant group by donor-columns
# TODO: clarify - we got sagittal and coronal planes for mice. do we need both? for humans, no planes are specified (i guess microarray works differently).

#print(mouse)
#print(human)

#show(human, settings={'block': True})
#show(mouse[0], settings={'block': True})

# TODO: check ABA institute approach => works? fine! else: report bug and evaluate devmouse. fallback visualize microarray-data if possible.
# TODO: other databases for mice gene expression, preferably using in-situ hybridization => florian will send some links.

# TODO: check http://help.brain-map.org/display/devmouse/API -> are there any expression-levels without structureid as well? it is a decent fallback.
# TODO: detailed microarray or sequencing would also be ok. single-cell is difficult.


# https://binx.io/blog/2020/03/05/setting-python-source-folders-vscode/