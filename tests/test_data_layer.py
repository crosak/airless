from airless.config import (
    ExperimentConfig,
    ModelOptions,
    OrbitConfig,
    PlanetConfig,
    StarConfig,
    SurfaceCompositionConfig,
)
from airless.model import ForwardExperiment, create_forward_experiment
import pytest

# Check whether the ForwardExperiment() instance gets created correctly (Smoke test)
def test_forward_experiment_can_be_created():
    config = ExperimentConfig(
        star=StarConfig(radius=1.0, temperature=5778.0, metallicity=0.0),
        orbit=OrbitConfig(
            semi_major_axis=1.0,
            distance=10.0,
            inclination=60.0,
            phase_angle=30.0,
        ),
        planet=PlanetConfig(radius=1.0, gravity=9.8, rotation_period=24.0),
        surface=SurfaceCompositionConfig(
            materials=["basalt"],
            weights=[1.0],
            reference_str=None,
        ),
        model=ModelOptions(
            phase_function="legendre",
            include_thermal=True,
            theta_step_deg=10.0,
            phi_step_deg=10.0,
        )
    )

    experiment = ForwardExperiment(config=config)

    assert isinstance(experiment, ForwardExperiment)
    assert experiment.config is config

# Check whether the create_forward_experiment() factory populates the ForwardExperiment() object correctly
def test_factory_populates_config_correctly():
    
    star_radius_input = 1.0
    star_temperature_input = 5778.0
    star_metallicity_input = 0.0
    
    semi_major_axis_input = 1.5
    distance_input = 10.0
    inclination_input = 90.0
    phase_angle_input = 10.0
    
    planet_radius_input = 2.0
    gravity_input = 9.8
    rotation_period_input = 24.0
    
    materials_input = ["basalt"]
    weights_input = [1.0]
    reference_str_input = None
    
    phase_function_input = "legendre"
    include_thermal_input = True
    theta_step_deg_input = 10.0
    phi_step_deg_input = 10.0
    
    lab_data_input = "data/"
    output_dir_input = "out/"

    experiment = create_forward_experiment(
        star_temperature=star_temperature_input,
        star_radius=star_radius_input,
        semi_major_axis=semi_major_axis_input,
        distance=distance_input,
        inclination=inclination_input,
        phase_angle=phase_angle_input,
        planet_radius=planet_radius_input,
        gravity=gravity_input,
        rotation_period=rotation_period_input,
        materials=materials_input,
        weights=weights_input,
        output_dir=output_dir_input,
        star_metallicity=star_metallicity_input,
        reference_str=reference_str_input,
        phase_function=phase_function_input,
        include_thermal=include_thermal_input,
        theta_step_deg=theta_step_deg_input,
        phi_step_deg=phi_step_deg_input,
        lab_data=lab_data_input,
    )

    assert isinstance(experiment, ForwardExperiment)
    
    # Inherited StarConfig object settings
    assert experiment.config.star.radius == star_radius_input
    assert experiment.config.star.temperature == star_temperature_input
    assert experiment.config.star.metallicity == star_metallicity_input
    # Inherited OrbitConfig object settings
    assert experiment.config.orbit.semi_major_axis == semi_major_axis_input
    assert experiment.config.orbit.distance == distance_input
    assert experiment.config.orbit.inclination == inclination_input
    assert experiment.config.orbit.phase_angle == phase_angle_input
    # Inherited PlanetConfig object settings
    assert experiment.config.planet.radius == planet_radius_input
    assert experiment.config.planet.gravity == gravity_input
    assert experiment.config.planet.rotation_period == rotation_period_input
    # Inherited SurfaceCompositionConfig object settings
    assert experiment.config.surface.materials == materials_input
    assert experiment.config.surface.weights == weights_input
    assert experiment.config.surface.reference_str == reference_str_input
    # Inherited ModelOptions object settings
    assert experiment.config.model.phase_function == phase_function_input
    assert experiment.config.model.include_thermal == include_thermal_input
    assert experiment.config.model.theta_step_deg == theta_step_deg_input
    assert experiment.config.model.phi_step_deg == phi_step_deg_input
    # Direct ExperimentConfig settings 
    assert experiment.config.mode == "forward"
    assert experiment.config.lab_data_dir == lab_data_input
    assert experiment.config.output_dir == output_dir_input
    
# Test default options for the factory
# For future reference, this test is intended to ensure the default case scenario that is supposed to always work.
# Example: Somebody writes an experimental phase function and updates the default to it. Whole code breaks.
def test_factory_populates_defaults_correctly():
    star_radius_input = 1.0
    star_temperature_input = 6000.0
    
    semi_major_axis_input = 1.5
    distance_input = 10.0
    
    planet_radius_input = 2.0
    gravity_input = 9.8
    rotation_period_input = 24.0
    
    materials_input = ["basalt"]
    weights_input = [1.0]
    
    experiment = create_forward_experiment(
        star_temperature=star_temperature_input,
        star_radius=star_radius_input,
        semi_major_axis=semi_major_axis_input,
        distance=distance_input,
        planet_radius=planet_radius_input,
        gravity=gravity_input,
        rotation_period=rotation_period_input,
        materials=materials_input,
        weights=weights_input
    )
    
    # Inherited StarConfig object settings
    assert experiment.config.star.metallicity == 0.0
     # Inherited OrbitConfig object settings
    assert experiment.config.orbit.inclination == 90.0
    assert experiment.config.orbit.phase_angle == 0.0
    # Inherited SurfaceCompositionConfig object settings
    assert experiment.config.surface.reference_str == None
    # Inherited ModelOptions object settings
    assert experiment.config.model.phase_function == "legendre"
    assert experiment.config.model.include_thermal == True
    assert experiment.config.model.theta_step_deg == 10
    assert experiment.config.model.phi_step_deg == 10
    # Direct ExperimentConfig settings 
    assert experiment.config.mode == "forward"
    assert experiment.config.lab_data_dir == "data/"
    assert experiment.config.output_dir == "out/"

# Test if our factory behaves correctly if given bad inputs.
BASE_ARGS = {
    "star_temperature": 6000.0,
    "star_radius": 1.0,
    "semi_major_axis": 1.5,
    "distance": 10.0,
    "planet_radius": 2.0,
    "gravity": 9.8,
    "rotation_period": 24.0,
    "materials": ["basalt"],
    "weights": [1.0],
}
@pytest.mark.parametrize(
    "overrides, msg",
    [
        ({"star_temperature": -1.0}, "positive"),
        ({"star_radius": -1.0}, "positive"),
        ({"inclination": 181.0}, "Inclination"),
        ({"phase_angle": -1.0}, "Phase angle"),
        ({"materials": ["a", "b"], "weights": [1.0]}, "correspond"),
        ({"materials": ["a", "b"], "weights": [-0.2, 0.8]}, "Negative"),
        ({"materials": ["a", "b"], "weights": [-0.2, 1.2]}, "Negative"),
        ({"weights": [0.9]}, "sum up to 1"),
        ({"phase_function": "bad_option"}, "not available"),
    ],
    ids=[
        "neg_star_temp",
        "neg_star_radius",
        "inclination_out_of_range",
        "phase_out_of_range",
        "materials_weights_len_mismatch",
        "negative_value_in_materials",
        "invalid_sum_to_one",
        "weights_sum_not_one",
        "invalid_phase_function",
    ],
)
def test_bad_inputs_for_factory(overrides, msg):
    """
    Imitate various "bad input" scenarios.
    """
    # It is good practice to work with copies (unless they are very expensive to copy)
    kwargs = BASE_ARGS.copy() 
    kwargs.update(overrides)
    with pytest.raises(ValueError, match=msg):
        create_forward_experiment(**kwargs)