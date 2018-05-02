import sys
import math
import random
import time
from collections import namedtuple

INIT_TIME = time.time()
ID_WEIGHT = 0
ID_VOLUME = 1
ID_TRUCK = 2


packetListForDispatch = list()
packets = list()
box_count = int(input())
for i in range(box_count):
    weight, volume = [float(j) for j in input().split()]
    Box = namedtuple('Box', 'id, weight, volume')
    packetListForDispatch.append(Box(id=i, weight=weight, volume=volume)) 
    packets.append([weight, volume, -1])

packetListForDispatch.sort(key=lambda x: x.volume, reverse=True)

class Truck:
    MAX_VOLUME = 100
    
    def __init__(self, id, platform):
        self.id = id
        self.platform = platform
        self.idPackets = list()
        self.totalVolume = 0.0
        self.totalWeight = 0.0
        self.isFull = False
    
    def isFullWithPacket(self, id):
        return (self.totalVolume + self.platform.packets[id][ID_VOLUME]) > self.MAX_VOLUME
    
    def isFullWithSwapingPackets(self, idPacketLess, idPacketMore):
        return (self.totalVolume + self.platform.packets[idPacketMore][ID_VOLUME] - self.platform.packets[idPacketLess][ID_VOLUME]) > self.MAX_VOLUME
        
    def possibleWeightSwapingPackets(self, idPacketLess, idPacketMore):
        return self.totalWeight - self.platform.packets[idPacketLess][ID_WEIGHT] + self.platform.packets[idPacketMore][ID_WEIGHT]
        
    def possibleWeightWithPacketMore(self, idPacketMore):
        return self.totalWeight + self.platform.packets[idPacketMore][ID_WEIGHT]
        
    def possibleWeightWithPacketLess(self, idPacketLess):
        return self.totalWeight - self.platform.packets[idPacketLess][ID_WEIGHT]
        
    def addPacket(self, id):
        self.idPackets.append(id)
        self.platform.packets[id][ID_TRUCK] = self.id
        self.calculateTotalVolume()
        self.calculateTotalWeight()
        
    def removePacket(self, id):
        self.idPackets.remove(id)
        self.platform.packets[id][ID_TRUCK] = -1
        self.calculateTotalVolume()
        self.calculateTotalWeight()
    
    def calculateTotalVolume(self):
        self.totalVolume = 0.0
        for i in range(len(self.idPackets)):
            self.totalVolume+= self.platform.packets[self.idPackets[i]][ID_VOLUME]
    
    def calculateTotalWeight(self):
        self.totalWeight = 0.0
        for i in range(len(self.idPackets)):
            self.totalWeight+= self.platform.packets[self.idPackets[i]][ID_WEIGHT]

class Platform:
    MAX_TRUCKS = 100
    MAX_DELTA = 100
    MAX_TIME = 45
    MAX_REPETITION_BEFORE_NEXT_IMPROVEMENT = 3
    
    def __init__(self, packets, trucks = None):
        self.packets = packets[:]        
        if trucks == None:        
            self.trucks = list()
            for i in range(self.MAX_TRUCKS):
                self.trucks.append(Truck(i, self))
            k = 0
            for i in range(len(packetListForDispatch)):
                idPacket = packetListForDispatch[i].id
                isNotAffected = True            
                while(isNotAffected):
                    if not self.trucks[k].isFullWithPacket(idPacket):
                        self.trucks[k].addPacket(idPacket)
                        isNotAffected = False
                    if k == self.MAX_TRUCKS -1:
                        k = 0
                    else:
                        k = k +1
        else:
            for i in range(len(trucks)):
                truck = Truck(i, self)
                truck.calculateTotalVolume()
                truck.calculateTotalWeight()
                self.trucks.append(truck)
        
    def truckMaxWeight(self):
        idTruck = 0
        maxWeight = 0
        for i in range(self.MAX_TRUCKS):
            if self.trucks[i].totalWeight > maxWeight:
                idTruck = i
                maxWeight = self.trucks[i].totalWeight
            self.heaviestTruck =  self.trucks[idTruck]
            
    def truckMinWeight(self):
        idTruck = 0
        minWeight = 1000000000
        for i in range(self.MAX_TRUCKS):
            if self.trucks[i].totalWeight < minWeight:
                idTruck = i
                minWeight = self.trucks[i].totalWeight
            self.lightestTruck = self.trucks[idTruck]
            
    def calculateDelta(self):
         self.truckMaxWeight()
         self.truckMinWeight()
         return self.heaviestTruck.totalWeight - self.lightestTruck.totalWeight
    
    
    def localSearch(self, truckA, truckB):
        if truckA.id == truckB.id:
            return
        iOffset = 0
        for i in range(0, len(truckA.idPackets)):
            actualDelta = math.fabs(truckA.totalWeight - truckB.totalWeight)
            i = i + iOffset
            idPacketTruckA = truckA.idPackets[i]
            newDelta = math.fabs(truckA.possibleWeightWithPacketLess(idPacketTruckA) - truckB.possibleWeightWithPacketMore(idPacketTruckA))
            if actualDelta > newDelta and not truckB.isFullWithPacket(idPacketTruckA):
                truckA.removePacket(idPacketTruckA)
                truckB.addPacket(idPacketTruckA)
                iOffset = iOffset-1
        
        loop=0
        improvement = True
        while improvement:
            improvement = False
            for i in range(0, len(truckA.idPackets)):
                for j in range(0, len(truckB.idPackets)):
                    actualDelta = math.fabs(truckA.totalWeight - truckB.totalWeight) 
                    idPacketTruckA = truckA.idPackets[i]
                    idPacketTruckB = truckB.idPackets[j]
                    
                    #Test swapping  
                    newDelta = math.fabs(truckA.possibleWeightSwapingPackets(idPacketTruckA, idPacketTruckB) - truckB.possibleWeightSwapingPackets(idPacketTruckB,idPacketTruckA))
                    if actualDelta > newDelta and not truckA.isFullWithSwapingPackets(idPacketTruckA, idPacketTruckB) and not truckB.isFullWithSwapingPackets(idPacketTruckB,idPacketTruckA):
                        truckA.removePacket(idPacketTruckA)
                        truckB.removePacket(idPacketTruckB)
                        truckA.addPacket(idPacketTruckB)
                        truckB.addPacket(idPacketTruckA)
                        improvement = True
                        continue         
                    loop+=1
                    if(loop>len(truckA.idPackets)*len(truckB.idPackets)):
                        return
        return
    
    def simulatedAnnealing(self):
        T = 0.9
        while(T>0.05):
            truckA = self.trucks[random.randint(0,self.MAX_TRUCKS-1)]
            truckB = self.trucks[random.randint(0,self.MAX_TRUCKS-1)]
            idPacketTruckA = truckA.idPackets[random.randint(0,len(truckA.idPackets) -1)]
            idPacketTruckB = truckB.idPackets[random.randint(0,len(truckB.idPackets) -1)]
            actualDelta = math.fabs(truckA.totalWeight - truckB.totalWeight) 
            newDelta = math.fabs(truckA.possibleWeightSwapingPackets(idPacketTruckA, idPacketTruckB) - truckB.possibleWeightSwapingPackets(idPacketTruckB,idPacketTruckA))

            if (actualDelta > newDelta or random.random() < math.exp(-abs(actualDelta - newDelta)/T)) and not truckA.isFullWithSwapingPackets(idPacketTruckA, idPacketTruckB) and not truckB.isFullWithSwapingPackets(idPacketTruckB,idPacketTruckA):
                truckA.removePacket(idPacketTruckA)
                truckB.removePacket(idPacketTruckB)
                truckA.addPacket(idPacketTruckB)
                truckB.addPacket(idPacketTruckA)
        
        
        loop=0
        improvement = True
        while improvement:
            improvement = False
            for i in range(0, len(truckA.idPackets)):
                for j in range(0, len(truckB.idPackets)):
                    actualDelta = math.fabs(truckA.totalWeight - truckB.totalWeight) 
                    idPacketTruckA = truckA.idPackets[i]
                    idPacketTruckB = truckB.idPackets[j]
                    
                    #Test swapping  
                    newDelta = math.fabs(truckA.possibleWeightSwapingPackets(idPacketTruckA, idPacketTruckB) - truckB.possibleWeightSwapingPackets(idPacketTruckB,idPacketTruckA))
                    if actualDelta > newDelta and not truckA.isFullWithSwapingPackets(idPacketTruckA, idPacketTruckB) and not truckB.isFullWithSwapingPackets(idPacketTruckB,idPacketTruckA):
                        truckA.removePacket(idPacketTruckA)
                        truckB.removePacket(idPacketTruckB)
                        truckA.addPacket(idPacketTruckB)
                        truckB.addPacket(idPacketTruckA)
                        improvement = True
                        continue         
                    loop+=1
                    if(loop>len(truckA.idPackets)*len(truckB.idPackets)):
                        return
        return
        
    def findSolution(self):
        nbIteration = 1
        while(True):
            nbIteration+=1
            now = time.time()
            if now - INIT_TIME > self.MAX_TIME:
                return
            
            self.calculateDelta()
            if nbIteration % 200 == 0 and now - INIT_TIME < 25:
                truckA = self.trucks[random.randint(0,self.MAX_TRUCKS-1)]
                truckB = self.trucks[random.randint(0,self.MAX_TRUCKS-1)]
                idPacketTruckA = truckA.idPackets[random.randint(0,len(truckA.idPackets) -1)]
                idPacketTruckB = truckB.idPackets[random.randint(0,len(truckB.idPackets) -1)]
                if truckA.isFullWithSwapingPackets(idPacketTruckA, idPacketTruckB) and not truckB.isFullWithSwapingPackets(idPacketTruckB,idPacketTruckA):
                    truckA.removePacket(idPacketTruckA)
                    truckB.removePacket(idPacketTruckB)
                    truckA.addPacket(idPacketTruckB)
                    truckB.addPacket(idPacketTruckA)
            repet = 0    
            while(repet < self.MAX_REPETITION_BEFORE_NEXT_IMPROVEMENT):
                self.localSearch(self.trucks[random.randint(0,self.MAX_TRUCKS-1)], self.trucks[random.randint(0,self.MAX_TRUCKS-1)])
                self.localSearch(self.heaviestTruck, self.trucks[random.randint(0,self.MAX_TRUCKS-1)])
                self.localSearch(self.lightestTruck, self.trucks[random.randint(0,self.MAX_TRUCKS-1)])
                repet = repet +1
    
    def stringResult(self):
        result = ""
        for i in range(box_count):
            result +=str(self.packets[i][ID_TRUCK])+" "
        return result

results = list()
random.seed(20)
plateform = Platform(packets)
plateform.findSolution()
print(plateform.stringResult())

    
# Write an action using print
# To debug: print("Debug messages...", file=sys.stderr)