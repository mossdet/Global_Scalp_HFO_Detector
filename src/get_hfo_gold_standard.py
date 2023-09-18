import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
import mne
import os

from datapaths import paths
'''
detection format

channel, type, startTime, endTime, startSample, endSample, comments, channSpec, creationTime, username

'''


def get_hfo_gold_standard(scalp_bp_eeg):

    # find
    patient_fn = scalp_bp_eeg['filename'].split('.')[0]
    mtg_labels = scalp_bp_eeg['mtg_labels'].lower()

    all_gs_files = os.listdir(paths['Scalp_Maggi_GS'])
    pat_valid_gs_sel = [gs_file.find(
        patient_fn) != -1 for gs_file in all_gs_files]
    pat_valid_gs_files = np.array(all_gs_files)[pat_valid_gs_sel]
    for gs_file in pat_valid_gs_files:
        mat_fname = paths['Scalp_Maggi_GS'] + gs_file
        mat_contents = sio.loadmat(mat_fname)
        detections = mat_contents['detections']
        dets_channel = np.array([detection[0].lower()
                                for detection in detections])
        dets_type = np.array([detection[1] for detection in detections])
        dets_start_s = np.array([detection[2] for detection in detections])
        dets_end_s = np.array([detection[3] for detection in detections])
        dets_start = np.array([detection[4] for detection in detections])
        dets_end = np.array([detection[5] for detection in detections])
        dets_comments = np.array([detection[6] for detection in detections])
        dets_chann_spec = np.array([detection[7] for detection in detections])
        dets_creation_t = np.array([detection[8] for detection in detections])
        dets_username = np.array([detection[9] for detection in detections])

        # matches = [match for match in ls if "Hello" in match]
        stop = 1
    print(pat_valid_gs_files)
    stop = 1
