from processor.tools.basetool import BaseTool
import pygame


class Reverser(BaseTool):
    def __init__(self):
        super().__init__()

    def process(self, processor, event: pygame.event):
        focus = processor.focus
        focus.raw_data = focus.ori_data
        focus.construct_surface()
        processor.PROCESS = False
        processor.REFRESH = True
        processor.process_initialized = False