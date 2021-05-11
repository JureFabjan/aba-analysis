import geneEcomparison

webApp = geneEcomparison.Visualisation.WebInterface(__name__) 

webApp.run_server(debug=True)