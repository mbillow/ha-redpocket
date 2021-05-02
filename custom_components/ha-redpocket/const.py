"""Constants for Mint Mobile."""
# Base component constants
NAME = "RedPocket Mobile"
DOMAIN = "redpocket"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "2.0.0"
ATTRIBUTION = "Data provided by https://www.redpocket.com"
ISSUE_URL = "https://github.com/mbillow/ha-redpocket/issues"

# Icons
ICON = "mdi:format-quote-close"

# Device classes

# Platforms
SENSOR = "sensor"
PLATFORMS = [SENSOR]


# Configuration and options
CONF_ENABLED = "enabled"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Defaults
DEFAULT_NAME = "redpocket"
DEFAULT_SCAN_INTERVAL = 15


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
