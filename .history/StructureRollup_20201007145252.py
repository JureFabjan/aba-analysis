import pandas as pd

class StructureRollup:
    
    #def __init__(self)
    #data.groupby([col for col in data.columns if 'level_' in col])
    def by(data, rollupColumns, aggregationColumns, aggregationFunctions):
        cols = []
        dfs = []
        for col in rollupColumns:
            cols.append(col)
            dfs.append(data.groupby(rollupColumns)[aggregationColumns].agg(aggregationFunctions))

        return pd.concat(dfs, axis=0)
        
    