from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from homeassistant.components.fan import (
    SUPPORT_SET_SPEED,
    FanEntity,
)

from .const import (
    DOMAIN,
    SPEED_OFF,
    SPEED_LOW,
    SPEED_MEDIUM,
    SPEED_HIGH,
    VALUE_TO_SPEED,
    SPEED_TO_VALUE,
    SIGNAL_TURKOV_CONTROLLER_STATE_UPDATE
)

async def async_setup_entry(hass, entry, async_add_entities):
    state_proxy = hass.data[DOMAIN]["state_proxy"]
    name = hass.data[DOMAIN]["name"]
    async_add_entities([TurkovControllerFan(state_proxy, name)])

class TurkovControllerFan(FanEntity):
    def __init__(self, state_proxy, name):
        self._state_proxy = state_proxy
        self._name = name

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

    async def async_set_speed(self, speed: str):
        """async_turn_on is used to set speed"""

    async def async_turn_on(self, speed: str = None, **kwargs) -> None:
        # ~ self._state_proxy.set_speed(speed if not speed is None else SPEED_LOW)
        await self._state_proxy.set_on(True)

    async def async_turn_off(self, **kwargs) -> None:
        # ~ self._state_proxy.set_speed(SPEED_OFF)
        await self._state_proxy.set_on(False)

    @property
    def name(self):
        return self._name

    @property
    def is_on(self) -> bool:
        return self._state_proxy.get_power_state()

    @property
    def speed(self) -> str:
        speed = self._state_proxy.get_fan_speed()
        if speed == None:
            return None
        return VALUE_TO_SPEED[speed]

    @property
    def speed_list(self) -> list:
        return [SPEED_OFF, SPEED_LOW, SPEED_MEDIUM, SPEED_HIGH]

    @property
    def supported_features(self) -> int:
        return SUPPORT_SET_SPEED
