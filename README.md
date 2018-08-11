# Compressed-Sensing-of-Images

This repository contains the code which I worked on in the Summer of 2017 at Nanyang Technological Unicersity, Singapore. 
I interned under Prof. Lam Kwok Yan and Dr. Anupam Chattopadhyay from the School of Computer Science and Engineering. Dr. Vikram Kumar 
Pudi, a postdoctoral fellow under Dr. Anupam, guided me and helped me develop the Raspberry Pi based compressed sensing application.

## Overview
The aim of this project was to use compressed sensing to build a low-cost, remote camera surveillance system.
- The images captured by the remote raspberry pi are compressed using Non-Orthogonal Random Matrices - `src/funtions.py - CS_Compression`
- The compressed images are encrypted using the ACORN Authenticated Encryption - `src/acorn.py`
- These are sent over a network to a computer which decrypts the images using the authenticated key `src/functions.py - send_object`
- Block-based Landweber method is used to recover images from the compressed image - `src/functions.py - CS_Recovery_Filt`

# Results
