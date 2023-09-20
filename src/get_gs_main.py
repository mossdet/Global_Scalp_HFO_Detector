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


# Find and return valid gold standard files for a specific patient.
def find_gs_files(patient_fn):
    all_gs_files = os.listdir(paths['Scalp_Maggi_GS'])
    pat_valid_gs_sel = \
        [gs_file.find(patient_fn) != -1 for gs_file in all_gs_files]

    pat_valid_gs_files = np.array(all_gs_files)[pat_valid_gs_sel]

    return pat_valid_gs_files


# Load data from a gold standard file and store it as a dictionary.
def load_gs_file(mat_fname):
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
    keys_list = list(marks.keys())
    marks_data_shape = marks[keys_list[0]].shape
    for key in marks:
        key_vec_shape = marks[key].shape
        if (len(key_vec_shape) > 1) or (key_vec_shape[0] != marks_data_shape[0]):
            raise ("Read featues from marks don't have uniform dimensions")

    return marks


def get_denoised_event_marks(mtg_labels, artefact_marks, event_marks):

    nr_artefacts = len(artefact_marks['type'])
    denoised_event_marks = {}

    for mtg_label in mtg_labels:
        ch_sel = event_marks['channel'] == mtg_label[0].lower()

        if sum(ch_sel) == 0:
            continue

        # get channel events
        chann_events = {key: value[ch_sel]
                        for key, value in event_marks.items()}
        nr_events = len(chann_events['type'])
        event_in_artfct_sel = np.full((nr_events), False)

        # loop through artefact and channel events to determine coincidence
        for ai in range(0, nr_artefacts):

            artfct_chann = artefact_marks['channel'][ai]
            artfct_chspec = artefact_marks['chann_spec'][ai] == 1
            if artfct_chspec and (artfct_chann != mtg_label):
                continue

            artfct_strt = artefact_marks['start'][ai]
            artfct_end = artefact_marks['end'][ai]

            for ei in range(0, nr_events):
                event_strt = chann_events['start'][ei]
                event_end = chann_events['end'][ei]

                coincide_1 = (
                    event_strt >= artfct_strt and event_strt <= artfct_end)
                coincide_2 = (
                    event_end >= artfct_strt and event_end <= artfct_end)

                event_in_artfct_sel[ei] = coincide_1 | coincide_2

        if len(denoised_event_marks) == 0:
            for key, value in chann_events.items():
                denoised_event_marks[key] = value[~event_in_artfct_sel]
        else:
            for key, value in chann_events.items():
                denoised_event_marks[key] = np.append(
                    denoised_event_marks[key], value[~event_in_artfct_sel])

    return denoised_event_marks


def erase_spike_events(denoised_event_marks):
    # Erase remaining spike events
    spikes_sel = np.array([type.find("ike") != -
                           1 for type in denoised_event_marks['type']])

    for key in denoised_event_marks:
        denoised_event_marks[key] = denoised_event_marks[key][~spikes_sel]

    return denoised_event_marks


# Extract and process high-frequency oscillation (HFO) gold standard data.
def get_hfo_gold_standard(scalp_bp_eeg):
    clean()
    patient_fn = scalp_bp_eeg['filename'].split('.')[0]
    pat_valid_gs_files = find_gs_files(patient_fn)

    all_denoised_event_marks = {}
    all_artefact_marks = {}

    for gs_file in pat_valid_gs_files:
        mat_fname = paths['Scalp_Maggi_GS'] + gs_file
        marks = load_gs_file(mat_fname)

        # get artefact and event marks
        artefacts_sel = marks['type'] == 'IED'
        artefact_marks = {key: value[artefacts_sel]
                          for key, value in marks.items()}
        event_marks = {key: value[~artefacts_sel]
                       for key, value in marks.items()}

        # get events outside of marked artefactual segments
        denoised_event_marks = get_denoised_event_marks(
            scalp_bp_eeg['mtg_labels'], artefact_marks, event_marks)

        denoised_event_marks = erase_spike_events(denoised_event_marks)

        # Append file specific artefact marks to the all files artefact markers
        if not all_denoised_event_marks:
            all_denoised_event_marks = denoised_event_marks
        else:
            for key in denoised_event_marks:
                all_denoised_event_marks[key] = np.append(
                    all_denoised_event_marks[key], denoised_event_marks[key])

        if not all_artefact_marks:
            all_artefact_marks = artefact_marks
        else:
            for key in artefact_marks:
                all_artefact_marks[key] = np.append(
                    all_artefact_marks[key], artefact_marks[key])

    # Sort by start time
    sort_idx = np.argsort(all_denoised_event_marks['start_s'])
    all_denoised_event_marks = {
        key: value[sort_idx] for key, value in all_denoised_event_marks.items()}

    return all_denoised_event_marks, all_artefact_marks
