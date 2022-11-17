import numpy as np


def downsample(img, height):
    '''
    Downsample 2d array using fourier transform.
    factor is the downsample factor.
    '''
    m, n = img.shape[-2:]
    ds_factor = m / height
    width = int(n / ds_factor / 2) * 2
    F = np.fft.rfft2(img)
    A = F[..., 0:height // 2, 0:width // 2 + 1]
    B = F[..., -height // 2:, 0:width // 2 + 1]
    F = np.concatenate([A, B], axis=0)
    f = np.fft.irfft2(F, s=(height, width))
    return f
