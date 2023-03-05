# Voltronic Logger
Python program that runs on a Raspberry Pi or similar device connected to a Voltronic/Axpert type inverter using the USB port. It logs the data to a postgres DB and also allows for sending data over MQTT to a broker of your choice.

# Prerequisites
- Python
- psycopg2
- paho-mqtt
- crcmod

All of the can be installed using pip.

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
    "grid_voltage": 240.4,
    "grid_frequency": 50,
    "inverter_voltage": 240.4,
    "inverter_frequency": 50,
    "inverter_apparent_output": 456,
    "inverter_active_power": 404,
    "inverter_load": 9,
    "bus_voltage": 388,
    "battery_voltage": 51.9,
    "charge_current": 0,
    "battery_capacity": 100,
    "inverter_temperature": 40,
    "pv_input_current": 0,
    "pv_input_voltage": 0,
    "battery_voltage_scc": 0,
    "discharge_current": 0,
    "inverter_status": "00010101",
    "mode": "L"
}
```

# HomeAssistant
I have included a yaml file (voltronic_mqtt.yaml) which you can append to your HomeAssistant configuration.yaml file to add the inverter data as sensors. It's based on the JSON structure provided in the MQTT section above.
