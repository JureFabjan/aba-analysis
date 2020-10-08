from allensdk.api.queries.ontologies_api import OntologiesApi
from allensdk.api.queries.grid_data_api  import GridDataApi
from allensdk.core.structure_tree import StructureTree
from allensdk.api.queries.mouse_atlas_api import MouseAtlasApi
from allensdk.api.queries.rma_api import RmaApi
from allensdk.api.cache import Cache

import struct 
import numpy
import pandas as pd

# https://github.com/benfulcher/AllenSDK
# http://help.brain-map.org/display/api/Atlas+Drawings+and+Ontologies


# we use the RmaApi to query specific information, such as the section data sets of a specific gene
rma = RmaApi()

# the cache_writeer allows us to easily cache the results
cache_writer = Cache()
use_cache = True

# http://api.brain-map.org/examples/rma_builder/index.html
# http://api.brain-map.org/examples/rma_builder/rma_builder.html
gene_ids = pd.DataFrame( # wrap is told to be deprecated, but there is no information on what to use instead :(
    cache_writer.wrap(rma.model_query,
                        path='cache\\section-data-sets.csv',
                        cache=use_cache,
                        model='SectionDataSet',
                        #criteria='',
                        include="genes[acronym$ilgabra4]"
                        num_rows='all'))

print(gene_ids)

#oapi = OntologiesApi()
#structure_graph = oapi.get_structures_with_sets([1])  # 1 is the id of the adult mouse structure graph

# This removes some unused fields returned by the query
#structure_graph = StructureTree.clean_structures(structure_graph)  

#tree = StructureTree(structure_graph)
#print(tree.parents([1011]))

gdApi = GridDataApi()
exp = 71924402

exp_path = f"data\\{exp}\\"

#gdApi.download_expression_grid_data(exp,GridDataApi.ENERGY,'gd.zip')
#gdApi.download_gene_expression_grid_data(exp,GridDataApi.ENERGY, exp_path)

# energy.raw

# According to the docs here: http://help.brain-map.org/display/api/Downloading+3-D+Expression+Grid+Data
# we have "A raw uncompressed float (32-bit) little-endian volume representing average expression energy per voxel. A value of "-1" represents no data. This file is returned by default if the volumes parameter is null."
# https://docs.python.org/3/library/struct.html
# struct helps us to read binary data by providing the used format. here, it is little-endian (represented by "<") and a 32-bit 
#energy = numpy.array(list(struct.iter_unpack("<f", open(exp_path + "energy.raw", "rb").read()))).flatten() # way too complicated, but there is a delta in mean and sum. what is the right value??
# just use 
energy2 = numpy.fromfile(exp_path + "energy.raw",  dtype=numpy.float32) # we can use numpy.float32 or "<f"

#print(numpy.mean(energy))
#print(numpy.mean(energy2))
#print(gd)

# http://help.brain-map.org/display/mousebrain/API#API-Expression3DGridsExpressionGridding
# http://help.brain-map.org/display/mousebrain/Documentation
# https://developingmouse.brain-map.org/static/atlas
# http://help.brain-map.org/pages/viewpage.action?pageId=2424836

# we only have 2 experiments for gabra4, right?
# https://mouse.brain-map.org/search/show?page_num=0&page_size=34&no_paging=false&exact_match=false&search_term=gaba%20alpha%204&search_type=gene
# mice: 75551483, 71924402
#

# humans:
# https://human.brain-map.org/ish/search/?page_num=0&page_size=400&no_paging=false&exact_match=false&search_term=gabra4&search_type=gene

# https://allensdk.readthedocs.io/en/latest/allensdk.api.queries.mouse_atlas_api.html

# mouseAtlasApi = MouseAtlasApi()

# print('getting genes')
# # data-model: http://api.brain-map.org/doc/Gene.html
# # https://stackoverflow.com/questions/17815945/convert-generator-object-to-a-dictionary
# all_genes = mouseAtlasApi.get_genes()
# print('got all genes')
# genes = {c['acronym']:c['id'] for c in all_genes} # (mouseAtlasApi.get_genes())
# print('transformed genes to dict')

# print(genes)
# gene_ids = []
# print('bla')

#for gene in genes:
    #if(gene['acronym'].lower() == 'gabra4'):
         #print('gene')
         #print(gene['id'])
         #gene_ids.append(gene['id'])
#print('done')
#print(gene_ids)

#datasets = mouseAtlasApi.get_section_data_sets(gene_ids)
#print(datasets)

# https://allensdk.readthedocs.io/en/latest/data_api_client.html

# "http://api.brain-map.org/api/v2/data/query.xml?criteria=model::SectionDataSet,rma::criteria,[failed$eq%27false%27],rma::include,genes[acronym$eq%27Gabra4%27]"

