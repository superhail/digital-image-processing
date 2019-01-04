from processor.tools.basetool import BaseTool
import pygame
import cv2
import numpy as np
import matplotlib.pyplot as plt


class Color(BaseTool):
    def __init__(self):
        super().__init__()

    def process(self, processor, event: pygame.event):
        focus = processor.focus
        if processor.confirm:
            if processor.selection == 0:
                raw_data = focus.raw_data.copy()
                Y, U, V = cv2.split(cv2.cvtColor(raw_data[:, :, :3], cv2.COLOR_RGB2YUV))
                plt.subplot(131)
                plt.imshow(np.swapaxes(Y, 0, 1), cmap='gray')
                plt.axis('off')
                plt.subplot(132)
                plt.imshow(np.swapaxes(U, 0, 1), cmap='gray')
                plt.axis('off')
                plt.subplot(133)
                plt.imshow(np.swapaxes(V, 0, 1), cmap='gray')
                plt.axis('off')
                plt.show()
            elif processor.selection == 1:
                raw_data = focus.raw_data.copy()
                YCrCb = cv2.cvtColor(raw_data[:, :, :3], cv2.COLOR_RGB2YCR_CB)
                Y, Cr, Cb = cv2.split(YCrCb)
                plt.subplot(131)
                plt.imshow(np.swapaxes(Y, 0, 1), cmap='gray')
                plt.axis('off')
                plt.subplot(132)
                plt.imshow(np.swapaxes(Cr, 0, 1), cmap='gray')
                plt.axis('off')
                plt.subplot(133)
                plt.imshow(np.swapaxes(Cb, 0, 1), cmap='gray')
                plt.axis('off')
                plt.show()
            elif processor.selection == 2:
                raw_data = focus.raw_data.copy()
                LAB = cv2.cvtColor(raw_data[:, :, :3], cv2.COLOR_RGB2LAB)
                L, A, B = cv2.split(LAB)
                plt.subplot(131)
                plt.imshow(np.swapaxes(L, 0, 1), cmap='gray')
                plt.axis('off')
                plt.subplot(132)
                plt.imshow(np.swapaxes(A, 0, 1), cmap='gray')
                plt.axis('off')
                plt.subplot(133)
                plt.imshow(np.swapaxes(B, 0, 1), cmap='gray')
                plt.axis('off')
                plt.show()
            # refresh variables
            processor.PROCESS = False
        elif processor.cancel:
            # refresh variables
            processor.PROCESS = False