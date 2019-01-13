import numpy as np
from scipy import misc
from pygame import Surface
from PIL import Image, ImageColor
import pygame.surfarray as surfarray
import pygame.transform as transform


class ImageToProcess:
    def __init__(self, raw_data: np.ndarray, view_shape, background, surface=None):
        self._raw_data = raw_data
        self.view_data = raw_data
        self.ori_data = raw_data
        self.view_shape = view_shape
        self.ori_view_shape = view_shape
        self.offset = (0, 0)
        self.ori_offset = self.offset
        self.background = background
        self.surface = surface
        self.construct_surface()
        self.rotation = 0

    def construct_surface(self):
        shape = self._raw_data.shape[:2]
        width = shape[0]
        height = shape[1]
        height_scaler = self.view_shape[1] / height
        width_scaler = self.view_shape[0] / width
        raw_data = self._raw_data.copy()
        raw_data[:, :, 3] = 255
        if height_scaler <= width_scaler:
            new_width = int(width * height_scaler)
            self.view_data = misc.imresize(raw_data, (new_width, self.view_shape[1]))

        elif height_scaler > width_scaler:
            new_height = int(height * width_scaler)
            self.view_data = misc.imresize(raw_data, (self.view_shape[0], new_height))

        self.view_shape = self.view_data.shape[:2]
        RGB_view_data = self.view_data[:, :, :3]
        self.surface = surfarray.make_surface(RGB_view_data)
        # self._raw_data = temp_raw_data

    def raw_pos(self, pos):
        pos = np.array(pos)
        pos = pos - np.array(self.offset)
        scaler = pos / np.array(self.view_data.shape[:2])
        raw_pos = (scaler * self._raw_data.shape[:2]).astype(np.int32)
        return tuple(raw_pos)

    @property
    def raw_data(self):
        return self._raw_data

    @raw_data.getter
    def raw_data(self):
        self.ori_view_shape = self.view_shape
        self.ori_offset = self.offset
        self.ori_data = self._raw_data.copy()
        return self._raw_data

    @raw_data.setter
    def raw_data(self, value):
        self._raw_data = value