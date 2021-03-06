#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
The purpose of this script is to find .slurm files recursively from the calling
directory and then then add these .slurm files to the Iridis 5 queue - or any
HPC cluster which uses slurm.
"""


import argparse as ap
from subprocess import Popen, PIPE
from typing import List, Tuple
from pathlib import Path


def split_path_fname(path: str) -> Tuple[str, str]:
    """

    Parameters
    ----------
    path: str
        The relative path of a slurm file: include the slurm file itself and
        the directories.

    Returns
    -------
    slurmf: str
        The name of the slurm file
    slurmdir: str
        The relative path containing the slurm file
    """

    assert(type(path) == str)

    sidx = -1
    idx = path.find(".slurm")
    for i in range(idx - 1, -1, -1):
        if path[i] == "/":
            sidx = i
            break

    slurmf = path[sidx + 1:]
    if sidx > -1:
        slurmdir = path[:sidx]
    else:
        slurmdir = "./"

    return slurmf, slurmdir


def add_to_queue(slurmfs: List[str]) -> None:
    """
    Add a bunch of slurm parameter files to the slurm queue.

    Parameters
    ----------
    slurmfs: List[str]
        A list of slurm files to run, must contain the relative path and
        the .slurm file.
    """

    nslurm = len(slurmfs)
    codes = []
    for i in range(nslurm):
        f, wd = split_path_fname(slurmfs[i])
        cmd = "cd {}; sbatch {}; cd ..".format(wd, f)
        sh = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = sh.communicate()
        if stderr:
            print(stderr.decode("utf-8"))
        codes.append(stdout.decode("utf-8").split()[-1])

    if len(codes) > 1:
        print("Submitted batch jobs" + ", ".join(codes[:-1]) + " and " + codes[-1])
    else:
        print("Submitted batch job", codes[0])

    return


def find_slurm_files(path: str = ".") -> List[str]:
    """
    Searches recursively from the calling direction for files which end with
    the extension *.slurm and returns a list of the found files.

    Parameters
    ----------
    path: str, optional
        The directory of which to search recursively from.

    Returns
    -------
    slurmf: List[str]
        A list containing the relative paths of the slurm files.
    """

    slurmf = []

    for filename in Path(path).glob("**/*.slurm"):
        fname = str(filename)
        if fname[0] == "/":
            fname = fname[1:]
        slurmf.append(fname)

    if len(slurmf) == 0:
        print("No .slurm files were found.")
        exit(1)

    slurmf = sorted(slurmf, key=str.lower)

    return slurmf


def setup():
    """
    Parse the command line for run time arguments.
    """

    p = ap.ArgumentParser(description=__doc__)

    p.add_argument("-a",
                   "--add_to_queue",
                   action="store_true",
                   default=False,
                   help="Add slurm files to the slurm queue.")

    args = p.parse_args()

    return args.add_to_queue


def main() -> None:
    """
    Main function - calls find_slurm_files to find the slurm files in directories
    and then uses add_to_queue to add them to the slurm queue.
    """

    add = setup()
    slurmf = find_slurm_files()

    print("The following {} .slurm files will be added to the queue:\n".format(len(slurmf)))
    for n, f in enumerate(slurmf):
        print("{}\t{}".format(n + 1, f))
    print("")

    if add:
        add_to_queue(slurmf)

    return


if __name__ == "__main__":
    main()
