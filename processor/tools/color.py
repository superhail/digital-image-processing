from processor.tools.basetool import BaseTool
import pygame
import cv2


class Color(BaseTool):
    def __init__(self):
        super().__init__()

    def process(self, processor, event: pygame.event):
        focus = processor.focus
        if processor.confirm:
            if processor.selection == 0:
                raw_data = focus.raw_data.copy()
                raw_data[:, :, :3] = cv2.cvtColor(raw_data[:, :, :3], cv2.COLOR_RGB2HSV)
                focus.raw_data = raw_data
            elif processor.selection == 1:
                raw_data = focus.raw_data.copy()
                raw_data[:, :, :3] = cv2.cvtColor(raw_data[:, :, :3], cv2.COLOR_RGB2YCR_CB)
                focus.raw_data = raw_data
            elif processor.selection == 2:
                raw_data = focus.raw_data.copy()
                raw_data[:, :, :3] = cv2.cvtColor(raw_data[:, :, :3], cv2.COLOR_RGB2LAB)
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