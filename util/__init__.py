from util.buttons import Register
from processor.Processors import ImageProcessor
from processor.ProcessingImage import ImageToProcess
from util.buttons import PygButton
import tkinter
from tkinter.filedialog import askopenfilename, asksaveasfilename
import numpy as np
from PIL import Image
import pygame


def draw_rect_line(surface, color, rect):
    pygame.draw.line(surface, color, rect.topleft, rect.topright)
    pygame.draw.line(surface, color, rect.topleft, rect.bottomleft)
    pygame.draw.line(surface, color, rect.bottomleft, rect.bottomright)
    pygame.draw.line(surface, color, rect.bottomright, rect.topright)

def centered_rect(pos, size):
    rect = pygame.Rect(pos+size)
    rect.center = pos

    return rect


# initialize pygame buttons
def button_initialize(button_register: Register,
                      processor: ImageProcessor,
                      args):
    temp_button_register = Register()
    # confirm button
    button_confirm = PygButton((502, 2, 38, 38),
                               bgcolor=[80, 80, 80],
                               fgcolor=[30, 30, 30],
                               image_path="resources/icons/confirm.png")
    button_confirm.visible = False
    button_register.register("confirm", button_confirm)
    temp_button_register.register("confirm", button_confirm)

    # cancel_button
    button_cancel = PygButton((542, 2, 38, 38),
                               bgcolor=[80, 80, 80],
                               fgcolor=[30, 30, 30],
                               image_path="resources/icons/cancel.png")
    button_cancel.visible = False
    button_register.register("cancel", button_cancel)
    temp_button_register.register("cancel", button_cancel)

    # move button
    button_move = PygButton((1, 47, 38, 38),
                            bgcolor=[80, 80, 80],
                            fgcolor=[30, 30, 30],
                            image_path="resources/icons/move.png")
    def button_move_callback(event):
        temp_button_register.set_all_invisible()
        processor.set_process("move")
    button_move.mouseClickCallback = button_move_callback
    button_register.register("move", button_move)

    # crop button
    button_crop = PygButton((1, 87, 38, 38),
                            bgcolor=[80, 80, 80],
                            fgcolor=[30, 30, 30],
                            image_path="resources/icons/crop.png")
    def button_crop_callback(event):
        temp_button_register.set_all_invisible()
        button_cancel.visible = True
        def mouse_callback_cancel(event):
            button_confirm.visible = False
            button_cancel.visible = False
            processor.cancel = True
        button_cancel.mouseClickCallback = mouse_callback_cancel
        button_confirm.visible = True
        def mouse_callback_confirm(event):
            button_cancel.visible = False
            button_confirm.visible = False
            processor.confirm = True
        button_confirm.mouseClickCallback = mouse_callback_confirm
        processor.set_process("crop")
    button_crop.mouseClickCallback = button_crop_callback
    button_register.register("crop", button_crop)

    # file button
    button_file = PygButton((2, 2, 50, 38),
                            caption="File",
                            bgcolor=[80, 80, 80],
                            fgcolor=[30, 30, 30],)
    def button_file_callback(event):
        temp_button_register.set_all_invisible()
        button_cancel.visible = False
        button_confirm.visible = False
        # tkinter.Tk().withdraw()
        # filename = askopenfilename(initialdir="./resources/images", title="Select files")
        filename = "./resources/images/lena.jpg"
        if filename is not ():
            try:
                im = Image.open(filename)
                pixel_array = np.array(im)
                pixel_array = np.swapaxes(pixel_array, 0, 1)
                view_shape = args.view_shape
                list.reverse(view_shape)
                imageObj = ImageToProcess(raw_data=pixel_array,
                                          view_shape=view_shape,
                                          background=args.background)
                processor.set_image(imageObj)
                processor.set_process("image_added")
            except Exception as e:
                pass
    button_file.mouseClickCallback = button_file_callback
    button_register.register("file", button_file)

    # save button
    button_save = PygButton((52, 2, 50, 38),
                            caption="Save",
                            bgcolor=[80, 80, 80],
                            fgcolor=[30, 30, 30],)
    def button_save_callback(event):
        temp_button_register.set_all_invisible()
        button_cancel.visible = False
        button_confirm.visible = False
        tkinter.Tk().withdraw()
        filename = asksaveasfilename(initialdir="./resources/saved",
                                     title="Select files",
                                     filetypes=(("jpg files", "*.jpg"), ("png files", "*.png"),
                                                ("jpeg files", "*.jpeg")))
        if filename is not ():
            try:
                if processor.focus is not None:
                    pixel_array = processor.focus.raw_data
                    pixel_array = np.swapaxes(pixel_array, 0, 1)
                    im = Image.fromarray(pixel_array)
                    im.save(filename)
                    processor.set_process("save")
            except Exception as e:
                pass
    button_save.mouseClickCallback = button_save_callback
    button_register.register("save", button_save)
