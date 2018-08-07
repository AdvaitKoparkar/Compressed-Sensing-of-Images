import socket
import sys
import cv2
import numpy as np
from DCT2D_Matrix import DCT2D_Matrix, Psi_select
from functions import *
import argparse
import multiprocessing
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

MAX_NUM_OF_CLIENTS = 1

class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = 'localhost'
        self.port = 1060
        self.error = 0
        self.block_size = 16
        self.iters = 50
        self.authentication = None
        self.stop = ''
        self.q_compressed_image = multiprocessing.Queue()
        self.q_decompressed_image = multiprocessing.Queue()
        self.compressed_image = None
        self.decompressed_image = None
        self.Psi = None
        self.image_size = (0, 0)
        self.Phi = None
        self.compressed_image_size = (230, 1200)

    def get_Psi(self):
        """ Returns Psi (DCT) Matrix """
        Psi8,Psi16,Psi32 = DCT2D_Matrix()
        self.Psi = Psi_select(Psi8,Psi16,Psi32, self.block_size)
        # return Psi

    def receiveProcess(self):
        """ Receives compressed image and stores in receive queue """
        while True:
            self.compressed_image = receive_object_decrypt(self.sock, self.compressed_image_size, self.authentication)
            # self.compressed_image = receive_object(self.sock)
            if self.compressed_image is None:
                break
            self.q_compressed_image.put(self.compressed_image)

    def decompressProcess(self):
        """ Uses images from compressed queue and stores decompressed image in receive queue """
        # print("Entering dcompression process")
        while True:
            self.compressed_image = self.q_compressed_image.get()
            if self.compressed_image is None:
                continue
            self.decompress_image()
            if self.decompressed_image is None:
                break
            self.q_decompressed_image.put(self.decompressed_image)

    def displayProcess(self):
        """ Displays images from decompressed image queue """
        # print("entering display process")
        while True:
            self.decompress_image = self.q_decompressed_image.get()
            if not self.show_decompressed_image(self.decompress_image):
                break

    # def decompress_image(compressed_image, image_size, Phi, Psi):
    def decompress_image(self):
        """ Decompresses image """
        Rrows, Rcols = self.image_size[0], self.image_size[1]
        S1,SQ = Scalar_Quant(self.block_size)
        X0,i = CS_Recovery_Filt(self.compressed_image, self.Phi, self.Psi, Rrows, Rcols, SQ, S1, self.block_size, self.iters)
        self.decompressed_image  = col2img(X0, self.block_size, self.block_size, Rrows, Rcols)
        # plt.imshow(X1, cmap='gray', interpolation = 'bicubic')
        # plt.show()
        # return X1

    def show_decompressed_image(self, X1):
        """ display image """
        X1 = cv2.convertScaleAbs(X1)
        cv2.imshow('Reconstructed Image',X1)
        if cv2.waitKey(1) == 27:
            return False
        return True

    def set_values(self, address, port, subrate, error, block_size, iters, authentication):
        self.address = address
        self.port = port
        self.subrate = subrate
        self.error = error
        self.block_size = block_size
        self.iters - iters
        self.authentication = authentication

    def stop_processes(self):
        self.receive_process.terminate()
        self.decompress_process.terminate()
        self.display_process.terminate()
        self.q_compressed_image.close()
        self.q_compressed_image.join_thread()
        self.q_decompressed_image.close()
        self.q_decompressed_image.join_thread()

    def client(self):
        """ Client driver function """
        # self.set_values(address, port, subrate, error, block_size, iters, authentication)
        self.get_Psi()
        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.address, self.port))
        # sock.shutdown(socket.SHUT_WR)

        send_object(self.sock, self.block_size)
        send_object(self.sock, self.subrate)
        send_object(self.sock, self.error)

        self.sock.shutdown(socket.SHUT_WR)

        self.image_size = receive_object(self.sock)
        self.Phi = receive_object(self.sock)
        self.compressed_image_size = receive_object(self.sock)


        # self.rows_of_compressed_image = 230  # Phi.shape[0]
        # self.cols_of_compressed_image = 1200 # (image_size[0]*image_size[1])/(block_size*block_size)

        self.receive_process = multiprocessing.Process(target = self.receiveProcess)
        self.decompress_process = multiprocessing.Process(target = self.decompressProcess)
        self.display_process = multiprocessing.Process(target = self.displayProcess)

        self.receive_process.start()
        time.sleep(0.2)
        self.decompress_process.start()
        self.display_process.start()

        # print("Press 'q' to exit")
        # while True:
        #     if self.stop == 'q':
        #         self.stop_processes()
        #         break
        #     self.stop = raw_input()

        # receive_process.join()
        # decompress_process.join()
        # display_process.join()

        self.sock.close()

class Server:

    def __init__(self):
        self.camera = PiCamera()
        self.rawCapture = PiRGBArray(camera)
        self.image = None
        self.address = ''
        self.port = 1060
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.image = None
        self.image_size = (0, 0)
        self.block_size = 16
        self.subrate= 0.9
        self.error = 0
        self.S1 = 0
        self.SQ = 0
        self.compressed_image = None
        self.compressed_image_size = (230, 1200)

    def get_image(self):                      ## FOR RPI
        # print("initializing camera")
        # self.camera = self.PiCamera()
        # self.rawCapture = PiRGBArray(camera)
        time.sleep(0.1)
        # print("capturing image")
        self.rawCapture.truncate(0)
        self.camera.capture(self.rawCapture, format="bgr")
        self.image = self.rawCapture.array
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        # print("image clicked")
        # return image

    # def get_image(self):
    #     """ Captures image from camera """
    #     # image = cv2.imread('car.jpg', 0)
    #     _, self.image = self.cap.read()
    #     self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
    #     # cap.release()
    #     # return self.image

    def get_image_size(self):
        """ Returns size of image passed to it """
        self.image_size = np.shape(self.image)

    def get_Phi(self):
        """ Returns Phi matrix and Phi1 matrix """
        N = self.block_size*self.block_size
        M = round(N*self.subrate)
        self.Phi = Phi_Matrix(M,N);
        self.Phi1 = Phi_Error(self.Phi,self.error, M, N);
        # return self.Phi, self.Phi1

    def compress_image(self):
        """ Compresses image and returns compressed image """
        X = img2col(self.image, self.block_size, self.block_size)
        self.compressed_image = CS_Compression(X, self.Phi, self.SQ);

    def set_values(self, address, port):
        self.address = address
        self.port = port

    def get_compressed_image_size(self):
        self.compress_image()
        self.compressed_image_size = self.compressed_image.shape

    def server(self, address, port):
        """ Server driver function """
        self.set_values(address, port)
        self.sock.bind((self.address, self.port))


        while True:
            self.sock.listen(MAX_NUM_OF_CLIENTS)
            self.sc, self.sockname = self.sock.accept()
            if self.sockname is None:
                continue

            self.cap = cv2.VideoCapture(0)
            self.block_size = receive_object(self.sc)
            self.subrate = receive_object(self.sc)
            self.error = receive_object(self.sc)

            self.sc.shutdown(socket.SHUT_RD)

            # camera = PiCamera()
            # rawCapture = PiRGBArray(camera)

            self.get_image()
            self.get_Phi()
            self.get_image_size()
            self.S1, self.SQ = Scalar_Quant(self.block_size)
            self.get_compressed_image_size()

            send_object(self.sc, self.image_size)
            send_object(self.sc, self.Phi1)
            send_object(self.sc, self.compressed_image_size)
            while True:
                # image = get_image(camera, rawCapture)
                self.get_image()
                if not self.image is None:
                    self.compress_image()
                    # send_object_encrypt(self.sc, self.compressed_image)
                    try:
                        send_object_encrypt(self.sc, self.compressed_image)

                    except:
                        self.cap.release()
                        break
                    # send_object_encrypt(self.sc, self.compressed_image)
                else:
                    self.cap.release()
                    break

            self.sc.close()
        self.sock.close()

if __name__ == '__main__':
    serverObj = Server()
    serverObj.server("", 1060)
