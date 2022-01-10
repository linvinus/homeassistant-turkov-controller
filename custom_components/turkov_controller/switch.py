from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import (
    DOMAIN,
    SIGNAL_TURKOV_CONTROLLER_STATE_UPDATE
)

async def async_setup_entry(hass, entry, async_add_entities):
    name = hass.data[DOMAIN]["name"] + ' '
    state_proxy = hass.data[DOMAIN]["state_proxy"]
    async_add_entities(
        [
            TurkovControllerAutoSwitch(state_proxy, name + "On"),
        ]
    )

class TurkovControllerAutoSwitch(SwitchEntity):
    def __init__(self, state_proxy, name):
        self._state_proxy = state_proxy
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self):
        return "mdi:auto-fix"

    @property
    def should_poll(self):
        return False

    @property
    def is_on(self):
        return self._state_proxy.get_power_state()

    async def async_turn_on(self, **kwargs):
        await self._state_proxy.set_on(True)

    async def async_turn_off(self, **kwargs):
        await self._state_proxy.set_on(False)

    async def async_added_to_hass(self):
        async_dispatcher_connect(
            self.hass, SIGNAL_TURKOV_CONTROLLER_STATE_UPDATE, self._update_callback
        )

    @callback
    def _update_callback(self):
        self.async_schedule_update_ha_state(True)
