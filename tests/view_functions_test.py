from geneEcomparison import Visualisation, Comparison, HumanMicroarrayData, MouseISHData, Constants

def test_coexpressions():
  # https://docs.python-guide.org/writing/structure/
  # https://gist.github.com/tasdikrahman/2bdb3fb31136a3768fac

  webApp = Visualisation.WebInterface(__name__) 
  result = webApp.coexpressions(aggregation_function='mean', structure_level=3, species='human', gene1='Gabra4', gene2='Gabra1', side='left')
  
  assert not result is None

def test_by_donor():
  gene = "Gabra4"
  Comparison.byDonor(
      HumanMicroarrayData.HumanMicroarrayData(gene).get(from_cache=True, aggregations=Constants.AGGREGATION_FUNCTIONS.data),
      MouseISHData.MouseISHData(gene).get(from_cache=True, aggregations=Constants.AGGREGATION_FUNCTIONS.data),
      'mean'
    )