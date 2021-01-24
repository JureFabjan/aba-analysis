import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LogNorm
import pandasgui
import plotly.graph_objects as go
import plotly.express as px

import dash
from dash import Dash, no_update
import dash_bootstrap_components as dbc # used for css
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, MATCH, ALL

import pandas as pd
import webbrowser
from threading import Timer

from HumanMicroarrayData import HumanMicroarrayData
from MouseISHData import MouseISHData

import Comparison
from Constants import AGGREGATION_FUNCTIONS, GENE_LIST, STRUCTURE_LEVELS

# ? For some good tutorials on Dash (https://dash.plotly.com/), see:
# ? https://www.youtube.com/watch?v=Ldp3RmUxtOQ
# ? https://www.youtube.com/watch?v=hSPmj7mK6ng
class WebInterface:
  def __init__(self, name, port = 5000):
        # for layout & css, see https://dash.plotly.com/layout
    self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    self.port = port

    # ! adjust lists declared in Constants.py (such as GENE_LIST) to change the dropdown-list's options.

    # assume you have a "long-form" data frame
    # see https://plotly.com/python/px-arguments/ for more options
    # df = pd.DataFrame({
    #     "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    #     "Amount": [4, 1, 2, 2, 4, 5],
    #     "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    # })

    # fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

    self.app.title = "Gene-expression comparison"
    # https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
    self.app.layout = html.Div([
        html.H1('Z-score gene-expression by species & regions', className="p-2"),
        html.P('All data obtained from Allen Brain Institute: Human microarray-data vs rodent in-situ hybridization', className="p-1 pl-2"),

        dbc.Tabs([
          dbc.Tab(self.sideBySideView('all-species'), label="Heatmap by region"),
          dbc.Tab(self.sideBySideView('by-species'), label="Charts by structure and species"),
          # Stacked bars by structure, sorted
          # Co-expressions by structure
          #dbc.Tab([], label="Co-expressions by structure"), #, with shared variance
          dbc.Tab([], label="Data-grid"),
          #dbc.Tab([], label="Pivot table")

          #dbc.Tab(self.gridView(), label="grid-view"),
          #dbc.Tab(              "This tab's content is never seen", label="Tab 3", disabled=True          ),
        ]),
    ])

    # TODO: selectboxes for species, hemisphere
    # we need to update left/right side  https://dash.plotly.com/pattern-matching-callbacks
    # see https://dash-bootstrap-components.opensource.faculty.ai/docs/components/input/
    @self.app.callback( # MATCH is a bit tricky. in this case, it basically says that all inputs and outputs need to belong to the same view
      [Output({'type': 'graph', 'side': 'left', 'view': MATCH}, "figure"), 
       Output({'type': 'graph', 'side': 'right', 'view': MATCH}, "figure")], 
      [Input({'type': 'aggregation_function', 'view': MATCH}, "value"), 
       Input({'type': 'gene', 'side': 'left', 'view': MATCH}, "value"), 
       Input({'type': 'gene', 'side': 'right', 'view': MATCH}, "value")])
    def heatMapsByRegionCallback(agg_function, left_gene, right_gene):
      
      # we don't want to update a side if only the opposing side's gene has been changed
      # https://dash.plotly.com/advanced-callbacks
      ctx = dash.callback_context

      print(ctx.triggered[0])
      
      # https://stackoverflow.com/questions/4547274/convert-a-python-dict-to-a-string-and-back
      # the prop_id is a stringified dictionary (ugh...) so we need to "eval" it. the contents are trusted, because they are defined in our own code.
      # no additional security using ast.literal_eval required here..
      input_props = eval(ctx.triggered[0]['prop_id'])

      # handle the initial load, which is provided with triggered = False. changing the aggregation-function, however, forces a reload of both sides
      if not ctx.triggered or input_props['type'] == 'aggregation_function':
        left_unchanged = False
        right_unchanged = False
      else:
        print(ctx.triggered[0])
        # check which input triggered this callback. there can only be one input at a time, so we only check the first element:
        left_unchanged = (input_props['side'] != "left")
        right_unchanged = (input_props['side'] != "right")

      # https://community.plotly.com/t/i-want-to-create-a-conditional-callback-in-dash-is-it-possible/23418/2
      # we are able to prevent an update of one side. however, the loading-indicator will still be shown. track this bug here: https://github.com/plotly/dash/issues/1120
      return no_update if left_unchanged else heatmapByRegion(agg_function, left_gene), no_update if right_unchanged else heatmapByRegion(agg_function, right_gene)
      
    def heatmapByRegion(agg_function, gene):

      print('heatmapByRegion', agg_function, gene)
      return heatmap(Comparison.byDonor(
        HumanMicroarrayData(gene).get(from_cache=True, aggregations=AGGREGATION_FUNCTIONS),
        MouseISHData(gene).get(from_cache=True, aggregations=AGGREGATION_FUNCTIONS),
        agg_function
      ))

  def getSelectionControls(self): 
    return []

  def sideBySideView(self, viewName): #, left, right): 
    defaultClassName = "mr-3"

    return dbc.Card(
    dbc.CardBody(
        [
          dbc.Form(
            dbc.FormGroup([
                dbc.Label("Structure level", className=defaultClassName),
                self.dropDownByList(STRUCTURE_LEVELS, {'type': 'structure_level', 'view': viewName}, value=2, className=defaultClassName), 
                dbc.Label("Aggregation function", className=defaultClassName),
                self.dropDownByList(AGGREGATION_FUNCTIONS, {'type': 'aggregation_function', 'view': viewName}, value='mean', className=defaultClassName)
                ])
          , inline=True),
          dbc.Row([
                dbc.Col([
                  dbc.Row(
                    dbc.Form(
                      dbc.FormGroup([
                        dbc.Label("Gene", className=defaultClassName),
                        self.dropDownByList(GENE_LIST, {'type': 'gene', 'view': viewName, 'side': 'left'}, value="Gabra4")]
                    ), inline=True, className="ml-5 mt-3")
                  ),
                  dbc.Row(html.Div(dcc.Loading(
                    dcc.Graph(id={ 'type': 'graph', 'view': viewName, 'side': 'left'})
                  )), className="mt-3 w-100")
                ]),
                dbc.Col([
                  dbc.Row(
                    dbc.Form(
                      dbc.FormGroup([
                      dbc.Label("Gene", className=defaultClassName), 
                      self.dropDownByList(GENE_LIST, {'type': 'gene', 'view': viewName, 'side': 'right'}, value="Gabrg3")]
                      ), inline=True, className="ml-5 mt-3")
                  ),
                  dbc.Row(html.Div(dcc.Loading(
                    dcc.Graph(id={ 'type': 'graph', 'view': viewName, 'side': 'right'})
                  )), className="mt-3 w-100")
                ])
          ])
        ]
    ),
    className="mt-3 ml-3"
    )

  

  def dropDownByList(self, lst, id, **kwags):
    return dbc.Select(id=id, options=[{ "label": g, "value": g } for g in lst], **kwags)

  def gridView(self): 
    return dbc.Card(
    dbc.CardBody(
        [
            html.P("This is the grid-view!", className="card-text"),
            dbc.Button("Click here", color="success"),
        ]
    ),
    className="mt-3",
    )


  def run_server(self, **kwags):
    return self.app.run_server(**kwags, port=self.port)

  def __open(self):
    webbrowser.open_new("http://localhost:{}".format(self.port))

  def open_browser(self):
    Timer(1, self.__open).start()
    

  

# TODO: https://github.com/plotly/react-pivottable/

# TODO: allow log-scaled colors for better visualisation. 
# https://stackoverflow.com/questions/36898008/seaborn-heatmap-with-logarithmic-scale-colorbar
# => norm=LogNorm(), ...but this doesn't work with 0 or negative values
def heatmap(data, title = None, subplots_adjust_parameters = None, xlabel = None, ylabel = None, **kwags):
  # The heatmap-component tries to fit labels automatically, which sometimes hides labels unnecessarily.
  # To prevent this, use: yticklabels=True or xticklabels=True, respectively. see: https://seaborn.pydata.org/generated/seaborn.heatmap.html

  # https://www.delftstack.com/howto/matplotlib/how-to-plot-a-2d-heatmap-with-matplotlib/
  # plt.figure(num=title)
  # ax = sns.heatmap(data, linewidth=0.3, **kwags)
  # ax.set_title(title)
  # if not xlabel is None: ax.set_xlabel(xlabel)
  # if not ylabel is None: ax.set_ylabel(ylabel)

  # ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
  # plt.tight_layout()
  # plt.subplots_adjust(**subplots_adjust_parameters)
  
  # # TODO: ask Jure whether we need tooltips on hovering data-points, e.g. to show the specific fine-structure's name (currently only the rank is given)
  # # https://stackoverflow.com/questions/7908636/possible-to-make-labels-appear-when-hovering-over-a-point-in-matplotlib
  # plt.show()


  fig = px.imshow(data
                  #,labels=dict(x="Day of Week", y="Time of Day", color="Productivity"),
                  #x=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                  #y=['Morning', 'Afternoon', 'Evening']
  )

  #fig.update_xaxes(automargin=True)
  #fig.update_yaxes(automargin=True)

  fig.update_layout(
    autosize=True,
    margin=dict(l=0, r=0, t=25, b=10),
    title=title)
  

  return fig


def heatmap_tiled(dfs, title, names, rows, cols, subplots_adjust_parameters, **kwags):
  # https://stackoverflow.com/questions/43131274/how-do-i-plot-two-countplot-graphs-side-by-side-in-seaborn
  
  fig, ax =plt.subplots(rows, cols, num=title)
  
  for i in range(0, len(dfs)):
    # we need to access ax.flat, because otherwise we would need to track current row/col
    # see: https://stackoverflow.com/questions/37604730/subplot-error-in-matplotlib-using-seaborn
    sns.heatmap(dfs[i], ax=ax.flat[i], **kwags)
    ax.flat[i].set_title(names[i])
    ax.flat[i].set_xticklabels(ax.flat[i].get_xticklabels(), rotation=30)

  # https://dev.to/thalesbruno/subplotting-with-matplotlib-and-seaborn-5ei8
  fig.suptitle(title)

  # https://stackoverflow.com/questions/6541123/improve-subplot-size-spacing-with-many-subplots-in-matplotlib
  fig.tight_layout()
  # https://stackoverflow.com/questions/6976658/most-pythonic-way-of-assigning-keyword-arguments-using-a-variable-as-keyword
  plt.subplots_adjust(**subplots_adjust_parameters)
  plt.show()

def grid(data, **kwags):
  # to see how the ui (especially the grapher) works:
  # https://towardsdatascience.com/pandasgui-analyzing-pandas-dataframes-with-a-graphical-user-interface-36f5c1357b1d
  pandasgui.show(data, settings={'block': True}, **kwags)


def scatter(data, **kwags):
  # https://seaborn.pydata.org/examples/scatter_bubbles.html
  sns.scatterplot( #palette="muted", relplot alpha=.5,
            data=data, ci=None, # dont calculate confidence-intervals, which are expensive to compute..
            alpha=.65,
            **kwags)
  plt.show()


# for 3d: 
# drawing 3d: https://plotly.com/python/3d-mesh/
# getting the mesh, see get_structure_mesh @ https://alleninstitute.github.io/AllenSDK/allensdk.core.reference_space_cache.html