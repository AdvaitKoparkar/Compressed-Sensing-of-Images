# Compressed-Sensing-of-Images
## Overview
![a](https://user-images.githubusercontent.com/21837899/43992042-66fe836c-9d46-11e8-8374-a2e4845c1a9b.png)

The aim of this project was to use compressed sensing to build a low-cost, remote camera surveillance system.
- The images captured by the remote raspberry pi are compressed using Non-Orthogonal Random Matrices - `src/functions.py - CS_Compression`
- The compressed images are encrypted using the ACORN Authenticated Encryption - `src/acorn.py`
- These are sent over a network to a computer which decrypts the images using the authenticated key `src/functions.py - send_object`
- Block-based Landweber method is used to recover images from the compressed image - `src/functions.py - CS_Recovery_Filt`
- Developed simple GUI for requesting raspberry pi to send images - `src/GUI.py`

## Results
Landweber compressed sensing is a block-based compressed sensing algorithm. Varying the block size and dimensions of the 
measurement matrix affects performance and quality of reconstruction. Since this application was built for real-time survellance 
applications, a between between the two parameters is to be maintained. 

### Sample images: 
#### Original Image
![cake](https://user-images.githubusercontent.com/21837899/43992214-cc312692-9d49-11e8-91eb-8dba59895a0e.jpg)

#### Reconstructed Images
Block Size 8
![b8s3i5](https://user-images.githubusercontent.com/21837899/43992213-c3677106-9d49-11e8-8223-632c46109d6c.jpg)

Block Size 32
![b32s6i50](https://user-images.githubusercontent.com/21837899/43992215-d07c5c58-9d49-11e8-896a-f63582e36256.jpg)


### Performance Summary

#### Compression
![b](https://user-images.githubusercontent.com/21837899/43992110-94a6d674-9d47-11e8-9d72-6c7d21cb745c.png)

#### Decompression
![c](https://user-images.githubusercontent.com/21837899/43992119-c161ec3a-9d47-11e8-874b-173624f246d7.png)

## GUI
![f](https://user-images.githubusercontent.com/21837899/43992167-d02dcb20-9d48-11e8-856e-6ae0216c089e.png)

## ACORN AE
http://www3.ntu.edu.sg/home/wuhj/research/caesar/caesar.html
