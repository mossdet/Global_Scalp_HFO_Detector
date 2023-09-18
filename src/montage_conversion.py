import numpy as np
import matplotlib.pyplot as plt
import mne
import os

SCALP_LONG_BIP = ['Fp1-F7', 'F7-T7', 'T7-P7', 'P7-O1', 'F7-T3', 'T3-T5', 'T5-O1',
                  'Fp2-F8', 'F8-T8', 'T8-P8', 'P8-O2', 'F8-T4', 'T4-T6', 'T6-O2', 'Fp1-F3', 'F3-C3', 'C3-P3',
                  'P3-O1', 'Fp2-F4', 'F4-C4', 'C4-P4', 'P4-O2', 'FZ-CZ', 'CZ-PZ']


def convert_to_long_bipolar(eeg_data, plot_ok=False):
    print(eeg_data)
    print(eeg_data.info)

    data = eeg_data.get_data()
    n_time_samps = eeg_data.n_times
    time_secs = np.array(eeg_data.times)
    ch_names = eeg_data.ch_names
    ch_names_low = [chn.lower() for chn in ch_names]
    n_chan = len(ch_names)
    units = eeg_data.__dict__['_orig_units']
    fs = eeg_data.info["sfreq"]
    filename = eeg_data.filenames[0].split(os.path.sep)[-1]

    scalp_bp_eeg = {'filename': filename,
                    'fs': fs,
                    'mtg_labels': np.array([]),
                    'data': np.array([]),
                    'n_samples': data.shape[1],
                    'units': units[ch_names[0]],
                    'time_s': time_secs
                    }

    for bip_mtg in SCALP_LONG_BIP:
        bip_mtg_parts = bip_mtg.split('-')
        bip_mtg_parts = [mtgname.lower() for mtgname in bip_mtg_parts]

        try:
            ch_1_idx = ch_names_low.index(bip_mtg_parts[0])
        except:
            print(f"Channel {bip_mtg_parts[0]} not found in EEG")
            continue

        try:
            ch_2_idx = ch_names_low.index(bip_mtg_parts[1])
        except:
            print(f"Channel {bip_mtg_parts[1]} not found in EEG")
            continue

        ch_to_plot_name = ch_names[ch_1_idx] + "-" + ch_names[ch_2_idx]
        signal_to_plot = np.array(data[ch_1_idx] - data[ch_2_idx])*-1

        if len(scalp_bp_eeg['data']) == 0:
            scalp_bp_eeg['mtg_labels'] = ch_to_plot_name
            scalp_bp_eeg['data'] = signal_to_plot
        else:
            scalp_bp_eeg['mtg_labels'] = np.vstack(
                (scalp_bp_eeg['mtg_labels'], np.array(ch_to_plot_name)))
            scalp_bp_eeg['data'] = np.vstack(
                (scalp_bp_eeg['data'], signal_to_plot))

        if plot_ok:

            sample_sel = (time_secs >= 0) & (time_secs <= 10)

            # Plot signals
            left_color = [0, 0.45, 0.74]
            right_color = [0.93, 0.7, 0.13]

            fig, axs = plt.subplots(1, 3, figsize=(16, 9))
            fig.suptitle(filename + "\n" +
                         "Physical Montage vs Scalp_Long_Bipolar Montage")
            sig_lw = 0.5

            plt_ax = axs[0]
            time_to_plot = time_secs[sample_sel]
            signal_to_plot = data[ch_1_idx][sample_sel]
            signal_to_plot *= -1
            ch_to_plot_name = ch_names[ch_1_idx]
            units_str = units[ch_to_plot_name]

            plt_ax.plot(time_to_plot, signal_to_plot,
                        '-', color='black', linewidth=sig_lw)
            plt_ax.set_title(ch_to_plot_name)
            plt_ax.set_xlim(min(time_to_plot), max(time_to_plot))
            plt_ax.set_ylim(min(signal_to_plot), max(signal_to_plot))
            plt_ax.set_ylabel(f"Amplitude ({units_str})")
            plt_ax.set_xlabel("Time (s)")
            plt_ax.legend(["Channel 1"], loc='upper right')

            plt_ax = axs[1]
            time_to_plot = time_secs[sample_sel]
            signal_to_plot = data[ch_2_idx][sample_sel]
            signal_to_plot *= -1
            ch_to_plot_name = ch_names[ch_2_idx]
            units_str = units[ch_to_plot_name]

            plt_ax.plot(time_to_plot, signal_to_plot, '-',
                        color='black', linewidth=sig_lw)
            plt_ax.set_title(ch_to_plot_name)
            plt_ax.set_xlim(min(time_to_plot), max(time_to_plot))
            plt_ax.set_ylim(min(signal_to_plot), max(signal_to_plot))
            plt_ax.set_ylabel(f"Amplitude ({units_str})")
            plt_ax.set_xlabel("Time (s)")
            plt_ax.legend(["Channel 2"], loc='upper right')

            plt_ax = axs[2]
            time_to_plot = time_secs[sample_sel]
            signal_to_plot = data[ch_1_idx][sample_sel] - \
                data[ch_2_idx][sample_sel]
            signal_to_plot *= -1
            ch_to_plot_name = ch_names[ch_1_idx] + "-" + ch_names[ch_2_idx]
            units_str = units[ch_names[ch_1_idx]]

            plt_ax.plot(time_to_plot, signal_to_plot, '-',
                        color='black', linewidth=sig_lw)
            plt_ax.set_title(ch_to_plot_name)
            plt_ax.set_xlim(min(time_to_plot), max(time_to_plot))
            plt_ax.set_ylim(min(signal_to_plot), max(signal_to_plot))
            plt_ax.set_ylabel(f"Amplitude ({units_str})")
            plt_ax.set_xlabel("Time (s)")
            plt_ax.legend([ch_to_plot_name], loc='upper right')

            plt.show()

    return scalp_bp_eeg
