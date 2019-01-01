import logging

from util.buttons import Register, MultipleSelection, ExclusiveSelection
from processor.Processors import ImageProcessor
from processor.ProcessingImage import ImageToProcess
from util.buttons import PygButton, FocusButtonBar
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


def draw_quatragon_line(surface, color, rect):
    pygame.draw.line(surface, color, rect[0], rect[1])
    pygame.draw.line(surface, color, rect[0], rect[2])
    pygame.draw.line(surface, color, rect[1], rect[3])
    pygame.draw.line(surface, color, rect[2], rect[3])


def centered_rect(pos, size):
    rect = pygame.Rect(pos+size)
    rect.center = pos

    return rect


# initialize pygame buttons
def button_initialize(button_register: Register,
                      processor: ImageProcessor,
                      imFocus: FocusButtonBar,
                      args):
    temp_button_register = Register()

    # Exclusive selection
    exclusive_selection = ExclusiveSelection(processor=processor, pos=(800, 1), color=[60, 60, 60])
    button_register.register("exclusive", exclusive_selection)
    temp_button_register.register("exclusive", exclusive_selection)

    # Multiple selection
    multiple_selection = MultipleSelection(processor=processor, pos=(800, 1), color=[60, 60, 60])
    button_register.register("multiple", multiple_selection)
    temp_button_register.register("multiple", multiple_selection)

    # confirm button
    button_confirm = PygButton((502, 2, 38, 38),
                               bgcolor=[80, 80, 80],
                               fgcolor=[30, 30, 30],
                               image_path="resources/icons/confirm.png")
    def mouse_callback_confirm(event):
        button_cancel.visible = False
        button_confirm.visible = False
        processor.confirm = True
    button_confirm.mouseClickCallback = mouse_callback_confirm
    button_confirm.visible = False
    button_register.register("confirm", button_confirm)
    temp_button_register.register("confirm", button_confirm)

    # cancel_button
    button_cancel = PygButton((542, 2, 38, 38),
                               bgcolor=[80, 80, 80],
                               fgcolor=[30, 30, 30],
                               image_path="resources/icons/cancel.png")
    def mouse_callback_cancel(event):
        button_confirm.visible = False
        button_cancel.visible = False
        processor.cancel = True
    button_cancel.mouseClickCallback = mouse_callback_cancel
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
        processor.cancel = False
        processor.confirm = False
        button_cancel.visible = True
        button_confirm.visible = True
        processor.set_process("crop")
    button_crop.mouseClickCallback = button_crop_callback
    button_register.register("crop", button_crop)

    # rotate button
    button_rotate = PygButton((1, 127, 38, 38),
                            bgcolor=[80, 80, 80],
                            fgcolor=[30, 30, 30],
                            image_path="resources/icons/rotate.png")
    def button_rotate_callback(event):
        temp_button_register.set_all_invisible()
        processor.cancel = False
        processor.confirm = False
        button_cancel.visible = True
        button_confirm.visible = True
        processor.set_process("rotate")
    button_rotate.mouseClickCallback = button_rotate_callback
    button_register.register("rotate", button_rotate)

    # resize button
    button_resize = PygButton((1, 167, 38, 38),
                              bgcolor=[80, 80, 80],
                              fgcolor=[30, 30, 30],
                              image_path="resources/icons/resize.png")
    def button_resize_callback(event):
        temp_button_register.set_all_invisible()
        processor.cancel = False
        processor.confirm = False
        button_cancel.visible = True
        button_confirm.visible = True
        processor.set_process("resize")
    button_resize.mouseClickCallback = button_resize_callback
    button_register.register("resize", button_resize)

    # text button
    button_text = PygButton((1, 207, 38, 38),
                              bgcolor=[80, 80, 80],
                              fgcolor=[30, 30, 30],
                              image_path="resources/icons/text.png")
    def button_text_callback(event):
        temp_button_register.set_all_invisible()
        processor.cancel = False
        processor.confirm = False
        button_cancel.visible = True
        button_confirm.visible = True
        processor.set_process("text")
    button_text.mouseClickCallback = button_text_callback
    button_register.register("text", button_text)

    # reverse button
    button_reverse = PygButton((1, 247, 38, 38),
                               bgcolor=[80, 80, 80],
                               fgcolor=[30, 30, 30],
                               image_path="resources/icons/reverse.png")
    def button_reverse_callback(event):
        temp_button_register.set_all_invisible()
        processor.set_process("reverse")
    button_reverse.mouseClickCallback = button_reverse_callback
    button_register.register("reverse", button_reverse)

    # hist button
    button_hist = PygButton((1, 287, 38, 38),
                            bgcolor=[80, 80, 80],
                            fgcolor=[30, 30, 30],
                            image_path="resources/icons/histogram.png")
    def button_hist_callback(event):
        temp_button_register.set_all_invisible()
        exclusive_selection.visible = True
        exclusive_selection.contruct_selection(["equalization", "linear", "unlinear"])
        processor.cancel = False
        processor.confirm = False
        button_cancel.visible = True
        button_confirm.visible = True
        processor.set_process("hist")
    button_hist.mouseClickCallback = button_hist_callback
    button_register.register("hist", button_hist)

    # color button
    button_color = PygButton((1, 327, 38, 38),
                            bgcolor=[80, 80, 80],
                            fgcolor=[30, 30, 30],
                            image_path="resources/icons/colorspace.png")
    def button_color_callback(event):
        temp_button_register.set_all_invisible()
        exclusive_selection.visible = True
        exclusive_selection.contruct_selection(["HSV", "YCbCr", "LAB"])
        processor.cancel = False
        processor.confirm = False
        button_cancel.visible = True
        button_confirm.visible = True
        processor.set_process("color")
    button_color.mouseClickCallback = button_color_callback
    button_register.register("color", button_color)

    # blur button
    button_blur = PygButton((1, 367, 38, 38),
                             bgcolor=[80, 80, 80],
                             fgcolor=[30, 30, 30],
                             image_path="resources/icons/blur.png")
    def button_blur_callback(event):
        temp_button_register.set_all_invisible()
        exclusive_selection.visible = True
        exclusive_selection.contruct_selection(["average", "gaussian", "median"])
        processor.cancel = False
        processor.confirm = False
        button_cancel.visible = True
        button_confirm.visible = True
        processor.set_process("blur")
    button_blur.mouseClickCallback = button_blur_callback
    button_register.register("blur", button_blur)

    # sharpen button
    button_sharpen = PygButton((1, 407, 38, 38),
                             bgcolor=[80, 80, 80],
                             fgcolor=[30, 30, 30],
                             image_path="resources/icons/sharpen.png")
    def button_sharpen_callback(event):
        temp_button_register.set_all_invisible()
        exclusive_selection.visible = True
        exclusive_selection.contruct_selection(["sobel", "laplacian"])
        processor.cancel = False
        processor.confirm = False
        button_cancel.visible = True
        button_confirm.visible = True
        processor.set_process("sharpen")
    button_sharpen.mouseClickCallback = button_sharpen_callback
    button_register.register("sharpen", button_sharpen)

    # transform button
    button_transform = PygButton((1, 447, 38, 38),
                               bgcolor=[80, 80, 80],
                               fgcolor=[30, 30, 30],
                               image_path="resources/icons/transform.png")
    def button_transform_callback(event):
        temp_button_register.set_all_invisible()
        exclusive_selection.visible = True
        exclusive_selection.contruct_selection(["FFT", "DCT"])
        processor.cancel = False
        processor.confirm = False
        button_cancel.visible = True
        button_confirm.visible = True
        processor.set_process("transform")
    button_transform.mouseClickCallback = button_transform_callback
    button_register.register("transform", button_transform)

    # perspective button
    button_perspective = PygButton((1, 447, 38, 38),
                                 bgcolor=[80, 80, 80],
                                 fgcolor=[30, 30, 30],
                                 image_path="resources/icons/perspective.png")
    def button_perspective_callback(event):
        temp_button_register.set_all_invisible()
        processor.cancel = False
        processor.confirm = False
        button_cancel.visible = True
        button_confirm.visible = True
        processor.set_process("perspective")
    button_perspective.mouseClickCallback = button_perspective_callback
    button_register.register("perspective", button_perspective)

    # file button
    button_file = PygButton((2, 2, 50, 38),
                            caption="File",
                            bgcolor=[80, 80, 80],
                            fgcolor=[30, 30, 30],)
    def button_file_callback(event):
        temp_button_register.set_all_invisible()
        tkinter.Tk().withdraw()
        filename = askopenfilename(initialdir="./resources/images", title="Select files")
        # filename = "./resources/images/lena.jpg"
        if filename is not ():
            try:
                im = Image.open(filename)
                im = im.convert("RGBA")
                pixel_array = np.array(im)
                pixel_array = np.swapaxes(pixel_array, 0, 1)
                view_shape = args.view_shape
                imageObj = ImageToProcess(raw_data=pixel_array,
                                          view_shape=view_shape,
                                          background=[80, 80, 80])
                processor.set_image(imageObj)
                processor.set_process("image_added")
                imFocus.addImage(imageObj)
            except Exception as e:
                logging.exception("File open failed")
    button_file.mouseClickCallback = button_file_callback
    button_register.register("file", button_file)

    # save button
    button_save = PygButton((52, 2, 50, 38),
                            caption="Save",
                            bgcolor=[80, 80, 80],
                            fgcolor=[30, 30, 30],)
    def button_save_callback(event):
        temp_button_register.set_all_invisible()
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
                    im = im.convert("RGB")
                    im.save(filename)
                    processor.set_process("save")
            except Exception as e:
                logging.exception("File save failed")
    button_save.mouseClickCallback = button_save_callback
    button_register.register("save", button_save)
