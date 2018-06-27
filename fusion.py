import getDataFromApiSensors
import sendDataToApiOntology
import math
import datetime 
import pprint

import numpy as np
from scipy.spatial.distance import euclidean
from matplotlib.pyplot import *
from fastdtw import fastdtw
import itertools

from math import radians, cos, sin, asin, sqrt

import copy

def interpolate_polyline(polyline, num_points):
    duplicates = []
    for i in range(1, len(polyline)):
        if np.allclose(polyline[i], polyline[i-1]):
            duplicates.append(i)
    if duplicates:
        polyline = np.delete(polyline, duplicates, axis=0)
    tck, u = interp.splprep(polyline.T, s=0)
    u = np.linspace(0.0, 1.0, num_points)
    return np.column_stack(interp.splev(u, tck))

def haversine(latlon1, latlon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    lat1 = latlon1[0]
    lon1 = latlon1[1]
    
    lat2 = latlon2[0]
    lon2 = latlon2[1]
    
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    m = 6371 * c * 1000
    return m

def areTimeOverlapped(traj1, traj2) :
    if len(traj1) <= 0 or len(traj2) <= 0 :
        return False
    
    for i in traj1 :
        for j in traj2 :
            if i[0] > j[0] and i[0]-j[0] < datetime.timedelta(seconds=2) :
                return True
            
            if j[0] > i[0] and j[0]-i[0] < datetime.timedelta(seconds=2) :
                return True
    
    return False

def distance(a, b) :
    return math.hypot(b[0] - a[0], b[1] - a[1])

def trajectoryDistance(traj1, traj2) :
    
    for i in traj1 :
        
        minTime = datetime.timedelta(seconds=59) 
        indexTraj2 = -1
        
        for j in range(0, len(traj2)) :
              
            if i[0]>traj2[j][0] :
                if i[0]-traj2[j][0] < minTime :
                    minTime = i[0]-traj2[j][0]
                    indexTraj2 = j 
            else :
                if traj2[j][0]-i[0] < minTime :
                    minTime = traj2[j][0]-i[0]
                    indexTraj2 = j 
            

        #TODO sensor specfic selection
        if minTime < datetime.timedelta(seconds=2) :
            
            
            #TODO sum on all traj 
            print  distance(i[1], traj2[indexTraj2][1])


def main():
    
    #dataDict = {}
    
    #dataDict["ID1"] = {}
    #dataDict["ID1"]["sensor"] = "NoSensor1"
    #dataDict["ID1"]["trajectory"] = []
    
    #dataDict["ID1"]["trajectory"].append( [datetime.datetime(2012, 1, 1, 14, 0, 0, 0), [-1, 0] ])                
    #dataDict["ID1"]["trajectory"].append( [datetime.datetime(2012, 1, 1, 14, 0, 1, 0), [0, 0] ])
    #dataDict["ID1"]["trajectory"].append( [datetime.datetime(2012, 1, 1, 14, 0, 2, 0), [1, 0] ])
    #dataDict["ID1"]["trajectory"].append( [datetime.datetime(2012, 1, 1, 14, 0, 3, 0), [2, 0] ])
    
    #dataDict["ID2"] = {}
    #dataDict["ID2"]["sensor"] = "NoSensor2"
    #dataDict["ID2"]["trajectory"] = []
    
    #dataDict["ID2"]["trajectory"].append( [datetime.datetime(2012, 1, 1, 14, 0, 1, 100000), [0.5, 0] ])
    #dataDict["ID2"]["trajectory"].append( [datetime.datetime(2012, 1, 1, 14, 0, 2, 100000), [1.5, 0] ])
    #dataDict["ID2"]["trajectory"].append( [datetime.datetime(2012, 1, 1, 14, 0, 3, 100000), [2.5, 0] ])
    #dataDict["ID2"]["trajectory"].append( [datetime.datetime(2012, 1, 1, 14, 0, 4, 100000), [3.5, 0] ])
    
    #dataDict["ID3"] = {}
    #dataDict["ID3"]["sensor"] = "NoSensor3"
    #dataDict["ID3"]["trajectory"] = []
    
    #dataDict["ID3"]["trajectory"].append( [datetime.datetime(2012, 1, 1, 14, 0, 1, 200000), [0.75, 0] ])
    #dataDict["ID3"]["trajectory"].append( [datetime.datetime(2012, 1, 1, 14, 0, 2, 200000), [1.75, 0] ])
    #dataDict["ID3"]["trajectory"].append( [datetime.datetime(2012, 1, 1, 14, 0, 3, 200000), [2.75, 0] ])
    
    dataDict = getDataFromApiSensors.getData()
    
    fusionList = []
    
    for dk in dataDict.keys() :
        dataDict[dk+"LISSAGE"] = dataDict.pop(dk)

    for id1 in dataDict.keys() :
        for id2 in dataDict.keys() :
            if id1!=id2 and dataDict[id1]["trajectory"][0][0] <= dataDict[id2]["trajectory"][0][0] : 
                
                #print id1,id2,dataDict[id1]["trajectory"][0][0], dataDict[id1]["trajectory"][-1][0], dataDict[id2]["trajectory"][0][0],  dataDict[id2]["trajectory"][-1][0]
                
                #print dataDict[id1]["trajectory"]
                
                #if len(dataDict[id1]["trajectory"]) < 5 or len(dataDict[id2]["trajectory"]) < 5:
                #    continue
                
                #print "sensor", dataDict[id1]["sensor"], dataDict[id2]["sensor"]
                
                if dataDict[id1]["sensor"] == dataDict[id2]["sensor"] or \
                   ( "geolys" in dataDict[id1]["sensor"] and "geolys" in dataDict[id2]["sensor"] ) or \
                   dataDict[id1]["trajectory"][-1][0] < dataDict[id2]["trajectory"][0][0] or \
                   dataDict[id2]["trajectory"][-1][0] < dataDict[id1]["trajectory"][0][0] :
                    continue

                print id1, id2
                
                npTime1 = np.array( [k[0] for k in dataDict[id1]["trajectory"] ] )
                npTime2 = np.array( [k[0] for k in dataDict[id2]["trajectory"] ] )
                
                npCoord1 = np.array( [k[1] for k in dataDict[id1]["trajectory"] ] )
                npCoord2 = np.array( [k[1] for k in dataDict[id2]["trajectory"] ] )
                
                idx1 = 0
                idx2 = 0
                idy1 = len(dataDict[id1]["trajectory"])
                idy2 = len(dataDict[id2]["trajectory"])
                
                if npTime1[0] < npTime2[0] :
                    idx1 = (np.abs(npTime1-npTime2[0])).argmin()
                    npTime1 = npTime1[idx1:]
                    npCoord1 = npCoord1[idx1:]
                    
                else :
                    idx2 = (np.abs(npTime1[0]-npTime2)).argmin()
                    npTime2 = npTime2[idx2:]
                    npCoord2 = npCoord2[idx2:]
                
                if npTime1[-1] > npTime2[-1] :
                    idy1 = (np.abs(npTime1-npTime2[-1])).argmin()
                    npTime1 = npTime1[:idy1+1]
                    npCoord1 = npCoord1[:idy1+1]
                    
                else :
                    idy2 = (np.abs(npTime1[-1]-npTime2)).argmin()
                    npTime2 = npTime2[:idy2+1]
                    npCoord2 = npCoord2[:idy2+1]

                distance, path = fastdtw(npCoord1, npCoord2, dist=haversine)
                #distance, path = fastdtw(npCoord1, npCoord2, dist=euclidean)
                
                distance = distance/len(path)

                #print distance, path
                
                if len(path) >=0 and distance < 10 :
                    fusionList.append([distance,id1,id2])
    
    fusionList=sorted(fusionList)
    
    toBeFused = []
    
    for f in fusionList :
        print f[1], f[2], f[0]
        
        tbf1 = [tbf for tbf in tobeFused if f[1] in tbf]
        tbf2 = [tbf for tbf in tobeFused if f[2] in tbf]
        #TODO no cyclic confirmation (A->B, B->C so A->C)
        
        
        response = raw_input("Proceed with fusion? (y/n)")
        if response == "y" :
            toBeFused.append(f[1:3])
        
    #print toBeFused
    
    fusionCluster = []
    while len(toBeFused)>0:
        first, rest = toBeFused[0], toBeFused[1:]
        first = set(first)

        lf = -1
        while len(first)>lf:
            lf = len(first)

            rest2 = []
            for r in rest:
                if len(first.intersection(set(r)))>0:
                    first |= set(r)
                else:
                    rest2.append(r)     
            rest = rest2

        fusionCluster.append(list(first))
        toBeFused = rest
    
    print(fusionCluster)
    
    for fc in fusionCluster :
        for idTraj in fc[1:] :
            dataDict[fc[0]]["trajectory"] = sorted(dataDict[fc[0]]["trajectory"] + dataDict[idTraj]["trajectory"])
            #dataDict[fc[0]]["sensor"] = dataDict[fc[0]]["sensor"] + " " + dataDict[idTraj]["sensor"]
            dataDict.pop(idTraj)
    
    fusedTraj = {}
    
    for traj in dataDict :
        fusedTraj[traj] = {}
        fusedTraj[traj]["trajectory"]  = []
        fusedTraj[traj]["sensor"] = dataDict[traj]["sensor"]
        lastPoint = dataDict[traj]["trajectory"][0]
        for point in dataDict[traj]["trajectory"] :
            if point[0] - lastPoint[0] > datetime.timedelta(seconds=1):
                meanPoint = lastPoint
                for p in range(dataDict[traj]["trajectory"].index(lastPoint)+1, dataDict[traj]["trajectory"].index(point)+1) :
                    meanPoint[1][0] += (dataDict[traj]["trajectory"][p][1][0]- lastPoint[1][0])* (dataDict[traj]["trajectory"][p][0] - dataDict[traj]["trajectory"][p-1][0]).total_seconds()
                    meanPoint[1][1] += (dataDict[traj]["trajectory"][p][1][1]- lastPoint[1][1])* (dataDict[traj]["trajectory"][p][0] - dataDict[traj]["trajectory"][p-1][0]).total_seconds()
                meanPoint[0] = point[0] + (point[0]-lastPoint[0])/2 
                fusedTraj[traj]["trajectory"].append(meanPoint)
                lastPoint = point
        
    print(fusedTraj)
    
    response = raw_input("SEND TO API? (y/n)")
    
    if response == "y" :
        sendDataToApiOntology.sendData(dataDict)
    

if __name__ == "__main__":
    # Someone is launching this directly
    main()
