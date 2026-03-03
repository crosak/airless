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


from airless.io import read_spectral_data_tab

import numpy as np
import pytest
import astropy.units as u

# Test the outputs of the lab data reader function
def test_spectral_data_reader():
    
    # Use a known "gold standard" file
    file_path = 'tests/data/Basalt/bir1dp001a.tab'
    Wave_R_, R_ = read_spectral_data_tab(file_path)
    
    # The first 20 entries of the file
    Wave_R_contents = np.array([1999.7, 2000.5, 2001.3, 2002.1, 2002.8 ,
                                2003.6, 2004.4, 2005.2, 2005.9, 2006.7,
                                2007.5, 2008.3, 2009.0, 2009.8, 2010.6,
                                2011.4, 2012.2, 2012.9, 2013.7, 2014.5])
    Wave_R_contents_um = (Wave_R_contents * u.nm).to(u.micron).value
    R_contents = np.array([0.21228, 0.21229, 0.21223, 0.21223, 0.21215,
                           0.21206, 0.21198, 0.21196, 0.21194, 0.21191,
                           0.21182, 0.21177, 0.21167, 0.21159, 0.21149,
                           0.21156, 0.21161, 0.21150, 0.21148, 0.21142])
    
    # Check dimensions
    input_file_shape:int = 2490
    assert np.shape(Wave_R_)[0] == input_file_shape
    assert np.shape(R_)[0] == input_file_shape
    # Check contents
    assert np.allclose(Wave_R_[:np.shape(Wave_R_contents_um)[0]] - Wave_R_contents_um, np.zeros(np.shape(Wave_R_contents_um)[0]), 1e-6)
    assert np.allclose(R_[:np.shape(R_contents)[0]] - R_contents, np.zeros(np.shape(R_contents)[0]), 1e-6)

# Test various "bad" file cases
@pytest.mark.parametrize(
    "overrides, msg",
    [
        ("", "Invalid .tab file"),
        ("\n2000 0.2\n", "Invalid .tab header"),
        ("not_an_int\n2000 0.2\n", "Invalid .tab header"),
        ("2\n2000 0.2\n\n", "Missing wavelength"),
        ("2\n2000 0.2\n2000.5\n", "Missing reflectance"),
        ("2\n2000 0.2\nNaN 0.3\n", "contains NaNs"),
    ],
    ids=[
        "empty_file",
        "bad_header_blank",
        "bad_header_non_numeric",
        "missing_wavelength_data_row",
        "missing_reflectance_data_row",
        "contains_NaNs",
    ],
)
def test_spectral_data_reader_exceptions(overrides, msg, tmp_path):
    tmp_file = tmp_path / "bad.tab"
    tmp_file.write_text(overrides)
    with pytest.raises(ValueError, match = msg):
        read_spectral_data_tab(tmp_file) 

def test_spectral_data_reader_missing_file():
    with pytest.raises(FileNotFoundError):
        read_spectral_data_tab("does_not_exist.tab")
