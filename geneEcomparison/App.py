from . import Visualisation
from . import Constants
from . import Utils

import webbrowser
from threading import Timer

def setAvailableGenes(str, default, defaultL, defaultR):
  Constants.Genes = str
  Constants.GENE_LIST = Utils.DropDownListConfiguration(label='Gene', type='gene', 
    data=str,
    default=default, defaultLeft=defaultL, defaultRight=defaultR)

  Constants.GENE1_LIST = Utils.DropDownListConfiguration(label='Gene', type='gene1', 
    data=str,
    default=default, defaultLeft=defaultL, defaultRight=defaultL)

  Constants.GENE2_LIST = Utils.DropDownListConfiguration(label='vs', type='gene2', 
    data=str,
    default=default, defaultLeft=defaultR, defaultRight=defaultR)


def start(port = 5000):

  def open_browser():
  	webbrowser.open_new("http://localhost:{}".format(port))

  webApp = Visualisation.WebInterface(__name__, port) 

  Timer(1, open_browser).start();
  webApp.run_server(debug=False)



