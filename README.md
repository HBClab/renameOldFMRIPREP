# Rename Old FMRIPREP (< v1.2.0) files

This script updates the names of _some_ of the fmriprep files.
Currently I'm ignoring figures.
Ideally, I will be covering all anatomical and functional image outputs.

## Quickstart

1. clone this repository

```bash
git clone https://github.com/HBClab/renameOldFMRIPREP.git
```

2. install the requirements

```bash
pip install -r requirements.txt
```

3. run the command help

```bash
./rename_old_fmriprep/conform_fmriprep.py -h
```

4. run the command on your data

```bash
./rename_old_fmriprep/conform_fmriprep.py \
    -i /path/to/old/fmriprep \
    -o /path/to/new/fmriprep \
    -d /path/to/dataset/description/dataset_description.json
```

The `dataset_description.json` is a json file that contains
information about the dataset and the fmriprep version you ran
previously

```python
{
    "Name": "test_data",
    "BIDSVersion": "1.0.0",
    "PipelineDescription": {"Name": "fmriprep", "Version": "1.1.8"}
}
```

Now your data _should_ be bids derivatives compliant!

Please let me know if something does not work properly in [the issues](https://github.com/HBClab/renameOldFMRIPREP/issues)