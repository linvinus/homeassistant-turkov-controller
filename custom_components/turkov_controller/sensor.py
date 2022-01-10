from datetime import datetime, date

from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import (
    DOMAIN,
    SIGNAL_TURKOV_CONTROLLER_STATE_UPDATE
)

async def async_setup_entry(hass, entry, async_add_entities):
    name = hass.data[DOMAIN]["name"] + ' '
    state_proxy = hass.data[DOMAIN]["state_proxy"]

    async_add_entities(
        [
            TurkovControllerTempSensor(state_proxy, name + "Outside Air", "out_temp"),
            TurkovControllerTempSensor(state_proxy, name + "Internal Air", "in_temp"),
            TurkovControllerTempSensor(state_proxy, name + "Target Air", "temp_sp"),
            TurkovControllerFanSpeedSensor(state_proxy, name),
            TurkovControllerFanModeSensor(state_proxy, name),
            TurkovControllerFanFilterSensor(state_proxy, name),
        ],
        update_before_add=False
    )

class TurkovControllerTempSensor(Entity):
    def __init__(self, state_proxy, name, metric):
        self._state = None
        self._name = name
        self._metric = metric
        self._state_proxy = state_proxy

    @property
    def should_poll(self):
        return False

    async def async_added_to_hass(self):
        async_dispatcher_connect(
            self.hass, SIGNAL_TURKOV_CONTROLLER_STATE_UPDATE, self._update_callback
        )

    @callback
    def _update_callback(self):
        self.async_schedule_update_ha_state(True)

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state_proxy.get_temperature(self._metric)

    @property
    def unit_of_measurement(self):
        return TEMP_CELSIUS

class TurkovControllerSensor(Entity):
    def __init__(self, client, name, var, var_length, units, icon):
        self._state = None
        self._name = name
        self._variable = var
        self._var_length = var_length
        self._units = units
        self._icon = icon
        self._client = client

    def update(self):
        self._state = self._client.get_variable(
            self._variable,
            self._var_length,
            conversion=int
        )

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return self._icon

    @property
    def unit_of_measurement(self):
        return self._units

class TurkovControllerFanSpeedSensor(Entity):
    def __init__(self, state_proxy, name):
        self._state_proxy = state_proxy
        self._name = name + "Fan Speed"

    @property
    def should_poll(self):
        return False

    async def async_added_to_hass(self):
        async_dispatcher_connect(
            self.hass, SIGNAL_TURKOV_CONTROLLER_STATE_UPDATE, self._update_callback
        )

    @callback
    def _update_callback(self):
        self.async_schedule_update_ha_state(True)

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state_proxy.get_fan_speed()

    @property
    def icon(self):
        return "mdi:fan"

    @property
    def unit_of_measurement(self):
        return ""

class TurkovControllerFanModeSensor(Entity):
    def __init__(self, state_proxy, name):
        self._state_proxy = state_proxy
        self._name = name + "Fan Mode"

    @property
    def should_poll(self):
        return False

    async def async_added_to_hass(self):
        async_dispatcher_connect(
            self.hass, SIGNAL_TURKOV_CONTROLLER_STATE_UPDATE, self._update_callback
        )

    @callback
    def _update_callback(self):
        self.async_schedule_update_ha_state(True)

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state_proxy.get_mode()

    @property
    def icon(self):
        return "mdi:radiator"

    @property
    def unit_of_measurement(self):
        return ""


class TurkovControllerFanFilterSensor(Entity):
    def __init__(self, state_proxy, name):
        self._state_proxy = state_proxy
        self._name = name + "Fan Filter usage"

    @property
    def should_poll(self):
        return False

    async def async_added_to_hass(self):
        async_dispatcher_connect(
            self.hass, SIGNAL_TURKOV_CONTROLLER_STATE_UPDATE, self._update_callback
        )

    @callback
    def _update_callback(self):
        self.async_schedule_update_ha_state(True)

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state_proxy.get_filter()

    @property
    def icon(self):
        return "mdi:air-filter"

    @property
    def unit_of_measurement(self):
        return "%"
