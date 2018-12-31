from processor.tools.basetool import BaseTool
import pygame
import cv2
import numpy as np

class Sharpen(BaseTool):
    def __init__(self):
        super().__init__()

    def process(self, processor, event: pygame.event):
        focus = processor.focus
        if processor.confirm:
            if processor.selection == 0:
                raw_data = focus.raw_data.copy()
                sobel_x = cv2.Sobel(np.float32(raw_data), cv2.CV_32F, 1, 0)
                sobel_y = cv2.Sobel(np.float32(raw_data), cv2.CV_32F, 0, 1)
                mag, ang = cv2.cartToPolar(sobel_x, sobel_y)
                raw_data = np.float32(raw_data) + 0.2 * np.absolute(mag)
                raw_data = np.clip(raw_data, 0, 255)
                focus.raw_data = raw_data.astype(np.int32)
            elif processor.selection == 1:
                raw_data = focus.raw_data.copy()
                laplacian = cv2.Laplacian(np.float32(raw_data), cv2.CV_32F)
                raw_data = np.float32(raw_data) + np.absolute(laplacian)
                raw_data = np.clip(raw_data, 0, 255)
                focus.raw_data = raw_data.astype(np.int32)
            # refresh variables
            focus.construct_surface()
            processor.REFRESH = True
            processor.PROCESS = False
        elif processor.cancel:
            # refresh variables
            focus.construct_surface()
            processor.REFRESH = True
            processor.PROCESS = False

