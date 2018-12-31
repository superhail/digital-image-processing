from processor.tools.basetool import BaseTool
import pygame
import cv2
import numpy as np


class Blur(BaseTool):
    def __init__(self):
        super().__init__()

    def process(self, processor, event: pygame.event):
        focus = processor.focus
        if processor.confirm:
            if processor.selection == 0:
                raw_data = focus.raw_data.copy()
                shape = raw_data.shape[:2]
                filter_size = (int(shape[0] / 60), int(shape[1] / 60))
                dst = cv2.blur(raw_data, filter_size)
                raw_data = dst
                focus.raw_data = raw_data
            elif processor.selection == 1:
                raw_data = focus.raw_data.copy()
                shape = raw_data.shape[:2]
                filter_size = (int(shape[0] / 60), int(shape[1] / 60))
                filter_size = tuple(map(lambda x: x if x % 2 == 1 else x+1, filter_size))
                dst = cv2.GaussianBlur(raw_data, filter_size, 0)
                raw_data = dst
                focus.raw_data = raw_data
            elif processor.selection == 2:
                raw_data = focus.raw_data.copy()
                shape = raw_data.shape[:2]
                filter_size = int(shape[0] / 120 + shape[1] / 120)
                dst = cv2.medianBlur(raw_data, filter_size if filter_size % 2 == 1 else filter_size + 1)
                raw_data = dst
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
