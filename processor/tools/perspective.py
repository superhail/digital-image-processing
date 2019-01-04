from processor.tools.basetool import BaseTool
import pygame
import cv2
import numpy as np
from PIL import Image
import util


class Perspective(BaseTool):
    def __init__(self):
        super().__init__()
        self.topleft = None
        self.topright = None
        self.bottomleft = None
        self.bottomright = None
        self.im_rect = None
        self.marker = (8, 8)
        self.pressed = None

    def process(self, processor, event: pygame.event):
        focus = processor.focus
        if not processor.process_initialized:
            rect = focus.surface.get_rect()
            size = [rect[2], rect[3]]
            outline = pygame.Rect(list(focus.offset) + size)
            self.topleft, self.topright, self.bottomleft, self.bottomright = \
                outline.topleft, outline.topright, outline.bottomleft, outline.bottomright
            self.im_rect = outline
            self.draw_outline(processor)
            processor.process_initialized = True
        if processor.confirm:
            raw_data = focus.raw_data
            view_data = focus.view_data
            offset = focus.offset
            im_rect = self.im_rect
            shape = raw_data.shape[:2]
            pts1 = np.subtract((self.topleft, self.topright, self.bottomleft, self.bottomright), offset)
            scaler = np.divide(shape, view_data.shape[:2])
            pts1 = np.array(np.multiply(pts1, scaler)).astype(np.int32).astype(np.float32)
            pts1 = np.flip(pts1, 1)
            pts2 = np.array([(0, 0), (0, shape[0]), (shape[1], 0), (shape[1], shape[0])]).astype(np.float32)
            M = cv2.getPerspectiveTransform(pts1, pts2)
            dst = cv2.warpPerspective(raw_data, M, (shape[1], shape[0]))
            focus.raw_data = dst
            focus.construct_surface()
            processor.REFRESH = True
            processor.PROCESS = False
            processor.process_initialized = False
            self.pressed = None
        if processor.cancel:
            focus = processor.focus
            focus.construct_surface()
            processor.REFRESH = True
            processor.PROCESS = False
            processor.process_initialized = False
            self.pressed = None
        if event.type == pygame.MOUSEBUTTONDOWN:
            event_rpos = processor.get_offset_pos(event.pos)
            topleft_rect = util.centered_rect(self.topleft, self.marker)
            topright_rect = util.centered_rect(self.topright, self.marker)
            bottomleft_rect = util.centered_rect(self.bottomleft, self.marker)
            bottomright_rect = util.centered_rect(self.bottomright, self.marker)
            if topleft_rect.collidepoint(event_rpos[0], event_rpos[1]):
                self.pressed = "topleft"
            elif topright_rect.collidepoint(event_rpos):
                self.pressed = "topright"
            elif bottomleft_rect.collidepoint(event_rpos):
                self.pressed = "bottomleft"
            elif bottomright_rect.collidepoint(event_rpos):
                self.pressed = "bottomright"
        elif event.type == pygame.MOUSEMOTION:
            if self.pressed is not None:
                # event relative position
                event_rpos = processor.get_offset_pos(event.pos)
                x0, y0 = event_rpos
                if self.pressed == "topleft":
                    x1, y1 = self.im_rect.topleft
                    self.topleft = (x0 if x0 > x1 else x1, y0 if y0 > y1 else y1)
                    self.draw_outline(processor)
                elif self.pressed == "topright":
                    x1, y1 = self.im_rect.topright
                    self.topright = (x0 if x0 < x1 else x1, y0 if y0 > y1 else y1)
                    self.draw_outline(processor)
                elif self.pressed == "bottomleft":
                    x1, y1 = self.im_rect.bottomleft
                    self.bottomleft = (x0 if x0 > x1 else x1, y0 if y0 < y1 else y1)
                    self.draw_outline(processor)
                elif self.pressed == "bottomright":
                    x1, y1 = self.im_rect.bottomright
                    self.bottomright = (x0 if x0 < x1 else x1, y0 if y0 < y1 else y1)
                    self.draw_outline(processor)
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed is not None:
                self.pressed = None

    def draw_outline(self, processor):
        processor.up_surface.fill(processor.background+[0])
        util.draw_quatragon_line(processor.up_surface,
                                 [255, 255, 255, 255],
                                 (self.topleft, self.topright, self.bottomleft, self.bottomright))
        topleft_rect = pygame.Rect(self.topleft+self.marker)
        topleft_rect.center = self.topleft
        pygame.draw.rect(processor.up_surface,
                         [255, 255, 255, 255],
                         topleft_rect)
        topright_rect = pygame.Rect(self.topright+self.marker)
        topright_rect.center = self.topright
        pygame.draw.rect(processor.up_surface,
                         [255, 255, 255, 255],
                         topright_rect)
        bottomleft_rect = pygame.Rect(self.bottomleft+self.marker)
        bottomleft_rect.center = self.bottomleft
        pygame.draw.rect(processor.up_surface,
                         [255, 255, 255, 255],
                         bottomleft_rect)
        bottomright_rect = pygame.Rect(self.bottomright+self.marker)
        bottomright_rect.center = self.bottomright
        pygame.draw.rect(processor.up_surface,
                         [255, 255, 255, 255],
                         bottomright_rect)
