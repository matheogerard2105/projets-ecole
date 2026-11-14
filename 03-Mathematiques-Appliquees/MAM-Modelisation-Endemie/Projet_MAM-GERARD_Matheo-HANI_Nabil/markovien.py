from random import *
import matplotlib.pyplot as plt
def simulation1temp (N,i,p):
    s=i
    for j in range(N-i):
        a=random()
        if a <(1-p)**i:
            s+=1
    return N-s
def simulationntemps (N,i0,p,n):
    i=i0
    listei=[]
    listei.append(i)
    for j in range (n):
        i=simulation1temp(N,i,p)
        listei.append(i)
    listex=list(range(0, len(listei)))
    plt.plot(listex,listei)
    plt.show()
    return i
def calculT(N,i,p):
    t=0
    sim=simulation1temp(N,i,p)
    while sim!=0:
        t+=1
        sim=simulation1temp(N,sim,p)
    return t

def moyenneT(N,i,p):
    s=0
    for k in range(10):
        s+=calculT(N,i,p)
    return s/10