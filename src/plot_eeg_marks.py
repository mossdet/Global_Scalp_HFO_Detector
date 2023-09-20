import numpy as np
import math
import matplotlib.pyplot as plt
from pynput import keyboard
from pynput.keyboard import Key, Listener


def plot_eeg_marks(eeg, marks):
    filename = eeg['filename']
    fs = eeg['fs']
    mtg_labels = eeg['mtg_labels']
    nr_mtgs = len(mtg_labels)
    data = eeg['data']
    nr_samples = eeg['n_samples']
    units = eeg['units']
    time = eeg['time_s']

    wi = 0
    wdw_dur_s = 10
    wdw_nr_samples = int(math.floor(wdw_dur_s * fs))

    wdw_start = np.arange(0, nr_samples, wdw_nr_samples)

    y_delta = np.abs(np.max(data[:]))

    fig, ax = plt.subplots()

    # for wi in range(0, len(wdw_start)):
    while 1:

        sample_start = wdw_start[wi]
        sample_end = sample_start + wdw_nr_samples
        wdw_data = data[:, sample_start:sample_end]
        wdw_time = time[sample_start:sample_end]

        # plot_eeg_wdw(filename, wdw_time, wdw_data, mtg_labels, y_delta)
        fn = filename
        wdw_data = np.flipud(wdw_data)
        mtg_labels = np.fliplr(mtg_labels)
        y_ticks = []
        ax.clear()
        for mi in range(0, nr_mtgs):
            ch_offset = y_delta * mi * 2
            y_ticks.append(ch_offset)
            signal = ch_offset + wdw_data[mi]
            ax.plot(wdw_time, signal, '-', color='black',  linewidth=0.5)

        textstr = str(round(y_delta*1000000)) + "uV"
        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        ax.text(0.95, 0.05, textstr, transform=ax.transAxes, fontsize=12,
                verticalalignment='top', bbox=props)

        ax.set_xlim(min(wdw_time), max(wdw_time))
        ax.set_yticks(y_ticks, labels=mtg_labels)
        ax.set_title(fn)
        plt.draw()
        plt.show(block=False)

        action = input("Type command: ")
        if action == '4':
            wi -= 1
            ax.clear()
            print('You Pressed left!')
        if action == '6':
            wi += 1
            ax.clear()
            print('You Pressed right!')
        if action == '2':
            y_delta += y_delta*0.1
            ax.clear()
            print('You Pressed down!')
        if action == '8':
            y_delta -= y_delta*0.1
            ax.clear()
            print('You Pressed up!')

        if wi < 0:
            wi = 0
        if wi > len(wdw_start)-1:
            wi = len(wdw_start)-1
