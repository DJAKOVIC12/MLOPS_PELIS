# -*- coding: utf-8 -*-
"""



Original file is located at
...https://drive.google.com/drive/folders/1wtcFH99-FQCtG5eeQ9uVnr5PUft-oXvU
"""

#Importación de librerias necesarias
import pandas as pd
import numpy as np
import json
import ast
import re

#Creamos el data set, a partir del CSV
df_movies = pd.read_csv('movies_dataset.csv')

df_credits = pd.read_csv('credits.csv')

"""Unimos los dos dataframe"""

#Cambio a numerico el tipo de datos de la columna ID
df_movies['id'] = pd.to_numeric(df_movies['id'], errors='coerce')

#Observo cuales son las columnas sin ID
df_movies[df_movies['id'].isnull()]

#Dado que solo son 3, decido eliminarlas
df_movies = df_movies.dropna(subset=['id'])

#Cambio el tipo de dato de float a int de la columna, para que coincida en ambos df
df_movies['id'] = df_movies['id'].astype(int)

df_merge = pd.merge(df_movies, df_credits, on='id', how='inner')

#df_merge.head()

#df_merge.info()
#Posee 26 columnas inicialmente
#Posee 45538 registros inicialmente

"""Eliminar las columnas que no serán utilizadas, video,imdb_id,adult,original_title,poster_path y homepage."""

#Eliminamos columnas que no se utilizarán
columns_drop = ['video', 'imdb_id', 'adult', 'original_title', 'poster_path', 'homepage']
df = df_merge.drop(columns_drop, axis=1)

"""Algunos campos, como belongs_to_collection, production_companies y otros (ver diccionario de datos) están anidados, esto es o bien tienen un diccionario o una lista como valores en cada fila, ¡deberán desanidarlos para poder y unirlos al dataset de nuevo hacer alguna de las consultas de la API! O bien buscar la manera de acceder a esos datos sin desanidarlos."""

#Creamos clase para desanidar las columnas
class desanidar:

    @staticmethod
    def convertir_a_str(valor):               #Creamos funcion para convertir valores a cadena de string
        if isinstance(valor, (list, dict)):   #Condicional para identificar una lista o diccionario
            return json.dumps(valor)          #Convierte la lista o diccionario en string
        return str(valor)                     #Convierte a string a valor

    @staticmethod
    def extraer_nombres(valor):                     #Creamos funcion para extraer el nombre que contiene el registro
        pattern = r"'name': '([^']*)'"              #Creamos variable con el formato de la expresion regular 'name': '([^']*)' - Debe decir name y todo lo que siga despues dentro de esos signos
        coincidencias = re.findall(pattern, valor)  #Buscamos la coincidencia entre la variable pattern y el registro evaluado 
        if len(coincidencias) > 0:                  #Si la coincidencia es distinta a vacio, se guarda en nombre, sino se devuelve None
            nombre = coincidencias[0]
            return nombre
        else:
            return None 

    @staticmethod
    def extraer_director(valor):                    #Creamos funcion para extraer el nombre del director que contiene el registro
        pattern = r"'Director', 'name': '([^']*)'"    #Creamos variable con el formato de la expresion regular 'name': '([^']*)' - Debe decir name y todo lo que siga despues dentro de esos signos
        coincidencias = re.findall(pattern, valor)  #Buscamos la coincidencia entre la variable pattern y el registro evaluado 
        if len(coincidencias) > 0:                  #Si la coincidencia es distinta a vacio, se guarda en nombre, sino se devuelve None
            nombre = coincidencias[0]
            return nombre
        else:
            return None

# Función para convertir una columna de strings en diccionarios
def convertir_a_dicc(column):
    return column.apply(lambda x: ast.literal_eval(x) if pd.notna(x) else np.nan)

# Función para desanidar una columna y obtener solo los nombres de los elementos
def Desanidar_columna(column):
    return column.apply(lambda x: ', '.join([d['name'] for d in x]) if isinstance(x, list) else np.nan)

# Función para convertir la columna 'belongs_to_collection' de strings en diccionario 
def convertir_a_dicc_btc(column):
    return column.apply(lambda x: {} if pd.isna(x) else ast.literal_eval(x))

# Función para desanidar la columna "belongs_to_collection" y obtener solo los nombres de las colecciones
def desanidar_btc(column):
    return column.apply(lambda x: x['name'] if isinstance(x, dict) and 'name' in x else np.nan)

#df['belongs_to_collection'] = df['belongs_to_collection'].apply(desanidar.convertir_a_str).apply(desanidar.extraer_nombres)
# Convertir los strings de las columnas en diccionarios
df['belongs_to_collection'] = convertir_a_dicc_btc(df['belongs_to_collection'])
# Desanidar el campo "belongs_to_collection" y obtener solo los nombres de las colecciones a las que pertenecen
df['belongs_to_collection'] = desanidar_btc(df['belongs_to_collection'])

#df['production_companies'] = df['production_companies'].apply(desanidar.convertir_a_str).apply(desanidar.extraer_nombres)
df['production_companies'] = convertir_a_dicc(df['production_companies'])
df['production_companies'] = Desanidar_columna(df['production_companies'])

#df['production_countries'] = df['production_countries'].apply(desanidar.convertir_a_str).apply(desanidar.extraer_nombres)
df['production_countries'] = convertir_a_dicc(df['production_countries'])
df['production_countries'] = Desanidar_columna(df['production_countries'])

df['spoken_languages'] = df['spoken_languages'].apply(desanidar.convertir_a_str).apply(desanidar.extraer_nombres)

df['director'] = df['crew'].apply(desanidar.convertir_a_str).apply(desanidar.extraer_director)

df = df.drop('crew', axis=1)

df['cast'] = convertir_a_dicc(df['cast'])
df['cast'] = Desanidar_columna(df['cast'])

df['genres'] = convertir_a_dicc(df['genres'])
df['genres'] = Desanidar_columna(df['genres'])

"""Los valores nulos de los campos revenue, budget deben ser rellenados por el número 0."""

#Cambiamos el tipo de dato de las columnas a int.
df['budget'] = df['budget'].astype(float)
df['revenue'] = df['revenue'].astype(float)
df.dtypes

#Opción B: df['budget'] = pd.to_numeric(df['budget'], errors='coerce')

#Rellenamos los nulos con 0
df['budget'] = df['budget'].fillna(0)

#Rellenamos los nulos con 0
df['revenue'] = df['revenue'].fillna(0)

"""Los valores nulos del campo release date deben eliminarse."""

df['release_date'].isnull().sum() #Hay 87 registros nulos
df = df.dropna(subset=['release_date']) #Eliminamos los registros nulos de la columna 'release_date'

"""De haber fechas, deberán tener el formato AAAA-mm-dd, además deberán crear la columna release_year donde extraerán el año de la fecha de estreno."""

#Normalizamos el formato de las fechas

# Convertir la columna de fechas a tipo datetime
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

# Verificar el formato de las fechas y contar los registros que no cumplen con el formato deseado
formato_deseado = '%Y-%m-%d'
registros_incorrectos = df['release_date'].dt.strftime(formato_deseado) != df['release_date']

# Contar el número de registros incorrectos
cantidad_registros_incorrectos = registros_incorrectos.sum()

print(cantidad_registros_incorrectos)

#Creamos columna 'release_year' y la rellenamos con los años de 'release_date'
df['release_year'] = df['release_date'].dt.year
print(df['release_year'])

#Creamos columna 'release_month' y la rellenamos con los meses de 'release_date'
df['release_month'] = df['release_date'].dt.month
print(df['release_month'])

#Creamos columna 'release_day' y la rellenamos con los dias de 'release_date'
df['release_day'] = df['release_date'].dt.day
print(df['release_day'])

"""Crear la columna con el retorno de inversión, llamada return con los campos revenue y budget, dividiendo estas dos últimas revenue / budget, cuando no hay datos disponibles para calcularlo, deberá tomar el valor 0."""

# Crear la columna 'return' y calcular el retorno de inversión
df['return'] = df['revenue'].div(df['budget'], fill_value=0)

# Establecer el valor 0 en los casos donde budget sea 0 o haya valores faltantes en revenue o budget
df.loc[(df['budget'] == 0) | (df['revenue'].isnull()) | (df['budget'].isnull()), 'return'] = 0

#Elimino la columna tagline, xq presenta casi el 50% de registros nulos
columns_delete = ['tagline' ]
df = df.drop(columns_delete, axis=1)

#Relleno la columna runtine con la media de duraciones de todas las peliculas
valor_medio = df['runtime'].mean()
df['runtime'] = df['runtime'].fillna(valor_medio)

#Relleno los nulos de la columna spoken_languages con su valor modal 
valor_modal = df['spoken_languages'].mode().values[0]
df['spoken_languages'] = df['spoken_languages'].fillna(valor_modal)

#Relleno los nulos de la columna original_language con su valor modal 
valor_modal = df['original_language'].mode().values[0]
df['original_language'] = df['original_language'].fillna(valor_modal)

#Relleno los nulos de Overview con 'Sin descripcion'
df['overview'] = df['overview'].fillna('Sin descripcion')

#Relleno los nulos de Director con 'Sin director'
df['director'] = df['director'].fillna('Sin director')

#Relleno los nulos de Status con 'Sin informacion'
df['status'] = df['status'].fillna('Sin informacion')

#Relleno los nulos de belongs_to_collection con 'Sin informacion'
df['belongs_to_collection'] = df['belongs_to_collection'].fillna('Sin informacion')

#Pasar a string, los datos object
df['belongs_to_collection'] = df['belongs_to_collection'].astype(str)
df['genres'] = df['genres'].astype(str)
df['original_language'] = df['original_language'].astype(str)
df['overview'] = df['overview'].astype(str)
df['production_companies'] = df['production_companies'].astype(str)
df['production_countries'] = df['production_countries'].astype(str)
df['spoken_languages'] = df['spoken_languages'].astype(str)
df['status'] = df['status'].astype(str)
df['title'] = df['title'].astype(str)
df['cast'] = df['cast'].astype(str)
df['director'] = df['director'].astype(str)

df['belongs_to_collection'] = df['belongs_to_collection'].astype(str)

df['earns'] = df['revenue'] - df['budget']

# Pasar a minúscula los registros de todas las columnas
df = df.applymap(lambda x: x.lower() if isinstance(x, str) else x)

df = df.reset_index(drop=True)

df.to_csv('movies_clean.csv', index=False)

df['director'].values

df.info()

df.head()