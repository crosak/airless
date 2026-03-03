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

# TODO: Introduce meaningful comments.    
class CompositionLibrary:
    def __init__(self, preset_composition: str, preset_file: str | Path | None = None) -> None:
        self.preset_composition = preset_composition
        if preset_file is None:
            self.preset_file = (
                Path(__file__).resolve().parent.parent / "data" / "presets" / "material_presets.csv"
            )
        else:
            self.preset_file = Path(preset_file)
        self.materials_: list[str] = []
        self.weights_: list[float] = []
        
    def load_composition(self) -> tuple[list[str], list[float]]:
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
    
