# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__) # __name__ diz ao Dash onde a app está definida, para gerir caminhos e ficheiros estáticos.

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'fontSize': '40px'}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', # Menu suspenso em PT
                                                options=[ # 'label' → o texto mostrado no menu. 'value' → o valor devolvido quando a opção é escolhida.
                                                    {'label': 'All Sites', 'value': 'ALL'},
                                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                ],
                                                value='ALL', # valor inicial (por defeito) selecionado
                                                placeholder="Select a Launch Site here", # texto exibido quando nada está selecionado.
                                                searchable=True # permite filtrar a lista de opções existentes ao escrever
                                                ),
                                html.Br(), # Adiciona uma quebra de linha (<br> em HTML) — serve apenas para espaçar visualmente os elementos no ecrã

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"), 
                                # html.P() é um componente do Dash que cria um parágrafo (<p> em HTML).
                                # O texto dentro das aspas ("Payload range (Kg):") será exibido na página.
                                # <- parágrafo (texto simples)

                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', # Identificador único do componente. Necessário para callbacks.
                                                min=0, # Valor mínimo que o slider pode assumir (extremo esquerdo).
                                                max=10000, # Valor máximo que o slider pode assumir (extremo direito).
                                                step=1000, # Incremento mínimo ao mover o slider.
                                                # marks={0: '0',
                                                #        100: '100'}, # Dicionário que define rótulos visuais no slider. Formato: {valor: "texto exibido"}. Pode marcar intervalos importantes. 
                                                value=[min_payload, max_payload]
                                                ), # Lista com dois valores para o RangeSlider → define a posição inicial das duas “pontas” (início e fim do intervalo selecionado).

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),]
                                )

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
              # Output e Input são classes
              # Input: Representa entrada do callback
              # Output Representa saída do callback
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class', # Coluna do DataFrame que define o tamanho de cada fatia (slice)
        names='Launch Site', # Coluna do DataFrame que será usada para os rótulos das fatias
        title="Resultados de 'ALL'") # Título do gráfico (opcional).
        return fig
        # Para cada linha do DataFrame, px.pie pega o valor de class.
        # Para cada site, ele SOMA os valores de class de todas as linhas correspondentes.
        # Ou seja, o gráfico mostra a proporção de lançamentos bem sucedidos por site em relação ao total de sucessos
    else:
        # return the outcomes piechart for a selected site
         filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
         outcome_counts = filtered_df['class'].map({1:'Success', 0:'Failure'}).value_counts().reset_index() # outcome_counts is a Dataframe
         outcome_counts.columns = ['Outcome', 'Count']
         fig = px.pie(outcome_counts, values='Count', # Coluna do DataFrame que define o tamanho de cada fatia (slice)
         names='Outcome', # Coluna do DataFrame que será usada para os rótulos das fatias
         title=f"Resultados de {entered_site}") # Título do gráfico (opcional).
         return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
                [Input(component_id='site-dropdown', component_property='value'), Input(component_id='payload-slider', component_property='value'),])
def scatter_plot(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                          (spacex_df['Payload Mass (kg)'] <= high)]
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, 
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title='Scatter plot of Payload Mass (kg) vs Launch Sucess',  
                         )
        return fig
    else:
        filtered_df2 = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df2, 
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title=f'Scatter plot of Payload Mass (kg) vs Launch Sucess for {entered_site}',  
                         ) 
        return fig

# Run the app
if __name__ == '__main__':
    app.run(port=8052)

