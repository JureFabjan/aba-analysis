# from https://www.tutorialspoint.com/How-can-I-create-a-directory-if-it-does-not-exist-using-Python

import os

def makedir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def merge_with_structure(data, structure, value_cols, aggregations):
    ret = structure.merge(data,  left_index=True, right_on="structure_id", how="left").dropna(axis=1, how='all')

    left_cols = ['structure_id', 'structure_name']
    level_cols = [col for col in ret.columns if 'level_' in col]
    ret = ret.groupby(level_cols, dropna=False)[value_cols].agg(aggregations)
    
    # https://stackoverflow.com/questions/11194610/how-can-i-reorder-multi-indexed-dataframe-columns-at-a-specific-level
    print(ret)
    return ret
    # https://stackoverflow.com/questions/14507794/pandas-how-to-flatten-a-hierarchical-index-in-columns
    # remove multi-index, so that we can select columns in a specific order
    #ret.columns = ret.columns.get_level_values(0)

    #return ret[[left_cols + value_cols + level_cols]]
    