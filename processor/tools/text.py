from processor.tools.basetool import BaseTool
import pygame
import numpy as np
from util.pygame_textinput import TextInput
from PIL import Image, ImageDraw, ImageFont


class Texter(BaseTool):
    def __init__(self):
        super().__init__()
        self.textinput = None
        self.offset = None
        self.pre_pos = None
        self.out_bound = False

    def process(self, processor, event: pygame.event):
        focus = processor.focus

        if not processor.process_initialized:
            self.textinput = TextInput()
            self.offset = focus.offset
            processor.process_initialized = True
            self.out_bound = False

        text_rect = self.textinput.get_surface().get_rect()
        focus_rect = focus.surface.get_rect()
        if not self.test_inside(text_rect, focus_rect, self.out_bound):
            self.textinput.input_string = self.textinput.input_string[:-1]
        if not self.out_bound:
            self.textinput.update([event])
            processor.up_surface.fill(processor.background+[0])
            processor.up_surface.blit(self.textinput.get_surface(), self.offset)

        if processor.confirm:
            text = self.textinput.get_text()
            src = Image.fromarray(focus.raw_data.swapaxes(0, 1), "RGBA")
            im = Image.new("RGBA", (src.size[1], src.size[0]), color=(255, 255, 255, 0))
            draw = ImageDraw.Draw(im, "RGBA")
            scaler = focus.raw_data.shape[0] / focus.view_shape[0]
            text_size = scaler * 22
            font = ImageFont.truetype("FreeSansBold.ttf", int(text_size))
            im_offset = np.multiply(scaler, np.subtract(self.offset, focus.offset))
            draw.text(im_offset, text, fill=(0, 0, 0, 255), font=font)
            out = Image.alpha_composite(src, im)
            focus.raw_data = np.array(out).swapaxes(0, 1)
            # refresh variables
            focus.construct_surface()
            processor.REFRESH = True
            processor.PROCESS = False
            processor.process_initialized = False
        if processor.cancel:
            focus.construct_surface()
            processor.REFRESH = True
            processor.PROCESS = False
            processor.process_initialized = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            rect = pygame.Rect(self.offset,
                               self.textinput.get_surface().get_rect()[2:])
            event_rpos = processor.get_offset_pos(event.pos)
            if rect.collidepoint(event_rpos[0], event_rpos[1]):
                self.pre_pos = event_rpos
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pre_pos is not None:
                self.pre_pos = None
        elif event.type == pygame.MOUSEMOTION:
            if self.pre_pos is not None:
                event_rpos = processor.get_offset_pos(event.pos)
                move_pos = (event_rpos[0]-self.pre_pos[0],
                            event_rpos[1]-self.pre_pos[1])
                rect_offset = tuple(map(lambda x, y: x+y,
                                        self.offset, move_pos))
                rect_offset = (rect_offset[0], rect_offset[1])
                text_size = self.textinput.get_surface().get_size()
                im_size = focus.surface.get_size()
                boundary = pygame.Rect(focus.offset, np.subtract(im_size, text_size))
                self.offset = self.boundary_offset(rect_offset, boundary)
                self.pre_pos = event_rpos

    def test_inside(self, inner: pygame.Rect, outside: pygame.Rect, flag):
        return outside.collidepoint(inner.topleft[0], inner.topleft[1]) and \
               outside.collidepoint(inner.topright[0], inner.topright[1]) and \
               outside.collidepoint(inner.bottomleft[0], inner.bottomleft[1]) and \
               outside.collidepoint(inner.bottomright[0], inner.bottomright[1])

    def boundary_offset(self, offset, boundary:pygame.Rect):
        x0, y0 = boundary.topleft
        x1, y1 = boundary.bottomright
        new_x = offset[0]
        new_y = offset[1]
        if offset[0] < x0:
            new_x = x0
        elif offset[0] > x1:
            new_x = x1
        if offset[1] < y0:
            new_y = y0
        elif offset[1] > y1:
            new_y = y1
        return (new_x, new_y)