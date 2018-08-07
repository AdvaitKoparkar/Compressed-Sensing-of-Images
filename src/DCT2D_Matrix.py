
import cv2
import numpy as np
from matplotlib import pyplot as plt
import sys
import random



def DCT2D_Matrix():
    N = 8;
    Psi8 = np.zeros(shape=(N*N,N*N))

    for row in range(0,N):
        for col in range(0,N):
            X = np.zeros(shape=(N, N));
            X[row, col] = 1;
            X1 = cv2.idct(X);
            X2 = np.transpose(X1);
            X2 = X2.reshape(N*N,1);
            #print (row*(N)) + col
            Psi8[:, (row*(N)) + col] = X2[:,0]

    #np.savetxt('DCT2D_Matrix_Psi8.txt', Psi8, fmt='%2.4f\n')

    N = 16;
    Psi16 = np.zeros(shape=(N*N,N*N))

    for row in range(0,N):
        for col in range(0,N):
            X = np.zeros(shape=(N, N));
            X[row, col] = 1;
            X1 = cv2.idct(X);
            X2 = np.transpose(X1);
            X2 = X2.reshape(N*N,1);
            #print (row*(N)) + col
            Psi16[:, (row*(N)) + col] = X2[:,0]

    #np.savetxt('DCT2D_Matrix_Psi16.txt', Psi16, fmt='%2.4f\n')

    N = 32;
    Psi32 = np.zeros(shape=(N*N,N*N))

    for row in range(0,N):
        for col in range(0,N):
            X = np.zeros(shape=(N, N));
            X[row, col] = 1;
            X1 = cv2.idct(X);
            X2 = np.transpose(X1);
            X2 = X2.reshape(N*N,1);
            #print (row*(N)) + col
            Psi32[:, (row*(N)) + col] = X2[:,0]

    #np.savetxt('DCT2D_Matrix_Psi32.txt', Psi32, fmt='%2.4f\n')
    
    return Psi8,Psi16,Psi32

def Psi_select(Psi8,Psi16,Psi32, block_size):
    if block_size == 8:
        Psi = Psi8
    elif block_size == 16:
        Psi = Psi16
    elif block_size == 32:
        Psi = Psi32;
    else:
        print "ERROR: Invalid Input Block Size", block_size 
        Psi = [];

    return Psi
        
    

##Psi8,Psi16,Psi32 = DCT2D_Matrix()
##
##block_size = 21
##
##Psi = Psi_select(Psi8,Psi16,Psi32, block_size)
##
##print Psi.shape
