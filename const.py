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


VALUE_TO_SPEED = {
    0: SPEED_OFF,
    1: SPEED_LOW,
    2: SPEED_MEDIUM,
    3: SPEED_HIGH
}
SPEED_TO_VALUE = {v: k for k, v in VALUE_TO_SPEED.items()}
