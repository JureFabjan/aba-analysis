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
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
import dash_pivottable

import pandas as pd
import webbrowser
from threading import Timer

from HumanMicroarrayData import HumanMicroarrayData
from MouseISHData import MouseISHData

import Comparison
from Constants import AGGREGATION_FUNCTIONS, GENE1_LIST, GENE2_LIST, GENE_LIST, HEMISPHERES, SPECIES, STRUCTURE_LEVELS

import json
import Utils 

FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"

# ! adjust lists declared in Constants.py (such as GENE_LIST) to change the dropdown-list's options.

# ? For some good tutorials on Dash (https://dash.plotly.com/), see:
# ? https://www.youtube.com/watch?v=Ldp3RmUxtOQ
# ? https://www.youtube.com/watch?v=hSPmj7mK6ng
class WebInterface:
   
    
  def __init__(self, name, port = 5000):
        # for layout & css, see https://dash.plotly.com/layout
    self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX, FONT_AWESOME])
    self.port = port

    self.app.title = "Gene-expression comparison"
    self.downloads = {}

    VIEWS = Utils.simple({
    'coexpressions': Utils.simple({ 'name': 'coexpressions', 'fn': self.coexpressions}), 
    'stackedBarsBySpecies': Utils.simple({'name': 'stackedBarsBySpecies', 'fn': self.stackedBarsBySpecies}),
    'allSpecies': Utils.simple({ 'name': 'allSpecies', 'fn': self.heatmapByRegion}),
    'gridView': Utils.simple({ 'name': 'gridView', 'fn': self.getPivotTable})
    
    })

    # https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
    self.app.layout = html.Div([
        html.H1('Z-score gene-expression by species & region', className="p-2 pl-4"),
        html.P('All data obtained from Allen Brain Institute: Human microarray-data vs rodent in-situ hybridization. Note that mouse - sagittal only provides data for left hemisphere.', className="p-1 pl-4"),
        # TODO: explain z-score with a tooltip: https://dash-bootstrap-components.opensource.faculty.ai/docs/components/tooltip/ 
        #html.Div([html.Button("Download", id="btn"), Download(id="download")]),
        
        dbc.Tabs([
          # TODO: HEMISPHERES? (only available for human). method for scale-normalization.
          dbc.Tab(self.sideBySideView(VIEWS.allSpecies.name, [AGGREGATION_FUNCTIONS], [GENE_LIST]),  
            label="Expression-heatmaps"),
          dbc.Tab(self.sideBySideView(VIEWS.coexpressions.name, [AGGREGATION_FUNCTIONS], [SPECIES, GENE1_LIST, GENE2_LIST, STRUCTURE_LEVELS]),  #HEMISPHERES
           label="Co-expressions"),
          dbc.Tab(self.sideBySideView(VIEWS.stackedBarsBySpecies.name, [AGGREGATION_FUNCTIONS], [SPECIES, GENE_LIST, STRUCTURE_LEVELS]), 
           label="Stacked bars"),
          dbc.Tab(self.gridView(VIEWS.gridView.name, [SPECIES, GENE_LIST, STRUCTURE_LEVELS]), label="Data-grid")
        ]),
    ])

    

    # from: download https://community.plotly.com/t/allowing-users-to-download-csv-on-click/5550/42
    # @self.app.callback(Output("download", "data"), [Input("btn", "n_clicks")])
    # def func(n_clicks):
    #   if not n_clicks is None:
    #     df = Comparison.byDonor(
    #     HumanMicroarrayData('Gabra4').get(from_cache=True, aggregations=AGGREGATION_FUNCTIONS.data),
    #     MouseISHData('Gabra4').get(from_cache=True, aggregations=AGGREGATION_FUNCTIONS.data),
    #     'mean'
    #     )

    #     return send_data_frame(self.df.to_excel, "mydf.xlsx", index=True)
    #   else:
    #     return no_update


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
    def sideBySideViewCallback(common, left, right): # these parameters are actually not required / usable, because the real inputs are provided dynamically
      
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
      # we are able to prevent an update of one side. however, the loading-indicator will still be shown. 
      # track this bug here: https://github.com/plotly/dash/issues/1120
      return (
        no_update if left_unchanged else fn(**common, **left, side='left'), 
        no_update if right_unchanged else fn(**common, **right, side='right')
        )

        
    @self.app.callback( 
      # MATCH is a bit tricky. in this case, it basically says that all inputs and outputs need to belong to the same view
      [Output({'type': 'grid', 'view': MATCH}, "data"), 
      Output({'type': 'grid', 'view': MATCH}, "cols"),
      Output({'type': 'grid', 'view': MATCH}, "rows"),
      Output({'type': 'grid', 'view': MATCH}, "vals")],
        # we need to separate the side-specific graphs from the inputs. we use input: True to filter out non-input-controls
      Input({'type': ALL, 'input': True, 'view': MATCH}, "value"))
    def gridViewCallback(common): # these parameters are actually not required / usable, because the real inputs are provided dynamically
      
      # we don't want to update a side if only the opposing side's gene has been changed
      # https://dash.plotly.com/advanced-callbacks
      ctx = dash.callback_context

      # https://stackoverflow.com/questions/4547274/convert-a-python-dict-to-a-string-and-back
      # the prop_id is a stringified dictionary (ugh...) so we need to json.loads it. but it is provided in the format 'stringified_dict.value', so we split it...
      # ! we cant use eval here, because Dash lowercases the property-values, which changes True to true. eval does not recognize this as a keyword and crashes
      input_props = json.loads(ctx.triggered[0]['prop_id'].split('.')[0]) if ctx.triggered else {}

      common = self.callbackInputsToKwags(ctx.inputs_list[0])

      # handle the initial load, which is provided with triggered = False. changing non-side related inputs, however, forces a reload of both sides

      # the function used for creating the chart-figure is defined as a pointer in the views-object:
      fn = getattr(VIEWS, ctx.outputs_list[0]['id']['view']).fn

      # https://community.plotly.com/t/i-want-to-create-a-conditional-callback-in-dash-is-it-possible/23418/2
      # we are able to prevent an update of one side. however, the loading-indicator will still be shown. 
      # track this bug here: https://github.com/plotly/dash/issues/1120
      data = Utils.unstack_columns((fn(**common)).reset_index())
      #print(data)
      
      columns = data.columns.tolist()
      
      # data, cols, rows, vals
      
      return ([data.columns.tolist(), data.values.tolist()], # data
        [c  for c in columns if 'structure' in c], # cols
        [c  for c in columns if 'level' in c and not 'expression' in c], # rows
        [c  for c in columns if 'expression' in c] + [c  for c in columns if 'z-score' in c] # vals
      )
      
  def heatmapByRegion(self, aggregation_function, gene, side):
    # self.downloads[side] = Utils.simple({ 'filename': f"{gene}_agg", 'dataFrames': [  
    #   {'human': HumanMicroarrayData(gene).get(from_cache=True, aggregations=AGGREGATION_FUNCTIONS.data).data.structure}]
    #   + [{ m.name: m.data  } for m in MouseISHData(gene).get(from_cache=True, aggregations=AGGREGATION_FUNCTIONS.data)]
    #   }
    # )
    #self.right_df = Utils.simple({ 'name': f"human_{gene}_agg", 'df': HumanMicroarrayData(gene).get(from_cache=True, aggregations=AGGREGATION_FUNCTIONS.data).data.structure })
    
    return heatmap(Comparison.byDonor(
      HumanMicroarrayData(gene).get(from_cache=True, aggregations=AGGREGATION_FUNCTIONS.data),
      MouseISHData(gene).get(from_cache=True, aggregations=AGGREGATION_FUNCTIONS.data),
      aggregation_function
    ))

  # TODO: enforce same scaling for both sides to make the visual data comparable
  def coexpressions(self, aggregation_function, structure_level, species, gene1, gene2, side): # hemisphere,
    structure_level = f"level_{structure_level}"
    sizeBy = f"shared_{aggregation_function}"


    if(gene1 == gene2):
      raise Exception("Co-expressions for the same gene of the same species make no sense and would lead to errors.")

    result1 = Comparison.species_map[species](gene1).get(from_cache=True, aggregations=AGGREGATION_FUNCTIONS.data)
    result2 = Comparison.species_map[species](gene2).get(from_cache=True, aggregations=AGGREGATION_FUNCTIONS.data)
    
    # TODO: there we could allow comparison of the same gene and same species.
    if(species == 'mouse - sagittal'):
      result1 = result1[0]      
      result2 = result2[0]      
    elif(species == 'mouse - coronal'):
      result1 = result1[1]      
      result2 = result2[1]      
    
    data = Comparison.coexpression(result1, result2,
      aggregation_function, structure_level, gene1, gene2) # hemisphere, 

    # https://plotly.com/python-api-reference/generated/plotly.express.scatter
    fig = px.scatter(Utils.sort_case_insensitive(data, structure_level), y=f"expression_level_{gene1}_{aggregation_function}", x=f"expression_level_{gene2}_{aggregation_function}"
          # TODO: there is some issue with sizes. besides NaN, we got some weird errors...
	        #,size=sizeBy#, size_max=400 
          ,color=structure_level
          ,opacity=0.65
          # https://plotly.com/javascript/reference/#parcats-dimensions-items-dimension-categoryorder
          #,dimensions={'categoryorder':'category ascending'} # sort categories 
          )

    
    
    fig.update_xaxes(title=gene2)           
    fig.update_yaxes(title=gene1)
    return fig

  # TODO: there are some NaNs...
  def stackedBarsBySpecies(self, aggregation_function, structure_level, species, gene, side): # hemisphere, 
    result = Comparison.species_map[species](gene).get(from_cache=True, aggregations=AGGREGATION_FUNCTIONS.data)
    # TODO: deal with a list for mice (but sometimes it isnt...)
    if(species == 'mouse - sagittal'):
      result = result[0]      
    elif(species == 'mouse - coronal'):
      result = result[1]      

    return heatmap(Comparison.by_region(
      result.data.structure, 
      aggregation_function, 'global-z-score', f'level_{structure_level}', 'structure_name')
    )

  def callbackInputsToKwags(self, input):
    return { input[i]['id']['type']:input[i]['value']  for i in range(0,len(input)) }

  def gridView(self, viewName, filters):
    return html.Div(
          dbc.Card(dbc.CardBody([
            dbc.Form( # we get an array (label + dropdown) inside an array. so we need to unpack that
              dbc.FormGroup(Utils.unpack(self.dropDownByList(lst, {'type': lst.type, 'view': viewName}, value=lst.default) for lst in filters))
            , inline=True), 
            html.Div(
              dash_pivottable.PivotTable(
              id={ 'type': 'grid', 'view': viewName },
          data=[], #
        #cols=['Day of Week'],
        #colOrder="key_a_to_z",
        #rows=['Party Size'],
        #rowOrder="key_a_to_z",
        #rendererName="Grouped Column Chart",
        aggregatorName="Average"
        #vals=["Total Bill"],
        #valueFilter={'Day of Week': {'Thursday': False}}
        )
              )]
          , className="p-2", style={ 'width': 'calc(100vw - 8px)'})))

  def getPivotTable(self, species, gene, structure_level):
    #data = []
    #print(filters)
    return Comparison.species_map[species](gene).get(from_cache=True, aggregations=AGGREGATION_FUNCTIONS.data).data.structure
  
  # TODO: two range-sliders (for x and y) on common-control-div to allow synchronization of axis. 
  # # TODO or maybe is it possible to callback to hidden controls to then trigger updates on the axis?
  def sideBySideView(self, viewName, commonFilters, sideFilters):
    dimensions = Utils.simple({ 'w': 'calc(49vw - 30px)', 'h': 'calc(100vh - 320px)' })

    return html.Div([
          dbc.Card(dbc.CardBody(
          dbc.Form( # we get an array (label + dropdown) inside an array. so we need to unpack that
            dbc.FormGroup(Utils.unpack(self.dropDownByList(lst, {'type': lst.type, 'view': viewName}, value=lst.default) for lst in commonFilters))
          , inline=True), className="p-2")),
          dbc.Row([
                dbc.Col([
                  dbc.Row(
                    dbc.Form(
                      dbc.FormGroup( # TODO: make this responsive, because they overlap on smaller screens
                        Utils.unpack(self.dropDownByList(lst, {'type': lst.type, 'side': 'left', 'view': viewName}, value=lst.defaultLeft) for lst in sideFilters)
                        #+ [self.downloadButton(id={'action': 'download', 'side': 'left', 'view': viewName})]
                      ), inline=True, className="ml-4 mt-3")
                  ),
                  dbc.Row(html.Div(dcc.Loading(
                    dcc.Graph(id={ 'type': 'graph', 'view': viewName, 'side': 'left'}, config={'scrollZoom': True}, style={'width': dimensions.w, 'height': dimensions.h})
                  )), className="ml-2 mt-3")
                ], className="border-right"),
                dbc.Col([
                  dbc.Row(
                    dbc.Form(
                      dbc.FormGroup(
                        Utils.unpack(self.dropDownByList(lst, {'type': lst.type, 'side': 'right', 'view': viewName}, value=lst.defaultRight) for lst in sideFilters)
                      ), inline=True, className="ml-4 mt-3")
                  ),
                  dbc.Row(html.Div(dcc.Loading(
                    dcc.Graph(id={ 'type': 'graph', 'view': viewName, 'side': 'right'}, config={'scrollZoom': True}, style={'width': dimensions.w, 'height': dimensions.h})
                  )), className="ml-2 mt-3")
                ])
          ])
        ], className="p-2", style={ 'width': 'calc(100vw - 8px)'})

  # https://community.plotly.com/t/gluphicons-in-bootstrap-buttons/23438/2
  #def downloadButton(self, **kwags):
#    return dbc.Button(["Download", html.I(className="fas fa-plus-circle ml-2")], **kwags)


  def dropDownByList(self, lst, idProps, **kwags):
    return ([dbc.Label(lst.label, className="mr-2")] if not lst.label is None else []) + [dbc.Select(id={'type': lst.type, 'input': True, **idProps}, 
      options=[{ "label": g, "value": g } for g in lst.data], className="mr-3", **kwags)]

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
  # TODO: always start at (0, 0) in every chart

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


