import random
import numpy as np
import pickle
import time
import threading

from multiprocessing import Process, Pipe
from WorldConst import *

class Empty:
    pass        

######################## Settings #############################

gMaxAge = 100
gDiscoveryRate = 30     # rate of discoveries those adds extar energy and grow experience, percents
gMaxIQres = 2           # maximum possible extra resources with 100% IQ
gAttSz = 10             # look for partner and/or free spae or energy source in this range
gAttChildSz = 2         # children look up for adults in this range
gChildAge = 10          # before this age children require extra energy from parents and cannot create own ones
                        #   effective child age is increased by iq, up to 4 points
gBirthEnergy = 4
gFailedBirthEnergy = 0
gMaxNeibghors = 6       # don't create children when number of neibghors reaches this limit and look for free space if possible
gAllowLocalRes = False  # allow getting resources from own location, not only from free ones around
gIQ0 = True             # initialize with all zeros (except of Share)
gMutationRate = 1       # frequency of mutations, percents
gMutationFactor = 3     # for gMutationTypeV 0 use 1/N of distance between min/max values and end of range, 0 and 100 respectively 
                        #   as result range edges
                        # for gMutationTypeV 1 use 1/N of distance between min/max values as result range edges, overriden by gMutationMinStep
gMutationMinStep = 30   # not less than N points around parents min/max, for gMutationTypeV 1 and 2
gMutationTypeV = 2      # 2=natural
gMaxDamage = 1          # max possible amount of energy which can be aggressively taken from other person
gMaxGroundRes   = 2     # how many resources try to fetch from free area by default
gResRespawn     = 2     # max ground resource respawn

gParallel = 2

##################### End of Settings ##########################

gMatrix = None
gDepth = L.layers
gW = 0
gH = 0

gEpoch=0
gPersons=0
gPersonsTotal=0

bStop = False
gWorldLock = threading.Lock()

gInitOptions = Empty()
gInitOptions.N = 2500

nLockCounter = 0

def WLock():
    global gWorldLock, nLockCounter
    nLockCounter += 1
    return gWorldLock.acquire(False)
#end WLock()

def WLockWait():
    global gWorldLock, nLockCounter
    nLockCounter += 1
    return gWorldLock.acquire(True)
#end WLockWait()

def WRelease():
    global gWorldLock, nLockCounter
    nLockCounter -= 1
    gWorldLock.release()
#end WRelease()

def CrossGenes(xm, ym, xf, yf, layer):
    global gMatrix
    global gMutationRate, gMutationFactor, gMutationMinStep, gMutationTypeV

    a = gMatrix.item((xm, ym, layer))
    b = gMatrix.item((xf, yf, layer))

    if(gMutationTypeV == T.mutNat):
        v0 = min(a, b)
        v1 = max(a, b)
        m = random.randint(0,99)
        if(m > gMutationRate):
            d = 0
        else:
            d = gMutationMinStep
        r = random.randint(max(0, v0-d),min(v1+d, 100))
        return r

    r = random.randint(0,1)
    if(r == T.male):
        r = a
    else:
        r = b

    m = random.randint(0,99)
    if(m < gMutationRate):
        v0 = min(a, b)
        v1 = max(a, b)
        if(gMutationTypeV == T.mutInt):
            d = (int)(max((v1-v0)/gMutationFactor, gMutationMinStep))
            r = random.randint(v0-d, v1+d)
        else:
            r = random.randint(int(v0-v0/gMutationFactor-1), int(v1+(100-v1)/gMutationFactor+1))
        r = max(0, r)
        r = min(r, 100)

    '''
    v0 = min(a, b)
    v1 = max(a, b)
    r = random.randint(v0-1,v1+1)
    r = max(0, r)
    r = min(r, 100)
    '''
    return int(r)
#end CrossGenes()

def actualChildAge(iq):
    global gChildAge
    return gChildAge + iq/25
#end actualChildAge()

def makeColor(x,y):
    global gH, gW
    return int(y/gH * 16)*16 + int(x/gW * 16)
#end makeColor()

def CreatePerson(x, y):
    global gMatrix, gPersons, gPersonsTotal, gH, gW
    global gInitOptions
    #global gIQ0
    gMatrix[x, y, L.ctype ] = T.person
    gMatrix[x, y, L.energy] = random.randint(30,100)
    gMatrix[x, y, L.age   ] = 16
    gMatrix[x, y, L.sex   ] = random.randint(0,1)
    gMatrix[x, y, L.exp   ] = 0

    '''
    if(gIQ0):
        gMatrix[x, y, L.share     ] = random.randint(0,100)
        gMatrix[x, y, L.aggressive] = 0
        gMatrix[x, y, L.iq        ] = 0
        gMatrix[x, y, L.defence   ] = 0
        gMatrix[x, y, L.mobility  ] = 0
    else:
        gMatrix[x, y, L.share     ] = random.randint(0,100)
        gMatrix[x, y, L.aggressive] = random.randint(0,100)
        gMatrix[x, y, L.iq        ] = random.randint(0,100)
        gMatrix[x, y, L.defence   ] = random.randint(0,100)
        gMatrix[x, y, L.mobility  ] = random.randint(0,100)
    gMatrix[x, y, L.fert      ] = random.randint(0,100)
    '''
    for i in range(L.genes, L.pseudo_genes):
        name = LayerName[i]
        try:
            desc = getattr(gInitOptions, name)
            a, b = desc
        except:
            a = 0
            b = 100
        #end try
        gMatrix[x, y, i  ] = random.randint(a,b)
    #end for()

    # marker pseudo-gene
    color = makeColor(x,y)
    gMatrix[x, y, L.color] = color
    gMatrix[x, y, L.myth]  = color

    gPersons += 1
    gPersonsTotal += 1
#end CreatePerson()

def CreateChild(x, y, xm, ym, xf, yf):
    global gMatrix, gBirthEnergy, gFailedBirthEnergy, gPersons, gPersonsTotal

    gMatrix[x, y, L.ctype ] = T.person
    #gMatrix[x, y, L.energy] = random.randint(10,20)
    #gMatrix[x, y, L.energy] = random.randint(1,gBirthEnergy)
    gMatrix[x, y, L.age   ] = 0
    gMatrix[x, y, L.sex   ] = random.randint(0,1)

    de = gMatrix.item((xf, yf, L.energy))
    if(de > gBirthEnergy):
        de = gBirthEnergy

    #gMatrix[x, y, L.energy] = random.randint(1,de)
    gMatrix[x, y, L.energy] = de
    gMatrix[xf, yf, L.energy] -= de

    SHARE = random.randint(0,100)
    if(SHARE < gMatrix.item((xm, ym, L.share))):
        de = gBirthEnergy
        em = gMatrix.item((xm, ym, L.energy))
        if(em < de):
            de = em/2

        de = int(de)
        gMatrix[xm, ym, L.energy] -= de
        gMatrix[xf, yf, L.energy] += de
    #end if(SHARE...)    

    for layer in range(L.genes, L.pseudo_genes):
        gMatrix[x, y, layer     ] = CrossGenes(xm, ym, xf, yf, layer)
    gMatrix[x, y, L.color] = int(( gMatrix.item((xm, ym, L.color)) + gMatrix.item((xf, yf, L.color)) ) / 2)
    gMatrix[x, y, L.myth]  = gMatrix.item((xf, yf, L.myth))

    exp = (0 + gMatrix.item((xf, yf, L.exp)) + gMatrix.item((xm, ym, L.exp))) * gMatrix.item((x, y, L.iq)) / 200
    if(exp > 100):
        print("high exp")
        exp = 100
    gMatrix[x, y, L.exp   ] = int(exp)

    gPersons += 1
    gPersonsTotal += 1
    #print("Birth sex/total", gMatrix[x,y, L.sex], gPersons)
#end CreateChild()

def CreateMatrix(w, h, p):
    global gMatrix, gW, gH, gDepth
    gMatrix = np.zeros((w, h, gDepth), dtype=np.uint8)
    gW = w
    gH = h
    for i in range(p):
        x = random.randint(0,gW-1)
        y = random.randint(0,gH-1)
        CreatePerson(x, y)
    #end for()
#end CreateMatrix()

def HandleResources(x, y):
    global gMatrix, gW, gH, gMaxAge, gPersons, gResRespawn
    if(gMatrix.item((x,y, L.ctype)) == T.ground):
        if(gMatrix.item((x,y, L.resources)) < 150):
            gMatrix[x,y, L.resources] += random.randint(0,gResRespawn)
    else:
        #print("@"+str(x)+"x"+str(y))
        # die if no energy
        if(gMatrix.item((x,y, L.age)) >= gMaxAge or \
           gMatrix.item((x,y, L.energy)) < 1):
            gMatrix[x,y, L.ctype] = T.ground
            gMatrix[x,y, L.resources] = gMatrix.item((x,y, L.energy))
            gPersons -= 1
            #print("Die sex/age/energy/iq total", gMatrix[x,y, L.sex], gMatrix[x,y, L.age], gMatrix[x,y, L.energy], gMatrix[x,y, L.iq], gPersons)
            return

        gMatrix[x,y, L.age] += 1
        gMatrix[x,y, L.energy] -= 1
    #end if()

#end HandleResources()

def FetchResources(x, y):
    global gMatrix, gW, gH, gDiscoveryRate, gMaxIQres, gAllowLocalRes, gMaxDamage, gMaxGroundRes, gBirthEnergy

    if(gMatrix.item((x,y, L.ctype)) == T.ground):
        return
    energy = gMatrix.item((x,y, L.energy))
    if(energy > 250):
        return

    age      = gMatrix.item((x,y, L.age))
    iq       = gMatrix.item((x,y, L.iq))
    exp      = gMatrix.item((x,y, L.exp))
    mobility = gMatrix.item((x,y, L.mobility))

    r = random.randint(0,100)
    if(gDiscoveryRate > r):
        IQ = random.randint(0,100)
        if(iq > IQ):
            gMatrix[x,y, L.energy] += 1
        if(exp < 100):
            gMatrix[x,y, L.exp] += 1
    #end if()

    if(gAllowLocalRes):
        # unconditionally get local resorces if any
        if(gMatrix.item((x,y, L.resources)) > 0):
            gMatrix[x,y, L.energy] += 1
            gMatrix[x,y, L.resources] -= 1
    #end if(gAllowLocalRes)

    X=x
    Y=y


    n=6
    bIsChild = age < actualChildAge(iq)

    while(X==x and Y==y and n>0):
        d = 2+int(mobility*2/100)
        ox = random.randint(0,d)
        oy = random.randint(0,d)

        D = int(d/2)
        X = x+ox-D
        Y = y+oy-D

        if(X<0 or X>=gW or Y<0 or Y>=gW):
            n -= 1
            continue

        if(bIsChild):
            #if(gMatrix.item((X,Y, L.ctype)) == T.ground or gMatrix.item((X,Y, L.age)) < actualChildAge(gMatrix.item((X,Y, L.iq)))):
            if(gMatrix.item((X,Y, L.ctype)) == T.person and gMatrix.item((X,Y, L.age)) < actualChildAge(gMatrix.item((X,Y, L.iq)))):
                # children looks for adult, and give extra chance
                X=x
                Y=y
                n += 1
            else:
                break
        else:
            if(gMatrix.item((X,Y, L.ctype)) == T.person and gMatrix.item((X,Y, L.age)) < actualChildAge(gMatrix.item((X,Y, L.iq)))):
                # don't touch children
                X=x
                Y=y
        #end if(bIsChild)
        n -= 2

    #end while()
    '''

    d = 2+int(mobility*2/100)
    ox = random.randint(0,d)
    oy = random.randint(0,d)

    D = int(d/2)
    X = x+ox-D
    Y = y+oy-D
    '''

    if(X==x and Y==y):
        return
#    if(X<0 or X>=gW or Y<0 or Y>=gH):
#        return

    if(X>=0 and X<gW and Y>=0 and Y<gH):
        if(gMatrix.item((X,Y, L.ctype)) == T.ground):

            '''
            IQ = random.randint(0,100)
            if(iq+exp < IQ):
                return
            '''
            #dr = int((iq+exp)*gMaxIQres/100+1)
            dr0 = gMaxGroundRes
            if(energy < gBirthEnergy and not bIsChild):
                dr0 += int(gBirthEnergy/2)

            dr = 0
            if(iq+exp > 0):
                DR = random.randint(0, 200)
                if(DR < iq+exp):
                    dr = random.randint(1, gMaxIQres)

            dr = min(gMatrix.item((X,Y, L.resources)), dr+dr0)

            if(gMatrix.item((X,Y, L.resources)) >= dr0):
                gMatrix[X,Y, L.resources] -= dr0
                gMatrix[x,y, L.energy] += dr
                if(gMatrix.item((x,y, L.energy)) > 250-gMaxIQres):
                    gMatrix[x,y, L.energy] = 250-gMaxIQres
        else:
            if(bIsChild):
                de = min(2, gMatrix.item((X,Y, L.energy)))
                gMatrix[X,Y, L.energy] -= de
                gMatrix[x,y, L.energy] += de
            else:
                SHARE = random.randint(0,100)
                if(gMatrix.item((X,Y, L.share)) > SHARE):
                    de = min(1, gMatrix.item((X,Y, L.energy)))
                    gMatrix[X,Y, L.energy] -= de
                    gMatrix[x,y, L.energy] += de
#                return

            AGGR = random.randint(0,100)
            if(gMatrix.item((x,y, L.aggressive)) * (1 + iq/10) <= AGGR):
                return

            DEFENCE = random.randint(0,100)
            if(gMatrix.item((X,Y, L.defence)) * (1 + iq/10)  <= DEFENCE):
                if(gMaxDamage > 1):
                    de = random.randint(1,gMaxDamage)
                else:
                    de = 1
                de = min(de, gMatrix.item((X,Y, L.energy)))
                gMatrix[X,Y, L.energy] -= de
                gMatrix[x,y, L.energy] += de
                return
        #end if(L.ctype)

    #end if() in ranges

#end FetchResources()

def AdjustRanges(x, y, sz):
    global gW, gH

    if(x >= sz):
        x0 = x-sz
    else:
        x0 = 0

    if(y >= sz):
        y0 = y-sz
    else:
        y0 = 0

    if(x < gW-sz):
        x1 = x+sz+1
    else:
        x1 = gW

    if(y < gH-sz):
        y1 = y+sz+1
    else:
        y1 = gH

    return x0, x1, y0, y1
#end AdjustRanges()

def CountNeibghors(x, y):
    global gMatrix, gW, gH

    sz = 1
    N = 0

    x0, x1, y0, y1 = AdjustRanges(x, y, sz)

    for xi in range(x0, x1):
        for yi in range(y0, y1):
            if(xi==x and yi==y):
                continue
            if(gMatrix.item((xi,yi, L.ctype)) == T.person):
                N += 1
    #end for(x, y)

    return N

#end CountNeibghors()

def CountAttractionPoint(x, y):
    global gMatrix, gW, gH, gAttSz, gAttChildSz, gMaxNeibghors

    if(gMatrix.item((x,y, L.ctype)) == T.ground):
        return
    if(gMatrix.item((x,y, L.energy)) < 2):
        return

    bFindRes = False    

    MOB = random.randint(0,100)
    N = CountNeibghors(x, y)
    if(N == 8):
        return  # no chance

    if(gMatrix.item((x,y, L.mobility)) > MOB):
        # high mobility, look for resources
        if(N < gMaxNeibghors):
            # few neighbors, stay here
            return
        bFindRes = True
    else:
        # look for partner
        if(N >= gMaxNeibghors):
            # too many neighbors, look for free resources
            bFindRes = True

    sex = gMatrix.item((x,y, L.sex))
    age = gMatrix.item((x,y, L.age))
    iq  = gMatrix.item((x,y, L.iq))
    if(age < actualChildAge(iq)):
        sz = gAttChildSz
    else:
        sz = gAttSz


    x0, x1, y0, y1 = AdjustRanges(x, y, sz)

    AttXsum = 0
    AttYsum = 0
    AttN = 0

    ResXsum = 0
    ResYsum = 0
    ResN = 0

    for xi in range(x0, x1):
        for yi in range(y0, y1):
            if(gMatrix.item((xi,yi, L.ctype)) == T.ground):
                ResXsum += xi
                ResYsum += yi
                ResN += 1
                continue
            if(xi == x and yi == y):
                continue
            if(age >= actualChildAge(iq)):
                if(gMatrix.item((xi,yi, L.sex)) == sex):
                    continue
            AttXsum += xi
            AttYsum += yi
            AttN += 1

    dx = 0
    dy = 0

    if(bFindRes):
        AttXsum = ResXsum
        AttYsum = ResYsum
        AttN    = ResN

    if(AttN == 0):
        dx = random.randint(-2,2)
        dy = random.randint(-2,2)
    else:
        dx = AttXsum/AttN - x
        dy = AttYsum/AttN - y
        if(dx > 0):
            dx = 1
        if(dx < 0):
            dx = -1
        if(dy > 0):
            dy = 1
        if(dy < 0):
            dy = -1
        dx *= random.randint(1,3)    
        dy *= random.randint(1,3)    

    xi = int(x+dx)
    yi = int(y+dy)
    if(xi == x and yi == y):
        return

    if(xi<0 or yi<0 or xi>=gW or yi>=gH):
        return
    
    if(gMatrix.item((xi,yi, L.ctype)) == T.person):
        return
    savedRes = gMatrix.item((xi,yi, L.resources))

    gMatrix[xi,yi] = gMatrix[x,y]
    gMatrix[x,y, L.ctype] = T.ground
    gMatrix[xi,yi, L.resources] = savedRes
    gMatrix[xi,yi, L.energy] -= 1
#end CountAttractionPoint()

def MakeChildren(x, y):
    global gMatrix, gW, gH, gAttSz, gAttChildSz, gBirthEnergy, gFailedBirthEnergy

    if(gMatrix[x,y, L.ctype] == T.ground):
        return
    if(gMatrix[x,y, L.energy] < gBirthEnergy*2):
        return
    if(gMatrix[x,y, L.sex] == T.male):
        return
    if(gMatrix.item((x,y, L.age)) < actualChildAge(gMatrix.item((x,y, L.iq)))):
        return

    sz = 1

    x0, x1, y0, y1 = AdjustRanges(x, y, sz)

    X = -1
    Y = -1
    xt = -1
    yt = -1

    partners = []
    places = []

    xi = x0
    yi = y0

    for xi in range(x0, x1):
        for yi in range(y0, y1):
            #if(xt == -1):
            if(gMatrix.item((xi,yi, L.ctype)) == T.ground):
                xt = xi
                yt = yi
                places.append([xt,yt])
                continue

            if(xi == x and yi == y):
                continue
            if(gMatrix[xi,yi, L.sex] == T.female):
                continue
            if(gMatrix[xi,yi, L.age] < gAttChildSz + gMatrix.item((xi,yi, L.iq))/25):
                continue

            fert = gMatrix.item((x, y, L.fert)) * gMatrix.item((xi, yi, L.fert))
            if( fert < random.randint(1,100*100)):
                continue

#            if(X == -1):
            X = xi
            Y = yi
            partners.append([X, Y])
                #if(not xt == -1):
                #    break

        #end for yi
    #end for xi

    if(X == -1):  # no partner
        return

    if(xt == -1): # failed birth, not free place
        gMatrix[x,y, L.energy] -= gFailedBirthEnergy
        return

    n = len(partners)
    m = len(places)

    if(n>1):
        n = random.randint(0, n-1)
    else:
        n = 0

    if(m>1):
        m = random.randint(0, m-1)
    else:
        m = 0

    X, Y = partners[n]
    xt, yt = places[m]

    # target, male, female
    CreateChild(xt, yt, X, Y, x, y)
#end MakeChildren()

def DoStage(StageF, x0, x1):
    global gMatrix, gW, gH, gEpoch
    global bStop

    x = x0
    while(x<x1):
        y = 0
        while(y<gH):
            if(bStop):
                return
            StageF(x, y)
            y+=1
        #end while(y)
        x+=1
    #end while(x)

    ''' It was bad idea
    if(gEpoch & 0x1):
        _x0 = x0
        _x1 = x1
        _dx = 1
    else:
        _x0 = x1-1
        _x1 = x0-1
        _dx = -1

    if(gEpoch & 0x2):
        _y0 = 0
        _y1 = gH
        _dy = 1
    else:
        _y0 = gH-1
        _y1 = -1
        _dy = -1

    x = _x0
    y = _y0
    try:
        x = _x0
        while(not (x==_x1)):
            y = _y0
            while(not (y==_y1)):
                if(bStop):
                    return
                StageF(x, y)
                y+=_dy
            #end while(y)
            x+=_dx
        #end while(x)
    except Exception as e:
        print('DoStage ERR: '+ str(e) + " @"+str(x)+"x"+str(y))
        #print(str(x)+","+str(y))
        time.sleep(60)
    '''

#end DoStage()

def _Next(x0, x1):
    global gMatrix, gW, gH, gEpoch
    global bStop

    print(str(gEpoch))
    gEpoch += 1
    if(gEpoch == 1):
        return

    #print(str(bStop))

    try:
        DoStage(HandleResources,      x0, x1)
        DoStage(FetchResources,       x0, x1)
        DoStage(CountAttractionPoint, x0, x1)
        DoStage(MakeChildren,         x0, x1)

    except Exception as e:
        print('_Next ERR: '+ str(e))
        #print(str(x)+","+str(y))
        time.sleep(60)

    pass
    return    
#end _Next()

gStarted = False

def f1(conn):
    global gMatrix, gW, gH, gEpoch, gPersons, gPersonsTotal
    global parent_conn
    try:
        parent_conn = conn
        '''
        gMatrix, gW, gH, gEpoch, gPersons, gPersonsTotal = conn.recv()
        #s = conn.recv()
        #print('got s')
        #o = pickle.loads(s)
        #print('unpacked s')
        '''
        o = conn.recv()
        conn.send("Done")
        print('Try unpack world')
        bRet = UnpackWorld(o)
        print(str(gW)+'x'+ str(gH))
        if(not bRet):
            print('Cant unpack world')
            return

        while(True):
            #print(str(gEpoch))
            #if(conn.poll()):
            #    print('Exit request')
            #    break

            #print("read task")

            _Next(0, gW)
            #conn.send([gMatrix, gEpoch, gPersons, gPersonsTotal])
            #o = PackWorld()
            #conn.send(o)
            conn.send(gMatrix)

            print("update worker")

        #end while()

    except Exception as e:
        print('f ERR: '+ str(e))
        time.sleep(60)
    pass
    return    
#end f()

def f(conn):
    global gMatrix, gW, gH, gEpoch, gPersons, gPersonsTotal
    global parent_conn
    try:
        parent_conn = conn
        '''
        gMatrix, gW, gH, gEpoch, gPersons, gPersonsTotal = conn.recv()
        #s = conn.recv()
        #print('got s')
        #o = pickle.loads(s)
        #print('unpacked s')
        '''
        o = conn.recv()
        conn.send("Done")
        print('Try unpack world')
        bRet = UnpackWorld(o)
        print(str(gW)+'x'+ str(gH))
        if(not bRet):
            print('Cant unpack world')
            return


        while(True):
            #print(str(gEpoch))
            #if(conn.poll()):
            #    print('Exit request')
            #    break

            #print("read task")
            gPart, th = conn.recv()
            
            d = int(gW/4)

            x0 = int((gPart + th*2)*d)
            x1 = x0+d

            x0s = max(x0-gAttSz, 0)
            x1s = min(x1+gAttSz, gW)
            print(str(th)+':'+ str(x0)+'-'+ str(x1))

            _Next(x0, x1)
            #conn.send([gMatrix, gEpoch, gPersons, gPersonsTotal])
            #o = PackWorld()
            #conn.send(o)
            conn.send([gMatrix[x0s:x1s], x0s, x1s])

            print("update worker "+str(th))
            Matrixs, x0s, x1s = conn.recv()
            gMatrix[x0s:x1s] = Matrixs

        #end while()

    except Exception as e:
        print('f ERR: '+ str(e))
        time.sleep(60)
    pass
    return    
#end f()

gPart = 0

def NextTask():
    global gEpoch, gPart
    global parent_conn1, child_conn1
    global parent_conn2, child_conn2

    print("send tasks")
    child_conn1.send([gPart, 0])
    child_conn2.send([gPart, 1])

    gPart = int(gPart) ^ int(1)
    if(gPart == 0):
        gEpoch += 1

#end NextTask()

def NextLocked():
    global gMatrix, gW, gH, gEpoch, gPersons, gPersonsTotal, gPart
    global parent_conn1, child_conn1
    global parent_conn2, child_conn2
    global p1, p2, gStarted
    global gParallel

    if(gParallel == 0):
        _Next(0, gW)
        return

    bInit = not gStarted

    if(bInit):
        gPart = 0

        if(gParallel == 1):
            parent_conn1, child_conn1 = Pipe()
            p1 = Process(target=f1, args=(parent_conn1,))
            p1.start()
            o = PackWorld()
            child_conn1.send(o)
        else:
            parent_conn1, child_conn1 = Pipe()
            parent_conn2, child_conn2 = Pipe()
            p1 = Process(target=f, args=(parent_conn1,))
            p1.start()
            p2 = Process(target=f, args=(parent_conn2,))
            p2.start()
            '''
            child_conn.send([gMatrix, gW, gH, gEpoch, gPersons, gPersonsTotal])
            '''
            o = PackWorld()
            #s = pickle.dumps(o)
            child_conn1.send(o)
            child_conn2.send(o)

            child_conn1.recv()
            child_conn2.recv()

            NextTask()
        
        gStarted = True
    #end if(not gStarted)

    if(gParallel == 1):
        if(not p1.is_alive()):
            return False

        o = child_conn1.recv()
        bRet = UnpackWorld(o)
        return True

    if(not p1.is_alive() or not p2.is_alive()):
        return False

    if(not bInit):
        if(not child_conn1.poll() or not child_conn2.poll()):
            return False

    #gMatrix, gEpoch, gPersons, gPersonsTotal = child_conn.recv()
    #o = child_conn.recv()
    #bRet = UnpackWorld(o)

    print("read workers")
    Matrixs1, x0s1, x1s1 = child_conn1.recv()
    gMatrix[x0s1:x1s1] = Matrixs1

    Matrixs2, x0s2, x1s2 = child_conn2.recv()
    gMatrix[x0s2:x1s2] = Matrixs2

    print("sync workers")
    child_conn1.send([Matrixs2, x0s2, x1s2])
    child_conn2.send([Matrixs1, x0s1, x1s1])

    NextTask()

    return True

#end NextLocked()

def Next():
    if(not WLock()):
        return False
    bRet = False
    try:
        bRet = NextLocked()
    except Exception as e:
        print('Next ERR: '+ str(e))
    pass
    WRelease()
    return bRet
#end Next():

def Stop():
    global parent_conn1, child_conn1
    global parent_conn2, child_conn2
    global p, p2, gStarted

    if(gStarted):
        if(p1.is_alive()):
            #child_conn.send("Stop")
            #p.join()
            p1.terminate()
            #p.close()
            parent_conn1.close()
            child_conn1.close()

        if(p2.is_alive()):
            p2.terminate()
            parent_conn2.close()
            child_conn2.close()

        gStarted = False
    #end if(gStarted)

#end Stop()

def PackWorld():
    global gMatrix       
    global gMaxAge       
    global gDiscoveryRate
    global gMaxIQres     
    global gAttSz        
    global gAttChildSz   
    global gChildAge     
    global gBirthEnergy  
    global gFailedBirthEnergy
    global gMaxNeibghors 
    global gEpoch        
    global gPersons      
    global gPersonsTotal 
    global gAllowLocalRes
    global gMutationRate   
    global gMutationFactor 
    global gMutationMinStep
    global gMutationTypeV  
    global gMaxDamage
    global gMaxGroundRes
    global gResRespawn
    
    #print("matrix=>"+str(gMatrix))

    o = Empty()

    o.version = 1
    o.L = L()
    o.Tunable = GetTunableNames()
    #o.gMatrix         = np.copy(gMatrix)
    o.gMatrix         = gMatrix
    o.gMaxAge         = gMaxAge
    o.gDiscoveryRate  = gDiscoveryRate
    o.gMaxIQres       = gMaxIQres     
    o.gAttSz          = gAttSz        
    o.gAttChildSz     = gAttChildSz   
    o.gChildAge       = gChildAge     
    o.gBirthEnergy    = gBirthEnergy  
    o.gFailedBirthEnergy= gFailedBirthEnergy
    o.gMaxNeibghors   = gMaxNeibghors 
    o.gEpoch          = gEpoch        
    o.gPersons        = gPersons
    o.gPersonsTotal   = gPersonsTotal 
    o.gAllowLocalRes  = gAllowLocalRes
    o.gMutationRate   = gMutationRate   
    o.gMutationFactor = gMutationFactor 
    o.gMutationMinStep= gMutationMinStep
    o.gMutationTypeV  = gMutationTypeV
    o.gMaxDamage      = gMaxDamage
    o.gMaxGroundRes   = gMaxGroundRes
    o.gResRespawn     = gResRespawn

    '''
    for key, value in o.__dict__.items():
        if not callable(value) and not key.startswith('__'):
            print(str(key)+"=>"+str(value))
    '''
    return o
#end PackWorld()

def UnpackWorld(o):

    global gMatrix       
    global gMaxAge       
    global gDiscoveryRate
    global gMaxIQres     
    global gAttSz        
    global gAttChildSz   
    global gChildAge     
    global gBirthEnergy  
    global gFailedBirthEnergy
    global gMaxNeibghors 
    global gEpoch        
    global gPersons      
    global gPersonsTotal 
    global gAllowLocalRes
    global gMutationRate   
    global gMutationFactor 
    global gMutationMinStep
    global gMutationTypeV  
    global gMaxDamage
    global gMaxGroundRes
    global gResRespawn

    global gH,gW,layers, gDepth

    H,W,layers    = o.gMatrix.shape
    if(layers > gDepth):
        print('layers > gDepth')
        gWorldLock.release()
        return False

    gH = H
    gW = W

    #gMatrix = np.zeros((W, H, gDepth), dtype=np.uint8)

    try:
        if(layers == gDepth):
            gMatrix         = o.gMatrix
        else:
            print('layers != gDepth')
            CreateMatrix(W, H, 0)
            gMatrix[0:W,0:H, 0:layers] = o.gMatrix[0:W,0:H, 0:layers]
            if(layers <= L.color):
                for x in range(gW):
                    for y in range(gH):
                        if( gMatrix.item((x,y, L.ctype)) == T.person):
                            gMatrix[x, y, L.color] = makeColor(x,y)

            if(layers <= L.myth):
                for x in range(gW):
                    for y in range(gH):
                        if( gMatrix.item((x,y, L.ctype)) == T.person):
                            gMatrix[x, y, L.myth] = makeColor(x,y)


        #gMatrix[:]      = o.gMatrix
        #gMatrix         = np.copy(o.gMatrix)
        gMaxAge         = o.gMaxAge       
        gDiscoveryRate  = o.gDiscoveryRate
        gMaxIQres       = o.gMaxIQres     
        gAttSz          = o.gAttSz        
        gAttChildSz     = o.gAttChildSz   
        gChildAge       = o.gChildAge     
        gBirthEnergy    = o.gBirthEnergy  
        gMaxNeibghors   = o.gMaxNeibghors 
        gEpoch          = o.gEpoch        
        gPersons        = o.gPersons
        gPersonsTotal   = o.gPersonsTotal 
    except Exception as e:
        print('UnpackWorld ERR: '+ str(e))
        pass

    # newer versions
    try:
        gAllowLocalRes  = o.gAllowLocalRes
        gMutationRate   = o.gMutationRate   
        gMutationFactor = o.gMutationFactor 
        gMutationMinStep= o.gMutationMinStep
        gMutationTypeV  = o.gMutationTypeV
        gFailedBirthEnergy= o.gFailedBirthEnergy
    except Exception as e:
        gMutationRate   = 1
        gMutationFactor = 3
        gMutationMinStep= 1
        gMutationTypeV  = T.mutExt
        gFailedBirthEnergy = 0
        print('Load Defaults 1: '+ str(e))
        pass

    # newer versions
    try:
        gMaxDamage      = 1
        gMaxGroundRes   = 1
        gResRespawn     = 2
        gMaxDamage      = o.gMaxDamage
        gMaxGroundRes   = o.gMaxGroundRes
        gResRespawn     = o.gResRespawn
    except Exception as e:
        print('Load Defaults 2: '+ str(e))
        pass

    '''
    for key, value in o.__dict__.items():
        if not callable(value) and not key.startswith('__'):
            print(str(key)+"=>"+str(value))
    '''
    return True
#end UnpackWorld()

def GetTunableNames():
    return {
        "MaxAge"        : ["Maximum possible age", 100],
        "DiscoveryRate" : ["Discovery rate (extra energy), %",    30],
        "MaxIQres"      : ["Max resource benefit of high IQ", 2],
        "AttSz"         : ["Visibility/movement distance for adults", 10],
        "AttChildSz"    : ["Visibility/movement distance for children", 2],
        "ChildAge"      : ["Puberty age", 10],
        "BirthEnergy"   : ["Birth cost (energy/resource points)", 4 ],  
        "FailedBirthEnergy": ["Failed birth cost (no free place around)", 0 ],  
        "MaxNeibghors"  : ["Max. neibghors, try to move away when reached", 6],
        "AllowLocalRes" : ["Allow resource extraction from own cell, not only from free", False],
        "MutationRate"  : ["Mutation rate, %",    1],
        "MutationFactor": ["Mutation factor, max relative change",    3],
        "MutationMinStep": ["Mutation min step",    30],
        "MutationTypeV" : ["Mutation/inheritance model",    {0: "Progressive", 1:"Random", 2:"Natural"}],
        "MaxDamage"     : ["Max damage",    1],
        "MaxGroundRes"  : ["Default resource consumption",    2],
        "ResRespawn"    : ["Resource respawn factor (energy points)",    2],
#        "Parallel"      : ["Max parallel processes",    2],
        }
#end GetTunableNames

def GetInitOptions():
    global gInitOptions
    return gInitOptions
#end GetInitOptions()

def SetInitOptions(o):
    global gInitOptions
    gInitOptions = o
#end SetInitOptions()
        
def Save(fn):
    with open(fn, 'wb') as fh:
        o = PackWorld()
        pickle.dump(o, fh)

    return
#end Save()

def Load(fn):

    with open(fn, 'rb') as fh:
        o = pickle.load(fh) 
        if(o.version != 1):
            return False

        WLockWait()
    
        Stop()
        UnpackWorld(o)

        WRelease()

    #end with open()

    return True
#end Load()

