"""
Core code accelerated with numba, collected together
for easy maintenance when updates to numba and
llvmlite are made.
"""

from typing import Iterable

import numba
import numpy as np


@numba.njit()
def _njit_count_cells(cells, counts):
    for cell in cells:
        counts[cell] += 1

    return


def count_cells(cells, cells_per_axis):
    counts = np.zeros(cells_per_axis * cells_per_axis * cells_per_axis, dtype=np.int32)

    # njit doesn't like my zeroes!
    _njit_count_cells(cells=cells, counts=counts)

    return counts


@numba.njit()
def compute_particle_ids_binned_by_cell(
    cells: np.array,
    counts: np.array,
):
    """
    Given the cells that each particle is in, inverts the table
    to return an array of cells with particle IDs in each cell.

    Parameters
    ----------

    cells: np.array
        Array of cells that each particle is in.

    counts: np.array
        Count of particles in each cell (can be thought of as
        a histogram of cells with bin width 1).


    Returns
    -------

    particle_ids: List[np.array]
        List of length (number of cells), the same as counts.
        Each item in the list is an array showing which particles
        (by id, which here is just their position in the array - not
        their unique ``ParticleID``) are in the corresponding cell.
    """
    counted_so_far = np.zeros_like(counts)
    particle_ids = [np.empty(count, dtype=np.int32) for count in counts]

    for index_in_file in np.arange(len(cells), dtype=np.int32):
        cell = cells[index_in_file]
        array_id = counted_so_far[cell]
        particle_ids[cell][array_id] = index_in_file
        counted_so_far[cell] = array_id + np.int32(1)

    # Runtime check
    assert (counts == counted_so_far).all()

    return particle_ids


@numba.njit()
def ranges_from_array(array: Iterable[np.int32]) -> np.ndarray:
    """
    Finds contiguous ranges of IDs in sorted list of IDs

    Parameters
    ----------
    array : np.array of int
        sorted list of IDs

    Returns
    -------
    np.ndarray
        list of length two arrays corresponding to contiguous
        ranges of IDs (inclusive) in the input array

    Examples
    --------
    The array

    [0, 1, 2, 3, 5, 6, 7, 9, 11, 12, 13]

    would return

    [[0, 4], [5, 8], [9, 10], [11, 14]]

    """

    output = []

    start = array[0]
    stop = array[0]

    for value in array[1:]:
        if value != stop + 1:
            output.append([start, stop + 1])

            start = value
            stop = value
        else:
            stop = value

    output.append([start, stop + 1])

    return output
