# -*- coding: utf-8 -*-
"""world_data_2023.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/gist/sebalemus/7857ada466581575d9201776948b903a/world_data_2023.ipynb

#En este documento analizaremos un dataset con la informacion recopilada de distintos paises del mundo en el año 2023
"""

#importamos lobrerias
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans

import warnings
warnings.filterwarnings("ignore")

#carga el archivo con la ruta en la que lo almacenas
data = pd.read_csv("/content/sample_data/world-data-2023.csv")

data.head()

"""podemos ver en el head que hay columans con simbolos y comas ", " en sus columnas lo cual deberemos liompiar"""

data.info()

"""Observamos que hay varias columnas con el tipo de datos "Object" que podrían contener valores numéricos. Esto podría indicar que hay caracteres adicionales en esos campos, como símbolos de porcentaje o comas, que impiden que se reconozcan como números. Podemos limpiar y transformar estos datos según sea necesario para el análisis."""

#seleccionamos las columans a convertir y limpiar(son 20 columnas)
columnas_convertir_limpiar = [
    'Density\n(P/Km2)', 'Agricultural Land( %)', 'Land Area(Km2)',
    'Armed Forces size', 'Co2-Emissions', 'CPI', 'CPI Change (%)',
    'Minimum wage', 'Out of pocket health expenditure', 'Population',
    'Population: Labor force participation (%)', 'Tax revenue (%)',
    'Total tax rate', 'Unemployment rate', 'Urban_population',
    'Forested Area (%)', 'Gasoline Price', 'GDP',
    'Gross primary education enrollment (%)', 'Gross tertiary education enrollment (%)'
]

#limpiamos y convertimos las columnas, convertimos ($,',', % en ' ')
for column in columnas_convertir_limpiar:
    if data[column].dtype == 'object':
        data[column] = data[column].str.replace('%', '', regex=False).str.replace(',', '', regex=False).str.replace('$', '', regex=False).astype(float)

data.info()

"""observamos que hay muchos valores  nulos en el datset
procedemos alimpar los valores
"""

#seleccionamos solo las columnas numéricas
numeric_data_with_additional = data.select_dtypes(include=['float64'])
#usamos un estimador simpleimputer que se utiliza para completar los valores faltantes en los conjuntos de datos con la media en este caso
imputer = SimpleImputer(strategy='mean')
numeric_data_with_additional_imputed = imputer.fit_transform(numeric_data_with_additional)

"""#PCA

#ahora realizaremos un pca para reducir las dimensiones del dataset
"""

# procedemos a normalizar las coliumans con (media = 0, desviación estándar = 1)
scaler = StandardScaler()
scaled_data_with_additional = scaler.fit_transform(numeric_data_with_additional_imputed)

#ajustamos el modelo con el pca
pca_with_additional = PCA()#usamos el metodo PCA() para reducir las dimensiones
pca_result_with_additional = pca_with_additional.fit_transform(scaled_data_with_additional)#ajustamos el modelo

#usaremos las dos primeras componentes principales para la visualización
pca_2d_with_additional = pca_result_with_additional[:, :2]
pca_2d_df_with_additional = pd.DataFrame(pca_2d_with_additional, columns=['Componente Principal 1', 'Componente Principal 2'])
pca_2d_df_with_additional['País'] = data['Country']
plt.figure(figsize=(12, 8))
sns.scatterplot(x='Componente Principal 1', y='Componente Principal 2', data=pca_2d_df_with_additional)
plt.title('Visualización de las Dos Primeras Componentes Principales (Con Datos Adicionales)')
plt.xlabel('Componente Principal 1')
plt.ylabel('Componente Principal 2')
plt.show()

feature_loadings = pd.DataFrame(pca_with_additional.components_[:2], columns=numeric_data_with_additional.columns).T
feature_loadings.columns = ['Componente Principal 1', 'Componente Principal 2']

#ordenamos las características por su carga en la primera componente principal de mayor a menor
feature_loadings_sorted_by_cp1 = feature_loadings.sort_values(by='Componente Principal 1', ascending=False)

#mostramos las 10 características más importantes para cada componente principal
top_features_cp1 = feature_loadings_sorted_by_cp1.head(10)
bottom_features_cp1 = feature_loadings_sorted_by_cp1.tail(10)

print(top_features_cp1)
print(bottom_features_cp1)

"""Resumen:
La Componente Principal 1 en nuestro análisis de PCA ha revelado patrones significativos en los datos. Las características con cargas positivas, como "Esperanza de vida" y "Inscripción en educación terciaria", sugieren una fuerte asociación con el bienestar y el desarrollo en los países. Por otro lado, las características con cargas negativas, como "Tasa de mortalidad infantil" y "Tasa de fertilidad", ofrecen una perspectiva complementaria, posiblemente reflejando desafíos en la salud y el desarrollo.

Esta componente principal parece capturar una dimensión fundamental en nuestro conjunto de datos, posiblemente representando una medida del nivel de desarrollo y bienestar.

#Clustering

realizaremos un análisis de clustering para identificar grupos de objetos similares en los datos.
Usaremos K-means para agrupar países según sus características similares, utilizando las componentes principales que hemos obtenido.
"""

#determinamos el N° de clusters con el metodo 'codo' Vamos a ejecutar el
#método K-means para diferentes valores K y calcular la suma de las distancias al cuadrado
#dentro de los clusters, luego, graficaremos estos valores para encontrar el 'codo',
#que es el punto donde agregar otro cluster ya no proporciona una mejora significativa.
K_range = range(1, 11)
inertia = []
for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(pca_result_with_additional)
    inertia.append(kmeans.inertia_)

plt.figure(figsize=(10, 6))
plt.plot(K_range, inertia, marker='o')
plt.title('Método del Codo')
plt.xlabel('Número de Clusters (K)')
plt.ylabel('Inercia')
plt.xticks(K_range)
plt.grid(True)
plt.show()

"""podemos ver que tenemos iun valor optimo con K= 3, o K= 4"""

#aplicamos K-means con K=4
kmeans = KMeans(n_clusters=4, random_state=42)
clusters = kmeans.fit_predict(pca_result_with_additional)

#agregamos los clusters como columna qal datset original
data['Cluster'] = clusters

data.head(2)

#estadísticas descriptivas para cada cluster
cluster_summary = data.groupby('Cluster').mean()

pca_df = pd.DataFrame({
    'Componente Principal 1': pca_result_with_additional[:, 0],
    'Componente Principal 2': pca_result_with_additional[:, 1],
    'Cluster': clusters
})
sns.set(style="whitegrid")
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Componente Principal 1', y='Componente Principal 2', hue='Cluster', style='Cluster', palette='viridis', markers=['o', 's', 'D', 'X'], data=pca_df)
plt.title('Visualización de Clusters (K=4)')
plt.show()

cluster_number = 0
countries_in_cluster = data[data['Cluster'] == cluster_number]['Country']
print(f"Los países en el cluster {cluster_number} son:")
print(countries_in_cluster.tolist())

cluster_number = 1
countries_in_cluster = data[data['Cluster'] == cluster_number]['Country']
print(f"Los países en el cluster {cluster_number} son:")
print(countries_in_cluster.tolist())

cluster_number = 2
countries_in_cluster = data[data['Cluster'] == cluster_number]['Country']
print(f"Los países en el cluster {cluster_number} son:")
print(countries_in_cluster.tolist())

cluster_number = 3
countries_in_cluster = data[data['Cluster'] == cluster_number]['Country']
print(f"Los países en el cluster {cluster_number} son:")
print(countries_in_cluster.tolist())

"""#EDA"""

#resumen estadístico
statistical_summary = data.describe().T

# Gráfico de barras para comparar características entre clusters
plt.figure(figsize=(14, 6))
plt.subplot(1, 2, 1)
sns.barplot(x='Cluster', y='Co2-Emissions', data=data, palette='viridis')
plt.title('Emisión de CO2 por Cluster')
plt.ylabel('Emisión de CO2')
plt.xlabel('Cluster')
plt.subplot(1, 2, 2)
sns.barplot(x='Cluster', y='Gasoline Price', data=data, palette='viridis')
plt.title('Precio de la Gasolina por Cluster')
plt.ylabel('Precio de la Gasolina')
plt.xlabel('Cluster')
plt.tight_layout()
plt.show()

"""Estas diferencias pueden reflejar las variaciones económicas, industriales y políticas entre los clusters."""

# Gráfico de caja para comparar características entre clusters
plt.figure(figsize=(14, 6))
plt.subplot(1, 2, 1)
sns.boxplot(x='Cluster', y='Birth Rate', data=data, palette='viridis')
plt.title('Tasa de Natalidad por Cluster')
plt.ylabel('Tasa de Natalidad')
plt.xlabel('Cluster')
plt.subplot(1, 2, 2)
sns.boxplot(x='Cluster', y='Fertility Rate', data=data, palette='viridis')
plt.title('Tasa de Fertilidad por Cluster')
plt.ylabel('Tasa de Fertilidad')
plt.xlabel('Cluster')
plt.tight_layout()
plt.show()

"""Estas diferencias pueden reflejar variaciones en la estructura demográfica, las políticas familiares y los niveles de desarrollo entre los clusters.

matriz de correlaciones
"""

#exclimos las columnas de latitud y longitud de la matriz de correlación
correlation_matrix = data.drop(columns=['Latitude', 'Longitude']).select_dtypes(include=['float64']).corr()

plt.figure(figsize=(14, 10))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Matriz de Correlación')
plt.show()

# determinamos el número de filas y columnas necesarias en función del número de pares de correlación fuerte
num_rows = int(len(strong_correlation_pairs) / 3) + (len(strong_correlation_pairs) % 3 > 0)
num_cols = 3

fig, axes = plt.subplots(num_rows, num_cols, figsize=(18, 5 * num_rows))
axes_flat = axes.flatten() if num_rows > 1 else axes #aplanamos los ejes para facilitar la iteración

#iteramos sobre los pares de características fuertemente correlacionadas
for i, (feature1, feature2) in enumerate(strong_correlation_pairs):
    sns.scatterplot(x=feature1, y=feature2, hue='Cluster', data=data, ax=axes_flat[i])
    axes_flat[i].set_title(f'{feature1} vs {feature2}')
    axes_flat[i].legend(title='Cluster', loc='upper left')

for i in range(len(strong_correlation_pairs), num_rows * num_cols):#eliminamos los ejes adicionales si hay más subparcelas que gráficos
    fig.delaxes(axes_flat[i])
plt.tight_layout()
plt.show()

"""#interpretación de los clusteres

primeros veremos distintas visualizaciones para encontrar las caractericticas ams importantes en cada grupo, para esto usaremos las caracteriticas mas representativas
"""

cluster_means = data.groupby('Cluster').mean()#media de cada cluster
std_deviation = cluster_means.std()#desv estand de medias entre clusters
mean_of_means = cluster_means.mean()#la media de las medias entre los clusters
feature_variation = std_deviation / mean_of_means#variación relativa como la desviación estándar dividida por la media de medias

top_features = feature_variation.nlargest(5)#seleccionamos las 5 características con la mayor variación relativa
print(top_features)

fig, axes = plt.subplots(3, 2, figsize=(15, 12))
axes_flat = axes.flatten()

for i, feature in enumerate(top_features.index):
    sns.barplot(x='Cluster', y=feature, data=data, ax=axes_flat[i], palette='viridis')
    axes_flat[i].set_title(f'{feature} por Cluster')
    axes_flat[i].set_ylabel(feature)
    axes_flat[i].set_xlabel('Cluster')

fig.delaxes(axes_flat[-1])
plt.tight_layout()
plt.show()

"""Los gráficos de barras anteriores muestran la media de las cinco características con la mayor variación relativa en cada uno de los cuatro clusters. Estas visualizaciones ofrecen una vista clara de cómo estas características clave diferencian los clusters:

Podemos interpretar los clusters de la siguiente manera:

Cluster 0: Países con economías medianas, emisiones moderadas de CO2, y fuerzas armadas relativamente grandes.
Cluster 1: Países más pequeños en términos de economía y fuerzas armadas, con bajas emisiones de CO2.
Cluster 2: Países con economías considerablemente grandes pero no tan grandes como el Cluster 3, emisiones moderadas de CO2.
Cluster 3: Países gigantes en términos de PIB, población, población urbana, y fuerzas armadas; emisiones de CO2 extremadamente altas.
Podemos asignar etiquetas descriptivas a cada cluster basadas en estas interpretaciones:

Cluster 0: "Economías Medianas"
Cluster 1: "Economías Menores"
Cluster 2: "Economías Emergentes"
Cluster 3: "Superpotencias Económicas"

estos insights podrían tener podrían tener aplicaciones prácticas en:
1. Política y Gobierno:
Ayuda Internacional: Identificar a los países que necesitan más ayuda en áreas como la reducción de emisiones de CO2, el desarrollo económico, o la urbanización.
Relaciones Diplomáticas: Entender cómo los países están agrupados puede ayudar a formar alianzas y acuerdos comerciales, especialmente con países con características similares.
2. Negocios e Inversiones:
Estrategia de Mercado: Las empresas pueden utilizar esta información para planificar su expansión en nuevos mercados, entendiendo las economías y características demográficas.
Inversiones: Los inversores pueden usar estos grupos para identificar oportunidades de inversión en países emergentes o en economías estables y grandes.
3. Salud y Educación:
Programas de Salud: Los organismos de salud pueden dirigir recursos y programas hacia los países que muestran necesidades específicas en términos de población y urbanización.
Educación: Los insights sobre la educación primaria y terciaria pueden guiar las inversiones en educación y los intercambios culturales y académicos.
4. Medio Ambiente:
Sostenibilidad: Los organismos medioambientales pueden dirigir esfuerzos de conservación y sostenibilidad hacia países con altas emisiones de CO2 y grandes áreas urbanas.
5. Defensa y Seguridad:
Alianzas Militares: Entender el tamaño y la capacidad de las fuerzas armadas puede guiar las decisiones de defensa, alianzas militares y acuerdos de paz.
En resumen, estos insights pueden guiar decisiones en una variedad de campos, desde la política y los negocios hasta la salud y el medio ambiente. La interpretación y aplicación de estos insights deben hacerse en colaboración con expertos en el área de interés para garantizar que se utilicen de manera ética y efectiva.

Aplicar los insights obtenidos en el contexto de la educación puede ofrecer una variedad de oportunidades para mejorar los sistemas educativos, identificar necesidades, y fomentar la colaboración internacional.
1. Identificación de Necesidades Educativas:
Cluster 3 (Superpotencias Económicas): Pueden tener sistemas educativos avanzados y recursos para invertir en educación terciaria y tecnología.
Cluster 0 y 2 (Economías Medianas y Emergentes): Pueden tener necesidades mixtas, con oportunidades para mejorar tanto la educación primaria como la terciaria.
Cluster 1 (Economías Menores): Pueden tener necesidades en la educación primaria y en la formación de docentes.
2. Colaboración y Alianzas Internacionales:
Entre Clusters Similares: Los países dentro de un mismo cluster pueden colaborar en programas educativos, compartiendo recursos y conocimientos.
Entre Clusters Diferentes: Los países de clusters con sistemas educativos más avanzados pueden ofrecer apoyo, formación y recursos a los de clusters con necesidades mayores.
3. Inversiones y Financiamiento:
Enfoque en la Educación Primaria: Para los países en clusters con bajos niveles de inscripción en la educación primaria, la inversión en infraestructura escolar y formación de docentes puede ser clave.
Fomento de la Educación Terciaria: Para los países en clusters con economías emergentes o grandes, la inversión en universidades y tecnología educativa puede impulsar la innovación y el crecimiento económico.
4. Políticas y Reformas Educativas:
Análisis Comparativo: Utilizar los datos para comparar políticas y prácticas educativas entre países similares y diferentes, identificando mejores prácticas.
Reformas a Medida: Diseñar reformas educativas que se ajusten a las características y necesidades de cada cluster, considerando factores como la economía, la urbanización y la población.
5. Programas de Intercambio y Movilidad:
Fomentar Intercambios: Establecer programas de intercambio entre países dentro y entre clusters, fomentando la diversidad y el aprendizaje intercultural.
Conclusión:
La aplicación de estos insights en el contexto de la educación requiere una colaboración estrecha con educadores, legisladores y otros expertos en el campo. La información puede ser una herramienta poderosa para informar decisiones y diseñar intervenciones que mejoren la calidad y el acceso a la educación en diferentes contextos nacionales.
"""