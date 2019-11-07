import os
import json

import requests
import pytest
from ..conform_fmriprep import rename_fmriprep_files


@pytest.fixture
def bold_file(request, tmp_path):
    fname = ("sub-01_ses-post_task-flanker_bold_space-MNI152NLin2009cAsym"
             "_variant-smoothAROMAnonaggr_preproc.nii.gz")
    cwd = os.path.dirname(os.path.realpath(__file__))
    cache_file = os.path.join(cwd, "data", "cache.txt")
    fname_full = os.path.join(cwd, "data", "dset2", fname)
    bold_file = request.config.cache.get(cache_file, None)
    if bold_file is None:
        url = "https://osf.io/wtzde/download"
        bold_file_request = requests.get(url, allow_redirects=True)
        open(fname_full, 'wb').write(bold_file_request.content)
        request.config.cache.set(cache_file, fname_full)

    return fname_full


def test_gen_ref(bold_file, tmp_path):
    cwd = os.path.dirname(os.path.realpath(__file__))
    fmriprep_dir = os.path.join(cwd, 'data', 'dset2')
    renamed_dir = tmp_path
    dset_desc = os.path.join(fmriprep_dir, "dataset_description.json")
    tst_json = rename_fmriprep_files(fmriprep_dir, str(renamed_dir), dset_desc, gen_ref=True)

    with open(tst_json, 'r') as js2:
        tst_dict = json.load(js2)
 
    assert [k for k in tst_dict.keys() if "boldref" in k]


def test_rename_fmriprep_files(tmp_path):
    cwd = os.path.dirname(os.path.realpath(__file__))
    fmriprep_dir = os.path.join(cwd, 'data', 'dset1')
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
