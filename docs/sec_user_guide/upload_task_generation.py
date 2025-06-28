"""DCOR-Aid task creator

This script automatically generates *.dcoraid-task files recursively.
For each directory with *.rtdc files, an upload_job.dcoraid-task file
is generated. This task file can then be loaded into DCOR-Aid for the
actual upload. This script only serves as a template. Please go ahead
and edit it to your needs if necessary.

Changelog
---------
2021-10-26
 - initial version
"""
import copy
import pathlib

import dclab
import dcoraid


#: Local directory to search recursively for .rtdc files
DATA_DIRECTORY = r"T:\Example_Data\Main_Directory"

#: List of file name suffixes of files to be included in the upload
#: (see :func:`dcoraid.CKANAPI.get_supported_resource_suffixes`)
DATA_FILE_SUFFIXES = [
    "*.ini",
    "*.csv",
    "*.tsv",
    "*.txt",
    "*.pdf",
    "*.jpg",
    "*.png",
    "*.so2",
    "*.poly",
    "*.sof",
    ]


#: Default values for the dataset upload
DATASET_TEMPLATE_DICT = {
    # Should the datasets by private or publicly visible (optional)?
    "private": False,
    # Under which license would you like to publish your data (mandatory)?
    "license_id": "CC0-1.0",
    # To which DCOR circle should the dataset be uploaded (optional)?
    "owner_org": "my-dcor-circle",
    # Who is responsible for this dataset (mandatory)?
    "authors": "Heinz Beinz Automated Upload",
}

#: Supplementary resource metadata
#: (see :func:`dcoraid.CKANAPI.get_supplementary_resource_schema`)
RSS_DICT = {
    "cells": {
        "organism": "human",
        "cell type": "blood",
        "fixed": False,
        "live": True,
        "frozen": False,
        },
    "experiment": {
        "buffer osmolality": 284.0,
        "buffer ph": 7.4,
    }
}


def recursive_task_file_generation(path=DATA_DIRECTORY):
    """Recursively generate .dcoraid-task files in a directory tree

    Skips directories that already contain a .dcoraid-task file
    (This is important in case DCOR-Aid already imported that task
    file and gave that task a DCOR dataset ID).
    """
    # Iterate over all directories
    for pp in pathlib.Path(path).rglob("*"):
        if pp.is_dir():
            generate_task_file(pp)


def generate_task_file(path):
    """Generate the upload_job.dcoraid-task file in directory `path`

    A task file is only generated if the directory contains .rtdc
    files.
    """
    path = pathlib.Path(path)
    assert path.is_dir()

    path_task = path / "upload_job.dcoraid-task"
    if path_task.exists():
        print(f"Skipping creation of {path_task} (already exists)")
        return
    else:
        print(f"Processing {path}", end="", flush=True)

    # get all .rtdc files
    resource_paths = sorted(path.glob("*.rtdc"))
    # make sure they are ok
    for pp in copy.copy(resource_paths):
        try:
            with dclab.IntegrityChecker(pp) as ic:
                cues = ic.sanity_check()
                if len(cues):
                    raise ValueError(f"Sanity Check failed for {pp}!")
        except BaseException:
            print(f"\n...Excluding corrupt resource {pp.name}",
                  end="", flush=True)
            resource_paths.remove(pp)

    # proceed with task generation
    if resource_paths:
        # DCOR dataset dictionary
        dataset_dict = copy.deepcopy(DATASET_TEMPLATE_DICT)
        # Set the directory name as the dataset title
        dataset_dict["title"] = path.name

        # append additional resources
        for suffix in DATA_FILE_SUFFIXES:
            resource_paths += path.glob(suffix)

        # create resource dictionaries for all resources
        resource_dicts = []
        for pp in resource_paths:
            rsd = {"path": pp,
                   "name": pp.name}
            if pp.suffix == ".rtdc":
                # only .rtdc data can have supplementary resource metadata
                rsd["supplements"] = get_supplementary_resource_metadata(pp)
            resource_dicts.append(rsd)
        dcoraid.create_task(path=path_task,
                            dataset_dict=dataset_dict,
                            resource_dicts=resource_dicts)
        print(" - Done!")
    else:
        print("\n...No usable DC files!")


def get_supplementary_resource_metadata(path):
    """Return dictionary with supplementary resource metadata

    You will probably want to modify this function to your liking.
    """
    path = pathlib.Path(path)
    assert path.suffix == ".rtdc"
    supplements = copy.deepcopy(RSS_DICT)
    # Here you may add additional information, e.g. if you want
    # to add a pathology depending on the folder name of the
    # containing folder:
    #
    # if path.parent.name.count("BH"):
    #     supplements["cells"]["pathology"] = "long covid"
    #
    return supplements


if __name__ == "__main__":
    recursive_task_file_generation()
