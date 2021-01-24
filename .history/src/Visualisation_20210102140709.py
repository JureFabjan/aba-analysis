import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LogNorm
import pandasgui

# TODO: allow log-scaled colors for better visualisation. 
# https://stackoverflow.com/questions/36898008/seaborn-heatmap-with-logarithmic-scale-colorbar
# => norm=LogNorm(), ...but this doesn't work with 0 or negative values
def heatmap(data, title, subplots_adjust_parameters, **kwags):
  # The heatmap-component tries to fit labels automatically, which sometimes hides labels unnecessarily.
  # To prevent this, use: yticklabels=True or xticklabels=True, respectively. see: https://seaborn.pydata.org/generated/seaborn.heatmap.html

  # https://www.delftstack.com/howto/matplotlib/how-to-plot-a-2d-heatmap-with-matplotlib/
  plt.figure(num=title)
  ax = sns.heatmap(data, linewidth=0.3, **kwags)
  ax.set_title(title)
  ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
  plt.tight_layout()
  plt.subplots_adjust(**subplots_adjust_parameters)
  
  plt.show()

def heatmap_tiled(dfs, title, names, rows, cols, subplots_adjust_parameters):
  # https://stackoverflow.com/questions/43131274/how-do-i-plot-two-countplot-graphs-side-by-side-in-seaborn
  
  fig, ax =plt.subplots(rows, cols, num=title)
  
  for i in range(0, len(dfs)):
    # we need to access ax.flat, because otherwise we would need to track current row/col
    # see: https://stackoverflow.com/questions/37604730/subplot-error-in-matplotlib-using-seaborn
    sns.heatmap(dfs[i], ax=ax.flat[i])
    ax.flat[i].set_title(names[i])
    ax.flat[i].set_xticklabels(ax.flat[i].get_xticklabels(), rotation=30)

  # https://dev.to/thalesbruno/subplotting-with-matplotlib-and-seaborn-5ei8
  fig.suptitle(title)

  # https://stackoverflow.com/questions/6541123/improve-subplot-size-spacing-with-many-subplots-in-matplotlib
  fig.tight_layout()
  # https://stackoverflow.com/questions/6976658/most-pythonic-way-of-assigning-keyword-arguments-using-a-variable-as-keyword
  plt.subplots_adjust(**subplots_adjust_parameters)
  plt.show()

def grid(data, **kwags):
  # to see how the ui (especially the grapher) works:
  # https://towardsdatascience.com/pandasgui-analyzing-pandas-dataframes-with-a-graphical-user-interface-36f5c1357b1d
  pandasgui.show(data, settings={'block': True}, **kwags)


# for 3d: 
# drawing 3d: https://plotly.com/python/3d-mesh/
# getting the mesh, see get_structure_mesh @ https://alleninstitute.github.io/AllenSDK/allensdk.core.reference_space_cache.html