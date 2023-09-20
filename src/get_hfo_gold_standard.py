from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
import mne
import os
from helpers import clean

from datapaths import paths
'''
detection format

channel, type, startTime, endTime, startSample, endSample, comments, channSpec, creationTime, username

'''


def find_gs_files(patient_fn):
    """
    Find and return valid gold standard files for a specific patient.

    Parameters:
    - patient_fn: The filename of the patient.

    Returns:
    - pat_valid_gs_files: A list of valid gold standard files for the patient.
    """
    mtg_labels = [mtg_label[0].lower()
                  for mtg_label in scalp_bp_eeg['mtg_labels']]

    all_gs_files = os.listdir(paths['Scalp_Maggi_GS'])
    pat_valid_gs_sel = [gs_file.find(
        patient_fn) != -1 for gs_file in all_gs_files]
    pat_valid_gs_files = np.array(all_gs_files)[pat_valid_gs_sel]
    return pat_valid_gs_files


def load_gs_file(mat_fname):
    """
    Load data from a gold standard file and store it as a dictionary.

    Parameters:
    - mat_fname: The filename of the gold standard file (MATLAB format).

    Returns:
    - marks: A dictionary containing the loaded data.
    """
    mat_contents = sio.loadmat(mat_fname)
    detections_data = mat_contents['detections']

    # store data as a dictionary
    marks = {}
    marks['channel'] = np.array(
        [detection[0][0].lower() for detection in detections_data])

    marks['type'] = np.array([detection[1][0]
                             for detection in detections_data])

    marks['start_s'] = np.array([detection[2][0][0]
                                for detection in detections_data])

    marks['end_s'] = np.array([detection[3][0][0]
                              for detection in detections_data])

    marks['start'] = np.array([detection[4][0][0]
                               for detection in detections_data])

    marks['end'] = np.array([detection[5][0][0]
                            for detection in detections_data])

    marks['comments'] = np.array([detection[6][0]
                                  for detection in detections_data])

    marks['chann_spec'] = np.array(
        [detection[7][0][0] for detection in detections_data])

    marks['creation_t'] = np.array(
        [detection[8][0] for detection in detections_data])

    marks['username'] = np.array([detection[9][0]
                                  for detection in detections_data])
    return marks


def get_hfo_gold_standard(scalp_bp_eeg):
    """
    Extract and process high-frequency oscillation (HFO) gold standard data.

    Parameters:
    - scalp_bp_eeg: EEG data for the patient.

    Returns:
    - all_detectors_denoised_marks: A dictionary containing denoised HFO markers.
    """
    clean()

    # find gold standard file from specific patient
    patient_fn = scalp_bp_eeg['filename'].split('.')[0]
    pat_valid_gs_files = find_gs_files(patient_fn)

    # load GS data from each file
    all_detectors_denoised_marks = []
    for gs_file in pat_valid_gs_files:
        mat_fname = paths['Scalp_Maggi_GS'] + gs_file

        marks = load_gs_file(mat_fname)

        all_denoised_marks = []
        # Extract channel specific marks and artefacts

        # channel wide artefacts
        spike_sel = marks['type'] == 'IED'
        chanspec_sel = marks['chann_spec'] < 0.1
        chanspec_sel = chanspec_sel[:][:][:]

        all_ch_artfct_sel = (marks['type'] == 'IED') & (
            marks['chann_spec'] == 0)
        all_ch_artfct_start = marks['start'][all_ch_artfct_sel]
        all_ch_artfct_end = marks['end'][all_ch_artfct_sel]

        for mtg_label in mtg_labels:
            ch_sel = marks['channel'] == mtg_label
            ch_marks = {}
            for marks_info in marks:
                ch_marks[marks_info] = marks[marks_info][ch_sel]

            # channel specific artefacts
            ch_artfct_sel = np.array(ch_marks['type'] == 'IED') & np.array(
                ch_marks['chann_spec'] == 1)
            ch_artfct_start = ch_marks['start'][ch_artfct_sel]
            ch_artfct_end = ch_marks['end'][ch_artfct_sel]

            artfct_start = np.append(all_ch_artfct_start, ch_artfct_start)
            artfct_end = np.append(all_ch_artfct_end, ch_artfct_end)

            # check which marks are within artefacts
            del_list = []
            for ai in range(0, len(artfct_start)):
                artfct_s = artfct_start[ai]
                artfct_e = artfct_end[ai]
                for mi in range(0, len(ch_marks['end'])):
                    ch_mark_s = ch_marks['start'][mi]
                    ch_mark_e = ch_marks['end'][mi]

                    coincide_1 = ch_mark_s >= artfct_s and ch_mark_s <= artfct_e
                    coincide_2 = ch_mark_e >= artfct_s and ch_mark_e <= artfct_e
                    if coincide_1 or coincide_2:
                        del_list.append(mi)

            # delete the marks within artefacts
            denoised_ch_marks = {}
            for marks_info in ch_marks:
                denoised_ch_marks[marks_info] = np.delete(
                    ch_marks[marks_info], del_list)

            if len(ch_marks['channel']) < len(denoised_ch_marks['channel']):
                raise ("Denoised marks are more than unedited!")

            if len(all_denoised_marks) == 0:
                all_denoised_marks = denoised_ch_marks
            else:
                for marks_info in denoised_ch_marks:
                    all_denoised_marks[marks_info] = np.append(
                        all_denoised_marks[marks_info], denoised_ch_marks[marks_info])

        values, count = np.unique(marks['type'], return_counts=True)
        denoised_values, denoised_count = np.unique(
            all_denoised_marks['type'], return_counts=True)

        print("\nOriginal marks:")
        for idx in range(0, len(values)):
            print(f"{values[idx]} ({count[idx]})")

        print("\n Denoised marks:")
        for idx in range(0, len(denoised_values)):
            print(f"{denoised_values[idx]} ({denoised_count[idx]})")

        stop = 1
        all_detectors_denoised_marks
        if len(all_detectors_denoised_marks) == 0:
            all_detectors_denoised_marks = all_denoised_marks
        else:
            for marks_info in all_denoised_marks:
                all_detectors_denoised_marks[marks_info] = np.append(
                    all_detectors_denoised_marks[marks_info], all_denoised_marks[marks_info])

    # erase remaining spike events
    event_types = np.unique(all_detectors_denoised_marks['type'])
    found_spike_types = [
        spike_type for spike_type in event_types if spike_type.find('ike') != -1]
    sel_spikes = all_detectors_denoised_marks['type'] == found_spike_types
    for marks_info in all_denoised_marks:
        all_detectors_denoised_marks[marks_info] = all_detectors_denoised_marks[marks_info][np.logical_not(
            sel_spikes)]

    event_types = np.unique(all_detectors_denoised_marks['type'])
    found_spike_types = [
        spike_type for spike_type in event_types if spike_type.find('ike') != -1]

    # sort by star time
    sort_idx = np.argsort(all_detectors_denoised_marks['start_s'])
    for marks_info in all_denoised_marks:
        all_detectors_denoised_marks[marks_info] = all_detectors_denoised_marks[marks_info][sort_idx]

    return all_detectors_denoised_marks
