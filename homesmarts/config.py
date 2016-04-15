"""
homesmarts.config
~~~~~~~~~~~~~

This module contains configuration information and logic for the homesmarts program.
Configuration information includes:
 - switches: details on Dash buttons in use (mac, id, and lights they are associated with)
 - lights: default values for brightness, saturation, and hue when switch is pressed
 - IP of the Phillips Hue bridge.

All these details are contained in the 'homesmarts_config.yaml' file.
"""

import logging
import logging.config
from phue import Bridge
from phue import Light
from phue import Group
import yaml

from dash_listener import DashListener

HOMESMARTS_CONFIG_FILE = "homesmarts_config.yaml"
LOGGING_CONFIG_FILE = "logging_config.yaml"

LIGHT_DEFAULTS_KEY = "light-defaults"
LIGHT_DEFAULTS_BRIGHTNESS_KEY = "brightness"
LIGHT_DEFAULTS_SATURATION_KEY = "saturation"
LIGHT_DEFAULTS_HUE_KEY = "hue"

SWITCHES_KEY = "switches"
SWITCHES_LIGHT_ID_KEY = "light_id"
SWITCHES_GROUP_ID_KEY = "group_id"
SWITCHES_MAC_KEY = "mac"

BRIDGE_IP_KEY = "bridge-ip"

logger = logging.getLogger(__name__)


def init(config_file=HOMESMARTS_CONFIG_FILE):
    """Initializes 'homesmarts' configuration (and logging configuration)"""
    with open(LOGGING_CONFIG_FILE) as f:
        logging_dict = yaml.safe_load(f)
        logging.config.dictConfig(logging_dict)
        logger.debug("Initialized logging from file: %s", f.name)

    return SmartsConfig(config_file)


class SmartsConfig:
    """This class represents the configuration for the 'homesmarts' program

    After being initialized from the config file, this class keeps track of:
     - available Dash IDs and 'DashListener' objects
     - default values to use for Phillips Hue lights
    """
    def __init__(self, config_file):
        with open(config_file) as f:
            self.config_dict = yaml.safe_load(f)
            logger.debug("Initialized 'smarts' using [file: %s]\nconfig_dict=%s", f.name, self.config_dict)

        self.dash_ids = []
        self.dash_listeners = []
        self.bridge = Bridge(self.config_dict[BRIDGE_IP_KEY])

        # Create a "listener" for each Dash button and configure it appropriately
        # Note: A Dash button can be associated with either a "Light" or a "Group"
        for switch_key, switch in self.config_dict[SWITCHES_KEY].items():
            light_id = switch[SWITCHES_LIGHT_ID_KEY] if SWITCHES_LIGHT_ID_KEY in switch else None
            group_id = switch[SWITCHES_GROUP_ID_KEY] if SWITCHES_GROUP_ID_KEY in switch else None
            if bool(light_id) == bool(group_id):
                raise RuntimeError("Must provide exactly one of: {} or {}".format(
                                   SWITCHES_LIGHT_ID_KEY, SWITCHES_GROUP_ID_KEY))

            hue_unit = Light(self.bridge, light_id) if light_id else Group(self.bridge, group_id)
            logger.debug("[switch=%s] is using [hue_unit=%s]...", switch_key, hue_unit)
            mac = switch[SWITCHES_MAC_KEY]

            dash_listener = DashListener(switch_key, mac, hue_unit, self)
            self.dash_listeners.append(dash_listener)
            self.dash_ids.append(switch_key)

    def available_dash_ids(self):
        """Returns a list of all supported Dash identifiers being used in 'homesmarts'"""
        return self.dash_ids

    def get_dash_listeners(self):
        """Returns a list of all Dash listener objects that have been initialized."""
        return self.dash_listeners

    def get_mac_to_message_key_dict(self):
        """Returns dictionary with the 'mac' of the Dash button as the key, and the messaging 'routing_key' as value"""
        mac_to_message_key_dict = dict()
        for dash_listener in self.dash_listeners:
            mac_to_message_key_dict[dash_listener.mac] = dash_listener.dash_id
        return mac_to_message_key_dict

    def default_light_brightness(self):
        """Returns the default brightness to use when triggering a light"""
        return self._default_light_param(LIGHT_DEFAULTS_BRIGHTNESS_KEY)

    def default_light_saturation(self):
        """Returns the default saturation to use when triggering a light"""
        return self._default_light_param(LIGHT_DEFAULTS_SATURATION_KEY)

    def default_light_hue(self):
        """Returns the default hue to use when triggering a light"""
        return self._default_light_param(LIGHT_DEFAULTS_HUE_KEY)

    def _default_light_param(self, light_config_key):
        """Helper method to return appropriate config param from YAML file."""
        light_defaults = self.config_dict[LIGHT_DEFAULTS_KEY]
        return light_defaults[light_config_key]
