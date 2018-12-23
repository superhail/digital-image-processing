import pygame
from abc import ABC, abstractmethod


class BaseTool:
    def __init__(self):
        pass

    @abstractmethod
    def process(self, processor, event: pygame.event):
        pass
