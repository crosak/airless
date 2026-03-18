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

'''
Configuration dataclasses for stars, orbits, planets and experiments.
'''

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class StarConfig:
    radius: float
    temperature: float
    metallicity: float = 0.0

@dataclass(frozen=True)
class OrbitConfig:
    semi_major_axis: float
    distance: float
    inclination: float
    phase_angle: float 

@dataclass(frozen=True)
class PlanetConfig:
    radius: float
    gravity: float
    rotation_period: float

@dataclass(frozen=True)
class SurfaceCompositionConfig:
    materials: list[str]
    weights: list[float]
    reference_str: str | None

@dataclass(frozen=True)
class ModelOptions:
    phase_function: str
    include_thermal: bool
    theta_step_deg: float
    phi_step_deg: float
    
@dataclass(frozen=True)
class ExperimentConfig:
    star: StarConfig
    orbit: OrbitConfig
    planet: PlanetConfig
    surface: SurfaceCompositionConfig
    model: ModelOptions
    mode: str = "forward" 
    lab_data_dir: str | Path | None = None
    output_dir: str | Path | None = None

class CompositionLibrary:
    """Load a named surface-composition preset from the material preset CSV."""

    def __init__(self, preset_composition: str, preset_file: str | Path | None = None) -> None:
        self.preset_composition = preset_composition
        if preset_file is None:
            # Use the package default preset table when no custom file is provided.
            self.preset_file = (
                Path(__file__).resolve().parent.parent / "data" / "presets" / "material_presets.csv"
            )
        else:
            self.preset_file = Path(preset_file)
        self.materials_: list[str] = []
        self.weights_: list[float] = []
        
    def load_composition(self) -> tuple[list[str], list[float]]:
        """
        Return (materials, weights) for the selected preset.

        The CSV is expected to contain rows in the form:
        preset_name, material_name, weight
        """
        self.materials_.clear()
        self.weights_.clear()
        available_presets: set[str] = set()

        with self.preset_file.open("r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=",", quotechar="'", skipinitialspace=True)
            for line_no, row in enumerate(reader, start=1):
                if not row:
                    continue

                preset_name = row[0].strip()
                if not preset_name:
                    continue

                available_presets.add(preset_name)
                if preset_name != self.preset_composition:
                    # Track all known presets for better unknown-preset error messages.
                    continue

                if len(row) != 3:
                    raise ValueError(
                        f"Malformed preset row at line {line_no}: expected 3 columns "
                        f"(preset, material, weight)."
                    )

                material_name = row[1].strip()
                if not material_name:
                    raise ValueError(f"Empty material name at line {line_no}.")

                try:
                    weight_value = float(row[2])
                except ValueError as exc:
                    raise ValueError(f"Invalid weight value at line {line_no}: {row[2]!r}.") from exc

                self.materials_.append(material_name)
                self.weights_.append(weight_value)

        if not self.materials_:
            available_str = ", ".join(sorted(available_presets))
            raise ValueError(
                f"Unknown preset composition {self.preset_composition!r}. "
                f"Available presets: {available_str}."
            )

        return self.materials_, self.weights_
    
class MaterialLibrary:
    """Initialize a state which efficiently loads/stores lab spectra."""
    
    def __init__(self, materials: list[str], lab_data_dir: str | Path | None = None, lab_data_format: str = "*.tab") -> None:
        if lab_data_dir is None:
            self.lab_data_dir_ = Path(__file__).resolve().parent.parent / "data"
        elif type(lab_data_dir) == str:
            self.lab_data_dir_ = Path(lab_data_dir)
        else:
            self.lab_data_dir_ = lab_data_dir
        self.lab_data_format_ = lab_data_format
        self.materials_ = materials
        self.material_library_: dict[str, str] = {}
        self.special_dirs_: list[str] = ["presets"] # Special directories that won't be parsed
    def get(self) -> None:
        """
        Parse through the lab data folder and fill an internal dict.
        TODO: How would caching work in this scenario?
        TODO: How to ensure calling get() twice results in the same output?
        """
        for folder_ in self.lab_data_dir_.iterdir():
            folder_name_ = str(folder_.relative_to(self.lab_data_dir_))
            if folder_.is_dir() and (folder_name_ not in self.special_dirs_):
                new_material_path = list(folder_.glob(self.lab_data_format_))
                # What if there are none/multiple .tab files? Shouldn't happen in theory, but a user might make a mistake.
                if new_material_path == []:
                    raise ValueError(f"Missing {self.lab_data_format_} file. Please check your lab data files.")
                elif len(new_material_path) != 1:
                    raise ValueError(
                        f"Multiple {self.lab_data_format_} files found in directory {folder_}! Only one data file per folder is permitted."
                    )        
                new_material_entry: dict[str, str] = {folder_name_: str(new_material_path[0])}
                self.material_library_.update(new_material_entry)

    def load(self):
        pass