import pygame
import numpy
from processor.tools import *
import util


class ImageProcessor:
    def __init__(self, surface: pygame.Surface,
                 up_surface: pygame.Surface,
                 offset=(100, 100),
                 background=(80, 80, 80)):
        self.REFRESH = False
        self.PROCESS = False
        self.focus = None
        self.imagelist = []
        self.up_surface = up_surface
        self.surface = surface
        self.tool_name = None
        self.offset = offset
        self.background = list(background)
        self.confirm = False
        self.cancel = False
        self.process_initialized = False

        # image processing tools
        self.mover = Mover()
        self.cropper = Cropper()
        self.rotater = Rotater()
        self.resizer = Resizer()

    def if_refresh(self):
        return self.REFRESH

    def if_process(self):
        return self.PROCESS

    def draw(self):
        self.surface.fill(self.background)
        for image in self.imagelist:
            self.surface.blit(self.focus.surface, self.focus.offset)
        self.up_surface.fill(self.background+[0])

    def process(self, event: pygame.event):
        if self.focus is not None:
            rect = self.focus.surface.get_rect()
            if self.tool_name == "image_added":
                self.focus.offset = \
                    (self.surface.get_width() // 2 - rect.center[0],
                     self.surface.get_height() // 2 - rect.center[1])
                self.REFRESH = True
                self.PROCESS = False
                self.tool_name = None
            elif self.tool_name == "move":
                self.mover.process(self, event)
            elif self.tool_name == "crop":
                self.cropper.process(self, event)
            elif self.tool_name == "save":
                self.REFRESH = True
                self.PROCESS = False
            elif self.tool_name == "rotate":
                self.rotater.process(self, event)
            elif self.tool_name == "resize":
                self.resizer.process(self, event)

    def set_process(self, tool_name: str):
        self.draw()
        self.process_initialized = False
        self.tool_name = tool_name
        self.PROCESS = True

    def set_image(self, image):
        self.focus = image
        self.imagelist.append(image)

    def set_surface(self, surface):
        self.surface = surface

    def get_offset_pos(self, pos):
        return (pos[0] - self.offset[0], pos[1] - self.offset[1])

