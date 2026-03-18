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

# Patch for Python 3.9 for now
from __future__ import annotations

from .config import (
    StarConfig, OrbitConfig, PlanetConfig,
    SurfaceCompositionConfig, ModelOptions,
    ExperimentConfig, CompositionLibrary,
    MaterialLibrary,
)
from pathlib import Path
import numpy as np

class ForwardExperiment:
    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config
        self.validate_config()
    def validate_config(self) -> None:
        """
        Sanity checks for inputs.
        """
        # Positive physical quantities
        star_temperature_ = self.config.star.temperature
        star_radius_ = self.config.star.radius
        semi_major_axis_ = self.config.orbit.semi_major_axis
        distance_ = self.config.orbit.distance
        planet_radius_ = self.config.planet.radius
        gravity_ = self.config.planet.gravity
        rotation_period_ = self.config.planet.rotation_period
        positive_physical_qs = [star_temperature_, star_radius_,
                                semi_major_axis_, distance_,
                                planet_radius_, gravity_,
                                rotation_period_
                                ]
        for quantity in positive_physical_qs:
            if (quantity < 0.0):
                raise ValueError(f"{quantity} needs to be positive!")
        
        # Angle ranges
        inclination_ = self.config.orbit.inclination
        phase_angle_ = self.config.orbit.phase_angle
        if (inclination_ < 0.0 or inclination_ > 180.0):
            raise ValueError("Inclination value must be between 0.0 and 180.0 degrees.")
        if (phase_angle_ < 0.0 or phase_angle_ > 180.0):
            raise ValueError("Phase angle value must be between 0.0 and 180.0 degrees.")
        # Material settings
        materials_ = self.config.surface.materials
        weights_ = self.config.surface.weights
        if not materials_:
            raise ValueError("User needs to input a materials array for calculations.")
        if len(materials_) != len(weights_):
            raise ValueError("The weights array must correspond to the materials array in length.")
        for weight_ in weights_:
            if (weight_ < 0.0):
                raise ValueError("Negative weights are not allowed!")
        if (sum(weights_) < 0.0 or not np.allclose(sum(weights_), 1.0, 1e-6)):
            raise ValueError("Weights must sum up to 1!")
        # Available options for the phase function
        phase_function_ = self.config.model.phase_function
        phase_function_options = ["legendre", "HG"]
        if (phase_function_ not in phase_function_options):
            raise ValueError("Chosen phase function option is not available.")
        
    # def run(self):
        # Construct the material library
        # lab_data_dir_ = self.config.lab_data_dir
        # spectra_loader = MaterialLibrary(lab_data_dir=lab_data_dir_)
        # spectra_loader.get()
        # Load lab spectra data
        # spectra_loader.load(materials=materials_)
        # Build mixed reflectance (?)
        # Bin the lab data
        
        # Calculate disk integrated flux 
        # Calculate stellar flux
        # Return result
            

def create_forward_experiment(
    star_temperature: float,
    star_radius: float,
    semi_major_axis: float,
    distance: float,
    planet_radius: float,
    gravity: float, 
    rotation_period: float,
    inclination: float = 90.0,
    phase_angle: float = 0.0,
    star_metallicity: float = 0.0,
    materials: list[str] | None = None,
    weights: list[float] | None = None,
    reference_str: str | None = None,
    preset_composition: str | None = None,
    preset_file: str | Path | None = None,
    phase_function: str = "legendre",
    include_thermal: bool = True,
    theta_step_deg: float = 10,
    phi_step_deg: float = 10,
    lab_data: str | Path = "data/",
    output_dir: str | Path = "out/",
) -> ForwardExperiment:
    """
    Parameters
    ----------
    star_temperature: float
        Stellar effective temperature
    star_radius: float
        Stellar radius
    semi_major_axis: float
        Orbital semi-major axis
    distance: float
        Distance to observer
    planet_radius: float
        Planet radius
    materials: list[str]
        Material name
    weights: list[float]
        Material weight, should correspond to the material list. Weights should sum to ~1.
    reference_str: str
        Optional free-form reference string for the surface composition.
    preset_composition: str
        Reference string for any available preset composition from our database.
        Overrides the materials - weights inputs.
    preset_file: str | pathlib.Path | None
        Optional path to the preset CSV file. If omitted, the package default is used.
    star_metallicity: float
        Optional metallicity indicator (e.g. [Fe/H]).
    inclination: float
        Orbital inclination (degrees). Default is 90 (edge-on).
    phase_deg: float
        Phase angle (degrees). Default is 0.
    phase_function: float
        Phase function identifier (e.g. "legendre" or "HG").
    include_thermal: bool
        Whether to include thermal emission in the forward model.
    lab_data_dir, output_dir: str | pathlib.Path
        Optional base directories for lab data and outputs.

    Returns
    -------
    ForwardExperiment:
        A configured experiment object.
    """
    # Build sub-configs
    star = StarConfig(star_radius, star_temperature, star_metallicity)
    planet = PlanetConfig(planet_radius, gravity, rotation_period)
    orbit = OrbitConfig(semi_major_axis, distance, inclination, phase_angle)
    if (preset_composition):
        preset_material = CompositionLibrary(preset_composition, preset_file)
        preset_material.load_composition()
        surface = SurfaceCompositionConfig(preset_material.materials_, preset_material.weights_, reference_str)
    else:
        surface = SurfaceCompositionConfig(materials, weights, reference_str)
    model = ModelOptions(phase_function, include_thermal, theta_step_deg, phi_step_deg)
    # Build ExperimentConfig
    config = ExperimentConfig(
        star=star,
        orbit=orbit,
        planet=planet,
        surface=surface,
        model=model,
        mode="forward",
        lab_data_dir=lab_data,
        output_dir=output_dir,
    )
    # Return ForwardExperiment(config)
    experiment = ForwardExperiment(config)
    
    return experiment
