from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util.percentage import ordered_list_item_to_percentage, percentage_to_ordered_list_item

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
    ORDERED_NAMED_FAN_SPEEDS,
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

    async def async_turn_on(self, speed: str = None, percentage: int = None, preset_mode: str = None, **kwargs) -> None:
        """Turn on the fan."""
        # ~ self._state_proxy.set_speed(speed if not speed is None else SPEED_LOW)
        await self._state_proxy.set_on(True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the fan off."""
        # ~ self._state_proxy.set_speed(SPEED_OFF)
        await self._state_proxy.set_on(False)

    @property
    def name(self):
        return self._name

    @property
    def is_on(self) -> bool:
        return self._state_proxy.get_power_state()

    @property
    def percentage(self) -> int:
        """Return the current speed percentage."""
        s = self._state_proxy.get_fan_speed()
        if s is not None:
          return ordered_list_item_to_percentage(ORDERED_NAMED_FAN_SPEEDS, s)
        else:
          return 0

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan, as a percentage."""
        if percentage == 0:
            await self._state_proxy.set_on(False)
        await self._state_proxy.set_fan_speed(percentage_to_ordered_list_item(ORDERED_NAMED_FAN_SPEEDS, percentage))

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return len(ORDERED_NAMED_FAN_SPEEDS)

    @property
    def supported_features(self) -> int:
        return SUPPORT_SET_SPEED
