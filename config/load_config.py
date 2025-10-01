import yaml
from typing import Optional, Dict, Any

class GeneralConfig:
    def __init__(self, raw: Dict[str, Any]) -> None:
        self.iterations = raw['iterations']
        self.dae_output = raw['dae_output']
        self.continuous_play = raw['continuous_play']

    def __repr__(self):
        return str(self.__dict__) + '\n'

class BouldersConfig:
    def __init__(self, raw: Dict[str, Any]) -> None:
        self.density = raw['density']
        self.max_dist = raw['max_dist']
        self.alpha_min = raw['alpha_min']
        self.alpha_max = raw['alpha_max']

    def __repr__(self):
        return str(self.__dict__) + '\n'

class LandscapeConfig:
    def __init__(self, raw: Dict[str, Any]) -> None:
        self.size = raw['size']
        self.noise_chance = raw['noise_chance']
        self.boulder_chance = raw['boulder_chance']
        self.alpha_min = raw['alpha_min']
        self.alpha_max = raw['alpha_max']

    def __repr__(self):
        return str(self.__dict__) + '\n'

class SensorTrajectoryConfig:
    def __init__(self, raw: Dict[str, Any]) -> None:
        self.size = raw['size']
        self.height_min = raw['height_min']
        self.height_max = raw['height_max']
        self.bend_radius_min = raw['bend_radius_min']
        self.bend_radius_max = raw['bend_radius_max']
        self.bend_occ_min = raw['bend_occ_min']
        self.bend_occ_max = raw['bend_occ_max']
        self.trajectory_deviation_param = raw["trajectory_deviation_param"]

    def __repr__(self):
        return str(self.__dict__) + '\n'

class MunitionsConfig:
    def __init__(self, raw: Dict[str, Any]) -> None:
        self.generate = raw['generate']
        self.munition_type = raw['munition_type']
        self.num_munitions = raw['num_instances']
        self.min_distance = raw['min_distance']
        self.alpha_min = raw['alpha_min']
        self.alpha_max = raw['alpha_max']
        self.save_bb_info = raw['save_bb_info']  # Save bounding box info of munitions

    def __repr__(self):
        return str(self.__dict__) + '\n'

class SonarConfig:
    def __init__(self, raw: Dict[str, Any]) -> None:
        self.generate = raw['generate']
        self.fov = raw['fov']
        self.resolution = raw['resolution']
        self.noise_mean = raw['noise_mean']
        self.noise_std = raw['noise_std']
        self.interference_noise = raw['interference_noise']
        self.interference_noise_chance_per_ping = raw['interference_noise_chance_per_ping']
        self.interference_noise_min = raw['interference_noise_min']
        self.interference_noise_max = raw['interference_noise_max']
        self.interference_noise_chance_per_beam = raw['interference_noise_chance_per_beam']
        self.save_csv = raw['save_csv']

    def __repr__(self):
        return str(self.__dict__) + '\n'

class RootConfig:
    def __init__(self, raw: Dict[str, Any]) -> None:
        self.__base = ""
        if 'general' in raw:
            self.general = GeneralConfig(raw['general'])
        else:
            self.general = None

        if 'boulders' in raw:
            self.boulders = BouldersConfig(raw['boulders'])
        else:
            self.boulders = None

        if 'landscape' in raw:
            self.landscape = LandscapeConfig(raw['landscape'])
        else:
            self.landscape = None

        if 'sonar' in raw:
            self.sonar = SonarConfig(raw['sonar'])
        else:
            self.sonar = None

        if 'munitions' in raw:
            self.munitions = MunitionsConfig(raw['munitions'])
        else:
            self.munitions = None

        if 'sensor_trajectory' in raw:
            self.sensor_trajectory = SensorTrajectoryConfig(raw['sensor_trajectory'])
        else:
            self.sensor_trajectory = None


    def set_base_path(self, path):
        '''Sets the base path for relative file references.
        Args:
            path (str): The base path to set.
        '''
        self.__base = path

    def get_base_path(self):
        '''Gets the base path for relative file references.
        Returns:
            str: The base path.
        '''
        return self.__base

def load_configuration(config_file: str) -> RootConfig:
    """Load and parse a YAML configuration file.

    Args:
        config_file: Path to the YAML configuration file

    Returns:
        RootConfig object containing parsed configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If YAML is invalid or required keys are missing
    """
    try:
        with open(config_file, "r") as stream:
            config = RootConfig(yaml.safe_load(stream))
            return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {config_file}")
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML format: {exc}")
    except KeyError as exc:
        raise ValueError(f"Missing required configuration key: {exc}")
