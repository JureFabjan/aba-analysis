import matplotlib.pyplot as plt
import seaborn as sns
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
from Constants import AGGREGATION_FUNCTIONS, GENE1_LIST, GENE2_LIST, GENE_LIST, HEMISPHERES, SPECIES, STRUCTURE_LEVELS

import json
import Utils 


# ! adjust lists declared in Constants.py (such as GENE_LIST) to change the dropdown-list's options.

# ? For some good tutorials on Dash (https://dash.plotly.com/), see:
# ? https://www.youtube.com/watch?v=Ldp3RmUxtOQ
# ? https://www.youtube.com/watch?v=hSPmj7mK6ng
class WebInterface:
   
    
  def __init__(self, name, port = 5000):
        # for layout & css, see https://dash.plotly.com/layout
    self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
    self.port = port

    self.app.title = "Gene-expression comparison"

    
    VIEWS = Utils.simple({
    'coexpressions': Utils.simple({ 'name': 'coexpressions', 'fn': self.coexpressions}), 
    'stackedBarsBySpecies': Utils.simple({'name': 'stackedBarsBySpecies', 'fn': self.stackedBarsBySpecies}),
    'allSpecies': Utils.simple({ 'name': 'allSpecies', 'fn': self.heatmapByRegion})
    })

    # https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
    self.app.layout = html.Div([
        html.H1('Z-score gene-expression by species & region', className="p-2 pl-4"),
        html.P('All data obtained from Allen Brain Institute: Human microarray-data vs rodent in-situ hybridization', className="p-1 pl-4"),

        dbc.Tabs([
          dbc.Tab(self.sideBySideView(VIEWS.allSpecies.name, [AGGREGATION_FUNCTIONS], [GENE_LIST]),  # TODO: HEMISPHERES?
            label="Expression-heatmaps"),
          dbc.Tab(self.sideBySideView(VIEWS.coexpressions.name, [AGGREGATION_FUNCTIONS], [SPECIES, GENE1_LIST, GENE2_LIST, HEMISPHERES, STRUCTURE_LEVELS]), 
           label="Co-expressions"),
          dbc.Tab(self.sideBySideView(VIEWS.stackedBarsBySpecies.name, [AGGREGATION_FUNCTIONS], [SPECIES, GENE_LIST, HEMISPHERES, STRUCTURE_LEVELS]), 
           label="Stacked bars"),
          # Stacked bars by structure, sorted
          # Co-expressions by structure
          #dbc.Tab([], label="Co-expressions by structure"), #, with shared variance
          dbc.Tab([], label="Data-grid")
          #dbc.Tab([], label="Pivot table")

          #dbc.Tab(self.gridView(), label="grid-view"),
          #dbc.Tab(              "This tab's content is never seen", label="Tab 3", disabled=True          ),
        ]),
    ])

    # TODO: define only by side, match plot-parameters by name
    # TODO: selectboxes for species, hemisphere
    # we need to update left/right side https://dash.plotly.com/pattern-matching-callbacks
    # see https://dash-bootstrap-components.opensource.faculty.ai/docs/components/input/
    @self.app.callback( 
      # MATCH is a bit tricky. in this case, it basically says that all inputs and outputs need to belong to the same view
      [Output({'type': 'graph', 'side': 'left', 'view': MATCH}, "figure"), 
       Output({'type': 'graph', 'side': 'right', 'view': MATCH}, "figure")], 
       # we need to separate the side-specific graphs from the inputs. we use input: True to filter out non-input-controls
      [Input({'type': ALL, 'input': True, 'view': MATCH}, "value"), 
       Input({'type': ALL, 'input': True, 'side': 'left', 'view': MATCH}, "value"), 
       Input({'type': ALL, 'input': True, 'side': 'right', 'view': MATCH}, "value")])
    def heatMapsByRegionCallback(agg_function, left_gene, right_gene):
      
      # we don't want to update a side if only the opposing side's gene has been changed
      # https://dash.plotly.com/advanced-callbacks
      ctx = dash.callback_context

      # https://stackoverflow.com/questions/4547274/convert-a-python-dict-to-a-string-and-back
      # the prop_id is a stringified dictionary (ugh...) so we need to json.loads it. but it is provided in the format 'stringified_dict.value', so we split it...
      # ! we cant use eval here, because Dash lowercases the property-values, which changes True to true. eval does not recognize this as a keyword and crashes
      input_props = json.loads(ctx.triggered[0]['prop_id'].split('.')[0]) if ctx.triggered else {}

      common = self.callbackInputsToKwags(ctx.inputs_list[0])
      left = self.callbackInputsToKwags(ctx.inputs_list[1])
      right = self.callbackInputsToKwags(ctx.inputs_list[2])

      # handle the initial load, which is provided with triggered = False. changing non-side related inputs, however, forces a reload of both sides
      if not ctx.triggered or 'side' not in input_props: 
        left_unchanged = False
        right_unchanged = False
      else:
        # check which input triggered this callback. there can only be one input at a time, so we only check the first element:
        left_unchanged = (input_props['side'] != "left")
        right_unchanged = (input_props['side'] != "right")

      # the function used for creating the chart-figure is defined as a pointer in the views-object:
      fn = getattr(VIEWS, ctx.outputs_list[0]['id']['view']).fn

      # https://community.plotly.com/t/i-want-to-create-a-conditional-callback-in-dash-is-it-possible/23418/2
      # we are able to prevent an update of one side. however, the loading-indicator will still be shown. track this bug here: https://github.com/plotly/dash/issues/1120
      return no_update if left_unchanged else fn(**common, **left), no_update if right_unchanged else fn(**common, **right)
      
  def heatmapByRegion(self, aggregation_function, gene):

    return heatmap(Comparison.byDonor(
      HumanMicroarrayData(gene).get(from_cache=True, aggregations=AGGREGATION_FUNCTIONS.data),
      MouseISHData(gene).get(from_cache=True, aggregations=AGGREGATION_FUNCTIONS.data),
      aggregation_function
    ))

  # TODO: enforce same scaling for both sides to make the visual data comparable
  def coexpressions(self, aggregation_function, structure_level, species, hemisphere, gene1, gene2):
    structure_level = f"level_{structure_level}"
    sizeBy = f"shared_{aggregation_function}"
    # this is very slow when providing many different values. try to keep it coarsly grained, e.g. on larger scaled brain-structures (level 1-3)
    data = Comparison.coexpression(
      aggregation_function, structure_level, species, hemisphere, gene1, gene2)

    #print(data)    
    # https://plotly.com/python-api-reference/generated/plotly.express.scatter
    fig = px.scatter(data, y=f"expression_level_{gene1}_{aggregation_function}", x=f"expression_level_{gene2}_{aggregation_function}"
          # TODO: there is some issue with sizes. besides NaN, we got some weird errors...
	        #,size=sizeBy#, size_max=400 
          ,color=structure_level
          ,opacity=0.65
          )


    fig.update_xaxes(title=gene2)           
    fig.update_yaxes(title=gene1)
    return fig

  # TODO: there are some NaNs...
  def stackedBarsBySpecies(self, aggregation_function, structure_level, species, hemisphere, gene):
    result = Comparison.species_map[species](gene).get(from_cache=True, aggregations=AGGREGATION_FUNCTIONS.data)
    # TODO: deal with a list for mice (but sometimes it isnt...)
    if(species == 'mouse'):
      result = result[0]      

    return heatmap(Comparison.by_region(result.data.structure, aggregation_function, 'global-z-score', f'level_{structure_level}', 'structure_name'))


  def callbackInputsToKwags(self, input):
    return { input[i]['id']['type']:input[i]['value']  for i in range(0,len(input)) }

  def sideBySideView(self, viewName, commonFilters, sideFilters):
    dimensions = Utils.simple({ 'w': 'calc(49vw - 30px)', 'h': 'calc(100vh - 400px)' })

    return dbc.Card(
    dbc.CardBody(
        [
          dbc.Card(dbc.CardBody(
          dbc.Form( # we get an array (label + dropdown) inside an array. so we need to unpack that
            dbc.FormGroup(Utils.unpack(self.dropDownByList(lst, {'type': lst.type, 'view': viewName}, value=lst.default) for lst in commonFilters))
          , inline=True))),
          dbc.Row([
                dbc.Col([
                  dbc.Row(
                    dbc.Form(
                      dbc.FormGroup(
                        Utils.unpack(self.dropDownByList(lst, {'type': lst.type, 'side': 'left', 'view': viewName}, value=lst.defaultLeft) for lst in sideFilters)
                      ), inline=True, className="ml-4 mt-3")
                  ),
                  dbc.Row(html.Div(dcc.Loading(
                    dcc.Graph(id={ 'type': 'graph', 'view': viewName, 'side': 'left'}, style={'width': dimensions.w, 'height': dimensions.h})
                  )), className="mt-3 w-100")
                ], className="border-right"),
                dbc.Col([
                  dbc.Row(
                    dbc.Form(
                      dbc.FormGroup(
                        Utils.unpack(self.dropDownByList(lst, {'type': lst.type, 'side': 'right', 'view': viewName}, value=lst.defaultRight) for lst in sideFilters)
                      ), inline=True, className="ml-4 mt-3")
                  ),
                  dbc.Row(html.Div(dcc.Loading(
                    dcc.Graph(id={ 'type': 'graph', 'view': viewName, 'side': 'right'}, style={'width': dimensions.w, 'height': dimensions.h})
                  )), className="mt-3 w-100")
                ])
          ])
        ]
    ),
    className="m-3"
    )

  def dropDownByList(self, lst, idProps, **kwags):
    return ([dbc.Label(lst.label, className="mr-2")] if not lst.label is None else []) + [dbc.Select(id={'type': lst.type, 'input': True, **idProps}, 
      options=[{ "label": g, "value": g } for g in lst.data], className="mr-3", **kwags)]

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
  # TODO: ask Jure whether we need tooltips on hovering data-points, e.g. to show the specific fine-structure's name (currently only the rank is given)
  
  fig = px.imshow(data
                  #,labels=dict(x="Day of Week", y="Time of Day", color="Productivity"),
                  #x=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                  #y=['Morning', 'Afternoon', 'Evening']
  )

  fig.update_xaxes(
        tickangle = 45)
  fig.update_layout(
    autosize=True,
    #height=700,
    #width=700,
    margin=dict(l=0, r=0, t=25, b=10),
    title=title)

  return fig


def grid(data, **kwags):
  # to see how the ui (especially the grapher) works:
  # https://towardsdatascience.com/pandasgui-analyzing-pandas-dataframes-with-a-graphical-user-interface-36f5c1357b1d
  pandasgui.show(data, settings={'block': True}, **kwags)

