import os


path = os.path.dirname(os.path.abspath(__file__))
cutIdx = path.rfind(os.path.sep)
workspacePath = path[:cutIdx]
data_path = workspacePath + os.path.sep + 'Data' + os.path.sep
scalp_data_path = data_path + 'Scalp_EEG' + os.path.sep
intra_data_path = data_path + 'Intracranial_EEG' + os.path.sep
scalp_maggi_gs = data_path + 'Scalp_Maggi_GS' + os.path.sep

paths = {
    'Data': data_path,
    'ScalpData': scalp_data_path,
    '   ': intra_data_path,
    'Scalp_Maggi_GS': scalp_maggi_gs,
}
