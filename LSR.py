#!C:\Python27\python
import sys
import time
import thread
from socket import *
import json
from copy import deepcopy


neighbors = {}
# "neighbors" is the dictionary conatining information about the neighbors.
nodes = {}
# "node" is the current node or the starting node.
alive={}



#taking argumenst file to be read( the starting node, port number) 
if(len(sys.argv))<4:
	print("Not enough arguments passsed") 
try:
	file = open(sys.argv[3])
	total = file.readline();

	total = int(total)
	for i in range(0,total):
		row = file.readline()
		row = row.split(" ")
		neighbors[row[0]] = {
			"cost":row[1],
			"port":int(row[2])
		}
	nodes[sys.argv[1]] = [neighbors]
except:
	print("There was error in reading the file")
finally:
	file.close()


# message is recieved, json loads message. updates according to packet numbers.

def receiveNeighbors():
	serverIP="localhost"
	serverPort= int(sys.argv[2])

	serverSocket=socket(AF_INET,SOCK_DGRAM)

	serverSocket.bind((serverIP,serverPort))
	sequenceNumbers = {}
	while 1:
	    message,clientAddress=serverSocket.recvfrom(2048)
	    message = json.loads(message)
	    recfrom = message['from']
	    origin = message['origin']
	    pNo = message['pno']
	    if origin not in sequenceNumbers or sequenceNumbers[origin]<pNo:
	    	sequenceNumbers[origin] = pNo
	    	message['from'] = sys.argv[1]
	    	nodes[origin]=message['neighbors']
	    	alive[origin]=message['time']
	    	message = json.dumps(message)

	    	for key,value in neighbors.items():
	    		if key!=origin and key != recfrom:
	    			clientSocket = socket(AF_INET,SOCK_DGRAM)
	    			clientSocket.sendto(message,('localhost',value['port']))
	    	# print(recfrom,origin,pNo)



# client socket is made, message is generated and sent to the server.

def sendNeighbors():
	clientSocket = socket(AF_INET,SOCK_DGRAM)
	pno = 0
	while True:
		pno = pno+1
		message = {
			'pno':pno,
			'neighbors':neighbors,
			'time':time.time(),
			'origin':sys.argv[1],
			'from':sys.argv[1]
		}
		message = json.dumps(message)
		for key,value in neighbors.items():
			clientSocket.sendto(message,('localhost',value['port'])) 
			# print("sent")
		time.sleep(1)


# dijkstra 

def dijkstra(key,comming,cost,tree,bestCost):
	if key not in bestCost:
		bestCost[key] = {}
		bestCost[key]['cost'] = 9999999
		bestCost[key]['path'] = ""
	previousCost = bestCost[key]['cost']
	currentCost = float(bestCost[comming]['cost'])+float(cost)
	if previousCost>currentCost and key in tree:
		bestCost[key]['cost'] = currentCost
		bestCost[key]['path'] = bestCost[comming]['path']+key
		currentNeighbors = tree[key]
		for neighbor,value in currentNeighbors.items():
			dijkstra(neighbor,key,value['cost'],tree,bestCost)





def calculate():
	while True:
		time.sleep(10)
		tree = deepcopy(nodes)
		currentTime = time.time()
		for key, value in alive.items():
			if (currentTime - value)>5:
				del tree[key]
		bestCost={}
		currentNeighbors = tree[sys.argv[1]]
		bestCost[sys.argv[1]]={}
		bestCost[sys.argv[1]]['path'] = sys.argv[1]
		bestCost[sys.argv[1]]['cost'] = 0
		for key,value in neighbors.items():
			dijkstra(key,sys.argv[1],value['cost'],tree,bestCost)
		print("I'm router "+sys.argv[1])
		for key,value in bestCost.items():
			if(value['cost']<999999 and value['cost']>0):
				print("Least cost path to router "+str(key)+":"+str(value['path'])+" and the cost: "+str(value['cost']))
	# print nodes
	# print alive


# threads. 

try:
   thread.start_new_thread( sendNeighbors, () )
   thread.start_new_thread( receiveNeighbors, () )
   thread.start_new_thread( calculate, () )
   
except:
   print "Error: unable to start thread"
# calculate()

while 1:
   time.sleep(100)