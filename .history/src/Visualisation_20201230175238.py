import matplotlib.pyplot as plt

import seaborn as sns

def heatmap(data, **kwags):
  # https://www.delftstack.com/howto/matplotlib/how-to-plot-a-2d-heatmap-with-matplotlib/
  ax = sns.heatmap(data, linewidth=0.3, **kwags)
  plt.show()
