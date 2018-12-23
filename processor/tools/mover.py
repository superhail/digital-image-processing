from processor.tools.basetool import BaseTool
import numpy as np
import pygame


class Mover(BaseTool):
    def __init__(self):
        self.pre_pos = None
        super().__init__()

    def process(self, processor, event: pygame.event):
        focus = processor.focus
        if event.type == pygame.MOUSEBUTTONDOWN:
            rect = pygame.Rect(focus.offset,
                               focus.surface.get_rect()[2:])
            event_rpos = processor.get_offset_pos(event.pos)
            if rect.collidepoint(event_rpos[0], event_rpos[1]):
                self.pre_pos = event_rpos
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pre_pos is not None:
                event_rpos = processor.get_offset_pos(event.pos)
                move_pos = [event_rpos[0]-self.pre_pos[0],
                            event_rpos[1]-self.pre_pos[1]]
                focus.offset = tuple(map(lambda x, y: x+y,
                                        focus.offset, move_pos))
                self.pre_pos = None
                processor.REFRESH = True

        elif event.type == pygame.MOUSEMOTION:
            if self.pre_pos is not None:
                event_rpos = processor.get_offset_pos(event.pos)
                move_pos = [event_rpos[0]-self.pre_pos[0],
                            event_rpos[1]-self.pre_pos[1]]
                rect_offset = list(map(lambda x, y: x+y,
                                        focus.offset, move_pos))
                rect = pygame.Rect(rect_offset + focus.surface.get_rect()[2:])
                processor.up_surface.fill(processor.background+[0])
                pygame.draw.line(processor.up_surface,
                                 [255, 255, 255, 255],
                                 rect.bottomleft,
                                 rect.bottomright)
                pygame.draw.line(processor.up_surface,
                                 [255, 255, 255, 255],
                                 rect.bottomleft,
                                 rect.topleft)
                pygame.draw.line(processor.up_surface,
                                 [255, 255, 255, 255],
                                 rect.topright,
                                 rect.bottomright)
                pygame.draw.line(processor.up_surface,
                                 [255, 255, 255, 255],
                                 rect.topleft,
                                 rect.topright)
