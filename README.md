# RedPocket Mobile - Home Assistant Integration

This is a fork of the [Mint Mobile Home Assistant plugin](https://github.com/ryanmac8/HA-Mint-Mobile) that I retro-fit with my RedPocket API wrapper.


This integration creates a group of sensors for each line and displays the remaining balances for the month.


### Sensors Included:

- Amount of minutes, messages, and high-speed data remaining
- Days remaining in month (The number of days left in the data plan month)
- Months remaining for plan (The number of months left that you have purchased)


![GitHub contributors](https://img.shields.io/github/contributors/mbillow/ha-redpocket)
![Maintenance](https://img.shields.io/maintenance/yes/2021)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/mbillow/ha-redpocket)
![GitHub last commit](https://img.shields.io/github/last-commit/mbillow/ha-redpocket)



## Installation
### [HACS](https://hacs.xyz) (Recommended)
1. Have [HACS](https://github.com/custom-components/hacs) installed, this will allow you to easily update
2. Add `https://github.com/mbillow/ha-redpocket` as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories) and Type: Integration
3. Click install under "RedPocket Mobile", restart your instance.

### Manual Installation
1. Download this repository as a ZIP (green button, top right) and unzip the archive
2. Copy the `redpocket` folder inside the `custom_components` folder to the Home Assistant `/<config path>/custom_components/` directory
   * You may need to create the `custom_components` in your Home Assistant installation folder if it does not exist
   * On Home Assistant (formerly Hass.io) and Home Assistant Container the final location should be `/config/custom_components/redpocket`
   * On Home Assistant Supervised, Home Assistant Core, and Hassbian the final location should be `/home/homeassistant/.homeassistant/custom_components/redpocket`
3. Restart your instance.
