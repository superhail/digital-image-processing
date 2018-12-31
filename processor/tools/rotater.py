from PIL import Image

from processor.tools.basetool import BaseTool
import pygame
import numpy as np
import util


class Rotater(BaseTool):
    def __init__(self):
        super().__init__()
        self.reference = (0, 0)
        self.start_pos = None
        self.angle = 0
        self.marker = (8, 8)

    def process(self, processor, event: pygame.event):
        focus = processor.focus
        if not processor.process_initialized:
            self.reference = tuple(np.add(focus.surface.get_rect().center, focus.offset))
            self.start_pos = None
            self.angle = 0
            self.draw_outline(processor)
            processor.process_initialized = True
        if processor.confirm:
            focus = processor.focus
            raw_data = focus.raw_data
            im = Image.fromarray(raw_data, "RGBA")
            rot_im = im.rotate(self.angle, expand=1, fillcolor=(80, 80, 80, 0), resample=Image.BILINEAR)
            rot = np.array(rot_im)
            cropped = self.crop_transparent_edge(rot)
            # reconstruct surface
            focus.raw_data = cropped
            scaler = np.average(np.divide(cropped.shape[:2], raw_data.shape[:2]))
            view_shape = np.array(np.ceil(np.multiply(scaler, focus.view_shape))).astype(np.int32)
            focus.view_shape = tuple(view_shape)
            rect = pygame.Rect((0, 0), focus.view_shape)
            rect.center = self.reference
            focus.offset = rect.topleft
            # refresh variables
            focus.construct_surface()
            focus.rotation = (focus.rotation + self.angle) % 360
            processor.REFRESH = True
            processor.PROCESS = False
            processor.process_initialized = False
        if processor.cancel:
            focus = processor.focus
            focus.construct_surface()
            processor.REFRESH = True
            processor.PROCESS = False
            processor.process_initialized = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            event_rpos = processor.get_offset_pos(event.pos)
            self.start_pos = event_rpos
        elif event.type == pygame.MOUSEMOTION:
            event_rpos = processor.get_offset_pos(event.pos)
            if self.start_pos is not None:
                end_rpos = event_rpos
                angle = self.get_angle(self.start_pos, end_rpos, self.reference)
                self.angle -= angle
                self.draw_outline(processor)
                self.start_pos = end_rpos
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.start_pos is not None:
                self.start_pos = None

    def draw_outline(self, processor):
        processor.up_surface.fill(processor.background+[0])
        rotation = processor.focus.rotation
        size = np.divide(processor.focus.surface.get_size(),
                         np.abs(np.sin(rotation * np.pi / 180)) + np.abs(np.cos(rotation * np.pi / 180)))
        size = tuple(np.array(np.ceil(size)).astype(np.int32))
        topleft, topright, bottomleft, bottomright = self.rotate_pos(self.angle+rotation,
                                                                     size,
                                                                     self.reference)
        util.draw_quatragon_line(processor.up_surface,
                                 [255, 255, 255, 255],
                                 (topleft, topright, bottomleft, bottomright))
        topleft_rect = pygame.Rect(topleft+self.marker)
        topleft_rect.center = topleft
        pygame.draw.rect(processor.up_surface,
                         [255, 255, 255, 255],
                         topleft_rect)
        topright_rect = pygame.Rect(topright+self.marker)
        topright_rect.center = topright
        pygame.draw.rect(processor.up_surface,
                         [255, 255, 255, 255],
                         topright_rect)
        bottomleft_rect = pygame.Rect(bottomleft+self.marker)
        bottomleft_rect.center = bottomleft
        pygame.draw.rect(processor.up_surface,
                         [255, 255, 255, 255],
                         bottomleft_rect)
        bottomright_rect = pygame.Rect(bottomright+self.marker)
        bottomright_rect.center = bottomright
        pygame.draw.rect(processor.up_surface,
                         [255, 255, 255, 255],
                         bottomright_rect)

    def rotate_pos(self, angle, size, offset):
        rect = pygame.Rect((0, 0), size)
        rect.center = (0, 0)
        topleft = rect.topleft
        topright = rect.topright
        bottomleft = rect.bottomleft
        bottomright = rect.bottomright

        pos_matrix = np.array((topleft, topright, bottomleft, bottomright))
        affine_transform = pos_matrix @ self.get_rotation_matrix(angle)

        centered_affine_transform = np.add(affine_transform, np.tile(offset, (4, 1)))
        topleft, topright, bottomleft, bottomright = centered_affine_transform.astype(np.int32)

        return tuple(topleft), tuple(topright), tuple(bottomleft), tuple(bottomright)

    def get_rotation_matrix(self, angle):
        angle = angle * np.pi / 180
        rotation = np.array([[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]])
        return rotation

    def crop_transparent_edge(self, pixel_array):
        index = np.argwhere(pixel_array[:, :, 3] == 255)
        x0, y0 = index.min(axis=0)
        x1, y1 = index.max(axis=0)
        pixel_array = pixel_array[x0:x1, y0:y1, :]
        pixel_array[pixel_array[:, :, 3] == 0] = [80, 80, 80, 0]

        return pixel_array

    def get_angle(self, start, end, ref):
        start_reference = tuple(np.subtract(start, ref))
        end_reference = tuple(np.subtract(end, ref))
        start_comp = np.complex(start_reference[0], start_reference[1])
        end_comp = np.complex(end_reference[0], end_reference[1])
        angle = np.angle(start_comp / end_comp) / np.pi * 180

        return angle

