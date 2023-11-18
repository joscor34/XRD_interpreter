# Importamos librerias necesarias para nuestro programa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go  # Ensure plotly.graph_objects is imported
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Initialize Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    dcc.Input(id='y_position_input', type='number', value=0),  # Input box for y-position value
    dcc.Graph(id='line-plot')  # Graph area
])


file = open('../SrTiO3.uxd', mode='r')

content = file.read()

partes_importantes = content.split(';')

tabla_contenido = partes_importantes[7]

titles = tabla_contenido[1:15]

tabla_contenido = tabla_contenido.replace(titles, '2THETA, PSD\n')
tabla_contenido = tabla_contenido.replace('       ', ', ')
tabla_contenido = tabla_contenido.replace('      ', ', ')

file.close()

output_file = open('data.csv', 'w')

output_file.write(tabla_contenido)

output_file.close()

df = pd.read_csv('data.csv')

y_position_value_global = 0
beta_constant_value = 0

@app.callback(
    Output('line-plot', 'figure'),
    [Input('y_position_input', 'value')]
)
def update_plot(y_position_value):
    # Create an interactive plot

    global y_position_value_global  # Se una la varibale de manera globar
    y_position_value_global = y_position_value  # Se guardan los datos en la variable global

    global beta_constant_value #Se una la varibale de manera globar
    
    fig = px.line(df, x=' 2THETA', y=' PSD', labels={'Name': '2theta', 'Value': 'values'}, title='SrTiO3 difractograma')
    fig.update_traces(line=dict(color='blue')) 
   
    # Add a line parallel to x-axis at y_position_value
    fig.add_shape(
        type='line',
        x0=df[' 2THETA'].min(),
        y0=y_position_value,
        x1=df[' 2THETA'].max(),
        y1=y_position_value,
        line=dict(color='red', width=2, dash='solid'),
    )

    #-------------------------------------------------
    #Se calcula la altura máxima en de la reflexión más grande:
    altura_reflexion_max = max(df[' PSD'].values) - y_position_value_global

    # Obtenemos la mitad de la distancia con de la reflexión mas grande usando el punto de referencia
    given_PSD_value = altura_reflexion_max/2

    # Se calcula la diferencia absoluta entre los dos valores dados y todos los datos de la columna PSD.
    df['Absolute_Difference'] = abs(df[' PSD'] - given_PSD_value)

    
   # Encuentra la fila con la menor diferencia encontrada
    closest_index = df['Absolute_Difference'].idxmin()

    closest_2THETA_value = df.loc[closest_index, ' 2THETA']
    closest_PSD_value = df.loc[closest_index, ' PSD']

    # Encontramos el siguiente valor más cercano
    next_upper_values = df[df[' PSD'] > given_PSD_value]
    if not next_upper_values.empty:
        next_upper_index = next_upper_values[' PSD'].idxmin()
        next_upper_2THETA = df.loc[next_upper_index, ' 2THETA']
        next_upper_PSD = df.loc[next_upper_index, ' PSD']
    
    #-------------------------------------------------

    promedio_de_dos_puntos = ((df[' 2THETA'][next_upper_index] + df[' 2THETA'][next_upper_index + 1])/2) + 0.003
    
    # Agregamos dos puntos con las coordenadas de closes index y el promedio de 2theta en el next_upper_index y next_upper_index + 1
    fig.add_trace(go.Scatter(x=[df[' 2THETA'][closest_index]], y=[df[' PSD'][closest_index]], mode='markers+text', text='Point A', textposition='bottom center', marker=dict(color='blue')))
    fig.add_trace(go.Scatter(x=[promedio_de_dos_puntos], y=[df[' PSD'][closest_index]], mode='markers+text', text='Point B', textposition='bottom center', marker=dict(color='red')))


    # Creamos una linea entre esos cos puntos
    fig.add_trace(go.Scatter(x=[df[' 2THETA'][closest_index], promedio_de_dos_puntos], y=[df[' PSD'][closest_index], df[' PSD'][closest_index]], mode='lines', line=dict(color='green', dash='dash')))
    
    
    # Se calcula la distancia con la formula euclidiana
    distance = np.sqrt((df[' 2THETA'][closest_index] - (promedio_de_dos_puntos))**2 + (df[' PSD'][closest_index] - df[' PSD'][closest_index])**2)


    beta_constant_value = distance  #Se guardan los datos en la variable global
    # Se agrega una anotación con esta distancia
    fig.add_annotation(
        x=(next_upper_2THETA + closest_2THETA_value)/2,
        y=df[' PSD'][closest_index],
        text=f'Distancia: {distance:.5f}', # Ponemos la distancia con 3 puntos decimales
        showarrow=True,
        arrowhead=1,
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=5050)