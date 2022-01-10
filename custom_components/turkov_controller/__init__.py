"""The Turkov controller integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import logging
import sys
import asyncio
import async_timeout
import aiohttp
from datetime import datetime
import voluptuous as vol

from .const import ( DOMAIN ,
                     CONF_HOST,
                     CONF_NAME,
                     SCAN_INTERVAL,
                     REQUEST_TIMEOUT,
                     SIGNAL_TURKOV_CONTROLLER_STATE_UPDATE )
 
# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[str] = ["fan"]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Turkov controller from a config entry."""
    host = config_entry.data[CONF_HOST]
    name = config_entry.data[CONF_NAME]
    
    state_proxy = TurkovControllerStateProxy(hass, host)
    
    hass.data[DOMAIN] = { "state_proxy": state_proxy, "name": name}
    # TODO Store an API object for your platforms to access
    # hass.data[DOMAIN][config_entry.entry_id] = MyApi(...)

    # ~ def handle_fan_boost(call):
        # ~ duration = call.data.get('duration', 60)
        # ~ speed = call.data.get('speed', 'high')
        # ~ if int(duration) > 0:
            # ~ hass.data[DOMAIN]['state_proxy'].start_boost_mode(speed, duration)
        # ~ else:
            # ~ hass.data[DOMAIN]['state_proxy'].stop_boost_mode()

    # ~ hass.services.async_register(DOMAIN, "fan_boost", handle_fan_boost)

    # ~ hass.config_entries.async_setup_platforms(config_entry, PLATFORMS)
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, "sensor"))
    #hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, "switch"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, "fan"))

    async_track_time_interval(hass, state_proxy.async_update, SCAN_INTERVAL)
    await state_proxy.async_update(0)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # ~ unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    # ~ if unload_ok:
    hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class TurkovControllerStateProxy:
    def __init__(self, hass, host):
      self._hass = hass
      self._host = host
      self._on = False
      self._fan_speed = None
      self._fan_mode = None
      self._mode = None
      self._filter = 0
      self._temp_sp = 0
      self._in_temp = 0
      self._out_temp = 0
      self._on_last_time = None

    async def async_update(self, event_time):
        """async_fetchingData."""
        _LOGGER.debug("[" + sys._getframe().f_code.co_name + "]--> %s", self._host)

        try:
            websession = async_get_clientsession(self._hass)
            with async_timeout.timeout(REQUEST_TIMEOUT):
                resp = await websession.get("http://%s/state" % (self._host))
            if resp.status != 200:
                _LOGGER.error(f"{resp.url} returned {resp.status}")
                return

            _LOGGER.debug("[" + sys._getframe().f_code.co_name + "] async_update: %s", resp)
            json_response = await resp.json(content_type=None)
            _LOGGER.debug("[" + sys._getframe().f_code.co_name + "] async_update: %s", json_response)
            # _LOGGER.debug("async_update: %s", req.text.encode("utf-8"))
            self._on = json_response['on']
            self._fan_speed = json_response['fan_speed']
            self._fan_mode = json_response['fan_mode']
            self._temp_sp = json_response['temp_sp']
            self._mode = json_response['mode']
            self._filter = json_response['filter']
            self._in_temp = json_response['in_temp']
            self._out_temp = json_response['out_temp']
            
            async_dispatcher_send(self._hass, SIGNAL_TURKOV_CONTROLLER_STATE_UPDATE)

            return json_response

        except (asyncio.TimeoutError) as err:
            _LOGGER.error("[" + sys._getframe().f_code.co_name + "] TimeoutError %s", err)
        except (aiohttp.ClientError) as err:
            _LOGGER.error("[" + sys._getframe().f_code.co_name + "] aiohttp.ClientError %s", err)
        except ValueError:
            _LOGGER.error("[" + sys._getframe().f_code.co_name + "] Received non-JSON data from API endpoint")
        except vol.Invalid as err:
            _LOGGER.error("[" + sys._getframe().f_code.co_name + "] Received unexpected JSON from " " API endpoint: %s", err)
        except Exception as e:
            _LOGGER.error("[" + sys._getframe().f_code.co_name + "] Exception: " + str(e))
        #raise myRequestError
      #return

    async def send_command(self, command, new_state) -> bool:
        _LOGGER.debug("[" + sys._getframe().f_code.co_name + "]--> %s", self._host)

        try:
            websession = async_get_clientsession(self._hass)
            with async_timeout.timeout(REQUEST_TIMEOUT):
                J = {}
                J[command] = new_state
                resp = await websession.post("http://%s/command" % (self._host),json=J)
            if resp.status != 200:
                _LOGGER.error(f"{resp.url} returned {resp.status}")
                return

            _LOGGER.debug("[" + sys._getframe().f_code.co_name + "] async_update: %s", resp)
            json_response = await resp.json(content_type=None)
            _LOGGER.debug("[" + sys._getframe().f_code.co_name + "] async_update: %s", json_response)
            # _LOGGER.debug("async_update: %s", req.text.encode("utf-8"))
            if json_response['message'] == 'success':
              return True

        except (asyncio.TimeoutError) as err:
            _LOGGER.error("[" + sys._getframe().f_code.co_name + "] TimeoutError %s", err)
        except (aiohttp.ClientError) as err:
            _LOGGER.error("[" + sys._getframe().f_code.co_name + "] aiohttp.ClientError %s", err)
        except ValueError:
            _LOGGER.error("[" + sys._getframe().f_code.co_name + "] Received non-JSON data from API endpoint")
        except vol.Invalid as err:
            _LOGGER.error("[" + sys._getframe().f_code.co_name + "] Received unexpected JSON from " " API endpoint: %s", err)
        except Exception as e:
            _LOGGER.error("[" + sys._getframe().f_code.co_name + "] Exception: " + str(e))
        
        return False

    def get_power_state(self) -> bool:
        return self._on

    async def set_on(self, new_state) -> bool:
        _LOGGER.debug("[" + sys._getframe().f_code.co_name + "]--> %s", self._host)
        if self._on_last_time is not None and self._mode == 'heating':
          #protection in heating mode
          if (datetime.now() - self._on_last_time).total_seconds() < 120:
            _LOGGER.error("[" + sys._getframe().f_code.co_name + "] error last time state change < 120sec")
            return False

        if await self.send_command("on",str(new_state).lower()):
          self._on = new_state
          async_dispatcher_send(self._hass, SIGNAL_TURKOV_CONTROLLER_STATE_UPDATE)
          self._on_last_time = datetime.now()
          return True
        return False


    def get_fan_speed(self) -> int:
        return int(self._fan_speed) if self._fan_speed is not None else None

    async def set_fan_speed(self, new_speed) -> bool:
        _LOGGER.debug("[" + sys._getframe().f_code.co_name + "]--> %s", self._host)

        if await self.send_command("fan_speed",str(new_speed).lower()):
          self._fan_speed = new_speed
          async_dispatcher_send(self._hass, SIGNAL_TURKOV_CONTROLLER_STATE_UPDATE)
          return True
        return False



    def get_fan_mode(self) -> str:
        return self._fan_mode

    def get_mode(self) -> str:
        return self._mode

    def get_filter(self) -> int:
        return self._filter

    def get_temp_sp(self) -> int:
        return int(self._temp_sp) if self._temp_sp is not None else None

    def get_in_temp(self) -> int:
        return int(self._in_temp)/10.0 if self._in_temp is not None else None

    def get_out_temp(self) -> int:
        return int(self._out_temp)/10.0 if self._out_temp is not None else None

    def get_temperature(self,name) -> int:
        if name == 'temp_sp':
          return self.get_temp_sp()
        elif name == 'in_temp':
          return self.get_in_temp()
        elif name == 'out_temp':
          return self.get_out_temp()
