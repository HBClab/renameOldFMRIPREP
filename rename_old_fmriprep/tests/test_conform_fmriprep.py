import os
import json
from ..conform_fmriprep import rename_fmriprep_files


def test_rename_fmriprep_files(tmp_path):
    cwd = os.path.dirname(os.path.realpath(__file__))
    fmriprep_dir = os.path.join(cwd, 'data')
    renamed_dir = tmp_path
    dset_desc = os.path.join(fmriprep_dir, "dataset_description.json")
    # reference output
    with open(os.path.join(cwd, 'data_transfer.json'), 'r') as js:
        ground_truth_tmp = json.load(js)
    ground_truth = {os.path.basename(old): os.path.basename(new)
                    for old, new in ground_truth_tmp.items()}
    tst_truth_file = rename_fmriprep_files(fmriprep_dir, str(renamed_dir), dset_desc)

    with open(tst_truth_file, 'r') as js2:
        tst_truth_tmp = json.load(js2)

    tst_truth = {os.path.basename(old): os.path.basename(new)
                 for old, new in tst_truth_tmp.items()}
    # get basenames for each key-value

    assert ground_truth == tst_truth
