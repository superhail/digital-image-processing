import numpy as np
import cv2
import matplotlib.pyplot as plt
import scipy.fftpack as fftpack


# Derivative's Fourier transform
# dxx
def get_dxx(size):
    width = size[1]
    height = size[0]
    matrix = np.zeros((height, width))
    matrix[height//2-1, width//2-1] = 1
    matrix[height//2-1, width//2] = -2
    matrix[height//2-1, width//2+1] = 1
    dft = cv2.dft(matrix, flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = fftpack.fftshift(dft)
    comp = dft_shift[:, :, 0] + 1j * dft_shift[:, :, 1]

    return comp


def get_dyy(size):
    width = size[1]
    height = size[0]
    matrix = np.zeros((height, width))
    matrix[height//2-1, width//2-1] = 1
    matrix[height//2, width//2-1] = -2
    matrix[height//2+1, width//2-1] = 1
    dft = cv2.dft(matrix, flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = fftpack.fftshift(dft)
    comp = dft_shift[:, :, 0] + 1j * dft_shift[:, :, 1]

    return comp


def get_dxy(size):
    width = size[1]
    height = size[0]
    matrix = np.zeros((height, width))
    matrix[height//2-1, width//2-1] = 1
    matrix[height//2-1, width//2] = -1
    matrix[height//2, width//2] = -1
    matrix[height//2, width//2+1] = 1
    dft = cv2.dft(matrix, flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = fftpack.fftshift(dft)
    comp = dft_shift[:, :, 0] + 1j * dft_shift[:, :, 1]

    return comp


def get_dx(size):
    width = size[1]
    height = size[0]
    matrix = np.zeros((height, width))
    matrix[height//2-1, width//2-1] = -1
    matrix[height//2-1, width//2] = 1
    dft = cv2.dft(matrix, flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = fftpack.fftshift(dft)
    comp = dft_shift[:, :, 0] + 1j * dft_shift[:, :, 1]

    return comp


def get_dy(size):
    width = size[1]
    height = size[0]
    matrix = np.zeros((height, width))
    matrix[height//2-1, width//2-1] = -1
    matrix[height//2, width//2-1] = 1
    dft = cv2.dft(matrix, flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = fftpack.fftshift(dft)
    comp = dft_shift[:, :, 0] + 1j * dft_shift[:, :, 1]

    return comp


def edgetaper(im: np.ndarray, gamma, beta):
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


def mat2gray(im):
    cv2.normalize(im, im, 1.0, 0.0, cv2.NORM_MINMAX)


def gray2mat(im):
    out = np.empty_like(im)
    cv2.normalize(im, out, 255.0, 0.0, cv2.NORM_MINMAX)
    return out


# Image = Latent * PSF + Noise
iterations = 10
threshold = 5
im = cv2.imread("./../../resources/images/blur_2.png")
im = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
# im = edgetaper(im, 5.0, 0.2)
im = im.astype(np.float32)
# mat2gray(im)


def compute_smooth_mask(im, threshold=5):
    '''
    :param im: pixels in range(0, 255)
    :param threshold: 5
    :return: smooth_mask
    '''
    kernel_size = im.shape[:2]
    kernel_size = (x // 20 for x in kernel_size)
    kernel_size = tuple([x if x % 2 == 1 else x+1 for x in kernel_size])
    blurred = cv2.blur(im, kernel_size)
    std = cv2.blur(np.power(im, 2), kernel_size) - np.power(blurred, 2)
    mask = np.zeros(im.shape)
    mask[std < threshold] = 1.0
    np.max(std)

    return mask


def log_gradient_distribution(x):
    piece_1 = -2.7 * np.abs(x)
    piece_2 = -6.1*1e-4*(x**2)-5
    ret = piece_1.copy()
    ret[piece_1 < piece_2] = piece_2[piece_1 < piece_2]

    return ret


def deriv_log_gradient_distribution(x):
    ret = np.empty_like(x)
    index_less = np.abs(x) < 1.852627281
    index_more = np.abs(x) >= 1.852627281
    ret[index_less] = 2.7
    ret[index_more] = -2 * 6.1 * 1e-4 * np.abs(x[index_more])
    ret[x < 0] *= -1

    return ret


def update_phi(I_sobel, L_sobel, lambda_1, lambda_2, gamma, mask):
    phi_1 = 2 * (lambda_2 * mask * I_sobel + gamma * L_sobel) / (2 * lambda_2 * mask + 1.26e-3 + 2 * gamma)
    phi_1 = np.clip(phi_1, None, -1.852627281)
    phi_2 = 2 * (lambda_2 * mask * I_sobel + gamma * L_sobel) + 2.7 / (2 * lambda_2*mask + 2 * gamma)
    phi_2 = np.clip(phi_2, -1.852627281, 0)
    phi_3 = 2 * (lambda_2 * mask * I_sobel + gamma * L_sobel) - 2.7 / (2 * lambda_2*mask + 2 * gamma)
    phi_3 = np.clip(phi_3, 0, 1.852627281)
    phi_4 = 2 * (lambda_2 * mask * I_sobel + gamma * L_sobel) / (2 * lambda_2 * mask + 1.26e-3 + 2 * gamma)
    phi_4 = np.clip(phi_4, 1.852627281, None)

    phi = np.stack([phi_1, phi_2, phi_3, phi_4], 2)
    energy = lambda_1 * (- log_gradient_distribution(phi)) + \
             lambda_2 * mask * ((phi - I_sobel[:, :, None])**2) + \
             gamma * ((phi - L_sobel[:, :, None])**2)
    min_index = np.argmin(energy, 2)
    a = np.reshape(np.arange(energy.size), energy.shape) % energy.shape[2]
    min_mask = (min_index[:, :, None] == a)

    updated_phi = np.sum(min_mask * phi, 2)

    return updated_phi


def update_L(I_DFT, f_DFT, gamma, phi_x_DFT, phi_y_DFT, delta, dx_DFT, dy_DFT):
    numerator = np.conjugate(f_DFT)*I_DFT*delta + gamma*np.conjugate(dx_DFT)*phi_x_DFT + \
                gamma*np.conjugate(dy_DFT)*phi_y_DFT
    denominator = np.conjugate(f_DFT)*f_DFT*delta + gamma*np.conjugate(dx_DFT)*phi_x_DFT + \
                  gamma*np.conjugate(dy_DFT)*phi_y_DFT
    optimal_L = np.fft.ifft2(numerator / denominator)
    optimal_L = np.real(optimal_L)

    return optimal_L


def update_f():
    pass


if __name__ == "__main__":
    latent = im
    height, width = im.shape
    for epoch in range(iterations):
        smooth_mask = compute_smooth_mask(im, threshold)
        # TODO
        # optimize L and f
            # optimize latent, update psi
            # until L2 < 1e-5, phi2 < 1e-5
        # until f2 < 1e-5 or the max iterations have been performed
        # return L, f