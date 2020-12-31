import matplotlib.pyplot as plt

def heatmap(data, **kwags):
  plt.imshow(data, cmap='cool', interpolation='nearest', **kwags)
  plt.show()
