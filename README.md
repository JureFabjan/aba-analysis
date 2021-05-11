# aba-analysis
## Installation & setup
When using VS Code, make sure to add the setting described here to avoid an Execution_Policies-error when running python scripts:
https://stackoverflow.com/questions/56199111/visual-studio-code-cmd-error-cannot-be-loaded-because-running-scripts-is-disabl 

For allensdk, Microsoft Build Tools for C++ is required, so please install:
https://visualstudio.microsoft.com/de/visual-cpp-build-tools/
including the optional MSVC package => then restart your computer

use python 3.6.8. it has to be < 3.7 due to the allensdk requiring the tables-library, which has been precompiled for python 3.6
(see: https://stackoverflow.com/questions/53643594/unable-to-install-library-due-to-error-with-hdf5)
download python 3.6.8 here: https://www.python.org/downloads/release/python-368/

pip install -r requirements.txt

if you are debugging with vs code, use https://pypi.org/project/ptvsd/ for much better debugging-performance:
pip install ptvsd

IMPORTANT:
A probe is a plane through the brain in order to detect a specific gene. It contains normalized expression levels and the z-score for each element of the samples-array. "The z-score is computed independently for each probe over all donors and samples." Check out http://help.brain-map.org/display/humanbrain/API for more information.

For extending the code used to retrive microarray-data (human), use the http://api.brain-map.org/examples/rma_builder/index.html

To force a reload and process data anew, delete one or multiple gene-specific folders in cache\data-frames\mouse or cache\data-frames\human, respectively.

if rna-seq not possible => smoothen correlation of subunits using 3d-gaussian per voxel

load all experiments for mice and humans (=> rows), collect meta-data (sex, age, species, etc. => columns). then: get variance/std by meta-data and brain-region
meta-data model definition: http://api.brain-map.org/doc/Donor.html
how do i get a list of all experiments? => http://help.brain-map.org/display/api/Example+Queries+for+Experiment+Metadata
http://help.brain-map.org/display/api/Allen%2BBrain%2BAtlas%2BAPI
https://portal.brain-map.org/explore/transcriptome
https://wiki.mouseimaging.ca/ => https://wiki.mouseimaging.ca/display/MICePub/Mouse+Brain+Atlases
https://allensdk.readthedocs.io/en/latest/allensdk.api.queries.grid_data_api.html
https://allensdk.readthedocs.io/en/latest/data_api_client.html


groupby poses an issue: donor-information for specific regions might vary => we cant group by donor-columns

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


# example for region-assignments.csv:
Human,Mouse,Name
"level_3;pons","level_4;Pons","Pons"


building and deploying the package:
! clean the dist/-folder before building. else, twine will later try to upload previous files which is not possible.
/ see: https://stackoverflow.com/questions/52016336/how-to-upload-new-versions-of-project-to-pypi-with-twine
py -m build
/ then:
py -m twine upload --repository testpypi dist/* --skip-existing
/ login using your credentials



https://test.pypi.org/manage/project/geneecomparison/releases/

python -m venv .venv



pip install -i https://test.pypi.org/simple/ geneEcomparison==0.0.15 --extra-index-url https://pypi.org/simple

pip install -i https://test.pypi.org/simple/ geneEcomparison==0.0.3

https://hub.gke2.mybinder.org/user/christoph-hue-py-dist-test-gv3vktv6/notebooks/test.ipynb


https://stackoverflow.com/questions/16425434/how-to-create-a-python-package-with-multiple-files-without-subpackages

https://mybinder.org/v2/git/https%3A%2F%2Fgithub.com%2Fchristoph-hue%2Fpy-dist-test/HEAD?filepath=test.ipynb



make sure to define "module": "src.geneEcomparison" in launch.json - else, the package wont be available


install package for testing:
pip install -e .

uninstall package:
python setup.py develop -u


https://stackoverflow.com/questions/14132789/relative-imports-for-the-billionth-time

https://fabiomolinar.com/blog/2019/02/23/debugging-python-packages-vscode/

https://realpython.com/absolute-vs-relative-python-imports/

https://riptutorial.com/python/example/18555/making-package-executable