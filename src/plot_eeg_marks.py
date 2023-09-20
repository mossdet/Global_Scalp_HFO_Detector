import numpy as np
import math
import matplotlib.pyplot as plt
from pynput import keyboard
from pynput.keyboard import Key

y_delta = 0


def on_key_release(key):
    if key == Key.right:
        print("Right key clicked")
    elif key == Key.left:
        print("Left key clicked")
    elif key == Key.up:
        y_delta /= 2
        print("Up key clicked")
    elif key == Key.down:
        y_delta *= 2
        print("Down key clicked")
    elif key == Key.esc:
        exit()


def plot_eeg_wdw(fn, time, data, mtg_labels, y_delta):
    data = np.flipud(data)
    mtg_labels = np.fliplr(mtg_labels)
    y_ticks = []
    nr_mtgs = len(mtg_labels)

    for mi in range(0, nr_mtgs):
        ch_offset = y_delta * mi * 2
        y_ticks.append(ch_offset)
        signal = ch_offset + data[mi]
        plt.plot(time, signal, '-', color='black',  linewidth=0.5)

    plt.xlim(min(time), max(time))
    plt.yticks(y_ticks, labels=mtg_labels)
    plt.title(fn)
    plt.show(block=False)


def plot_eeg_marks(eeg, marks):
    filename = eeg['filename']
    fs = eeg['fs']
    mtg_labels = eeg['mtg_labels']
    nr_mtgs = len(mtg_labels)
    data = eeg['data']
    nr_samples = eeg['n_samples']
    units = eeg['units']
    time = eeg['time_s']

    with keyboard.Listener(on_release=on_key_release) as listener:
        listener.join()

    wdw_dur_s = 10
    wdw_nr_samples = int(math.floor(wdw_dur_s * fs))

    wdw_start = np.arange(0, nr_samples, wdw_nr_samples)

    y_delta = np.abs(np.max(data[:]))

    # for wi in range(0, len(wdw_start)):
    wi = 0
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
        for mi in range(0, nr_mtgs):
            ch_offset = y_delta * mi * 2
            y_ticks.append(ch_offset)
            signal = ch_offset + wdw_data[mi]
            plt.plot(wdw_time, signal, '-', color='black',  linewidth=0.5)

        plt.xlim(min(wdw_time), max(wdw_time))
        plt.yticks(y_ticks, labels=mtg_labels)
        plt.title(fn)
        plt.show(block=False)

        action = input("Type command: ")
        if action == '4':
            wi -= 1
            if wi < 0:
                wi = 0
            plt.clf()
            print('You Pressed left!')
        if action == '6':
            wi += 1
            if wi > len(wdw_start)-1:
                wi = len(wdw_start)-1
            plt.clf()
            print('You Pressed right!')
        if action == '2':
            y_delta *= 2
            plt.clf()
            print('You Pressed down!')
        if action == '8':
            y_delta /= 2
            plt.clf()
            print('You Pressed up!')
