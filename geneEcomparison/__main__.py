# this file is required in order to be able to debug the app, e.g. under vs code. 
# make sure to define "module": "geneEcomparison" in launch.json - else, the package wont be available
# the app is only started when run as a script
# https://docs.python.org/3/library/__main__.html
if __name__ == "__main__":
    # execute only if run as a script
  from . import App
  App.setAvailableGenes(["Gabra4", "Gabra5", "Gabrb1", "Gabrb2", "Gabrb3", "Gabrd", "Gabrg2"], "Gabra5", "Gabrb1", "Gabrb2")
  App.start()