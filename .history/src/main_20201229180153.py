import numpy as np
import pandas as pd

from pandasgui import show

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
import FormattedExport

geneAcronym = "Gabra4"

# TODO: try nrrd http://help.brain-map.org/display/mouseconnectivity/API#API-DownloadAtlas
aggregations = ['min', 'max', 'mean', 'var', 'count']

# columns_and_rows_to_freeze='B2', 
human = HumanMicroarrayData(geneAcronym).get(from_cache=True, aggregations=aggregations)
FormattedExport.to_excel(human, f'export\\human_agg_{geneAcronym}.xlsx', columns_and_rows_to_freeze='M2')

#human.to_excel()

mouse = MouseISHData(geneAcronym).get(from_cache=True, aggregations=aggregations) 
mouse[0].to_excel(f'export\\mouse_0_agg_{geneAcronym}.xlsx')
mouse[1].to_excel(f'export\\mouse_1_agg_{geneAcronym}.xlsx')

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