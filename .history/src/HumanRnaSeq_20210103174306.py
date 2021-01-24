# from https://medium.com/analytics-vidhya/optimized-ways-to-read-large-csvs-in-python-ab2b36a7914e
from dask import dataframe as dd

# import Visualisation
# import FormattedExport
# install like this (according to https://docs.dask.org/en/latest/install.html#pip):
# pip install "dask[complete]"

# use dask to circumvent memory-issues, which occur according to https://community.brain-map.org/t/reading-rna-seq-data-into-python/658
def read(path):
  # https://stackoverflow.com/questions/61647974/valueerror-sample-is-not-large-enough-to-include-at-least-one-row-of-data-plea
  return dd.read_csv(urlpath=path, sample=256000 * 100)
  
# https://docs.dask.org/en/latest/dataframe.html
# https://brainmapportal-live-4cc80a57cd6e400d854-f7fdcae.divio-media.net/filer_public/70/32/70326830-e306-4743-a02c-a8da5bf9eb56/readme-m1-10.txt
# https://portal.brain-map.org/atlases-and-data/rnaseq
# https://portal.brain-map.org/atlases-and-data/rnaseq/human-m1-10x
# https://portal.brain-map.org/atlases-and-data/rnaseq/mouse-whole-cortex-and-hippocampus-10x
rnaseq = read('data-rnaseq/aibs_human_m1_10x/matrix.csv')

rnaseq.partitions[0].to_csv( 'export/rna-seq-0.xlsx')
#head = rnaseq.head(2).compute()
#FormattedExport.to_excel(rnaseq.partitions[0], 'export/rna-seq-0.xlsx')
#Visualisation.grid(head)

#print(rnaseq.columns)

