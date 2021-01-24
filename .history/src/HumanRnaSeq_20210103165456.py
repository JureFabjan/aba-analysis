# from https://medium.com/analytics-vidhya/optimized-ways-to-read-large-csvs-in-python-ab2b36a7914e
from dask import dataframe as dd

dask_df = dd.read_csv('huge_data.csv')

# print("Read csv with dask: ",(end-start),"sec")
#Read csv with dask:  0.07900428771972656 sec