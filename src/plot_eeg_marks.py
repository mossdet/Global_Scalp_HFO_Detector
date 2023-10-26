import numpy as np
import math
import matplotlib.pyplot as plt

from matplotlib.widgets import Button
from matplotlib.patches import Rectangle
from matplotlib.ticker import AutoMinorLocator
from dsp_tools import get_cmwt

from fir_bp_filter import filter_data

filename = ""
time = []
data = []
fs = 0
bp_data = []
cmwt_data = []
mtg_labels = []
y_delta_big = []
y_ticks_big = []
y_delta_small = []
y_ticks_small = []

wdw_start = []
wdw_nr_samples = 0
small_wdw_nr_samples = 0
spctrm_chidx = 0

fig = []
ax_big = []
ax_small = []
ax_spctrm = []

hfo = []
artefacts = []


def refresh_plots():
    plot_big_wdw()
    plot_small_wdw()
    plot_events_big_wdw()
    plot_events_small_wdw()


def back_button_big(button):
    global wi
    wi -= 1
    refresh_plots()
    plot_spctrm_wdw()


def fwd_button_big(button):
    global wi
    wi += 1
    refresh_plots()
    plot_spctrm_wdw()


def dwn_button_big(button):
    global y_delta_big
    y_delta_big += y_delta_big*0.1
    refresh_plots()


def up_button_big(button):
    global y_delta_big
    y_delta_big -= y_delta_big*0.1
    refresh_plots()


def back_button_small(button):
    global wi
    wi -= 1
    refresh_plots()
    plot_spctrm_wdw()


def fwd_button_small(button):
    global wi
    wi += 1
    refresh_plots()
    plot_spctrm_wdw()


def dwn_button_small(button):
    global y_delta_small
    y_delta_small += y_delta_small*0.1
    refresh_plots()


def up_button_small(button):
    global y_delta_small
    y_delta_small -= y_delta_small*0.1
    refresh_plots()


def button_spctrm_ch_up(button):
    global spctrm_chidx
    spctrm_chidx += 1
    if spctrm_chidx > len(mtg_labels)-1:
        spctrm_chidx = len(mtg_labels)-1
    plot_spctrm_wdw()


def button_spctrm_ch_down(button):
    global spctrm_chidx
    spctrm_chidx -= 1
    if spctrm_chidx < 0:
        spctrm_chidx = 0
    plot_spctrm_wdw()


def plot_big_wdw():
    global filename, mtg_labels
    global time, data, y_delta_big, y_ticks_big, wdw_start, wdw_nr_samples, wi
    global fig, ax_big

    nr_mtgs = len(mtg_labels)

    if wi < 0:
        wi = 0
    if wi > len(wdw_start)-1:
        wi = len(wdw_start)-1

    sample_start = wdw_start[wi]
    sample_end = sample_start + wdw_nr_samples
    wdw_data = data[:, sample_start:sample_end]
    wdw_time = time[sample_start:sample_end]

    y_ticks_big = []
    ax_big.clear()
    for mi in range(0, nr_mtgs):
        ch_offset = y_delta_big * mi * 2
        y_ticks_big.append(ch_offset)
        signal = ch_offset + wdw_data[mi]
        ax_big.plot(wdw_time, signal, '-', color='black',  linewidth=0.5)

    textstr = str(round(y_delta_big*1000000)) + "uV"
    props = dict(boxstyle='round', facecolor='white', alpha=0.5)
    ax_big.text(0.9, 0.05, textstr, transform=ax_big.transAxes, fontsize=12,
                verticalalignment='top', bbox=props)

    time_step = np.floor(np.abs(np.mean(np.diff(wdw_time))))
    x_ticks_vals = np.arange(wdw_time[0], wdw_time[-1]+time_step, 1)
    ax_big.set_xticks(x_ticks_vals)
    ax_big.set_xlim(min(wdw_time), max(wdw_time))
    ax_big.set_yticks(y_ticks_big, labels=mtg_labels)
    ax_big.set_title(filename)

    ax_big.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax_big.grid(True, 'both', 'x', color='g', linestyle='--', linewidth=0.5)
    plt.draw()


def plot_events_big_wdw():
    global filename, mtg_labels
    global time, data, y_delta_big, y_ticks_big, wdw_start, wdw_nr_samples, wi
    global fig, ax_big
    global marks, artefacts

    nr_mtgs = len(mtg_labels)

    sample_start = wdw_start[wi]
    sample_end = sample_start + wdw_nr_samples
    wdw_start_s = time[sample_start]
    wdw_end_s = time[sample_end]

    for mi in range(0, nr_mtgs):
        mtg_name = mtg_labels[mi]
        ch_sel = marks['channel'] == mtg_name.lower()
        wdw_sel = np.logical_and(
            (marks['start_s'] >= wdw_start_s), (marks['start_s'] <= wdw_end_s))

        hfo_sel = np.logical_and(ch_sel, wdw_sel)

        chann_hfo = {key: value[hfo_sel]
                     for key, value in marks.items()}
        nr_events = len(chann_hfo['channel'])

        if mtg_name == "T5-O1":
            stop = 1

        for ei in range(0, nr_events):
            ss = chann_hfo['start'][ei]
            se = chann_hfo['end'][ei]
            event_name = chann_hfo['type'][ei]
            ch_offset = y_delta_big * mi * 2
            hfo_signal = ch_offset + data[mi, ss:se]
            hfo_time = time[ss:se]

            inter_y = np.abs(np.mean(np.diff(y_ticks_big)))
            rect_w = hfo_time[-1]-hfo_time[0]
            if rect_w < 0.02:
                rect_w = 0.02
            rect_h = (inter_y/3)*2
            rect = plt.Rectangle((hfo_time[0], ch_offset-inter_y/3), rect_w, rect_h,
                                 facecolor="red", alpha=0.7)
            ax_big.add_patch(rect)

            stop = 1

    plt.draw()


def plot_small_wdw():
    global filename, mtg_labels
    global time, bp_data, y_delta_small, y_ticks_small, wdw_start, small_wdw_nr_samples, wi
    global fig, ax_small

    nr_mtgs = len(mtg_labels)

    if wi < 0:
        wi = 0
    if wi > len(wdw_start)-1:
        wi = len(wdw_start)-1

    sample_start = wdw_start[wi]
    sample_end = sample_start + small_wdw_nr_samples
    wdw_data = bp_data[:, sample_start:sample_end]
    wdw_time = time[sample_start:sample_end]

    y_ticks_small = []
    ax_small.clear()
    for mi in range(0, nr_mtgs):
        ch_offset = y_delta_small * mi * 2
        y_ticks_small.append(ch_offset)
        signal = ch_offset + wdw_data[mi]
        ax_small.plot(wdw_time, signal, '-', color='black',  linewidth=0.5)

    textstr = str(round(y_delta_small*1000000)) + "uV"
    props = dict(boxstyle='round', facecolor='white', alpha=0.5)
    ax_small.text(0.9, 0.05, textstr, transform=ax_small.transAxes, fontsize=12,
                  verticalalignment='top', bbox=props)

    ax_small.set_xlim(min(wdw_time), max(wdw_time))
    ax_small.set_yticks(y_ticks_small, labels=mtg_labels)
    ax_small.set_title(filename)

    ax_small.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax_small.grid(True, 'both', 'x', color='g', linestyle='--', linewidth=0.5)
    plt.draw()


def plot_events_small_wdw():
    global filename, mtg_labels
    global time, bp_data, y_delta_small, wdw_start, small_wdw_nr_samples, wi
    global fig, ax_small
    global marks, artefacts

    nr_mtgs = len(mtg_labels)

    sample_start = wdw_start[wi]
    sample_end = sample_start + small_wdw_nr_samples
    wdw_start_s = time[sample_start]
    wdw_end_s = time[sample_end]

    for mi in range(0, nr_mtgs):
        mtg_name = mtg_labels[mi]
        ch_sel = marks['channel'] == mtg_name.lower()
        wdw_sel = np.logical_and(
            (marks['start_s'] >= wdw_start_s), (marks['start_s'] <= wdw_end_s))

        hfo_sel = np.logical_and(ch_sel, wdw_sel)

        chann_hfo = {key: value[hfo_sel]
                     for key, value in marks.items()}
        nr_events = len(chann_hfo['channel'])

        for ei in range(0, nr_events):
            ss = chann_hfo['start'][ei]
            se = chann_hfo['end'][ei]
            event_name = chann_hfo['type'][ei]
            ch_offset = y_delta_small * mi * 2
            hfo_signal = ch_offset + bp_data[mi, ss:se]
            hfo_time = time[ss:se]

            inter_y = np.abs(np.mean(np.diff(y_ticks_small)))
            rect_w = hfo_time[-1]-hfo_time[0]
            if rect_w < 0.02:
                rect_w = 0.02
            rect_h = (inter_y/3)*2
            rect = plt.Rectangle((hfo_time[0], ch_offset-inter_y/3), rect_w, rect_h,
                                 facecolor="red", alpha=0.7)
            ax_small.add_patch(rect)

    plt.draw()


def plot_spctrm_wdw():
    global filename, fs, mtg_labels
    global time, data, wdw_start, small_wdw_nr_samples, wi, spctrm_chidx
    global fig, ax_spctrm

    data_len = np.shape(data)[1]

    if wi < 0:
        wi = 0
    if wi > len(wdw_start)-1:
        wi = len(wdw_start)-1

    start_pad = int(2*fs)
    end_pad = int(2*fs)
    sample_start = int(wdw_start[wi] - start_pad)
    sample_end = int(wdw_start[wi] + small_wdw_nr_samples + end_pad)
    if sample_start < 0:
        sample_start = wdw_start[wi]
        start_pad = 0
    if sample_end > data_len-1:
        sample_end = wdw_start[wi] + small_wdw_nr_samples
        end_pad = 0

    wdw_data = data[spctrm_chidx, sample_start:sample_end]

    freqs = np.arange(70, 510, 5)
    freqs, cmwtm = get_cmwt(wdw_data, fs, freqs, nr_cycles=7)

    # remove befor and after data pads
    sample_start += start_pad
    sample_end -= end_pad
    wdw_time = time[sample_start:sample_end]
    loc_wdw_s = start_pad
    loc_wdw_e = np.shape(cmwtm)[1]-end_pad
    cmwtm = cmwtm[:, loc_wdw_s:loc_wdw_e]

    ax_spctrm.clear()
    ax_spctrm.pcolormesh(wdw_time, freqs, cmwtm,
                         cmap='viridis', shading='gouraud')

    ax_spctrm.set_title(mtg_labels[spctrm_chidx])

    plt.draw()


def plot_eeg_marks(eeg, hfo_marks, artefact_marks):
    global filename, fs, mtg_labels, time, data, bp_data, cmwt_data
    global y_delta_big, y_delta_small, wdw_start, wdw_nr_samples, small_wdw_nr_samples, wi, spctrm_chidx
    global fig, ax_big, ax_small, ax_spctrm
    global marks, artefacts

    marks = hfo_marks
    artefacts = artefact_marks

    filename = eeg['filename']
    fs = eeg['fs']
    mtg_labels = eeg['mtg_labels']
    nr_mtgs = len(mtg_labels)
    data = eeg['data']
    nr_samples = eeg['n_samples']
    units = eeg['units']
    time = eeg['time_s']

    data = np.flipud(data)
    mtg_labels = np.flip(mtg_labels)

    bp_data = filter_data(fs, data, 80, 500)

    wi = 0
    wdw_dur_s = 10
    small_wdw_dur_s = 10
    wdw_nr_samples = int(math.floor(wdw_dur_s * fs))
    small_wdw_nr_samples = int(math.floor(small_wdw_dur_s * fs))
    wdw_start = np.arange(0, nr_samples, wdw_nr_samples)
    y_delta_big = np.abs(np.max(data[:]))/10
    y_delta_small = np.abs(np.max(bp_data[:]))/10
    spctrm_chidx = 0

    plt.close()
    fig = plt.figure(figsize=(6, 6))

    # Add panels to figure
    ax_big = fig.add_axes([0.05, 0.1, 0.45, 0.85])
    ax_big.set_facecolor([0.86275, 0.98039, 0.86275])
    ax_small = fig.add_axes([0.55, 0.5, 0.43, 0.45])
    ax_small.set_facecolor([0.86275, 0.98039, 0.86275])
    ax_spctrm = fig.add_axes([0.55, 0.1, 0.43, 0.35])

    # Big Wdw Buttons
    axdown_big = fig.add_axes([0.1, 0.02, 0.05, 0.05])
    axup_big = fig.add_axes([0.15, 0.02, 0.05, 0.05])
    axprev_big = fig.add_axes([0.25, 0.02, 0.05, 0.05])
    axnext_big = fig.add_axes([0.30, 0.02, 0.05, 0.05])

    bprev = Button(axprev_big, '<<')
    bprev.on_clicked(back_button_big)
    bnext = Button(axnext_big, '>>')
    bnext.on_clicked(fwd_button_big)

    bdown = Button(axdown_big, '-')
    bdown.on_clicked(dwn_button_big)
    bup = Button(axup_big, '+')
    bup.on_clicked(up_button_big)

    # Small Wdw Buttons
    ax_down_small = fig.add_axes([0.65, 0.02, 0.05, 0.05])
    ax_up_small = fig.add_axes([0.70, 0.02, 0.05, 0.05])
    axprev_small = fig.add_axes([0.8, 0.02, 0.05, 0.05])
    axnext_small = fig.add_axes([0.85, 0.02, 0.05, 0.05])

    bprev = Button(axprev_small, '<<')
    bprev.on_clicked(back_button_small)
    bnext = Button(axnext_small, '>>')
    bnext.on_clicked(fwd_button_small)

    bdown_small = Button(ax_down_small, '-')
    bdown_small.on_clicked(dwn_button_small)
    bup_small = Button(ax_up_small, '+')
    bup_small.on_clicked(up_button_small)

    # Spectrogramm buttons
    ax_spctrm_ch_up = fig.add_axes([0.95, 0.04, 0.02, 0.015])
    ax_spctrm_ch_dwn = fig.add_axes([0.95, 0.02, 0.02, 0.015])
    spctrm_ch_up = Button(ax_spctrm_ch_up, 'ʌ')
    spctrm_ch_up.on_clicked(button_spctrm_ch_up)
    spctrm_ch_dwn = Button(ax_spctrm_ch_dwn, 'v')
    spctrm_ch_dwn.on_clicked(button_spctrm_ch_down)

    plot_big_wdw()
    plot_small_wdw()
    plot_spctrm_wdw()

    plot_events_big_wdw()
    plot_events_small_wdw()

    plt.show(block=True)
