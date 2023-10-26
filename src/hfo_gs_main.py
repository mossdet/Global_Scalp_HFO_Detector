import numpy as np
import matplotlib.pyplot as plt
import mne
from helpers import clean
from events_characterization import get_characterized_events
from discretize_eeg import get_eeg_event_wdws
from plot_eeg_marks import plot_eeg_marks


from scalp_eeg_filenames import SCALP_EEG_FILES, INTRACRANIAL_EEG_FILES
from datapaths import paths
from montage_conversion import convert_to_long_bipolar
from get_hfo_and_artefacts_marks import get_hfo_gold_standard

for fn in SCALP_EEG_FILES:
    eeg_path = paths['ScalpData'] + fn
    eeg_data = mne.io.read_raw_edf(eeg_path)
    eeg_data_wdw = eeg_data.copy().crop(tmin=0, tmax=10)
    eeg_data_wdw.set_montage("standard_1020", match_case=False,
                             match_alias=True, on_missing='warn', verbose=None)

    eegplt = eeg_data_wdw.plot()

    scalp_bp_eeg = convert_to_long_bipolar(eeg_data, False)
    denoised_gs, artefact_marks = get_hfo_gold_standard(scalp_bp_eeg)

    plot_eeg_marks(scalp_bp_eeg, denoised_gs, artefact_marks)

    get_characterized_events(scalp_bp_eeg, denoised_gs)
    get_eeg_event_wdws(scalp_bp_eeg, denoised_gs)
    stop = 1
