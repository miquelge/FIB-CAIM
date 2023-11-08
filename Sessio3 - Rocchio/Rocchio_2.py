
from __future__ import print_function
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch.client import CatClient
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q
import argparse
import math
import operator
import numpy as np

nrounds = int(5)
k = int(10)
r = int(5)
alpha = 0.9
beta = 1-alpha

def search_file_by_path(client, index, path):
    """
    Search for a file using its path

    :param path:
    :return:
    """
    s = Search(using=client, index=index)
    q = Q('match', path=path)  # exact search in the path field
    s = s.query(q)
    result = s.execute()

    lfiles = [r for r in result]
    if len(lfiles) == 0:
        raise NameError('File [%s] not found'%path)
    else:
        return lfiles[0].meta.id

def document_term_vector(client, index, id):
    """
    Returns the term vector of a document and its statistics a two sorted list of pairs (word, count)
    The first one is the frequency of the term in the document, the second one is the number of documents
    that contain the term

    :param client:
    :param index:
    :param id:
    :return:
    """
    termvector = client.termvectors(index=index, doc_type='document', id=id, fields=['text'],
                                    positions=False, term_statistics=True)

    file_td = {}
    file_df = {}

    if 'text' in termvector['term_vectors']:
        for t in termvector['term_vectors']['text']['terms']:
            file_td[t] = termvector['term_vectors']['text']['terms'][t]['term_freq']
            file_df[t] = termvector['term_vectors']['text']['terms'][t]['doc_freq']
    return sorted(file_td.items()), sorted(file_df.items())

def toTFIDF(client, index, file_id):
    """
    Returns the term weights of a document

    :param file:
    :return:
    """

    # Get document terms frequency and overall terms document frequency
    file_tv, file_df = document_term_vector(client, index, file_id)
    #print (file_df)

    max_freq = max([f for _, f in file_tv])

    dcount = doc_count(client, index)

    tfidfw = {}
    for (t, w),(_, df) in zip(file_tv, file_df):
        tfidfw[t] = (w / max_freq * np.log2(dcount/df))
    return normalize(tfidfw)

def print_term_weigth_vector(twv):
    """
    Prints the term vector and the correspondig weights
    :param twv:
    :return:
    """
    for (t, w) in twv.items():
        print(t,w)

def normalize(tw):
    """
    Normalizes the weights in t so that they form a unit-length vector
    It is assumed that not all weights are 0
    :param tw:
    :return:
    """
    total = np.sqrt(sum([ np.power(f,2) for _, f in tw.items()]))
    if total != 0:
        for t, val in tw.items():
            tw[t] = val / total
    return tw

def cosine_similarity(tw1, tw2):
    """
    Computes the cosine similarity between two weight vectors, terms are alphabetically ordered
    :param tw1:
    :param tw2:
    :return:
    """
    dotProduct = 0
    i = 0
    j = 0
    tw1List = list(tw1.items())
    tw2List = list(tw2.items())
    tw1List.sort()
    tw2List.sort()
    while (i < len(tw1) and j < len(tw2)):
        t1, w1 = tw1List[i]
        t2, w2 = tw2List[j]
        if (t1 == t2):
            dotProduct = dotProduct + w1 * w2
            i = i + 1
            j = j + 1
        elif (t1 < t2):
            i = i + 1
        else:
            j = j + 1

    return dotProduct

def doc_count(client, index):
    """
    Returns the number of documents in an index

    :param client:
    :param index:
    :return:
    """
    return int(CatClient(client).count(index=[index], format='json')[0]['count'])

def query_to_list(query):
    list = {}
    for word in query:
        if "^" not in word:
            list[word] = 1
        else:
            s = word.split("^")
            list[s[0]] = s[1]
    return list

def list_to_query(list):
    print ("list_to_query")
    query="["
    for t, w in list.items():
        if (int(w) < 1.0):
            query += "'"+t+"',"
        else:
            query += "'"+t+"^"+str(int(w))+"',"
    query += "]"
    print (query)
    print ("out of list_to_query")
    return query

def Rocchio(alpha, beta, query, t_query, nhits):
    newquery = {}
    for word, weight in t_query.items():
        newquery[word] = beta * weight
    for word, weight in query.items():
        newquery[word] = newquery.get(word,0) + alpha * weight
    ret = dict(sorted(newquery.iteritems(), key=operator.itemgetter(1), reverse=True)[:5])
    return ret

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, help='Index to search')
    parser.add_argument('--nhits', default=10, type=int, help='Number of hits to return')
    parser.add_argument('--query', default=None, nargs=argparse.REMAINDER, help='List of words to search')

    args = parser.parse_args()

    index = args.index
    query = args.query
    #print(query)
    nhits = args.nhits
    

    try:
        client = Elasticsearch()
        s = Search(using=client, index=index)

        if query is not None:
            
            #original query
            q = Q('query_string',query=query[0])
            for i in range(1, len(query)):
                q &= Q('query_string',query=query[i])
            query_aux = query_to_list(query)
            print (query_aux)


            #nrounds -1 iterations
            for x in range(0, nrounds-1):
                #execution
                print ("round", x)
                print(query)
                print(q)
                print()
                s = s.query(q)
                
                ##print("post query")
                response = s[0:k].execute()
                

                #grab k relevant and see tfidf
                dic = {}
                for r in response:
                    tw = toTFIDF(client, index, r.meta.id)
                    for key, value in tw.items():
                        dic[key] = dic.get(key,0) + value


                # new query
                query_aux = Rocchio(alpha, beta, query_aux, dic, nhits)
                query = list_to_query(query_aux)
                q = Q('query_string',query=query[0])
                for i in range(1, len(query)):
                    q &= Q('query_string',query=query[i])


            #last search
            s = s.query(q)
            response = s[0:nhits].execute()
            for r in response:  # only returns a specific number of results
                print('ID= %s SCORE=%s' % (r.meta.id,  r.meta.score))
                print('PATH= %s' % r.path)
                print('TEXT: %s' % r.text[:50])
                print('-----------------------------------------------------------------')

        else:
            print('No query parameters passed')

        print ('%d Documents'% response.hits.total)

    except NotFoundError:
        print('Index %s does not exists' % index)

