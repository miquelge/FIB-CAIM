"""
.. module:: CountWords

CountWords
*************

:Description: CountWords

    Generates a list with the counts and the words in the 'text' field of the documents in an index

:Authors: bejar
    

:Version: 

:Created on: 04/07/2017 11:58 

"""

from __future__ import print_function
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from elasticsearch.exceptions import NotFoundError, TransportError

import argparse
import enchant
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.optimize import curve_fit

__author__ = 'bejar'


# Función a optimizar
def func(rank, a, b, c):
    return c / np.power(rank + b, a)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, required=True, help='Index to search')
    parser.add_argument('--alpha', action='store_true', default=False, help='Sort words alphabetically')
    args = parser.parse_args()

    index = args.index
    
    d = enchant.Dict("en_GB")

    try:
        client = Elasticsearch()
        voc = {}
        sc = scan(client, index=index, doc_type='document', query={"query" : {"match_all": {}}})
        for s in sc:
            try:
                tv = client.termvectors(index=index, doc_type='document', id=s['_id'], fields=['text'])
                if 'text' in tv['term_vectors']:
                    for t in tv['term_vectors']['text']['terms']:
                        if t in voc:
                            voc[t] += tv['term_vectors']['text']['terms'][t]['term_freq']
                        else:
                            voc[t] = tv['term_vectors']['text']['terms'][t]['term_freq']
            except TransportError:
                pass
        lpal = []

        for v in voc:
            lpal.append((v.encode("utf8", "ignore"), voc[v]))
         
        # Se obtienen las palabras que existen en inglés   
        filtrado = []
  
        for pal, cnt in sorted(lpal, key=lambda x: x[0 if args.alpha else 1]):
            # Se comprueba con un diccionario que la palabra existe
            if(d.check(pal.decode("utf-8"))): 
                filtrado.append(cnt)
        print('%s Words' % len(filtrado))
        filtrado.reverse() # Las palabras están ordenadas en orden inverso, se le da la vuelta





        ydata = [ x for x in filtrado]
        xdata = [ x for x in range(1,len(ydata)+1)]
        plt.loglog(xdata,ydata) # Se muestra el grafico log-log de las palabras
	
        # Se obtienen los parametros a, b y c que mejor encajan
        popt, pcov = curve_fit(func, xdata[10:-1], ydata[10:-1], maxfev=5000)
        print(popt)
        # Se compara la solución con el original
        plt.loglog(xdata[10:-1], func(xdata[10:-1], *popt), 'r-', label='fit')
        plt.show()

        # Se muestra el gráfico de las muestras y las funciones en escala lineal para las 100
        #    primeras muestras
        plt.plot(xdata[10:-1],ydata[10:-1])
        plt.plot(xdata[10:-1], func(xdata[10:-1],*popt), 'r-', label='fit')
        plt.show()

    except NotFoundError:
        print('Index %s does not exists' % index)
