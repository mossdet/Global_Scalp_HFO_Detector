import numpy as np
from scipy.signal import kaiserord, lfilter, firwin, freqz


def filter_data(fs, data, lowcut, highcut):
    nr_rows = data.shape[0]
    ntaps = 256
    window = 'hamming'  # 'blackmanharris', 'blackmanharris'
    taps = firwin(ntaps, [lowcut, highcut], fs=fs, pass_zero=False,
                  window=window, scale=False)

    fltrd_data = data.copy()

    for chi in range(0, nr_rows):
        signal = data[chi]
        fltrd_sig = lfilter(taps, 1.0, np.flip(signal))
        fltrd_sig = lfilter(taps, 1.0, np.flip(fltrd_sig))
        fltrd_data[chi] = fltrd_sig

    return fltrd_data
