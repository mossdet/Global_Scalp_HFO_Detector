import numpy as np
import matplotlib.pyplot as plt
import mne

from scalp_eeg_filenames import SCALP_EEG_FILES, INTRACRANIAL_EEG_FILES
from datapaths import paths
from montage_conversion import convert_to_long_bipolar
from get_hfo_gold_standard import get_hfo_gold_standard

for fn in SCALP_EEG_FILES:
    eeg_path = paths['ScalpData'] + fn
    eeg_data = mne.io.read_raw_edf(eeg_path)
    scalp_bp_eeg = convert_to_long_bipolar(eeg_data, False)
    get_hfo_gold_standard(scalp_bp_eeg)

    input("Next file? ")


for fn in INTRACRANIAL_EEG_FILES:
    eeg_path = paths['IntraData'] + fn
    print(eeg_path)
    edfData = mne.io.read_raw_edf(eeg_path)
    # edfDataRaw =    mne.io.read_raw_edf(edf_path, preload=False)
    mtgT = edfData.get_montage()

    print(edfData)
    print(edfData.info)
