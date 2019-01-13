from processor.tools.basetool import BaseTool
import pygame
import cv2
import scipy.fftpack as fftpack
import numpy as np
import matplotlib.pyplot as plt
from skimage import color, data, restoration
from scipy.signal import convolve2d


class MotionDeblur(BaseTool):
    def __init__(self):
        super().__init__()

    def process(self, processor, event: pygame.event):
        focus = processor.focus
        if processor.confirm:
            raw_data = focus.raw_data[:, :, :3]
            LEN, THETA, SNR = np.int32(processor.text.split(","))
            gray = cv2.cvtColor(np.float32(raw_data), cv2.COLOR_RGB2GRAY)
            psf = self.cal_psf(gray.shape[:2], LEN, THETA)
            wnr_filter = self.cal_wnr_filter(psf, 1.0 / 300)
            im = [self.edgetaper(raw_data[:, :, channel], 5.0, 0.2) for channel in range(3)]
            out = [self.filter_2d_frequency(im[channel], wnr_filter) for channel in range(3)]
            out = cv2.merge([np.clip(out[channel], 0, 255) for channel in range(3)])

            focus.raw_data[:, :, :3] = out.astype(np.uint8)
            focus.construct_surface()
            processor.REFRESH = True
            processor.PROCESS = False
        if processor.cancel:
            focus.construct_surface()
            processor.REFRESH = True
            processor.PROCESS = False


    def cal_psf(self, shape, len, angle):
        psf = np.zeros(shape)
        center = (psf.shape[1] // 2, psf.shape[0] // 2)
        cv2.ellipse(psf, center, (0, len // 2), 90 - angle, 0, 360, (255,), -1)
        summa = np.sum(psf)
        psf = psf / summa

        return psf

    def filter_2d_frequency(self, im: np.ndarray, H: np.ndarray):
        planes = [im.copy().astype(np.float32), np.zeros(H.shape, np.float32)]
        complexI = cv2.merge(planes)
        cv2.dft(complexI, complexI, cv2.DFT_SCALE)

        planesH = [H.copy().astype(np.float32), np.zeros(H.shape, np.float32)]
        complexH = cv2.merge(planesH)
        complexIH = cv2.mulSpectrums(complexI, complexH, 0)

        cv2.idft(complexIH, complexIH)
        planes = cv2.split(complexIH)

        return planes[0]

    def cal_wnr_filter(self, input_h_psf, nsr):
        h_psf_shifted = fftpack.fftshift(input_h_psf)
        planes = [h_psf_shifted.copy().astype(np.float32), np.zeros(h_psf_shifted.shape, np.float32)]
        complexI = cv2.merge(planes)
        cv2.dft(complexI, complexI)
        planes = cv2.split(complexI)
        denom = np.power(np.abs(planes[0]), 2)
        denom += nsr
        output_G = np.divide(planes[0], denom)

        return output_G

    def edgetaper(self, im: np.ndarray, gamma, beta):
        Nx = im.shape[1]
        Ny = im.shape[0]
        w1 = np.zeros((1, Nx), np.float32)
        w2 = np.zeros((Ny, 1), np.float32)
        dx = 2.0 * np.pi / Nx
        x = -np.pi
        for i in range(Nx):
            w1[0, i] = 0.5 * (np.tanh((x + gamma / 2) / beta) - np.tanh((x - gamma / 2) / beta))
            x += dx
        dy = 2.0 * np.pi / Ny
        y = -np.pi
        for i in range(Ny):
            w2[i, 0] = 0.5 * (np.tanh((y + gamma / 2) / beta) - np.tanh((y - gamma / 2) / beta))
            y += dy

        w = np.matmul(w2, w1)

        output = np.multiply(im, w)

        return output


def make_odd(x):
    return x if x % 2 == 1 else x+1


def crop_transparent_edge(pixel_array):
    index = np.argwhere(pixel_array[:, :] != 0)
    x0, y0 = index.min(axis=0)
    x1, y1 = index.max(axis=0)
    assert x0 != x1
    assert y0 != y1
    pixel_array = pixel_array[x0:x1, y0:y1]

    return pixel_array


if __name__ == "__main__":
    raw_im = cv2.imread("../../resources/images/blur_.jpg")
    LEN = 17
    THETA = 0
    SNR = 70
    new_width = make_odd(raw_im.shape[1])
    new_height = make_odd(raw_im.shape[0])
    im = np.zeros((new_height, new_width, raw_im.shape[2]))
    im[:raw_im.shape[0], :raw_im.shape[1], :] = raw_im[:, :, :]
    im = cv2.cvtColor(np.float32(im), cv2.COLOR_RGB2GRAY)
    handler = MotionDeblur()
    psf = handler.cal_psf(im.shape[:2], LEN, THETA)
    plt.subplot(151)
    plt.imshow((psf * 255).astype(np.uint8), cmap='gray')
    wnr_filter = handler.cal_wnr_filter(psf, 1.0 / 300)
    im = handler.edgetaper(im, 5.0, 0.2)
    out = handler.filter_2d_frequency(im, wnr_filter)
    out = np.clip(out, 0, 255).astype(np.uint8)
    plt.subplot(152)
    plt.imshow(out, cmap='gray')
    plt.subplot(153)
    plt.imshow(raw_im, cmap='gray')
    plt.show()
