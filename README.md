# gene-E-comparison
## Project setup (using Visual Studio Code)
As always when using VS Code, make sure to add the setting described here to avoid an Execution_Policies-error when running Python scripts in general:
https://stackoverflow.com/questions/56199111/visual-studio-code-cmd-error-cannot-be-loaded-because-running-scripts-is-disabl 

For the AllenSDK to be able to run, Microsoft Build Tools for C++ is required. Please install them using this link:
https://visualstudio.microsoft.com/de/visual-cpp-build-tools/ 

Make sure to include the optional MSVC package, then restart your computer.

Python 3.6.8 is required. The Python version has to be < 3.7 and > 3.6.4 due to the AllenSDK requiring the tables-library, which has only been precompiled for Python 3.6
(see: https://stackoverflow.com/questions/53643594/unable-to-install-library-due-to-error-with-hdf5). You can try to build your own whl-file using a newer Python-version. Otherwise, download and install Python 3.6.8 from here: https://www.python.org/downloads/release/python-368/

Create a new virtual environment using this command:
```
py -m venv .venv
```

Once you ensured these prerequisites, install the required packages using the provided *requirements.txt*:
```
pip install -r requirements.txt
```
Note that the AllenSDK unfortunately requires quite an old version of pandas. You might want to upgrade to a newer version of it, once all required packages have been installed.

If you are debugging with VS Code, you might want to use https://pypi.org/project/ptvsd/ for much better debugging-performance:
```
pip install ptvsd
```
As this project is provided as a package, you need to start it as a module instead of a top-level script (check out this blog-post: https://fabiomolinar.com/blog/2019/02/23/debugging-python-packages-vscode/). To do this, define "module": "src.geneEcomparison" in your *launch.json*:
```json
"configurations": [
        {
            "name": "Python: geneEcomparison",
            "type": "python",
            "request": "launch",
            "module": "src.geneEcomparison",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "justMyCode": false
        }
    ]
```

Else, the package won't be available and the relative imports (https://stackoverflow.com/questions/14132789/relative-imports-for-the-billionth-time, https://realpython.com/absolute-vs-relative-python-imports/) won't work. You need to run the project from the debugging-tab instead of the green arrow in the toolbar (which only runs the current script-file). The debugger will execute the package (https://riptutorial.com/python/example/18555/making-package-executable) or - to be more precise - the script defined in the package's _\_\_main\_\_.py_-file.

## Packaging
Creating a Python-package is quite complicated and requires knowledge of some conventions. Most of these conventions have already been abided in this project for it to be deployed. Please read the python-documentation for some background-information on this topic: https://packaging.python.org/tutorials/packaging-projects/

To deploy the package to pypi.org, you need to build it first. Pypi does not support overwriting existing versions of a package, so make sure to increment the version-/revision-number in *setup.cfg* accordingly. Then, clean the dist/-folder in order to remove existing builds that would only take time for uploading just to be refused by pypi anyways. Build the package with this command:
```
py -m build
```

You need to create an account for pypi (you need separate accounts for each environment - testing: https://test.pypi.org/, production: https://pypi.org/) to upload the package. Upload the package using your account (you will be asked for username and password in the command-prompt):
```
py -m twine upload --repository testpypi dist/* --skip-existing
```
NOTE: The _skip-existing_-flag only makes sure that no error occurs due to any attempts of uploading already existing versions - in case you forgot to clean the dist/-folder (https://stackoverflow.com/questions/52016336/how-to-upload-new-versions-of-project-to-pypi-with-twine).

## Testing the package
The package is now ready to be installed. To test its installation in a clean environment, I recommend using https://mybinder.org/. Mybinder allows you to use a variety of sources (e.g. a GitHub-repository, as done here) to set up a Python-environment and access it online. This Jupyter-notebook provides the correct environment for gene-e-comparison:
https://mybinder.org/v2/git/https%3A%2F%2Fgithub.com%2Fchristoph-hue%2Fpy-dist-test/HEAD?filepath=test.ipynb

The main block is intended for testing the installation using pip (make sure to change the geneEcomparison-version-number according to your recently deployed package):
```
pip install -i https://test.pypi.org/simple/ geneEcomparison==0.0.19 --extra-index-url https://pypi.org/simple
```
Be aware that the _extra-index-url_-argument makes sure that all dependencies are requested from the production-environment of pypi, as its test-environment does not provide all necessary packages and should thus not be used. You can omit this parameter when using the production-environment.

Deploying in pypi.org's production-environment:
```
py -m twine upload --repository pypi dist/* --skip-existing
```

## Usage
Running this package requires a permanent internet-connection. To start the web-application, use this code-block:
```python
from geneEcomparison import App
# You can provide your own list of genes to be selectable in dropdowns. However, note that there is yet no interface for defining defaults other than the current ones, which are hard-coded.
# App.setAvailableGenes(["Gabra4", "Gabra5", "Gabrb1", "Gabrb2", "Gabrb3", "Gabrd", "Gabrg2"])
App.start()
```

This will start the flask-server, making the app available on the localhost, port 5000: http://127.0.0.1:5000/

Please note that any (or most of the) requested and processed data will be cached for performance-reasons.

### Region-assignments
The mapping-file *region-assignments.csv* assigns diverging structures of different species to a common conceptual structure, which helps making the data comparable. Multiple structures can be mapped to a single concept.

**Example for region-assignments.csv:**
```csv
Human,Mouse,Name
"level_3;pons","level_4;Pons","Pons"
"level_3;hypothalamus","level_4;Hypothalamus","Hypothalamus"
"level_3;thalamus","level_4;Thalamus","Thalamus"
"level_4;cerebellar cortex","level_3;Cerebellar cortex","Cerebellar cortex"
```

## Shutdown
You can dispose the flask-server by pressing CTRL+C in the Python-console that hosts the web-application. There is currently no interface for shutting it down.
