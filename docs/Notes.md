

IMPORTANT:
A probe is a plane through the brain in order to detect a specific gene. It contains normalized expression levels and the z-score for each element of the samples-array. "The z-score is computed independently for each probe over all donors and samples." Check out http://help.brain-map.org/display/humanbrain/API for more information.

For extending the code used to retrive microarray-data (human), use the http://api.brain-map.org/examples/rma_builder/index.html

To force a reload and process data anew, delete one or multiple gene-specific folders in cache\data-frames\mouse or cache\data-frames\human, respectively.

if rna-seq not possible => smoothen correlation of subunits using 3d-gaussian per voxel

load all experiments for mice and humans (=> rows), collect meta-data (sex, age, species, etc. => columns). then: get variance/std by meta-data and brain-region
meta-data model definition: http://api.brain-map.org/doc/Donor.html
how do i get a list of all experiments? => http://help.brain-map.org/display/api/Example+Queries+for+Experiment+Metadata
http://help.brain-map.org/display/api/Allen%2BBrain%2BAtlas%2BAPI
https://portal.brain-map.org/explore/transcriptome
https://wiki.mouseimaging.ca/ => https://wiki.mouseimaging.ca/display/MICePub/Mouse+Brain+Atlases
https://allensdk.readthedocs.io/en/latest/allensdk.api.queries.grid_data_api.html
https://allensdk.readthedocs.io/en/latest/data_api_client.html


groupby poses an issue: donor-information for specific regions might vary => we cant group by donor-columns

Fyi
http://neuroexpresso.org/
http://atlas.brain-map.org/atlas?atlas=138322605#atlas=138322605&plate=112360888&structure=13230&x=23424&y=53120&zoom=-7&resolution=124.49&z=3

https://stackoverflow.com/questions/32639074/why-am-i-getting-importerror-no-module-named-pip-right-after-installing-pip


https://dash.plotly.com/installation

https://community.brain-map.org/t/what-is-the-z-score-reference-value-in-rnaseq-gbm-data/513
http://help.brain-map.org/display/humanbrain/API


https://community.brain-map.org/t/transcriptomics-rna-seq-microarray-data-normalization-faq/182

                      probes
human microarray data [1,2,3.. z-score:  mean:2, var: 1] [1,4,7, z-score: mean: 4, var:3] [ ] ... ]
ish mouse data        [1,2,3,4,7, z-score: mean:4, var: 2               ]

this video helps to clarify the microarray-approach and explains what a probe actually is: https://www.youtube.com/watch?v=Hv5flUOsE0s



According to WholeBrainMicroarray_WhitePaper.pdf:
For two brains (H0351.2001 and H0351.2002), samples were collected from both hemispheres (cerebral,
cerebellar and both sides of brainstem). Otherwise, samples for microarray were collected from the left
cerebral and cerebellar hemispheres and left brainstem.

https://test.pypi.org/manage/project/geneecomparison/releases/




pip install -i https://test.pypi.org/simple/ geneEcomparison==0.0.15 --extra-index-url https://pypi.org/simple

pip install -i https://test.pypi.org/simple/ geneEcomparison==0.0.3


https://stackoverflow.com/questions/16425434/how-to-create-a-python-package-with-multiple-files-without-subpackages



install package for testing:
pip install -e .

uninstall package:
python setup.py develop -u



https://python-reference.readthedocs.io/en/latest/docs/operators/index.html
https://github.com/benfulcher/AllenSDK
http://help.brain-map.org/display/api/Atlas+Drawings+and+Ontologies

this is a good usecase of using model_query
https://download.alleninstitute.org/informatics-archive/september-2017/mouse_projection/download_projection_structure_unionize_as_csv.html

https://allensdk.readthedocs.io/en/latest/_static/examples/nb/reference_space.html#Constructing-a-structure-tree
http://help.brain-map.org/display/api/Atlas+Drawings+and+Ontologies#AtlasDrawingsandOntologies-StructuresAndOntologies
http://help.brain-map.org/display/mousebrain/API#API-Expression3DGridsExpressionGridding
http://help.brain-map.org/display/mousebrain/Documentation
https://developingmouse.brain-map.org/static/atlas
http://help.brain-map.org/pages/viewpage.action?pageId=2424836

https://github.com/hms-dbmi/brainmapr/blob/master/README_data.md

https://github.com/UCI-CARL/ABADV/blob/master/query.js
http://sciviscontest.ieeevis.org/2013/VisContest/index.html

https://github.com/UCI-CARL/ABADV/blob/master/query.js => line 100

# usefull links:

https://alleninstitute.github.io/AllenSDK/examples.html
https://community.brain-map.org/t/allen-mouse-ccf-accessing-and-using-related-data-and-tools/359
https://github.com/AllenInstitute/AllenSDK/blob/master/allensdk/api/queries/image_download_api.py


# accessing microarray-data:
https://github.com/benfulcher/AllenSDK
https://human.brain-map.org/microarray/search/show?exact_match=false&search_term=gabra4&search_type=gene
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5777841/
http://help.brain-map.org/display/api/Connected+Services+and+Pipes





# ratios = [
#   pd.DataFrame({'human/' + m['name']: comp_pivot.loc[Constants.Z_SCORE + '_' + human['name'], :] 
#   / comp_pivot.loc[Constants.Z_SCORE + '_' + m['name'], :]})
#   for m in mouse  
# ]
#   'human/' + m['name']: comp_pivot.loc[Constants.Z_SCORE + '_' + human['name'], :] / comp_pivot.loc[Constants.Z_SCORE + '_' +m['name'], :] for m in mouse  
#   })

# print(ratios)
#Visualisation.heatmap(comp_pivot)

TODO: try nrrd http://help.brain-map.org/display/mouseconnectivity/API#API-DownloadAtlas


# rna-seq
https://maayanlab.cloud/Harmonizome/dataset/Allen+Brain+Atlas+Developing+Human+Brain+Tissue+Gene+Expression+Profiles+by+RNA-seq
https://community.brain-map.org/t/reading-rna-seq-data-into-python/658

https://medium.com/analytics-vidhya/optimized-ways-to-read-large-csvs-in-python-ab2b36a7914e