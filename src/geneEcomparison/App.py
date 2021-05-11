from . import Visualisation
from . import Constants

def setAvailableGenes(str):
  Constants.Genes = str

def start():
  webApp = Visualisation.WebInterface(__name__) 

  webApp.run_server(debug=False)