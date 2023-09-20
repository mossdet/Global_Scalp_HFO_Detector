import numpy as np
import math
import matplotlib.pyplot as plt

from matplotlib.widgets import Button
from fir_bp_filter import filter_data

filename = ""
time = []
data = []
bp_data = []
mtg_labels = []
y_delta_big = []
y_delta_small = []
nr_mtgs = []

wdw_start = []
wdw_nr_samples = 0

fig = []
ax_big = []
ax_small = []
ax_spctrm = []


def back_button(button):
    global wi
    wi -= 1
    plot_big_wdw()
    plot_small_wdw()


def fwd_button(button):
    global wi
    wi += 1
    plot_big_wdw()
    plot_small_wdw()


def dwn_button(button):
    global y_delta_big
    y_delta_big += y_delta_big*0.1
    plot_big_wdw()


def up_button(button):
    global y_delta_big
    y_delta_big -= y_delta_big*0.1
    plot_big_wdw()


def dwn_button_small(button):
    global y_delta_small
    y_delta_small += y_delta_small*0.1
    plot_small_wdw()


def up_button_small(button):
    global y_delta_small
    y_delta_small -= y_delta_small*0.1
    plot_small_wdw()


def plot_big_wdw():
    global filename, mtg_labels
    global time, data, y_delta_big, wdw_start, wdw_nr_samples, wi
    global ax_big

    nr_mtgs = len(mtg_labels)

    if wi < 0:
        wi = 0
    if wi > len(wdw_start)-1:
        wi = len(wdw_start)-1

    sample_start = wdw_start[wi]
    sample_end = sample_start + wdw_nr_samples
    wdw_data = data[:, sample_start:sample_end]
    wdw_time = time[sample_start:sample_end]

    wdw_data = np.flipud(wdw_data)
    mtg_labels = np.fliplr(mtg_labels)

    y_ticks = []
    ax_big.clear()
    for mi in range(0, nr_mtgs):
        ch_offset = y_delta_big * mi * 2
        y_ticks.append(ch_offset)
        signal = ch_offset + wdw_data[mi]
        ax_big.plot(wdw_time, signal, '-', color='black',  linewidth=0.5)

    textstr = str(round(y_delta_big*1000000)) + "uV"
    props = dict(boxstyle='round', facecolor='white', alpha=0.5)
    ax_big.text(0.9, 0.05, textstr, transform=ax_big.transAxes, fontsize=12,
                verticalalignment='top', bbox=props)

    ax_big.set_xlim(min(wdw_time), max(wdw_time))
    ax_big.set_yticks(y_ticks, labels=mtg_labels)
    ax_big.set_title(filename)
    plt.draw()


def plot_small_wdw():
    global filename, mtg_labels
    global time, bp_data, y_delta_small, wdw_start, wdw_nr_samples, wi
    global ax_small

    nr_mtgs = len(mtg_labels)

    if wi < 0:
        wi = 0
    if wi > len(wdw_start)-1:
        wi = len(wdw_start)-1

    sample_start = wdw_start[wi]
    sample_end = sample_start + wdw_nr_samples
    wdw_data = bp_data[:, sample_start:sample_end]
    wdw_time = time[sample_start:sample_end]

    wdw_data = np.flipud(wdw_data)
    mtg_labels = np.fliplr(mtg_labels)

    y_ticks = []
    ax_small.clear()
    for mi in range(0, nr_mtgs):
        ch_offset = y_delta_small * mi * 2
        y_ticks.append(ch_offset)
        signal = ch_offset + wdw_data[mi]
        ax_small.plot(wdw_time, signal, '-', color='black',  linewidth=0.5)

    textstr = str(round(y_delta_small*1000000)) + "uV"
    props = dict(boxstyle='round', facecolor='white', alpha=0.5)
    ax_small.text(0.9, 0.05, textstr, transform=ax_small.transAxes, fontsize=12,
                  verticalalignment='top', bbox=props)

    ax_small.set_xlim(min(wdw_time), max(wdw_time))
    ax_small.set_yticks(y_ticks, labels=mtg_labels)
    ax_small.set_title(filename)
    plt.draw()


def plot_eeg_marks(eeg, marks):
    global filename, mtg_labels, time, data, bp_data
    global y_delta_big, y_delta_small, wdw_start, wdw_nr_samples, wi
    global fig, ax_big, ax_small, ax_spctrm

    filename = eeg['filename']
    fs = eeg['fs']
    mtg_labels = eeg['mtg_labels']
    nr_mtgs = len(mtg_labels)
    data = eeg['data']
    nr_samples = eeg['n_samples']
    units = eeg['units']
    time = eeg['time_s']

    bp_data = filter_data(fs, data, 80, 500)

    wi = 0
    wdw_dur_s = 10
    wdw_nr_samples = int(math.floor(wdw_dur_s * fs))
    wdw_start = np.arange(0, nr_samples, wdw_nr_samples)
    y_delta_big = np.abs(np.max(data[:]))
    y_delta_small = np.abs(np.max(bp_data[:]))

    plt.close()
    fig = plt.figure(figsize=(6, 6))

    ax_big = fig.add_axes([0.05, 0.1, 0.45, 0.85])
    ax_small = fig.add_axes([0.55, 0.1, 0.43, 0.85])
    # ax_spctrm = fig.add_axes([0.02, 0.1, 0.5, 0.8])

    axprev = fig.add_axes([0.45, 0.02, 0.05, 0.05])
    axnext = fig.add_axes([0.5, 0.02, 0.05, 0.05])
    axdown_big = fig.add_axes([0.2, 0.02, 0.05, 0.05])
    axup_big = fig.add_axes([0.25, 0.02, 0.05, 0.05])
    ax_down_small = fig.add_axes([0.7, 0.02, 0.05, 0.05])
    ax_up_small = fig.add_axes([0.75, 0.02, 0.05, 0.05])

    bnext = Button(axnext, '>>')
    bnext.on_clicked(fwd_button)
    bprev = Button(axprev, '<<')
    bprev.on_clicked(back_button)

    bdown = Button(axdown_big, '-')
    bdown.on_clicked(dwn_button)
    bup = Button(axup_big, '+')
    bup.on_clicked(up_button)

    bdown_small = Button(ax_down_small, '-')
    bdown_small.on_clicked(dwn_button_small)
    bup_small = Button(ax_up_small, '+')
    bup_small.on_clicked(up_button_small)

    plot_big_wdw()
    plot_small_wdw()

    plt.show(block=True)


"""     action = ""
    while action != "exit":
        stop = 1
        # action = input("Exit(exit)? ")
 """
