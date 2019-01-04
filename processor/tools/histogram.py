from processor.tools.basetool import BaseTool
import pygame
import util.imhelper as imhelper
import numpy as np
import scipy.ndimage as image
import cv2


class Histogrammer(BaseTool):
    def __init__(self):
        super().__init__()
    def process(self, processor, event: pygame.event):
        focus = processor.focus
        if processor.confirm:
            if processor.selection == 0:
                raw_data = focus.raw_data.copy()
                untransparent = raw_data[raw_data[:, :, 3] != 0]
                rgb = untransparent[None, :, :3]
                Y, Cb, Cr = cv2.split(cv2.cvtColor(rgb, cv2.COLOR_RGB2YCR_CB))
                eq_Y = cv2.equalizeHist(Y)
                eq_image = cv2.cvtColor(cv2.merge([eq_Y, Cb, Cr]), cv2.COLOR_YCR_CB2RGB)
                untransparent[:, :3] = np.squeeze(eq_image, 0)
                raw_data[raw_data[:, :, 3] != 0] = untransparent
                focus.raw_data = raw_data
            elif processor.selection == 1:
                raw_data = focus.raw_data.copy()
                untransparent = raw_data[raw_data[:, :, 3] != 0]
                rgb = untransparent[None, :, :3]
                Y, Cb, Cr = cv2.split(cv2.cvtColor(rgb, cv2.COLOR_RGB2YCR_CB))
                stretch_Y = ((Y - np.min(Y)) / (0.1+np.max(Y) - np.min(Y))) * 255
                stretch_Y = np.clip(stretch_Y, 0, 255).astype(Cb.dtype)
                stretch_image = cv2.cvtColor(cv2.merge([stretch_Y, Cb, Cr]), cv2.COLOR_YCR_CB2RGB)
                untransparent[:, :3] = np.squeeze(stretch_image, 0)
                raw_data[raw_data[:, :, 3] != 0] = untransparent
                focus.raw_data = raw_data
            elif processor.selection == 2:
                lambda_ = float(processor.text)
                raw_data = focus.raw_data.copy()
                untransparent = raw_data[raw_data[:, :, 3] != 0]
                rgb = untransparent[None, :, :3]
                Y, Cb, Cr = cv2.split(cv2.cvtColor(rgb, cv2.COLOR_RGB2YCR_CB))
                stretch_Y = (255 * np.power(Y/255, lambda_)).astype(Cb.dtype)
                stretch_Y = np.clip(stretch_Y, 0, 255)
                stretch_image = cv2.cvtColor(cv2.merge([stretch_Y, Cb, Cr]), cv2.COLOR_YCR_CB2RGB)
                untransparent[:, :3] = np.squeeze(stretch_image, 0)
                raw_data[raw_data[:, :, 3] != 0] = untransparent
                focus.raw_data = raw_data
            # refresh variables
            focus.construct_surface()
            processor.REFRESH = True
            processor.PROCESS = False
        elif processor.cancel:
            # refresh variables
            focus.construct_surface()
            processor.REFRESH = True
            processor.PROCESS = False
