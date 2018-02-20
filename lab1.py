import numpy as np
import matplotlib.pyplot as plt
import math
import os

# ---------- Conversion constants --------------
conv1 = 0.0254   #inch to m
conv2 = 6894.76  #psi to Pa
conv3 = 3386.39  #inHg to Pa
dens = 998
visc = 0.001

#----------- Dimensions in Inches ------------
dim = dict()
dim['0.5PVC'] = [0.480,124.0]
dim['0.5Copper'] = [0.545,131.5]
dim['0.5Steel'] = [0.622,115.8]
dim['0.25Copper'] = [0.315,116.8]
dim['1Copper'] = [1.025,115.0]
dim['1Steel'] = [1.049,114.0]

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
    print(filename)
    
    two = False
    flow = []
    data = []
    for line in info:
        point = []
        a = line.split()
        if a[0] == 'mano':
            method = 'mano'
            material = a[1]
            continue
        elif a[0] == 'bourdin':
            method = 'bourdin'
            two = True
            material = a[1]
            continue
        elif a[0] == 'pt':
            method = 'pt'
            material = a[1]
            continue
        flow.append(float(a[0]))
        if two:
            point.append(float(a[1]))
            point.append(float(a[2]))  
            data.append(point)
        else:
            data.append(float(a[1]))
    return flow,data,method,material

def mflow(volt):
    mflow = 0.57*(volt - 1.02)
    return mflow

def velocity(mflow,diam):
    velocity = mflow/((math.pi/4)*(diam**2)*dens)
    return velocity

def reynolds(velocity,material):
    diam = dim[material][0]*conv1
    Re = dens*velocity*diam/visc
    return Re

def fric_fact(method,data,material,volt):
    if method == 'bourdin':
        up = data[0]*conv2
        down = data[1]*conv3
        delta_p = up-down
    elif method == 'mano':
        delta_p = (13593-998)*9.8*data*conv1
    elif method == 'pt':
        delta_p = 0.5*data*conv2  
        
    diam = dim[material][0]*conv1
    length = dim[material][1]*conv1
    flow = mflow(volt)
    fric = (delta_p*(diam**5)*(math.pi**2)*dens)/(8*length*(flow**2))
    velo = velocity(flow,diam)
    uncert = uncertainty(method,delta_p,material,volt)
    return fric,velo,uncert
    
def uncertainty(method,deltap,material,volt):
    import sympy as sp
    delta_p,voltage = sp.symbols('delta_p voltage')
    diam = dim[material][0]*conv1
    length = dim[material][1]*conv1
    w_volt = 0.001/2
    if method == 'bourdin':
        w_p1 = 0.35*conv2
        w_p2 = 0.1*conv2 + 0.25*conv3
        w_deltap = w_p1+w_p2
    elif method == 'mano':
        w_deltap = 0.1
    elif method == 'pt':
        w_deltap = deltap*0.0004
    fric = (delta_p*(diam**5)*(math.pi**2)*dens)/(8*length*((0.57*(voltage-1.02))**2))
    diff1 = fric.diff(delta_p)
    diff2 = fric.diff(voltage)
    deltap_contrib = diff1.subs({voltage:volt})*w_deltap
    volt_contrib = diff2.subs({delta_p:deltap,voltage:volt})*w_volt
    totalUncertainty = math.sqrt(deltap_contrib**2 + volt_contrib**2)
    return totalUncertainty

if __name__ == '__main__':
    from sys import argv
    myargs = getopts(argv)
    if '-i' in myargs:
        fin = myargs['-i']
    elif '-in' in myargs:
        fin = myargs['-in']
    
    if '-o' in myargs:
        fout = myargs['-o']
    
    flow,data,method,material = parse(fin)
    print flow
    print data
    fric = []
    Re = []
    path = 'C:\Users\Victor\Documents\RPI\TF2\lab1\Results'
    fout = os.path.join(path,material + '_out.txt')
    out = open(fout,'w')
    out.write(method+'\t'+material+'\n')
    for i in range(len(flow)):
        fric,velo,uncert = fric_fact(method,data[i],material,flow[i])
        out.write(str(fric)+'\t')
        out.write(str(velo)+'\t')
        out.write(str(reynolds(velo,material))+'\t')
        out.write(str('%.10f' %uncert)+'\n')
    out.close()

    
    