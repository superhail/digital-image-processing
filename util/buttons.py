"""
PygButton v0.1.0

PygButton (pronounced "pig button") is a module that implements UI buttons for Pygame.
PygButton requires Pygame to be installed. Pygame can be downloaded from http://pygame.org
PygButton was developed by Al Sweigart (al@inventwithpython.com)
https://github.com/asweigart/pygbutton


Simplified BSD License:

Copyright 2012 Al Sweigart. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY Al Sweigart ''AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Al Sweigart OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of Al Sweigart.
"""
from functools import reduce

import util
import pygame
import numpy as np
from pygame.locals import *
import pygame.surfarray as surfarray

pygame.font.init()
PYGBUTTON_FONT = pygame.font.Font('freesansbold.ttf', 14)

BLACK     = (  0,   0,   0)
WHITE     = (255, 255, 255)
DARKGRAY  = ( 64,  64,  64)
GRAY      = (128, 128, 128)
LIGHTGRAY = (212, 208, 200)


class Register:
    def __init__(self):
        self.element_dict = {}

    def register(self, name, element):
        self.element_dict[name] = element

    def handleEvent(self, event):
        for element in self.element_dict.values():
            if element.visible:
                retVal = element.handleEvent(event)

    def draw(self, screenObj):
        for element in self.element_dict.values():
            if element.visible:
                element.draw(screenObj)

    def set_invisible(self, name):
        self.element_dict[name].visible = False

    def set_all_invisible(self):
        for element in self.element_dict.values():
            element.visible = False


class ButtonBar:
    def __init__(self, color, pos, size):
        self.size = size
        self.pos = pos
        self.color = color

    def draw(self, screenObj):
        screenObj.fill(self.color, self.pos+self.size)

    def __sizeof__(self):
        return self.size


class ExclusiveSelection:
    def __init__(self, processor, pos, color):
        self.processor = processor
        self.selection = 0
        self.selection_list = []
        self.rect_list = []
        self.pos = pos
        self.color = color
        self.surface = None
        self.visible = False
        self.font = pygame.font.Font(None, 20)

    def draw(self, screenObj):
        self.surface.fill(self.color)
        for index, selection in enumerate(self.selection_list):
            if index == self.selection:
                sunken_color = np.subtract(self.color, 20)
                pygame.draw.rect(self.surface, sunken_color, self.rect_list[index])
                text = self.font.render(selection, True, (0, 0, 0))
                rect = text.get_rect()
                rect.center = self.rect_list[index].center
                self.surface.blit(text, rect.topleft)
            else:
                pygame.draw.rect(self.surface, self.color, self.rect_list[index])
                text = self.font.render(selection, True, (0, 0, 0))
                rect = text.get_rect()
                rect.center = self.rect_list[index].center
                self.surface.blit(text, rect.topleft)
        screenObj.blit(self.surface, self.pos)

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            event_rpos = np.subtract(event.pos, self.pos)
            for index, rect in enumerate(self.rect_list):
                if rect.collidepoint(event_rpos[0], event_rpos[1]):
                    self.selection = index
                    self.processor.selection = self.selection

    def contruct_selection(self, selection_list):
        self.selection_list = selection_list
        self.rect_list.clear()
        self.selection = 0
        for index, selection in enumerate(self.selection_list):
            rect = pygame.Rect((110 * index, 0), (100, 38))
            self.rect_list.append(rect)
        self.surface = pygame.Surface((110 * len(selection_list) - 10, 38), pygame.SRCALPHA)
        self.visible = True
        self.processor.selection = 0


class MultipleSelection:
    def __init__(self, processor, pos, color):
        self.processor = processor
        self.selections = []
        self.selection_list = []
        self.rect_list = []
        self.pos = pos
        self.color = color
        self.surface = None
        self.visible = False
        self.font = pygame.font.Font(None, 20)

    def draw(self, screenObj):
        self.surface.fill(self.color)
        for index, selection in enumerate(self.selection_list):
            if self.selections[index]:
                sunken_color = np.subtract(self.color, 20)
                pygame.draw.rect(self.surface, sunken_color, self.rect_list[index])
                text = self.font.render(selection, True, (0, 0, 0))
                rect = text.get_rect()
                rect.center = self.rect_list[index].center
                self.surface.blit(text, rect.topleft)
            else:
                pygame.draw.rect(self.surface, self.color, self.rect_list[index])
                text = self.font.render(selection, True, (0, 0, 0))
                rect = text.get_rect()
                rect.center = self.rect_list[index].center
                self.surface.blit(text, rect.topleft)
        screenObj.blit(self.surface, self.pos)

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            event_rpos = np.subtract(event.pos, self.pos)
            for index, rect in enumerate(self.rect_list):
                if rect.collidepoint(event_rpos[0], event_rpos[1]):
                    if np.sum(self.selections) > 1:
                        self.selections[index] = False if self.selections[index] else True
                    else:
                        self.selections[index] = True
                    self.processor.selection = reduce(lambda x, y: 2*x + y, self.selections, 0)

    def contruct_selection(self, selection_list):
        self.selection_list = selection_list
        self.rect_list.clear()
        self.selections.clear()
        for index, selection in enumerate(self.selection_list):
            rect = pygame.Rect((110 * index, 0), (100, 38))
            self.rect_list.append(rect)
            self.selections.append(False)
        self.selections[0] = True
        self.surface = pygame.Surface((110 * len(selection_list) - 10, 38), pygame.SRCALPHA)
        self.visible = True
        self.processor.selection = 0


class FocusButtonBar:
    def __init__(self, processor, color, pos, size):
        self.processor = processor
        self.size = size
        self.pos = pos
        self.color = color
        self.imageList = []
        self.confirm_buttonList = []
        self.cancel_buttonList = []
        self.id = 0
        self.focus = None
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        self.surface.fill(color=color)

    def draw(self, screenObj):
        self.surface.fill((80, 80, 80))
        for index, thumb in enumerate(self.imageList):
            if self.focus == index:
                rect = pygame.Rect((0, index * 50), (150, 50))
                pygame.draw.rect(self.surface, (50, 50, 50), rect)
            self.surface.blit(thumb, (6, index * 50 + 6))
            rect = pygame.Rect((3, index*50+3), (144, 44))
            util.draw_rect_line(self.surface, (60, 60, 60), rect)
        screenObj.blit(self.surface, self.pos)
        for conf, canc in zip(self.confirm_buttonList, self.cancel_buttonList):
            id = self.confirm_buttonList.index(conf)
            conf.rect = pygame.Rect(np.add(self.pos, (56, 6 + id * 50)), (38, 38))
            canc.rect = pygame.Rect(np.add(self.pos, (106, 6 + id * 50)), (38, 38))
            conf.draw(screenObj)
            canc.draw(screenObj)

    def handleEvent(self, event):
        for conf, canc in zip(self.confirm_buttonList, self.cancel_buttonList):
            conf.handleEvent(event)
            canc.handleEvent(event)

    def addImage(self, im):
        surf = surfarray.make_surface(im.raw_data[:, :, :3])
        thumbnail = pygame.transform.scale(surf, (38, 38))
        self.imageList.append(thumbnail)
        button_offset = np.add(self.pos, (56, 6 + self.id * 50))
        rect = pygame.Rect(button_offset, (38, 38))
        button_confirm = PygButton(rect,
                                   bgcolor=[80, 80, 80],
                                   fgcolor=[30, 30, 30],
                                   image_path="resources/icons/confirm.png")
        def confirm_callback(event):
            id = self.confirm_buttonList.index(button_confirm)
            self.selectImage(id)
        button_confirm.mouseClickCallback = confirm_callback
        self.confirm_buttonList.append(button_confirm)
        button_offset = np.add(self.pos, (106, 6 + self.id * 50))
        rect = pygame.Rect(button_offset, (38, 38))
        button_cancel = PygButton(rect,
                                  bgcolor=[80, 80, 80],
                                  fgcolor=[30, 30, 30],
                                  image_path="resources/icons/cancel.png")
        def cancel_callback(event):
            id = self.cancel_buttonList.index(button_cancel)
            self.deleteImage(id)
        button_cancel.mouseClickCallback = cancel_callback
        self.cancel_buttonList.append(button_cancel)
        self.focus = self.id
        self.id += 1

    def selectImage(self, id):
        self.processor.focus = self.processor.imagelist[id]
        self.focus = id

    def deleteImage(self, id):
        im = self.processor.imagelist.pop(id)
        self.cancel_buttonList.pop(id)
        self.confirm_buttonList.pop(id)
        self.imageList.pop(id)
        if self.processor.focus == im:
            if len(self.processor.imagelist) == 0:
                self.processor.focus = None
                self.focus = None
            else:
                index = (id + 1) % len(self.processor.imagelist)
                self.processor.focus = self.processor.imagelist[index]
                self.focus = index
        self.processor.REFRESH = True


class PygButton(object):
    def __init__(self, rect=None, caption='', bgcolor=LIGHTGRAY, fgcolor=BLACK, font=None, image_path=None, ):
        """Create a new button object. Parameters:
            rect - The size and position of the button as a pygame.Rect object
                or 4-tuple of integers.
            caption - The text on the button (default is blank)
            bgcolor - The background color of the button (default is a light
                gray color)
            fgcolor - The foreground color (i.e. the color of the text).
                Default is black.
            font - The pygame.font.Font object for the font of the text.
                Default is freesansbold in point 14.
            image_path - A pygame.Surface object for the button's image_path
                appearance.
            down - A pygame.Surface object for the button's pushed down
                appearance.
            highlight - A pygame.Surface object for the button's appearance
                when the mouse is over it.

            If the Surface objects are used, then the caption, bgcolor,
            fgcolor, and font parameters are ignored (and vice versa).
            Specifying the Surface objects lets the user use a custom image
            for the button.
            The image_path, down, and highlight Surface objects must all be the
            same size as each other. Only the image_path Surface object needs to
            be specified. The others, if left out, will default to the image_path
            surface.
            """
        if rect is None:
            self._rect = pygame.Rect(0, 0, 30, 60)
        else:
            self._rect = pygame.Rect(rect)

        self._caption = caption
        self._bgcolor = bgcolor
        self._fgcolor = fgcolor

        if font is None:
            self._font = PYGBUTTON_FONT
        else:
            self._font = font

        # tracks the state of the button
        self.buttonDown = False # is the button currently pushed down?
        self.mouseOverButton = False # is the mouse currently hovering over the button?
        self.lastMouseDownOverButton = False # was the last mouse down event over the mouse button? (Used to track clicks.)
        self._visible = True # is the button visible
        self.customSurfaces = False # button starts as a text button instead of having custom images for each surface
        self.imageSurface = None
        self.mouseClickCallback = None
        self.mouseDownCallback = None
        self.mouseEnterCallback = None
        self.mouseExitCallback = None
        self.mouseMoveCallback = None
        self.mouseUpCallback = None

        if image_path is None:
            # create the surfaces for a text button
            self.surfaceNormal = pygame.Surface(self._rect.size)
            self.surfaceDown = pygame.Surface(self._rect.size)
            self.surfaceHighlight = pygame.Surface(self._rect.size)
            self._update() # draw the initial button images
        else:
            # create the surfaces for a custom image button
            self.surfaceNormal = pygame.Surface(self._rect.size)
            self.surfaceDown = pygame.Surface(self._rect.size)
            self.surfaceHighlight = pygame.Surface(self._rect.size)
            self.setImageSurface(image_path)
            self._update() # draw the initial button images

    def handleEvent(self, eventObj):
        """All MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN event objects
        created by Pygame should be passed to this method. handleEvent() will
        detect if the event is relevant to this button and change its state.

        There are two ways that your code can respond to button-events. One is
        to inherit the PygButton class and override the mouse*() methods. The
        other is to have the caller of handleEvent() check the return value
        for the strings 'enter', 'move', 'down', 'up', 'click', or 'exit'.

        Note that mouseEnter() is always called before mouseMove(), and
        mouseMove() is always called before mouseExit(). Also, mouseUp() is
        always called before mouseClick().

        buttonDown is always True when mouseDown() is called, and always False
        when mouseUp() or mouseClick() is called. lastMouseDownOverButton is
        always False when mouseUp() or mouseClick() is called."""

        if eventObj.type not in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN) or not self._visible:
            # The button only cares bout mouse-related events (or no events, if it is invisible)
            return []

        retVal = []

        hasExited = False
        if not self.mouseOverButton and self._rect.collidepoint(eventObj.pos):
            # if mouse has entered the button:
            self.mouseOverButton = True
            self.mouseEnter(eventObj)
            retVal.append('enter')
        elif self.mouseOverButton and not self._rect.collidepoint(eventObj.pos):
            # if mouse has exited the button:
            self.mouseOverButton = False
            hasExited = True # call mouseExit() later, since we want mouseMove() to be handled before mouseExit()

        if self._rect.collidepoint(eventObj.pos):
            # if mouse event happened over the button:
            if eventObj.type == MOUSEMOTION:
                self.mouseMove(eventObj)
                retVal.append('move')
            elif eventObj.type == MOUSEBUTTONDOWN:
                self.buttonDown = True
                self.lastMouseDownOverButton = True
                self.mouseDown(eventObj)
                retVal.append('down')
        else:
            if eventObj.type in (MOUSEBUTTONUP, MOUSEBUTTONDOWN):
                # if an up/down happens off the button, then the next up won't cause mouseClick()
                self.lastMouseDownOverButton = False

        # mouse up is handled whether or not it was over the button
        doMouseClick = False
        if eventObj.type == MOUSEBUTTONUP:
            if self.lastMouseDownOverButton:
                doMouseClick = True
            self.lastMouseDownOverButton = False

            if self.buttonDown:
                self.buttonDown = False
                self.mouseUp(eventObj)
                retVal.append('up')

            if doMouseClick:
                self.buttonDown = False
                self.mouseClick(eventObj)
                retVal.append('click')

        if hasExited:
            self.mouseExit(eventObj)
            retVal.append('exit')

        return retVal

    def draw(self, surfaceObj):
        """Blit the current button's appearance to the surface object."""
        if self._visible:
            if self.buttonDown:
                surfaceObj.blit(self.surfaceDown, self._rect)
            elif self.mouseOverButton:
                surfaceObj.blit(self.surfaceHighlight, self._rect)
            else:
                surfaceObj.blit(self.surfaceNormal, self._rect)

            # if self.customSurfaces:
            #     surfaceObj.blit(self.imageSurface.convert(), self._rect)

    def _update(self):
        """Redraw the button's Surface object. Call this method when the button has changed appearance."""

        w = self._rect.width # syntactic sugar
        h = self._rect.height # syntactic sugar

        # fill background color for all buttons
        self.surfaceNormal.fill(self.bgcolor)
        self.surfaceDown.fill(self.bgcolor)
        self.surfaceHighlight.fill(self.bgcolor)

        sunken_color = list(map(lambda x: x-25 if x > 20 else 0, self.bgcolor))
        # draw border for down button
        self.surfaceDown.fill(
            sunken_color,
            (2, 2, w-4, h-4))
        pygame.draw.rect(self.surfaceDown, [125, 125, 212], (0, 0, w-1, h-1), 2)

        # draw border for highlight button
        self.surfaceHighlight.fill(
            sunken_color,
            (2, 2, w-4, h-4))

        # draw caption text for all buttons
        captionSurf = self._font.render(self._caption, True, self.fgcolor)
        captionRect = captionSurf.get_rect()
        captionRect.center = int(w / 2), int(h / 2)
        self.surfaceNormal.blit(captionSurf, captionRect)
        self.surfaceDown.blit(captionSurf, captionRect)
        self.surfaceHighlight.blit(captionSurf, captionRect)

        if self.customSurfaces:
            self.surfaceNormal.blit(self.imageSurface, (4, 4))
            self.surfaceDown.blit(self.imageSurface, (4, 4))
            self.surfaceHighlight.blit(self.imageSurface, (4, 4))


    def mouseClick(self, event):
        if self.mouseClickCallback is not None:
            self.mouseClickCallback(event)

    def mouseEnter(self, event):
        if self.mouseEnterCallback is not None:
            self.mouseEnterCallback(event)

    def mouseMove(self, event):
        if self.mouseMoveCallback is not None:
            self.mouseMoveCallback(event)

    def mouseExit(self, event):
        if self.mouseExitCallback is not None:
            self.mouseExitCallback(event)

    def mouseDown(self, event):
        if self.mouseDownCallback is not None:
            self.mouseDownCallback(event)

    def mouseUp(self, event):
        if self.mouseUpCallback is not None:
            self.mouseUpCallback(event)

    def setImageSurface(self, path):
        """Switch the button to a custom image type of button (rather than a
        text button). You can specify either a pygame.Surface object or a
        string of a filename to load for each of the three button appearance
        states."""
        self.customSurfaces = True
        imageSurface = pygame.image.load(path)
        height = imageSurface.get_height()
        width = imageSurface.get_width()
        if height >= width and height >= self._rect.height:
            scaler = height / self._rect.height
            self.imageSurface = \
                pygame.transform.scale(
                    imageSurface,
                    (int(height // scaler)-8, int(width // scaler)-8))
        elif width > self._rect.width and width > self._rect.width:
            scaler = width / self._rect.width
            self.imageSurface = \
                pygame.transform.scale(
                    imageSurface,
                    (int(height // scaler)-8, int(width // scaler)-8))
        else:
             self.imageSurface = imageSurface

    def _propGetCaption(self):
        return self._caption

    def _propSetCaption(self, captionText):
        self.customSurfaces = False
        self._caption = captionText
        self._update()

    def _propGetRect(self):
        return self._rect

    def _propSetRect(self, newRect):
        # Note that changing the attributes of the Rect won't update the button. You have to re-assign the rect member.
        self._update()
        self._rect = newRect


    def _propGetVisible(self):
        return self._visible


    def _propSetVisible(self, setting):
        # Note that if mouse is set to be invisible it wont have an exit event triggered
        if setting == True:
            self.mouseOverButton = False
        self._visible = setting


    def _propGetFgColor(self):
        return self._fgcolor


    def _propSetFgColor(self, setting):
        self.customSurfaces = False
        self._fgcolor = setting
        self._update()


    def _propGetBgColor(self):
        return self._bgcolor


    def _propSetBgColor(self, setting):
        self.customSurfaces = False
        self._bgcolor = setting
        self._update()


    def _propGetFont(self):
        return self._font


    def _propSetFont(self, setting):
        self.customSurfaces = False
        self._font = setting
        self._update()

    caption = property(_propGetCaption, _propSetCaption)
    rect = property(_propGetRect, _propSetRect)
    visible = property(_propGetVisible, _propSetVisible)
    fgcolor = property(_propGetFgColor, _propSetFgColor)
    bgcolor = property(_propGetBgColor, _propSetBgColor)
    font = property(_propGetFont, _propSetFont)