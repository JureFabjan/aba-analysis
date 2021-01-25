# from https://medium.com/analytics-vidhya/optimized-ways-to-read-large-csvs-in-python-ab2b36a7914e
from dask import dataframe as dd

# use dask to circumvent memory-issues, which occur according to https://community.brain-map.org/t/reading-rna-seq-data-into-python/658
def read():
  dask_df = dd.read_csv('data-rnaseq/aibs_human_m1_10x/matrix.csv')
  print("Read csv with dask..")
#Read csv with dask:  0.07900428771972656 sec