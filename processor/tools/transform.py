from processor.tools.basetool import BaseTool
import pygame
import cv2
import numpy as np
import scipy.fftpack as fftpack
import matplotlib.pyplot as plt


class Transform(BaseTool):
    def __init__(self):
        super().__init__()

    def process(self, processor, event: pygame.event):
        focus = processor.focus
        if processor.confirm:
            if processor.selection == 0:
                raw_data = focus.raw_data.copy()
                gray = cv2.cvtColor(raw_data[:, :, :3], cv2.COLOR_RGB2GRAY)
                dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
                dft_shift = fftpack.fftshift(dft)
                mag = 20*np.log(cv2.magnitude(dft_shift[:,:,0],dft_shift[:,:,1]))
                plt.imshow(mag, cmap='gray')
                plt.title("FFT")
                plt.show()
            elif processor.selection == 1:
                raw_data = focus.raw_data.copy()
                gray = cv2.cvtColor(raw_data[:, :, :3], cv2.COLOR_RGB2GRAY)
                dct = cv2.dct(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
    #            dct_shift = fftpack.fftshift(dct)j2
                mag = 20*np.log(np.abs(dct))
                plt.imshow(mag, cmap='gray')
                plt.title("DCT")
                plt.show()
            # refresh variables
            processor.PROCESS = False
        elif processor.cancel:
            # refresh variables
            processor.PROCESS = False
