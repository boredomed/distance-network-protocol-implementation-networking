import sys
import socket
import json
import threading
import time
import os
import collections

current_node = sys.argv[1];
current_port = int(sys.argv[2]);
config = sys.argv[3];

d1={};
dis_vec={};
routing_table={}
all_unique_routers={}
neigh_through={}
displayLock=threading.Lock()

# Nodes Class
class Read:
    def __init__(self, current_node,current_port,config):  #self variable represents the instance of the object itself.
        self.current_node=current_node;
        self.current_port=current_port;

        global copy_dv;
        copy_dv={}
        neigh_list=[]
        all_nodes={}

        self.all_nodes=all_nodes
        self.neigh_list=neigh_list

        fo = open(config, "r+");    #Opening the file in read and write modes
        data=fo.read();             #Reading and storing it in data variable
        nodes=(data.split());       #Splits the string as words in a list

        i=1;
        length=len(nodes);          #Find total words in file

        d1[current_node]={'cost':float(0),'port':int(current_port)}

        while (i!=length):
            d1[nodes[i]]={'cost':float(nodes[i+1]),'port':int(nodes[i+2])} #Dict to store data from config file
            i+=3;

        j=0;
                                   #will contain only neighbour nodes names
        all_nodes={}                             #contins name -> cost of neighbourrs+current_node

        for values in d1:
            all_nodes[(d1.keys())[j]]=d1[values]['cost']
            if ((d1.keys())[j] != current_node):
                neigh_list.append( (d1.keys())[j] )       #Creating list of neighbours
            j=j+1

        #dis_vec.setdefault(current_node, {}).update(all_nodes)  #Storing it in as Dict with key as curren node
        dis_vec[current_node]=all_nodes                                                #Format y {A: {B:6.5,F:2.2}}
        copy_dv=dis_vec.copy()                                  #copy can be used when our dis vec gets updated

#Socket Programing
#Reciever
def Recv():
    recvIP="localhost"
    recvPort=current_port

    recv=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    recv.bind((recvIP,recvPort))

    dv_all_nodes={}                                   #stores all neigh+me with cost in me
    dv_parent={}                                      #stores neigh+me with key that is sender

    x={}

    print ("SERVER HERE!\nThe server is ready to receive")
    while 1:
        message, clientAddress = recv.recvfrom(2048)
        data_loaded = json.loads(message) #data loaded

        for keys in data_loaded.keys():
            sendr = keys
        for key,val in data_loaded[sendr].items():
            dv_all_nodes[key]=val

        '''This was the data that arrived from sender'''
        dv_parent[sendr]=dv_all_nodes.copy()   #copy so both are independent
                                        #dv_all_nodes has all neighbours of a node with their cost
        dv_all_nodes = {}                       #again initialized so can store new messange ie neighbours then

        '''Now creating routing table'''
        #initially it should only have the information of our neighbours
        #so is put equaal to config files
        routing_table[current_node]=copy_dv[current_node].copy()  #'''This is our data'''

        routing_table.update(dv_parent)        #This will append the incoming data with the out data+previous data
                                               #From other nodes

        '''Call to ballmanford it will find my cost to all the nodes then
        update the dis_vector that initially has only my neghbours
        but now it will have other nodes as well and least cost to them'''
        threading.Thread(target=ballman_ford, args=(routing_table,)).start()

    recv.close()

#Sender
def Sender():
      while 1:
        #Making list of all the neighbour port numbers
        serverIP="localhost"
        sender=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        list_t=json.dumps(dis_vec)

    	#sending data to each port in list
        for values in d1:
    		if int(d1[values]['port'])!=current_port:
    			sender.sendto(list_t.encode(),(serverIP, d1[values]['port']))
        time.sleep(5)
        sender.close()

#''''''''''''''''Ballman ford implementation''''''''''''''''
def ballman_ford(routing_table):
    all_routers=[]                                 #This store all the that are currently reached
                                                  #ie their dis vector info has been recieved
    for nodes in routing_table:
        for neighbour in routing_table[nodes]:
            all_routers.append(neighbour)          #The will the duplications in it

    allr_set=set(all_routers)
    all_unique_routers = list(allr_set)   #Because set only store unique data

    my_neigh=[]
    for node in routing_table:
        for neighbour in node1.neigh_list:  #cant access class
            if(node == neighbour):
                #dead links excluded
                my_neigh.append(node)

    for nodes in routing_table:                   #these are nodes whose data is recieved
        for node in all_routers:                  #these are all the current nodes accesed
            if(node not in routing_table[nodes].keys()): #node is not in the list of routing table
                routing_table[nodes][node] = float('inf')

                '''Algorithm'''
    for d_nodes in all_routers:
        for my_neighbour in my_neigh:
            if(routing_table[current_node][d_nodes] > routing_table[current_node][my_neighbour]+routing_table[my_neighbour][d_nodes]):
                tempp = routing_table[current_node][my_neighbour]+routing_table[my_neighbour][d_nodes]
                routing_table[current_node][d_nodes]=tempp
                neigh_through[d_nodes]=my_neighbour        #This stores hop through which the route to dest starts
            elif(len(neigh_through) != len(all_routers)):  #This will save processing in that node
                neigh_through[d_nodes]='direct'

    #dis_vec.setdefault(current_node, {}).update(routing_table)
    dis_vec[current_node]=routing_table[current_node]      #updating our dis_vec to now not only neighbours but all hopes
    #print(dis_vec)
    printt()

def printt():
    with displayLock:
        os.system("cls")
        print("\n I am Router " + current_node + '\n')
        for node in dis_vec[current_node].keys():
            print(" Least cost path to router " + node + " : through " + neigh_through[node] + " with  cost " +  str("{0:.1f}".format(dis_vec[current_node][node]) + "\n"))

node1=Read(current_node,current_port,config)

threading.Thread(target=Sender).start()             #Creating thread using threading module
threading.Thread(target=Recv).start()
