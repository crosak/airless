# MIT License
#
# Copyright (c) 2025 Leonardos Gkouvelis, Can Akin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Input/Output functionalities for the model."""


# Patch for Python 3.9 for now
from __future__ import annotations

import numpy as np
import astropy.units as u

from pathlib import Path

def read_spectral_data_tab(file_path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """
    Function to read spectral data from a .tab lab data files.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Read the number of useful lines
    try:
        header = lines[0].strip()
    except IndexError as e:
        raise ValueError("Invalid .tab file: missing first line with row count.") from e

    try:
        num_useful_lines = int(header)
    except ValueError as e:
        raise ValueError(f"Invalid .tab header: expected integer row count, got {header!r}.") from e
    
    # Parse the data into arrays
    Wave_R = np.zeros(num_useful_lines)
    R = np.zeros(num_useful_lines)
    for i in range(1, num_useful_lines + 1):
        line_data = lines[i].strip().split()
        try:
            Wave_R[i-1] = (float(line_data[0]) * u.nm).to(u.micron).value  # Convert nm to micron
        except IndexError as e: 
            raise ValueError(f"Missing wavelength data on row {i}") from e
        try:
            R[i-1] = float(line_data[1])
        except IndexError as e:
            raise ValueError(f"Missing reflectance data on row {i}") from e
        
    # Catch inf, -inf and NaN values inside the data    
    if (np.sum(~np.isfinite(Wave_R)) > 0 or np.sum(~np.isfinite(R)) > 0):
        raise ValueError("Input file contains NaNs!")
    
    return Wave_R, R