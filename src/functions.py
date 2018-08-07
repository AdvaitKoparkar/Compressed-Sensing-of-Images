import cv2
import numpy as np
from matplotlib import pyplot as plt
import sys
import random
from scipy.signal import medfilt2d, wiener
import pickle, struct
from DCT2D_Matrix import DCT2D_Matrix, Psi_select
# import securitylib
import acorn
import time

header_struct = struct.Struct('q')

## ENCRYPTION VARIABLES
# c_key_byte = [0x12, 0x2f, 0xa2, 0xfc, 0xdb, 0x53, 0x78, 0xe4, 0x00, 0xbf, 0xc4, 0x91, 0xed, 0x6f, 0x33, 0xaa]
c_key_byte = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 65, 66, 67, 68, 69, 70]
c_iv_byte = [0xa2, 0x23, 0xae, 0xf3, 0x1b, 0x26, 0x78, 0xe9, 0xa0, 0xbf, 0x6c, 0x91, 0xdf, 0x1f, 0xf3, 0xfa]
c_ad_byte = [0x1b, 0x56, 0x78, 0xe9, 0xa0, 0x91, 0xef, 0x6f, 0xd3, 0x23, 0xa2, 0x12, 0xbf, 0xcc, 0xf3, 0xaa]
c_plaintext_byte = [0x12, 0x23, 0xa2, 0xf3, 0x1b, 0x56, 0x78, 0xe9, 0xa0, 0xbf, 0xcc, 0x91, 0xef, 0x6f, 0xd3, 0xdd]
#----------------------------------------
key = ''
for i in c_key_byte:
    a = bin(i)[2:]
    b = '0'*(8-len(a)) + a
    key += b[::-1]

#print len(key)
#print key

key = [int(i) for i in key]
#----------------------------------------
iv = ''
for i in c_iv_byte:
    a = bin(i)[2:]
    b = '0'*(8-len(a)) + a
    iv += b[::-1]

#print len(iv)
#print iv

iv = [int(i) for i in iv]
#----------------------------------------
ad = ''
for i in c_ad_byte:
    a = bin(i)[2:]
    b = '0'*(8-len(a)) + a
    ad += b[::-1]

#print len(ad)
#print ad
ad = [int(i) for i in ad]
#----------------------------------------


def img2col(image, Brows, Bcols):
    scrambled = image.copy()

    no_rows = scrambled.shape[0]
    no_cols = scrambled.shape[1]
    # print no_rows, no_cols
    ## Find the remainders
    Rr = no_rows%Brows
    Rc = no_cols%Bcols

    # print Rr, Rc
    if Rr == 0:
        max_width = no_rows
    else:
        max_width = no_rows + Brows-Rr

    if Rc == 0:
        max_height = no_cols
    else:
        max_height = no_cols + Bcols-Rc


    # resize to make sure each block has the same number of pixels from the initial image
    new_img = np.zeros(shape=(max_width,max_height))
    allBlocks = np.zeros(shape=(Brows*Bcols, (max_width*max_height)/(Brows*Bcols)))

    new_img[0:no_rows,0:no_cols]=image
    L = 0

##    # store all the blocks in a list, which we shuffle later and remerge
    #allBlocks = np.array([])
    for row in xrange(0,max_width,Brows):
        for col in xrange(0, max_height, Bcols):
            ## print row, col
            block = np.reshape(new_img[row:row+Brows, col:col+Bcols], (Brows*Bcols, 1))
            #allBlocks = np.append(allBlocks,block)
            allBlocks[:Brows*Bcols,L] = block[:,0]
            L = L+1
    return allBlocks

def col2img(X, Brow, Bcol, Rrows, Rcols ):
    ### need to be tested
    no_rows = X.shape[0]
    no_cols = X.shape[1]

    if no_rows*no_cols < Rrows*Rcols :
        print "Requested image size is more than the original columns matrix"
        # break

    # resize to make sure each block has the same number of pixels from the initial image
    #new_img = np.zeros(shape=(Rrows,Rcols))
    Kr = int(np.ceil(float(Rrows)/Brow)*Brow)
    Kc = int(np.ceil(float(Rcols)/Bcol)*Bcol)
    ## print 'row', Kr, 'col', Kc
    allBlocks = np.zeros(shape=(Kr, Kc))

    L = 0
    for row in xrange(0, Kr-1, Brow):
        for col in xrange(0, Kc-1, Bcol):
            #block = np.reshape(new_x[:, L], (Brow,Bcol))
            block = np.reshape(X[:int(Brow*Bcol), L], (Brow,Bcol))
            ## print row,row+Brow, col,col+Bcol
            allBlocks[row:row+Brow, col:col+Bcol] = block
            L = L+1

    # print allBlocks.shape

    new_img = allBlocks[:Rrows, :Rcols]


    return new_img

def col2img_block(X, block_size):
    X_img = np.zeros((block_size, block_size))
    col_len, _ = X.shape
    for i in range(col_len):
        X_img[i/block_size, i%block_size] = X[i,0]
    return X_img


def Phi_Matrix( M,N):

    #Phi = np.random.randn(int(M),int(N))
    #Phi[Phi > 0] = 1
    #Phi[Phi <= 0] = -1
    Phi = np.random.binomial(1, 0.5, size=(int(M),int(N)))
    Phi = -2*Phi+1
    # print 'Phi Sum', np.sum(Phi)
    return Phi

def Phi_Error(Phi,Err,M,N):
    Phi2 = Phi.copy();
    Phi1 = np.random.binomial(1, 0.5, size=(int(M),int(N)))
    Phi1 = -2*Phi1+1

    L = int(round(Err/10.0))
    for i in range(0,int(N)-20,10):
        Phi2[:,i:i+L] = Phi1[:,i:i+L]
    Phi1 = Phi2;

    return Phi1

def Scalar_Quant(block_size):
    SQ = float(2*block_size);
    S1 = float(block_size);
    return S1,SQ

def CS_Compression(X, Phi, SQ):
    Y = np.round(1/SQ*Phi.dot(X))
    return Y


def CS_Recovery_Filt(Y,Phi, Psi, Rrows, Rcols, SQ, S1, block_size, iters = 50):
    M,N = Phi.shape

    CR = round(M/float(N) * (Rrows*Rcols))
    S_CR = 1.0/np.sqrt(CR)

    lamda = 1;
    # iters = 100;
    ## Initial Iteration
    X = np.dot(np.transpose(Phi),Y)
    X_hat = X;

    Th_prev = 0;

    for i in range(0,iters):

        # X1 = col2img(X, block_size, block_size, Rrows, Rcols)
        X1 = col2img_block(X, block_size)
        X_hat1 = medfilt2d(X1,3)
        X_hat = img2col(X_hat1, block_size,block_size)

        R = Y - (1.0/float(SQ))*Phi.dot(X_hat)
        X_hat = X_hat + (1.0/float(S1))*np.dot(np.transpose(Phi),R)

        X_check = np.dot(np.transpose(Psi),X_hat)


        Th = lamda*S_CR*np.sqrt(np.sum(R*R))
        #Th = lamda*S_CR*np.linalg.norm(R,ord=2)
        ## print i, Th, lamda, R.dtype
        X_check[abs(X_check) < Th] = 0;

        X_bar = np.dot(Psi,X_check)

        R = Y - (1.0/float(SQ))*Phi.dot(X_bar)
        X = X_bar + (1.0/float(S1))*np.dot(np.transpose(Phi),R)

        if abs(Th_prev-Th) < 0.01 :
            if lamda > pow(2,-6):
                lamda = 0.5*lamda
            else:
                # print 'Number iterations =', i
                break


        Th_prev = Th


    return X,i

def send_object(sc, obj):
    """ Send any object """
    obj_b = pickle.dumps(obj)
    put_block(sc, obj_b)

def encrypt_object(img):
    p = ''
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            p = p + np.binary_repr(int(img[i][j]+255), 10)
    p = [int(i) for i in p]
    # t1 = cv2.getTickCount()
    z1, ct, tag1 = acorn.encrypt(key, iv, ad, p)
    # t2 = cv2.getTickCount()
    # print (t2-t1)/cv2.getTickFrequency()
    return ct, tag1


def send_object_encrypt(sc, obj):
    """ Send any object """
    obj_encrypted, tag1 = encrypt_object(obj)
    # if len(obj_encrypted) != obj.size*10: ## Should not go inside
    #     return
    obj_b = pickle.dumps(obj_encrypted)
    send_object(sc, tag1)
    put_block(sc, obj_b)

def receive_object(sock):
    """ Receive any object """
    obj_b = get_block(sock)
    obj = pickle.loads(obj_b)
    return obj

def decrypt_obj(ct, authentication):
    key_list = [i for i in authentication]
    key_list = map(ord, key_list)
    key1 = ''
    for i in key_list:
        a = bin(i)[2:]
        b = '0'*(8-len(a)) + a
        key1 += b[::-1]
    key1 = [int(i) for i in key1]

    z2, pt, tag2 = acorn.decrypt(key1, iv, ad, ct)
    pt = "".join(map(str, pt))
    pt = [pt[i:i+10] for i in range(0, len(pt), 10)]
    pt = map(lambda i: (int(i, 2)-255), pt)
    pt = np.array(pt)
    print('done')
    return pt, tag2

def receive_object_decrypt(sock, imgsize, authentication):
    """ Receive any object """
    tag1 = receive_object(sock)
    obj_b = get_block(sock)
    obj = pickle.loads(obj_b)
    obj_decrypted, tag2 = decrypt_obj(obj, authentication)
    # obj_array = np.fromstring(obj_decrypted, dtype = np.float64)
    # print obj_decrypted[imgsize[0]*imgsize[1]:]
    # obj_decrypted = obj_decrypted[:imgsize[0]*imgsize[1]]
    if tag1 == tag2:
        print 'equal tags'
        obj_decrypted = obj_decrypted.reshape(imgsize[0], imgsize[1])
        # cv2.imwrite('generated.jpg', obj_decrypted)
        return obj_decrypted
    else:
        return 60*np.random.randn(imgsize[0], imgsize[1])

def recvall(sock, length):
    """ Function to receive data over a network """
    blocks = []
    while length:
        block = sock.recv(length)
        if not block:
            raise EOFError('EOFError')
            exit(0)
        length -= len(block)
        blocks.append(block)
    return b''.join(blocks)

def get_block(sock):
    """ receive block of data over a netowrk """
    data = recvall(sock, header_struct.size)
    (block_length,) = header_struct.unpack(data)
    return recvall(sock, block_length)

def put_block(sock, message):
    """ Send block over a network """
    block_length = len(message)
    sock.send(header_struct.pack(block_length))
    sock.send(message)
