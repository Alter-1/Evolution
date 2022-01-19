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

    pseudo_genes = 12 # marker
    color     = 12

    layers    = 13

LayerName = [
    "resources ",
    "ctype     ",
    "energy    ",
    "age       ",
    "sex       ",
    "exp       ",
                
    #"genes     ",
                
    "share     ",
    "aggressive",
    "iq        ",
    "defence   ",
    "mobility  ",
    "fert      ",
    "color     ",
                
    "layers    "]

class T:
    ground = 0
    person = 1

    male = 0
    female = 1

    # mutation range
    mutExt = 0  # depends on delta between current range and max/min available
    mutInt = 1  # depends only on current range +/- N% with fixed minimal step
    mutNat = 2  # natural - random around mean value of parents

