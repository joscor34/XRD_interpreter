# Importamos librerias necesarias para nuestro programa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

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

fig = px.line(df, x=' 2THETA', y=' PSD', labels={'Name': '2theta', 'Value': 'values'}, title='SrTiO3 difractograma')
fig.update_traces(marker=dict(color='red'))
fig.write_html("template/index.html")
fig.show()