import numpy as np
from scipy import misc
from pygame import Surface
import pygame.surfarray as surfarray


class ImageToProcess:
    def __init__(self, raw_data: np.ndarray, view_shape, background, surface=None):
        self.raw_data = raw_data
        self.view_data = raw_data
        self.ori_data = raw_data
        self.view_shape = view_shape
        self.offset = (0, 0)
        self.background = background
        self.surface = surface
        self.construct_surface()

    def construct_surface(self):
        self.ori_data = self.raw_data
        shape = self.raw_data.shape[:2]
        width = shape[0]
        height = shape[1]
        height_scaler = self.view_shape[1] / height
        width_scaler = self.view_shape[0] / width
        if height_scaler <= width_scaler:
            new_width = int(width * height_scaler)
            self.view_data = misc.imresize(self.raw_data, (new_width, self.view_shape[1]))

        elif height_scaler > width_scaler:
            new_height = int(height * width_scaler)
            self.view_data = misc.imresize(self.raw_data, (self.view_shape[0], new_height))

        self.view_shape = self.view_data.shape[:2]
        self.surface = surfarray.make_surface(self.view_data)

    def raw_pos(self, pos):
        pos = np.array(pos)
        pos = pos - np.array(self.offset)
        scaler = pos / np.array(self.view_data.shape[:2])
        raw_pos = (scaler * self.raw_data.shape[:2]).astype(np.int32)
        return tuple(raw_pos)

