from . import Visualisation
from . import Constants

import webbrowser
from threading import Timer

def setAvailableGenes(str):
  Constants.Genes = str

def start(port = 5000):

  def open_browser():
  	webbrowser.open_new("http://localhost:{}".format(port))

  webApp = Visualisation.WebInterface(__name__, port) 

  Timer(1, open_browser).start();
  webApp.run_server(debug=False)



