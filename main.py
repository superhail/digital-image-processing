import sys
import pygame
import argparse
from util.buttons import PygButton, Register, ButtonBar, FocusButtonBar, MultipleSelection, Input
from util import button_initialize
from processor.Processors import ImageProcessor


def main(args):
    # read arguments
    size = width, height = args.width, args.height
    background = args.background
    canvas_size = args.canvas_size
    canvas_offset = [100, 100]

    # initialize screen
    pygame.init()
    screen = pygame.display.set_mode(size, pygame.SRCALPHA)
    image_canvas = pygame.Surface(canvas_size, pygame.SRCALPHA)
    image_canvas.fill([80, 80, 80, 255])
    image_up_canvas = pygame.Surface(canvas_size, pygame.SRCALPHA)
    image_up_canvas.fill([80, 80, 80, 0])
    processor = ImageProcessor(image_canvas, image_up_canvas, canvas_offset)

    # button_bar
    up_button_bar = ButtonBar(color=[80, 80, 80], pos=(0, 0), size=(1280, 40))
    left_button_bar = ButtonBar(color=[80, 80, 80], pos=(0, 45), size=(40, 700))

    # image thumbnail focus bar
    im_focus_bar = FocusButtonBar(processor=processor, color=[80, 80, 80], pos=(1090, 100), size=(150, 600))

    # buttons
    button_register = Register()
    button_initialize(button_register, processor, im_focus_bar, args)

    # clock
    clock = pygame.time.Clock()

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            button_register.handleEvent(event)
            im_focus_bar.handleEvent(event)
            if processor.if_process():
                processor.process(event)

        if processor.if_refresh():
            processor.draw()
            processor.REFRESH = False

        if processor.confirm:
            processor.confirm = False
            button_register.element_dict["confirm"].visible = False
            button_register.element_dict["cancel"].visible = False
            button_register.element_dict["multiple"].visible = False
            button_register.element_dict["exclusive"].visible = False
            button_register.element_dict["input"].visible = False
        if processor.cancel:
            processor.confirm = False
            button_register.element_dict["confirm"].visible = False
            button_register.element_dict["cancel"].visible = False
            button_register.element_dict["multiple"].visible = False
            button_register.element_dict["exclusive"].visible = False
            button_register.element_dict["input"].visible = False

        # add object
        screen.fill(background)
        screen.blit(image_canvas, canvas_offset)
        screen.blit(image_up_canvas, canvas_offset)

        up_button_bar.draw(screen)
        left_button_bar.draw(screen)
        button_register.draw(screen)
        im_focus_bar.draw(screen)

        pygame.display.update()
        clock.tick(30)


if __name__ == "__main__":
    # parse arguments;
    parser = argparse.ArgumentParser(prog="PROG", description="digital image processing")
    parser.add_argument('--width', '-w', help='width', default=1280, type=int)
    parser.add_argument('--height', help='height', default=800, type=int)
    parser.add_argument('--background', '-b', help='background', default=[45, 45, 45], nargs=3, type=int)
    parser.add_argument('--canvas_size', '-c', help='canvas size', default=[950, 600], nargs=2, type=int)
    parser.add_argument('--image_directory', '-d', help='image_directory', default="./resources/images", type=str)
    parser.add_argument('--view_shape', '-v', help='image view shape', default=[400, 300], nargs=2, type=int)
    args = parser.parse_args()

    # start main loop
    main(args)
