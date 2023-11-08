"""
.. module:: MRKmeansDef

MRKmeansDef
*************

:Description: MRKmeansDef

    

:Authors: bejar
    

:Version: 

:Created on: 17/07/2017 7:42 

"""

from __future__ import division
from mrjob.job import MRJob
from mrjob.step import MRStep

__author__ = 'bejar'


class MRKmeansStep(MRJob):
    prototypes = {}

    def jaccard(self, prot, doc):
        """
        Compute here the Jaccard similarity between  a prototype and a document
        prot should be a list of pairs (word, probability)
        doc should be a list of words
        Words must be alphabeticaly ordered

        The result should be always a value in the range [0,1]
        """
        unionSize = len(filter(lambda x: x[0] in doc, prot))
        return unionSize / float(len(prot) + len(doc) - unionSize)

    def configure_args(self):
        """
        Additional configuration flag to get the prototypes files

        :return:
        """
        super(MRKmeansStep, self).configure_args()
        self.add_file_arg('--prot')

    def load_data(self):
        """
        Loads the current cluster prototypes

        :return:
        """
        f = open(self.options.prot, 'r')
        for line in f:
            cluster, words = line.split(':')
            cp = []
            for word in words.split():
                cp.append((word.split('+')[0], float(word.split('+')[1])))
            self.prototypes[cluster] = cp

    def assign_prototype(self, _, line):
        """
        This is the mapper it should compute the closest prototype to a document

        Words should be sorted alphabetically in the prototypes and the documents

        This function has to return at list of pairs (prototype_id, document words)

        You can add also more elements to the value element, for example the document_id
        """

        # Each line is a string docid:wor1 word2 ... wordn
        doc, words = line.split(':')
        lwords = words.split()

        jaccard_values = []
        for key, value in prototypes.iteritems():
            jaccard_values.append(key, jaccard(prot, lwords))

        line_prototype = min(jaccard_values, key = lambda t: t[1])[0]
        
        # Return pair key, value
        yield line_prototype, (doc, lwords)

    def aggregate_prototype(self, key, values):
        """
        input is cluster and all the documents it has assigned
        Outputs should be at least a pair (cluster, new prototype)

        It should receive a list with all the words of the documents assigned for a cluster

        The value for each word has to be the frequency of the word divided by the number
        of documents assigned to the cluster

        Words are ordered alphabetically but you will have to use an efficient structure to
        compute the frequency of each word

        :param key:
        :param values:
        :return:
        """

        newPrototype = {}
        newDocuments = []
        totalDocuments = 0
        for doc in values:
            totalDocuments += 1
            newDocuments.append(doc[0])
            for word in doc[1]:
                if word in newPrototype:
                    newPrototype[word] += 1
                else:
                    newPrototype[word] = 1
        
        ret = []
        for word in newPrototype:
            ret.append((word, float(newPrototype[word]) / float(totalDocuments)))

        yield key, (sorted(newDocuments), sorted(ret, key=lambda x: x[0]))

    def steps(self):
        return [MRStep(mapper_init=self.load_data, mapper=self.assign_prototype,
                       reducer=self.aggregate_prototype)
            ]



# %%%%%%%%%%%%%%%%%%%%%%%% TESTING %%%%%%%%%%%%%%%%%%%%%%%
#   delete all when tested except for main and line 185
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



# def jaccard(prot, doc):
#         """
#         Compute here the Jaccard similarity between  a prototype and a document
#         prot should be a list of pairs (word, probability)
#         doc should be a list of words
#         Words must be alphabeticaly ordered

#         The result should be always a value in the range [0,1]
#         """
#         unionSize = len(filter(lambda x: x[0] in doc, prot))
#         return unionSize / float(len(prot) + len(doc) - unionSize)

# def jaccardTest():
#     prot = (("a",1.0),("b",1.0),("c",1.0),("d",1.0),("e",1.0),("f",1.0))
#     docs = [("a","b","c","f"), ("a","k","e","d","p","i"), ("a","b","q","l","n"), ("a","w","y")]
#     print(map(lambda doc: jaccard(prot, doc), docs))

# def assign_prototype(_, line):
#     """
#     This is the mapper it should compute the closest prototype to a document

#     Words should be sorted alphabetically in the prototypes and the documents

#     This function has to return at list of pairs (prototype_id, document words)

#     You can add also more elements to the value element, for example the document_id
#     """

#     # Each line is a string docid:wor1 word2 ... wordn
#     doc, words = line.split(':')
#     lwords = words.split()

#     jaccard_values = []
#     for key, value in prototypes.iteritems():
#         jaccard_values.append((key, jaccard(value, lwords)))

#     line_prototype = max(jaccard_values, key = lambda t: t[1])[0]
    
#     # Return pair key, value
#     #yield line_prototype, (doc, lwords)
#     return line_prototype, (doc, lwords)

# def assign_prototypesTest():
#     docs = [("doc1: a b c f"), ("doc2: a k e d p i"), ("doc3: a b q l n"), ("doc4: a w y")]
#     print(map(lambda doc: assign_prototype("", doc), docs))

if __name__ == '__main__':
    MRKmeansStep.run()
    # prototypes = {'CLASS0': [('a', 1.0), ('b', 1.0), ('d', 1.0)], 'CLASS1': [('a', 1.0), ('d', 1.0), ('e', 1.0)], 'CLASS2': [('c', 1.0), ('l', 1.0), ('n', 1.0)]}
    # print("Generating prototypes...\n")
    # print(prototypes)
    # print("\nRunning Jaccard unit test...\n")
    # jaccardTest()
    # print("\nRunning assign_prototype unit test...\n")
    # assign_prototypesTest()