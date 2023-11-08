"""
.. module:: MRKmeans

MRKmeans
*************

:Description: MRKmeans

    Iterates the MRKmeansStep script

:Authors: bejar
    

:Version: 

:Created on: 17/07/2017 10:16 

"""
from __future__ import print_function, division

from MRKmeansStep import MRKmeansStep
import shutil
import argparse
import os
import time
from mrjob.util import to_lines

__author__ = 'bejar'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prot', default='prototypes.txt', help='Initial prototpes file')
    parser.add_argument('--docs', default='documents.txt', help='Documents data')
    parser.add_argument('--iter', default=5, type=int, help='Number of iterations')
    parser.add_argument('--nmaps', default=2, type=int, help='Number of parallel map processes to use')
    parser.add_argument('--nreduces', default=2, type=int, help='Number of parallel reduce processes to use')

    args = parser.parse_args()
    assign = {}

    # Copies the initial prototypes
    cwd = os.getcwd()
    shutil.copy(cwd + '/' + args.prot, cwd + '/prototypes0.txt')

    nomove = False  # Stores if there has been changes in the current iteration
    for i in range(args.iter):
        tinit = time.time()  # For timing the iterations

        # Configures the script
        print('Iteration %d ...' % (i + 1))
        # The --file flag tells to MRjob to copy the file to HADOOP
        # The --prot flag tells to MRKmeansStep where to load the prototypes from
        mr_job1 = MRKmeansStep(args=['-r', 'local', args.docs,
                                     '--file', cwd + '/prototypes%d.txt' % i,
                                     '--prot', cwd + '/prototypes%d.txt' % i,
                                     '--jobconf', 'mapreduce.job.maps=%d' % args.nmaps,
                                     '--jobconf', 'mapreduce.job.reduces=%d' % args.nreduces])

        # Runs the script
        with mr_job1.make_runner() as runner1:
            runner1.run()
            new_assign = {}
            new_proto = {}
            # Process the results of the script, each line one results
            for line in to_lines(runner1.cat_output()):
                key, value = mr_job1.parse_output_line(line)
                new_proto[key] = value[1]
                new_assign[key] = value[0]

            # Save actual assignement in a file
            file = open(cwd + '/assignments' + str(i+1) + '.txt', 'w')
            for key in new_assign:
                aux = ""
                for el in new_assign[key]:
                    aux = aux + el + ' '
                newAssignFile.write(key + ':' + aux + '\n')
            file.close()

            # Check if there's been a change in the assignement, if not the execution ends
            # otherwise we update the assignement value
            if new_assign == assign:
                nomove = True
            assign = new_assign

            # Save the actual prototype in a file
            file = open(cwd + '/prototypes' + str(i+1) + '.txt' , 'w')
            for key in new_proto:
                auxString = key + ':'
                for item in new_proto[key]:
                    auxString = auxString + item[0] + '+' + repr(item[1]) + ' '
                auxString = auxString[:-1]
                newProtoFile.write(auxString + '\r\n')
            file.close()

        print("Time= %f seconds" % (time.time() - tinit))

        if nomove:  # If there is no changes in two consecutive iteration we can stop
            print("Algorithm converged")
            break

    # Now the last prototype file should have the results
