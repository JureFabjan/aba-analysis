from . import Visualisation

#def run():
webApp = Visualisation.WebInterface(__name__) 

webApp.run_server(debug=False)
#sys.exit()

#ärun()

# def run():
#   webApp = Visualisation.WebInterface(__name__) 

#   webApp.run_server(debug=False)
#   #sys.exit()