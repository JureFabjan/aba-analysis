

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