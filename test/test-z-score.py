
import pandas as pd
import numpy as np

folder = "samples_zscore" # structures_log2intensities / samples_log2intensities
# tested using downloads from http://human.brain-map.org/microarray/search/show?exact_match=false&search_term=gabra4&search_type=gene&page_num=0
z = pd.read_csv(f'test\\{folder}\\Expression.csv', header=None)


# the first column (provided as a row here) is the expression-id, so drop it
all_values = z.drop([0], axis=1).values.flatten()
all_values.sort()

#print(all_values)
np.savetxt(f"dl_z-score_{folder}.csv", all_values, delimiter=",")