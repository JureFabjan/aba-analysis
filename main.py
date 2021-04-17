

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

import sys

# our code
import Visualisation

webApp = Visualisation.WebInterface(__name__) 

webApp.run_server(debug=True)
sys.exit()
