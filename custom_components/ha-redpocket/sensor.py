"""Sensor platform for Mint Mobile."""
import datetime
import logging
from datetime import timedelta
from typing import List

from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from redpocket import RedPocket, RedPocketAuthError, RedPocketException
from redpocket.api import RedPocketLine, RedPocketLineDetails

from .const import DEFAULT_NAME, DEFAULT_SCAN_INTERVAL

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

    lines: List[RedPocketLine] = await hass.async_add_executor_job(rp.get_lines)
    _LOGGER.info("Found %d associated lines with RedPocket account.", len(lines))

    for line in lines:

        async def async_update_data() -> RedPocketLineDetails:
            """Fetch data from API endpoint.

            This is the place to pre-process the data to lookup tables
            so entities can quickly look up their data.
            """
            _LOGGER.debug(
                "Refreshing line details for line: %s (%s)",
                line.number,
                line.account_id,
            )
            try:
                # Note: asyncio.TimeoutError and aiohttp.ClientError are already
                # handled by the data update coordinator.
                return await hass.async_add_executor_job(line.get_details)
            except RedPocketAuthError as err:
                _LOGGER.error("Unable to update line data, invalid credentials!")
                raise UpdateFailed from err
            except RedPocketException as err:
                _LOGGER.exception("Unable to update line data, unknown error!")
                raise UpdateFailed from err

        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name=f"redpocket line {line.number} sensor",
            update_method=async_update_data,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL),
        )

        _LOGGER.info(
            "Configuring sensors for RedPocket Line: %d (%s)",
            line.number,
            line.account_id,
        )
        _LOGGER.debug(line)
        sensors.append(RedPocketVoiceBalanceSensor(hass, line, coordinator))
        sensors.append(RedPocketMessagingBalanceSensor(hass, line, coordinator))
        sensors.append(RedPocketDataBalanceSensor(hass, line, coordinator))
        sensors.append(RedPocketRemainingDaysSensor(hass, line, coordinator))
        sensors.append(RedPocketRemainingMonthsSensor(hass, line, coordinator))

    async_add_entities(sensors, True)


class RedPocketBaseSensor(CoordinatorEntity):
    def __init__(
        self,
        hass: HomeAssistant,
        line: RedPocketLine,
        coordinator: DataUpdateCoordinator,
    ):
        super().__init__(coordinator)

        # Home Assistant Constants
        self.hass = hass

        # Sensor Defaults
        self._id_suffix = "unknown"
        self._detail_key = ""
        self._name = "Unknown RedPocket Sensor"
        self._icon = "mdi:border-none-variant"
        self._unit_of_measurement = None
        self._state = STATE_UNKNOWN

        # Red Pocket Line Information
        self._line: RedPocketLine = line

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
        if (
            not self.coordinator.data
            or not self._detail_key
            or getattr(self.coordinator.data, self._detail_key) == -1
        ):
            return STATE_UNAVAILABLE
        return getattr(self.coordinator.data, self._detail_key)

    @staticmethod
    def _current_time() -> str:
        """Return current timestamp"""
        return datetime.datetime.now().strftime("%b-%d-%Y %I:%M %p")


class RedPocketDataBalanceSensor(RedPocketBaseSensor):
    def __init__(
        self,
        hass: HomeAssistant,
        line: RedPocketLine,
        coordinator: DataUpdateCoordinator,
    ):

        # Initialize Defaults
        super().__init__(hass, line, coordinator)

        # Sensor Overrides
        self._id_suffix = "data_balance"
        self._name = f"{line.number} High-Speed Data Balance"
        self._icon = "mdi:signal-4g"
        self._unit_of_measurement = "MB"
        self._detail_key = "data_balance"


class RedPocketVoiceBalanceSensor(RedPocketBaseSensor):
    def __init__(
        self,
        hass: HomeAssistant,
        line: RedPocketLine,
        coordinator: DataUpdateCoordinator,
    ):

        # Initialize Defaults
        super().__init__(hass, line, coordinator)

        # Sensor Overrides
        self._id_suffix = "voice_balance"
        self._name = f"{line.number} Voice Balance"
        self._icon = "mdi:account-voice"
        self._unit_of_measurement = "Minutes"
        self._detail_key = "voice_balance"


class RedPocketMessagingBalanceSensor(RedPocketBaseSensor):
    def __init__(
        self,
        hass: HomeAssistant,
        line: RedPocketLine,
        coordinator: DataUpdateCoordinator,
    ):

        # Initialize Defaults
        super().__init__(hass, line, coordinator)

        # Sensor Overrides
        self._id_suffix = "messaging_balance"
        self._name = f"{line.number} Messaging Balance"
        self._icon = "mdi:message-processing"
        self._unit_of_measurement = "Messages"
        self._detail_key = "messaging_balance"


class RedPocketRemainingDaysSensor(RedPocketBaseSensor):
    def __init__(
        self,
        hass: HomeAssistant,
        line: RedPocketLine,
        coordinator: DataUpdateCoordinator,
    ):

        # Initialize Defaults
        super().__init__(hass, line, coordinator)

        # Sensor Overrides
        self._id_suffix = "remaining_days"
        self._name = f"{line.number} Days Remaining In Cycle"
        self._icon = "mdi:timer-sand"
        self._unit_of_measurement = "Days"
        self._detail_key = "remaining_days_in_cycle"


class RedPocketRemainingMonthsSensor(RedPocketBaseSensor):
    def __init__(
        self,
        hass: HomeAssistant,
        line: RedPocketLine,
        coordinator: DataUpdateCoordinator,
    ):

        # Initialize Defaults
        super().__init__(hass, line, coordinator)

        # Sensor Overrides
        self._id_suffix = "remaining_months"
        self._name = f"{line.number} Months Purchased Left"
        self._icon = "mdi:calendar-month"
        self._unit_of_measurement = "Months"
        self._detail_key = "remaining_months_purchased"
