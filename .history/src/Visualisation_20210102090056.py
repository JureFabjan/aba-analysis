import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LogNorm
from pandasgui import show

# TODO: allow log-scaled colors for better visualisation. 
# https://stackoverflow.com/questions/36898008/seaborn-heatmap-with-logarithmic-scale-colorbar
# => norm=LogNorm(), ...but this doesn't work with 0 or negative values
def heatmap(data, title, **kwags):
  # https://www.delftstack.com/howto/matplotlib/how-to-plot-a-2d-heatmap-with-matplotlib/
  ax = sns.heatmap(data, linewidth=0.3, **kwags)
  ax.set_title(title)
  plt.show()

def heatmap_tiled(dfs, names, rows, cols):
  # https://stackoverflow.com/questions/43131274/how-do-i-plot-two-countplot-graphs-side-by-side-in-seaborn
  
  fig, ax =plt.subplots(rows, cols)
  for i in range(1, len(dfs)):
    sns.heatmap(dfs[i], ax=ax.flat[i])

  plt.show()

def grid(data, **kwags):
  show(data, settings={'block': True}, **kwags)