import random
import numpy as np
import pickle
import time
import threading

from multiprocessing import Process, Pipe

class Empty:
    pass        

gMatrix = None
'''
0 - resources
1 - type
2 - energy
3 - 
'''
class L:
    resources = 0
    ctype     = 1
    energy    = 2
    age       = 3
    sex       = 4
    exp       = 5

    genes     = 6 # marker

    share     = 6
    aggressive= 7
    iq        = 8
    defence   = 9
    mobility  = 10
    fert      = 11

    layers    = 12

class T:
    ground = 0
    person = 1

    male = 0
    female = 1


gDepth = L.layers
gW = 0
gH = 0
gMaxAge = 100
gDiscoveryRate = 30
gMaxIQres = 2
gAttSz = 10
gAttChildSz = 2
gChildAge = 10
gBirthEnergy = 4
gMaxNeibghors = 6
gAllowLocalRes = False
gIQ0 = True
gMutationRate = 1
gMutationFactor = 3

gEpoch=0
gPersons=0
gPersonsTotal=0

bStop = False
gWorldLock = threading.Lock()

nLockCounter = 0

def WLock():
    global gWorldLock, nLockCounter
    nLockCounter += 1
    return gWorldLock.acquire(False)
#end UILock()

def WLockWait():
    global gWorldLock, nLockCounter
    nLockCounter += 1
    return gWorldLock.acquire(True)
#end UILock()

def WRelease():
    global gWorldLock, nLockCounter
    nLockCounter -= 1
    gWorldLock.release()
#end UIRelease()

def CrossGenes(xm, ym, xf, yf, layer):
    global gMatrix
    global gMutationRate, gMutationFactor

    a = gMatrix[xm, ym, layer]
    b = gMatrix[xf, yf, layer]
    r = random.randint(0,1)
    if(r == T.male):
        r = a
    else:
        r = b

    m = random.randint(0,99)
    if(m < gMutationRate):
        v0 = min(a, b)
        v1 = max(a, b)
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
#end CrossGenes

def CreatePerson(x, y):
    global gMatrix, gPersons, gPersonsTotal
    global gIQ0
    gMatrix[x, y, L.ctype ] = T.person
    gMatrix[x, y, L.energy] = random.randint(20,50)
    gMatrix[x, y, L.age   ] = 16
    gMatrix[x, y, L.sex   ] = random.randint(0,1)
    gMatrix[x, y, L.exp   ] = 0

    if(gIQ0):
        gMatrix[x, y, L.share     ] = 0
        gMatrix[x, y, L.aggressive] = 0
        gMatrix[x, y, L.iq        ] = 0
        gMatrix[x, y, L.defence   ] = 0
        gMatrix[x, y, L.mobility  ] = 0
    else:
        gMatrix[x, y, L.share     ] = random.randint(0,10)
        gMatrix[x, y, L.aggressive] = random.randint(0,100)
        gMatrix[x, y, L.iq        ] = random.randint(0,100)
        gMatrix[x, y, L.defence   ] = random.randint(0,100)
        gMatrix[x, y, L.mobility  ] = random.randint(0,100)
    gMatrix[x, y, L.fert      ] = random.randint(0,100)

    gPersons += 1
    gPersonsTotal += 1
#end CreatePerson()

def CreateChild(x, y, xm, ym, xf, yf):
    global gMatrix, gBirthEnergy, gPersons, gPersonsTotal

    gMatrix[x, y, L.ctype ] = T.person
    #gMatrix[x, y, L.energy] = random.randint(10,20)
    #gMatrix[x, y, L.energy] = random.randint(1,gBirthEnergy)
    gMatrix[x, y, L.age   ] = 0
    gMatrix[x, y, L.sex   ] = random.randint(0,1)

    if(gMatrix[xf, yf, L.energy] < gBirthEnergy):
        de = gMatrix[xf, yf, L.energy]
    else:
        de = gBirthEnergy

    gMatrix[x, y, L.energy] = random.randint(1,de)
    gMatrix[xf, yf, L.energy] -= int(de)

    de = (gBirthEnergy * gMatrix[xm, ym, L.share]) / 200
    if(gMatrix[xm, ym, L.energy] < de):
        de = gMatrix[xm, ym, L.energy]/2

    gMatrix[xm, ym, L.energy] -= int(de)
    gMatrix[xf, yf, L.energy] += int(de)

    for layer in range(L.genes, L.layers):
        gMatrix[x, y, layer     ] = CrossGenes(xm, ym, xf, yf, layer)

    exp = (0 + gMatrix[xf, yf, L.exp] + gMatrix[xm, ym, L.exp]) * gMatrix[x, y, L.iq] / 200
    if(exp > 100):
        print("high exp")
        exp = 100
    gMatrix[x, y, L.exp   ] = int(exp)

    gPersons += 1
    gPersonsTotal += 1
    print("Birth sex/total", gMatrix[x,y, L.sex], gPersons)
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
    global gMatrix, gW, gH, gMaxAge, gPersons
    if(gMatrix[x,y, L.ctype] == T.ground):
        if(gMatrix[x,y, L.resources] < 150):
            gMatrix[x,y, L.resources] += 1
    else:
        #print("@"+str(x)+"x"+str(y))
        # die if no energy
        if(gMatrix[x,y, L.age] >= gMaxAge or \
           gMatrix[x,y, L.energy] < 1):
            gMatrix[x,y, L.ctype] = T.ground
            gMatrix[x,y, L.resources] = gMatrix[x,y, L.energy]
            gPersons -= 1
            print("Die sex/age/energy/iq total", gMatrix[x,y, L.sex], gMatrix[x,y, L.age], gMatrix[x,y, L.energy], gMatrix[x,y, L.iq], gPersons)
            return

        gMatrix[x,y, L.age] += 1
        gMatrix[x,y, L.energy] -= 1
    #end if()

#end HandleResources()

def FetchResources(x, y):
    global gMatrix, gW, gH, gDiscoveryRate, gMaxIQres, gAllowLocalRes

    if(gMatrix[x,y, L.ctype] == T.ground):
        return
    if(gMatrix[x,y, L.energy] > 250):
        return

    age = gMatrix[x,y, L.age]
    iq = gMatrix[x,y, L.iq]
    exp = gMatrix[x,y, L.exp]
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
        if(gMatrix[x,y, L.resources] > 0):
            gMatrix[x,y, L.energy] += 1
            gMatrix[x,y, L.resources] -= 1
    #end if(gAllowLocalRes)

    X=x
    Y=y

    '''
    n=1

    while(X==x and Y==y and n>0):
        d = 2+int(gMatrix[x,y, L.mobility]*2/100)
        ox = random.randint(0,d)
        oy = random.randint(0,d)

        D = int(d/2)
        X = x+ox-D
        Y = y+oy-D

        if(X<0 or X>=gW or Y<0 or Y>=gW):
            n -= 1
            continue

        if(age < gChildAge):
            if(gMatrix[X,Y, L.ctype] == T.ground):
                # children looks for adult
                X=x
                Y=y
        else:
            break

        n -= 1
    #end while()
    '''

    d = 2+int(gMatrix[x,y, L.mobility]*2/100)
    ox = random.randint(0,d)
    oy = random.randint(0,d)

    D = int(d/2)
    X = x+ox-D
    Y = y+oy-D

    if(X==x and Y==y):
        return
    if(X<0 or X>=gW or Y<0 or Y>=gW):
        return

    if(X>=0 and X<gW and Y>=0 and Y<gH):
        if(gMatrix[X,Y, L.ctype] == T.ground):

            '''
            IQ = random.randint(0,100)
            if(iq+exp < IQ):
                return
            '''
            dr = int((iq+exp)*gMaxIQres/100+1)
            dr = min(gMatrix[X,Y, L.resources], dr)

            if(gMatrix[X,Y, L.resources] >= 1):
                gMatrix[X,Y, L.resources] -= 1
                gMatrix[x,y, L.energy] += dr
        else:
            SHARE = random.randint(0,100)
            if(gMatrix[X,Y, L.share] > SHARE or age < gChildAge):
                gMatrix[X,Y, L.energy] -= 1
                gMatrix[x,y, L.energy] += 1
#                return

            AGGR = random.randint(0,100)
            if(gMatrix[x,y, L.aggressive] * (1 + iq/10) < AGGR):
                return

            DEF = random.randint(0,100)
            if(gMatrix[X,Y, L.defence] * (1 + iq/10)  < DEF):
                gMatrix[X,Y, L.energy] -= 1
                gMatrix[x,y, L.energy] += 1
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
            if(gMatrix[xi,yi, L.ctype] == T.person):
                N += 1
    #end for(x, y)

    return N

#end CountNeibghors()

def CountAttractionPoint(x, y):
    global gMatrix, gW, gH, gAttSz, gAttChildSz, gMaxNeibghors

    if(gMatrix[x,y, L.ctype] == T.ground):
        return
    if(gMatrix[x,y, L.energy] < 2):
        return

    bFindRes = False    

    MOB = random.randint(0,100)
    N = CountNeibghors(x, y)
    if(N == 8):
        return  # no chance

    if(gMatrix[x,y, L.mobility] > MOB):
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

    sex = gMatrix[x,y, L.sex]
    age = gMatrix[x,y, L.age]
    if(age < gChildAge):
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
            if(gMatrix[xi,yi, L.ctype] == T.ground):
                ResXsum += xi
                ResYsum += yi
                ResN += 1
                continue
            if(xi == x and yi == y):
                continue
            if(age >= gChildAge):
                if(gMatrix[xi,yi, L.sex] == sex):
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
    
    if(gMatrix[xi,yi, L.ctype] == T.person):
        return
    savedRes = gMatrix[xi,yi, L.resources]

    gMatrix[xi,yi] = gMatrix[x,y]
    gMatrix[x,y, L.ctype] = T.ground
    gMatrix[xi,yi, L.resources] = savedRes
    gMatrix[xi,yi, L.energy] -= 1
#end CountAttractionPoint()

def MakeChildren(x, y):
    global gMatrix, gW, gH, gAttSz, gAttChildSz, gBirthEnergy

    if(gMatrix[x,y, L.ctype] == T.ground):
        return
    if(gMatrix[x,y, L.energy] < gBirthEnergy):
        return
    if(gMatrix[x,y, L.sex] == T.male):
        return
    if(gMatrix[x,y, L.age] < gChildAge + gMatrix[x,y, L.iq]/25):
        return

    sz = 1

    x0, x1, y0, y1 = AdjustRanges(x, y, sz)

    X = -1
    Y = -1
    xt = -1
    yt = -1

    for xi in range(x0, x1):
        for yi in range(y0, y1):
            if(xt == -1):
                if(gMatrix[xi,yi, L.ctype] == T.ground):
                    xt = xi
                    yt = yi
                    continue

            if(xi == x and yi == y):
                continue
            if(gMatrix[xi,yi, L.sex] == T.female):
                continue
            if(gMatrix[xi,yi, L.age] < gAttChildSz + gMatrix[xi,yi, L.iq]/25):
                continue

            fert = 1 * gMatrix[x, y, L.fert] * gMatrix[xi, yi, L.fert]
            if( fert < random.randint(1,100*100)):
                continue

            if(X == -1):
                X = xi
                Y = yi
                if(not xt == -1):
                    break

    if(xt == -1 or X == -1):
        return

    # target, male, female
    CreateChild(xt, yt, X, Y, x, y)
#end MakeChildren()

def _Next():
    global gMatrix, gW, gH, gEpoch
    global bStop

    print(str(gEpoch))
    gEpoch += 1
    if(gEpoch == 1):
        return

    #print(str(bStop))

    try:
        for x in range(gW):
            for y in range(gH):
                if(bStop):
                    return
                HandleResources(x, y)
        for x in range(gW):
            for y in range(gH):
                if(bStop):
                    return
                FetchResources(x, y)
        for x in range(gW):
            for y in range(gH):
                if(bStop):
                    return
                CountAttractionPoint(x, y)
        for x in range(gW):
            for y in range(gH):
                if(bStop):
                    return
                MakeChildren(x, y)

    except Exception as e:
        print('_Next ERR: '+ str(e))
        print(str(x)+","+str(y))
        time.sleep(60)

    pass
    return    
#end _Next()

from multiprocessing import Process, Pipe
gStarted = False

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
        print('Try unpack world')
        bRet = UnpackWorld(o)
        print(str(gW)+'x'+ str(gH))
        if(not bRet):
            print('Cant unpack world')
            return
        
        while(True):
            #print(str(gEpoch))
            if(conn.poll()):
                print('Exit request')
                break
            _Next()
            #conn.send([gMatrix, gEpoch, gPersons, gPersonsTotal])
            o = PackWorld()
            conn.send(o)
        #end while()

    except Exception as e:
        print('f ERR: '+ str(e))
        time.sleep(60)
    pass
    return    
#end f()

def NextLocked():
    global gMatrix, gW, gH, gEpoch, gPersons, gPersonsTotal
    global parent_conn, child_conn
    global p, gStarted

    if(not gStarted):
        parent_conn, child_conn = Pipe()
        p = Process(target=f, args=(parent_conn,))
        p.start()
        '''
        child_conn.send([gMatrix, gW, gH, gEpoch, gPersons, gPersonsTotal])
        '''
        o = PackWorld()
        #s = pickle.dumps(o)
        child_conn.send(o)
        
        gStarted = True
    #end if(not gStarted)


    if(not p.is_alive()):
        return False

    if(not child_conn.poll()):
        return False

    #gMatrix, gEpoch, gPersons, gPersonsTotal = child_conn.recv()
    o = child_conn.recv()
    bRet = UnpackWorld(o)
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
    global parent_conn, child_conn
    global p, gStarted

    if(gStarted):
        if(not p.is_alive()):
            return
        #child_conn.send("Stop")
        #p.join()
        p.terminate()
        #p.close()
        parent_conn.close()
        child_conn.close()
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
    global gMaxNeibghors 
    global gEpoch        
    global gPersons      
    global gPersonsTotal 
    global gAllowLocalRes


    #print("matrix=>"+str(gMatrix))

    o = Empty()

    o.version = 1
    o.L = L()
    #o.gMatrix         = np.copy(gMatrix)
    o.gMatrix         = gMatrix
    o.gMaxAge         = gMaxAge
    o.gDiscoveryRate  = gDiscoveryRate
    o.gMaxIQres       = gMaxIQres     
    o.gAttSz          = gAttSz        
    o.gAttChildSz     = gAttChildSz   
    o.gChildAge       = gChildAge     
    o.gBirthEnergy    = gBirthEnergy  
    o.gMaxNeibghors   = gMaxNeibghors 
    o.gEpoch          = gEpoch        
    o.gPersons        = gPersons
    o.gPersonsTotal   = gPersonsTotal 
    o.gAllowLocalRes  = gAllowLocalRes

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
    global gMaxNeibghors 
    global gEpoch        
    global gPersons      
    global gPersonsTotal 
    global gAllowLocalRes

    global gH,gW,layers, gDepth

    H,W,layers    = o.gMatrix.shape
    if(layers != gDepth):
        print('layers != gDepth')
        gWorldLock.release()
        return False

    gH = H
    gW = W

    #gMatrix = np.zeros((W, H, gDepth), dtype=np.uint8)

    try:
        gMatrix         = o.gMatrix
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
        gAllowLocalRes  = o.gAllowLocalRes
    except Exception as e:
        print('UnpackWorld ERR: '+ str(e))
        pass

    '''
    for key, value in o.__dict__.items():
        if not callable(value) and not key.startswith('__'):
            print(str(key)+"=>"+str(value))
    '''
    return True
#end UnpackWorld()

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

