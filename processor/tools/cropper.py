from processor.tools.basetool import BaseTool
import pygame
import util
import numpy as np


class Cropper(BaseTool):
    def __init__(self):
        super().__init__()
        self.pressed = None
        self.outline = None
        self.marker = (8, 8)

    def process(self, processor, event: pygame.event):
        if not processor.process_initialized:
            rect = processor.focus.surface.get_rect()
            size = [rect[2], rect[3]]
            self.outline = pygame.Rect(list(processor.focus.offset) + size)
            self.draw_outline(processor)
            processor.process_initialized = True
        if processor.confirm:
            focus = processor.focus
            raw_topleft = focus.raw_pos(self.outline.topleft)
            raw_bottomright = focus.raw_pos(self.outline.bottomright)
            focus.raw_data = focus.raw_data[
                             raw_topleft[0]:raw_bottomright[0], raw_topleft[1]:raw_bottomright[1], :]
            focus.offset = self.outline.topleft
            focus.view_shape = (self.outline.width, self.outline.height)
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
            topleft_rect = util.centered_rect(self.outline.topleft, self.marker)
            topright_rect = util.centered_rect(self.outline.topright, self.marker)
            bottomleft_rect = util.centered_rect(self.outline.bottomleft, self.marker)
            bottomright_rect = util.centered_rect(self.outline.bottomright, self.marker)
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
                image_rect = pygame.Rect(processor.focus.offset, processor.focus.surface.get_rect()[2:])
                if self.pressed == "topleft":
                    event_rpos = tuple(map(lambda x, y: x if x > y else y, event_rpos, image_rect.topleft))
                    bottomright = self.outline.bottomright
                    new_size = tuple(map(lambda y, x: y-x if y-x>0 else 0,
                                         bottomright, event_rpos))
                    self.outline = pygame.Rect(event_rpos, new_size)
                    self.draw_outline(processor)
                elif self.pressed == "topright":
                    event_rpos = \
                        (event_rpos[0] if event_rpos[0]<image_rect.topright[0] else image_rect.topright[0],
                         event_rpos[1] if event_rpos[1]>image_rect.topright[1] else image_rect.topright[1])
                    bottomleft = self.outline.bottomleft
                    new_size = \
                        (event_rpos[0]-bottomleft[0] if event_rpos[0]>bottomleft[0] else 0,
                         bottomleft[1]-event_rpos[1] if event_rpos[1]<bottomleft[1] else 0)
                    new_topleft = (self.outline.topleft[0], event_rpos[1])
                    self.outline = pygame.Rect(new_topleft, new_size)
                    self.draw_outline(processor)
                elif self.pressed == "bottomleft":
                    event_rpos = \
                        (event_rpos[0] if event_rpos[0]>image_rect.bottomleft[0] else image_rect.bottomleft[0],
                         event_rpos[1] if event_rpos[1]<image_rect.bottomleft[1] else image_rect.bottomleft[1])
                    topright = self.outline.topright
                    new_size = \
                        (topright[0]-event_rpos[0] if event_rpos[0]<topright[0] else 0,
                         event_rpos[1]-topright[1] if event_rpos[1]>topright[1] else 0)
                    new_topleft = (event_rpos[0], topright[1])
                    self.outline = pygame.Rect(new_topleft, new_size)
                    self.draw_outline(processor)
                elif self.pressed == "bottomright":
                    event_rpos = tuple(map(lambda x, y: x if x < y else y, event_rpos, image_rect.bottomright))
                    topleft = self.outline.topleft
                    new_size = tuple(map(lambda y, x: x-y if x-y>0 else 0,
                                         topleft, event_rpos))
                    self.outline = pygame.Rect(self.outline.topleft, new_size)
                    self.draw_outline(processor)
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed is not None:
                self.pressed = None

    def draw_outline(self, processor):
        processor.up_surface.fill(processor.background+[0])
        util.draw_rect_line(processor.up_surface, [255, 255, 255, 255], self.outline)
        topleft_rect = pygame.Rect(self.outline.topleft+self.marker)
        topleft_rect.center = self.outline.topleft
        pygame.draw.rect(processor.up_surface,
                         [255, 255, 255, 255],
                         topleft_rect)
        topright_rect = pygame.Rect(self.outline.topright+self.marker)
        topright_rect.center = self.outline.topright
        pygame.draw.rect(processor.up_surface,
                         [255, 255, 255, 255],
                         topright_rect)
        bottomleft_rect = pygame.Rect(self.outline.bottomleft+self.marker)
        bottomleft_rect.center = self.outline.bottomleft
        pygame.draw.rect(processor.up_surface,
                         [255, 255, 255, 255],
                         bottomleft_rect)
        bottomright_rect = pygame.Rect(self.outline.bottomright+self.marker)
        bottomright_rect.center = self.outline.bottomright
        pygame.draw.rect(processor.up_surface,
                         [255, 255, 255, 255],
                         bottomright_rect)
