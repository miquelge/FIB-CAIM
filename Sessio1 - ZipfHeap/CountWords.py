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

import string
import argparse
import matplotlib.pyplot as plt
import csv

csv_file = "./dades.csv"
__author__ = 'bejar'



abecedari = set(string.ascii_lowercase) | set(string.ascii_uppercase) | {'-'}

def sida (paraula):
	for x in paraula:
		if x not in abecedari:
			#print(paraula);
			return True
	return False

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--index', default=None, required=True, help='Index to search')
	parser.add_argument('--alpha', action='store_true', default=False, help='Sort words alphabetically')
	args = parser.parse_args()

	index = args.index

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
			if not sida(v):
				lpal.append((v.encode("utf8", "ignore"), voc[v]))
		print ("Tenim %s paraules en total" %len(lpal))


		freqs = []
		for pal, cnt in sorted(lpal, key=lambda x: x[0 if args.alpha else 1]):
			#print('%d, %s' % (cnt, pal.decode("utf-8")))
			if 50 < cnt < 16000:
				freqs.append(cnt)
		print ("Ara tenim %s paraules" %len(freqs))
		#print(freqs)
		

		with open (csv_file, "w", newline = '') as csvfile:
			writer = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting= csv.QUOTE_MINIMAL)
			for val in freqs:
				if 50 < val < 16000:
					#print ("write de : %s" % val)
					writer.writerow([val])
		
		#print('%s Words' % len(freqs))
		#plt.plot(freqs)
		#plt.gca().invert_xaxis()
		#plt.ylabel('Zipf’s law')
		#plt.show()


	except NotFoundError:
		print('Index %s does not exists' % index)



