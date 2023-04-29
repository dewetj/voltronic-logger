# Voltronic Logger
Python program that runs on a Raspberry Pi or similar device connected to a Voltronic/Axpert type inverter using the USB port. It logs the data to a postgres DB and also allows for sending data over MQTT to a broker of your choice.

# Prerequisites
- Python
- psycopg2
- paho-mqtt
- crcmod

All of these can be installed using pip.

# Configuration
All of the configurations reside in config.py, it currently contains dummy connection strings and server locations, hence nothing will be logged or published.
By default the configuration is set to test, which means the logger will simulate inverter output instead of actually reading from the USB port, this is great for testing locally on a Windows machine or any other machine not actaully connected to an inverter.

# Running the logger
You can run the directly my simply navigating to the loggers files and calling main.py, however the best way to use the logger consistantly is to run it as a service in Linux. Using Raspberry Pi OS as an example, you can add a new service to SYSTEMD as follows:

```bash
# Add service configuration to SYSTEMD
nano /etc/systemd/system/voltronic-logger.service
```

In this example the program resides in /usr/voltronic-logger and runs under the root user:
```
[Unit]
Description=Python Voltronic Logger
After=multi-user.target

[Service]
Type=idle
ExecStart=python /usr/voltronic-logger/main.py > /usr/voltronic-logger/main.log 2>&1
Restart=on-failure
RestartSec=10s
User=root

[Install]
WantedBy=multi-user.target
```

Enable the service:
```bash
# Enable the service
systemctl enable voltronic-logger.service

# Reload daemon, always run this after making changes to the loggers source code
systemctl daemon-reload
```

The service should now startup automatically when the Pi boots up, however you can manuall start and stop it using:
```bash
# Start the service
service voltronic-logger start

# Stop the service
service voltronic-logger stop
```

Should the service fail, you can use the below command to check what caused the failure:
```bash
systemctl status voltronic-logger
```

# Postgres Connection
The config.py file contains the configuration for which provider and/or DB you want to write to, please point your connection strings to the prostgres provider you will be making use of.

# MQTT
The config.py file also allows you to publish to a broker and topic of your choice, great for integrating with HomeAssistant. The data published to the broker is a JSON file that looks as follows:
```
{
    "grid_voltage": 0,
    "grid_frequency": 0,
    "inverter_voltage": 230,
    "inverter_frequency": 50,
    "inverter_apparent_output": 322,
    "inverter_active_power": 237,
    "inverter_load": 6,
    "bus_voltage": 346,
    "battery_voltage": 49.7,
    "charge_current": 0,
    "battery_capacity": 91,
    "inverter_temperature": 43,
    "pv_input_current": 0,
    "pv_input_voltage": 0,
    "battery_voltage_scc": 0,
    "discharge_current": 5,
    "inverter_status": "00010000",
    "battery_voltage_offset_fan": 0,
    "eeprom_version": "00",
    "pv_in_power": 0,
    "device_status": "010",
    "mode": "B",
    "grid_rating_voltage": 230,
    "grid_rating_current": 21.7,
    "ac_output_rating_voltage": 230,
    "ac_output_rating_frequency": 50,
    "ac_output_rating_current": 21.7,
    "ac_output_rating_apparent_power": 5000,
    "ac_output_rating_active_power": 5000,
    "battery_rating_voltage": 48,
    "battery_recharge_voltage": 48,
    "battery_under_voltage": 45,
    "battery_bulk_voltage": 53.2,
    "Battery_float_voltage": 53.2,
    "battery_type": "3",
    "current_max_ac_charging_current": 50,
    "current_max_charging_current": 20,
    "input_voltage_range": "1",
    "output_source_priority": "0",
    "charger_source_priority": "2",
    "parallel_max_num": 9,
    "machine_type": "00",
    "topology": "0",
    "output_mode": "0",
    "battery_redischarge_voltage": 51,
    "pv_ok_condition_for_parallel": "0",
    "pv_power_balance": "1",
    "unknown": "000"
}
```

# HomeAssistant
I have included a yaml file (voltronic_mqtt.yaml) which you can append to your HomeAssistant configuration.yaml file to add the inverter data as sensors. It's based on the JSON structure provided in the MQTT section above.
