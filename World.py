import random
import numpy as np
import pickle

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

gEpoch=0
gPersons=0
gPersonsTotal=0

bStop = False

def CrossGenes(xm, ym, xf, yf, layer):
    global gMatrix
    a = gMatrix[xm, ym, layer]
    b = gMatrix[xf, yf, layer]
    v0 = min(a, b)
    v1 = max(a, b)
    r = random.randint(v0-1,v1+1)
    r = max(0, r)
    r = min(r, 100)
    return r

def CreatePerson(x, y):
    global gMatrix, gPersons, gPersonsTotal
    gMatrix[x, y, L.ctype ] = T.person
    gMatrix[x, y, L.energy] = random.randint(20,50)
    gMatrix[x, y, L.age   ] = 16
    gMatrix[x, y, L.sex   ] = random.randint(0,1)
    gMatrix[x, y, L.exp   ] = 0

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
    gMatrix[x, y, L.energy] = random.randint(1,gBirthEnergy)
    gMatrix[x, y, L.age   ] = 0
    gMatrix[x, y, L.sex   ] = random.randint(0,1)

    if(gMatrix[xf, yf, L.energy] < gBirthEnergy):
        gMatrix[xf, yf, L.energy] = 0

    for layer in range(L.genes, L.layers):
        gMatrix[x, y, L.share     ] = CrossGenes(xm, ym, xf, yf, layer)

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

    d = 2+int(gMatrix[x,y, L.mobility]*2/100)
    ox = random.randint(0,d)
    oy = random.randint(0,d)

    if(gAllowLocalRes):
        # unconditionally get local resorces if any
        if(gMatrix[x,y, L.resources] > 0):
            gMatrix[x,y, L.energy] += 1
            gMatrix[x,y, L.resources] -= 1
    #end if(gAllowLocalRes)

    D = int(d/2)
    X = x+ox-D
    Y = y+oy-D

    if(X==x and Y==y):
        return

    if(X>=0 and X<gW and Y>=0 and Y<gH):
        if(gMatrix[X,Y, L.ctype] == T.ground):

            IQ = random.randint(0,100)
            if(iq+exp < IQ):
                return

            dr = int(iq*gMaxIQres/100)
            dr = min(gMatrix[X,Y, L.resources], dr)

            if(gMatrix[X,Y, L.resources] >= 1):
                gMatrix[X,Y, L.resources] -= 1
                gMatrix[x,y, L.energy] += dr
        else:
            SHARE = random.randint(0,100)
            if(gMatrix[X,Y, L.share] > SHARE):
                gMatrix[X,Y, L.energy] -= 1
                gMatrix[x,y, L.energy] += 1
#                return

            AGGR = random.randint(0,100)
            if(gMatrix[x,y, L.aggressive] < AGGR):
                return

            DEF = random.randint(0,100)
            if(gMatrix[X,Y, L.defence] < DEF):
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
    if(gMatrix[x,y, L.mobility] > MOB):
        # high mobility, look for resources
        if(CountNeibghors(x, y) < gMaxNeibghors):
            # few neighbors, stay here
            return
        bFindRes = True
    else:
        # look for partner
        if(CountNeibghors(x, y) >= gMaxNeibghors):
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
    if(gMatrix[x,y, L.age] < gChildAge):
        return

    sz = 1

    x0, x1, y0, y1 = AdjustRanges(x, y, sz)

    X = -1
    Y = -1
    xt = -1
    yt = -1

    for xi in range(x0, x1):
        for yi in range(y0, y1):
            if(gMatrix[xi,yi, L.ctype] == T.ground):
                if(xt == -1):
                    xt = xi
                    yt = yi

                continue
            if(xi == x and yi == y):
                continue
            if(gMatrix[xi,yi, L.sex] == T.female):
                continue
            if(gMatrix[xi,yi, L.age] < gAttChildSz):
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

    CreateChild(xt, yt, xi, yi, X, Y)
#end MakeChildren()

def Next():
    global gMatrix, gW, gH, gEpoch
    print(str(gEpoch))
    gEpoch += 1
    if(gEpoch == 1):
        return

    try:
        for x in range(gW):
            for y in range(gH):
                if(bStop):
                    return
                HandleResources(x, y)
                FetchResources(x, y)
                CountAttractionPoint(x, y)
                MakeChildren(x, y)

    except Exception as e:
        print('ERR: '+ str(e))
        print(str(x)+","+str(y))

    pass
    return    
#end Next()

def Save(fn):
    with open(fn, 'wb') as fh:
        o = Empty()

        o.version = 1
        o.L = L()
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

        pickle.dump(o, fh)

    return
#end Save()

def Load(fn):
    with open(fn, 'rb') as fh:
        o = pickle.load(fh) 
        if(o.version != 1):
            return False

        H,W,layers    = o.gMatrix.shape
        if(layers != gDepth):
            return False
        gH = H
        gW = W
        try:
            gMatrix[:]      = o.gMatrix
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
        except:
            pass
    #end with open()

    return True
#end Load()

