import matplotlib.pyplot as plt

def heatmap(data, **kwags):
  # https://www.delftstack.com/howto/matplotlib/how-to-plot-a-2d-heatmap-with-matplotlib/
  plt.imshow(data, cmap='cool', **kwags) # interpolation='nearest', 
  plt.show()
