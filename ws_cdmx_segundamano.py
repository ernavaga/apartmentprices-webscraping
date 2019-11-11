#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Librerías
import urllib.request as urllib2
from bs4 import BeautifulSoup
import csv
import json

# Adaptado del libro Web Scraping with Python - Richard Lawson
def download(url, user_agent='wswp', num_retries=2):
    headers = {'User-agent': user_agent}
    request = urllib2.Request(url, headers=headers)
    try:
        html = urllib2.urlopen(request).read()
    except urllib2.URLError as e:
        print ('Download error:', e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # retry 5XX HTTP errors
                return download(url, user_agent, num_retries-1)
    return html

""" Urls tomadas del análisis del mapa de sitio, se colocan solamente las urls de las 3 alcaldías.
    Se puede transformar para cambiar de ciudad además de alcaldía y municipio.
    Se agrega el filtro de precio para dejar solo los reportados en precio de 5,000 a 12,000 pesos.
    Dentro del archivo robots.txt se encuentran habilitados todos los agentes, se limita el acceso a
    las cuentas personales de los usuarios.
""" 
urls = ['https://www.segundamano.mx/anuncios/ciudad-de-mexico/cuauhtemoc/renta-inmuebles',
       'https://www.segundamano.mx/anuncios/ciudad-de-mexico/miguel-hidalgo/renta-inmuebles',
       'https://www.segundamano.mx/anuncios/ciudad-de-mexico/benito-juarez/renta-inmuebles']
filtro = '&precio=5000-12000'

""" La lógica del código es tomar las primeras 10 páginas de cada dataset, en cada una aparecen los
    datos principales de 30 departamentos, de cada uno de ellos se guarda su url para posteriormente
    explorar detalles adicionales de cada uno de ellos.
    En ambos casos la información está dentro de un formato json integrado en el html.
"""
webs = []
for u in urls:
    for i in range(10):
        url = u + '?pagina=' + str(i+1) + filtro
        html = download(url)
        soup = BeautifulSoup(html, 'lxml')
        json_extract = soup.find(attrs={"type":"application/ld+json"})
        json_output= BeautifulSoup(str(json_extract), 'lxml')
        json_text=json_output.get_text()
        json_data = json.loads(json_text)
        for j in range(30):
            data1 = json_data['itemListElement'][j]["url"]
            webs.append(data1)
     
# Se guardan el nombre, descripción, precio, moneda, fecha, ubicación (ciudad, alcaldía)
name = []
desc = []
price = []
currency = []
date =[]
locality = []
suburb = []
k = 0

# En cada una de las urls se van a buscar los datos antes mencionados
for w in webs:
    html_ = download(webs[k])
    soup_ = BeautifulSoup(html_, 'lxml')
    json_extract_ = soup_.find(attrs={"type":"application/ld+json"})
    json_output_= BeautifulSoup(str(json_extract_), 'lxml')
    json_text_=json_output_.get_text()
    json_data_ = json.loads(json_text_)
    name.append(json_data_[0]['name'])
    desc.append(json_data_[0]['description'])
    price.append(json_data_[0]['offers']['price'])
    currency.append(json_data_[0]['offers']['priceCurrency'])
    date.append(json_data_[0]['offers']['availabilityStarts'])
    locality.append(json_data_[0]['offers']['areaServed']['address']['addressLocality'])
    suburb.append(json_data_[1]['itemListElement'][5]['name'])
    k += 1

# Se unen cada una de las listas más la url en un listado general
segunda_m = zip(name,desc,price,currency,date,locality,suburb,webs)

# Se guarda el listado en una csv
with open('rentcdmx_segundamano.csv', "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['name','desc','price','currency','date','locality','suburb','url'])
    for row in segunda_m:
        writer.writerow(row)

