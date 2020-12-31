import matplotlib.pyplot as plt

import seaborn as sns

# TODO: allow log-scaled colors for better visualisation
# https://stackoverflow.com/questions/36898008/seaborn-heatmap-with-logarithmic-scale-colorbar
def heatmap(data, **kwags):
  # https://www.delftstack.com/howto/matplotlib/how-to-plot-a-2d-heatmap-with-matplotlib/
  ax = sns.heatmap(data, linewidth=0.3, **kwags)
  plt.show()
