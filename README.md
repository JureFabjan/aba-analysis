# aba-analysis


IMPORTANT:
A probe is a plane through the brain in order to detect a specific gene. It contains normalized expression levels and the z-score for each element of the samples-array. "The z-score is computed independently for each probe over all donors and samples." Check out http://help.brain-map.org/display/humanbrain/API for more information.

For extending the code used to retrive microarray-data (human), use the http://api.brain-map.org/examples/rma_builder/index.html

To force a reload and process data anew, delete one or multiple gene-specific folders in cache\data-frames\mouse or cache\data-frames\human, respectively.

Fyi
http://neuroexpresso.org/
http://atlas.brain-map.org/atlas?atlas=138322605#atlas=138322605&plate=112360888&structure=13230&x=23424&y=53120&zoom=-7&resolution=124.49&z=3

https://stackoverflow.com/questions/32639074/why-am-i-getting-importerror-no-module-named-pip-right-after-installing-pip


https://dash.plotly.com/installation

https://community.brain-map.org/t/what-is-the-z-score-reference-value-in-rnaseq-gbm-data/513
http://help.brain-map.org/display/humanbrain/API


https://community.brain-map.org/t/transcriptomics-rna-seq-microarray-data-normalization-faq/182

                      probes
human microarray data [1,2,3.. z-score:  mean:2, var: 1] [1,4,7, z-score: mean: 4, var:3] [ ] ... ]
ish mouse data        [1,2,3,4,7, z-score: mean:4, var: 2               ]

this video helps to clarify the microarray-approach and explains what a probe actually is: https://www.youtube.com/watch?v=Hv5flUOsE0s



According to WholeBrainMicroarray_WhitePaper.pdf:
For two brains (H0351.2001 and H0351.2002), samples were collected from both hemispheres (cerebral,
cerebellar and both sides of brainstem). Otherwise, samples for microarray were collected from the left
cerebral and cerebellar hemispheres and left brainstem.