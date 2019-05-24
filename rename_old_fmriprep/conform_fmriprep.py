#!/usr/bin/env python3
"""
rename fmriprep (< v1.2.0) files to be in conformance with the
bids derivatives release candidate
"""
from argparse import ArgumentParser
import json
import os
import re
from shutil import copyfile

from bids.layout.writing import build_path


# templates for matching the old fmriprep files
BIDS_NAME = (
    r'^(.*\/)?'
    r'sub-(?P<subject>[a-zA-Z0-9]+)'
    r'(_ses-(?P<session>[a-zA-Z0-9]+))?'
    r'(_task-(?P<task>[a-zA-Z0-9]+))?'
    r'(_acq-(?P<acq>[a-zA-Z0-9]+))?'
    r'(_rec-(?P<rec>[a-zA-Z0-9]+))?'
    r'(_run-(?P<run>[a-zA-Z0-9]+))?')

DERIV_NAME = (
    r'_(?P<suffix>[a-zA-Z0-9]+)'
    r'(_space-(?P<space>[a-zA-Z0-9]+))?'
    r'(_class-(?P<class>[a-zA-Z0-9]+))?'
    r'(_target-(?P<target>[a-zA-Z0-9]+))?'
    r'(_variant-(?P<variant>[a-zA-Z0-9]+))?'
    r'_(?P<desc>[a-zA-Z0-9]+)'
    r'\.(?P<ext>(?!svg).*)')

# regular expression to match old fmriprep
DERIV_REGEX = re.compile(r''.join([BIDS_NAME, DERIV_NAME]))

# template to build the "correct" derivative file
PATH_PATTERN = (
    'sub-{subject}'
    '[_ses-{session}]'
    '[_task-{task}]'
    '[_acq-{acq}]'
    '[_rec-{rec}]'
    '[_run-{run}]'
    '[_from-{fspace}]'
    '[_to-{tspace}]'
    '[_mode-{mode}]'
    '[_hemi-{hemi}]'
    '[_space-{space}]'
    '[_label-{label}]'
    '[_desc-{desc}]'
    '_{suffix}'
    '.{ext}')


def rename_fmriprep_files(fmriprep_dir, renamed_dir, dset_desc):
    # copy the dataset_description file over first
    os.makedirs(renamed_dir, exist_ok=True)
    copyfile(dset_desc, os.path.join(renamed_dir, os.path.basename(dset_desc)))

    # collect the mapping from old file names to new file names
    rename_files = {}
    for root, _, files in os.walk(fmriprep_dir):
        for file in files:
            match = re.search(DERIV_REGEX, file)
            if match is not None:
                file_dict = match.groupdict()
                # change brainmask to desc-brain_mask
                if file_dict.get('desc') == 'brainmask':
                    file_dict['desc'] = 'brain'
                    file_dict['suffix'] = 'mask'
                # variant is now desc
                if file_dict.get('variant'):
                    file_dict['desc'] = file_dict.pop('variant')
                # different formats of transformation files
                if file_dict.get('space') and file_dict.get('target'):
                    file_dict['fspace'] = file_dict.pop('space')
                    file_dict['tspace'] = file_dict.pop('target')
                    file_dict['mode'] = 'image'
                    file_dict['suffix'] = 'xfm'
                    del file_dict['desc']
                if file_dict.get('target'):
                    file_dict['fspace'] = file_dict.pop('suffix')
                    file_dict['tspace'] = file_dict.pop('target')
                    file_dict['mode'] = 'image'
                    file_dict['suffix'] = 'xfm'
                    del file_dict['desc']
                # segmentations
                if file_dict.get('class'):
                    file_dict['label'] = file_dict.pop('class')
                    file_dict['suffix'] = 'probseg'
                    del file_dict['desc']
                if file_dict.get('desc') == 'dtissue':
                    file_dict['suffix'] = 'dseg'
                    del file_dict['desc']
                # freesurfer hemisphere files
                if file_dict['ext'].startswith('L') or file_dict['ext'].startswith('R'):
                    file_dict['hemi'] = file_dict['ext'][0]
                    file_dict['ext'] = file_dict['ext'][2:]
                    file_dict['suffix'] = file_dict.pop('desc')
                # aroma files
                if file_dict.get('desc') == 'MELODICmix':
                    file_dict['desc'] = 'MELODIC'
                    file_dict['suffix'] = 'mixing'
                if file_dict.get('desc') == 'AROMAnoiseICs':
                    file_dict['suffix'] = file_dict['desc']
                    del file_dict['desc']
                # confounds file change
                if file_dict.get('desc') == 'confounds':
                    file_dict['suffix'] = 'regressors'

                # write the file to the new directory
                new_file = build_path(file_dict, PATH_PATTERN)
                new_root = root.replace(fmriprep_dir, renamed_dir)
                new_path = os.path.join(new_root, new_file)
                old_path = os.path.join(root, file)
                rename_files[old_path] = new_path
                os.makedirs(new_root, exist_ok=True)
                copyfile(old_path, new_path)

    # write out log for how files were renamed
    data_transfer_log = os.path.join(renamed_dir, "logs", "data_transfer.json")
    os.makedirs(os.path.dirname(data_transfer_log), exist_ok=True)
    with open(data_transfer_log, 'w') as fp:
        json.dump(rename_files, fp)

    return data_transfer_log


def main():
    # set up a parser to read arguments
    parser = ArgumentParser(description='conform_fmriprep: rename old fmriprep (< v1.2.0) files')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-i', '--input-dir', dest='fmriprep_dir',
                               action='store', required=True,
                               help='the root folder of a fmriprep derivatives '
                               'dataset (sub-XXXXX folders should be found at the '
                               'top level in this folder).')
    requiredNamed.add_argument('-o', '--output-dir', dest='renamed_dir',
                               action='store', required=True,
                               help='the root folder to place the renamed fmriprep outputs')
    requiredNamed.add_argument('-d', '--dataset-description', dest='dset_desc',
                               action='store', required=True,
                               help='the required dataset description file to be placed '
                               'at the root folder of fmriprep')

    opts = parser.parse_args()

    # rename the files
    rename_fmriprep_files(opts.fmriprep_dir, opts.renamed_dir, opts.dset_desc)


if __name__ == '__main__':
    main()
