import numpy as np 
import matplotlib.pyplot as plt

def getopts(argv):
    opts = {}  # Empty dictionary to store key-value pairs.
    while argv:  # While there are arguments left to parse...
        if argv[0][0] == '-':  # Found a "-name value" pair.
            opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
        argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
    return opts

def parse(filename):
    data = open(filename)
    info = data.readlines()
    
    fric = []
    Re = []
    std = []
    for line in info:
        a = line.split()
        if a[0] == 'mano' or a[0] == 'bourdin' or a[0] == 'pt':
            method = a[0]
            continue
        fric.append(float(a[0]))
        Re.append(float(a[2]))
        std.append(float(a[3]))
    return fric,Re,std,method

if __name__ == "__main__":
    from sys import argv
    myargs = getopts(argv)
    if '-i' in myargs:
        fin = myargs['-i']
    elif '-in' in myargs:
        fin = myargs['-in']    
    
    fric,Re,std,method = parse(fin)
    #-------- Smooth ------------
    Rey = np.arange(20000,130000)
    fric_b = 0.184*Rey**(-0.2)
    
    #--------- Copper -----------
    e = 0.03e-3
    d1 = 0.0138
    d2 = 0.008
    d3 = 0.0260
    rough1 = e/d1
    rough2 = e/d2
    rough3 = e/d3
    Rey = np.arange(10000,80000)
    
    #--------- Steel -------------
    e = 0.15e-3
    d1 = 0.015798
    d2 = 0.026644
    rough1 = e/d1
    rough2 = e/d2
    fric_c = 0.25*(np.log10((rough2*(1./3.7)) + (5.75/Rey**0.9)))**-2
    
    f = plt.figure()
    ax = f.add_subplot(111)
    ax.set_xlabel('Re')
    ax.set_ylabel('Friction Factor')
    plt.title('1" Steel ('+method+')')
    plt.plot(Rey,fric_c,color='g',label='expected')
    plt.errorbar(Re,fric,std,ecolor='r',label='experimental')
    plt.legend()
    plt.show()
    
    print fric,Re,std