"""Sensor platform for Mint Mobile."""
import datetime
import logging
import numbers
import uuid
from datetime import timedelta
from typing import Optional

from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, STATE_UNKNOWN, STATE_UNAVAILABLE
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

from redpocket import RedPocket, RedPocketAuthError, RedPocketException
from redpocket.api import RedPocketLine, RedPocketLineDetails
from .const import (
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    ICON,
    SENSOR,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    config = {
        CONF_USERNAME: entry.data[CONF_USERNAME],
        CONF_PASSWORD: entry.data[CONF_PASSWORD],
    }

    sensors = []
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    rp = await hass.async_add_executor_job(RedPocket, username, password)

    lines = await hass.async_add_executor_job(rp.get_lines)
    for line in lines:
        sensors.append(RedPocketVoiceBalanceSensor(hass, line))
        sensors.append(RedPocketMessagingBalanceSensor(hass, line))
        sensors.append(RedPocketDataBalanceSensor(hass, line))
        sensors.append(RedPocketRemainingDaysSensor(hass, line))
        sensors.append(RedPocketRemainingMonthsSensor(hass, line))

    async_add_entities(sensors, True)


class RedPocketBaseSensor(Entity):
    def __init__(self, hass: HomeAssistant, line: RedPocketLine):

        # Home Assistant Constants
        self.hass = hass
        self._scan_interval = timedelta(minutes=DEFAULT_SCAN_INTERVAL)
        _LOGGER.debug("Config scan interval: %s", self._scan_interval)

        # Sensor Defaults
        self._id_suffix = "unknown"
        self._name = "Unknown RedPocket Sensor"
        self._icon = "mdi:border-none-variant"
        self._unit_of_measurement = None
        self._state = STATE_UNKNOWN
        self._last_updated = self._current_time()

        # Red Pocket Line Information
        self._line: RedPocketLine = line
        self._last_update = None

        # Schedule Update
        self.async_update = Throttle(self._scan_interval)(self.async_update)

    @property
    def unique_id(self):
        """
        Return a unique, Home Assistant friendly identifier for this entity.
        """
        return f"{DEFAULT_NAME}_{self._line.number}_{self._id_suffix}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._state == -1:
            return STATE_UNAVAILABLE
        return self._state

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        return {"last_updated": self._last_updated}

    @staticmethod
    def _current_time() -> str:
        """Return current timestamp"""
        return datetime.datetime.now().strftime("%b-%d-%Y %I:%M %p")

    async def _async_get_line_details(self) -> Optional[RedPocketLineDetails]:
        """
        Fetch new state data for the sensor.
        """

        # Pull additional information from APIs
        try:
            details = await self.hass.async_add_executor_job(self._line.get_details)
            self.last_updated = self._current_time()
            return details
        except RedPocketAuthError:
            _LOGGER.error("Unable to update line data, invalid credentials!")
        except RedPocketException:
            _LOGGER.exception("Unable to update line data, unknown error!")


class RedPocketDataBalanceSensor(RedPocketBaseSensor):
    def __init__(self, hass: HomeAssistant, line: RedPocketLine):

        # Initialize Defaults
        super().__init__(hass, line)

        # Sensor Overrides
        self._id_suffix = "data_balance"
        self._name = f"{line.number} High-Speed Data Balance"
        self._icon = "mdi:signal-4g"
        self._unit_of_measurement = "MB"

    async def async_update(self):
        """
        Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        # Pull additional information from APIs
        update = await self._async_get_line_details()
        if isinstance(update, RedPocketLineDetails):
            self._state = update.data_balance


class RedPocketVoiceBalanceSensor(RedPocketBaseSensor):
    def __init__(self, hass: HomeAssistant, line: RedPocketLine):

        # Initialize Defaults
        super().__init__(hass, line)

        # Sensor Overrides
        self._id_suffix = "voice_balance"
        self._name = f"{line.number} Voice Balance"
        self._icon = "mdi:account-voice"
        self._unit_of_measurement = "Minutes"

    async def async_update(self):
        """
        Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        # Pull additional information from APIs
        update = await self._async_get_line_details()
        if isinstance(update, RedPocketLineDetails):
            self._state = update.voice_balance


class RedPocketMessagingBalanceSensor(RedPocketBaseSensor):
    def __init__(self, hass: HomeAssistant, line: RedPocketLine):

        # Initialize Defaults
        super().__init__(hass, line)

        # Sensor Overrides
        self._id_suffix = "messaging_balance"
        self._name = f"{line.number} Messaging Balance"
        self._icon = "mdi:message-processing"
        self._unit_of_measurement = "Messages"

    async def async_update(self):
        """
        Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        # Pull additional information from APIs
        update = await self._async_get_line_details()
        if isinstance(update, RedPocketLineDetails):
            self._state = update.messaging_balance


class RedPocketRemainingDaysSensor(RedPocketBaseSensor):
    def __init__(self, hass: HomeAssistant, line: RedPocketLine):

        # Initialize Defaults
        super().__init__(hass, line)

        # Sensor Overrides
        self._id_suffix = "remaining_days"
        self._name = f"{line.number} Days Remaining In Cycle"
        self._icon = "mdi:timer-sand"
        self._unit_of_measurement = "Days"

    async def async_update(self):
        """
        Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        # Pull additional information from APIs
        update = await self._async_get_line_details()
        if isinstance(update, RedPocketLineDetails):
            self._state = update.remaining_days_in_cycle


class RedPocketRemainingMonthsSensor(RedPocketBaseSensor):
    def __init__(self, hass: HomeAssistant, line: RedPocketLine):

        # Initialize Defaults
        super().__init__(hass, line)

        # Sensor Overrides
        self._id_suffix = "remaining_months"
        self._name = f"{line.number} Months Purchased Left"
        self._icon = "mdi:calendar-month"
        self._unit_of_measurement = "Months"

    async def async_update(self):
        """
        Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        # Pull additional information from APIs
        update = await self._async_get_line_details()
        if isinstance(update, RedPocketLineDetails):
            self._state = update.remaining_months_purchased
