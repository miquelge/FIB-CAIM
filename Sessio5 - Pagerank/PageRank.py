import time
import sys
from math import pow

class Edge:
	def __init__ (self, origin = None, listIndex = None):
		self.origin = origin
		self.weight = 1
		self.listIndex = listIndex	# index of the airport origin (identified with the
									# atribute origin) in the Airport List

	def __repr__(self):
		return "edge: {0} {1}".format(self.origin, self.weight)

class Airport:
	def __init__ (self, iden = None, name = None, index = None):
		self.code = iden
		self.name = name
		self.routes = []
		self.routeHash = dict()
		self.outweight = 0

	def __repr__(self):
		return "{0} {1} {2} \n".format(self.code, self.name, self.routes)

edgeList = [] # list of Edge
edgeHash = dict() # hash of edge to ease the match
airportList = [] # list of Airport
airportHash = dict() # hash key IATA code -> Airport
maxIterations = 500


def readAirports(fd):
	print("Reading Airport file from {0}".format(fd))
	airportsTxt = open(fd, "r");
	cont = 0
	for line in airportsTxt.readlines():
		a = Airport()
		try:
			temp = line.split(',')
			if len(temp[4]) != 5 :
				raise Exception('not an IATA code')
			a.name=temp[1][1:-1] + ", " + temp[3][1:-1]
			a.code=temp[4][1:-1]
		except Exception as inst:
			pass
		else:
			airportList.append(a)
			airportHash[a.code] = cont
			cont += 1

	airportsTxt.close()
	print("Read Airports: There were {0} Airports with IATA code".format(cont))

def readRoutes(fd):
	print("Reading Routes file from {0}".format(fd))
	routesTxt = open(fd, "r");
	cont = 0
	for line in routesTxt.readlines():
		#print (line)
		try: 
			temp = line.split(',')
			
			#check for the origin and destination codes to be IATA codes
			if len(temp[2]) != 3 or len(temp[4]) != 3:
				raise Exception('not an IATA code')
			
			origin = temp[2]
			destination = temp[4]

			# obtain origin and destination airports
			if not (origin in airportHash) or not (destination in airportHash):
				raise Exception ("Could not find Airports")

			pos1 = airportHash[origin]
			originAirport = airportList[pos1]
			pos2 = airportHash[destination]
			destinationAirport = airportList[pos2]

			# if the edge exists increase its weight
			if origin in destinationAirport.routeHash:
				pos = destinationAirport.routeHash[origin]
				destinationAirport.routes[pos].weight += 1
			else: #otherwise we add the origin airport to the destination airport routes atribute
				pos = airportHash[origin]
				newEdge = Edge(origin, pos)
				destinationAirport.routes.append(newEdge)
				# since it didn't exist we also have to add it to
				# the routeHash
				destinationAirport.routeHash[origin] = len(destinationAirport.routes) - 1

			# we also need to add the corresponding weight to the origin Airport
			originAirport.outweight += 1

		except Exception as inst:
			pass
		else:
			cont += 1
	  
	routesTxt.close()
	print ("Read Routes: There were {0} routes with IATA code".format(cont))

def computePageRanks(left_behind):        
        print ("Calculating Page Rank")
        nAirports = len(airportList)
        P = [1.0/nAirports]*nAirports
        L = 0.90
        it = 0
        continuar = True
        nextv = 1.0/nAirports
        convergence = pow(10,-10)

        while (continuar):
            Q = [0.0]*nAirports
            
            for i in range(nAirports):
                airport = airportList[i]
                suma = 0
                for j in airport.routes:
                    weight = j.weight
                    outweight = airportList[j.listIndex].outweight
                    suma += P[j.listIndex] * weight / outweight
                        
                Q[i] = L * suma + (1.0 - L)/nAirports + nextv * L/nAirports*left_behind

            nextv = (1.0 - L)/nAirports + nextv*L/nAirports*left_behind
            continuar = it < maxIterations
            diference = [abs(a - b) for a, b in zip(P, Q)]
            #print("Diference with last: " + str(sum(diference)))
            continuar = continuar and (sum(diference) > convergence)
            #print ("sum must be 1 : "+ str(sum(Q)))
            P = Q
            it += 1

        global PageRank
        PageRank = P
        return it-1


def outputPageRanks():
    print ("PageRank Result:")
    nAirports = len(airportList)
    newPR = zip (PageRank, range(nAirports))
    orderedPageRank = sorted(newPR, reverse=True)
    position = 1; 
    for value, index in orderedPageRank:
    	print (str(position) + " : " + str(value) + " -> " +  str(airportList[index].name))
        position += 1



def main(argv=None):
	readAirports("airports.txt")
	readRoutes("routes.txt")
	#print (airportHash)
	#print (airportList)

	left_behind = 0
	for i in airportList:
		if (i.outweight == 0):
			left_behind = left_behind +1

	time1 = time.time()
	iterations = computePageRanks(left_behind)
	time2 = time.time()
	#print (PageRank)

	outputPageRanks()

	print("#Iterations:", iterations)
	print("Time of computePageRanks():", time2-time1)

if __name__ == "__main__":
	sys.exit(main())
