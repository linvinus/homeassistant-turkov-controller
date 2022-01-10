"""Constants for the Turkov controller integration."""

import datetime
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.components.fan import (
    SPEED_HIGH,
    SPEED_LOW,
    SPEED_MEDIUM,
    SPEED_OFF
)

DOMAIN = "turkov_controller"

SCAN_INTERVAL = datetime.timedelta(seconds=10)

REQUEST_TIMEOUT = 60

SIGNAL_TURKOV_CONTROLLER_STATE_UPDATE = "turkov_controller_state_update"

ORDERED_NAMED_FAN_SPEEDS = [1, 2, 3]  # off is not included

