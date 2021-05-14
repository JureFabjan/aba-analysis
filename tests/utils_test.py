
import numpy as np
from numpy import testing as nptest

from geneEcomparison import Utils

def test_zscore():
  result = Utils.z_score(np.asarray([1, 3 , 5]))
  
  # https://stackoverflow.com/questions/3302949/best-way-to-assert-for-numpy-array-equality
  assert nptest.assert_allclose(result, np.asarray([-1.22474487,  0,  1.22474487])) is None
  
